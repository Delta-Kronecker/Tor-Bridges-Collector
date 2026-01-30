```python
import os
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

TARGETS = [
    {"url": "https://bridges.torproject.org/bridges?transport=obfs4", "file": "obfs4.txt"},
    {"url": "https://bridges.torproject.org/bridges?transport=webtunnel", "file": "webtunnel.txt"},
    {"url": "https://bridges.torproject.org/bridges?transport=vanilla", "file": "vanilla.txt"},
    {"url": "https://bridges.torproject.org/bridges?transport=obfs4&ipv6=yes", "file": "obfs4_ipv6.txt"},
    {"url": "https://bridges.torproject.org/bridges?transport=webtunnel&ipv6=yes", "file": "webtunnel_ipv6.txt"},
    {"url": "https://bridges.torproject.org/bridges?transport=vanilla&ipv6=yes", "file": "vanilla_ipv6.txt"},
]

HISTORY_FILE = "bridge_history.json"
RECENT_FILE = "recent_bridges_24h.txt"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

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

def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    history = load_history()
    total_new_bridges_session = 0
    
    log("Starting Bridge Scraper Session...")

    for target in TARGETS:
        url = target["url"]
        filename = target["file"]
        
        file_bridges = set()
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            file_bridges.add(line.strip())
            except:
                pass

        fetched_bridges = set()
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                bridge_div = soup.find("div", id="bridgelines")
                
                if bridge_div:
                    raw_text = bridge_div.get_text()
                    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
                    
                    for line in lines:
                        if line and not line.startswith("#") and "No bridges available" not in line:
                            fetched_bridges.add(line)
                            
                            if line not in history:
                                history[line] = datetime.now().isoformat()
                                total_new_bridges_session += 1
                else:
                    log(f"Warning: No bridge container found for {filename}.")
            else:
                log(f"Failed to fetch {url}. Status: {response.status_code}")

        except Exception as e:
            log(f"Connection error for {filename}: {e}")

        new_for_file = fetched_bridges - file_bridges
        if new_for_file:
            file_bridges.update(new_for_file)
            with open(filename, "w", encoding="utf-8") as f:
                for bridge in sorted(file_bridges):
                    f.write(bridge + "\n")
            log(f"Updated {filename}: {len(new_for_file)} new bridges added.")
        else:
            log(f"Checked {filename}: No new unique bridges.")

    cutoff_time = datetime.now() - timedelta(hours=24)
    recent_bridges = []

    for bridge, timestamp_str in history.items():
        try:
            bridge_time = datetime.fromisoformat(timestamp_str)
            if bridge_time > cutoff_time:
                recent_bridges.append(bridge)
        except ValueError:
            continue

    if recent_bridges:
        with open(RECENT_FILE, "w", encoding="utf-8") as f:
            for bridge in sorted(recent_bridges):
                f.write(bridge + "\n")
        log(f"Recent 24h file generated with {len(recent_bridges)} bridges.")
    else:
        log("No bridges found in last 24 hours. Skipping recent file creation.")

    save_history(history)

    log(f"Session Finished. Total new: {total_new_bridges_session}.")

if __name__ == "__main__":
    main()
```
