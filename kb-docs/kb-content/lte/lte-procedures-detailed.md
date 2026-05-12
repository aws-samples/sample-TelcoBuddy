# LTE Procedures - Detailed Call Flows

**Based on**: 3GPP TS 23.401, TS 24.301

## Initial Attach Procedure

### Complete Attach Flow

**Step 1-3: RRC Connection Establishment**
```
UE → eNB: RRC Connection Request
eNB → UE: RRC Connection Setup
UE → eNB: RRC Connection Setup Complete
```

**Step 4-7: NAS Authentication**
```
UE → MME: Attach Request (IMSI/GUTI, UE capabilities)
MME → HSS: Authentication Information Request
HSS → MME: Authentication Information Answer (AV)
MME → UE: Authentication Request (RAND, AUTN)
UE validates AUTN, computes RES
UE → MME: Authentication Response (RES)
MME validates RES = XRES
```

**Step 8-10: NAS Security**
```
MME → UE: Security Mode Command (algorithms)
UE → MME: Security Mode Complete
[All subsequent NAS messages encrypted/integrity protected]
```

**Step 11-13: Location Update**
```
MME → HSS: Update Location Request
HSS → MME: Cancel Location (to old MME if exists)
HSS → MME: Insert Subscriber Data (APN, QoS profile)
MME → HSS: Update Location Answer
```

**Step 14-19: Default Bearer Establishment**
```
MME → SGW: Create Session Request (IMSI, APN, QoS)
SGW → PGW: Create Session Request
PGW allocates UE IP address
PGW → PCRF: CCR (Credit Control Request) - optional
PCRF → PGW: CCA (with PCC rules)
PGW → SGW: Create Session Response (UE IP, PGW TEID)
SGW → MME: Create Session Response (SGW TEID)
```

**Step 20-23: Radio Bearer Setup**
```
MME → eNB: Initial Context Setup Request (NAS, bearers)
eNB → UE: RRC Connection Reconfiguration (DRB setup)
UE → eNB: RRC Connection Reconfiguration Complete
eNB → MME: Initial Context Setup Response
```

**Step 24-26: Attach Complete**
```
UE → MME: Attach Complete (via eNB)
MME → SGW: Modify Bearer Request (eNB address, TEID)
SGW → PGW: Modify Bearer Request
PGW → SGW: Modify Bearer Response
SGW → MME: Modify Bearer Response
```

**Result**: UE attached, default bearer active, IP address assigned

### Attach Reject Scenarios

**Causes**:
- Unknown IMSI (not in HSS)
- Authentication failure
- Network failure
- Congestion
- Roaming not allowed

**Message**: Attach Reject (cause code)

## Dedicated Bearer Establishment

### Network-Initiated

**Trigger**: Application requires specific QoS (VoLTE, video)

**Flow**:
```
Application Server → PGW: Request (via SGi)
PGW → PCRF: CCR (request PCC rules)
PCRF → PGW: CCA (PCC rules, QoS)
PGW → SGW: Create Bearer Request (QCI, GBR, ARP)
SGW → MME: Create Bearer Request
MME → eNB: Bearer Setup Request
eNB → UE: RRC Connection Reconfiguration (new DRB)
UE → eNB: RRC Connection Reconfiguration Complete
eNB → MME: Bearer Setup Response
MME → SGW: Create Bearer Response
SGW → PGW: Create Bearer Response
```

**Result**: Dedicated bearer established with guaranteed QoS

### UE-Initiated

**Trigger**: UE requests specific QoS

**Flow**:
```
UE → MME: Bearer Resource Allocation Request (QoS)
MME → SGW: Create Bearer Request
[Same as network-initiated from this point]
```

## Service Request Procedure

### Trigger

UE in IDLE mode needs to send/receive data

### Flow

**Step 1-3: RRC Connection**
```
UE → eNB: RRC Connection Request (cause: mo-Data)
eNB → UE: RRC Connection Setup
UE → eNB: RRC Connection Setup Complete
```

**Step 4-6: Service Request**
```
UE → MME: Service Request (via eNB)
MME → SGW: Modify Bearer Request (eNB address)
SGW → MME: Modify Bearer Response
```

**Step 7-9: Radio Bearer Activation**
```
MME → eNB: Initial Context Setup Request
eNB → UE: RRC Connection Reconfiguration
UE → eNB: RRC Connection Reconfiguration Complete
eNB → MME: Initial Context Setup Response
```

**Result**: UE in CONNECTED mode, bearers active

## Handover Procedures

### X2 Handover (Intra-MME)

**Step 1-3: Handover Decision**
```
Source eNB: Measurement reports indicate handover needed
Source eNB → Target eNB: Handover Request (X2)
Target eNB: Admission control
Target eNB → Source eNB: Handover Request Ack
```

**Step 4-6: UE Handover**
```
Source eNB → UE: RRC Connection Reconfiguration (target cell)
UE: Synchronize with target cell
UE → Target eNB: RRC Connection Reconfiguration Complete
Target eNB → Source eNB: UE Context Release (X2)
```

**Step 7-10: Path Switch**
```
Target eNB → MME: Path Switch Request
MME → SGW: Modify Bearer Request (new eNB address)
SGW → MME: Modify Bearer Response
MME → Target eNB: Path Switch Request Ack
```

**Step 11: Resource Release**
```
Target eNB → Source eNB: UE Context Release (X2)
Source eNB: Release resources
```

**Result**: UE connected to target eNB, data path updated

### S1 Handover (Inter-MME)

**When**: X2 not available or inter-MME handover

**Additional Steps**:
```
Source MME → Target MME: Forward Relocation Request
Target MME → Target eNB: Handover Request
[UE handover execution]
Target eNB → Target MME: Handover Notify
Target MME → Source MME: Forward Relocation Complete
Source MME → Source eNB: UE Context Release Command
```

**Result**: UE connected to target eNB and target MME

## Tracking Area Update

### Periodic TAU

**Trigger**: TAU timer expires (T3412)

**Flow**:
```
UE → MME: Tracking Area Update Request (old GUTI)
MME → HSS: Update Location Request (if MME changed)
HSS → MME: Insert Subscriber Data
MME → HSS: Update Location Answer
MME → UE: Tracking Area Update Accept (new GUTI)
UE → MME: Tracking Area Update Complete
```

### TAU with Active Flag

**Trigger**: UE moves to new TA while in CONNECTED mode

**Flow**: Similar to periodic TAU, but includes bearer modification

## Detach Procedure

### UE-Initiated Detach

**Flow**:
```
UE → MME: Detach Request (switch off / normal detach)
MME → SGW: Delete Session Request
SGW → PGW: Delete Session Request
PGW → PCRF: CCR (termination)
PGW → SGW: Delete Session Response
SGW → MME: Delete Session Response
MME → HSS: Purge UE (if switch off)
MME → UE: Detach Accept (if normal detach)
MME → eNB: UE Context Release Command
eNB → MME: UE Context Release Complete
```

### Network-Initiated Detach

**Triggers**:
- Subscription cancelled
- Roaming restriction
- Network maintenance

**Flow**:
```
MME → UE: Detach Request (cause)
UE → MME: Detach Accept
[Session deletion same as UE-initiated]
```

## Paging Procedure

### Trigger

Downlink data arrives for UE in IDLE mode

**Flow**:
```
PGW: Receives downlink packet
PGW → SGW: Downlink Data Notification
SGW → MME: Downlink Data Notification
MME → eNBs: Paging (in tracking area)
eNBs: Broadcast paging message
UE: Receives paging
UE: Initiates Service Request procedure
```

## PDN Connectivity

### Additional PDN Connection

**Trigger**: UE requests second APN

**Flow**:
```
UE → MME: PDN Connectivity Request (APN)
MME → SGW: Create Session Request (new APN)
SGW → PGW: Create Session Request
PGW: Allocate second IP address
[Bearer establishment similar to attach]
MME → UE: Activate Default EPS Bearer Context Request
UE → MME: Activate Default EPS Bearer Context Accept
```

**Result**: UE has multiple PDN connections (multiple IP addresses)

### PDN Disconnection

**Flow**:
```
UE → MME: PDN Disconnect Request (bearer ID)
MME → SGW: Delete Bearer Request
SGW → PGW: Delete Bearer Request
PGW → SGW: Delete Bearer Response
SGW → MME: Delete Bearer Response
MME → UE: Deactivate EPS Bearer Context Request
UE → MME: Deactivate EPS Bearer Context Accept
```

## Bearer Modification

### QoS Modification

**Trigger**: Application QoS requirements change

**Flow**:
```
PGW → PCRF: CCR (QoS change request)
PCRF → PGW: CCA (new PCC rules)
PGW → SGW: Update Bearer Request (new QoS)
SGW → MME: Update Bearer Request
MME → eNB: Bearer Modify Request
eNB → UE: RRC Connection Reconfiguration
UE → eNB: RRC Connection Reconfiguration Complete
eNB → MME: Bearer Modify Response
MME → SGW: Update Bearer Response
SGW → PGW: Update Bearer Response
```

## Idle Mode Procedures

### Cell Selection

**Process**:
1. UE scans frequencies
2. Measures signal strength (RSRP)
3. Measures signal quality (RSRQ)
4. Selects cell with best quality
5. Reads system information

### Cell Reselection

**Triggers**:
- Better cell available
- Current cell quality degraded
- Timer-based reselection

**Criteria**:
- Intra-frequency: Ranking based on RSRP/RSRQ
- Inter-frequency: Priority-based
- Inter-RAT: Priority-based (LTE → 3G/2G)

## Error Handling

### Authentication Failure

**Causes**:
- MAC failure (AUTN invalid)
- SQN out of sync
- Non-EPS authentication unacceptable

**Recovery**:
```
UE → MME: Authentication Failure (cause)
If SQN sync failure:
  MME → HSS: Authentication Information Request (AUTS)
  HSS: Re-sync SQN
  MME: Retry authentication
```

### Attach Failure

**Causes**:
- Network congestion
- No suitable cell
- Authentication failure
- Subscription issue

**Recovery**:
- UE waits (T3410 timer)
- Retry attach
- If repeated failures, enter limited service

### Handover Failure

**Causes**:
- Target cell unavailable
- Radio link failure
- Timeout

**Recovery**:
```
UE: RRC re-establishment procedure
UE → eNB: RRC Connection Re-establishment Request
eNB → UE: RRC Connection Re-establishment
[Resume connection]
```

## State Transitions

### RRC States

**IDLE**:
- No RRC connection
- UE-controlled mobility
- Paging for incoming data
- Battery efficient

**CONNECTED**:
- RRC connection active
- Network-controlled mobility
- Data transfer possible
- Higher power consumption

**Transitions**:
- IDLE → CONNECTED: Service Request, Attach
- CONNECTED → IDLE: Inactivity timer, Detach

### EMM States

**DEREGISTERED**:
- Not attached to network
- No EPS context

**REGISTERED**:
- Attached to network
- EPS context active
- Can be in IDLE or CONNECTED

### ECM States

**IDLE**:
- EMM-REGISTERED + RRC-IDLE
- No S1 connection

**CONNECTED**:
- EMM-REGISTERED + RRC-CONNECTED
- S1 connection active

## Timers

### Key Timers

**T3410** (Attach): 15 seconds
- Attach request timeout
- Retry on expiry

**T3411** (Attach retry): 10 seconds
- Wait before retry after failure

**T3412** (Periodic TAU): 54 minutes (default)
- Periodic tracking area update

**T3402** (Attach reject): 12 minutes
- Wait after attach reject

**T3421** (Detach): 15 seconds
- Detach request timeout

**T3430** (Authentication): 15 seconds
- Authentication timeout

## Summary

LTE procedures provide:
- **Attach**: Network registration and bearer setup
- **Detach**: Clean disconnection
- **Handover**: Seamless mobility
- **TAU**: Location tracking
- **Service Request**: IDLE to CONNECTED transition
- **Bearer Management**: QoS control
- **Paging**: Downlink data notification

**Key Characteristics**:
- Efficient signaling
- Robust error handling
- Seamless mobility
- QoS support
- Security integration
