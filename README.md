# Tor Bridges Collector & Archive

This repository automatically collects, validates, and archives Tor bridges. A GitHub Action runs every 3 hours to fetch new bridges from the official Tor Project.

## 🔥 Bridge Lists

### 1. Fresh Bridges (Last 72 Hours)
Use these files for the most reliable connections. These contain bridges discovered within the last 3 days.

| Transport Type | IPv4 (72h) | IPv6 (72h) |
| :--- | :--- | :--- |
| **obfs4** | [obfs4_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/obfs4_72h.txt) | [obfs4_ipv6_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/obfs4_ipv6_72h.txt) |
| **WebTunnel** | [webtunnel_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/webtunnel_72h.txt) | [webtunnel_ipv6_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/webtunnel_ipv6_72h.txt) |
| **Vanilla** | [vanilla_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/vanilla_72h.txt) | [vanilla_ipv6_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/vanilla_ipv6_72h.txt) |

### 2. Full Archive (Accumulative)
These files contain the history of all collected bridges.

| Transport Type | IPv4 (All Time) | IPv6 (All Time) |
| :--- | :--- | :--- |
| **obfs4** | [obfs4.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/obfs4.txt) | [obfs4_ipv6.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/obfs4_ipv6.txt) |
| **WebTunnel** | [webtunnel.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/webtunnel.txt) | [webtunnel_ipv6.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/webtunnel_ipv6.txt) |
| **Vanilla** | [vanilla.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/vanilla.txt) | [vanilla_ipv6.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/vanilla_ipv6.txt) |

## 🔥 Automation Logic

-   **Schedule:** Runs every 3 hours.
-   **Retention:** 
    -   `*_72h.txt` files contain bridges seen in the last 3 days.
    -   `bridge_history.json` is automatically cleaned to remove entries older than 30 days.

## 🔥 Disclaimer
This project is for educational and archival purposes. Please use these bridges responsibly.
