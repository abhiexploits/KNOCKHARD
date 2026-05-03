#!/usr/bin/env python3
import socket
import time
import json
import sys
import argparse

class KnockClient:
    def __init__(self, config_file='config.json'):
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"[-] Config file {config_file} not found")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"[-] Invalid JSON in {config_file}")
            sys.exit(1)
        
        self.sequence = self.config['knock_sequence']
        self.target = self.config['target_ip']
        self.timeout = self.config.get('client_timeout', 2)
        self.delay = self.config.get('knock_delay', 0.1)
    
    def send_knock(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            sock.sendto(b'K', (self.target, port))
            sock.close()
            return True
        except socket.timeout:
            print(f"    Timeout on port {port}")
            return False
        except Exception as e:
            print(f"    Failed on port {port}: {e}")
            return False
    
    def test_port_open(self, port, timeout=5):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((self.target, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def execute(self, verbose=True):
        if verbose:
            print(f"\n{'='*50}")
            print(f"KNOCKHARD Client")
            print(f"{'='*50}")
            print(f"[*] Target: {self.target}")
            print(f"[*] Sequence: {self.sequence}")
            print(f"[*] Knock delay: {self.delay}s")
            print(f"{'='*50}\n")
        
        successful = 0
        for i, port in enumerate(self.sequence, 1):
            print(f"  [{i}/{len(self.sequence)}] Knocking port {port}...", end=' ')
            
            if self.send_knock(port):
                print("OK")
                successful += 1
            else:
                print("FAILED")
            
            if i < len(self.sequence):
                time.sleep(self.delay)
        
        print(f"\n[+] Knocks sent: {successful}/{len(self.sequence)}")
        
        if successful == len(self.sequence):
            print(f"[+] Sequence complete!")
            print(f"[*] Waiting {self.timeout}s for port to open...")
            time.sleep(2)
            
            target_port = self.config['open_port']
            if self.test_port_open(target_port):
                print(f"\n[SUCCESS] Port {target_port} is NOW OPEN!")
                print(f"[*] You can now connect:")
                print(f"    ssh root@{self.target} -p {target_port}")
                print(f"    nc {self.target} {target_port}")
            else:
                print(f"\n[WARNING] Port {target_port} still closed")
                print(f"[*] Check if server is running and sequence matches")
        else:
            print(f"\n[FAILED] Not all knocks delivered")
        
        return successful == len(self.sequence)

def main():
    parser = argparse.ArgumentParser(description='KNOCKHARD - Port Knocking Client')
    parser.add_argument('-c', '--config', default='config.json', help='Config file path')
    parser.add_argument('-t', '--target', help='Target IP (overrides config)')
    parser.add_argument('-s', '--sequence', help='Knock sequence (comma separated, overrides config)')
    parser.add_argument('--delay', type=float, help='Delay between knocks in seconds')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode')
    
    args = parser.parse_args()
    
    client = KnockClient(args.config)
    
    if args.target:
        client.target = args.target
    if args.sequence:
        client.sequence = [int(p.strip()) for p in args.sequence.split(',')]
    if args.delay:
        client.delay = args.delay
    
    success = client.execute(verbose=not args.quiet)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
