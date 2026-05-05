# KNOCKHARD - Professional Port Knocking Suite

## Developed by Abhishek



## What is Port Knocking?

Port knocking is a stealth method to hide services behind a firewall.  
All ports appear closed until a secret sequence of "knocks" (connection attempts)  
is received in the correct order.
## Features

| Feature | Description |
|---------|-------------|
| Raw socket listener | Stealth, no open ports |
| iptables integration | Dynamic firewall rules |
| Full logging | All knock attempts logged |
| Auto-close | Port closes automatically |
| Configurable sequence | Any ports, any length |
| Client with flags | Command line support |

## Installation

```bash
git clone https://github.com/abhiexploits/KNOCKHARD.git
cd KNOCKHARD
sudo chmod +x setup.sh
sudo ./setup.sh
```

Configuration

Edit config.json:

```json
{
    "knock_sequence": [10001, 10002, 10003, 10004, 10005],
    "open_port": 22,
    "timeout_seconds": 10,
    "open_duration": 60,
    "target_ip": "192.168.1.100"
}
```

Usage

Start Server (Target Machine)

```bash
sudo python3 server.py
```

Send Knock (Attacker Machine)

```bash
python3 client.py
```
