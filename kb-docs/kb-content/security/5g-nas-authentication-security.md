# 5G NAS Authentication and Security Procedures

**Source**: Telecom Trainer (https://www.telecomtrainer.com/5g-nas-authentication-and-security-procedure-explained-step-by-step-5g-core-process/)

## Overview

NAS (Non-Access Stratum) Authentication and Security is the foundation of 5G security, ensuring only legitimate users access network services. This process involves the AMF, AUSF, and UDM working together to perform mutual authentication and establish security keys.

## NAS Layer Fundamentals

### Purpose

The NAS layer handles communication between UE and 5G Core for:
- **Mobility Management**: Registration, handover, paging
- **Session Management**: PDU session establishment
- **Security**: Authentication, encryption, integrity protection

### Security Objectives

**Mutual Authentication**:
- UE authenticates network
- Network authenticates UE
- Prevents rogue base stations

**Integrity Protection**:
- Protect control-plane messages from tampering
- Detect message modification
- Ensure message authenticity

**Encryption**:
- Protect user data confidentiality
- Secure signaling messages
- Generate session keys

## 5G Security Enhancements vs LTE

### New Features in 5G

**SUPI/SUCI Privacy Protection**:
- Encrypted subscriber identity
- Prevents IMSI catching
- Home network decryption

**Flexible Authentication**:
- 5G-AKA (SIM-based)
- EAP-AKA' (extensible)
- Support for non-3GPP access

**Separated Security Functions**:
- AUSF: Authentication logic
- UDM: Subscriber data management
- Clear separation of concerns

**Enhanced Key Hierarchy**:
- K_AUSF as master key
- Improved key derivation
- Better forward secrecy

**Algorithm Protection**:
- ABBA parameter
- Prevents downgrade attacks
- Ensures strong algorithms

**Network Slice Awareness**:
- Authentication per slice
- Slice-specific security
- NSSAI integration

## Authentication Flow Overview

### Step-by-Step Process

**Step 32: AUSF Selection**
- AMF selects appropriate AUSF
- Based on Serving Network ID (SNID)
- Based on Home PLMN information

**Step 33: Authentication Request to AUSF**
- AMF → AUSF: `Nausf_UEAuthenticate_authenticate Request`
- Contains SUCI (encrypted identity)
- Specifies authentication method

**Step 34: Authentication Data Request**
- AUSF → UDM: `Nudm_UEAuthenticate_Get Request`
- Requests authentication vectors
- Sends SUCI for decryption

**Step 35: Authentication Vector Generation**
- UDM decrypts SUCI to get SUPI
- ARPF generates authentication vectors
- Creates RAND, AUTN, XRES*, K_AUSF, ABBA

**Step 36: Authentication Data Response**
- UDM → AUSF: `Nudm_UEAuthenticate_Get Response`
- Returns authentication vectors
- Includes authentication method

**Step 37: Authentication Response to AMF**
- AUSF → AMF: `Nausf_UEAuthenticate_authenticate Response`
- Contains SUPI (decrypted)
- Provides authentication challenge data

**Step 38: Authentication Challenge to UE**
- AMF → UE: `NAS Authentication Request`
- Contains RAND, AUTN, ABBA, ngKSI
- UE validates and responds

## Detailed Component Roles

### AMF (Access and Mobility Management Function)

**Responsibilities**:
- Select appropriate AUSF
- Forward authentication requests
- Send challenge to UE
- Verify UE response
- Establish NAS security context

**Key Actions**:
- AUSF selection based on PLMN
- Coordinate authentication flow
- Manage NAS security mode
- Derive NAS keys from K_AMF

### AUSF (Authentication Server Function)

**Responsibilities**:
- Manage authentication logic
- Interact with UDM for subscriber data
- Validate authentication vectors
- Store XRES* for verification
- Derive K_AUSF

**Key Actions**:
- Process authentication requests from AMF
- Request authentication data from UDM
- Validate UE responses (RES* vs XRES*)
- Generate authentication result
- Provide SUPI to AMF

### UDM (Unified Data Management)

**Responsibilities**:
- Store subscriber data
- Decrypt SUCI to SUPI
- Generate authentication vectors via ARPF
- Manage subscriber security credentials

**Key Actions**:
- Decrypt SUCI using home network private key
- Retrieve subscriber authentication key (K)
- Generate authentication vectors
- Return authentication data to AUSF

### ARPF (Authentication Credential Repository and Processing Function)

**Responsibilities**:
- Generate authentication vectors
- Manage long-term keys
- Compute authentication parameters

**Key Actions**:
- Generate RAND (random challenge)
- Compute AUTN (authentication token)
- Compute XRES* (expected response)
- Derive K_AUSF (master key)
- Include ABBA (anti-bidding down)

## Authentication Parameters

### Key Parameters Explained

**SUCI (Subscription Concealed Identifier)**:
- Encrypted subscriber identity
- Protects SUPI from eavesdropping
- Uses ECIES encryption
- Only home network can decrypt

**SUPI (Subscription Permanent Identifier)**:
- Permanent subscriber identity
- Format: IMSI or NAI
- Decrypted by UDM from SUCI
- Never sent in clear over radio

**RAND (Random Challenge)**:
- 128-bit random number
- Generated by network
- Freshness guarantee
- Prevents replay attacks

**AUTN (Authentication Token)**:
- Proves network authenticity
- Contains SQN (sequence number)
- Contains MAC (message authentication code)
- UE validates before responding

**XRES* (Expected Response)**:
- Network's expected UE response
- Stored at AUSF for verification
- Derived from K and RAND
- Compared with UE's RES*

**RES* (Response)**:
- UE's computed response
- Sent to network for verification
- Proves UE has valid K
- Must match XRES* for success

**K_AUSF (AUSF Key)**:
- Master key for session
- Derived from K and RAND
- Used to derive subsequent keys
- Enables forward secrecy

**ABBA (Anti-Bidding down Between Architectures)**:
- Prevents algorithm downgrade attacks
- Ensures strong security algorithms
- Protects against forced fallback
- Included in key derivation

**ngKSI (NAS Key Set Identifier)**:
- Identifies the key set in use
- Allows key reuse
- Simplifies re-authentication
- Range: 0-6 (7 reserved)

## Authentication Vector Structure

### Complete Authentication Vector

```
Authentication Vector (AV):
├── RAND: 128-bit random challenge
├── AUTN: Authentication token
│   ├── SQN ⊕ AK: Concealed sequence number
│   ├── AMF: Authentication Management Field
│   └── MAC: Message Authentication Code
├── XRES*: Expected response (128-bit)
├── K_AUSF: AUSF master key (256-bit)
└── ABBA: Anti-bidding down parameter
```

### Key Derivation Hierarchy

```
K (Long-term key in USIM)
    ↓
CK, IK (Cipher Key, Integrity Key)
    ↓
K_AUSF (AUSF master key)
    ↓
K_SEAF (SEAF key at AMF)
    ↓
K_AMF (AMF master key)
    ↓
├── K_NASenc (NAS encryption key)
├── K_NASint (NAS integrity key)
└── K_gNB (gNB master key)
        ↓
        ├── K_RRCenc (RRC encryption)
        ├── K_RRCint (RRC integrity)
        ├── K_UPenc (User plane encryption)
        └── K_UPint (User plane integrity)
```

## Authentication Methods

### 5G-AKA (5G Authentication and Key Agreement)

**Characteristics**:
- Derived from LTE-AKA
- SIM/USIM-based authentication
- Uses symmetric key cryptography
- New key hierarchy with K_AUSF

**Use Cases**:
- Mobile operators with SIM cards
- 3GPP access (5G NR)
- Traditional mobile authentication

**Process**:
1. UE and network share secret key K
2. Network sends RAND and AUTN
3. UE validates AUTN (network authentication)
4. UE computes RES* and sends to network
5. Network validates RES* (UE authentication)
6. Both derive K_AUSF and subsequent keys

### EAP-AKA' (Extensible Authentication Protocol)

**Characteristics**:
- Based on EAP framework
- Supports non-3GPP access
- Flexible authentication
- Wi-Fi integration

**Use Cases**:
- Non-3GPP access (Wi-Fi)
- Hybrid networks
- Untrusted non-3GPP access
- Enterprise integration

**Process**:
1. EAP identity request/response
2. EAP-AKA' challenge/response
3. Multiple round-trips possible
4. EAP success/failure
5. Key derivation

### Method Selection

**Factors**:
- Access type (3GPP vs non-3GPP)
- Subscriber profile
- Network policy
- UE capabilities

**AUSF Decision**:
- Queries UDM for subscriber authentication method
- Selects based on network configuration
- Dynamically adapts per subscriber

## NAS Security Mode Command

### After Successful Authentication

**AMF sends NAS Security Mode Command**:
- Activates NAS security
- Specifies encryption algorithm
- Specifies integrity algorithm
- Includes security capabilities

**UE responds with NAS Security Mode Complete**:
- Confirms algorithm selection
- Activates NAS security
- All subsequent NAS messages protected

### Security Algorithms

**Integrity Algorithms** (NIA):
- NIA0: Null integrity (no protection)
- NIA1: SNOW 3G
- NIA2: AES-128
- NIA3: ZUC

**Encryption Algorithms** (NEA):
- NEA0: Null encryption (no protection)
- NEA1: SNOW 3G
- NEA2: AES-128
- NEA3: ZUC

**Algorithm Selection**:
- Based on UE capabilities
- Based on network policy
- Preference order configured
- ABBA prevents downgrade

## Security Features

### SUCI-Based Identity Protection

**Problem in LTE**:
- IMSI sent in clear
- IMSI catchers can track users
- Privacy vulnerability

**5G Solution**:
- SUPI encrypted to SUCI
- Only home network can decrypt
- Uses ECIES public key encryption
- Prevents tracking

### Mutual Authentication

**Network Authentication**:
- UE validates AUTN
- Checks sequence number (SQN)
- Verifies MAC
- Prevents rogue base stations

**UE Authentication**:
- Network validates RES*
- Compares with XRES*
- Proves UE has valid K
- Prevents unauthorized access

### Algorithm Protection (ABBA)

**Purpose**:
- Prevent downgrade attacks
- Ensure strong algorithms
- Protect against forced fallback

**Mechanism**:
- ABBA included in key derivation
- Different ABBA for different architectures
- Binds keys to security context
- Detects algorithm manipulation

### Network Slice Awareness

**Integration**:
- Authentication can be slice-specific
- NSSAI included in authentication
- Slice-specific security policies
- Per-slice key derivation

## Common Authentication Failures

### Failure Scenarios

**MAC Failure**:
- AUTN validation fails
- Indicates network authentication failure
- Possible rogue base station
- UE rejects authentication

**SQN Out of Sync**:
- Sequence number mismatch
- Triggers synchronization failure
- UE sends sync failure message
- Network re-synchronizes

**Authentication Reject**:
- Network rejects UE
- Invalid credentials
- Subscription issue
- UE barred from network

**Timeout**:
- No response from UE
- Network timeout
- Retry or abort

### Troubleshooting

**Check Subscriber Data**:
- Verify SUPI provisioned in UDM
- Check authentication method
- Validate K value
- Confirm subscription active

**Verify Network Configuration**:
- AUSF reachable from AMF
- UDM reachable from AUSF
- Correct PLMN configuration
- Algorithm support

**Analyze Logs**:
- AMF logs for AUSF selection
- AUSF logs for UDM interaction
- UDM logs for SUCI decryption
- UE logs for AUTN validation

## Best Practices

### Security

1. **Use Strong Algorithms**: Prefer NIA2/NEA2 or NIA3/NEA3
2. **Protect Keys**: Secure key storage in USIM
3. **Monitor Failures**: Track authentication failures
4. **Update Regularly**: Keep security patches current
5. **Audit Access**: Review authentication logs

### Performance

1. **Optimize AUSF Selection**: Minimize latency
2. **Cache Authentication Vectors**: Reduce UDM load
3. **Fast Re-authentication**: Use ngKSI for key reuse
4. **Parallel Processing**: Handle multiple authentications
5. **Monitor Latency**: Track authentication time

### Operational

1. **Subscriber Provisioning**: Accurate data in UDM
2. **Key Management**: Secure key lifecycle
3. **Incident Response**: Quick authentication failure resolution
4. **Capacity Planning**: Scale AUSF/UDM appropriately
5. **Testing**: Regular security testing

## Summary

5G NAS Authentication and Security is the foundation of 5G network security:

**Key Components**:
- AMF: Coordinates authentication
- AUSF: Manages authentication logic
- UDM: Stores subscriber data, generates vectors

**Key Features**:
- SUPI/SUCI privacy protection
- Mutual authentication
- Flexible authentication methods (5G-AKA, EAP-AKA')
- Enhanced key hierarchy
- Algorithm protection (ABBA)

**Security Benefits**:
- Prevents IMSI catching
- Protects against rogue base stations
- Ensures strong encryption
- Enables network slice security

**Key Takeaway**: 5G NAS authentication provides robust, privacy-preserving security that protects subscriber identity, ensures mutual authentication, and establishes secure communication channels for all subsequent 5G services.
