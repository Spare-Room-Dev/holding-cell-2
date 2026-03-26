"""
Persistence manager for attack history and analytics.

Per STORE-01: Last 20 attacks stored persistently (survives server restart)
Per STORE-02: In-memory cache for fast history delivery to all clients
Per STAT-01: Lifetime counter persisted in JSON, displayed via get_lifetime_count()
Per D-01: JSON file for attack history - simple, Docker volume-friendly
Per D-02: attacks.json stored in shared Docker volume at /data
Per D-03: Persist every attack immediately after emission - no data loss on crash
Per D-04: Last 20 attacks stored as array, newest first, capped at 20 items
"""

import json
import os
import asyncio
from pathlib import Path
from typing import Optional


# Per D-02: File paths for persistence
PERSISTENCE_FILE = Path("/data/attacks.json")
TEMP_FILE = Path("/data/attacks.json.tmp")


class PersistenceManager:
    """
    Manages attack history and analytics persistence.

    Implements atomic writes to prevent data loss on crash:
    1. Write to temp file
    2. Atomic replace (os.replace is atomic on POSIX)

    Attributes:
        _lock: asyncio.Lock for thread-safe writes
        attacks: List of last 20 attacks, newest first
        lifetime_count: Cumulative counter of all attacks since deployment
        analytics: Aggregation data (countries, protocols, ports)
    """

    def __init__(self):
        """Initialize persistence manager with empty state."""
        self._lock = asyncio.Lock()
        self.attacks: list[dict] = []
        self.lifetime_count: int = 0
        self.analytics: dict = {
            "countries": {},
            "protocols": {},
            "ports": {}
        }

    async def load(self) -> None:
        """
        Load history from JSON file on startup.

        Per D-07: On server startup, load history from JSON file into memory.
        If file missing or corrupted, start fresh with empty state.
        """
        async with self._lock:
            if PERSISTENCE_FILE.exists():
                try:
                    with open(PERSISTENCE_FILE, 'r') as f:
                        data = json.load(f)

                    self.attacks = data.get("attacks", [])
                    self.lifetime_count = data.get("lifetime_count", 0)
                    self.analytics = data.get("analytics", {
                        "countries": {}, "protocols": {}, "ports": {}
                    })

                    print(f"[Persistence] Loaded {len(self.attacks)} attacks, "
                          f"lifetime_count={self.lifetime_count}")

                except json.JSONDecodeError as e:
                    # Per Claude's Discretion: start fresh on corrupted file
                    print(f"[Persistence] Warning: Corrupted JSON file, starting fresh: {e}")
                    self._reset()

                except KeyError as e:
                    print(f"[Persistence] Warning: Missing expected key, starting fresh: {e}")
                    self._reset()

                except Exception as e:
                    print(f"[Persistence] Warning: Unexpected error loading file, starting fresh: {e}")
                    self._reset()
            else:
                print("[Persistence] No history file found, starting fresh")
                self._reset()

    def _reset(self) -> None:
        """Reset to empty state."""
        self.attacks = []
        self.lifetime_count = 0
        self.analytics = {
            "countries": {},
            "protocols": {},
            "ports": {}
        }

    async def add_attack(self, attack: dict) -> None:
        """
        Add attack, update aggregations, persist atomically.

        Per D-08: After each attack, append to memory and flush to JSON file.
        Per D-03: Persist immediately after emission - no data loss on crash.
        Per D-04: Cap at 20 attacks, newest first.
        Per D-16: Real-time incremental aggregation.

        Args:
            attack: Attack dictionary with all AttackEvent fields
        """
        async with self._lock:
            # Per D-09/D-12: Increment lifetime counter
            self.lifetime_count += 1

            # Per D-04: Add to history (newest first, cap at 20)
            self.attacks.insert(0, attack)
            if len(self.attacks) > 20:
                self.attacks = self.attacks[:20]

            # Per D-16/D-17: Update aggregations incrementally
            # Countries - use countryCode for key
            country_code = attack.get("countryCode", "XX")
            self.analytics["countries"][country_code] = \
                self.analytics["countries"].get(country_code, 0) + 1

            # Protocols - SSH or TELNET
            protocol = attack.get("protocol", "SSH")
            self.analytics["protocols"][protocol] = \
                self.analytics["protocols"].get(protocol, 0) + 1

            # Ports - store as string key (per Pitfall 5 in RESEARCH.md)
            port = str(attack.get("port", 22))
            self.analytics["ports"][port] = \
                self.analytics["ports"].get(port, 0) + 1

            # Per D-03: Atomic write to disk
            await self._flush()

    async def _flush(self) -> None:
        """
        Write to JSON file atomically.

        Atomic write pattern for crash safety:
        1. Write to temp file first
        2. Use os.replace() which is atomic on POSIX systems

        This prevents partial/corrupted files if server crashes mid-write.
        """
        data = {
            "attacks": self.attacks,
            "lifetime_count": self.lifetime_count,
            "analytics": self.analytics
        }

        try:
            # Ensure directory exists
            PERSISTENCE_FILE.parent.mkdir(parents=True, exist_ok=True)

            # Write to temp file first
            with open(TEMP_FILE, 'w') as f:
                json.dump(data, f, indent=2)

            # Atomic replace (os.replace is atomic on POSIX)
            os.replace(TEMP_FILE, PERSISTENCE_FILE)

        except Exception as e:
            # Per Claude's Discretion: log error, continue (in-memory state preserved)
            print(f"[Persistence] Error writing to file: {e}")

    def get_history(self) -> list[dict]:
        """
        Return last 20 attacks for history event.

        Per D-06: Server maintains in-memory copy for fast history delivery.
        Per STORE-02: All clients receive same history from in-memory cache.

        Returns:
            List of attack dictionaries, newest first, max 20 items
        """
        return self.attacks

    def get_analytics(self) -> dict:
        """
        Return current analytics snapshot.

        Per D-17: Aggregations stored in memory with history JSON.
        Per STAT-02/STAT-03: Used for top countries and attack methods display.

        Returns:
            Dictionary with countries, protocols, and ports counts
        """
        return self.analytics

    def get_lifetime_count(self) -> int:
        """
        Return cumulative attack count.

        Per D-09/D-10/D-11: Counter starts at 0, increments forever, no reset.

        Returns:
            Total number of attacks since deployment
        """
        return self.lifetime_count