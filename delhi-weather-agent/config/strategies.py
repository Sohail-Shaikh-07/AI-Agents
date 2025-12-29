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