# DVOS Runtime Scheduler
# Automates repeated DVOS cycles at defined intervals

import time
import threading
from datetime import datetime
from dvos_cycle import run_dvos_cycle
from auto_healer import log_heal

# --- CONFIGURATION ---------------------------------------------------------

CYCLE_INTERVAL_HOURS = 6  # ⏱ how often to run full DVOS cycle
CHECK_INTERVAL_SECONDS = 10  # how often to check for next run (lightweight)
LOCK = threading.Lock()  # prevents overlapping runs

# --- CORE SCHEDULER -------------------------------------------------------

def run_scheduled_cycle():
    """Runs a single DVOS cycle, ensuring no overlap."""
    with LOCK:
        start_time = datetime.utcnow().isoformat() + "Z"
        log_heal(f"\n--- Scheduled DVOS Cycle Start @ {start_time} ---")
        try:
            run_dvos_cycle()
        except Exception as e:
            log_heal(f"[SCHEDULER ERROR] Cycle failed: {e}")
        finally:
            end_time = datetime.utcnow().isoformat() + "Z"
            log_heal(f"--- DVOS Cycle Complete @ {end_time} ---\n")


def start_scheduler():
    """Main runtime loop — executes DVOS cycles every X hours."""
    log_heal(f"DVOS Scheduler started. Interval: {CYCLE_INTERVAL_HOURS} hours")

    while True:
        next_run_time = datetime.utcnow().timestamp() + (CYCLE_INTERVAL_HOURS * 3600)

        run_scheduled_cycle()

        # Sleep until next scheduled run
        while datetime.utcnow().timestamp() < next_run_time:
            time.sleep(CHECK_INTERVAL_SECONDS)

# --- ENTRY POINT -----------------------------------------------------------

if __name__ == "__main__":
    log_heal("--- Initializing DVOS Runtime Scheduler ---")
    start_scheduler()
