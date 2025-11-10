# DVOS Generator — Runtime-Integrated Version
# Creates or updates asset variants using registry and runtime data
# Works in tandem with analyzer.py

import json
import os
from datetime import datetime

def load_registry(path="schema/registry.json"):
    """Load the DVOS registry for paths and settings."""
    with open(path, "r") as f:
        return json.load(f)

def generate_asset_variant(asset_id, style, output_folder="assets/generated"):
    """Generate a new variant entry and write to disk."""
    os.makedirs(output_folder, exist_ok=True)

    variant_name = f"{asset_id}-{style}.png"
    variant_path = os.path.join(output_folder, variant_name)

    # Simulated generation process
    print(f"[DVOS] Generating variant: {variant_name}")
    with open(variant_path, "wb") as f:
        f.write(b"")  # placeholder binary for now

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

    print(f"[DVOS] Variant metadata written: {json_path}")
    return metadata

def register_generated_asset(metadata, registry_path="systems/dvos/runtime/merged-asset-map.json"):
    """Append new generated asset metadata to runtime merged asset map."""
    if not os.path.exists(registry_path):
        print("[WARN] Merged asset map missing — creating new.")
        merged = {"assets": []}
    else:
        with open(registry_path, "r") as f:
            merged = json.load(f)

    merged["assets"].append(metadata)
    merged["last_updated"] = datetime.utcnow().isoformat() + "Z"

    with open(registry_path, "w") as f:
        json.dump(merged, f, indent=2)

    print(f"[DVOS] Asset registered to merged map: {metadata['id']}")
    return merged

def run_generator(asset_id, style="variant"):
    """Main entry point for variant generation."""
    registry = load_registry()
    runtime = registry.get("runtime", {})
    output_dir = runtime.get("variant_output", "assets/generated")

    variant = generate_asset_variant(asset_id, style, output_dir)
    updated_map = register_generated_asset(variant)

    print(f"[DVOS] Generation complete — {variant['id']}")
    return updated_map

if __name__ == "__main__":
    run_generator("button-primary", "dark")
