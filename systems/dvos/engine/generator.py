# DVOS Generator — Unified Log Bridge Edition
# Generates asset variants, syncs with analyzer, and logs all activity

import json
import os
import subprocess
from datetime import datetime

# --- Shared Utilities -------------------------------------------------------

def log_event(message, log_path="systems/dvos/runtime/logs/asset-sync.log"):
    """Append timestamped event to the DVOS sync log."""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as log:
        log.write(f"[{datetime.utcnow().isoformat()}Z] {message}\n")

def load_registry(path="schema/registry.json"):
    """Load DVOS registry for runtime settings."""
    with open(path, "r") as f:
        return json.load(f)

# --- Generator Core ---------------------------------------------------------

def generate_asset_variant(asset_id, style, output_folder="assets/generated", log_path=None):
    """Generate a new asset variant and metadata JSON."""
    os.makedirs(output_folder, exist_ok=True)

    variant_name = f"{asset_id}-{style}.png"
    variant_path = os.path.join(output_folder, variant_name)

    print(f"[DVOS] Generating variant: {variant_name}")
    log_event(f"Generating asset variant: {variant_name}", log_path)

    # Placeholder for image generation logic
    with open(variant_path, "wb") as f:
        f.write(b"")

    metadata = {
        "id": f"{asset_id}-{style}",
        "path": variant_path,
        "category": "generated",
        "style": style,
        "version": "1.0",
        "auto_optimize": True,
        "web_optimized": True,
        "source_asset": asset_id,
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }

    json_path = os.path.join(output_folder, f"{asset_id}-{style}.json")
    with open(json_path, "w") as meta_file:
        json.dump(metadata, meta_file, indent=2)

    print(f"[DVOS] Metadata written: {json_path}")
    log_event(f"Metadata created for {metadata['id']} at {json_path}", log_path)
    return metadata

def register_generated_asset(metadata, merged_map="systems/dvos/runtime/merged-asset-map.json", log_path=None):
    """Append generated asset metadata to runtime merged asset map."""
    if not os.path.exists(merged_map):
        merged = {"assets": []}
        log_event("[INFO] Created new merged asset map.", log_path)
    else:
        with open(merged_map, "r") as f:
            merged = json.load(f)

    merged["assets"].append(metadata)
    merged["last_updated"] = datetime.utcnow().isoformat() + "Z"

    os.makedirs(os.path.dirname(merged_map), exist_ok=True)
    with open(merged_map, "w") as f:
        json.dump(merged, f, indent=2)

    print(f"[DVOS] Asset registered: {metadata['id']}")
    log_event(f"Asset registered in merged map: {metadata['id']}", log_path)
    return merged

def trigger_auto_sync(analyzer_path="systems/dvos/engine/analyzer.py", log_path=None):
    """Automatically run analyzer after generation completes."""
    if not os.path.exists(analyzer_path):
        msg = f"[WARN] Analyzer not found at {analyzer_path}"
        print(msg)
        log_event(msg, log_path)
        return

    log_event("Auto-sync triggered — running analyzer.", log_path)
    subprocess.run(["python", analyzer_path], check=False)
    log_event("Auto-sync completed.", log_path)

# --- Main Execution ---------------------------------------------------------

def run_generator(asset_id, style="variant"):
    """Main entry point for DVOS Generator."""
    registry = load_registry()
    runtime = registry.get("runtime", {})
    output_dir = runtime.get("variant_output", "assets/generated")
    log_path = runtime.get("log_path", "systems/dvos/runtime/logs/asset-sync.log")

    log_event(f"--- Generator started for {asset_id} [{style}] ---", log_path)

    variant = generate_asset_variant(asset_id, style, output_dir, log_path)
    register_generated_asset(variant, log_path=log_path)
    trigger_auto_sync("systems/dvos/engine/analyzer.py", log_path)

    log_event(f"Generator complete for {variant['id']}", log_path)
    print(f"[DVOS] Generation complete — {variant['id']}")
    return variant

if __name__ == "__main__":
    run_generator("button-primary", "dark")
