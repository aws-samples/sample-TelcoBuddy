# 5G Identity Management - SUPI, SUCI, and GUTI

**Sources**: Telecom Trainer, TechPlayon

## Overview

5G introduces enhanced identity management to protect subscriber privacy while enabling efficient network operations. The system uses multiple identifiers for different purposes.

## Identity Types

### SUPI (Subscription Permanent Identifier)

**Definition**: Permanent subscriber identity stored in USIM and UDM

**Format Options**:
- **IMSI-based**: MCC-MNC-MSIN (e.g., 001-01-0000000001)
- **NAI-based**: username@realm (e.g., user@operator.com)

**Characteristics**:
- Never transmitted in clear over radio
- Stored securely in USIM
- Known only to UE and home network
- Basis for all other identities

**Usage**:
- Subscriber provisioning
- Billing and charging
- Internal network operations
- Never exposed to potential eavesdroppers

### SUCI (Subscription Concealed Identifier)

**Definition**: Encrypted form of SUPI for privacy protection

**Purpose**:
- Protect SUPI from IMSI catchers
- Prevent subscriber tracking
- Enable privacy-preserving authentication

**Encryption Method**: ECIES (Elliptic Curve Integrated Encryption Scheme)
- Public key encryption
- Home network public key used
- Only home network can decrypt
- Based on NIST P-256 curve

**Structure**:
```
SUCI = {
  Home Network Identifier (MCC-MNC)
  Routing Indicator
  Protection Scheme ID
  Home Network Public Key ID
  Encrypted SUPI
}
```

**Protection Schemes**:
- **Scheme 0**: Null scheme (SUPI in clear) - for testing only
- **Scheme 1**: Profile A (ECIES with AES-128-CTR)
- **Scheme 2**: Profile B (ECIES with AES-128-CBC)

**Generation Process**:
1. UE retrieves home network public key from USIM
2. UE generates ephemeral key pair
3. UE encrypts SUPI using ECIES
4. UE constructs SUCI with encrypted data
5. SUCI transmitted over radio

**Decryption**:
- Only UDM in home network can decrypt
- Uses home network private key
- Recovers SUPI for authentication

### GUTI (Globally Unique Temporary Identifier)

**Definition**: Temporary identifier assigned by AMF

**Purpose**:
- Identify UE in subsequent procedures
- Avoid SUCI transmission overhead
- Enable efficient paging
- Temporary privacy protection

**Structure**:
```
GUTI = {
  GUAMI (Globally Unique AMF Identifier)
    ├── PLMN ID (MCC-MNC)
    ├── AMF Region ID
    ├── AMF Set ID
    └── AMF Pointer
  5G-TMSI (5G Temporary Mobile Subscriber Identity)
}
```

**Lifecycle**:
- Assigned after successful authentication
- Valid until next authentication
- Changed periodically for privacy
- Released when UE deregisters

**Usage**:
- Service requests
- Paging
- Mobility updates
- Session management

### 5G-GUTI vs 4G GUTI

| Aspect | 4G GUTI | 5G-GUTI |
|--------|---------|---------|
| **Assigning Entity** | MME | AMF |
| **Structure** | GUMMEI + M-TMSI | GUAMI + 5G-TMSI |
| **Size** | 80 bits | Variable |
| **Flexibility** | Fixed format | More flexible |
| **Privacy** | Good | Enhanced |

## Identity Exchange Flow

### Initial Registration

**Step 1: UE Sends SUCI**
- UE has no GUTI yet
- Encrypts SUPI to SUCI
- Sends SUCI in Registration Request

**Step 2: Network Decrypts SUCI**
- AMF forwards SUCI to AUSF
- AUSF forwards to UDM
- UDM decrypts to get SUPI
- Authentication proceeds

**Step 3: Network Assigns GUTI**
- After successful authentication
- AMF allocates new GUTI
- Sends GUTI to UE
- UE stores for future use

### Subsequent Procedures

**UE Uses GUTI**:
- Service requests use GUTI
- Periodic updates use GUTI
- Paging uses GUTI
- Avoids SUCI overhead

**GUTI Refresh**:
- Periodically changed for privacy
- Changed after authentication
- Changed on mobility events
- Prevents long-term tracking

## Privacy Protection Mechanisms

### SUCI Encryption Benefits

**Prevents IMSI Catching**:
- IMSI catchers cannot read SUPI
- Encrypted identity useless to attackers
- Only home network can decrypt
- Protects against tracking

**Forward Secrecy**:
- Each SUCI uses new ephemeral key
- Past SUCIs cannot be decrypted
- Even if long-term key compromised
- Protects historical privacy

**Unlinkability**:
- Different SUCIs for same SUPI
- Cannot link multiple transmissions
- Prevents tracking across sessions
- Enhanced privacy

### GUTI Privacy Benefits

**Temporary Identity**:
- Changes periodically
- Prevents long-term tracking
- Reduces SUCI transmission
- Efficient and private

**Unpredictable Allocation**:
- Random GUTI assignment
- Cannot predict next GUTI
- Prevents tracking
- Enhanced privacy

## Routing Indicator

### Purpose

**Routing Information**:
- Helps route SUCI to correct home network
- Enables efficient message routing
- Supports multiple UDM instances
- Scalability enhancement

**Structure**:
- 1-4 digits
- Part of SUCI
- Configured in USIM
- Operator-specific

**Usage**:
- AMF uses to select AUSF
- AUSF uses to select UDM
- Enables distributed architecture
- Supports network slicing

## Implementation Considerations

### USIM Requirements

**Stored Data**:
- SUPI (permanent identity)
- Home network public key
- Protection scheme ID
- Routing indicator
- K (authentication key)

**Capabilities**:
- ECIES encryption
- Key generation
- SUCI construction
- Secure storage

### Network Requirements

**UDM**:
- Home network private key
- SUCI decryption capability
- SUPI database
- Key management

**AMF**:
- GUTI allocation
- GUTI management
- Identity mapping
- Privacy enforcement

**AUSF**:
- SUCI forwarding
- Identity validation
- Authentication coordination

## Security Considerations

### Threats Mitigated

**IMSI Catching**:
- SUCI encryption prevents
- Attackers cannot read SUPI
- Privacy protected

**Subscriber Tracking**:
- SUCI changes each time
- GUTI changes periodically
- Unlinkable identities

**Rogue Base Stations**:
- Cannot obtain SUPI
- Cannot track subscribers
- Limited attack surface

### Remaining Risks

**GUTI Tracking Window**:
- GUTI valid for period
- Temporary tracking possible
- Mitigated by frequent changes

**Metadata Analysis**:
- Traffic patterns still visible
- Timing analysis possible
- Requires additional protections

## Troubleshooting

### Common Issues

**SUCI Decryption Failure**:
- Check home network private key
- Verify public key in USIM
- Validate protection scheme
- Check UDM configuration

**GUTI Allocation Failure**:
- AMF capacity issues
- GUTI pool exhausted
- Configuration errors
- Check AMF logs

**Identity Mismatch**:
- GUTI not recognized
- SUCI decryption error
- Database inconsistency
- Trigger re-authentication

## Best Practices

### Privacy

1. **Use SUCI Always**: Never send SUPI in clear
2. **Frequent GUTI Changes**: Enhance privacy
3. **Strong Encryption**: Use Profile A or B
4. **Key Protection**: Secure private key storage
5. **Monitor Failures**: Track decryption errors

### Performance

1. **GUTI Reuse**: Reduce SUCI overhead
2. **Efficient Routing**: Optimize routing indicator
3. **Cache Management**: GUTI-SUPI mapping cache
4. **Load Balancing**: Distribute UDM load
5. **Fast Decryption**: Optimize SUCI processing

### Operational

1. **Key Management**: Secure key lifecycle
2. **USIM Provisioning**: Correct public key
3. **Database Sync**: SUPI-GUTI consistency
4. **Monitoring**: Track identity operations
5. **Incident Response**: Quick resolution

## Summary

5G identity management provides robust privacy protection:

**Key Identities**:
- **SUPI**: Permanent, never exposed
- **SUCI**: Encrypted, privacy-preserving
- **GUTI**: Temporary, efficient

**Privacy Features**:
- SUCI encryption prevents IMSI catching
- GUTI changes prevent tracking
- Unlinkable identities
- Forward secrecy

**Key Takeaway**: 5G's multi-layered identity system protects subscriber privacy while enabling efficient network operations through SUPI concealment (SUCI) and temporary identifiers (GUTI).
