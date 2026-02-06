import os
import requests
import json
import re
import socket
import concurrent.futures
import ssl
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

TARGETS = [
    {"url": "https://bridges.torproject.org/bridges?transport=obfs4", "file": "obfs4.txt", "type": "obfs4", "ip": "IPv4"},
    {"url": "https://bridges.torproject.org/bridges?transport=webtunnel", "file": "webtunnel.txt", "type": "WebTunnel", "ip": "IPv4"},
    {"url": "https://bridges.torproject.org/bridges?transport=vanilla", "file": "vanilla.txt", "type": "Vanilla", "ip": "IPv4"},
    {"url": "https://bridges.torproject.org/bridges?transport=obfs4&ipv6=yes", "file": "obfs4_ipv6.txt", "type": "obfs4", "ip": "IPv6"},
    {"url": "https://bridges.torproject.org/bridges?transport=webtunnel&ipv6=yes", "file": "webtunnel_ipv6.txt", "type": "WebTunnel", "ip": "IPv6"},
    {"url": "https://bridges.torproject.org/bridges?transport=vanilla&ipv6=yes", "file": "vanilla_ipv6.txt", "type": "Vanilla", "ip": "IPv6"},
]

HISTORY_FILE = "bridge_history.json"
RECENT_HOURS = 72
HISTORY_RETENTION_DAYS = 30
REPO_URL = "https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main"
MAX_WORKERS = 50
CONNECTION_TIMEOUT = 8
MAX_RETRIES = 2
SSL_TIMEOUT = 5

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def is_valid_bridge_line(line):
    line = line.strip()
    if not line:
        return False
    if "No bridges available" in line:
        return False
    if line.startswith("#"):
        return False
    if len(line) < 10:
        return False
    return True

def get_ip_port(line):
    line = line.strip()
    
    if line.startswith("https://"):
        match = re.search(r'https?://([^/:]+)(?::(\d+))?', line, re.IGNORECASE)
        if match:
            host = match.group(1)
            port = int(match.group(2)) if match.group(2) else 443
            return host, port
    
    ipv6_match = re.search(r'\[([0-9a-fA-F:]+)\]:(\d+)', line)
    if ipv6_match:
        return ipv6_match.group(1), int(ipv6_match.group(2))
    
    ipv4_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)', line)
    if ipv4_match:
        return ipv4_match.group(1), int(ipv4_match.group(2))
    
    simple_match = re.search(r'([^:\s]+):(\d+)', line)
    if simple_match:
        return simple_match.group(1), int(simple_match.group(2))
    
    return None, None

def test_bridge_connection(line):
    host, port = get_ip_port(line)
    if not host or not port:
        return False
    
    for attempt in range(MAX_RETRIES):
        try:
            if "https://" in line.lower() or "webtunnel" in line.lower():
                sock = socket.create_connection((host, port), timeout=CONNECTION_TIMEOUT)
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                ssl_sock = context.wrap_socket(sock, server_hostname=host)
                ssl_sock.settimeout(SSL_TIMEOUT)
                ssl_sock.close()
            else:
                sock = socket.create_connection((host, port), timeout=CONNECTION_TIMEOUT)
                sock.close()
            return True
        except:
            if attempt < MAX_RETRIES - 1:
                time.sleep(0.5)
    return False

def load_history():
    bridges_dir = "bridges"
    history_path = os.path.join(bridges_dir, HISTORY_FILE) if os.path.exists(bridges_dir) else HISTORY_FILE
    
    if os.path.exists(history_path):
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_history(history):
    bridges_dir = "bridges"
    history_path = os.path.join(bridges_dir, HISTORY_FILE) if os.path.exists(bridges_dir) else HISTORY_FILE
    
    try:
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        log(f"Error saving history: {e}")

def cleanup_history(history):
    cutoff = datetime.now() - timedelta(days=HISTORY_RETENTION_DAYS)
    return {k: v for k, v in history.items() if datetime.fromisoformat(v) > cutoff}

def count_file_lines(filepath):
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return sum(1 for line in f if line.strip())
        return 0
    except:
        return 0

def update_readme(stats):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    
    readme_content = f"""# Tor Bridges Collector & Archive

**Last Updated:** {timestamp}

## 📊 Overall Statistics
| Metric | Count |
|--------|-------|
| Total Bridges Collected | {stats.get('total_all', 0)} |
| Successfully Tested | {stats.get('total_tested', 0)} |
| New Bridges (72h) | {stats.get('total_recent', 0)} |
| History Retention | {HISTORY_RETENTION_DAYS} days |

This repository automatically collects, validates, and archives Tor bridges.

## 🔥 Bridge Lists

### ✅ Tested & Active
| Transport | IPv4 (Tested) | Count | IPv6 (Tested) | Count |
| :--- | :--- | :--- | :--- | :--- |
| **obfs4** | [obfs4_tested.txt]({REPO_URL}/bridges/obfs4_tested.txt) | **{stats.get('obfs4_tested.txt', 0)}** | [obfs4_ipv6_tested.txt]({REPO_URL}/bridges/obfs4_ipv6_tested.txt) | **{stats.get('obfs4_ipv6_tested.txt', 0)}** |
| **WebTunnel** | [webtunnel_tested.txt]({REPO_URL}/bridges/webtunnel_tested.txt) | **{stats.get('webtunnel_tested.txt', 0)}** | [webtunnel_ipv6_tested.txt]({REPO_URL}/bridges/webtunnel_ipv6_tested.txt) | **{stats.get('webtunnel_ipv6_tested.txt', 0)}** |
| **Vanilla** | [vanilla_tested.txt]({REPO_URL}/bridges/vanilla_tested.txt) | **{stats.get('vanilla_tested.txt', 0)}** | [vanilla_ipv6_tested.txt]({REPO_URL}/bridges/vanilla_ipv6_tested.txt) | **{stats.get('vanilla_ipv6_tested.txt', 0)}** |

### 🔥 Fresh Bridges (Last 72 Hours)
| Transport | IPv4 (72h) | Count | IPv6 (72h) | Count |
| :--- | :--- | :--- | :--- | :--- |
| **obfs4** | [obfs4_72h.txt]({REPO_URL}/bridges/obfs4_72h.txt) | **{stats.get('obfs4_72h.txt', 0)}** | [obfs4_ipv6_72h.txt]({REPO_URL}/bridges/obfs4_ipv6_72h.txt) | **{stats.get('obfs4_ipv6_72h.txt', 0)}** |
| **WebTunnel** | [webtunnel_72h.txt]({REPO_URL}/bridges/webtunnel_72h.txt) | **{stats.get('webtunnel_72h.txt', 0)}** | [webtunnel_ipv6_72h.txt]({REPO_URL}/bridges/webtunnel_ipv6_72h.txt) | **{stats.get('webtunnel_ipv6_72h.txt', 0)}** |
| **Vanilla** | [vanilla_72h.txt]({REPO_URL}/bridges/vanilla_72h.txt) | **{stats.get('vanilla_72h.txt', 0)}** | [vanilla_ipv6_72h.txt]({REPO_URL}/bridges/vanilla_ipv6_72h.txt) | **{stats.get('vanilla_ipv6_72h.txt', 0)}** |

### 📁 Full Archive
| Transport | IPv4 (All Time) | Count | IPv6 (All Time) | Count |
| :--- | :--- | :--- | :--- | :--- |
| **obfs4** | [obfs4.txt]({REPO_URL}/bridges/obfs4.txt) | **{stats.get('obfs4.txt', 0)}** | [obfs4_ipv6.txt]({REPO_URL}/bridges/obfs4_ipv6.txt) | **{stats.get('obfs4_ipv6.txt', 0)}** |
| **WebTunnel** | [webtunnel.txt]({REPO_URL}/bridges/webtunnel.txt) | **{stats.get('webtunnel.txt', 0)}** | [webtunnel_ipv6.txt]({REPO_URL}/bridges/webtunnel_ipv6.txt) | **{stats.get('webtunnel_ipv6.txt', 0)}** |
| **Vanilla** | [vanilla.txt]({REPO_URL}/bridges/vanilla.txt) | **{stats.get('vanilla.txt', 0)}** | [vanilla_ipv6.txt]({REPO_URL}/bridges/vanilla_ipv6.txt) | **{stats.get('vanilla_ipv6.txt', 0)}** |

## 🔥 Disclaimer
This project is for educational and archival purposes.
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    log("README.md updated.")

def main():
    bridges_dir = "bridges"
    if not os.path.exists(bridges_dir):
        os.makedirs(bridges_dir)
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    
    history = load_history()
    history = cleanup_history(history)
    
    recent_cutoff_time = datetime.now() - timedelta(hours=RECENT_HOURS)
    stats = {}
    
    log("Starting bridge collection...")

    for target in TARGETS:
        url = target["url"]
        filename = os.path.join(bridges_dir, target["file"])
        recent_filename = os.path.join(bridges_dir, target["file"].replace(".txt", f"_{RECENT_HOURS}h.txt"))
        tested_filename = os.path.join(bridges_dir, target["file"].replace(".txt", "_tested.txt"))
        
        existing_bridges = []
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    existing_bridges = [line.strip() for line in f if is_valid_bridge_line(line)]
            except:
                existing_bridges = []
        
        fetched_bridges = []
        try:
            response = session.get(url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                bridge_div = soup.find("div", id="bridgelines")
                
                if bridge_div:
                    raw_text = bridge_div.get_text()
                    for line in raw_text.split("\n"):
                        line = line.strip()
                        if is_valid_bridge_line(line):
                            fetched_bridges.append(line)
                            if line not in history:
                                history[line] = datetime.now().isoformat()
        except Exception as e:
            log(f"Error fetching {url}: {e}")
            continue

        all_bridges = list(set(existing_bridges + fetched_bridges))
        
        with open(filename, "w", encoding="utf-8") as f:
            for bridge in sorted(all_bridges):
                f.write(bridge + "\n")
        
        recent_bridges = []
        for bridge in all_bridges:
            if bridge in history:
                try:
                    first_seen = datetime.fromisoformat(history[bridge])
                    if first_seen > recent_cutoff_time:
                        recent_bridges.append(bridge)
                except:
                    pass
        
        with open(recent_filename, "w", encoding="utf-8") as f:
            for bridge in sorted(recent_bridges):
                f.write(bridge + "\n")
        
        tested_bridges = []
        if all_bridges:
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                future_to_bridge = {executor.submit(test_bridge_connection, bridge): bridge for bridge in all_bridges}
                for future in concurrent.futures.as_completed(future_to_bridge):
                    bridge = future_to_bridge[future]
                    try:
                        if future.result():
                            tested_bridges.append(bridge)
                    except:
                        pass
        
        with open(tested_filename, "w", encoding="utf-8") as f:
            for bridge in sorted(tested_bridges):
                f.write(bridge + "\n")
        
        base_filename = os.path.basename(filename)
        base_recent = os.path.basename(recent_filename)
        base_tested = os.path.basename(tested_filename)
        
        stats[base_filename] = len(all_bridges)
        stats[base_recent] = len(recent_bridges)
        stats[base_tested] = len(tested_bridges)
        
        log(f"{target['type']} ({target['ip']}): {len(all_bridges)} total, {len(recent_bridges)} recent, {len(tested_bridges)} working")

    save_history(history)
    
    stats['total_all'] = sum(stats.get(f, 0) for f in ['obfs4.txt', 'webtunnel.txt', 'vanilla.txt', 
                                                       'obfs4_ipv6.txt', 'webtunnel_ipv6.txt', 'vanilla_ipv6.txt'])
    stats['total_tested'] = sum(stats.get(f, 0) for f in ['obfs4_tested.txt', 'webtunnel_tested.txt', 'vanilla_tested.txt',
                                                          'obfs4_ipv6_tested.txt', 'webtunnel_ipv6_tested.txt', 'vanilla_ipv6_tested.txt'])
    stats['total_recent'] = sum(stats.get(f, 0) for f in ['obfs4_72h.txt', 'webtunnel_72h.txt', 'vanilla_72h.txt',
                                                          'obfs4_ipv6_72h.txt', 'webtunnel_ipv6_72h.txt', 'vanilla_ipv6_72h.txt'])
    
    log(f"\nTotal bridges: {stats['total_all']}")
    log(f"Working bridges: {stats['total_tested']}")
    log(f"Recent bridges (72h): {stats['total_recent']}")
    
    update_readme(stats)
    log("Done!")

if __name__ == "__main__":
    main()
