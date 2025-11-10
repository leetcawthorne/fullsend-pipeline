# DVOS Generator — Auto-Sync Edition
# Generates asset variants and automatically re-analyzes the system

import json
import os
import subprocess
from datetime import datetime

def load_registry(path="schema/registry.json"):
    """Load DVOS registry for paths and runtime settings."""
    with open(path, "r") as f:
        return json.load(f)

def generate_asset_variant(asset_id, style, output_folder="assets/generated"):
    """Generate a new asset variant and matching metadata JSON."""
    os.makedirs(output_folder, exist_ok=True)

    variant_name = f"{asset_id}-{style}.png"
    variant_path = os.path.join(output_folder, variant_name)

    print(f"[DVOS] Generating variant: {variant_name}")
    # Placeholder binary file; replace with image generation logic later
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
    return metadata

def register_generated_asset(metadata, merged_map="systems/dvos/runtime/merged-asset-map.json"):
    """Append the generated asset metadata to the merged asset map."""
    if not os.path.exists(merged_map):
        merged = {"assets": []}
    else:
        with open(merged_map, "r") as f:
            merged = json.load(f)

    merged["assets"].append(metadata)
    merged["last_updated"] = datetime.utcnow().isoformat() + "Z"

    os.makedirs(os.path.dirname(merged_map), exist_ok=True)
    with open(merged_map, "w") as f:
        json.dump(merged, f, indent=2)

    print(f"[DVOS] Asset registered: {metadata['id']}")
    return merged

def trigger_auto_sync(analyzer_path="systems/dvos/engine/analyzer.py"):
    """Automatically run analyzer after generation completes."""
    if not os.path.exists(analyzer_path):
        print(f"[WARN] Analyzer not found at {analyzer_path}")
        return
    print("[DVOS] Auto-sync triggered — running analyzer...")
    subprocess.run(["python", analyzer_path], check=False)
    print("[DVOS] Auto-sync completed.")

def run_generator(asset_id, style="variant"):
    """Main entry point for DVOS Generator."""
    registry = load_registry()
    runtime = registry.get("runtime", {})
    output_dir = runtime.get("variant_output", "assets/generated")

    variant = generate_asset_variant(asset_id, style, output_dir)
    register_generated_asset(variant)
    trigger_auto_sync("systems/dvos/engine/analyzer.py")

    print(f"[DVOS] Generation complete — {variant['id']}")
    return variant

if __name__ == "__main__":
    run_generator("button-primary", "dark")
