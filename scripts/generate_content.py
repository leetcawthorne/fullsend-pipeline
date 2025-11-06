import os
import random
from datetime import datetime

# Default list of topics
NICHES = [
    "AI tools for freelancers",
    "remote side hustles",
    "digital minimalism",
    "low cost SaaS tools",
    "self improvement via automation"
]

CONTENT_DIR = "./content"
os.makedirs(CONTENT_DIR, exist_ok=True)

def generate_article(keyword: str) -> str:
    title = f"The Ultimate Guide to {keyword.title()}"
    intro = (
        f"In this article, we'll explore how {keyword} are changing the way people "
        f"work, save time, and earn money online."
    )
    why_section = (
        f"{keyword.title()} is one of the fastest-growing topics globally. "
        f"With new tools appearing weekly, it's important to stay updated on what actually works."
    )
    main_points = [
        f"💡 Focus on simplicity — the best {keyword} make your life easier, not harder.",
        f"🚀 Use automation to multiply your results with minimal effort.",
        f"🧠 Learn from communities and creators sharing {keyword} success stories."
    ]
    conclusion = (
        f"Whether you're new to {keyword} or already experienced, now is the best time "
        f"to take action. The tools are free, global, and ready for you to explore."
    )

    article = f"""---
title: "{title}"
date: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}
tags: [{keyword.replace(" ", "-")}]
description: "Learn how {keyword} can help you build income and efficiency."
---

# {title}

{intro}

## Why It Matters
{why_section}

## Key Insights
{os.linesep.join(main_points)}

## Final Thoughts
{conclusion}

---

*Affiliate Disclosure: This page may contain affiliate links.*
"""
    return article

def main():
    keyword = random.choice(NICHES)
    filename = f"{datetime.utcnow().strftime('%Y-%m-%d')}-{keyword.replace(' ', '-')}.md"
    filepath = os.path.join(CONTENT_DIR, filename)

    if os.path.exists(filepath):
        print("Today's article already exists:", filepath)
        return

    content = generate_article(keyword)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Generated new article: {filepath}")

if __name__ == "__main__":
    main()
