import os
import json
import sys
from datetime import datetime
import yaml

# Add the scraper directory to sys.path for direct import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scraper')))
from analysts import analysts, Analyst

# Import the summary function
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from summarize_context import make_context_summary

DATA_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/articles.json'))
ANALYST_PAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../site/_analysts'))

os.makedirs(ANALYST_PAGES_DIR, exist_ok=True)

# Load articles.json
with open(DATA_FILE, 'r') as f:
    data = json.load(f)

# Build a mapping from analyst name to their articles
analyst_articles = {}
for analyst_entry in data:
    name = analyst_entry.get('analyst')
    articles = analyst_entry.get('articles', [])
    analyst_articles[name] = articles

# Helper to get Analyst object from name
analyst_objs = {a['name']: Analyst(a['name'], a['websites'], a['description']) for a in analysts}

def create_article_objects(articles, analyst_name):
    """Convert article dicts to Article objects for summary generation"""
    from summarize_context import Article
    article_objects = []
    for art in articles:
        article_obj = Article(
            title=art.get('title'),
            url=art.get('url'),
            text=art.get('text'),
            one_sentence_summary=art.get('one_sentence_summary'),
            paragraph_summary=art.get('paragraph_summary'),
            published=art.get('published'),
            analyst=analyst_name
        )
        article_objects.append(article_obj)
    return article_objects

for name, analyst_obj in analyst_objs.items():
    articles = analyst_articles.get(name, [])
    # Sort articles by published date, newest first
    articles = sorted(articles, key=lambda a: a.get('published', ''), reverse=True)
    
    # Generate summary for this analyst's articles
    summary = ""
    if articles:
        # Convert to Article objects for summary generation
        article_objects = create_article_objects(articles, name)
        # Take the most recent articles (up to 20) for summary
        recent_articles = article_objects[:20]
        if recent_articles:
            try:
                summary = make_context_summary(recent_articles)
            except Exception as e:
                print(f"Error generating summary for {name}: {e}")
                summary = f"Analysis of recent articles by {name}."
    
    # Compose YAML front matter
    front_matter = f"""---
layout: analyst
title: {analyst_obj.name}
name: {analyst_obj.name}
analyst_id: {analyst_obj.analyst_id}
description: "{analyst_obj.description}"
websites:
"""
    # Add websites as a list
    for website in analyst_obj.websites:
        front_matter += f"  - {website}\n"
    
    front_matter += f"""summary: |
  {summary.replace(chr(10), chr(10) + '  ')}
articles:
"""
    if articles:
        # Use PyYAML to dump the articles list, indented
        articles_yaml = yaml.safe_dump(articles, allow_unicode=True, default_flow_style=False, sort_keys=False)
        # Indent each line by 2 spaces
        articles_yaml = ''.join(['  ' + line if line.strip() else line for line in articles_yaml.splitlines(True)])
        front_matter += articles_yaml
    else:
        front_matter += "  []\n"
    front_matter += '---\n\n'
    # Write the file
    filename = os.path.join(ANALYST_PAGES_DIR, analyst_obj.filename)
    with open(filename, 'w') as f:
        f.write(front_matter) 
