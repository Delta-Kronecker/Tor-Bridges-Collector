import os
import requests
import json
import re
import socket
import concurrent.futures
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
MAX_WORKERS = 30
CONNECTION_TIMEOUT = 25
MAX_RETRIES = 5
SOCKET_RETRY_DELAY = 2

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
    return bool(re.search(r'\d+\.\d+\.\d+\.\d+|\[.*\]', line))

def extract_ip_port(line):
    ipv6_match = re.search(r'\[(.*?)\]:(\d+)', line)
    if ipv6_match:
        return ipv6_match.group(1), int(ipv6_match.group(2))
    
    ipv4_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)', line)
    if ipv4_match:
        return ipv4_match.group(1), int(ipv4_match.group(2))
    
    return None, None

def test_connection_with_fallback(bridge_line):
    if not bridge_line or len(bridge_line) < 8:
        return None
    
    extracted_ip, extracted_port = extract_ip_port(bridge_line)
    
    if not extracted_ip or not extracted_port:
        return None
    
    if "webtunnel" in bridge_line.lower():
        host = extracted_ip
        port = extracted_port
        
        for attempt in range(MAX_RETRIES):
            try:
                sock = socket.create_connection((host, port), timeout=CONNECTION_TIMEOUT + (attempt * 5))
                sock.settimeout(CONNECTION_TIMEOUT + 10)
                
                try:
                    sock.send(b"GET / HTTP/1.0\r\n\r\n")
                    response = sock.recv(1024)
                    if response:
                        sock.close()
                        return bridge_line
                except:
                    pass
                
                sock.close()
                return bridge_line
            except (socket.timeout, socket.error, ConnectionRefusedError, OSError) as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(SOCKET_RETRY_DELAY + attempt)
                continue
        return None
    
    else:
        host = extracted_ip
        port = extracted_port
        
        for attempt in range(MAX_RETRIES):
            try:
                sock = socket.create_connection((host, port), timeout=CONNECTION_TIMEOUT + (attempt * 3))
                sock.close()
                return bridge_line
            except (socket.timeout, socket.error, ConnectionRefusedError, OSError) as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(SOCKET_RETRY_DELAY)
                
                if "IPv6" in bridge_line:
                    try:
                        sock_v6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                        sock_v6.settimeout(CONNECTION_TIMEOUT + 10)
                        sock_v6.connect((host, port, 0, 0))
                        sock_v6.close()
                        return bridge_line
                    except:
                        continue
                continue
        return None

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
| **WebTunnel** | [webtunnel_72h.txt]({REPO_URL}/webtunnel_72h.txt) | **{stats.get('webtunnel_72h.txt', 0)}** | [webtunnel_ipv6_72h.txt]({REPO_URL}/webtunnel_ipv6_72h.txt) | **{stats.get('webtunnel_ipv6_72h.txt', 0)}** |
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
            response = session.get(url, timeout=45)
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
        
        log(f"Testing connectivity for {filename} ({len(all_bridges)} bridges)...")
        tested_bridges = []
        if all_bridges:
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                future_to_bridge = {executor.submit(test_connection_with_fallback, bridge): bridge for bridge in all_bridges}
                for future in concurrent.futures.as_completed(future_to_bridge):
                    bridge = future_to_bridge[future]
                    try:
                        result = future.result()
                        if result:
                            tested_bridges.append(result)
                    except Exception:
                        pass
        
        if tested_bridges:
            with open(tested_filename, "w", encoding="utf-8") as f:
                for bridge in sorted(tested_bridges):
                    f.write(bridge + "\n")
            log(f"   -> {len(tested_bridges)} bridges passed connectivity test.")
        else:
            with open(tested_filename, "w", encoding="utf-8") as f:
                f.write("")
            log(f"   -> No bridges passed connectivity test for {filename}.")

        stats[filename] = len(all_bridges)
        stats[recent_filename] = len(recent_bridges)
        stats[tested_filename] = len(tested_bridges)

    save_history(history)
    update_readme(stats)
    log("Session Finished.")

if __name__ == "__main__":
    main()
