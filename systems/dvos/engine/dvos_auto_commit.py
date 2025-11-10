# DVOS Auto Commit & Webhook System
# Reads configuration directly from registry.json for full automation
# Supports multiple webhook endpoints and resilient event delivery

import os
import json
import subprocess
import requests
import time
from datetime import datetime

REGISTRY_PATH = "systems/dvos/schema/registry.json"
LOG_PATH = "systems/dvos/runtime/logs/asset-sync.log"


def log_event(message):
    """Append DVOS commit/webhook events to the runtime log."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as log:
        log.write(f"[{datetime.utcnow().isoformat()}Z] [AUTO-COMMIT] {message}\n")


def load_registry():
    """Load registry.json for repo and webhook settings."""
    with open(REGISTRY_PATH, "r") as f:
        return json.load(f)


def git_commit_and_push(commit_message):
    """Commit and push changes to Git if enabled in registry."""
    registry = load_registry()
    repo_config = registry.get("repo", {})
    auto_commit = repo_config.get("auto_commit", False)
    branch = repo_config.get("branch", "main")

    if not auto_commit:
        log_event("Auto-commit disabled in registry.")
        return False

    try:
        # Check for pending changes
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not result.stdout.strip():
            log_event("No Git changes detected. Skipping commit.")
            return True

        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push", "origin", branch], check=True)
        log_event(f"Auto-commit successful: {commit_message}")
        return True
    except subprocess.CalledProcessError as e:
        log_event(f"[ERROR] Git operation failed: {e}")
        return False
    except Exception as e:
        log_event(f"[CRITICAL] Unexpected Git error: {e}")
        return False


def send_webhook_notification(summary, cycle_data=None):
    """
    Send webhook notification(s) with DVOS cycle details.
    Supports multiple webhook URLs (Discord, Slack, etc.)
    """
    registry = load_registry()
    notify_config = registry.get("notifications", {})
    webhook_urls = notify_config.get("webhook_url")

    # Allow either a single string or list of URLs
    if isinstance(webhook_urls, str):
        webhook_urls = [webhook_urls]

    if not webhook_urls:
        log_event("No webhook URLs found in registry.")
        return False

    notify_on = [n.lower() for n in notify_config.get("notify_on", [])]

    # Skip if this event type is not in allowed list
    event_name = (cycle_data or {}).get("status", "cycle_complete").lower()
    if not any(k in event_name or k in summary.lower() for k in notify_on):
        log_event("Webhook not triggered — event type not in notify_on list.")
        return False

    # Color mapping by status
    color_map = {
        "ok": 0x57F287,       # ✅ green
        "issues": 0xFAA61A,   # ⚠️ yellow
        "healed": 0x5865F2,   # 🔧 blue
        "error": 0xED4245     # 🟥 red
    }

    status = (cycle_data or {}).get("status", "ok")
    color = color_map.get(status, 0x5865F2)

    # Dynamic fields for visual embed
    fields = []
    if cycle_data:
        fields.extend([
            {"name": "🧩 Assets Processed", "value": str(cycle_data.get("assets", 0)), "inline": True},
            {"name": "🩹 Healed", "value": str(cycle_data.get("healed", 0)), "inline": True},
            {"name": "⏱ Duration", "value": str(cycle_data.get("duration", "n/a")), "inline": True},
            {"name": "📦 Commit", "value": "✅ Yes" if cycle_data.get("commit") else "❌ No", "inline": True},
            {"name": "📊 Status", "value": status.upper(), "inline": True}
        ])

    payload = {
        "username": "DVOS Notifier",
        "embeds": [
            {
                "title": "DVOS System Cycle Report",
                "description": summary,
                "color": color,
                "fields": fields,
                "footer": {"text": f"Full Send • {datetime.utcnow().isoformat()}Z"}
            }
        ]
    }

    def send_once(url):
        try:
            r = requests.post(url, json=payload, timeout=10)
            if r.status_code in [200, 204]:
                return True
            log_event(f"[WARN] Webhook {url[:40]}... returned {r.status_code}")
            return False
        except Exception as e:
            log_event(f"[ERROR] Webhook dispatch failed: {e}")
            return False

    success = False
    for url in webhook_urls:
        # First attempt
        if send_once(url):
            log_event(f"Webhook notification sent successfully → {url[:50]}...")
            success = True
            continue
        # Retry once after delay
        log_event(f"Retrying webhook to {url[:40]}...")
        time.sleep(3)
        if send_once(url):
            log_event(f"Webhook retry succeeded → {url[:50]}...")
            success = True
        else:
            log_event(f"[FAIL] Webhook permanently failed → {url[:50]}...")

    return success
