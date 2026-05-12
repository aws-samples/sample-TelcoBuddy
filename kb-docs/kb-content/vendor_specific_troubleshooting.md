# Vendor-Specific Troubleshooting Guide

## Ericsson Equipment

### MME (Mobility Management Entity)

#### Common Alarms
- **S1AP_CONNECTION_FAILURE**: S1 interface connectivity issue
  - Check: eNodeB reachability, SCTP associations, IP routing
  - CLI: `show s1ap connections`, `show sctp associations`
  
- **HSS_UNREACHABLE**: Diameter S6a interface down
  - Check: HSS connectivity, Diameter peer status, routing
  - CLI: `show diameter peers`, `show s6a statistics`

- **OVERLOAD_PROTECTION_ACTIVE**: MME in overload state
  - Check: CPU utilization, memory usage, message queue depths
  - CLI: `show system resources`, `show overload status`

#### Key Performance Counters
- **pmAttachSucc / pmAttachFail**: Attach procedure success/failure
- **pmTauSucc / pmTauFail**: Tracking Area Update success/failure
- **pmServiceReqSucc / pmServiceReqFail**: Service request procedures
- **pmS1SetupSucc / pmS1SetupFail**: S1 setup procedures
- **pmAuthenticationSucc / pmAuthenticationFail**: Authentication procedures

#### Troubleshooting Commands (AMOS/MML)
```
# Check MME status
show mme status

# View active subscribers
show subscribers summary

# Check S1AP connections
show s1ap connections

# View Diameter peers
show diameter peers

# Check overload status
show overload status

# View recent alarms
show alarms active

# Check pool status
show pool status

# View S6a statistics
show s6a statistics

# Check GTP-C tunnels
show gtpc tunnels
```

### eNodeB (Evolved NodeB)

#### Common Alarms
- **CELL_UNAVAILABLE**: Cell out of service
  - Check: Radio unit status, transport connectivity, configuration
  - CLI: `show cell status`, `show radio units`

- **S1_LINK_DOWN**: S1 interface failure
  - Check: MME connectivity, SCTP status, IP routing
  - CLI: `show s1 status`, `show sctp associations`

- **HIGH_PRB_UTILIZATION**: Physical Resource Block congestion
  - Check: Cell load, connected users, throughput
  - CLI: `show cell load`, `show prb utilization`

#### Key Performance Counters
- **pmRrcConnEstabSucc / pmRrcConnEstabFail**: RRC connection establishment
- **pmErabEstabSucc / pmErabEstabFail**: E-RAB establishment
- **pmHandoverSucc / pmHandoverFail**: Handover procedures
- **pmPrbUtilDl / pmPrbUtilUl**: PRB utilization downlink/uplink
- **pmCellAvailability**: Cell availability percentage

#### Troubleshooting Commands
```
# Check cell status
show cell status

# View connected UEs
show ue summary

# Check S1 interface
show s1 status

# View PRB utilization
show prb utilization

# Check handover statistics
show handover statistics

# View radio conditions
show radio conditions

# Check transport status
show transport status
```

---

## Nokia Equipment

### MME (Mobility Management Entity)

#### Common Alarms
- **MME_OVERLOAD**: System overload condition
  - Check: CPU load, memory, message processing rate
  - CLI: `show system load`, `show mme statistics`

- **S6A_PEER_DOWN**: HSS connectivity lost
  - Check: Diameter peer status, network connectivity
  - CLI: `show diameter peer-status`, `show s6a interface`

- **S1_ASSOCIATION_FAILURE**: S1 SCTP association down
  - Check: eNodeB connectivity, SCTP parameters
  - CLI: `show s1-mme associations`, `show sctp status`

#### Key Performance Measurements
- **AttachSuccess / AttachFailure**: Attach procedure outcomes
- **TauSuccess / TauFailure**: TAU procedure outcomes
- **ServiceRequestSuccess / ServiceRequestFailure**: Service requests
- **AuthenticationSuccess / AuthenticationFailure**: Authentication
- **S1SetupSuccess / S1SetupFailure**: S1 setup procedures

#### Troubleshooting Commands (BCF/CLI)
```
# Check MME operational state
show mme operational-state

# View subscriber statistics
show subscriber statistics

# Check S1-MME interface
show s1-mme interface

# View Diameter connections
show diameter connections

# Check system resources
show system resources

# View active alarms
show alarms active

# Check pool configuration
show pool configuration

# View S6a transactions
show s6a transactions
```

### eNodeB (Flexi)

#### Common Alarms
- **CELL_OUT_OF_SERVICE**: Cell not operational
  - Check: Radio module status, configuration, licenses
  - CLI: `show cell operational-state`, `show radio-modules`

- **S1_CONNECTION_LOST**: S1 interface down
  - Check: MME reachability, transport network
  - CLI: `show s1-interface status`, `show transport`

- **CAPACITY_ALARM**: Cell capacity threshold exceeded
  - Check: Connected users, PRB usage, throughput
  - CLI: `show cell capacity`, `show resource-usage`

#### Key Performance Measurements
- **RrcConnectionSetupSuccess / RrcConnectionSetupFailure**: RRC setup
- **ErabSetupSuccess / ErabSetupFailure**: E-RAB setup
- **HandoverInSuccess / HandoverOutSuccess**: Handover success
- **PrbUtilizationDl / PrbUtilizationUl**: Resource utilization
- **CellAvailability**: Cell uptime percentage

#### Troubleshooting Commands
```
# Check cell status
show cell status

# View active UEs
show ue-context summary

# Check S1 interface
show s1-interface status

# View resource utilization
show resource-usage

# Check handover performance
show handover statistics

# View radio performance
show radio performance

# Check transport links
show transport links
```

---

## Huawei Equipment

### MME (Mobility Management Entity)

#### Common Alarms
- **MME_CPU_OVERLOAD**: CPU utilization high
  - Check: System load, process status, traffic volume
  - MML: `DSP CPUINFO`, `DSP MMESTATUS`

- **S6A_LINK_FAULT**: S6a interface failure
  - Check: HSS connectivity, Diameter peer status
  - MML: `DSP DIAMETERPEERSTATUS`, `DSP S6ASTATUS`

- **S1_LINK_FAULT**: S1 interface failure
  - Check: eNodeB connectivity, SCTP associations
  - MML: `DSP S1LINK`, `DSP SCTPASSOC`

#### Key Performance Counters
- **pmAttachAttempt / pmAttachSuccess**: Attach procedures
- **pmTauAttempt / pmTauSuccess**: TAU procedures
- **pmServiceReqAttempt / pmServiceReqSuccess**: Service requests
- **pmAuthAttempt / pmAuthSuccess**: Authentication
- **pmS1SetupAttempt / pmS1SetupSuccess**: S1 setup

#### Troubleshooting Commands (MML)
```
# Display MME status
DSP MMESTATUS

# Show subscriber information
DSP UEINFO

# Check S1 interface
DSP S1LINK

# View Diameter peers
DSP DIAMETERPEERSTATUS

# Check system resources
DSP CPUINFO
DSP MEMINFO

# View active alarms
DSP ALM ACTIVE

# Check pool status
DSP MMEPOOLSTATUS

# View S6a statistics
DSP S6ASTATUS

# Check GTP-C status
DSP GTPCSTATUS
```

### eNodeB

#### Common Alarms
- **CELL_UNAVAILABLE**: Cell not in service
  - Check: Radio unit, configuration, transport
  - MML: `DSP CELL`, `DSP RADIOSTATUS`

- **S1_INTERFACE_FAULT**: S1 connectivity issue
  - Check: MME reachability, SCTP status
  - MML: `DSP S1INTERFACE`, `DSP SCTPLINK`

- **RESOURCE_CONGESTION**: Cell resource exhaustion
  - Check: PRB usage, connected UEs, capacity
  - MML: `DSP CELLLOAD`, `DSP PRBUSAGE`

#### Key Performance Counters
- **pmRrcConnEstabAttempt / pmRrcConnEstabSucc**: RRC establishment
- **pmErabEstabAttempt / pmErabEstabSucc**: E-RAB establishment
- **pmHandoverAttempt / pmHandoverSucc**: Handover procedures
- **pmPrbUsageDl / pmPrbUsageUl**: PRB utilization
- **pmCellAvailRate**: Cell availability rate

#### Troubleshooting Commands (MML)
```
# Display cell status
DSP CELL

# Show UE information
DSP UEINFO

# Check S1 interface
DSP S1INTERFACE

# View PRB utilization
DSP PRBUSAGE

# Check handover statistics
DSP HOSTAT

# View radio status
DSP RADIOSTATUS

# Check transport status
DSP TRANSPORT
```

---

## Samsung Equipment

### MME

#### Common Alarms
- **MME_SERVICE_UNAVAILABLE**: MME service down
  - Check: Process status, system health, configuration
  - CLI: `show mme service-status`

- **S6A_CONNECTION_FAILURE**: HSS connectivity issue
  - Check: Diameter connectivity, peer status
  - CLI: `show diameter peer-list`

#### Key Counters
- **AttachRequestCount / AttachSuccessCount**: Attach statistics
- **TauRequestCount / TauSuccessCount**: TAU statistics
- **ServiceRequestCount / ServiceSuccessCount**: Service requests

#### Troubleshooting Commands
```
# Check MME status
show mme status

# View subscribers
show subscriber list

# Check interfaces
show interface s1-mme
show interface s6a

# View statistics
show statistics mme
```

### eNodeB

#### Common Alarms
- **CELL_DOWN**: Cell not operational
  - Check: Radio hardware, configuration
  - CLI: `show cell status`

- **S1_CONNECTION_DOWN**: S1 interface failure
  - Check: MME connectivity, transport
  - CLI: `show s1 connection`

#### Troubleshooting Commands
```
# Check cell status
show cell status

# View UE list
show ue list

# Check S1 status
show s1 connection

# View performance
show performance cell
```

---

## ZTE Equipment

### MME

#### Common Alarms
- **MME_OVERLOAD_ALARM**: System overload
  - Check: CPU, memory, message queues
  - CLI: `show system status`

- **S6A_PEER_UNAVAILABLE**: HSS unreachable
  - Check: Diameter peer connectivity
  - CLI: `show diameter peer`

#### Troubleshooting Commands
```
# Display MME status
display mme status

# Show subscriber info
display subscriber info

# Check S1 interface
display s1 interface

# View alarms
display alarm active
```

---

## Common Troubleshooting Patterns Across Vendors

### High Attach Failure Rate
1. Check HSS connectivity (S6a/Diameter)
2. Verify authentication vectors
3. Review subscription data
4. Check MME capacity
5. Verify S1 interface stability

### S1 Interface Issues
1. Verify SCTP associations
2. Check IP connectivity (ping, traceroute)
3. Review firewall rules
4. Verify SCTP parameters (heartbeat, RTO)
5. Check eNodeB and MME configurations

### Handover Failures
1. Check neighbor cell relations
2. Verify X2 interface (if applicable)
3. Review handover parameters (thresholds, timers)
4. Check target cell capacity
5. Verify UE measurement reports

### Authentication Failures
1. Check HSS connectivity
2. Verify authentication vectors
3. Review security algorithms
4. Check UE security capabilities
5. Verify subscription data

### Bearer Establishment Failures
1. Check SGW/PGW connectivity (S11/S5)
2. Verify GTP-C signaling
3. Review QoS parameters
4. Check APN configuration
5. Verify IP address allocation

---

## Vendor-Specific Log Formats

### Ericsson Log Format
```
YYYY-MM-DD HH:MM:SS.mmm [SEVERITY] [MODULE] Message
ALARM CRITICAL ManagedElement=MME01,Function=S1AP S1AP_CONNECTION_FAILURE
Counter pmAttachSucc = 12345
```

### Nokia Log Format
```
YYYY-MM-DD HH:MM:SS [SEVERITY] [COMPONENT] Message
ALARM,MAJOR,MME-POOL-1,S6A_PEER_DOWN
AttachSuccess: 5678
```

### Huawei Log Format
```
YYYY-MM-DD HH:MM:SS [SEVERITY] [NE] [ALARM_ID] Message
ALM MAJOR NE=MME01 12345 S6A_LINK_FAULT
pmAttachAttempt = 10000
```

---

## Integration with Jitu Bhaiyya

When analyzing vendor logs, Jitu Bhaiyya automatically:
1. Detects vendor from log format
2. Parses vendor-specific alarms and counters
3. Correlates alarms with KPI degradations
4. Provides vendor-specific CLI commands
5. References vendor documentation

Upload vendor logs via:
```bash
curl -X POST https://api/analyze-file \
  -H "X-Filename: vendor_log.txt" \
  --data-binary @vendor_log.txt
```
