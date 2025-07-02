import json
from openai import OpenAI
import os
import datetime
import glob

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
DATA_FILE = 'data/articles.json'

def load_articles():
    with open(DATA_FILE) as f:
        return json.load(f)

def recent_articles(articles, hours=12):
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours)
    recents = []
    # if num articles is less than 10 return full text
    if len(articles) < 10:
        article_format = "text"
    elif len(articles) < 30:
        article_format = "paragraph_summary"
    else:
        article_format = "one_sentence_summary"

    for analyst in articles:
        for art in analyst['articles']:
            recents.append((analyst['analyst'], art['title'], art[article_format]))
    return recents

def make_context_summary(recent, input_context=None):
    prompt = """
You are a journalist and intelligence analyst assistant AI writing for the geopolitics news publication Geops Report.
You must write a journalistic article summarizing the geopolitical situation based on the following publications from selected independent analysts.

A new report is published every 12 hours, so:
- Focus on **new developments** or information instead of repeating previous reports.
- Keep it **short**, don't deal with more than 4 subjects at the time.
- When quoting a source on an opinion, use the **quote and the source**'s name.
- Keep the same **professional** tone and style as the source articles.

"""
    if input_context:
        prompt += f"\n\n{input_context}"
    for analyst, title, para_sum in recent:
        prompt += f"\n- [{analyst}] {title}: {para_sum}"
    prompt += "\n\nWrite a summary report for the main events, context, trends and expected outcomes."
    print("len(summary context):", len(prompt))
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10000,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

def save_site_post(summary):
    now = datetime.datetime.now(datetime.timezone.utc)
    date_str = now.strftime('%Y-%m-%d')
    hour_str = "morning" if now.hour < 12 else "afternoon"
    filename = f"site/_posts/{date_str}-{hour_str}-geops-report.md"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        f.write(f"---\ntitle: \"Geops Report {date_str} {hour_str}\"\ndate: {date_str} {now.strftime('%H')}:00 UTC\n---\n\n{summary}\n")

def main():
    articles = load_articles()
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
    
    context += "Last 2 reports:\n" + "\n".join(last_summaries) + "\n"

    summary = make_context_summary(recent_articles(articles, hours=12), context)
    
    save_site_post(summary)

if __name__ == "__main__":
    main() 