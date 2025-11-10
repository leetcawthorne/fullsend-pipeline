# DVOS Auto Commit & Webhook System v1.6
# Supports multiple webhook destinations (Discord + Slack)
# Reads config dynamically from DVOSRegistry

import os
import json
import subprocess
import requests
from datetime import datetime
from engine.registry_loader import DVOSRegistry

LOG_PATH = "systems/dvos/runtime/logs/asset-sync.log"


def log_event(message):
    """Append DVOS commit/webhook events to the runtime log."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as log:
        log.write(f"[{datetime.utcnow().isoformat()}Z] [AUTO-COMMIT] {message}\n")


def git_commit_and_push(commit_message):
    """Commit and push changes to Git if enabled in registry."""
    repo_config = DVOSRegistry.get_repo_config()
    auto_commit = repo_config.get("auto_commit", False)
    branch = repo_config.get("branch", "main")

    if not auto_commit:
        log_event("Auto-commit disabled in registry.")
        return False

    try:
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push", "origin", branch], check=True)
        log_event(f"Auto-commit successful: {commit_message}")
        return True
    except subprocess.CalledProcessError as e:
        log_event(f"[ERROR] Git operation failed: {e}")
        return False


def send_webhook_notification(summary, cycle_data=None):
    """
    Send notifications to multiple webhooks (Discord + Slack supported).
    Reads settings from registry.json:
      - notifications.webhook_url (list or string)
      - notifications.notify_on
      - notifications.embed_style
      - notifications.username
      - notifications.retry_on_fail
    """
    notify_config = DVOSRegistry.get_notifications()
    webhook_urls = notify_config.get("webhook_url", [])
    if isinstance(webhook_urls, str):
        webhook_urls = [webhook_urls]

    notify_on = notify_config.get("notify_on", [])
    embed_style = notify_config.get("embed_style", "rich")
    username = notify_config.get("username", "DVOS Notifier")

    if not webhook_urls:
        log_event("No webhook URLs configured in registry.")
        return False

    # Color code for Discord-style embeds
    color_map = {
        "ok": 0x57F287,       # green
        "issues": 0xFAA61A,   # yellow
        "healed": 0x5865F2,   # blue
        "error": 0xED4245     # red
    }

    status = (cycle_data or {}).get("status", "ok")
    color = color_map.get(status, 0x5865F2)

    fields = []
    if cycle_data:
        fields.extend([
            {"name": "🧩 Assets Processed", "value": str(cycle_data.get("assets", 0)), "inline": True},
            {"name": "🩹 Healed", "value": str(cycle_data.get("healed", 0)), "inline": True},
            {"name": "⏱ Duration", "value": str(cycle_data.get("duration", 'n/a')), "inline": True},
            {"name": "📦 Commit", "value": "✅ Yes" if cycle_data.get("commit") else "❌ No", "inline": True},
            {"name": "📊 Status", "value": status.upper(), "inline": True}
        ])

    embed = {
        "title": "DVOS System Cycle Report",
        "description": summary,
        "color": color,
        "fields": fields,
        "footer": {"text": f"Full Send • {datetime.utcnow().isoformat()}Z"}
    }

    # Convert to Slack format if needed
    def format_for_slack(embed):
        return {
            "text": f"*DVOS Cycle Report*\n{summary}",
            "attachments": [{
                "color": "#57F287" if status == "ok" else "#ED4245",
                "fields": [{"title": f["name"], "value": f["value"], "short": True} for f in fields],
                "footer": "Full Send • DVOS Runtime"
            }]
        }

    success_count = 0
    for url in webhook_urls:
        try:
            if "discord.com" in url:
                payload = {"username": username, "embeds": [embed]} if embed_style == "rich" else {"content": summary}
            elif "slack.com" in url:
                payload = format_for_slack(embed)
            else:
                payload = {"text": summary}

            response = requests.post(url, json=payload, timeout=10)
            if response.status_code in [200, 204]:
                success_count += 1
                log_event(f"Webhook notification sent successfully → {url}")
            else:
                log_event(f"[WARN] Webhook {url} returned {response.status_code}")
        except Exception as e:
            log_event(f"[ERROR] Failed to dispatch webhook to {url}: {e}")

    log_event(f"Webhook dispatch summary: {success_count}/{len(webhook_urls)} successful.")
    return success_count > 0
