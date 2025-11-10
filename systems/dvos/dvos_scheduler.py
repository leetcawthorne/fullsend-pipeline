# DVOS Scheduler — Full Autonomous Runtime Cycle
# Runs continuous DVOS system maintenance, verification, and healing

import time
import json
import os
from datetime import datetime

# Import core DVOS modules
from engine.analyzer import run_analysis
from engine.integrity_verifier import verify_assets
from engine.auto_healer import heal_assets
from engine.dvos_auto_commit import git_commit_and_push, send_webhook_notification

LOG_PATH = "systems/dvos/runtime/logs/asset-sync.log"


def log_cycle(message):
    """Append scheduler events to the runtime log."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as log:
        log.write(f"[{datetime.utcnow().isoformat()}Z] [CYCLE] {message}\n")


def run_dvos_cycle():
    """Run one full analysis → verification → healing → commit → notify cycle."""
    start_time = time.time()
    log_cycle("Starting DVOS cycle.")
    print("\n🚀 [DVOS] Initiating full system cycle...")

    cycle_data = {
        "assets": 0,
        "healed": 0,
        "status": "ok",
        "duration": "0s",
        "commit": False
    }

    try:
        # Step 1 — Analyze
        result = run_analysis()
        asset_count = len(result.get("assets", []))
        cycle_data["assets"] = asset_count
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
            cycle_data["healed"] = repairs
            cycle_data["status"] = "healed" if repairs else "issues"
            log_cycle(f"Auto-healer applied {repairs} repairs.")

        # Step 3 — Auto Commit
        commit_msg = f"DVOS automated cycle — {asset_count} assets processed"
        commit_status = git_commit_and_push(commit_msg)
        cycle_data["commit"] = commit_status
        log_cycle(f"Auto-commit {'successful' if commit_status else 'failed'}.")

    except Exception as e:
        log_cycle(f"[ERROR] DVOS cycle failure: {e}")
        cycle_data["status"] = "error"

    # Step 4 — Wrap up
    cycle_data["duration"] = f"{time.time() - start_time:.2f}s"
    summary = (
        f"**DVOS Cycle Summary**\n"
        f"- Assets Processed: {cycle_data['assets']}\n"
        f"- Healed: {cycle_data['healed']}\n"
        f"- Duration: {cycle_data['duration']}\n"
        f"- Commit: {'✅ Success' if cycle_data['commit'] else '❌ Failed'}\n"
        f"- Status: {cycle_data['status'].upper()}"
    )

    # Send webhook report
    send_webhook_notification(summary, cycle_data)

    log_cycle("Cycle complete.")
    print("🟢 [DVOS] Cycle complete.\n")
    return cycle_data


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
