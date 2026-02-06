# Tor Bridges Collector & Archive

**Last Updated:** 2026-02-06 08:31 UTC

## 📊 Overall Statistics
| Metric | Count | Percentage |
|--------|-------|------------|
| Total Bridges Collected | 10 | 100% |
| Successfully Tested | 7 | 70.0% |
| New Bridges (72h) | 10 | 100.0% |
| History Retention | 30 days | - |

This repository automatically collects, validates, and archives Tor bridges. A GitHub Action runs every hour to fetch new bridges from the official Tor Project.

## ⚠️ Important Notes on IPv6 & WebTunnel
1. **IPv6 Instability:** IPv6 bridges are significantly fewer in number and are often more susceptible to blocking or connection instability compared to IPv4.
2. **WebTunnel Overlap:** WebTunnel bridges often use the same endpoint domain for both IPv4 and IPv6. Consequently, the IPv6 list is frequently identical to or a subset of the IPv4 list.
3. **Recommendation:** For the most reliable connection, **prioritize using IPv4 bridges**. Use IPv6 only if IPv4 is completely inaccessible on your network.

## 🔥 Bridge Lists

### ✅ Tested & Active (Recommended)
These bridges from the archive have passed a TCP/SSL connectivity test (2 retries, 8s timeout) during the last run.

| Transport | IPv4 (Tested) | Count | IPv6 (Tested) | Count | Success Rate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **obfs4** | [obfs4_tested.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridges/obfs4_tested.txt) | **2** | [obfs4_ipv6_tested.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridges/obfs4_ipv6_tested.txt) | **0** | 100.0% |
| **WebTunnel** | [webtunnel_tested.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridges/webtunnel_tested.txt) | **2** | [webtunnel_ipv6_tested.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridges/webtunnel_ipv6_tested.txt) | **2** | 100.0% |
| **Vanilla** | [vanilla_tested.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridges/vanilla_tested.txt) | **1** | [vanilla_ipv6_tested.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridges/vanilla_ipv6_tested.txt) | **0** | 50.0% |

### 🔥 Fresh Bridges (Last 72 Hours)
Bridges discovered within the last 3 days. Updated every hour.

| Transport | IPv4 (72h) | Count | IPv6 (72h) | Count | New Rate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **obfs4** | [obfs4_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridges/obfs4_72h.txt) | **2** | [obfs4_ipv6_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridges/obfs4_ipv6_72h.txt) | **2** | 100.0% |
| **WebTunnel** | [webtunnel_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridges/webtunnel_72h.txt) | **2** | [webtunnel_ipv6_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridges/webtunnel_ipv6_72h.txt) | **2** | 100.0% |
| **Vanilla** | [vanilla_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridges/vanilla_72h.txt) | **2** | [vanilla_ipv6_72h.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridges/vanilla_ipv6_72h.txt) | **0** | 100.0% |

### 📁 Full Archive (Accumulative)
History of all collected bridges since the beginning.

| Transport | IPv4 (All Time) | Count | IPv6 (All Time) | Count | Total |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **obfs4** | [obfs4.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridges/obfs4.txt) | **2** | [obfs4_ipv6.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridges/obfs4_ipv6.txt) | **2** | **4** |
| **WebTunnel** | [webtunnel.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridges/webtunnel.txt) | **2** | [webtunnel_ipv6.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridges/webtunnel_ipv6.txt) | **2** | **4** |
| **Vanilla** | [vanilla.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridges/vanilla.txt) | **2** | [vanilla_ipv6.txt](https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridges/vanilla_ipv6.txt) | **0** | **2** |

### ⚙️ Technical Details
- **Connection Test:** TCP for obfs4/Vanilla, SSL/TLS for WebTunnel
- **Test Parameters:** 2 retries, 8s timeout
- **Maximum Workers:** 50 concurrent tests
- **History Retention:** 30 days
- **Update Frequency:** Every hour
- **Last Run:** 2026-02-06 08:31 UTC

## 🔥 Disclaimer
This project is for educational and archival purposes. Please use these bridges responsibly.
