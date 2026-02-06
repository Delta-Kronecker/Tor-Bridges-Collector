import os
import requests
import json
import re
import socket
import concurrent.futures
import ssl
import time
import ipaddress
from urllib.parse import urlparse
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
MAX_TEST_PER_TYPE = 500

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def is_valid_bridge_line(line):
    if "No bridges available" in line:
        return False
    if line.startswith("#"):
        return False
    if len(line) < 10:
        return False
    return bool(re.search(r'\d+\.\d+\.\d+\.\d+|\[.*\]|https?://', line))

def extract_connection_info(line):
    line = line.strip()
    
    if not line or len(line) < 5:
        return None, None, None
    
    line_lower = line.lower()
    
    if "obfs4" in line_lower:
        transport = "obfs4"
    elif "webtunnel" in line_lower or "https://" in line_lower:
        transport = "webtunnel"
    else:
        transport = "vanilla"
    
    patterns = [
        (r'https?://\[([0-9a-fA-F:]+)\](?::(\d+))?', "ipv6"),
        (r'https?://([^/:]+)(?::(\d+))?', "domain"),
        (r'\[([0-9a-fA-F:]+)\]:(\d+)', "ipv6"),
        (r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)', "ipv4"),
        (r'([a-zA-Z0-9.-]+):(\d+)', "domain"),
        (r'obfs4\s+([^:]+):(\d+)\s+', "obfs4"),
        (r'(\S+)\s+(\S+)\s+(\S+)', "fingerprint"),
    ]
    
    for pattern, ptype in patterns:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            if ptype == "fingerprint" and len(match.groups()) >= 3:
                host = match.group(1)
                port = match.group(2)
                return host, int(port), transport
            elif len(match.groups()) >= 2:
                host = match.group(1)
                port = match.group(2) if match.group(2) else "443"
                return host, int(port), transport
            elif ptype in ["domain", "ipv6"]:
                host = match.group(1)
                port = "443" if "https" in line_lower else "80"
                return host, int(port), transport
    
    return None, None, transport

def is_valid_ip(host):
    try:
        ipaddress.ip_address(host)
        return True
    except:
        return False

def resolve_host(host):
    try:
        return socket.gethostbyname(host)
    except:
        return None

def test_tcp_socket(host, port, timeout):
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.settimeout(1)
        
        try:
            sock.send(b"\x00")
            sock.recv(1)
        except:
            pass
        
        sock.close()
        return True
    except:
        return False

def test_ssl_socket(host, port, timeout):
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        ssl_sock = context.wrap_socket(sock, server_hostname=host)
        ssl_sock.settimeout(SSL_TIMEOUT)
        
        try:
            ssl_sock.send(b"GET / HTTP/1.0\r\n\r\n")
            ssl_sock.recv(1024)
        except:
            pass
        
        ssl_sock.close()
        return True
    except:
        return False

def advanced_connection_test(bridge_line):
    host, port, transport = extract_connection_info(bridge_line)
    
    if not host or not port:
        return False
    
    if transport == "webtunnel":
        test_func = test_ssl_socket
        timeout = CONNECTION_TIMEOUT
        default_port = 443
    else:
        test_func = test_tcp_socket
        timeout = CONNECTION_TIMEOUT
        default_port = 9001 if transport == "obfs4" else 443
    
    if port == 0:
        port = default_port
    
    test_hosts = []
    
    if is_valid_ip(host):
        test_hosts.append(host)
    else:
        resolved = resolve_host(host)
        if resolved:
            test_hosts.append(resolved)
        test_hosts.append(host)
    
    for test_host in test_hosts:
        for attempt in range(MAX_RETRIES):
            try:
                if test_func(test_host, port, timeout):
                    return True
            except:
                pass
            
            if attempt < MAX_RETRIES - 1:
                time.sleep(0.3 * (attempt + 1))
    
    return False

def smart_bridge_filter(bridge_list, transport_type):
    if not bridge_list:
        return []
    
    if len(bridge_list) > MAX_TEST_PER_TYPE:
        bridge_list = bridge_list[:MAX_TEST_PER_TYPE]
    
    unique_bridges = []
    seen = set()
    
    for bridge in bridge_list:
        key = re.sub(r'\s+', ' ', bridge.strip()).lower()
        if key not in seen:
            seen.add(key)
            unique_bridges.append(bridge)
    
    return unique_bridges

def batch_test_bridges(bridge_list, transport_type, batch_size=100):
    if not bridge_list:
        return []
    
    filtered_bridges = smart_bridge_filter(bridge_list, transport_type)
    
    if not filtered_bridges:
        return []
    
    working_bridges = []
    total = len(filtered_bridges)
    
    for i in range(0, total, batch_size):
        batch = filtered_bridges[i:i + batch_size]
        batch_working = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(batch))) as executor:
            future_to_bridge = {executor.submit(advanced_connection_test, bridge): bridge for bridge in batch}
            
            for future in concurrent.futures.as_completed(future_to_bridge):
                bridge = future_to_bridge[future]
                try:
                    if future.result():
                        batch_working.append(bridge)
                except:
                    pass
        
        working_bridges.extend(batch_working)
        
        if len(batch_working) > 0:
            log(f"   Batch {i//batch_size + 1}: {len(batch_working)}/{len(batch)} bridges working")
    
    return working_bridges

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        log(f"Error saving history: {e}")

def cleanup_history(history):
    cutoff = datetime.now() - timedelta(days=HISTORY_RETENTION_DAYS)
    new_history = {
        k: v for k, v in history.items() 
        if datetime.fromisoformat(v) > cutoff
    }
    return new_history

def update_readme(stats):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    
    readme_content = f"""# Tor Bridges Collector & Archive

**Last Updated:** {timestamp}

This repository automatically collects, validates, and archives Tor bridges. A GitHub Action runs every 1 hours to fetch new bridges from the official Tor Project.

## 🔥 Important Notes on IPv6 & WebTunnel

1.  **IPv6 Instability:** IPv6 bridges are significantly fewer in number and are often more susceptible to blocking or connection instability compared to IPv4.
2.  **WebTunnel Overlap:** WebTunnel bridges often use the same endpoint domain for both IPv4 and IPv6. Consequently, the IPv6 list is frequently identical to or a subset of the IPv4 list.
3.  **Recommendation:** For the most reliable connection, **prioritize using IPv4 bridges**. Use IPv6 only if IPv4 is completely inaccessible on your network.

## 🔥 Bridge Lists

### ✅ Tested & Active (Recommended)
These bridges from the archive have passed a TCP connectivity test (3 retries, 10s timeout) during the last run.

| Transport | IPv4 (Tested) | Count | IPv6 (Tested) | Count |
| :--- | :--- | :--- | :--- | :--- |
| **obfs4** | [obfs4_tested.txt]({REPO_URL}/obfs4_tested.txt) | **{stats.get('obfs4_tested.txt', 0)}** | [obfs4_ipv6_tested.txt]({REPO_URL}/obfs4_ipv6_tested.txt) | **{stats.get('obfs4_ipv6_tested.txt', 0)}** |
| **WebTunnel** | [webtunnel_tested.txt]({REPO_URL}/webtunnel_tested.txt) | **{stats.get('webtunnel_tested.txt', 0)}** | [webtunnel_ipv6_tested.txt]({REPO_URL}/webtunnel_ipv6_tested.txt) | **{stats.get('webtunnel_ipv6_tested.txt', 0)}** |
| **Vanilla** | [vanilla_tested.txt]({REPO_URL}/vanilla_tested.txt) | **{stats.get('vanilla_tested.txt', 0)}** | [vanilla_ipv6_tested.txt]({REPO_URL}/vanilla_ipv6_tested.txt) | **{stats.get('vanilla_ipv6_tested.txt', 0)}** |

### 🔥 Fresh Bridges (Last 72 Hours)
Bridges discovered within the last 3 days.

| Transport | IPv4 (72h) | Count | IPv6 (72h) | Count |
| :--- | :--- | :--- | :--- | :--- |
| **obfs4** | [obfs4_72h.txt]({REPO_URL}/obfs4_72h.txt) | **{stats.get('obfs4_72h.txt', 0)}** | [obfs4_ipv6_72h.txt]({REPO_URL}/obfs4_ipv6_72h.txt) | **{stats.get('obfs4_ipv6_72h.txt', 0)}** |
| **WebTunnel** | [webtunnel_72h.txt]({REPO_URL}/webtunnel_72h.txt) | **{stats.get('webtunnel_72h.txt', 0)}** | [webtunnel_ipv6_72h.txt]({REPO_URL}/webtunnel_ipv6_72h.txt) | **{stats.get('webtunnel_ipv6_tested.txt', 0)}** |
| **Vanilla** | [vanilla_72h.txt]({REPO_URL}/vanilla_72h.txt) | **{stats.get('vanilla_72h.txt', 0)}** | [vanilla_ipv6_72h.txt]({REPO_URL}/vanilla_ipv6_72h.txt) | **{stats.get('vanilla_ipv6_72h.txt', 0)}** |

### 🔥 Full Archive (Accumulative)
History of all collected bridges.

| Transport | IPv4 (All Time) | Count | IPv6 (All Time) | Count |
| :--- | :--- | :--- | :--- | :--- |
| **obfs4** | [obfs4.txt]({REPO_URL}/obfs4.txt) | **{stats.get('obfs4.txt', 0)}** | [obfs4_ipv6.txt]({REPO_URL}/obfs4_ipv6.txt) | **{stats.get('obfs4_ipv6.txt', 0)}** |
| **WebTunnel** | [webtunnel.txt]({REPO_URL}/webtunnel.txt) | **{stats.get('webtunnel.txt', 0)}** | [webtunnel_ipv6.txt]({REPO_URL}/webtunnel_ipv6.txt) | **{stats.get('webtunnel_ipv6.txt', 0)}** |
| **Vanilla** | [vanilla.txt]({REPO_URL}/vanilla.txt) | **{stats.get('vanilla.txt', 0)}** | [vanilla_ipv6.txt]({REPO_URL}/vanilla_ipv6.txt) | **{stats.get('vanilla_ipv6.txt', 0)}** |


## 🔥 Disclaimer
This project is for educational and archival purposes. Please use these bridges responsibly.
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    log("README.md updated with latest statistics.")

def main():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    history = load_history()
    history = cleanup_history(history)
    
    recent_cutoff_time = datetime.now() - timedelta(hours=RECENT_HOURS)
    stats = {}
    
    log("Starting Bridge Scraper Session...")

    for target in TARGETS:
        url = target["url"]
        filename = target["file"]
        recent_filename = filename.replace(".txt", f"_{RECENT_HOURS}h.txt")
        tested_filename = filename.replace(".txt", "_tested.txt")
        transport_type = target["type"]
        
        existing_bridges = set()
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if is_valid_bridge_line(line):
                            existing_bridges.add(line)
            except:
                pass

        fetched_bridges = set()
        try:
            response = session.get(url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                bridge_div = soup.find("div", id="bridgelines")
                
                if bridge_div:
                    raw_text = bridge_div.get_text()
                    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
                    
                    for line in lines:
                        if is_valid_bridge_line(line):
                            fetched_bridges.add(line)
                            
                            if line not in history:
                                history[line] = datetime.now().isoformat()
                else:
                    log(f"Warning: No bridge container for {filename}.")
            else:
                log(f"Failed to fetch {url}. Status: {response.status_code}")

        except Exception as e:
            log(f"Connection error for {filename}: {e}")

        all_bridges = existing_bridges.union(fetched_bridges)
        
        if all_bridges:
            with open(filename, "w", encoding="utf-8") as f:
                for bridge in sorted(all_bridges):
                    f.write(bridge + "\n")
            log(f"Processed {filename}: Total {len(all_bridges)}")
        else:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("")

        recent_bridges = []
        for bridge in all_bridges:
            if bridge in history:
                try:
                    first_seen = datetime.fromisoformat(history[bridge])
                    if first_seen > recent_cutoff_time:
                        recent_bridges.append(bridge)
                except ValueError:
                    pass
        
        if recent_bridges:
            with open(recent_filename, "w", encoding="utf-8") as f:
                for bridge in sorted(recent_bridges):
                    f.write(bridge + "\n")
        else:
            with open(recent_filename, "w", encoding="utf-8") as f:
                f.write("")
        
        tested_bridges = batch_test_bridges(list(all_bridges), transport_type)
        
        if tested_bridges:
            with open(tested_filename, "w", encoding="utf-8") as f:
                for bridge in sorted(tested_bridges):
                    f.write(bridge + "\n")
            log(f"   → {len(tested_bridges)} bridges passed connectivity test.")
        else:
            with open(tested_filename, "w", encoding="utf-8") as f:
                f.write("")
            log(f"   → No bridges passed connectivity test for {filename}.")

        stats[filename] = len(all_bridges)
        stats[recent_filename] = len(recent_bridges)
        stats[tested_filename] = len(tested_bridges)

    save_history(history)
    update_readme(stats)
    log("Session Finished.")

if __name__ == "__main__":
    main()
