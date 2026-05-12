# Protocol Analysis and Troubleshooting Guide

## S1AP Protocol (4G eNodeB-MME Interface)

### Overview
S1AP (S1 Application Protocol) operates over SCTP on the S1-MME interface between eNodeB and MME.

**Key Procedures:**
- S1 Setup: Initial connection establishment
- Initial UE Message: First message from UE
- Downlink/Uplink NAS Transport: NAS message delivery
- Initial Context Setup: Bearer establishment
- UE Context Release: Connection cleanup
- Handover procedures: Mobility management
- Paging: Idle mode UE notification

### Common Issues and Analysis

#### S1 Setup Failure
**Symptoms:** eNodeB cannot connect to MME
**Causes:**
- SCTP association failure
- IP connectivity issues
- Configuration mismatch (PLMN, TAC)
- MME overload or unavailable

**Analysis Steps:**
1. Verify SCTP association status
2. Check IP reachability (ping MME)
3. Validate PLMN and TAC configuration
4. Review S1 Setup Request/Response messages
5. Check MME capacity and status

**Wireshark Filters:**
```
s1ap.procedureCode == 17  # S1 Setup
sctp
```

#### Initial Context Setup Failure
**Symptoms:** Bearer establishment fails after attach
**Causes:**
- S11 interface issues (MME-SGW)
- GTP-C tunnel problems
- QoS parameter rejection
- Resource unavailability

**Analysis Steps:**
1. Check Initial Context Setup Request parameters
2. Verify E-RAB parameters (QCI, ARP, GBR/MBR)
3. Review failure cause in response
4. Check S11 signaling (Create Session)
5. Verify eNodeB resource availability

**Key Parameters:**
- E-RAB ID
- QCI (QoS Class Identifier)
- ARP (Allocation and Retention Priority)
- GBR/MBR (Guaranteed/Maximum Bit Rate)

#### UE Context Release
**Symptoms:** Unexpected connection drops
**Causes:**
- Radio link failure (Cause 21)
- User inactivity (Cause 20)
- Network-initiated release
- Handover failure

**Analysis Steps:**
1. Check release cause code
2. Review preceding events (handover, measurements)
3. Verify radio conditions (RSRP, RSRQ)
4. Check inactivity timers
5. Correlate with eNodeB logs

---

## NGAP Protocol (5G gNB-AMF Interface)

### Overview
NGAP (NG Application Protocol) is the 5G equivalent of S1AP, operating on the N2 interface.

**Key Procedures:**
- NG Setup: Initial connection
- Initial UE Message: First UE contact
- PDU Session Resource Setup: Data bearer establishment
- UE Context Release: Connection cleanup
- Handover procedures: Inter-gNB mobility
- Paging: Idle mode notification

### Common Issues

#### NG Setup Failure
**Symptoms:** gNB cannot register with AMF
**Causes:**
- SCTP connectivity issues
- PLMN/NSSAI mismatch
- AMF capacity limits
- Configuration errors

**Analysis Steps:**
1. Verify SCTP association
2. Check PLMN ID and supported slices (NSSAI)
3. Review NG Setup Request/Response
4. Validate AMF configuration
5. Check network slice availability

#### PDU Session Establishment Failure
**Symptoms:** Data session cannot be created
**Causes:**
- SMF selection failure
- DNN (Data Network Name) issues
- Slice unavailability (Cause 62)
- Insufficient resources (Cause 67)

**Analysis Steps:**
1. Check PDU Session Resource Setup Request
2. Verify S-NSSAI and DNN
3. Review SMF selection criteria
4. Check N4 interface (SMF-UPF)
5. Verify slice configuration and capacity

**Key Parameters:**
- PDU Session ID
- S-NSSAI (Single Network Slice Selection Assistance Information)
- DNN (Data Network Name)
- QoS Flow Identifier
- 5QI (5G QoS Identifier)

---

## Diameter Protocol (HSS/PCRF Interfaces)

### Overview
Diameter is used for authentication, authorization, and policy control.

**Key Interfaces:**
- S6a (MME-HSS): Authentication and subscription
- S6d (SGSN-HSS): 3G authentication
- Gx (PCEF-PCRF): Policy control
- Gy (PCEF-OCS): Online charging
- Cx/Dx (CSCF-HSS): IMS registration

### S6a Interface Analysis

**Key Commands:**
- Authentication Information Request/Answer (AIR/AIA)
- Update Location Request/Answer (ULR/ULA)
- Purge UE Request/Answer (PUR/PUA)
- Cancel Location Request/Answer (CLR/CLA)
- Insert Subscriber Data Request/Answer (IDR/IDA)

**Common Issues:**

#### Authentication Failure
**Result Code 5030:** User unknown in HSS
**Troubleshooting:**
- Verify IMSI provisioning in HSS
- Check subscription status
- Review billing system sync
- Validate IMSI format

**Result Code 5420:** Unknown EPS subscription
**Troubleshooting:**
- Check EPS subscription data
- Verify APN configuration
- Review subscription profile
- Check provisioning workflow

#### Update Location Failure
**Result Code 5421:** RAT not allowed
**Troubleshooting:**
- Check RAT restrictions in subscription
- Verify roaming agreements
- Review access policies
- Validate subscription profile

**Result Code 5423:** Unknown serving node
**Troubleshooting:**
- Verify MME registration in HSS
- Check node configuration
- Review topology data
- Validate MME identity

**Wireshark Filters:**
```
diameter.cmd.code == 318  # AIR/AIA
diameter.cmd.code == 316  # ULR/ULA
diameter.applicationId == 16777251  # S6a
```

---

## GTP-C Protocol (Core Network Tunneling)

### Overview
GTP-C (GPRS Tunneling Protocol - Control) manages user plane tunnels.

**Key Interfaces:**
- S11 (MME-SGW): LTE control plane
- S5/S8 (SGW-PGW): Inter-gateway
- S4 (SGSN-SGW): 3G to LTE

**Key Messages:**
- Create Session Request/Response
- Modify Bearer Request/Response
- Delete Session Request/Response
- Create Bearer Request/Response
- Release Access Bearers Request/Response

### Common Issues

#### Create Session Failure
**Symptoms:** Bearer cannot be established
**Causes:**
- PGW selection failure
- APN configuration issues
- IP address pool exhaustion
- QoS parameter rejection

**Analysis Steps:**
1. Check Create Session Request parameters
2. Verify APN name and configuration
3. Review PGW selection criteria
4. Check IP address allocation
5. Validate QoS parameters (QCI, ARP)

**Key Parameters:**
- IMSI
- APN
- RAT Type
- Serving Network
- Bearer Contexts (EBI, QCI, ARP)
- PDN Address Allocation

#### Modify Bearer Failure
**Symptoms:** QoS modification rejected
**Causes:**
- Resource unavailability
- Invalid QoS parameters
- Policy restrictions
- Network congestion

**Analysis Steps:**
1. Check Modify Bearer Request
2. Verify new QoS parameters
3. Review policy rules (Gx)
4. Check network capacity
5. Validate bearer context

**Wireshark Filters:**
```
gtp.message == 0x20  # Create Session Request
gtp.message == 0x21  # Create Session Response
gtp.message == 0x22  # Modify Bearer Request
```

---

## NAS Protocol (UE-Core Signaling)

### NAS-EMM (4G Mobility Management)

**Key Procedures:**
- Attach: Initial network registration
- Detach: Network de-registration
- TAU (Tracking Area Update): Location update
- Service Request: Transition from idle to connected

**Common Failure Scenarios:**

#### Attach Reject
**Cause 7:** EPS services not allowed
- Check subscription profile
- Verify APN configuration
- Review roaming status

**Cause 17:** Network failure
- Check S6a connectivity
- Verify HSS availability
- Review MME resources

**Cause 22:** Congestion
- Check MME load
- Review admission control
- Verify capacity planning

#### TAU Reject
**Cause 12:** Tracking area not allowed
- Check TA restrictions
- Verify roaming agreements
- Review subscription profile

**Cause 15:** No suitable cells
- Check cell availability
- Verify cell barring status
- Review access restrictions

### NAS-5GMM (5G Mobility Management)

**Key Procedures:**
- Registration: Network registration
- De-registration: Network detachment
- Service Request: Session establishment
- Configuration Update: Parameter updates

**Common Failure Scenarios:**

#### Registration Reject
**Cause 62:** No network slices available
- Verify NSSAI configuration
- Check slice availability
- Review AMF slice support

**Cause 67:** Insufficient resources for slice/DNN
- Check SMF/UPF capacity
- Verify slice resources
- Review DNN configuration

---

## SIP Protocol (IMS/VoLTE/VoNR)

### Overview
SIP (Session Initiation Protocol) manages voice and multimedia sessions in IMS.

**Key Methods:**
- INVITE: Session initiation
- ACK: Request acknowledgment
- BYE: Session termination
- REGISTER: User registration
- OPTIONS: Capability query
- PRACK: Provisional acknowledgment
- UPDATE: Session modification

**Key Response Classes:**
- 1xx: Provisional (100 Trying, 180 Ringing, 183 Session Progress)
- 2xx: Success (200 OK)
- 3xx: Redirection
- 4xx: Client Error (404 Not Found, 486 Busy)
- 5xx: Server Error (503 Service Unavailable)
- 6xx: Global Failure (603 Decline)

### Common Issues

#### Registration Failure
**401 Unauthorized:** Authentication required
- Check IMS credentials
- Verify authentication challenge/response
- Review HSS subscription

**403 Forbidden:** Registration not allowed
- Check subscription status
- Verify service authorization
- Review barring settings

**503 Service Unavailable:** IMS core unavailable
- Check P-CSCF/I-CSCF/S-CSCF status
- Verify Diameter Cx interface
- Review system capacity

#### Call Setup Failure
**404 Not Found:** Called party not registered
- Verify callee registration status
- Check number translation
- Review routing configuration

**480 Temporarily Unavailable:** User not reachable
- Check UE registration
- Verify paging procedures
- Review radio conditions

**486 Busy Here:** User busy
- Normal call rejection
- Check call waiting settings
- Verify supplementary services

**Wireshark Filters:**
```
sip.Method == "INVITE"
sip.Status-Code >= 400
sip.CSeq.Method == "REGISTER"
```

### IMS Call Flow Analysis

**Successful Call:**
1. INVITE (UE-A → P-CSCF)
2. 100 Trying (P-CSCF → UE-A)
3. INVITE forwarded through I-CSCF, S-CSCF
4. 180 Ringing (from UE-B)
5. 200 OK (call answered)
6. ACK
7. Media session (RTP)
8. BYE (call termination)
9. 200 OK

**Failed Call Analysis:**
- Check each hop in SIP routing
- Verify SDP (Session Description Protocol) negotiation
- Review P-Asserted-Identity and privacy headers
- Check IMS charging headers (P-Charging-Vector)
- Validate QoS preconditions

---

## Protocol Correlation Techniques

### Multi-Protocol Flow Analysis

**Attach Procedure (4G):**
1. RRC Connection Setup (RRC)
2. Initial UE Message (S1AP)
3. Attach Request (NAS-EMM)
4. Authentication (Diameter S6a)
5. Initial Context Setup (S1AP)
6. Create Session (GTP-C S11)
7. Attach Accept (NAS-EMM)

**Registration Procedure (5G):**
1. RRC Setup (RRC)
2. Initial UE Message (NGAP)
3. Registration Request (NAS-5GMM)
4. Authentication (HTTP/2 SBI to AUSF)
5. PDU Session Establishment (NGAP)
6. N4 Session Establishment (PFCP)
7. Registration Accept (NAS-5GMM)

### Correlation Keys
- IMSI/SUPI: Subscriber identifier
- GUTI/5G-GUTI: Temporary identifier
- eNB/gNB UE S1AP/NGAP ID: RAN context
- MME/AMF UE S1AP/NGAP ID: Core context
- TEID (Tunnel Endpoint ID): GTP tunnels
- Call-ID: SIP sessions
- Session-Id: Diameter transactions

---

## Troubleshooting Methodology

### Step 1: Identify the Failure Point
- Which protocol shows the error?
- What is the exact failure message/cause?
- When did the failure occur?

### Step 2: Collect Related Traces
- Capture all related protocols
- Include timestamps for correlation
- Gather logs from all involved elements

### Step 3: Analyze Message Flow
- Verify request/response pairs
- Check for missing messages
- Review timing and sequence

### Step 4: Check Parameters
- Validate all IEs (Information Elements)
- Compare with working scenarios
- Review configuration consistency

### Step 5: Correlate with KPIs
- Check if KPIs show degradation
- Review alarm history
- Analyze trends over time

### Step 6: Root Cause Identification
- Isolate the failing component
- Determine if issue is configuration, capacity, or fault
- Check for known issues or bugs

### Step 7: Remediation
- Apply appropriate fix
- Verify resolution
- Monitor for recurrence
