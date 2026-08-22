## If you find this helpful, don't forget to ⭐ it

This repository automatically collects, validates, and archives Tor bridges. A GitHub Action runs every 1 hours to fetch new bridges from the official Tor Project.

### Tested & Active (Recommended)
These bridges from the archive have passed a connectivity test during the last run.

| Transport | IPv4 (Tested) | Count | IPv6 (Tested) | Count |
| :--- | :--- | :--- | :--- | :--- |
| **obfs4** | [obfs4_tested.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/obfs4_tested.txt) | **497** | [obfs4_ipv6_tested.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/obfs4_ipv6_tested.txt) | **322** |
| **WebTunnel** | [webtunnel_tested.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/webtunnel_tested.txt) | **167** | [webtunnel_ipv6_tested.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/webtunnel_ipv6_tested.txt) | **87** |
| **Vanilla** | [vanilla_tested.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/vanilla_tested.txt) | **470** | [vanilla_ipv6_tested.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/vanilla_ipv6_tested.txt) | **50** |

### Fresh Bridges (Last 72 Hours)
Bridges discovered within the last 3 days.

| Transport | IPv4 (72h) | Count | IPv6 (72h) | Count |
| :--- | :--- | :--- | :--- | :--- |
| **obfs4** | [obfs4_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/obfs4_72h.txt) | **4** | [obfs4_ipv6_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/obfs4_ipv6_72h.txt) | **2** |
| **WebTunnel** | [webtunnel_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/webtunnel_72h.txt) | **4** | [webtunnel_ipv6_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/webtunnel_ipv6_72h.txt) | **2** |
| **Vanilla** | [vanilla_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/vanilla_72h.txt) | **1** | [vanilla_ipv6_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/vanilla_ipv6_72h.txt) | **1** |

### Full Archive (Since 2026-01-30)
History of all collected bridges.

| Transport | IPv4 | Count | IPv6 | Count |
| :--- | :--- | :--- | :--- | :--- |
| **obfs4** | [obfs4.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/obfs4.txt) | **626** | [obfs4_ipv6.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/obfs4_ipv6.txt) | **322** |
| **WebTunnel** | [webtunnel.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/webtunnel.txt) | **231** | [webtunnel_ipv6.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/webtunnel_ipv6.txt) | **222** |
| **Vanilla** | [vanilla.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/vanilla.txt) | **470** | [vanilla_ipv6.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/vanilla_ipv6.txt) | **50** |

## Important Notes on IPv6 & WebTunnel

1.  **IPv6 Instability:** IPv6 bridges are significantly fewer in number and are often more susceptible to blocking or connection instability compared to IPv4.
2.  **WebTunnel Overlap:** WebTunnel bridges often use the same endpoint domain for both IPv4 and IPv6. Consequently, the IPv6 list is frequently identical to or a subset of the IPv4 list.
3.  **Recommendation:** For the most reliable connection, **prioritize using IPv4 bridges**. Use IPv6 only if IPv4 is completely inaccessible on your network.

## Keep Delta-Kronecker Going!

### Donate

**USDT BEP20** (BNB Smart Chain):
```
0x2a434FF74737be5B94634040D010a458507b0741
```
> BEP20 network only — send only USDT on BNB Smart Chain.

---

## Disclaimer
This project is for educational and archival purposes. Please use these bridges responsibly.
