#!/bin/bash

echo "══════════════════════════════════════════════════════"
echo "  KNOCKHARD - Port Knocking Suite Installer"
echo "══════════════════════════════════════════════════════"

if [ "$EUID" -ne 0 ]; then 
    echo "[!] Please run as root: sudo ./setup.sh"
    exit 1
fi

echo "[*] Updating packages..."
apt update -y

echo "[*] Installing Python3..."
apt install python3 -y

echo "[*] Installing iptables..."
apt install iptables -y

echo "[*] Creating directories..."
mkdir -p logs

echo "[*] Setting permissions..."
chmod +x server.py client.py

echo ""
echo "══════════════════════════════════════════════════════"
echo "  INSTALLATION COMPLETE"
echo "══════════════════════════════════════════════════════"
echo ""
echo "CONFIGURATION:"
echo "  Edit config.json to set:"
echo "    - knock_sequence (ports to knock)"
echo "    - open_port (port to open after knock)"
echo "    - target_ip (for client)"
echo ""
echo "TO START SERVER (on target machine):"
echo "  sudo python3 server.py"
echo ""
echo "TO SEND KNOCK (from attacker machine):"
echo "  python3 client.py"
echo ""
echo "  Or with custom target:"
echo "  python3 client.py -t 192.168.1.100"
echo ""
echo "TO TEST ON LOCALHOST:"
echo "  Terminal 1: sudo python3 server.py"
echo "  Terminal 2: python3 client.py -t 127.0.0.1"
echo "  Then try: ssh localhost -p 22"
echo ""
