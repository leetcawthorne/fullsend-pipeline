# DVOS Scheduler — Fully Adaptive Runtime (DVOS v1.6)
# Integrates dynamic interval, webhook, and repo logic from registry.json
# Supports live configuration reload, fault-tolerant recovery, and visual context sync

import time
import os
from datetime import datetime
from random import uniform

# Core DVOS modules
from systems.dvos.engine.registry_loader import DVOSRegistry
from engine.analyzer import run_analysis
from engine.integrity_verifier import verify_assets
from engine.auto_healer import heal_assets
from engine.dvos_auto_commit import git_commit_and_push, send_webhook_notification
from engine.visual_profile_manager import apply_visual_context   # ✅ NEW

LOG_PATH = "systems/dvos/runtime/logs/asset-sync.log"


def log_cycle(message):
    """Append scheduler events to the runtime log."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as log:
        log.write(f"[{datetime.utcnow().isoformat()}Z] [CYCLE] {message}\n")


def exponential_backoff_retry(func, max_retries=3, base_delay=3, *args, **kwargs):
    """Retry wrapper with exponential backoff for resilience."""
    for attempt in range(1, max_retries + 1):
        try:
            result = func(*args, **kwargs)
            if result:
                return True
            else:
                log_cycle(f"[WARN] Attempt {attempt}/{max_retries} failed — retrying...")
        except Exception as e:
            log_cycle(f"[ERROR] Attempt {attempt}/{max_retries} threw exception: {e}")
        delay = base_delay * (2 ** (attempt - 1)) + uniform(0, 1.5)
        log_cycle(f"Retrying in {delay:.1f}s...")
        time.sleep(delay)
    log_cycle("[FAIL] All retries exhausted.")
    return False


def run_dvos_cycle():
    """Run one full analysis → verification → healing → commit → notify cycle."""
    start_time = time.time()
    registry = DVOSRegistry.load()
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
        # Step 0 — Apply visual context (themes, presets, metadata)
        apply_visual_context()
        log_cycle("Visual profile context applied.")
        print("🎨 Visual context loaded from registry and presets.")

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
            runtime_config = DVOSRegistry.get_runtime()
            auto_heal_enabled = runtime_config.get("auto_heal", True)
            if auto_heal_enabled:
                log_cycle("Integrity issues found — initiating healing process.")
                print("⚠️ Mismatches found, running auto-healer...")
                repairs = heal_assets(mismatches)
                cycle_data["healed"] = repairs
                cycle_data["status"] = "healed" if repairs else "issues"
                log_cycle(f"Auto-healer applied {repairs} repairs.")
            else:
                log_cycle("Integrity issues detected, but auto-heal is disabled.")
                cycle_data["status"] = "issues"

        # Step 3 — Auto Commit (with retry logic)
        repo_config = DVOSRegistry.get_repo_config()
        commit_prefix = repo_config.get("commit_prefix", "[DVOS]")
        commit_msg = f"{commit_prefix} Automated cycle — {asset_count} assets processed"
        commit_status = exponential_backoff_retry(git_commit_and_push, 3, 4, commit_msg)
        cycle_data["commit"] = commit_status
        log_cycle(f"Auto-commit {'successful' if commit_status else 'failed after retries'}.")

    except Exception as e:
        log_cycle(f"[CRITICAL] DVOS cycle failure: {e}")
        cycle_data["status"] = "error"

    # Step 4 — Wrap up and send webhook (with retry)
    cycle_data["duration"] = f"{time.time() - start_time:.2f}s"
    summary = (
        f"**DVOS Cycle Summary**\n"
        f"- Assets Processed: {cycle_data['assets']}\n"
        f"- Healed: {cycle_data['healed']}\n"
        f"- Duration: {cycle_data['duration']}\n"
        f"- Commit: {'✅ Success' if cycle_data['commit'] else '❌ Failed'}\n"
        f"- Status: {cycle_data['status'].upper()}"
    )

    exponential_backoff_retry(send_webhook_notification, 3, 5, summary, cycle_data)

    log_cycle("Cycle complete.")
    print("🟢 [DVOS] Cycle complete.\n")
    return cycle_data


def run_scheduler():
    """Run DVOS cycle continuously using dynamic interval from registry."""
    interval = DVOSRegistry.get_cycle_interval()
    log_cycle(f"Scheduler started — interval {interval / 60:.1f} minutes.")
    print(f"[DVOS Scheduler] Running every {interval / 60:.1f} min.\n")

    while True:
        start = time.time()
        run_dvos_cycle()

        # Reload interval dynamically each cycle
        interval = DVOSRegistry.get_cycle_interval()
        elapsed = time.time() - start
        remaining = max(interval - elapsed, 5)
        log_cycle(f"Sleeping for {remaining:.1f}s before next cycle.")
        time.sleep(remaining)


if __name__ == "__main__":
    try:
        run_scheduler()
    except KeyboardInterrupt:
        log_cycle("Scheduler stopped manually.")
        print("\n🟥 DVOS Scheduler stopped.")
