# LTE/EPC Architecture - Complete Overview

**Based on**: 3GPP Release 8-15 specifications

## Overview

LTE (Long Term Evolution) is the 4G mobile network standard with EPC (Evolved Packet Core) as its core network. It provides high-speed data, low latency, and all-IP architecture.

## EPC (Evolved Packet Core) Architecture

### Core Network Elements

**MME (Mobility Management Entity)**:
- Control plane hub
- Manages UE mobility and sessions
- Authentication and security
- Tracking area management
- Paging and bearer management

**HSS (Home Subscriber Server)**:
- Subscriber database
- Authentication vectors (AV) generation
- Subscriber profile storage
- Roaming authorization

**SGWC (Serving Gateway Control)**:
- S-GW control plane
- Mobility anchor for inter-eNB handover
- Lawful intercept
- Charging data collection

**SGWU (Serving Gateway User)**:
- S-GW user plane
- Routes user data packets
- Connects eNB to PGW
- Buffering for paging

**PGWC (PDN Gateway Control)**:
- P-GW control plane
- IP address allocation
- Policy enforcement point
- Charging gateway

**PGWU (PDN Gateway User)**:
- P-GW user plane
- Gateway to external networks
- NAT functionality
- QoS enforcement

**PCRF (Policy and Charging Rules Function)**:
- Policy control
- QoS rules
- Charging rules
- Gx interface to PGW

### Radio Access Network

**eNodeB (Evolved NodeB)**:
- LTE base station
- All radio functions
- Direct connection to EPC
- No RNC (flat architecture)

**Functions**:
- Radio resource management
- IP header compression
- Encryption
- Scheduling
- Mobility management

## LTE Interfaces

### Control Plane Interfaces

**S1-MME (eNB ↔ MME)**:
- Protocol: S1AP over SCTP
- Functions: NAS transport, paging, handover
- Port: 36412

**S6a (MME ↔ HSS)**:
- Protocol: Diameter
- Functions: Authentication, subscriber data
- Port: 3868

**S11 (MME ↔ SGW)**:
- Protocol: GTP-C
- Functions: Bearer management, mobility
- Port: 2123

**Gx (PGW ↔ PCRF)**:
- Protocol: Diameter
- Functions: Policy rules, QoS
- Port: 3868

### User Plane Interfaces

**S1-U (eNB ↔ SGW)**:
- Protocol: GTP-U over UDP
- Functions: User data transport
- Port: 2152

**S5/S8 (SGW ↔ PGW)**:
- Protocol: GTP-U over UDP
- Functions: User data between gateways
- Port: 2152

**SGi (PGW ↔ Internet)**:
- Protocol: IP
- Functions: External network connectivity

## Protocol Stack

### User Plane

```
Application
    ↓
IP
    ↓
PDCP (Packet Data Convergence Protocol)
    ↓
RLC (Radio Link Control)
    ↓
MAC (Medium Access Control)
    ↓
PHY (Physical Layer)
```

### Control Plane

```
NAS (Non-Access Stratum)
    ↓
RRC (Radio Resource Control)
    ↓
PDCP
    ↓
RLC
    ↓
MAC
    ↓
PHY
```

## LTE Bearers

### Bearer Types

**Default Bearer**:
- Established at attach
- Always active
- Best-effort QoS
- One per PDN connection

**Dedicated Bearer**:
- Established on demand
- Specific QoS
- For special services (VoLTE, video)
- Multiple per PDN

### QoS Parameters

**QCI (QoS Class Identifier)**:
- QCI 1-4: GBR (Guaranteed Bit Rate)
- QCI 5-9: Non-GBR
- QCI 65-69: Mission critical
- QCI 70-79: Mission critical delay sensitive

**ARP (Allocation and Retention Priority)**:
- Priority level: 1-15 (1 = highest)
- Pre-emption capability
- Pre-emption vulnerability

**GBR Parameters**:
- Guaranteed Bit Rate
- Maximum Bit Rate
- Aggregate Maximum Bit Rate (AMBR)

## LTE Procedures

### Attach Procedure

**Steps**:
1. UE → eNB: RRC Connection Request
2. eNB → UE: RRC Connection Setup
3. UE → MME: Attach Request (via eNB)
4. MME → HSS: Authentication Request
5. HSS → MME: Authentication Response
6. MME → UE: Authentication Request
7. UE → MME: Authentication Response
8. MME → HSS: Update Location Request
9. HSS → MME: Insert Subscriber Data
10. MME → SGW: Create Session Request
11. SGW → PGW: Create Session Request
12. PGW → SGW: Create Session Response
13. SGW → MME: Create Session Response
14. MME → UE: Attach Accept
15. UE → MME: Attach Complete

### Handover Procedure

**X2 Handover (between eNBs)**:
1. Source eNB decides handover
2. Source → Target: Handover Request (X2)
3. Target → Source: Handover Request Ack
4. Source → UE: RRC Connection Reconfiguration
5. UE → Target: RRC Connection Reconfiguration Complete
6. Target → MME: Path Switch Request
7. MME → SGW: Modify Bearer Request
8. Target → Source: Release Resource

**S1 Handover (via MME)**:
- Used when X2 not available
- MME coordinates handover
- More signaling overhead

### Tracking Area Update

**Triggers**:
- UE moves to new tracking area
- Periodic TAU timer expires
- After coming from idle mode

**Procedure**:
1. UE → MME: TAU Request
2. MME → HSS: Update Location (if needed)
3. MME → SGW: Modify Bearer Request
4. MME → UE: TAU Accept

## LTE Security

### Authentication (EPS-AKA)

**Process**:
1. MME requests authentication vectors from HSS
2. HSS generates: RAND, AUTN, XRES, KASME
3. MME sends RAND, AUTN to UE
4. UE validates AUTN (network authentication)
5. UE computes RES and sends to MME
6. MME validates RES = XRES (UE authentication)

### Key Hierarchy

```
K (in USIM)
    ↓
CK, IK (Cipher Key, Integrity Key)
    ↓
KASME (MME master key)
    ↓
├── KeNB (eNB key)
│   ↓
│   ├── KRRCenc (RRC encryption)
│   ├── KRRCint (RRC integrity)
│   ├── KUPenc (User plane encryption)
│   └── KUPint (User plane integrity - optional)
└── NAS keys
    ├── KNASenc (NAS encryption)
    └── KNASint (NAS integrity)
```

### Security Algorithms

**Integrity (EIA)**:
- EIA0: Null (no protection)
- EIA1: SNOW 3G
- EIA2: AES-128
- EIA3: ZUC

**Encryption (EEA)**:
- EEA0: Null (no encryption)
- EEA1: SNOW 3G
- EEA2: AES-128
- EEA3: ZUC

## LTE Identifiers

**IMSI (International Mobile Subscriber Identity)**:
- Format: MCC-MNC-MSIN
- Permanent subscriber identity
- 15 digits maximum

**GUTI (Globally Unique Temporary Identity)**:
- Temporary identity
- Prevents IMSI catching
- Format: GUMMEI + M-TMSI

**IMEI (International Mobile Equipment Identity)**:
- Device identifier
- 15 digits
- Used for device tracking/blocking

**eNB ID**:
- Identifies eNodeB
- Part of E-UTRAN Cell Global Identifier (ECGI)

## Radio Interface

### Physical Layer

**Downlink**: OFDMA (Orthogonal Frequency Division Multiple Access)
**Uplink**: SC-FDMA (Single Carrier FDMA)

**Frequency Bands**:
- FDD: Paired spectrum (separate UL/DL)
- TDD: Unpaired spectrum (time-shared UL/DL)
- Bands: 1-88 (various frequencies)

**Bandwidth Options**:
- 1.4, 3, 5, 10, 15, 20 MHz

**Modulation**:
- QPSK, 16QAM, 64QAM, 256QAM (Cat 11+)

### MAC Layer

**Functions**:
- Scheduling (uplink and downlink)
- HARQ (Hybrid ARQ)
- Multiplexing/demultiplexing
- Priority handling

**Channels**:
- PCCH: Paging Control Channel
- BCCH: Broadcast Control Channel
- CCCH: Common Control Channel
- DCCH: Dedicated Control Channel
- DTCH: Dedicated Traffic Channel

### RLC Layer

**Modes**:
- TM (Transparent Mode): No header
- UM (Unacknowledged Mode): No retransmission
- AM (Acknowledged Mode): ARQ retransmission

**Functions**:
- Segmentation/reassembly
- ARQ (in AM mode)
- In-sequence delivery
- Duplicate detection

### PDCP Layer

**Functions**:
- Header compression (ROHC)
- Encryption
- Integrity protection
- In-sequence delivery
- Duplicate detection

## LTE Categories

### UE Categories

| Category | Peak DL | Peak UL | MIMO | Modulation |
|----------|---------|---------|------|------------|
| Cat 1 | 10 Mbps | 5 Mbps | 1x2 | 64QAM DL |
| Cat 3 | 100 Mbps | 50 Mbps | 2x2 | 64QAM |
| Cat 4 | 150 Mbps | 50 Mbps | 2x2 | 64QAM |
| Cat 6 | 300 Mbps | 50 Mbps | 2x2/4x2 | 64QAM |
| Cat 9 | 450 Mbps | 50 Mbps | 4x4 | 64QAM |
| Cat 12 | 600 Mbps | 100 Mbps | 4x4 | 256QAM DL |
| Cat 16 | 1 Gbps | 150 Mbps | 4x4 | 256QAM |
| Cat 18 | 1.2 Gbps | 150 Mbps | 4x4 | 256QAM |

## VoLTE (Voice over LTE)

### IMS Integration

**Components**:
- P-CSCF (Proxy Call Session Control Function)
- I-CSCF (Interrogating CSCF)
- S-CSCF (Serving CSCF)

**Protocol**: SIP (Session Initiation Protocol)

**QoS**: QCI 1 (GBR, 100ms delay)

### Call Flow

1. UE → P-CSCF: SIP INVITE
2. P-CSCF → S-CSCF: SIP INVITE
3. S-CSCF → Terminating network
4. Dedicated bearer establishment
5. Call connected

## LTE Advanced Features

### Carrier Aggregation

**Types**:
- Intra-band contiguous
- Intra-band non-contiguous
- Inter-band

**Benefits**:
- Increased bandwidth
- Higher peak rates
- Better spectrum utilization

### CoMP (Coordinated Multi-Point)

**Techniques**:
- Joint transmission
- Dynamic cell selection
- Coordinated scheduling/beamforming

**Benefits**:
- Improved cell-edge performance
- Increased throughput
- Better interference management

### Enhanced ICIC

**Features**:
- Almost Blank Subframes (ABS)
- Reduced power subframes
- X2 interface coordination

**Benefits**:
- Reduced inter-cell interference
- Better cell-edge performance

## Comparison: LTE vs 5G

| Aspect | LTE | 5G |
|--------|-----|-----|
| **Architecture** | EPC (MME, SGW, PGW) | 5GC (AMF, SMF, UPF) |
| **Interfaces** | Reference points | Service-based |
| **Latency** | 10-20 ms | <1 ms (URLLC) |
| **Peak Rate** | 1 Gbps | 10+ Gbps |
| **Mobility** | Up to 350 km/h | Up to 500 km/h |
| **Slicing** | Limited (APN-based) | Native support |
| **Security** | EPS-AKA | 5G-AKA, SUCI |

## Migration Path: LTE to 5G

### NSA (Non-Standalone)

**Option 3/3a/3x**:
- LTE as anchor
- 5G NR for data
- EPC core
- Fastest deployment

### SA (Standalone)

**Option 2**:
- 5G NR only
- 5GC core
- Full 5G features
- Long-term target

### Interworking

**EPS Fallback**:
- 5G → LTE for voice
- Until VoNR available

**Dual Registration**:
- Simultaneous LTE and 5G
- Seamless handover

## Best Practices

### Deployment

1. **Coverage Planning**: RF optimization
2. **Capacity Planning**: Traffic forecasting
3. **QoS Configuration**: Proper QCI mapping
4. **Security**: Strong algorithms (EIA2/EEA2)
5. **Monitoring**: KPI tracking

### Optimization

1. **Handover Optimization**: Reduce failures
2. **Load Balancing**: Distribute traffic
3. **Interference Management**: ICIC, ABS
4. **Carrier Aggregation**: Maximize throughput
5. **VoLTE Quality**: QCI 1 prioritization

## Summary

LTE/EPC provides:
- **High-speed data**: Up to 1 Gbps
- **Low latency**: 10-20 ms
- **All-IP architecture**: Simplified core
- **Flat architecture**: No RNC
- **Advanced features**: CA, CoMP, VoLTE

**Key Components**:
- MME, HSS, SGW, PGW, PCRF (core)
- eNodeB (radio)
- S1, S6a, S11, Gx (interfaces)

**Evolution**: Foundation for 5G, with NSA and SA migration paths.
