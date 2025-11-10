# DVOS Registry Loader — Extended Version (v1.6)
# Provides centralized access + dynamic reload capability

import json
import os
import time
from datetime import datetime

REGISTRY_PATH = "systems/dvos/schema/registry.json"


class DVOSRegistry:
    _cache = None
    _last_load = 0
    _reload_interval = 30  # seconds — auto reload every 30s if file updated

    @classmethod
    def _load_json(cls):
        """Internal file loader."""
        if not os.path.exists(REGISTRY_PATH):
            raise FileNotFoundError(f"Registry file not found at {REGISTRY_PATH}")
        with open(REGISTRY_PATH, "r") as f:
            return json.load(f)

    @classmethod
    def load(cls, force_reload=False):
        """Load registry.json (cached with auto-reload)."""
        file_mtime = os.path.getmtime(REGISTRY_PATH)

        if (
            not force_reload
            and cls._cache is not None
            and time.time() - cls._last_load < cls._reload_interval
            and file_mtime <= cls._last_load
        ):
            return cls._cache

        cls._cache = cls._load_json()
        cls._last_load = time.time()
        return cls._cache

    # --- Access Helpers ---

    @classmethod
    def get(cls, key_path, default=None):
        """
        Get nested registry key using dot notation.
        Example: get("notifications.webhook_url")
        """
        data = cls.load()
        keys = key_path.split(".")
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return default
        return data

    @classmethod
    def get_runtime(cls):
        return cls.load().get("runtime", {})

    @classmethod
    def get_repo_config(cls):
        return cls.load().get("repo", {})

    @classmethod
    def get_notifications(cls):
        return cls.load().get("notifications", {})

    @classmethod
    def get_metadata(cls):
        return cls.load().get("metadata", {})

    @classmethod
    def get_asset_sources(cls):
        return cls.load().get("asset_sources", [])

    @classmethod
    def get_cycle_interval(cls):
        """Return the cycle interval in seconds (supports s/m/h)."""
        runtime = cls.get_runtime()
        interval_str = str(runtime.get("auto_cycle_interval", "5m")).strip().lower()

        if interval_str.endswith("h"):
            return int(interval_str.rstrip("h")) * 3600
        elif interval_str.endswith("m"):
            return int(interval_str.rstrip("m")) * 60
        elif interval_str.endswith("s"):
            return int(interval_str.rstrip("s"))
        else:
            return int(interval_str)
