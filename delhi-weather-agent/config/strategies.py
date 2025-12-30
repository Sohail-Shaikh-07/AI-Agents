import time
from typing import List
import itertools
from datetime import datetime
from .settings import API_KEYS, DAILY_QUOTA_PER_KEY


class EnterpriseLoadBalancer:
    """
    Advanced Round-Robin Load Balancer with Quota Tracking and Smart Sleep.
    """

    def __init__(self):
        self._keys = API_KEYS
        if not self._keys:
            raise ValueError(
                "CRITICAL: No API Keys found. Set VC_API_1, VC_API_2... in .env"
            )

        print(f"[System] Load Balancer initialized with {len(self._keys)} keys.")
        self._key_count = len(self._keys)
        self._cycler = itertools.cycle(self._keys)
        self.current_key = next(self._cycler)

        # Track failures to detect global exhaustion
        self._consecutive_failures = 0

    def get_current_key(self) -> str:
        return self.current_key

    def rotate_key(self):
        """
        Rotates to the next available credential.
        If all credentials reach their quota limits, the system initiates a Smart Wait.
        """
        old_key = self.current_key
        self.current_key = next(self._cycler)
        self._consecutive_failures += 1

        print(
            f"[LoadBalancer] Credential Rotation: ...{old_key[-4:]} -> ...{self.current_key[-4:]}"
        )

        # If we have rotated through the entire credential pool without success
        if self._consecutive_failures >= self._key_count:
            self._activate_smart_sleep()

    def report_success(self):
        """Reset failure counter on successful request."""
        self._consecutive_failures = 0

    def _activate_smart_sleep(self):
        """
        Pauses the Agent system for 24 hours (or until manual reset) to respect API rate limits.
        This ensures compliance with global daily quotas across all keys.
        """
        print("!" * 50)
        print("[CRITICAL] Global Quota Limit Reached (429).")
        print("[CRITICAL] Initiating 24-Hour Compliance Pause...")
        print("!" * 50)

        # We sleep in chunks to show liveness in logs
        hours_to_sleep = 24
        for h in range(hours_to_sleep):
            print(f"[System] Compliance Pause... {h}/{hours_to_sleep} hours elapsed.")
            time.sleep(3600)  # 1 hour

        print("[System] Resuming operations. Daily quotas reset.")
        self._consecutive_failures = 0
