---
layout: default
title: Geops Report
---

<ul class="article-list">
{% assign sorted_posts = site.posts | sort: 'date' | reverse %}
{% for post in sorted_posts limit:10 %}
  <li>
    <a class="article-title" href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a>
    <span class="article-date">{{ post.date | date: "%B %d, %Y %H:%M" }}</span>
    <p>{{ post.lead | strip_html }} <a class="read-more" title="{{ post.title }}" href="{{ site.baseurl }}{{ post.url }}">Read more</a></p>
  </li>
{% endfor %}
</ul>
