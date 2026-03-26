"""
Cowrie log reader for real-time attack processing.

Per D-05: Async file tailing with watchfiles
Per D-06: Reads /var/log/cowrie/cowrie.json via shared Docker volume
Per D-07: Replaces attack_generator.py for real data
Per D-09: Emits attacks on session close only
Per D-10: Session ID correlates events
Per D-11: Duration calculated from session timestamps
Per D-12: Throttled emission (1.5s buffer)
"""

import asyncio
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from watchfiles import awatch, Change

from models import AttackEvent, Archetype, create_attack_event
from archetypes import classify_attack, format_archetype_log
from geoip_service import GeoIPService


@dataclass
class SessionData:
    """Data collected for a Cowrie session."""
    session_id: str
    src_ip: str = ""
    src_port: int = 0
    dst_port: int = 2222
    protocol: str = "SSH"
    timestamp: str = ""
    hassh: Optional[str] = None
    username: Optional[str] = None
    commands: list[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    duration: float = 0.0


class CowrieReader:
    """
    Async Cowrie log reader with session correlation.

    Watches Cowrie JSON log for new events, correlates by session ID,
    and emits complete AttackEvents on session close.
    """

    def __init__(
        self,
        log_dir: str = "/var/log/cowrie",
        geoip_service: Optional[GeoIPService] = None
    ):
        """
        Initialize Cowrie reader.

        Args:
            log_dir: Directory containing cowrie.json log file
            geoip_service: GeoIP lookup service for country enrichment
        """
        self.log_dir = log_dir
        self.log_path = os.path.join(log_dir, "cowrie.json")
        self.geoip_service = geoip_service or GeoIPService()

        # Per D-10: Session correlation buffer
        self.sessions: dict[str, SessionData] = {}

        # Per D-12: Throttling
        self._emit_queue: list[AttackEvent] = []
        self._last_emit: float = 0.0
        self._throttle_interval: float = 1.5  # seconds

        # Track position in log file for initial read
        self._initialized = False

    async def process_existing_log(self) -> None:
        """
        Process existing log entries on startup.

        Reads through existing cowrie.json to capture any sessions
        that started before the reader was launched.
        """
        if not os.path.exists(self.log_path):
            print(f"[CowrieReader] Log file not found: {self.log_path}")
            return

        print(f"[CowrieReader] Processing existing log: {self.log_path}")

        try:
            with open(self.log_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                        await self._process_event(event)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"[CowrieReader] Error reading existing log: {e}")

        self._initialized = True
        print(f"[CowrieReader] Loaded {len(self.sessions)} incomplete sessions from existing log")

    async def watch_log(self, emit_callback) -> None:
        """
        Watch Cowrie JSON log for new entries.

        Per D-05: Uses watchfiles for async file watching

        Args:
            emit_callback: Async function to call with AttackEvent on session close
        """
        self._emit_callback = emit_callback

        print(f"[CowrieReader] Starting watch on: {self.log_dir}")

        # Per RESEARCH.md: Watch directory (not file) to handle log rotation
        async for changes in awatch(self.log_dir):
            for change_type, path in changes:
                if change_type == Change.added or change_type == Change.modified:
                    if path.endswith("cowrie.json"):
                        await self._read_new_lines(path)

            # Per D-12: Throttled emission
            await self._emit_throttled()

    async def _read_new_lines(self, path: str) -> None:
        """Read new lines from the log file."""
        try:
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                        await self._process_event(event)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"[CowrieReader] Error reading log: {e}")

    async def _process_event(self, event: dict) -> None:
        """
        Process a single Cowrie event.

        Per D-10: Correlate events by session ID

        Args:
            event: Parsed JSON event from Cowrie log
        """
        event_type = event.get("eventid", "")
        session_id = event.get("session", "")

        if not session_id:
            return

        if event_type == "cowrie.session.connect":
            # New session - initialize
            self.sessions[session_id] = SessionData(
                session_id=session_id,
                src_ip=event.get("src_ip", ""),
                src_port=event.get("src_port", 0),
                dst_port=event.get("dst_port", 2222),
                protocol=self._determine_protocol(event),
                timestamp=event.get("timestamp", ""),
                start_time=self._parse_timestamp(event.get("timestamp", ""))
            )
            print(f"[CowrieReader] Session started: {session_id[:8]} from {event.get('src_ip', '?')}")

        elif event_type == "cowrie.client.kex":
            # SSH key exchange - extract HASSH fingerprint
            # Per D-15: HASSH from Cowrie log field
            if session_id in self.sessions:
                self.sessions[session_id].hassh = event.get("hassh")

        elif event_type == "cowrie.login.success":
            # Successful login
            if session_id in self.sessions:
                self.sessions[session_id].username = event.get("username")

        elif event_type == "cowrie.command.input":
            # Command executed
            # Per D-10: Collect commands for classification
            if session_id in self.sessions:
                command = event.get("input", "")
                if command:
                    self.sessions[session_id].commands.append(command)

        elif event_type == "cowrie.session.closed":
            # Per D-09: Session complete - emit attack
            if session_id in self.sessions:
                session_data = self.sessions.pop(session_id)
                session_data.duration = event.get("duration", 0.0)

                attack = await self._create_attack_event(session_data)
                if attack:
                    self._emit_queue.append(attack)
                    self._log_attack(attack)

    def _determine_protocol(self, event: dict) -> str:
        """Determine protocol from event (SSH vs Telnet)."""
        dst_port = event.get("dst_port", 2222)
        # Per D-04: Cowrie SSH on 2222, Telnet on 2323
        if dst_port == 2323:
            return "TELNET"
        return "SSH"

    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse ISO timestamp string."""
        try:
            # Cowrie uses ISO 8601 format
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            return None

    async def _create_attack_event(self, session: SessionData) -> Optional[AttackEvent]:
        """
        Create AttackEvent from session data.

        Per D-03: Correlate connect, login, commands, close by session ID
        Per D-04: Classify using HASSH + command patterns
        Per D-05: GeoIP country lookup

        Args:
            session: Complete session data

        Returns:
            AttackEvent ready for emission
        """
        # GeoIP lookup
        country, country_code = self.geoip_service.get_country(session.src_ip)

        # Classification
        # Per D-14: HASSH + command pattern classification
        archetype = classify_attack(session.hassh, session.commands)

        # Protocol string
        protocol = "SSH" if session.dst_port == 2222 else "TELNET"

        # Raw log representation
        raw_log = f"[{protocol}] Session {session.session_id[:8]} from {session.src_ip}:{session.src_port} - {len(session.commands)} commands, {session.duration:.1f}s, {archetype}"

        return create_attack_event(
            ip=session.src_ip,
            country=country,
            countryCode=country_code,
            port=session.dst_port,
            protocol=protocol,
            archetype=archetype,
            commands=session.commands,
            duration=int(session.duration),
            rawLog=raw_log
        )

    def _log_attack(self, attack: AttackEvent) -> None:
        """Log attack to console with color."""
        log_msg = format_archetype_log(
            attack.archetype,
            attack.ip,
            attack.country,
            attack.duration,
            len(attack.commands)
        )
        print(log_msg)

    async def _emit_throttled(self) -> None:
        """
        Emit queued attacks with throttling.

        Per D-12: Throttled emission (1.5s buffer) to prevent UI flooding
        """
        if not self._emit_queue:
            return

        current_time = asyncio.get_event_loop().time()

        # Respect throttle interval
        if current_time - self._last_emit < self._throttle_interval:
            return

        # Emit all queued attacks
        for attack in self._emit_queue:
            if self._emit_callback:
                try:
                    await self._emit_callback(attack.model_dump())
                except Exception as e:
                    print(f"[CowrieReader] Emit error: {e}")

        self._emit_queue.clear()
        self._last_emit = current_time