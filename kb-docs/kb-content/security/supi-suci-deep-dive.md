# SUPI and SUCI - 5G Subscriber Identifiers Deep Dive

**Source**: Nick vs Networking (https://nickvsnetworking.com/5g-subscriber-identifiers-suci-supi/)

## Overview

5G introduces new subscriber identifiers to enhance privacy and security. SUPI replaces IMSI, while SUCI provides privacy-preserving concealment.

## SUPI (Subscription Permanent Identifier)

### Definition
- **Purpose**: Permanent unique identifier for each subscriber in 5G
- **Replaces**: IMSI from 4G/LTE
- **Format**: Typically 15-16 digits (same as IMSI format)
- **Structure**: MCC/MNC prefix + subscriber number

### SUPI Types

**Type 0: IMSI-based SUPI**
- Most common format
- Looks identical to IMSI
- Used for 3GPP access (cellular)
- Example: 310170123456789 (MCC=310, MNC=170)

**Type 1: Network Access Identifier (NAI)**
- Used for non-3GPP access (WiFi, fixed)
- Format: RFC 4282 compliant
- Example: user@realm.com
- Less common in mobile devices

### Key Characteristics
- **Permanent**: Never changes for a subscriber
- **Unique**: Globally unique identifier
- **Private**: Never sent in clear text over radio
- **Internal**: Used only within 5G core network

### Privacy Problem in 4G
In LTE/EUTRAN, IMSI was occasionally sent in clear text:
- Initial attach procedure
- Certain handover scenarios
- Tracking area updates (sometimes)
- **Risk**: IMSI catchers could intercept and track users

## SUCI (Subscription Concealed Identifier)

### Definition
- **Purpose**: Privacy-preserving encrypted version of SUPI
- **Usage**: Sent over radio instead of SUPI
- **Replaces**: GUTI/TMSI/IMSI for initial transactions
- **Protection**: Only home network can decrypt

### Key Principle
> SUPI is NEVER sent over the air in clear text. SUCI is used for all plaintext transactions over radio.

### SUCI Generation

**Two Methods:**

**Method 1: UE-Generated SUCI (Fast)**
- UE reads SUCI_Calc_Info from SIM
- Extracts Home Network Public Key
- Generates ephemeral key pair
- Computes SUCI using cryptographic function
- **Speed**: Milliseconds

**Method 2: SIM-Generated SUCI (Slow)**
- UE sends GET IDENTITY command to SIM
- SIM performs cryptographic calculation
- Returns computed SUCI
- **Speed**: Seconds (SIM processing is slow)
- **Advantage**: More secure (key never leaves SIM)

## SUCI Structure

SUCI is composed of multiple concatenated fields:

### 1. SUPI Type (1 digit)
- **0**: IMSI-based SUPI
- **1**: Network Access Identifier (NAI)

### 2. Home Network Identifier
- **Mobile**: PLMN (MCC + MNC)
- **Example**: 310170 (MCC=310, MNC=170)
- **Purpose**: Identifies home operator

### 3. Routing Indicator (1-4 digits)
- **Purpose**: Routes authentication to correct UDM
- **Use Case**: MVNOs with separate UDM
- **Example**: Routing Indicator "10" → MVNO's UDM
- **Flexibility**: Enables multi-tenant UDM deployments

### 4. Protection Scheme ID (1 digit)
- **0**: Null scheme (no protection)
- **1**: ECIES Profile A
- **2**: ECIES Profile B

### 5. Home Network Public Key Identifier
- **Purpose**: Identifies which public key was used
- **Reason**: Allows key rotation
- **Format**: 1 byte (0-255)

### 6. Protection Scheme Output
- **Content**: Encrypted SUPI
- **Generation**: Cryptographic function output
- **Length**: Varies by protection scheme

### Complete SUCI Example
```
suci-0-310-170-10-1-5-A1B2C3D4E5F6...
  │   │  │   │  │  │ │ └─ Protection Scheme Output
  │   │  │   │  │  │ └─── Home Network Public Key ID (5)
  │   │  │   │  │  └───── Protection Scheme (1 = ECIES Profile A)
  │   │  │   │  └──────── Routing Indicator (10)
  │   │  │   └─────────── MNC (170)
  │   │  └─────────────── MCC (310)
  │   └────────────────── Home Network Identifier
  └────────────────────── SUPI Type (0 = IMSI)
```

## Protection Schemes

### Protection Scheme 0: Null Scheme
- **Function**: No concealment
- **Output**: SUPI in plain text
- **Security**: NONE
- **Use Case**: Testing, legacy compatibility
- **Risk**: Anyone can intercept SUPI

### Protection Scheme 1 & 2: ECIES (Elliptic Curve Integrated Encryption Scheme)

**What is ECIES?**
- Elliptic Curve Cryptography for encryption
- Public key encryption scheme
- Provides confidentiality and authentication
- Computationally efficient

**How it Works:**
1. Home network generates public/private key pair
2. Public key provisioned to SIM during personalization
3. UE/SIM uses public key to encrypt SUPI
4. Only home network (with private key) can decrypt

**Profile A vs Profile B:**
- Both use ECIES
- Different cryptographic parameters
- Different elliptic curves
- Profile A: Curve25519
- Profile B: secp256r1 (NIST P-256)
- **Details**: 3GPP TS 33.501 Annex C.3.4

### Cryptographic Process (Simplified)

**Encryption (UE/SIM):**
```
1. Get Home Network Public Key from SIM
2. Generate ephemeral key pair (public/private)
3. Compute shared secret using ECDH
4. Derive encryption key from shared secret
5. Encrypt SUPI with derived key
6. Output: Protection Scheme Output
```

**Decryption (Home Network):**
```
1. Extract ephemeral public key from SUCI
2. Use Home Network Private Key
3. Compute same shared secret using ECDH
4. Derive same encryption key
5. Decrypt Protection Scheme Output
6. Result: SUPI
```

## SUCI in Signaling Flow

### Initial Registration

**Step 1: UE → AMF (Registration Request)**
```
Message: Registration Request
Contains: SUCI (not SUPI!)
Purpose: Initial attach to network
```

**Step 2: AMF → AUSF (Authentication Request)**
```
Message: Authentication Request
Contains: SUCI
Purpose: Forward to authentication server
```

**Step 3: AUSF → UDM (Get Authentication Data)**
```
Message: Get Authentication Data
Contains: SUCI
Purpose: UDM decrypts SUCI to get SUPI
```

**Step 4: UDM Decryption**
```
Action: UDM uses Home Network Private Key
Process: Decrypt Protection Scheme Output
Result: SUPI extracted
```

**Step 5: Authentication Proceeds**
```
UDM retrieves subscriber data using SUPI
Generates authentication vectors
Returns to AUSF → AMF → UE
```

### After Initial Authentication

**GUTI Assignment:**
- After successful authentication, AMF assigns GUTI
- GUTI is temporary identifier (like TMSI in 4G)
- GUTI used for all subsequent communications
- GUTI changes frequently for privacy

**Subsequent Procedures:**
- Service requests: Use GUTI (not SUCI)
- Periodic registration updates: Use GUTI
- Handovers: Use GUTI
- **SUCI only used**: Initial attach or after GUTI expires

## Security Benefits

### Protection Against IMSI Catchers

**4G Problem:**
- IMSI sent in clear during initial attach
- IMSI catchers intercept and track users
- Permanent identifier exposed

**5G Solution:**
- SUCI sent instead of SUPI
- SUCI is encrypted with home network public key
- Only home network can decrypt
- **Result**: IMSI catchers get useless encrypted data

### Privacy Enhancements

**Unlinkability:**
- Each SUCI is different (ephemeral key changes)
- Cannot link multiple SUCI to same user
- Prevents long-term tracking

**Forward Secrecy:**
- Ephemeral keys used for each SUCI generation
- Compromising one SUCI doesn't reveal others
- Past communications remain secure

## Implementation Details

### SIM Provisioning

**During SIM Personalization:**
1. Home Network Public Key written to SIM
2. Protection Scheme configured
3. Routing Indicator set
4. SUPI (IMSI) programmed

**SIM Files:**
- **SUCI_Calc_Info**: Contains public key, scheme, routing indicator
- **IMSI/SUPI**: Stored in standard IMSI file
- **Access**: Protected by PIN/PUK

### UE Behavior

**When to Generate SUCI:**
- Power-on registration
- After GUTI expires
- Network requests SUCI explicitly
- Roaming to new network

**SUCI Caching:**
- UE may cache generated SUCI briefly
- Reduces SIM access (if SIM-generated)
- Cleared after successful registration

## Routing Indicator Use Cases

### Use Case 1: MVNO Separation
```
Main Operator UDM: Routing Indicator 0-9
MVNO A UDM: Routing Indicator 10-19
MVNO B UDM: Routing Indicator 20-29

AMF routing logic:
- RI 0-9 → Main Operator UDM
- RI 10-19 → MVNO A UDM
- RI 20-29 → MVNO B UDM
```

### Use Case 2: Geographic Distribution
```
East Region UDM: Routing Indicator 1
West Region UDM: Routing Indicator 2
Central Region UDM: Routing Indicator 3
```

### Use Case 3: Service Type
```
Consumer UDM: Routing Indicator 0
Enterprise UDM: Routing Indicator 5
IoT UDM: Routing Indicator 9
```

## Troubleshooting

### Common Issues

**Issue 1: SUCI Decryption Failure**
- **Symptom**: Authentication fails, UDM cannot decrypt SUCI
- **Cause**: Wrong public key in SIM, or UDM missing private key
- **Solution**: Verify key provisioning, check UDM configuration

**Issue 2: Routing Indicator Mismatch**
- **Symptom**: AMF routes to wrong UDM
- **Cause**: Routing Indicator not configured in AMF
- **Solution**: Update AMF routing table

**Issue 3: Null Scheme in Production**
- **Symptom**: SUPI sent in clear (security risk)
- **Cause**: Protection Scheme set to 0 (null)
- **Solution**: Reprovision SIM with ECIES scheme, or OTA update

**Issue 4: Slow Registration**
- **Symptom**: Initial attach takes 5-10 seconds
- **Cause**: SIM-generated SUCI (slow)
- **Solution**: Use UE-generated SUCI if supported

### Debug Tools

**Wireshark:**
- Capture N1 (UE-AMF) messages
- Look for Registration Request with SUCI
- Verify SUCI format and fields

**SIM Card Reader:**
- Read SUCI_Calc_Info file
- Verify public key provisioned
- Check protection scheme setting

**UDM Logs:**
- Check SUCI decryption success/failure
- Verify SUPI extraction
- Monitor authentication flow

## Best Practices

1. **Always Use ECIES**: Never use null scheme in production
2. **Key Management**: Securely store home network private key
3. **Key Rotation**: Plan for periodic public key updates
4. **Routing Indicator**: Design logical RI allocation scheme
5. **Testing**: Validate SUCI generation before SIM deployment
6. **Monitoring**: Track SUCI decryption failures
7. **OTA Updates**: Capability to update SIM protection scheme remotely

## Comparison: 4G vs 5G

| Aspect | 4G (IMSI) | 5G (SUPI/SUCI) |
|--------|-----------|----------------|
| Permanent ID | IMSI | SUPI |
| Over-the-air | IMSI (clear text) | SUCI (encrypted) |
| Privacy | Low (IMSI exposed) | High (SUCI concealed) |
| IMSI Catcher | Vulnerable | Protected |
| Temporary ID | GUTI/TMSI | GUTI |
| Encryption | None (initial) | Public key crypto |
| Tracking | Easy | Difficult |

## Summary

SUPI and SUCI represent major privacy improvements in 5G:

**SUPI:**
- Permanent subscriber identifier
- Replaces IMSI
- Never sent over radio
- Used internally in core network

**SUCI:**
- Privacy-preserving encrypted SUPI
- Sent over radio instead of SUPI
- Only home network can decrypt
- Protects against IMSI catchers

**Key Takeaway**: 5G's SUCI mechanism eliminates the privacy vulnerability of sending permanent identifiers in clear text, making subscriber tracking significantly more difficult while maintaining network functionality.
