#!/bin/bash
# Create htpasswd file for HTTP Basic Auth
# Per D-01: HTTP Basic Auth with username/password
# Per D-02: htpasswd file stored at /etc/nginx/.htpasswd
# Per D-03: Single admin user for initial deployment

set -e

HTPASSWD_FILE="/etc/nginx/.htpasswd"

# Check if htpasswd utility is installed
if ! command -v htpasswd &> /dev/null; then
    echo "Installing apache2-utils (htpasswd utility)..."
    sudo apt update
    sudo apt install -y apache2-utils
fi

# Check if .env file exists and has ADMIN_USER
if [ -f ".env" ]; then
    ADMIN_USER=$(grep -E "^ADMIN_USER=" .env | cut -d'=' -f2 || echo "admin")
else
    ADMIN_USER="admin"
fi

# Prompt for username (default: admin)
read -p "Enter admin username [${ADMIN_USER}]: " USERNAME
USERNAME=${USERNAME:-$ADMIN_USER}

# Create htpasswd file with bcrypt hash
# -c: create new file
# -B: bcrypt hashing (required for security)
sudo htpasswd -cB "$HTPASSWD_FILE" "$USERNAME"

# Set correct permissions (per D-02)
# Owner: root, Group: nginx (or www-data on some systems)
sudo chown root:www-data "$HTPASSWD_FILE"
sudo chmod 640 "$HTPASSWD_FILE"

echo ""
echo "htpasswd file created at $HTPASSWD_FILE"
echo "Permissions: 640 (owner read/write, group read)"
echo ""
echo "To add additional users:"
echo "  sudo htpasswd -B $HTPASSWD_FILE <username>"