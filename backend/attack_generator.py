"""
Fake attack data generator for development and testing.

Per BACK-03: AttackGenerator produces fake attack events every 3-8 seconds
Per D-09: Console logging with colored archetype tags
"""

import random
from models import AttackEvent, Archetype, create_attack_event
from archetypes import (
    choose_archetype,
    choose_country,
    generate_ip,
    generate_attack_profile,
    generate_raw_log,
    format_archetype_log,
)


# Common ports for attack simulations
COMMON_PORTS: list[int] = [
    22,     # SSH
    80,     # HTTP
    443,    # HTTPS
    8080,   # HTTP Proxy/Alt HTTP
    3389,   # RDP
    3306,   # MySQL
    21,     # FTP
    23,     # Telnet
    25,     # SMTP
    445,    # SMB
]

# Port weights (SSH is most common for honeypot attacks)
PORT_WEIGHTS: list[int] = [
    40,     # SSH (40%)
    15,     # HTTP (15%)
    10,     # HTTPS (10%)
    10,     # 8080 (10%)
    5,      # RDP (5%)
    5,      # MySQL (5%)
    5,      # FTP (5%)
    5,      # Telnet (5%)
    3,      # SMTP (3%)
    2,      # SMB (2%)
]

# Protocol mapping for ports
PORT_PROTOCOL_MAP: dict[int, str] = {
    22: "SSH",
    80: "HTTP",
    443: "HTTPS",
    8080: "HTTP",
    3389: "RDP",
    3306: "MySQL",
    21: "FTP",
    23: "Telnet",
    25: "SMTP",
    445: "SMB",
}


def choose_port() -> int:
    """
    Select a random port using weighted selection.
    SSH is most common (40%), followed by HTTP/HTTPS.

    Returns:
        int: A port number
    """
    return random.choices(COMMON_PORTS, weights=PORT_WEIGHTS, k=1)[0]


def get_protocol(port: int) -> str:
    """
    Get the protocol name for a given port.

    Args:
        port: The port number

    Returns:
        str: Protocol name (e.g., "SSH", "HTTP")
    """
    return PORT_PROTOCOL_MAP.get(port, "TCP")


def generate_fake_attack() -> AttackEvent:
    """
    Generate a complete fake AttackEvent ready for Socket.io emission.

    Per BACK-03: Generates fake attack data with weighted archetype distribution
    Per BACK-04: Weighted archetype distribution (botnet_drone: 50%, etc.)
    Per BACK-05: AttackEvent contains all required fields
    Per BACK-06: IPs from TEST-NET ranges
    Per BACK-07: Countries weighted toward realistic attacker origins
    Per BACK-08: Archetype fingerprint rules for duration/commands

    Returns:
        AttackEvent: A complete attack event ready for emission
    """
    # Step 1: Choose archetype using weighted distribution
    archetype: Archetype = choose_archetype()

    # Step 2: Generate attack profile (duration, commands, rawLog template)
    duration, commands, raw_log_template = generate_attack_profile(archetype)

    # Step 3: Choose country using weighted distribution
    country, country_code = choose_country()

    # Step 4: Generate fake IP from TEST-NET ranges
    ip = generate_ip()

    # Step 5: Choose port and protocol
    port = choose_port()
    protocol = get_protocol(port)

    # Step 6: Regenerate raw log with actual IP
    raw_log = generate_raw_log(archetype, ip, commands, duration)

    # Step 7: Create the complete AttackEvent
    attack_event = create_attack_event(
        ip=ip,
        country=country,
        countryCode=country_code,
        port=port,
        protocol=protocol,
        archetype=archetype,
        commands=commands,
        duration=duration,
        rawLog=raw_log
    )

    # Step 8: Log to console with colored archetype tag (per D-09)
    log_message = format_archetype_log(archetype, ip, country, duration, len(commands))
    print(log_message)

    return attack_event


# For testing the generator standalone
if __name__ == "__main__":
    print("Generating 10 fake attacks for testing...\n")
    for i in range(10):
        attack = generate_fake_attack()
        print(f"  ID: {attack.id}")
        print(f"  Archetype: {attack.archetype}")
        print(f"  IP: {attack.ip}")
        print(f"  Country: {attack.country} ({attack.countryCode})")
        print(f"  Port: {attack.port} ({attack.protocol})")
        print(f"  Duration: {attack.duration}s")
        print(f"  Commands: {len(attack.commands)}")
        print(f"  Log: {attack.rawLog[:80]}...")
        print()