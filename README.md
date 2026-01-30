# Tor Bridges Collector & Archive

**Last Updated:** 2026-01-30 20:11 UTC

This repository automatically collects, validates, and archives Tor bridges. A GitHub Action runs every 3 hours to fetch new bridges from the official Tor Project.

## ⚠️ Important Notes on IPv6 & WebTunnel

1.  **IPv6 Instability:** IPv6 bridges are significantly fewer in number and are often more susceptible to blocking or connection instability compared to IPv4.
2.  **WebTunnel Overlap:** WebTunnel bridges often use the same endpoint domain for both IPv4 and IPv6. Consequently, the IPv6 list is frequently identical to or a subset of the IPv4 list.
3.  **Recommendation:** For the most reliable connection, **prioritize using IPv4 bridges**. Use IPv6 only if IPv4 is completely inaccessible on your network.

## 📂 Bridge Lists

### 1. Fresh Bridges (Last 72 Hours)
Use these files for the most reliable connections. These contain bridges discovered within the last 3 days.

| Transport | IPv4 (72h) | Count | IPv6 (72h) | Count |
| :--- | :--- | :--- | :--- | :--- |
| **obfs4** | [obfs4_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/obfs4_72h.txt) | **10** | [obfs4_ipv6_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/obfs4_ipv6_72h.txt) | **5** |
| **WebTunnel** | [webtunnel_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/webtunnel_72h.txt) | **5** | [webtunnel_ipv6_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/webtunnel_ipv6_72h.txt) | **5** |
| **Vanilla** | [vanilla_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/vanilla_72h.txt) | **13** | [vanilla_ipv6_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/vanilla_ipv6_72h.txt) | **0** |

### 2. Full Archive (Accumulative)
These files contain the history of all collected bridges.

| Transport | IPv4 (All Time) | Count | IPv6 (All Time) | Count |
| :--- | :--- | :--- | :--- | :--- |
| **obfs4** | [obfs4.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/obfs4.txt) | **10** | [obfs4_ipv6.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/obfs4_ipv6.txt) | **5** |
| **WebTunnel** | [webtunnel.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/webtunnel.txt) | **5** | [webtunnel_ipv6.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/webtunnel_ipv6.txt) | **5** |
| **Vanilla** | [vanilla.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/vanilla.txt) | **13** | [vanilla_ipv6.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/vanilla_ipv6.txt) | **0** |

## ⚙️ Automation Logic

-   **Schedule:** Runs every 3 hours.
-   **Retention:** 
    -   `*_72h.txt` files contain bridges seen in the last 3 days.
    -   `bridge_history.json` is automatically cleaned to remove entries older than 30 days.

## ⚠️ Disclaimer
This project is for educational and archival purposes. Please use these bridges responsibly.
