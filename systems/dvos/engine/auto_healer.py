# DVOS Auto-Healer — Repairs missing or mismatched assets

import os
import json
from datetime import datetime

def heal_assets(mismatches=None):
    """Repair missing .json or .svg files based on mismatch data."""
    repairs = 0

    if mismatches:
        # Create missing .json descriptors
        for asset in mismatches.get("missing_json", []):
            json_path = f"systems/dvos/assets/{asset}.json"
            if not os.path.exists(json_path):
                placeholder = {
                    "id": asset,
                    "path": f"assets/{asset}.svg",
                    "category": "unknown",
                    "style": "default",
                    "version": "1.0",
                    "auto_optimize": False,
                    "web_optimized": False,
                    "description": f"Auto-healed descriptor for {asset}.",
                    "last_updated": datetime.utcnow().isoformat() + "Z"
                }
                os.makedirs(os.path.dirname(json_path), exist_ok=True)
                with open(json_path, "w") as f:
                    json.dump(placeholder, f, indent=2)
                repairs += 1

        # Log missing .svg cases
        for asset in mismatches.get("missing_svg", []):
            print(f"[WARN] Descriptor found for {asset}, but SVG missing!")

    return repairs
