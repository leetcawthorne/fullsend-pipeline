# DVOS Integrity Verifier
# Ensures all assets in merged-asset-map.json are valid, unique, and present on disk.

import json
import os
from datetime import datetime

# --- Shared Log Bridge (consistent with analyzer/generator) -----------------

def log_event(message, log_path="systems/dvos/runtime/logs/asset-sync.log"):
    """Append timestamped integrity event to the DVOS sync log."""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as log:
        log.write(f"[{datetime.utcnow().isoformat()}Z] {message}\n")

# --- Integrity Checks -------------------------------------------------------

def load_merged_map(path="systems/dvos/runtime/merged-asset-map.json"):
    """Load the merged asset map produced by analyzer."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Merged asset map not found at {path}")
    with open(path, "r") as f:
        return json.load(f)

def check_assets(merged_data, base_path=".", log_path=None):
    """Run a series of integrity checks on all assets."""
    seen_ids = set()
    issues = {"missing_files": [], "duplicates": [], "invalid_entries": []}

    for asset in merged_data.get("assets", []):
        asset_id = asset.get("id")
        asset_path = asset.get("path")

        if not asset_id or not asset_path:
            issues["invalid_entries"].append(asset)
            log_event(f"[INVALID] Missing ID or path in asset entry: {asset}", log_path)
            continue

        # Check for duplicates
        if asset_id in seen_ids:
            issues["duplicates"].append(asset_id)
            log_event(f"[DUPLICATE] Asset ID '{asset_id}' appears multiple times.", log_path)
        else:
            seen_ids.add(asset_id)

        # Check for missing physical files
        full_path = os.path.join(base_path, asset_path)
        if not os.path.exists(full_path):
            issues["missing_files"].append(asset_path)
            log_event(f"[MISSING] File not found for {asset_id}: {asset_path}", log_path)

    log_event(
        f"Integrity check complete — {len(issues['missing_files'])} missing, "
        f"{len(issues['duplicates'])} duplicates, "
        f"{len(issues['invalid_entries'])} invalid.",
        log_path
    )
    return issues

def summarize_issues(issues):
    """Format a quick human-readable report."""
    lines = ["\nDVOS Integrity Report:"]
    for key, values in issues.items():
        lines.append(f"  {key}: {len(values)}")
        if values:
            lines.extend([f"    - {v}" for v in values])
    return "\n".join(lines)

# --- Runtime Entry ----------------------------------------------------------

def run_integrity_verifier():
    """Main entry point for the DVOS Integrity Verifier."""
    merged_path = "systems/dvos/runtime/merged-asset-map.json"
    log_path = "systems/dvos/runtime/logs/asset-sync.log"

    log_event("--- Running DVOS Integrity Verifier ---", log_path)
    merged_data = load_merged_map(merged_path)
    issues = check_assets(merged_data, ".", log_path)
    report = summarize_issues(issues)

    print(report)
    log_event("Integrity verification complete.\n", log_path)
    return issues

if __name__ == "__main__":
    run_integrity_verifier()
