# DVOS Registry Loader
# Provides centralized access to runtime configuration

import json
import os
from datetime import datetime

REGISTRY_PATH = "systems/dvos/schema/registry.json"


class DVOSRegistry:
    _cache = None
    _last_load = None

    @classmethod
    def load(cls, force_reload=False):
        """Load registry.json (cached unless forced)."""
        if cls._cache and not force_reload:
            return cls._cache

        if not os.path.exists(REGISTRY_PATH):
            raise FileNotFoundError(f"Registry file not found at {REGISTRY_PATH}")

        with open(REGISTRY_PATH, "r") as f:
            cls._cache = json.load(f)

        cls._last_load = datetime.utcnow()
        return cls._cache

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
        """Returns cycle interval in seconds."""
        runtime = cls.get_runtime()
        interval_str = runtime.get("auto_cycle_interval", "5m")

        if interval_str.endswith("m"):
            return int(interval_str.rstrip("m")) * 60
        elif interval_str.endswith("h"):
            return int(interval_str.rstrip("h")) * 3600
        else:
            return int(interval_str)

