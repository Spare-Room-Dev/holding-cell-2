#!/bin/bash
# UFW Firewall Setup for The Holding Cell VPS
# Per D-09: UFW for port management
# Per D-10: Admin SSH on port 2244
# Per D-11: Cowrie honeypot ports 22 and 23 publicly accessible
# Per D-12: HTTPS port 443 exposed
# Per D-13: Port 80 for Let's Encrypt ACME challenges
# Per D-14: All other ports closed by default

set -e

echo "=== UFW Firewall Setup for The Holding Cell ==="
echo ""
echo "This script will configure UFW to allow:"
echo "  - Port 2244/tcp: Admin SSH"
echo "  - Port 22/tcp:   Cowrie SSH honeypot"
echo "  - Port 23/tcp:   Cowrie Telnet honeypot"
echo "  - Port 80/tcp:   HTTP (ACME challenges)"
echo "  - Port 443/tcp:  HTTPS (dashboard)"
echo ""
echo "All other ports will be BLOCKED."
echo ""

# Safety check: ensure we're not locking ourselves out
read -p "Have you updated SSH to listen on port 2244? (y/N): " CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo ""
    echo "ABORTING: Configure SSH to listen on port 2244 first!"
    echo "Edit /etc/ssh/sshd_config: Port 2244"
    echo "Then restart SSH: sudo systemctl restart sshd"
    exit 1
fi

# Reset UFW to defaults (DANGER: this removes all existing rules)
echo ""
echo "Resetting UFW to defaults..."
sudo ufw --force reset

# Set default policies
echo "Setting default policies..."
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow Admin SSH (MUST be first to prevent lockout)
echo "Allowing admin SSH on port 2244..."
sudo ufw allow 2244/tcp comment 'Admin SSH'

# Allow Cowrie honeypot ports (public attack surface)
echo "Allowing Cowrie SSH honeypot on port 22..."
sudo ufw allow 22/tcp comment 'Cowrie SSH honeypot'

echo "Allowing Cowrie Telnet honeypot on port 23..."
sudo ufw allow 23/tcp comment 'Cowrie Telnet honeypot'

# Allow HTTP for Let's Encrypt ACME challenges
echo "Allowing HTTP on port 80 (ACME challenges)..."
sudo ufw allow 80/tcp comment 'HTTP/ACME'

# Allow HTTPS for dashboard access
echo "Allowing HTTPS on port 443..."
sudo ufw allow 443/tcp comment 'HTTPS'

# Enable firewall
echo ""
echo "Enabling UFW..."
sudo ufw --force enable

# Show status
echo ""
echo "=== UFW Status ==="
sudo ufw status numbered

echo ""
echo "=== Firewall Setup Complete ==="
echo ""
echo "Allowed ports:"
echo "  - 2244/tcp: Admin SSH"
echo "  - 22/tcp:   Cowrie SSH honeypot"
echo "  - 23/tcp:   Cowrie Telnet honeypot"
echo "  - 80/tcp:   HTTP (ACME challenges)"
echo "  - 443/tcp:  HTTPS (dashboard)"
echo ""
echo "Verify SSH access on port 2244 before logging out!"