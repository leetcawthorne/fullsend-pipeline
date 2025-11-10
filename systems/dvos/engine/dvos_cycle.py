# DVOS Cycle — Self-Healing Runtime Orchestrator
# Automates analyze → verify → heal → generate sequence with repair logic

import os
import json
from datetime import datetime

from engine.analyzer import run_analysis
from engine.integrity_verifier import verify_assets
from engine.auto_healer import heal_assets
from engine.generator import generate_asset_variant

LOG_PATH = "systems/dvos/runtime/logs/asset-sync.log"
MERGED_MAP_PATH = "systems/dvos/runtime/merged-asset-map.json"
ASSET_ROOT = "systems/dvos/assets"

def log_cycle(message):
    """Write DVOS cycle log messages."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as log:
        log.write(f"[{datetime.utcnow().isoformat()}Z] {message}\n")
    print(message)


def detect_asset_mismatches():
    """Compare .svg assets and .json descriptors to find missing counterparts."""
    svg_files = set()
    json_files = set()

    for root, _, files in os.walk(ASSET_ROOT):
        for f in files:
            full = os.path.join(root, f)
            if f.endswith(".svg"):
                svg_files.add(os.path.splitext(f)[0])
            elif f.endswith(".json") and "asset-map" not in f:
                json_files.add(os.path.splitext(f)[0])

    missing_json = svg_files - json_files
    missing_svg = json_files - svg_files

    return {
        "missing_json": list(missing_json),
        "missing_svg": list(missing_svg),
        "total_svg": len(svg_files),
        "total_json": len(json_files)
    }


def run_dvos_cycle():
    """Main DVOS runtime cycle."""
    log_cycle("\n--- Starting DVOS Cycle (Self-Healing) ---")

    # 1️⃣ Analyze
    try:
        analysis_result = run_analysis()
        asset_count = analysis_result.get("asset_count", 0)
        log_cycle(f"[ANALYSIS] Complete — {asset_count} assets scanned.")
    except Exception as e:
        log_cycle(f"[ERROR] Analyzer failed: {e}")
        return

    # 2️⃣ Verify
    try:
        verification_result = verify_assets()
        invalid = verification_result.get("invalid", 0)
        log_cycle(f"[VERIFIER] Complete — {invalid} invalid entries.")
    except Exception as e:
        log_cycle(f"[ERROR] Verifier failed: {e}")
        return

    # 3️⃣ Detect mismatches
    mismatches = detect_asset_mismatches()
    mj, ms = len(mismatches["missing_json"]), len(mismatches["missing_svg"])
    log_cycle(f"[SCAN] {mj} missing JSON, {ms} missing SVG files detected.")

    # 4️⃣ Heal assets automatically
    try:
        healed = heal_assets(mismatches)
        log_cycle(f"[HEALER] Complete — {healed} repairs applied.")
    except Exception as e:
        log_cycle(f"[ERROR] Healer failed: {e}")

    # 5️⃣ Generate variants
    try:
        generated = generate_asset_variant("button-primary", "energetic-creator")
        log_cycle(f"[GENERATOR] Variant generated: {generated}")
    except Exception as e:
        log_cycle(f"[ERROR] Generator failed: {e}")

    log_cycle("--- DVOS Cycle Complete ---\n")
    return {
        "status": "cycle_complete",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "mismatch_report": mismatches
    }


if __name__ == "__main__":
    run_dvos_cycle()
