# DVOS Auto-Healer — Full Self-Healing Version
# Repairs missing asset descriptors and regenerates stub SVGs if needed.

import os
import json
from datetime import datetime

def create_stub_svg(path):
    """Generate a minimal valid SVG placeholder."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" width="240" height="64">
  <rect width="240" height="64" fill="#1A1A1A" stroke="#FF00FF" stroke-width="2" rx="12" ry="12"/>
  <text x="50%" y="50%" fill="#FFFFFF" font-size="14" text-anchor="middle" dominant-baseline="middle">
    placeholder
  </text>
</svg>
"""
    with open(path, "w") as f:
        f.write(svg_content)


def create_placeholder_json(asset_id):
    """Generate a minimal descriptor for an asset."""
    return {
        "id": asset_id,
        "path": f"assets/ui/{asset_id}.svg",
        "category": "ui",
        "style": "auto-healed",
        "version": "1.0",
        "auto_optimize": True,
        "web_optimized": True,
        "resolution_target": "240x64",
        "description": f"Auto-generated descriptor for recovered asset '{asset_id}'.",
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }


def heal_assets(mismatches=None):
    """Repair missing .json or .svg files based on mismatch data."""
    repairs = 0
    log_report = []

    if mismatches:
        # ✅ Heal missing JSON descriptors
        for asset in mismatches.get("missing_json", []):
            json_path = f"systems/dvos/assets/ui/{asset}.json"
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            if not os.path.exists(json_path):
                with open(json_path, "w") as f:
                    json.dump(create_placeholder_json(asset), f, indent=2)
                repairs += 1
                log_report.append(f"Created descriptor: {json_path}")

        # ✅ Heal missing SVGs
        for asset in mismatches.get("missing_svg", []):
            svg_path = f"systems/dvos/assets/ui/{asset}.svg"
            if not os.path.exists(svg_path):
                create_stub_svg(svg_path)
                repairs += 1
                log_report.append(f"Created stub SVG: {svg_path}")

    if not mismatches:
        log_report.append("No mismatches detected.")

    print(f"[HEALER] {repairs} total repairs applied.")
    for entry in log_report:
        print(" -", entry)

    return repairs
