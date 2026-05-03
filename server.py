#!/usr/bin/env python3
import socket
import subprocess
import json
import time
import threading
import os
import sys
from datetime import datetime

class KnockServer:
    def __init__(self, config_file='config.json'):
        if not os.path.exists(config_file):
            print(f"[-] Config file {config_file} not found")
            sys.exit(1)
        
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.sequence = self.config['knock_sequence']
        self.open_port = self.config['open_port']
        self.listen_ip = self.config['listen_ip']
        self.timeout = self.config['timeout_seconds']
        self.open_duration = self.config.get('open_duration', 60)
        
        self.current_position = 0
        self.last_knock_time = 0
        self.log_file = 'logs/knock.log'
        self.running = True
        
        os.makedirs('logs', exist_ok=True)
    
    def log(self, message, level='INFO'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry + '\n')
        
        if level == 'ALERT':
            print(f"\033[91m{log_entry}\033[0m")
        elif level == 'SUCCESS':
            print(f"\033[92m{log_entry}\033[0m")
        elif level == 'INFO':
            print(f"\033[94m{log_entry}\033[0m")
        else:
            print(log_entry)
    
    def check_iptables_rule(self):
        try:
            result = subprocess.run(['sudo', 'iptables', '-L', 'INPUT', '-n'], 
                                  capture_output=True, text=True)
            return f'dpt:{self.open_port}' in result.stdout and 'ACCEPT' in result.stdout
        except:
            return False
    
    def open_port_firewall(self):
        try:
            subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-p', 'tcp', 
                          '--dport', str(self.open_port), '-j', 'ACCEPT'], 
                          capture_output=True, check=True)
            self.log(f"Port {self.open_port} opened successfully", 'SUCCESS')
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to open port: {e}", 'ALERT')
            return False
    
    def close_port_firewall(self):
        try:
            subprocess.run(['sudo', 'iptables', '-D', 'INPUT', '-p', 'tcp', 
                          '--dport', str(self.open_port), '-j', 'ACCEPT'], 
                          capture_output=True, check=True)
            self.log(f"Port {self.open_port} closed", 'INFO')
            return True
        except:
            return False
    
    def auto_close(self):
        time.sleep(self.open_duration)
        
        if self.check_iptables_rule():
            self.close_port_firewall()
            self.log(f"Auto-closed port {self.open_port} after {self.open_duration}s", 'INFO')
    
    def reset_sequence(self):
        self.current_position = 0
        self.last_knock_time = 0
    
    def process_knock(self, src_ip, knocked_port):
        current_time = time.time()
        
        if current_time - self.last_knock_time > self.timeout:
            if self.current_position > 0:
                self.log(f"Knock timeout from {src_ip}, resetting sequence", 'INFO')
            self.reset_sequence()
        
        expected_port = self.sequence[self.current_position]
        
        if knocked_port == expected_port:
            self.current_position += 1
            self.last_knock_time = current_time
            self.log(f"Valid knock {self.current_position}/{len(self.sequence)} from {src_ip}:{knocked_port}", 'INFO')
            
            if self.current_position == len(self.sequence):
                self.log(f"COMPLETE SEQUENCE from {src_ip}! Opening port {self.open_port}", 'ALERT')
                
                if self.open_port_firewall():
                    threading.Thread(target=self.auto_close, daemon=True).start()
                
                self.reset_sequence()
        else:
            self.log(f"Invalid knock from {src_ip}:{knocked_port} (expected {expected_port})", 'INFO')
            self.reset_sequence()
    
    def start(self):
        self.log(f"KNOCKHARD Server starting...", 'SUCCESS')
        self.log(f"Listening on {self.listen_ip}:*", 'INFO')
        self.log(f"Knock sequence length: {len(self.sequence)}", 'INFO')
        self.log(f"Target port to open: {self.open_port}", 'INFO')
        self.log(f"Open duration: {self.open_duration}s", 'INFO')
        self.log(f"Knock timeout: {self.timeout}s", 'INFO')
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            sock.bind((self.listen_ip, 0))
            
            self.log("Raw socket created successfully", 'SUCCESS')
            
            while self.running:
                try:
                    packet, addr = sock.recvfrom(65535)
                    
                    if len(packet) >= 40:
                        src_ip = addr[0]
                        
                        tcp_header = packet[20:40]
                        dest_port = int.from_bytes(tcp_header[2:4], byteorder='big')
                        
                        if dest_port in self.sequence:
                            threading.Thread(target=self.process_knock, 
                                           args=(src_ip, dest_port), 
                                           daemon=True).start()
                except socket.timeout:
                    continue
                except Exception as e:
                    self.log(f"Socket error: {e}", 'ALERT')
                    
        except PermissionError:
            self.log("Permission denied. Run with sudo.", 'ALERT')
            sys.exit(1)
        except Exception as e:
            self.log(f"Failed to create raw socket: {e}", 'ALERT')
            sys.exit(1)
    
    def stop(self):
        self.running = False
        self.log("Server stopping...", 'INFO')
        
        if self.check_iptables_rule():
            self.close_port_firewall()

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("[-] Root required for raw socket and iptables")
        print("[*] Run: sudo python3 server.py")
        sys.exit(1)
    
    try:
        server = KnockServer()
        server.start()
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
        if 'server' in locals():
            server.stop()
        sys.exit(0)
