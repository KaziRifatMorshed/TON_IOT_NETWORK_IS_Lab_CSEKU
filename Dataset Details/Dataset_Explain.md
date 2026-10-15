This data comes from **Zeek (formerly Bro)** network analysis logs formatted for machine learning intrusion detection—specifically matching the schema of the **TON_IoT** dataset (Network telemetry subset).

It records individual connection sessions across an IoT network testbed, aggregating transport-layer metrics with parsed application-layer protocols (DNS, HTTP, SSL) and labeling the traffic for classification tasks.

---

### Column Breakdown by Category

#### 1. Flow Identification & Timing

* **`ts`**: Unix epoch timestamp marking the start of the connection.
* **`src_ip` / `dst_ip**`: Source and destination IPv4 addresses.
* **`src_port` / `dst_port**`: Source and destination port numbers.
* **`protocol`**: Transport-layer protocol (`tcp`, `udp`, `icmp`).
* **`service`**: Zeek-identified application-layer protocol (e.g., `dns`, `http`, `ssl`, or `-` if undetermined).

#### 2. Connection Metrics & State

* **`duration`**: Connection length in seconds.
* **`src_bytes` / `dst_bytes**`: Payload bytes sent from the originator and responder.
* **`conn_state`**: Zeek connection summary state:
* `OTH`: Traffic seen without a standard SYN handshake or mid-stream traffic.
* `S0`: Connection attempt seen, no reply received (common for UDP broadcasts or dropped SYN scans).
* `SHR`: Responder sent a SYN ACK followed immediately by a RESET.


* **`missed_bytes`**: Bytes missing from the reassembly queue due to packet drops or loss.
* **`src_pkts` / `dst_pkts**`: Total packets sent by source and destination.
* **`src_ip_bytes` / `dst_ip_bytes**`: Total IP layer byte counts (including IP headers).

#### 3. Protocol-Specific Logs

##### DNS Activity

* **`dns_query`**: Domain name requested (e.g., `_sleep-proxy._udp.local`).
* **`dns_qclass` / `dns_qtype**`: Numerical query class (e.g., `1` for Internet, `32769` for multicast cache-flush) and query type (e.g., `12` for PTR).
* **`dns_rcode`**: Response code (`0` = No Error).
* **`dns_AA` / `dns_RD` / `dns_RA**`: Authoritative Answer, Recursion Desired, and Recursion Available flags (`T`/`F`).
* **`dns_rejected`**: Boolean indicating whether the DNS server rejected the lookup.

##### SSL / TLS Activity

* **`ssl_version` / `ssl_cipher**`: Negotiated TLS version and cryptographic suite.
* **`ssl_resumed` / `ssl_established**`: Session resumption and successful handshake flags.
* **`ssl_subject` / `ssl_issuer**`: X.509 certificate subject and issuing CA distinguished names.

##### HTTP Activity

* **`http_trans_depth`**: Pipelining depth ordinal of the request within the connection.
* **`http_method` / `http_uri` / `http_version**`: REST verbs (`GET`, `POST`), target paths, and HTTP protocol version.
* **`http_referrer` / `http_user_agent**`: Standard client request headers.
* **`http_request_body_len` / `http_response_body_len**`: Body sizes in bytes.
* **`http_status_code`**: Server response code (e.g., `200`, `404`).
* **`http_orig_mime_types` / `http_resp_mime_types**`: Detected content MIME types.

#### 4. Anomalies & Warnings

* **`weird_name`**: Zeek internal protocol violation or anomaly detection flag (e.g., `bad_TCP_checksum`, `bad_UDP_checksum`).
* **`weird_addl`**: Additional diagnostic metadata associated with the anomaly.
* **`weird_notice`**: Boolean flag indicating if the event triggered an alert notice (`T`/`F`).

#### 5. Target Labels (Ground Truth)

* **`label`**: Binary classification target (`0` = Benign/Normal, `1` = Attack/Malicious).
* **`type`**: Multi-class classification target specifying the exact attack family (e.g., `normal`, `ddos`, `dos`, `backdoor`, `scanning`, `xss`, `injection`).

---

### Patterns in the Sample Data

* **Local IoT Traffic**: Frequent loopback and internal node chatter on host `192.168.1.152` involving ports `1880` (Node-RED) and `10502` (commonly used for industrial automation/Modbus gateways).
* **Periodic Broadcasts**: `192.168.1.79` broadcasting to subnet broadcast address `192.168.1.255` on UDP port `15600` every few seconds.
* **External Traffic**: Outbound HTTPS connections (`443`) to public cloud nodes (Amazon AWS and Google IPs), as well as local DNS queries to resolver `192.168.1.190:53`.
* **Dataset Status**: All sample records represent baseline behavior (`label = 0`, `type = normal`).