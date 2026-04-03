"""
Pydantic models for AttackEvent.

Per BACK-05: AttackEvent includes all required fields for fake attack data.
Per D-10-D-13: This Python model should be kept in sync with frontend/src/types/attack.ts
Per SEC-05: Input validation for untrusted Cowrie log data
"""

from pydantic import BaseModel, field_validator
from typing import Literal
from datetime import datetime
import uuid
import re


# Archetype type alias - Literal union of all 5 archetypes
Archetype = Literal[
    "script_kiddie",
    "botnet_drone",
    "apt_operative",
    "iot_worm",
    "hacktivist"
]


# Per SEC-05: IP address regex pattern (IPv4)
IPV4_PATTERN = re.compile(
    r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
    r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
)

# Per SEC-05: ISO 3166-1 alpha-2 country code pattern
COUNTRY_CODE_PATTERN = re.compile(r'^[A-Z]{2}$')

# Per SEC-05: Maximum command length to prevent memory exhaustion
MAX_COMMAND_LENGTH = 2048

# Per SEC-05: Maximum number of commands per session
MAX_COMMANDS_COUNT = 100


class AttackEvent(BaseModel):
    """
    AttackEvent model representing a honeypot attack.

    Fields per BACK-05:
    - id: UUID string for unique identification
    - timestamp: ISO 8601 formatted timestamp
    - ip: Source IP address (from TEST-NET ranges per BACK-06)
    - country: Full country name
    - countryCode: ISO 3166-1 alpha-2 country code
    - port: Target port number
    - protocol: Protocol name (SSH, HTTP, HTTPS)
    - archetype: Behavioral classification
    - commands: List of commands attempted
    - duration: Session duration in seconds
    - rawLog: Original fake log line
    """
    id: str
    timestamp: str
    ip: str
    country: str
    countryCode: str
    port: int
    protocol: str
    archetype: Archetype
    commands: list[str]
    duration: int  # seconds
    rawLog: str

    # Per SEC-05: Validate IP address format
    @field_validator('ip')
    @classmethod
    def validate_ip(cls, v: str) -> str:
        if not IPV4_PATTERN.match(v):
            # Log warning but allow through (defense in depth)
            # Invalid IPs from Cowrie are unlikely but handle gracefully
            print(f"[SEC-05] Warning: Invalid IP format: {v}")
        return v

    # Per SEC-05: Validate port range
    @field_validator('port')
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (0 <= v <= 65535):
            raise ValueError(f"Port {v} out of valid range 0-65535")
        return v

    # Per SEC-05: Validate country code format
    @field_validator('countryCode')
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        if v and not COUNTRY_CODE_PATTERN.match(v):
            # Log warning but allow unknown (GeoIP DB might return non-standard)
            print(f"[SEC-05] Warning: Invalid country code format: {v}")
        return v

    # Per SEC-05: Validate commands list
    @field_validator('commands')
    @classmethod
    def validate_commands(cls, v: list[str]) -> list[str]:
        if len(v) > MAX_COMMANDS_COUNT:
            print(f"[SEC-05] Warning: Truncating commands from {len(v)} to {MAX_COMMANDS_COUNT}")
            v = v[:MAX_COMMANDS_COUNT]
        # Truncate individual commands
        return [cmd[:MAX_COMMAND_LENGTH] if len(cmd) > MAX_COMMAND_LENGTH else cmd for cmd in v]

    # Per SEC-05: Validate duration
    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v: int) -> int:
        if v < 0:
            return 0
        if v > 86400:  # Max 24 hours in seconds
            print(f"[SEC-05] Warning: Unusual duration {v}s, capping at 86400")
            return 86400
        return v


def create_attack_event(
    ip: str,
    country: str,
    countryCode: str,
    port: int,
    protocol: str,
    archetype: Archetype,
    commands: list[str],
    duration: int,
    rawLog: str
) -> AttackEvent:
    """
    Factory function to create an AttackEvent with auto-generated id and timestamp.

    Generates:
    - id: UUID v4 string
    - timestamp: Current UTC time in ISO 8601 format with 'Z' suffix

    Args:
        ip: Source IP address
        country: Full country name
        countryCode: ISO 3166-1 alpha-2 code
        port: Target port number
        protocol: Protocol name
        archetype: Behavioral archetype classification
        commands: List of commands attempted
        duration: Session duration in seconds
        rawLog: Original log line text

    Returns:
        AttackEvent instance ready for Socket.io emission
    """
    return AttackEvent(
        id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat() + "Z",
        ip=ip,
        country=country,
        countryCode=countryCode,
        port=port,
        protocol=protocol,
        archetype=archetype,
        commands=commands,
        duration=duration,
        rawLog=rawLog
    )