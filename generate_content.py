import os
import random
from datetime import datetime

# --- CONFIG ---
NICHES = [
    "AI tools for freelancers",
    "remote side hustles",
    "digital minimalism",
    "low cost SaaS tools",
    "self improvement via automation"
]

TOOLS = {
    "AI tools for freelancers": [
        ("Notion AI", "https://www.notion.so/product/ai"),
        ("ChatGPT", "https://chat.openai.com"),
        ("Jasper", "https://www.jasper.ai")
    ],
    "remote side hustles": [
        ("Fiverr", "https://www.fiverr.com"),
        ("Upwork", "https://www.upwork.com"),
        ("TaskRabbit", "https://www.taskrabbit.com")
    ],
    "digital minimalism": [
        ("Focus To-Do", "https://www.focustodo.cn"),
        ("RescueTime", "https://www.rescuetime.com"),
        ("Notion", "https://www.notion.so")
    ],
    "low cost SaaS tools": [
        ("Zapier", "https://zapier.com"),
        ("Trello", "https://trello.com"),
        ("Canva", "https://www.canva.com")
    ],
    "self improvement via automation": [
        ("IFTTT", "https://ifttt.com"),
        ("Todoist", "https://todoist.com"),
        ("Google Sheets Scripts", "https://developers.google.com/apps-script")
    ]
}

CONTENT_DIR = "./_posts"
os.makedirs(CONTENT_DIR, exist_ok=True)


# --- CORE GENERATOR ---
def generate_article(keyword: str) -> str:
    title = f"The Ultimate Guide to {keyword.title()}"
    today = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    intro = (
        f"## 🚀 Introduction\n"
        f"Imagine turning {keyword} into a system that works while you sleep. "
        f"In this article, we’ll explore how automation, smart tools, and the right strategies "
        f"can help you master {keyword} — faster and smarter.\n"
    )

    why_section = (
        f"## 💡 Why It Matters\n"
        f"{keyword.title()} isn’t just a buzzword — it’s reshaping how people earn, learn, "
        f"and live. Mastering this space helps you gain freedom, scalability, and digital leverage.\n"
    )

    insights = (
        f"## ⚙️ Key Insights\n"
        f"- 🔍 **Simplify Everything:** The best {keyword} strategies remove friction, not add it.\n"
        f"- 🧠 **Automate Consistently:** Systems outperform hustle. Set up once, benefit daily.\n"
        f"- 💬 **Community Wins:** Learn from others who are already succeeding in {keyword}.\n"
    )

    steps = (
        f"## 🧭 Step-by-Step Framework\n"
        f"1. **Identify Opportunities** — Spot trends or bottlenecks related to {keyword}.\n"
        f"2. **Choose Your Tools** — Mix AI and automation to boost results.\n"
        f"3. **Set & Forget** — Build repeatable systems that grow passively.\n"
        f"4. **Measure the Gains** — Track efficiency and income improvements.\n"
    )

    case_study = (
        f"## 📊 Real-World Example\n"
        f"> “Sarah started using AI-powered {keyword} strategies and reduced manual work by 60%, "
        f"while doubling her client capacity.”\n"
    )

    tools_list = TOOLS.get(keyword, [])
    tool_section = "## 🔗 Top Tools & Resources\n"
    for name, link in tools_list:
        tool_section += f"- [{name}]({link})\n"

    wrap_up = (
        f"## ✨ Wrap-Up\n"
        f"In a world that moves at digital speed, mastering {keyword} can give you a lasting edge. "
        f"Pick one tool from this guide and take action today — the results compound fast.\n\n"
        f"*Stay tuned for tomorrow’s AI-powered strategy from FullSend Passive V1.*\n"
    )

    # --- FINAL ASSEMBLY ---
    article = f"""---
layout: post
title: "{title}"
date: {today}
tags: [{keyword.replace(" ", "-")}]
description: "Discover how {keyword} can help you build scalable income and automate your workflow."
---

# {title}

{intro}
{why_section}
{insights}
{steps}
{case_study}
{tool_section}
{wrap_up}

---

*Affiliate Disclosure: This article may contain affiliate links. If you use these links, we may earn a commission at no cost to you.*
"""
    return article


# --- MAIN EXECUTION ---
def main():
    keyword = random.choice(NICHES)
    filename = f"{datetime.utcnow().strftime('%Y-%m-%d')}-{keyword.lower().replace(' ', '-')}.md"
    filepath = os.path.join(CONTENT_DIR, filename)

    if os.path.exists(filepath):
        print("Today's article already exists:", filepath)
        return

    content = generate_article(keyword)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Generated new detailed article: {filepath}")


if __name__ == "__main__":
    main()
