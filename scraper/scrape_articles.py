import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
import feedparser
import newspaper
import json
import os
import time
import random
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from openai import OpenAI
from analysts import analysts
from datetime import datetime, timezone
import string
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import openai
import traceback
from dateutil import parser as date_parser

client = OpenAI()

DATA_FILE = 'data/articles.json'

# Rotating User Agents to avoid detection
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
]

sleep_time = 0.1

def clean_url(url):
    """Remove UTM parameters and other tracking parameters from URLs"""
    try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Remove tracking parameters
        tracking_params = [
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'fbclid', 'gclid', 'msclkid', 'ref', 'source', 'campaign', 'medium',
            'term', 'content', 'mc_cid', 'mc_eid', 'mc_cid', 'mc_eid'
        ]
        
        # Remove tracking parameters
        for param in tracking_params:
            query_params.pop(param, None)
        
        # Rebuild URL without tracking parameters
        if query_params:
            new_query = urlencode(query_params, doseq=True)
            cleaned_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment
            ))
        else:
            cleaned_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                '',
                parsed.fragment
            ))
        
        return cleaned_url
    except Exception as e:
        print(f"Error cleaning URL {url}: {e}")
        return url

def create_session():
    session = requests.Session()
    
    # Randomly select a user agent
    user_agent = random.choice(USER_AGENTS)
    
    # Set up headers to mimic a real browser
    session.headers.update({
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',  # Let requests handle gzip/deflate, not brotli
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Referer': 'https://www.google.com/'
    })
    
    # Configure retries with exponential backoff
    retries = Retry(
        total=5,
        backoff_factor=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"]
    )
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

def is_mostly_printable(text, threshold=0.95):
    if not text:
        return False
    printable = set(string.printable)
    count = sum(1 for c in text if c in printable)
    return (count / len(text)) >= threshold

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((openai.APIConnectionError, openai.APITimeoutError, openai.RateLimitError))
)
def call_openai_api(messages, max_tokens, temperature=0.3, timeout=30):
    """Centralized OpenAI API call with retry logic"""
    return client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        timeout=timeout
    )

def test_openai_api():
    print("Testing OpenAI API connectivity...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say hello."}],
            max_tokens=10,
            temperature=0.0,
            timeout=20
        )
        print("OpenAI API test succeeded. Response:", response.choices[0].message.content.strip())
    except Exception as e:
        print("OpenAI API connectivity test failed:")
        traceback.print_exc()
        raise SystemExit("Exiting: OpenAI API is not reachable from this environment.")

def filter_links_with_llm(links, analyst_name, website):
    """Use LLM to filter links and keep only relevant article/blog post links"""
    if not links:
        return []
    
    # Clean URLs before sending to LLM
    for link in links:
        link['url'] = clean_url(link['url'])
    
    # Prepare the list of links for the LLM
    link_list = "\n".join([f"- {link['title']} ({link['url']})" for link in links])
    
    prompt = f"""You are analyzing links from {analyst_name}'s website ({website}).

Here are the links found:
{link_list}

Please identify which links are actual articles, blog posts, or opinion pieces that contain substantial written content. 

EXCLUDE:
- Contact pages, about pages, bio pages
- Social media links (Twitter, Facebook, YouTube, etc.)
- E-commerce pages (Amazon, book sales, etc.)
- Navigation/menu pages
- Service pages (consulting, speaking, etc.)
- External links that leave the main site
- Pages that are clearly not content articles

INCLUDE:
- Blog posts, articles, opinion pieces
- News analysis pieces
- Substantial written content
- Posts with dates (if visible in title)

Respond with ONLY the titles of the links to keep, one per line. If none are relevant, respond with "NONE".

Example response:
Article Title 1
Article Title 2
Article Title 3"""

    try:
        response = call_openai_api(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.1,
            timeout=60
        )
        
        selected_titles = response.choices[0].message.content.strip().split('\n')
        selected_titles = [title.strip() for title in selected_titles if title.strip() and title.strip() != "NONE"]
        
        # Filter the original links based on selected titles
        filtered_links = []
        for link in links:
            if link['title'] in selected_titles:
                filtered_links.append(link)
        
        print(f"LLM filtered {len(links)} links down to {len(filtered_links)} relevant articles for {analyst_name}")
        return filtered_links
        
    except Exception as e:
        print(f"LLM filtering failed for {analyst_name}: {e}")
        traceback.print_exc()
        # Fallback: return all links if LLM fails
        return links

def extract_pub_date(feed_entry=None, soup=None):
    # Try RSS feed date
    if feed_entry:
        try:
            if hasattr(feed_entry, 'published'):
                return date_parser.parse(feed_entry.published).isoformat()
            if hasattr(feed_entry, 'pubDate'):
                return date_parser.parse(feed_entry.pubDate).isoformat()
            return None
        except Exception:
            pass
    # Try meta tags in HTML
    if soup:
        for meta in soup.find_all('meta'):
            if meta.get('property') in ['article:published_time', 'og:published_time', 'datePublished'] or meta.get('name') in ['pubdate', 'publishdate', 'date', 'dc.date', 'datePublished']:
                try:
                    return date_parser.parse(meta['content']).isoformat()
                except Exception:
                    pass
        for tag in soup.find_all("time"):
            if meta.get("itemprop") in ['datePublished']:
                try:
                    return date_parser.parse(tag.get("datetime")).isoformat()
                except Exception:
                    pass
        for tag in soup.find_all("span"):
            if "entry-date" in tag.get("class"):
                try:
                    return date_parser.parse(tag['content']).isoformat()
                except Exception:
                    pass
    print("extract_pub_date failed")
    # Fallback to now
    return datetime.now(timezone.utc).isoformat()

def set_referer_origin(session, url):
    parsed = urlparse(url)
    site = f"{parsed.scheme}://{parsed.netloc}/"
    session.headers.update({
        'Referer': site,
        'Origin': site.rstrip('/')
    })

def find_article_links(website, session, analyst_name):
    """Very basic: ideally, customize for each site or use RSS."""
    num_articles = 30
    
    # Try RSS first
    feeds = [website.rstrip('/') + '/feed', website.rstrip('/') + '/rss']
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            if feed.entries:
                links = [{"title": e.title, "url": e.link, "published": extract_pub_date(feed_entry=e)} for e in feed.entries[:num_articles]]
                # Filter RSS links with LLM
                return filter_links_with_llm(links, analyst_name, website)
        except Exception as e:
            print(f"RSS feed failed for {feed_url}: {e}")
            continue
    
    # Fallback: HTML scraping
    try:
        # Add a small delay to be respectful
        time.sleep(random.uniform(2*sleep_time, 5*sleep_time))
        
        # Add site-specific headers
        set_referer_origin(session, website)
        
        resp = session.get(website, timeout=20)
        if resp.status_code != 200:
            print(f"HTTP {resp.status_code} for {website}")
            return []
        soup = BeautifulSoup(resp.text, 'html.parser')
        links = []
        for link in soup.find_all('a', href=True):
            title = link.get_text().strip()
            href = link['href']
            if not title or len(title) < 5: continue
            if href.startswith('/'): href = website.rstrip('/') + href
            if href.startswith('http'):
                links.append({"title": title, "url": href})
        
        # Filter HTML links with LLM
        return filter_links_with_llm(links[:num_articles], analyst_name, website)
        
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error for {website}: {e}")
        return []
    except requests.exceptions.Timeout as e:
        print(f"Timeout error for {website}: {e}")
        return []
    except Exception as e:
        print(f"Error scraping {website}: {e}")
        return []

def download(url, session):
    # Add a small delay between requests
    time.sleep(random.uniform(2*sleep_time, 4*sleep_time))    
    set_referer_origin(session, url)
    resp = session.get(url, timeout=25)
    if resp.status_code != 200:
        print(f"HTTP {resp.status_code} for {url}")
        return None
    # Check content-type
    ctype = resp.headers.get('Content-Type', '')
    if not ctype.startswith('text/html'):
        print(f"Skipping non-HTML content: {ctype} for {url}")
        return None
    # Always decode as utf-8, ignore errors
    return resp.content.decode('utf-8', errors='ignore')

def extract_content(html, url):
    try:
        # Use newspaper3k for article extraction
        try:
            article = newspaper.Article(url)            
            article.download(input_html=html)
            article.parse()
            text = article.text
            if text and len(text) > 100 and is_mostly_printable(text):
                print(f"Newspaper3k extracted {len(text)} characters from {url}")
                return text
            else:
                print(f"Newspaper3k failed for {url}, trying BeautifulSoup fallback...")
        except Exception as e:
            print(f"Newspaper3k failed for {url}: {e}, trying BeautifulSoup fallback...")
        # BeautifulSoup fallback
        soup = BeautifulSoup(html, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        content_selectors = [
            'article', 'main', '.content', '.post-content', '.entry-content',
            '.article-content', '.story-content', '.post-body', '.entry-body'
        ]
        text = None
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                text = content.get_text(separator=' ', strip=True)
                if len(text) > 500:
                    break
        if not text or len(text) < 500:
            text = soup.get_text(separator=' ', strip=True)
        if text and len(text) > 100 and is_mostly_printable(text):
            print(f"BeautifulSoup extracted {len(text)} characters from {url}")
            return text
        else:
            print(f"No usable content extracted from {url}")
            return None
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
        response = call_openai_api(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100 if mode == 'sentence' else 250,
            temperature=0.3,
            timeout=30
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Summarization failed: {e}")
        traceback.print_exc()
        return ""

def save_articles(articles, filepath=DATA_FILE):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(articles, f, indent=2)

def main():
    test_openai_api()  # Fail early if OpenAI API is not reachable
    session = create_session()
    existing_articles = load_existing_articles()
    existing_urls = get_existing_urls(existing_articles)
    analyst_dict = {a['analyst']: a for a in existing_articles}

    for analyst in analysts:
        print(f"Checking {analyst['name']}")
        try:
            links = find_article_links(analyst['website'], session, analyst['name'])
            if not links:
                print(f"No relevant links found for {analyst['name']}, skipping...")
                continue
            print(f"Found {len(links)} relevant links for {analyst['name']}")
                
            new_articles = []
            for art in links:
                # Clean the URL for duplicate checking
                clean_url_str = clean_url(art['url'])
                if clean_url_str in existing_urls:
                    continue  # Skip known
                html = download(clean_url_str, session)
                content = extract_content(html, clean_url_str)
                if not content or len(content) < 300:
                    continue
                sent_sum = summarize(content[:10000], 'sentence')
                print(f"Sent_sum: {sent_sum}")
                para_sum = summarize(content[:20000], 'paragraph')
                new_articles.append({
                    "title": art['title'],
                    "url": clean_url_str,  # Store cleaned URL
                    "text": content,
                    "one_sentence_summary": sent_sum,
                    "paragraph_summary": para_sum,
                    "published": art.get("published", extract_pub_date(soup=BeautifulSoup(html, 'html.parser')))
                })
                existing_urls.add(clean_url_str)  # Prevent repeats in same run

            if not new_articles:
                print(f"No new articles found for {analyst['name']}")
                continue

            if analyst['name'] in analyst_dict:
                analyst_dict[analyst['name']]['articles'].extend(new_articles)
                analyst_dict[analyst['name']]['timestamp'] = datetime.now(timezone.utc).isoformat()
            else:
                existing_articles.append({
                    "analyst": analyst["name"],
                    "website": analyst["website"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "articles": new_articles
                })
            print(f"Added {len(new_articles)} new articles from {analyst['name']}.")
            
        except Exception as e:
            print(f"Error processing {analyst['name']}: {e}")
            continue

    save_articles(existing_articles)

if __name__ == "__main__":
    main() 