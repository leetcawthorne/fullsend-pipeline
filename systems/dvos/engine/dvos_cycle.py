# DVOS Cycle — Core Runtime Orchestrator
# Runs full DVOS automation sequence: analyze → verify → heal → generate

import os
from datetime import datetime

from engine.analyzer import run_analysis
from engine.integrity_verifier import verify_assets
from engine.auto_healer import heal_assets
from engine.generator import generate_asset_variant

LOG_PATH = "systems/dvos/runtime/logs/asset-sync.log"

def log_cycle(message):
    """Write DVOS cycle log messages."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as log:
        log.write(f"[{datetime.utcnow().isoformat()}Z] {message}\n")
    print(message)


def run_dvos_cycle():
    """Main DVOS runtime cycle."""
    log_cycle("\n--- Starting DVOS Cycle ---")

    # 1️⃣ Analyze all assets
    try:
        analysis_result = run_analysis()
        asset_count = analysis_result.get("asset_count", 0)
        log_cycle(f"[ANALYSIS] Complete — {asset_count} assets found.")
    except Exception as e:
        log_cycle(f"[ERROR] Analyzer failed: {e}")
        return

    # 2️⃣ Verify asset integrity
    try:
        verification_result = verify_assets()
        invalid = verification_result.get("invalid", 0)
        log_cycle(f"[VERIFIER] Complete — {invalid} invalid entries.")
    except Exception as e:
        log_cycle(f"[ERROR] Verifier failed: {e}")
        return

    # 3️⃣ Heal detected issues
    try:
        healed = heal_assets()
        log_cycle(f"[HEALER] Complete — {healed} assets repaired.")
    except Exception as e:
        log_cycle(f"[ERROR] Healer failed: {e}")
        return

    # 4️⃣ Generate new or variant assets (optional)
    try:
        generated = generate_asset_variant("button-primary", "energetic-creator")
        log_cycle(f"[GENERATOR] Example variant generated: {generated}")
    except Exception as e:
        log_cycle(f"[ERROR] Generator failed: {e}")

    log_cycle("--- DVOS Cycle Complete ---\n")
    return {
        "status": "cycle_complete",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


if __name__ == "__main__":
    run_dvos_cycle()
