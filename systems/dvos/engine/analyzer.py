# DVOS Analyzer — Unified Log Bridge Edition
# Scans and validates all asset sources defined in registry.json
# Merges asset data into runtime/merged-asset-map.json
# Writes unified logs to runtime/logs/asset-sync.log

import json
import os
from datetime import datetime

# --- Shared Utility --------------------------------------------------------

def log_event(message, log_path="systems/dvos/runtime/logs/asset-sync.log"):
    """Append timestamped event to the DVOS sync log."""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as log:
        log.write(f"[{datetime.utcnow().isoformat()}Z] {message}\n")

# --- Core Functions --------------------------------------------------------

def load_registry(path="schema/registry.json"):
    """Load the DVOS registry file."""
    with open(path, "r") as f:
        return json.load(f)

def scan_asset_sources(sources, log_path=None):
    """Iterate through asset directories and collect .json descriptors."""
    assets = []
    for folder in sources:
        if not os.path.exists(folder):
            msg = f"[WARN] Missing asset folder: {folder}"
            print(msg)
            log_event(msg, log_path)
            continue
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".json") and "asset-map" not in file:
                    try:
                        with open(os.path.join(root, file), "r") as f:
                            asset_data = json.load(f)
                            assets.append(asset_data)
                    except Exception as e:
                        msg = f"[ERROR] Could not load {file}: {e}"
                        print(msg)
                        log_event(msg, log_path)
    log_event(f"Asset scan complete for {len(assets)} files.", log_path)
    return assets

def write_merged_asset_map(assets, output_path, log_path=None):
    """Save all collected assets to the runtime merged asset map."""
    merged_data = {
        "assets": assets,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "status": "ok" if assets else "empty"
    }
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(merged_data, f, indent=2)
    msg = f"Merged asset map updated: {output_path} ({len(assets)} assets)"
    print(f"[DVOS] {msg}")
    log_event(msg, log_path)
    return merged_data

# --- Runtime Entry ---------------------------------------------------------

def run_analysis():
    """Main entry point for DVOS Analyzer."""
    registry = load_registry()
    sources = registry.get("asset_sources", [])
    runtime = registry.get("runtime", {})

    output_path = runtime.get("compiled_output", "systems/dvos/runtime/merged-asset-map.json")
    log_path = runtime.get("log_path", "systems/dvos/runtime/logs/asset-sync.log")

    log_event("--- Analyzer execution started ---", log_path)
    assets = scan_asset_sources(sources, log_path)
    merged = write_merged_asset_map(assets, output_path, log_path)

    log_event(f"Analyzer complete. {len(assets)} assets registered.", log_path)
    print(f"[DVOS] Asset analysis complete — {len(assets)} assets registered.")
    return merged

if __name__ == "__main__":
    run_analysis()
