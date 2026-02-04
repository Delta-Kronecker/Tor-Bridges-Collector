# Tor Bridges Collector & Archive

**Last Updated:** 2026-02-04 21:30 UTC

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
| **obfs4** | [obfs4_tested.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/obfs4_tested.txt) | **55** | [obfs4_ipv6_tested.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/obfs4_ipv6_tested.txt) | **0** |
| **WebTunnel** | [webtunnel_tested.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/webtunnel_tested.txt) | **0** | [webtunnel_ipv6_tested.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/webtunnel_ipv6_tested.txt) | **0** |
| **Vanilla** | [vanilla_tested.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/vanilla_tested.txt) | **58** | [vanilla_ipv6_tested.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/vanilla_ipv6_tested.txt) | **0** |

### 🔥 Fresh Bridges (Last 72 Hours)
Bridges discovered within the last 3 days.

| Transport | IPv4 (72h) | Count | IPv6 (72h) | Count |
| :--- | :--- | :--- | :--- | :--- |
| **obfs4** | [obfs4_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/obfs4_72h.txt) | **36** | [obfs4_ipv6_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/obfs4_ipv6_72h.txt) | **19** |
| **WebTunnel** | [webtunnel_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/webtunnel_72h.txt) | **6** | [webtunnel_ipv6_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/webtunnel_ipv6_72h.txt) | **6** |
| **Vanilla** | [vanilla_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/vanilla_72h.txt) | **47** | [vanilla_ipv6_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/vanilla_ipv6_72h.txt) | **0** |

### 🔥 Full Archive (Accumulative)
History of all collected bridges.

| Transport | IPv4 (All Time) | Count | IPv6 (All Time) | Count |
| :--- | :--- | :--- | :--- | :--- |
| **obfs4** | [obfs4.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/obfs4.txt) | **64** | [obfs4_ipv6.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/obfs4_ipv6.txt) | **32** |
| **WebTunnel** | [webtunnel.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/webtunnel.txt) | **19** | [webtunnel_ipv6.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/webtunnel_ipv6.txt) | **19** |
| **Vanilla** | [vanilla.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/vanilla.txt) | **93** | [vanilla_ipv6.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/vanilla_ipv6.txt) | **0** |


## 🔥 Disclaimer
This project is for educational and archival purposes. Please use these bridges responsibly.
