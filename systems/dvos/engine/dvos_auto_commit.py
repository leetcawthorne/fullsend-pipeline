# DVOS Auto Commit & Webhook Notifier
# Handles automatic Git commits + external notifications

import subprocess
import json
import os
import requests
from datetime import datetime

CONFIG_PATH = "schema/registry.json"

def load_registry():
    """Load DVOS registry for webhook and repo data."""
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def git_commit_and_push(commit_message="Auto-update from DVOS"):
    """Automatically commit and push runtime changes to remote repo."""
    try:
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ [DVOS] Auto-commit successful.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ [DVOS] Git operation failed: {e}")
        return False


def send_webhook_notification(message):
    """Send cycle summary or healing notification via webhook."""
    registry = load_registry()
    webhook_url = registry.get("notifications", {}).get("webhook_url")

    if not webhook_url:
        print("[DVOS] No webhook configured — skipping.")
        return False

    payload = {
        "username": "DVOS Runtime",
        "content": f"🧩 {message}\n⏱ {datetime.utcnow().isoformat()}Z"
    }

    try:
        requests.post(webhook_url, json=payload)
        print("📡 [DVOS] Webhook sent.")
        return True
    except Exception as e:
        print(f"⚠️ [DVOS] Webhook failed: {e}")
        return False
