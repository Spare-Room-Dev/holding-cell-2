"""
Pydantic models for AttackEvent.

Per BACK-05: AttackEvent includes all required fields for fake attack data.
Per D-10-D-13: This Python model should be kept in sync with frontend/src/types/attack.ts
"""

from pydantic import BaseModel
from typing import Literal
from datetime import datetime
import uuid


# Archetype type alias - Literal union of all 5 archetypes
Archetype = Literal[
    "script_kiddie",
    "botnet_drone",
    "apt_operative",
    "iot_worm",
    "hacktivist"
]


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