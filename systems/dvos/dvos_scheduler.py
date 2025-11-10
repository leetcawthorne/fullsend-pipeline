# DVOS Scheduler — Full Autonomous Runtime Cycle
# Runs continuous DVOS system maintenance and healing

import time
import json
import os
from datetime import datetime

# Import core DVOS modules
from engine.analyzer import run_analysis
from engine.integrity_verifier import verify_assets
from engine.auto_healer import heal_assets

LOG_PATH = "systems/dvos/runtime/logs/asset-sync.log"


def log_cycle(message):
    """Append scheduler events to the runtime log."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as log:
        log.write(f"[{datetime.utcnow().isoformat()}Z] [CYCLE] {message}\n")


def run_dvos_cycle():
    """Run one full analysis → verification → healing cycle."""
    log_cycle("Starting DVOS cycle.")
    print("\n🚀 [DVOS] Initiating full system cycle...")

    # Step 1 — Analyze
    result = run_analysis()
    asset_count = len(result.get("assets", []))
    log_cycle(f"Analyzer complete: {asset_count} assets found.")

    # Step 2 — Verify
    mismatches = verify_assets()
    if mismatches["status"] == "ok":
        log_cycle("Integrity verified — all assets synchronized.")
        print("✅ No mismatches detected.")
    else:
        log_cycle("Integrity issues found — initiating healing process.")
        print("⚠️ Mismatches found, running auto-healer...")
        repairs = heal_assets(mismatches)
        log_cycle(f"Auto-healer applied {repairs} repairs.")

    # 🔁 Step 3 — Auto Commit + Webhook Notification
    try:
        from engine.dvos_auto_commit import git_commit_and_push, send_webhook_notification

        commit_msg = f"DVOS automated cycle — {asset_count} assets processed"
        commit_status = git_commit_and_push(commit_msg)

        summary = (
            f"✅ DVOS cycle complete.\n"
            f"Assets: {asset_count}\n"
            f"Commit: {'Success' if commit_status else 'Failed'}"
        )
        send_webhook_notification(summary)

        log_cycle("Auto-commit and webhook dispatch complete.")
    except Exception as e:
        log_cycle(f"[ERROR] Auto-commit/webhook step failed: {e}")

    log_cycle("Cycle complete.")
    print("🟢 [DVOS] Cycle complete.\n")


def run_scheduler(interval_minutes=5):
    """Run DVOS cycle continuously every given interval."""
    log_cycle(f"Scheduler started — interval {interval_minutes} minutes.")
    print(f"[DVOS Scheduler] Running every {interval_minutes} min.\n")

    while True:
        run_dvos_cycle()
        log_cycle(f"Sleeping for {interval_minutes} minutes.")
        time.sleep(interval_minutes * 60)


if __name__ == "__main__":
    try:
        run_scheduler(interval_minutes=5)
    except KeyboardInterrupt:
        log_cycle("Scheduler stopped manually.")
        print("\n🟥 DVOS Scheduler stopped.")
