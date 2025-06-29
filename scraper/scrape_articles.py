import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
import feedparser
import trafilatura
import json
import os
import openai
from analysts import analysts
from datetime import datetime

openai.api_key = os.getenv('OPENAI_API_KEY')

DATA_FILE = 'data/articles.json'

def create_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500,502,503,504], allowed_methods=["GET"])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.mount('http://', HTTPAdapter(max_retries=retries))
    return session

def load_existing_articles(filepath=DATA_FILE):
    if os.path.exists(filepath):
        with open(filepath) as f:
            return json.load(f)
    return []

def get_existing_urls(existing_articles):
    return {article["url"] for analyst in existing_articles for article in analyst["articles"]}

def find_article_links(website, session):
    """Very basic: ideally, customize for each site or use RSS."""
    # Try RSS first
    feeds = [website.rstrip('/') + '/feed', website.rstrip('/') + '/rss']
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        if feed.entries:
            return [{"title": e.title, "url": e.link} for e in feed.entries[:10]]
    # Fallback: HTML scraping
    resp = session.get(website, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = []
    for link in soup.find_all('a', href=True):
        title = link.get_text().strip()
        href = link['href']
        if not title or len(title) < 5: continue
        if href.startswith('/'): href = website.rstrip('/') + href
        if href.startswith('http'):
            links.append({"title": title, "url": href})
    return links[:10]

def extract_content(url, session):
    try:
        resp = session.get(url, timeout=15)
        if resp.status_code != 200:
            return None
        text = trafilatura.extract(resp.text, url=url, include_comments=False, include_tables=False)
        return text
    except Exception as e:
        print(f"Content extraction failed for {url}: {e}")
        return None

def summarize(text, mode='sentence'):
    if not text:
        return ""
    prompt = {
        "sentence": "Summarize the following article in one sentence:\n" + text,
        "paragraph": "Summarize the following article in one paragraph:\n" + text,
    }[mode]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100 if mode == 'sentence' else 250,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Summarization failed: {e}")
        return ""

def save_articles(articles, filepath=DATA_FILE):
    with open(filepath, 'w') as f:
        json.dump(articles, f, indent=2)

def main():
    session = create_session()
    existing_articles = load_existing_articles()
    existing_urls = get_existing_urls(existing_articles)
    analyst_dict = {a['analyst']: a for a in existing_articles}

    for analyst in analysts:
        print(f"Checking {analyst['name']}")
        links = find_article_links(analyst['website'], session)
        new_articles = []
        for art in links:
            if art['url'] in existing_urls:
                continue  # Skip known
            content = extract_content(art['url'], session)
            if not content or len(content) < 300:
                continue
            sent_sum = summarize(content[:1200], 'sentence')
            para_sum = summarize(content[:2000], 'paragraph')
            new_articles.append({
                "title": art['title'],
                "url": art['url'],
                "text": content,
                "one_sentence_summary": sent_sum,
                "paragraph_summary": para_sum
            })
            existing_urls.add(art['url'])  # Prevent repeats in same run

        if not new_articles:
            continue

        if analyst['name'] in analyst_dict:
            analyst_dict[analyst['name']]['articles'].extend(new_articles)
            analyst_dict[analyst['name']]['timestamp'] = datetime.utcnow().isoformat()
        else:
            existing_articles.append({
                "analyst": analyst["name"],
                "website": analyst["website"],
                "timestamp": datetime.utcnow().isoformat(),
                "articles": new_articles
            })
        print(f"Added {len(new_articles)} new articles from {analyst['name']}.")

    save_articles(existing_articles)

if __name__ == "__main__":
    main() 