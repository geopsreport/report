import json
from openai import OpenAI
import os
from datetime import datetime, timedelta

client = OpenAI()
DATA_FILE = 'data/articles.json'

def load_articles():
    with open(DATA_FILE) as f:
        return json.load(f)

def recent_articles(articles, days=7):
    cutoff = datetime.utcnow() - timedelta(days=days)
    recents = []
    for analyst in articles:
        for art in analyst['articles']:
            # Optional: parse and store publication date in each article for precision
            # For now, just include all
            recents.append((analyst['analyst'], art['title'], art['paragraph_summary']))
    return recents

def make_context_summary(recent):
    prompt = "Summarize the following developments from the independent analysts:\n"
    for analyst, title, para_sum in recent:
        prompt += f"\n- [{analyst}] {title}: {para_sum}"
    prompt += "\n\nHighlight the main events, trends, and context."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

def save_site_post(summary, period="week"):
    date_str = datetime.utcnow().strftime('%Y-%m-%d')
    filename = f"site/_posts/{date_str}-geops-report-{period}.md"
    with open(filename, 'w') as f:
        f.write(f"---\ntitle: \"Geops Report ({period}) {date_str}\"\ndate: {date_str}\n---\n\n{summary}\n")

def main():
    articles = load_articles()
    recents = recent_articles(articles, days=7)  # or 30 for monthly
    summary = make_context_summary(recents)
    save_site_post(summary, period="week")

if __name__ == "__main__":
    main() 