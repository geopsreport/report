---
layout: default
title: Geops Report
---

# Geops Report

Welcome to the Geops Report, your one stop to the latest geopolitics news from a range of curated sources.

<ul class="article-list">
{% assign sorted_posts = site.posts | sort: 'date' | reverse %}
{% for post in sorted_posts %}
  <li>
    <a class="article-title" href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a>
    <span class="article-date">{{ post.date | date: "%B %d, %Y %H:%M" }}</span>
    <p>{{ post.excerpt | strip_html | truncate: 180 }}</p>
  </li>
{% endfor %}
</ul>
