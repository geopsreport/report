---
layout: default
title: Geops Report
---

Welcome to the Geops Report, your one stop to the latest geopolitics news from a range of curated sources.

<ul class="article-list">
{% assign sorted_posts = site.posts | sort: 'date' | reverse %}
{% for post in sorted_posts %}
  <li>
    <a class="article-title" href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a>
    <span class="article-date">{{ post.date | date: "%B %d, %Y %H:%M" }}</span>
    <p>{{ post.excerpt | strip_html | truncate: 180 }} <a class="read-more" title="{{ post.title }}" href="{{ site.baseurl }}{{ post.url }}">Read more</a></p>
    <div style="margin-top:0.5rem;font-size:0.98rem;color:#555;">
      {% if post.analysts %}
        Contributions by 
        {% for analyst in post.analysts %}
          {% assign analyst_id = analyst | downcase | replace: '.', '' | replace: ',', '' | replace_regex: '[^a-z0-9]', '-' %}
          <a href="{{ site.baseurl }}/analyst/{{ analyst_id }}/" style="color:#1a2233;text-decoration:underline;">{{ analyst }}</a>{% unless forloop.last %}, {% endunless %}
        {% endfor %}
      {% endif %}
    </div>
  </li>
{% endfor %}
</ul>
