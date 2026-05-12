# Open5GS - Complete Setup and Configuration Guide

**Source**: Open5GS Official Documentation (https://open5gs.org/open5gs/docs/guide/01-quickstart/)

## Overview

Open5GS is an open-source implementation of 5G Core and EPC (4G core network). It implements 3GPP Release-17 specifications for both 4G/LTE and 5G SA/NSA networks.

## Architecture

### 4G / 5G NSA Core Components

**Control Plane:**
- **MME** (Mobility Management Entity): Session, mobility, paging, bearer management
- **HSS** (Home Subscriber Server): Authentication vectors, subscriber profiles
- **PCRF** (Policy and Charging Rules Function): Charging, policy enforcement
- **SGWC** (Serving Gateway Control Plane): S-GW control functions
- **PGWC/SMF** (Packet Gateway Control Plane): P-GW control functions

**User Plane:**
- **SGWU** (Serving Gateway User Plane): User data forwarding
- **PGWU/UPF** (Packet Gateway User Plane): Gateway to external networks

**Key Feature**: CUPS (Control/User Plane Separation) implemented

### 5G SA Core Functions

**Service-Based Architecture (SBA):**
- **NRF** (NF Repository Function): Service discovery
- **SCP** (Service Communication Proxy): Indirect communication
- **SEPP** (Security Edge Protection Proxy): Roaming security
- **AMF** (Access and Mobility Management Function): Connection, mobility
- **SMF** (Session Management Function): Session management
- **UPF** (User Plane Function): User data forwarding
- **AUSF** (Authentication Server Function): Authentication
- **UDM** (Unified Data Management): Subscriber data management
- **UDR** (Unified Data Repository): Data storage
- **PCF** (Policy Control Function): Policy, charging
- **NSSF** (Network Slice Selection Function): Slice selection
- **BSF** (Binding Support Function): Binding support

## Installation

### Prerequisites

**MongoDB Installation (Ubuntu 22.04):**
```bash
# Import MongoDB GPG key
sudo apt update
sudo apt install gnupg
curl -fsSL https://pgp.mongodb.com/server-8.0.asc | \
  sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg --dearmor

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg] \
  https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/8.0 multiverse" | \
  sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list

# Install MongoDB
sudo apt update
sudo apt install -y mongodb-org

# Start and enable MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

### Install Open5GS

**Ubuntu:**
```bash
sudo add-apt-repository ppa:open5gs/latest
sudo apt update
sudo apt install open5gs
```

**Debian:**
```bash
wget -qO - https://build.opensuse.org/projects/home:acetcom/signing_keys/download?kind=gpg | sudo apt-key add -
sudo sh -c "echo 'deb http://download.opensuse.org/repositories/home:/acetcom:/open5gs:/latest/Debian_10/ /' > /etc/apt/sources.list.d/open5gs.list"
sudo apt update
sudo apt install open5gs
```

**openSUSE:**
```bash
sudo zypper addrepo -f obs://home:mnhauke:open5gs home:mnhauke:open5gs
sudo zypper install mongodb-server mongodb-shell
sudo zypper install open5gs
```

### Install WebUI

**Install Node.js:**
```bash
# Download and import Nodesource GPG key
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | \
  sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg

# Create repository
NODE_MAJOR=20
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] \
  https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | \
  sudo tee /etc/apt/sources.list.d/nodesource.list

# Install Node.js
sudo apt update
sudo apt install nodejs -y
```

**Install WebUI:**
```bash
curl -fsSL https://open5gs.org/open5gs/assets/webui/install | sudo -E bash -
```

## Configuration

### Default Addresses

```
MongoDB   = 127.0.0.1 (subscriber data)
WebUI     = http://localhost:9999

# 4G/5G NSA Core
MME-s1ap  = 127.0.0.2:36412 (S1AP)
MME-gtpc  = 127.0.0.2:2123 (S11)
SGWC-gtpc = 127.0.0.3:2123 (S11)
SGWC-pfcp = 127.0.0.3:8805 (Sxa)
SMF-gtpc  = 127.0.0.4:2123 (S5c)
SMF-pfcp  = 127.0.0.4:8805 (N4/Sxb)
SMF-sbi   = 127.0.0.4:7777 (5G SBI)
SGWU-pfcp = 127.0.0.6:8805 (Sxa)
SGWU-gtpu = 127.0.0.6:2152 (S1-U, S5u)
UPF-pfcp  = 127.0.0.7:8805 (N4)
UPF-gtpu  = 127.0.0.7:2152 (N3, N4u)
HSS-frDi  = 127.0.0.8:3868 (S6a)
PCRF-frDi = 127.0.0.9:3868 (Gx)

# 5G SA Core
AMF-ngap  = 127.0.0.5:38412 (N2)
AMF-sbi   = 127.0.0.5:7777 (5G SBI)
NRF-sbi   = 127.0.0.10:7777 (5G SBI)
AUSF-sbi  = 127.0.0.11:7777 (5G SBI)
UDM-sbi   = 127.0.0.12:7777 (5G SBI)
PCF-sbi   = 127.0.0.13:7777 (5G SBI)
NSSF-sbi  = 127.0.0.14:7777 (5G SBI)
BSF-sbi   = 127.0.0.15:7777 (5G SBI)
UDR-sbi   = 127.0.0.20:7777 (5G SBI)
```

### Configure 4G/5G NSA Core

**Edit MME Configuration** (`/etc/open5gs/mme.yaml`):
```yaml
mme:
  freeDiameter: /etc/freeDiameter/mme.conf
  s1ap:
    server:
      - address: 10.10.0.2  # Change for external eNB
  gtpc:
    server:
      - address: 127.0.0.2
  gummei:
    plmn_id:
      mcc: 001  # Change to your PLMN
      mnc: 01
    mme_gid: 2
    mme_code: 1
  tai:
    plmn_id:
      mcc: 001
      mnc: 01
    tac: 1  # Change to your TAC
  security:
    integrity_order: [EIA2, EIA1, EIA0]
    ciphering_order: [EEA0, EEA1, EEA2]
```

**Edit SGWU Configuration** (`/etc/open5gs/sgwu.yaml`):
```yaml
sgwu:
  pfcp:
    server:
      - address: 127.0.0.6
  gtpu:
    server:
      - address: 10.11.0.6  # Change for external eNB
```

**Restart Services:**
```bash
sudo systemctl restart open5gs-mmed
sudo systemctl restart open5gs-sgwud
```

### Configure 5G SA Core

**Edit NRF Configuration** (`/etc/open5gs/nrf.yaml`):
```yaml
nrf:
  serving:
    - plmn_id:
        mcc: 001  # Change to your PLMN
        mnc: 01
  sbi:
    server:
      - address: 127.0.0.10
        port: 7777
```

**Edit AMF Configuration** (`/etc/open5gs/amf.yaml`):
```yaml
amf:
  sbi:
    server:
      - address: 127.0.0.5
        port: 7777
    client:
      nrf:
        - uri: http://127.0.0.10:7777
  ngap:
    server:
      - address: 10.10.0.5  # Change for external gNB
  guami:
    - plmn_id:
        mcc: 001
        mnc: 01
      amf_id:
        region: 2
        set: 1
  tai:
    - plmn_id:
        mcc: 001
        mnc: 01
      tac: 1
  plmn_support:
    - plmn_id:
        mcc: 001
        mnc: 01
      s_nssai:
        - sst: 1  # eMBB slice
        - sst: 2  # URLLC slice (optional)
  security:
    integrity_order: [NIA2, NIA1, NIA0]
    ciphering_order: [NEA0, NEA1, NEA2]
```

**Edit UPF Configuration** (`/etc/open5gs/upf.yaml`):
```yaml
upf:
  pfcp:
    server:
      - address: 127.0.0.7
  gtpu:
    server:
      - address: 10.11.0.7  # Change for external gNB
  session:
    - subnet: 10.45.0.1/16  # UE IP pool
    - subnet: 2001:db8:cafe::1/48  # IPv6 UE pool
  dns:
    - 8.8.8.8
    - 8.8.4.4
```

**Restart Services:**
```bash
sudo systemctl restart open5gs-nrfd
sudo systemctl restart open5gs-amfd
sudo systemctl restart open5gs-upfd
```

### Configure Logging

**Disable Duplicate Timestamps for journalctl:**
```yaml
# Add to any /etc/open5gs/*.yaml file
logger:
  default:
    timestamp: false  # Disable for stderr
  file:
    path: /var/log/open5gs/mme.log
    timestamp: true  # Keep for file
```

## Subscriber Management

### Using WebUI

**Access WebUI:**
- URL: http://localhost:9999
- Username: `admin`
- Password: `1423`

**Add Subscriber:**
1. Go to "Subscriber" menu
2. Click "+" button
3. Fill in:
   - **IMSI**: 001010000000001 (example)
   - **K**: Secret key from SIM (128-bit hex)
   - **OPc**: Operator key (128-bit hex)
   - **AMF**: 8000 (default)
   - **APN**: internet (or custom)
4. Click "SAVE"

**Network Slice Configuration:**
- **Slice 1 (SST=1)**: eMBB - Default data
- **Slice 2 (SST=2)**: URLLC - Low latency
- **Slice 3 (SST=3)**: mMTC - IoT devices

### Using CLI Tool

```bash
# Add subscriber
sudo /usr/bin/open5gs-dbctl add 001010000000001 \
  00112233445566778899aabbccddeeff \
  63bfa50ee6523365ff14c1f45f88737d

# Remove subscriber
sudo /usr/bin/open5gs-dbctl remove 001010000000001

# List subscribers
sudo /usr/bin/open5gs-dbctl showall
```

## Network Configuration

### Enable IP Forwarding

```bash
# Enable IPv4/IPv6 forwarding
sudo sysctl -w net.ipv4.ip_forward=1
sudo sysctl -w net.ipv6.conf.all.forwarding=1

# Make permanent
echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf
echo 'net.ipv6.conf.all.forwarding=1' | sudo tee -a /etc/sysctl.conf
```

### Configure NAT

```bash
# Add NAT rule for UE traffic
sudo iptables -t nat -A POSTROUTING -s 10.45.0.0/16 ! -o ogstun -j MASQUERADE
sudo ip6tables -t nat -A POSTROUTING -s 2001:db8:cafe::/48 ! -o ogstun -j MASQUERADE

# Accept traffic on ogstun interface
sudo iptables -I INPUT -i ogstun -j ACCEPT

# Optional: Block UE access to core host
sudo iptables -I INPUT -s 10.45.0.0/16 -j DROP
sudo ip6tables -I INPUT -s 2001:db8:cafe::/48 -j DROP
```

### Disable Firewall (if needed)

```bash
sudo ufw disable
```

## Connecting eNB/gNB

### Requirements

**For 4G eNB:**
- PLMN must match MME configuration
- TAC must match MME configuration
- S1AP connection to MME IP:36412

**For 5G gNB:**
- PLMN must match AMF configuration
- TAC must match AMF configuration
- NGAP connection to AMF IP:38412

### Verification

**Check MME/AMF logs:**
```bash
# Watch live logs
tail -f /var/log/open5gs/mme.log
tail -f /var/log/open5gs/amf.log

# Check for successful connection
grep "S1AP" /var/log/open5gs/mme.log
grep "NGAP" /var/log/open5gs/amf.log
```

**Expected log messages:**
```
[s1ap] INFO: S1 setup request (mme.c:123)
[s1ap] INFO: eNB-ID[0x1234] (mme.c:456)
[s1ap] INFO: S1 setup response (mme.c:789)
```

## UE Attachment

### Steps

1. Insert SIM card with provisioned IMSI
2. Configure APN to match Open5GS configuration
3. Enable data roaming (if PLMN mismatch)
4. Toggle airplane mode or manually search network
5. UE should attach and get IP from 10.45.0.0/16 pool

### Troubleshooting

**UE not attaching:**
- Check PLMN/TAC match between UE SIM, eNB/gNB, MME/AMF
- Verify subscriber provisioned in HSS/UDR
- Check APN configuration
- Enable data roaming if needed
- Check MME/AMF logs for authentication errors

**UE attached but no internet:**
- Verify NAT rules configured
- Check IP forwarding enabled
- Verify UPF/PGWU routing
- Check DNS configuration in UPF

## Service Management

### Start/Stop Services

**Stop all services:**
```bash
sudo systemctl stop open5gs-mmed
sudo systemctl stop open5gs-sgwcd
sudo systemctl stop open5gs-smfd
sudo systemctl stop open5gs-amfd
sudo systemctl stop open5gs-sgwud
sudo systemctl stop open5gs-upfd
sudo systemctl stop open5gs-hssd
sudo systemctl stop open5gs-pcrfd
sudo systemctl stop open5gs-nrfd
sudo systemctl stop open5gs-ausfd
sudo systemctl stop open5gs-udmd
sudo systemctl stop open5gs-pcfd
sudo systemctl stop open5gs-nssfd
sudo systemctl stop open5gs-bsfd
sudo systemctl stop open5gs-udrd
sudo systemctl stop open5gs-webui
```

**Restart specific service:**
```bash
sudo systemctl restart open5gs-amfd
```

**Check service status:**
```bash
sudo systemctl status open5gs-amfd
```

**View service logs:**
```bash
journalctl -u open5gs-amfd -f
```

## Uninstallation

**Remove Open5GS:**
```bash
# Ubuntu/Debian
sudo apt purge open5gs
sudo apt autoremove

# openSUSE
sudo zypper rm open5gs
```

**Remove logs:**
```bash
sudo rm -Rf /var/log/open5gs
```

**Remove WebUI:**
```bash
curl -fsSL https://open5gs.org/open5gs/assets/webui/uninstall | sudo -E bash -
```

## Advanced Configuration

### Network Slicing

**Configure multiple slices in AMF:**
```yaml
plmn_support:
  - plmn_id:
      mcc: 001
      mnc: 01
    s_nssai:
      - sst: 1  # eMBB
        sd: 0x000001
      - sst: 2  # URLLC
        sd: 0x000002
      - sst: 3  # mMTC
        sd: 0x000003
```

**Configure slice-specific UPF:**
```yaml
# In SMF configuration
session:
  - subnet: 10.45.0.1/16
    dnn: internet
    s_nssai:
      sst: 1
      sd: 0x000001
  - subnet: 10.46.0.1/16
    dnn: urllc
    s_nssai:
      sst: 2
      sd: 0x000002
```

### Multi-UPF Deployment

**Configure multiple UPFs:**
```yaml
# SMF configuration
upf:
  - dnn: internet
    pfcp:
      - address: 127.0.0.7
  - dnn: edge
    pfcp:
      - address: 10.20.0.7
```

## Best Practices

1. **Security**: Change default WebUI password immediately
2. **Monitoring**: Regularly check logs for errors
3. **Backups**: Backup MongoDB subscriber database
4. **Updates**: Keep Open5GS updated for security patches
5. **Testing**: Test in lab before production deployment
6. **Documentation**: Document custom configurations
7. **Firewall**: Configure firewall rules appropriately

## Summary

Open5GS provides complete open-source implementation of:
- **4G EPC**: MME, HSS, PCRF, SGW, PGW
- **5G SA Core**: AMF, SMF, UPF, AUSF, UDM, UDR, PCF, NRF, NSSF
- **Features**: CUPS, network slicing, SBA, multi-UPF
- **Tools**: WebUI for subscriber management, CLI tools

**Key Takeaway**: Open5GS enables rapid deployment of 4G/5G core networks for testing, development, and private network deployments using standard hardware and open-source software.
