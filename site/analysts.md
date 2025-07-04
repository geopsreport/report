---
layout: default
title: Analysts
---

<div class="analyst-grid">
  {% for analyst in site.analysts %}
    <div class="analyst-card">
      <h3><a href="{{ site.baseurl }}/analysts/{{ analyst.name | slugify 'ascii' }}" style="color: #1a2233; text-decoration: none;">{{ analyst.name }}</a></h3>
      {% assign analyst_posts = site.posts | where_exp: "post", "post.analysts contains analyst.name" %}
      <p>{{ analyst_posts.size }} contributions</p>
    </div>
  {% endfor %}
</div> 