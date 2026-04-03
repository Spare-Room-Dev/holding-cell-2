# The Holding Cell

A real-time security visualization that transforms honeypot attacks into an animated pixel-art jail.

## The Idea

Every day, automated bots and malicious actors scan the internet for vulnerable servers. They try common passwords, probe open ports, and attempt to break in. Most of this happens invisibly.

**What if you could see it happen?**

The Holding Cell takes SSH and Telnet connection attempts from a Cowrie honeypot and visualizes them as pixel-art "bandits" being thrown into a jail cell. Each attacker appears with their country of origin, the method they used, and when they tried to connect.

## Why I Built This

I wanted to make network security visible and engaging. Traditional security logs are dense text files - hard to parse, harder to care about. By turning attacks into animated sprites, the data becomes something you actually want to watch.

It's part security monitoring, part art project, part reminder that the internet is a hostile place.

## What You See

- **Attackers arrive in real-time** - Each connection attempt spawns a new sprite
- **Country flags** - GeoIP lookup shows where attacks originate
- **Attack methods** - SSH brute force, Telnet probes, credential attempts
- **Persistent jail population** - The cell fills up as attacks accumulate

## The Concept

The jail cell metaphor is intentional. These aren't real criminals - they're mostly automated bots running scripts. But they're also not welcome visitors. The "holding cell" treats them with a degree of whimsy while acknowledging their hostile intent.

## Running It

This project is designed to run on a dedicated server with a Cowrie honeypot exposed to the internet. It's not something you deploy on your main production server.

If you're interested in the technical setup, feel free to reach out.

## Acknowledgments

- [Cowrie](https://github.com/cowrie/cowrie) - The SSH/Telnet honeypot that captures the attacks
- [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) - IP geolocation data

---

*A window into the constant background noise of the internet's darker traffic.*