---
layout: home
title: "FullSend Passive V1"
background_asset: "/assets/images/header-bg.jpg"
visual_profile: "/assets/data/visual-profile.json"
logo: "/assets/images/fullsend-logo.png"
---

<button class="theme-toggle" onclick="
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', nextTheme);
  localStorage.setItem('theme', nextTheme);
">
  🌓
</button>

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

<script>
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
  } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.documentElement.setAttribute('data-theme', 'dark');
  }
</script>
