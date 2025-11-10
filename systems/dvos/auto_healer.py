# DVOS Auto-Healer
# Repairs asset inconsistencies found during integrity verification
# Integrates with analyzer and integrity_verifier logs

import json
import os
from datetime import datetime

def log_heal(message, log_path="systems/dvos/runtime/logs/asset-sync.log"):
    """Append healing actions to the DVOS sync log."""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as log:
        log.write(f"[{datetime.utcnow().isoformat()}Z] {message}\n")

def load_merged_map(path="systems/dvos/runtime/merged-asset-map.json"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Merged asset map not found at {path}")
    with open(path, "r") as f:
        return json.load(f)

def save_healed_map(data, path="systems/dvos/runtime/merged-asset-map.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def heal_assets(merged_data, base_path=".", auto_prune=True, auto_flag=True):
    healed_assets = []
    regen_queue = []

    for asset in merged_data.get("assets", []):
        asset_id = asset.get("id")
        asset_path = os.path.join(base_path, asset.get("path", ""))
        valid = os.path.exists(asset_path)

        if not valid:
            if auto_flag:
                asset["status"] = "missing"
                regen_queue.append(asset)
                log_heal(f"[FLAGGED] {asset_id} marked for regeneration.")
            if auto_prune:
                log_heal(f"[PRUNED] Removed missing asset {asset_id}.")
                continue

        # Repair metadata fields if missing
        if "version" not in asset:
            asset["version"] = "1.0"
            log_heal(f"[REPAIRED] Added default version to {asset_id}.")
        if "last_updated" not in asset:
            asset["last_updated"] = datetime.utcnow().date().isoformat()
            log_heal(f"[REPAIRED] Added last_updated field to {asset_id}.")
        if "auto_optimize" not in asset:
            asset["auto_optimize"] = True
            log_heal(f"[REPAIRED] Enabled auto_optimize for {asset_id}.")
        if "web_optimized" not in asset:
            asset["web_optimized"] = True
            log_heal(f"[REPAIRED] Enabled web_optimized for {asset_id}.")

        healed_assets.append(asset)

    healed_data = {
        "assets": healed_assets,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "status": "healed",
    }
    return healed_data, regen_queue

def run_auto_healer():
    merged_path = "systems/dvos/runtime/merged-asset-map.json"
    log_path = "systems/dvos/runtime/logs/asset-sync.log"

    log_heal("--- Running DVOS Auto-Healer ---")
    merged_data = load_merged_map(merged_path)
    healed_data, regen_queue = heal_assets(merged_data)
    save_healed_map(healed_data, merged_path)

    log_heal(
        f"Healing complete. {len(regen_queue)} assets flagged for regeneration."
    )
    print(f"[DVOS] Auto-healing complete — {len(regen_queue)} assets flagged.")
    return regen_queue

if __name__ == "__main__":
    run_auto_healer()
