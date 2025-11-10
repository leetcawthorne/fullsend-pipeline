# DVOS Auto Commit & Webhook System
# Reads configuration directly from registry.json for full automation

import os
import json
import subprocess
import requests
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
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push", "origin", branch], check=True)
        log_event(f"Auto-commit successful: {commit_message}")
        return True
    except subprocess.CalledProcessError as e:
        log_event(f"[ERROR] Git operation failed: {e}")
        return False


def send_webhook_notification(summary):
    """Send webhook notification with DVOS cycle summary."""
    registry = load_registry()
    notify_config = registry.get("notifications", {})
    webhook_url = notify_config.get("webhook_url")
    notify_on = notify_config.get("notify_on", [])

    if not webhook_url:
        log_event("No webhook URL found in registry.")
        return False

    # Only send if this type of event is configured
    if not any(event in summary.lower() for event in notify_on):
        log_event("Webhook not triggered — event type not in notify_on list.")
        return False

    payload = {
        "username": "DVOS Notifier",
        "embeds": [
            {
                "title": "DVOS Cycle Report",
                "description": summary,
                "color": 5814783,
                "footer": {"text": f"Full Send • {datetime.utcnow().isoformat()}Z"}
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204 or response.status_code == 200:
            log_event("Webhook notification sent successfully.")
            return True
        else:
            log_event(f"[WARN] Webhook returned {response.status_code}")
            return False
    except Exception as e:
        log_event(f"[ERROR] Webhook dispatch failed: {e}")
        return False
