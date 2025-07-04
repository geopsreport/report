import os
import json
import sys
from datetime import datetime
import yaml

# Add the scraper directory to sys.path for direct import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scraper')))
from analysts import analysts, Analyst

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
analyst_objs = {a['name']: Analyst(a['name'], a['website'], a['description']) for a in analysts}

def safe_filename(name):
    return Analyst(name, '', '').analyst_id + '.md'

for name, analyst_obj in analyst_objs.items():
    articles = analyst_articles.get(name, [])
    # Sort articles by published date, newest first
    articles = sorted(articles, key=lambda a: a.get('published', ''), reverse=True)
    # Compose YAML front matter
    front_matter = f"""---
layout: analyst
title: {analyst_obj.name}
name: {analyst_obj.name}
analyst_id: {analyst_obj.analyst_id}
description: "{analyst_obj.description}"
website: {analyst_obj.website}
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
    filename = os.path.join(ANALYST_PAGES_DIR, safe_filename(name))
    with open(filename, 'w') as f:
        f.write(front_matter) 
