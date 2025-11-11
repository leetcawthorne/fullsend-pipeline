---
layout: home
title: "FullSend Passive V1"
background_asset: "/assets/images/header-bg.jpg"
visual_profile: "/assets/data/visual-profile.json"
logo: "/assets/images/fullsend-logo.png"
---

<img src="{{ site.baseurl }}/assets/images/fullsend-logo.png" alt="Full Send Logo" class="logo">

Welcome to **FullSend Passive V1** — an automated content pipeline that generates, optimizes, and publishes AI-written posts daily.

Below you’ll find the latest articles:

<ul>
  {% for post in site.posts %}
    <li>
      <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
      <small>— {{ post.date | date: "%B %d, %Y" }}</small>
    </li>
  {% endfor %}
</ul>
