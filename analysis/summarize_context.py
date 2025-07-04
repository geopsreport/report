import json
from openai import OpenAI
import os
import datetime
import glob
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scraper')))
from analysts import Analyst

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
DATA_FILE = 'data/articles.json'

class Article:
    def __init__(self, title, url, text, one_sentence_summary, paragraph_summary, published, analyst):
        self.title = title
        self.url = url
        self.text = text
        self.one_sentence_summary = one_sentence_summary
        self.paragraph_summary = paragraph_summary
        self.published = published
        self.analyst = analyst

    def to_dict(self):
        return {
            "title": self.title,
            "url": self.url,
            "text": self.text,
            "one_sentence_summary": self.one_sentence_summary,
            "paragraph_summary": self.paragraph_summary,
            "published": self.published,
            "analyst": self.analyst,
        }

    @staticmethod
    def load_from_file(filepath=DATA_FILE):
        with open(filepath, 'r') as f:
            data = json.load(f)
        articles = []
        for analyst in data:
            for art in analyst.get('articles', []):
                article_obj = Article(
                    title=art.get('title'),
                    url=art.get('url'),
                    text=art.get('text'),
                    one_sentence_summary=art.get('one_sentence_summary'),
                    paragraph_summary=art.get('paragraph_summary'),
                    published=art.get('published'),
                    analyst=analyst.get('analyst')
                )
                articles.append(article_obj)
        return articles

    @staticmethod
    def filter_recent(articles, hours=12):
        cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours)
        filtered = []
        for article in articles:
            try:
                pub_dt = datetime.datetime.fromisoformat(article.published)
            except Exception:
                continue
            if pub_dt >= cutoff:
                filtered.append(article)
        return filtered

def recent_articles(articles, hours=12):
    # Use Article.filter_recent to get recent Article objects
    recents = Article.filter_recent(articles, hours)

    # Prepare tuples: (analyst, title, summary)
    result = []
    for art in recents:
        result.append(art)
    return result

def make_context_summary(recent, input_context=None):
    prompt = """
You are a journalist and intelligence analyst assistant AI writing for the geopolitics news publication Geops Report.
You must write a journalistic article summarizing the geopolitical situation based on the following publications from selected independent analysts.

A new report is published every 12 hours, so:
- Focus on **new developments** or information instead of repeating previous reports.
- Keep it **short**, not more than 3 or 4 subjects at the time.
- If you already addressed the issue in the previous summaries, and there is no new information, try other subject or go deeper into other issues.
- When quoting a source on an opinion, use the **quote and the source**'s name and bold the source name.
- Try not to quote always the same analyst as previous summaries and never repeat the same quote.
- Keep the same **professional** tone and style as the source articles.


"""
    if input_context:
        now = datetime.datetime.now(datetime.timezone.utc)
        today_str = now.strftime("%A, %B %d, %Y")
        time_str = now.strftime("%H:%M UTC")
        prompt += f"\n\n<context>\nToday is {today_str}, {time_str}\n{input_context}\n</context>"
    if len(recent) < 10:
        summary_field = "text"
    elif len(recent) < 20:
        summary_field = "paragraph_summary"
    else:
        summary_field = "one_sentence_summary"

    prompt += "<sources>"
    for article in recent:
        # Format the published date to a more readable format
        try:
            pub_dt = datetime.datetime.fromisoformat(article.published)
            readable_date = pub_dt.strftime("%B %d, %Y %H:%M")
        except Exception:
            readable_date = article.published
        prompt += f"\n### {article.title} by {article.analyst} ({readable_date})\n" + getattr(article, summary_field, '') + "\n"
    prompt += "\n</sources>\n"

    prompt += "\nWrite a summary report for the main events, context, trends and expected outcomes. First give a bit of context, go in detail on the most recent events or key issues and conclude with the trends and expected outcomes."
    print("len(summary context):", len(prompt), prompt)
    response = client.chat.completions.create(
        #model="gpt-4o",
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

def save_site_post(summary, sources):
    sources = [s.name for s in sources]
    sources = "analysts:\n  - "+"\n  - ".join(sources)
    now = datetime.datetime.now(datetime.timezone.utc)
    date_str = now.strftime('%Y-%m-%d')
    hour_str = "morning" if now.hour < 12 else "afternoon"
    filename = f"site/_posts/{date_str}-{hour_str}-geops-report.md"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        f.write(f"---\ntitle: \"Geops Report {date_str} {hour_str.capitalize()}\"\ndate: {date_str} {now.strftime('%H')}:00 UTC\n{sources}\n---\n\n{summary}\n")

def main():
    articles = Article.load_from_file()
    monthly_summary = make_context_summary(recent_articles(articles, hours=24*30))
    context = f"This month:\n{monthly_summary}\n\n"
    weekly_summary = make_context_summary(recent_articles(articles, hours=24*7), context)
    context += f"This week:\n{weekly_summary}\n\n"

    post_files = sorted(
        glob.glob("site/_posts/*-geops-report.md"),
        key=os.path.getmtime,
        reverse=True
    )

    last_summaries = []
    for fname in post_files[:2]:
        with open(fname) as f:
            last_summaries.append(f.read())
    
    context += "<previous summaries>\n" + "\n".join(last_summaries) + "\n</previous summaries>\n"

    this_edition_articles = recent_articles(articles, hours=36)
    summary = make_context_summary(this_edition_articles, context)
    sources = list(set([a.analyst for a in articles]))
    sources = [Analyst.find_analyst(a) for a in sources]

    save_site_post(summary, sources)

if __name__ == "__main__":
    main() 