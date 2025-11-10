# DVOS Analyzer — Runtime-Integrated Version
# Scans and validates all asset sources defined in registry.json
# Then merges asset data into runtime/merged-asset-map.json
# and logs results to runtime/logs/asset-sync.log

import json
import os
from datetime import datetime

def load_registry(path="schema/registry.json"):
    """Load the DVOS registry file."""
    with open(path, "r") as f:
        return json.load(f)

def scan_asset_sources(sources):
    """Iterate through asset directories and collect .json descriptors."""
    assets = []
    for folder in sources:
        if not os.path.exists(folder):
            print(f"[WARN] Missing asset folder: {folder}")
            continue
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".json") and "asset-map" not in file:
                    try:
                        with open(os.path.join(root, file), "r") as f:
                            asset_data = json.load(f)
                            assets.append(asset_data)
                    except Exception as e:
                        print(f"[ERROR] Could not load {file}: {e}")
    return assets

def write_merged_asset_map(assets, output_path):
    """Save all collected assets to the runtime merged asset map."""
    merged_data = {
        "assets": assets,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "status": "ok" if assets else "empty"
    }
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(merged_data, f, indent=2)
    return merged_data

def log_sync(message, log_path):
    """Append messages to the DVOS sync log."""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as log:
        log.write(f"[{datetime.utcnow().isoformat()}Z] {message}\n")

def run_analysis():
    """Main entry point for analyzer."""
    registry = load_registry()
    sources = registry.get("asset_sources", [])
    runtime = registry.get("runtime", {})

    output_path = runtime.get("compiled_output", "runtime/merged-asset-map.json")
    log_path = runtime.get("log_path", "runtime/logs/asset-sync.log")

    log_sync("Starting DVOS asset scan.", log_path)
    assets = scan_asset_sources(sources)
    merged = write_merged_asset_map(assets, output_path)

    log_sync(f"Scan complete. {len(assets)} assets merged.", log_path)
    print(f"[DVOS] Asset analysis complete — {len(assets)} assets registered.")
    return merged

if __name__ == "__main__":
    run_analysis()
