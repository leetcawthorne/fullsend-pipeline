# DVOS Visual Profile Manager
# Dynamically applies visual context, palette, and asset references
# Used by DVOS runtime to ensure aesthetics match the current visual profile

import json
import os
from datetime import datetime
from engine.registry_loader import DVOSRegistry

ASSET_BASE_PATH = "systems/dvos/assets/"
PROFILE_CACHE_PATH = "systems/dvos/runtime/visual-profile.json"
LOG_PATH = "systems/dvos/runtime/logs/asset-sync.log"


def log_visual_event(message):
    """Append visual profile events to the runtime log."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as log:
        log.write(f"[{datetime.utcnow().isoformat()}Z] [VISUAL] {message}\n")


def load_visual_profile():
    """Load the visual profile context from registry."""
    registry = DVOSRegistry.load()
    profile_name = registry.get("visual_profile", "default")
    style_meta = registry.get("metadata", {})
    runtime = registry.get("runtime", {})

    visual_context = {
        "profile": profile_name,
        "theme_alignment": style_meta.get("theme_alignment", "light"),
        "optimization_level": style_meta.get("optimization_level", "standard"),
        "background_asset": None,
        "ui_elements": [],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    asset_sources = registry.get("asset_sources", [])
    assets = []

    for folder in asset_sources:
        if not os.path.exists(folder):
            log_visual_event(f"[WARN] Missing asset source: {folder}")
            continue
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".json") and "asset-map" not in file:
                    try:
                        with open(os.path.join(root, file), "r") as f:
                            data = json.load(f)
                            data["path"] = os.path.normpath(data.get("path", "")).replace("\\", "/")
                            assets.append(data)
                    except Exception as e:
                        log_visual_event(f"[ERROR] Failed to load asset {file}: {e}")

    for a in assets:
        if a.get("style") == profile_name:
            if "background" in a.get("category", ""):
                visual_context["background_asset"] = a["path"]
            elif "ui" in a.get("category", ""):
                visual_context["ui_elements"].append(a["path"])

    # Fallback: choose first available background if none matched
    if not visual_context["background_asset"]:
        for a in assets:
            if a.get("category") == "background":
                visual_context["background_asset"] = a["path"]
                break

    os.makedirs(os.path.dirname(PROFILE_CACHE_PATH), exist_ok=True)
    with open(PROFILE_CACHE_PATH, "w") as f:
        json.dump(visual_context, f, indent=2)

    log_visual_event(f"Loaded visual profile: {profile_name}")
    return visual_context


def apply_visual_context():
    """Activate and log current aesthetic context."""
    context = load_visual_profile()
    print(f"\n🎨 [DVOS VISUAL CONTEXT]")
    print(f"Profile: {context['profile']}")
    print(f"Theme: {context['theme_alignment']}")
    print(f"Optimization: {context['optimization_level']}")
    print(f"Background: {context['background_asset'] or 'None'}")
    print(f"UI Elements: {len(context['ui_elements'])}")
    print(f"Updated: {context['timestamp']}\n")
    return context


if __name__ == "__main__":
    apply_visual_context()
