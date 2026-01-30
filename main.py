import os
import requests
import json
import re
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
RECENT_HOURS = 72
HISTORY_RETENTION_DAYS = 30

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

def main():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    history = load_history()
    history = cleanup_history(history)
    
    recent_cutoff_time = datetime.now() - timedelta(hours=RECENT_HOURS)
    
    log("Starting Bridge Scraper Session...")

    for target in TARGETS:
        url = target["url"]
        filename = target["file"]
        recent_filename = filename.replace(".txt", f"_{RECENT_HOURS}h.txt")
        
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
            log(f"   -> Generated {recent_filename} with {len(recent_bridges)} active bridges.")
        else:
            with open(recent_filename, "w", encoding="utf-8") as f:
                f.write("")

    save_history(history)
    log("Session Finished.")

if __name__ == "__main__":
    main()
