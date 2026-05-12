# 5G Authentication - Technical Deep Dive

**Source**: Telecom Trainer (https://www.telecomtrainer.com/5g-authentication/)

## Overview

5G authentication verifies user/device identity before granting network access. It provides enhanced security and privacy compared to 4G/LTE authentication.

## 1. Authentication Architecture

### Key Network Functions

#### AUSF (Authentication Server Function)
- **Role**: Central authentication authority
- **Functions**:
  - Stores subscriber authentication credentials
  - Performs authentication calculations
  - Generates authentication vectors
  - Manages authentication state
- **Interfaces**: N12 (AMF), N13 (UDM)

#### UDM (Unified Data Management)
- **Role**: Subscriber data repository
- **Functions**:
  - Stores long-term keys (K, OPc)
  - Manages subscription data
  - Provides authentication data to AUSF
  - Handles SUPI/SUCI management
- **Interfaces**: N8 (AMF), N10 (SMF), N13 (AUSF)

#### AMF (Access and Mobility Management Function)
- **Role**: Authentication coordinator
- **Functions**:
  - Initiates authentication procedure
  - Forwards authentication messages
  - Manages security context
  - Stores derived keys
- **Interfaces**: N1 (UE), N2 (gNB), N12 (AUSF)

## 2. Authentication Protocol: 5G-AKA

### 5G-AKA (Authentication and Key Agreement)
Enhanced version of EPS-AKA used in 4G, with improved security features.

### Key Improvements over 4G
1. **SUPI Concealment**: Permanent identifier encrypted
2. **Unified Authentication**: Single framework for 3GPP and non-3GPP access
3. **Enhanced Key Hierarchy**: Separate keys for different functions
4. **Anti-Bidding Down**: Protection against downgrade attacks
5. **Home Network Control**: Home network authenticates, not visited network

## 3. Key Identifiers

### SUPI (Subscription Permanent Identifier)
- **Definition**: Permanent unique subscriber identifier
- **Format**: IMSI (15 digits) or Network Access Identifier (NAI)
- **Usage**: Internal to 5G core, never sent in clear over radio
- **Privacy**: Always concealed when transmitted

### SUCI (Subscription Concealed Identifier)
- **Definition**: Privacy-preserving encrypted SUPI
- **Purpose**: Protects SUPI from eavesdropping (IMSI catchers)
- **Encryption**: Public key encryption using home network's public key
- **Usage**: Sent over radio during initial registration

### GUTI (Globally Unique Temporary Identifier)
- **Definition**: Temporary identifier assigned after authentication
- **Purpose**: Used for subsequent communications instead of SUPI/SUCI
- **Validity**: Until UE moves to new tracking area or re-registers
- **Privacy**: Frequently changed to prevent tracking

## 4. Authentication Flow (Step-by-Step)

### Phase 1: Initial Registration

**Step 1: UE → AMF (Registration Request)**
```
Message: Registration Request
Contains: SUCI (encrypted SUPI), Security Capabilities
```

**Step 2: AMF → AUSF (Authentication Request)**
```
Message: Nausf_UEAuthentication_Authenticate Request
Contains: SUCI, Serving Network Name
```

**Step 3: AUSF → UDM (Authentication Data Request)**
```
Message: Nudm_UEAuthentication_Get Request
Contains: SUCI
Action: UDM decrypts SUCI to get SUPI, retrieves authentication data
```

### Phase 2: Authentication Challenge

**Step 4: UDM → AUSF (Authentication Vector)**
```
Message: 5G HE AV (Home Environment Authentication Vector)
Contains:
  - RAND (Random challenge, 128 bits)
  - AUTN (Authentication token, 128 bits)
  - XRES* (Expected response, 128 bits)
  - KAUSF (Key for AUSF, 256 bits)
```

**Step 5: AUSF → AMF (Authentication Challenge)**
```
Message: 5G SE AV (Serving Environment Authentication Vector)
Contains:
  - RAND
  - AUTN
  - HXRES* (Hashed expected response)
  - KSEAF (Key for SEAF, 256 bits)
```

**Step 6: AMF → UE (Authentication Request)**
```
Message: Authentication Request (NAS)
Contains: RAND, AUTN
```

### Phase 3: Authentication Response

**Step 7: UE Computation**
```
UE calculates:
  - Verifies AUTN (checks if network is authentic)
  - Computes RES* from RAND using secret key K
  - Derives KAUSF, KSEAF
```

**Step 8: UE → AMF (Authentication Response)**
```
Message: Authentication Response (NAS)
Contains: RES* (Response, 128 bits)
```

**Step 9: AMF Verification**
```
AMF computes:
  - HRES* = SHA-256(RES*)
  - Compares HRES* with HXRES*
  - If match: Authentication successful
```

**Step 10: AMF → AUSF (Confirmation)**
```
Message: Nausf_UEAuthentication_Authenticate Response
Contains: RES*
Action: AUSF confirms authentication success
```

### Phase 4: Security Mode Command

**Step 11: AMF → UE (Security Mode Command)**
```
Message: Security Mode Command (NAS)
Contains:
  - Selected NAS security algorithms
  - Integrity protection using KNAS_int
```

**Step 12: UE → AMF (Security Mode Complete)**
```
Message: Security Mode Complete (NAS)
Action: NAS security activated
```

## 5. Key Hierarchy

### Key Derivation Chain
```
K (Secret key in USIM, 128/256 bits)
  ↓
CK, IK (Cipher Key, Integrity Key from AKA)
  ↓
KAUSF (Key at AUSF, 256 bits)
  ↓
KSEAF (Key at SEAF/AMF, 256 bits)
  ↓
KAMF (Key at AMF, 256 bits)
  ↓
├─ KNASenc (NAS encryption key)
├─ KNASint (NAS integrity key)
└─ KgNB (Key for gNB, sent to RAN)
     ↓
     ├─ KRRCenc (RRC encryption)
     ├─ KRRCint (RRC integrity)
     ├─ KUPenc (User plane encryption)
     └─ KUPint (User plane integrity - optional)
```

### Key Usage
- **KAUSF**: Used by AUSF for authentication
- **KSEAF**: Used by SEAF (Security Anchor Function in AMF)
- **KAMF**: Master key at AMF
- **KNASenc**: Encrypts NAS messages (UE ↔ AMF)
- **KNASint**: Protects NAS message integrity
- **KgNB**: Sent to gNB for RRC and user plane security
- **KRRCenc/int**: RRC signaling security
- **KUPenc/int**: User data security

## 6. Security Features

### Subscriber Privacy Enhancements

**SUPI Concealment**
- SUPI encrypted with home network public key
- Only home network can decrypt (has private key)
- Prevents IMSI catchers from tracking users

**Temporary Identifiers**
- GUTI used after initial authentication
- Changed frequently to prevent tracking
- No permanent identifier sent over radio

### Mutual Authentication
- **Network authenticates UE**: Verifies UE has correct key K
- **UE authenticates Network**: Verifies AUTN to ensure legitimate network
- **Protection**: Prevents rogue base stations

### Anti-Bidding Down Protection
- **Mechanism**: UE and network exchange security capabilities
- **Protection**: Prevents attacker from forcing weaker algorithms
- **Enforcement**: Both sides must agree on strongest common algorithm

### Replay Protection
- **RAND**: Fresh random challenge each authentication
- **Sequence Number**: In AUTN prevents replay of old authentication vectors
- **Freshness**: Ensures authentication is current, not replayed

## 7. Integrity Protection and Encryption

### NAS Security (UE ↔ AMF)

**Integrity Protection**
- **Algorithm**: 128-NIA1, 128-NIA2, 128-NIA3
- **Key**: KNASint
- **Coverage**: All NAS messages after Security Mode Command
- **MAC**: 32-bit Message Authentication Code appended

**Encryption**
- **Algorithm**: 128-NEA0 (null), 128-NEA1, 128-NEA2, 128-NEA3
- **Key**: KNASenc
- **Coverage**: NAS message payload (not header)

### RRC Security (UE ↔ gNB)

**Integrity Protection**
- **Algorithm**: 128-NIA1, 128-NIA2, 128-NIA3
- **Key**: KRRCint
- **Coverage**: RRC signaling messages

**Encryption**
- **Algorithm**: 128-NEA1, 128-NEA2, 128-NEA3
- **Key**: KRRCenc
- **Coverage**: RRC signaling messages

### User Plane Security (UE ↔ gNB)

**Encryption**
- **Algorithm**: 128-NEA1, 128-NEA2, 128-NEA3
- **Key**: KUPenc
- **Coverage**: User data (PDCP layer)
- **Mandatory**: Always enabled

**Integrity Protection**
- **Algorithm**: 128-NIA1, 128-NIA2, 128-NEA3
- **Key**: KUPint
- **Coverage**: User data (PDCP layer)
- **Optional**: Typically not used (performance impact)

## 8. Non-3GPP Access Authentication

### N3IWF (Non-3GPP Interworking Function)
- **Purpose**: Enables UE to connect via non-3GPP access (WiFi, fixed)
- **Protocol**: IKEv2 (Internet Key Exchange) for IPsec tunnel
- **Authentication**: EAP-5G (Extensible Authentication Protocol)

### EAP-5G Flow
1. UE connects to N3IWF via untrusted non-3GPP access
2. N3IWF initiates EAP-5G authentication
3. Authentication messages tunneled to AUSF
4. Same 5G-AKA procedure, but over EAP
5. IPsec tunnel established after successful authentication

## 9. Security Context Management

### AMF Security Context
- **Contents**: KAMF, NAS security algorithms, UE security capabilities
- **Lifetime**: Until UE deregisters or moves to new AMF
- **Handover**: Transferred to new AMF during mobility

### gNB Security Context
- **Contents**: KgNB, RRC/UP security algorithms
- **Lifetime**: Until UE moves to new gNB
- **Handover**: New KgNB derived during handover

## 10. Common Authentication Scenarios

### Scenario 1: Initial Registration
- UE sends SUCI (first time or after power-on)
- Full 5G-AKA authentication performed
- GUTI assigned for future use

### Scenario 2: Periodic Registration Update
- UE sends GUTI (not SUCI)
- AMF may skip authentication if recent
- Or perform authentication if security context expired

### Scenario 3: Service Request
- UE sends GUTI
- No authentication needed (uses existing security context)
- Resumes data session

### Scenario 4: Handover
- UE moves to new gNB
- New KgNB derived (not full authentication)
- Security context transferred

### Scenario 5: AMF Change
- UE moves to new AMF area
- Security context transferred from old AMF
- May trigger re-authentication

## 11. Troubleshooting Authentication Issues

### Common Failures

**Authentication Reject**
- **Cause**: Wrong key K in USIM or UDM
- **Solution**: Verify SUPI and key provisioning

**AUTN Verification Failure**
- **Cause**: Sequence number mismatch
- **Solution**: Resynchronization procedure (not covered here)

**MAC Failure**
- **Cause**: Integrity check failed
- **Solution**: Check security algorithms, key derivation

**Timeout**
- **Cause**: Network congestion, UE/network issue
- **Solution**: Retry authentication

### Debug Tools
- **Wireshark**: Capture NAS messages (encrypted after Security Mode)
- **UE Logs**: Check authentication steps, key derivation
- **AUSF Logs**: Verify authentication vectors, success/failure
- **AMF Logs**: Check security context, algorithm selection

## 12. Best Practices

1. **Key Management**: Securely provision K in USIM and UDM
2. **Algorithm Selection**: Use strongest algorithms (NIA3/NEA3)
3. **SUPI Protection**: Always use SUCI for initial registration
4. **Monitoring**: Track authentication failures, investigate patterns
5. **Testing**: Validate authentication in lab before production
6. **Security Audits**: Regular review of authentication logs
7. **Incident Response**: Plan for authentication-related security incidents

## Summary

5G authentication provides robust security through:
- **5G-AKA**: Mutual authentication with enhanced privacy
- **SUPI Concealment**: Protection against IMSI catchers
- **Key Hierarchy**: Separate keys for different security functions
- **Integrity & Encryption**: Comprehensive protection of signaling and data
- **Flexibility**: Supports both 3GPP and non-3GPP access

**Key Takeaway**: 5G authentication significantly improves security and privacy compared to 4G, with SUPI concealment and enhanced key management being major advancements.
