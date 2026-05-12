# Your First LTE Network with Open5GS

**Source**: Open5GS Official Documentation (https://open5gs.org/open5gs/docs/tutorial/01-your-first-lte/)

## Overview

This tutorial guides you through setting up your first LTE network using Open5GS core and srsRAN eNodeB/UE simulator.

## Prerequisites

### System Requirements

**Operating System**:
- Ubuntu 22.04 LTS (recommended)
- Debian 11+
- Other Linux distributions supported

**Hardware**:
- CPU: 2+ cores
- RAM: 4GB minimum, 8GB recommended
- Disk: 20GB free space
- Network: Internet connection for installation

### Software Components

**Open5GS**: 4G/5G core network
**srsRAN**: eNodeB and UE simulator
**MongoDB**: Subscriber database
**Node.js**: WebUI

## Installation Steps

### 1. Install MongoDB

```bash
# Import MongoDB GPG key
sudo apt update
sudo apt install gnupg curl
curl -fsSL https://pgp.mongodb.com/server-8.0.asc | \
  sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg --dearmor

# Add repository
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] \
  https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/8.0 multiverse" | \
  sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list

# Install
sudo apt update
sudo apt install -y mongodb-org

# Start service
sudo systemctl start mongod
sudo systemctl enable mongod
```

### 2. Install Open5GS

```bash
# Add PPA repository
sudo add-apt-repository ppa:open5gs/latest
sudo apt update

# Install Open5GS
sudo apt install open5gs

# Verify installation
systemctl list-units | grep open5gs
```

### 3. Install WebUI

```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install WebUI
curl -fsSL https://open5gs.org/open5gs/assets/webui/install | sudo -E bash -
```

### 4. Install srsRAN

```bash
# Install dependencies
sudo apt install -y build-essential cmake libfftw3-dev libmbedtls-dev \
  libboost-program-options-dev libconfig++-dev libsctp-dev

# Clone repository
git clone https://github.com/srsran/srsRAN_4G.git
cd srsRAN_4G

# Build
mkdir build && cd build
cmake ../
make -j$(nproc)
sudo make install
sudo ldconfig
```

## Configuration

### 1. Configure Open5GS MME

Edit `/etc/open5gs/mme.yaml`:

```yaml
mme:
  freeDiameter: /etc/freeDiameter/mme.conf
  s1ap:
    server:
      - address: 127.0.0.2  # MME S1AP address
  gtpc:
    server:
      - address: 127.0.0.2  # MME GTP-C address
  gummei:
    plmn_id:
      mcc: 001  # Mobile Country Code
      mnc: 01   # Mobile Network Code
    mme_gid: 2
    mme_code: 1
  tai:
    plmn_id:
      mcc: 001
      mnc: 01
    tac: 1  # Tracking Area Code
  security:
    integrity_order: [EIA2, EIA1, EIA0]
    ciphering_order: [EEA0, EEA1, EEA2]
```

### 2. Configure Open5GS SGWU

Edit `/etc/open5gs/sgwu.yaml`:

```yaml
sgwu:
  pfcp:
    server:
      - address: 127.0.0.6
  gtpu:
    server:
      - address: 127.0.0.6  # SGWU GTP-U address
```

### 3. Configure Open5GS UPF

Edit `/etc/open5gs/upf.yaml`:

```yaml
upf:
  pfcp:
    server:
      - address: 127.0.0.7
  gtpu:
    server:
      - address: 127.0.0.7  # UPF GTP-U address
  session:
    - subnet: 10.45.0.1/16  # UE IP pool
  dns:
    - 8.8.8.8
    - 8.8.4.4
```

### 4. Restart Open5GS Services

```bash
sudo systemctl restart open5gs-mmed
sudo systemctl restart open5gs-sgwcd
sudo systemctl restart open5gs-smfd
sudo systemctl restart open5gs-sgwud
sudo systemctl restart open5gs-upfd
sudo systemctl restart open5gs-hssd
sudo systemctl restart open5gs-pcrfd
```

## Add Subscriber

### Using WebUI

1. **Access WebUI**:
   - URL: http://localhost:9999
   - Username: `admin`
   - Password: `1423`

2. **Add Subscriber**:
   - Click "Subscriber" menu
   - Click "+" button
   - Fill in details:
     - **IMSI**: 001010000000001
     - **K**: 465B5CE8B199B49FAA5F0A2EE238A6BC
     - **OPc**: E8ED289DEBA952E4283B54E88E6183CA
     - **AMF**: 8000
     - **APN**: internet
   - Click "SAVE"

### Using CLI

```bash
sudo /usr/bin/open5gs-dbctl add 001010000000001 \
  465B5CE8B199B49FAA5F0A2EE238A6BC \
  E8ED289DEBA952E4283B54E88E6183CA
```

## Configure srsRAN eNodeB

### 1. Edit eNodeB Configuration

Create `/etc/srsran/enb.conf`:

```ini
[enb]
enb_id = 0x19B
mcc = 001
mnc = 01
mme_addr = 127.0.0.2
gtp_bind_addr = 127.0.1.1
s1c_bind_addr = 127.0.1.1

[enb_files]
sib_config = sib.conf
rr_config = rr.conf
rb_config = rb.conf

[rf]
dl_earfcn = 3350
tx_gain = 80
rx_gain = 40

[pcap]
enable = false
```

### 2. Start eNodeB

```bash
sudo srsenb /etc/srsran/enb.conf
```

**Expected Output**:
```
Built in Release mode using commit ...
Opening 1 channels in RF device=default
S1AP: Sending S1 Setup Request
S1AP: S1 Setup Response received
```

## Configure srsRAN UE

### 1. Edit UE Configuration

Create `/etc/srsran/ue.conf`:

```ini
[usim]
mode = soft
algo = milenage
opc = E8ED289DEBA952E4283B54E88E6183CA
k = 465B5CE8B199B49FAA5F0A2EE238A6BC
imsi = 001010000000001
imei = 353490069873319

[rrc]
release = 15
ue_category = 4

[nas]
apn = internet
apn_protocol = ipv4

[rf]
dl_earfcn = 3350
```

### 2. Start UE

```bash
sudo srsue /etc/srsran/ue.conf
```

**Expected Output**:
```
Built in Release mode using commit ...
Opening 1 channels in RF device=default
Searching cell in DL EARFCN=3350
Found Cell: PCI=1, EARFCN=3350
RRC Connected
Network attach successful
PDN session established
```

## Network Setup

### Enable IP Forwarding

```bash
sudo sysctl -w net.ipv4.ip_forward=1
echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf
```

### Configure NAT

```bash
# Add NAT rule
sudo iptables -t nat -A POSTROUTING -s 10.45.0.0/16 ! -o ogstun -j MASQUERADE

# Accept traffic on ogstun
sudo iptables -I INPUT -i ogstun -j ACCEPT

# Make persistent
sudo apt install iptables-persistent
sudo netfilter-persistent save
```

## Testing

### 1. Check UE IP Address

```bash
# On UE terminal
ip addr show tun_srsue
```

**Expected**: IP from 10.45.0.0/16 range

### 2. Test Internet Connectivity

```bash
# Ping from UE
ping -I tun_srsue 8.8.8.8

# Test DNS
ping -I tun_srsue google.com

# Test HTTP
curl --interface tun_srsue http://www.google.com
```

### 3. Monitor Traffic

```bash
# Watch UE traffic
sudo tcpdump -i tun_srsue

# Watch core network traffic
sudo tcpdump -i ogstun

# Watch S1AP traffic
sudo tcpdump -i lo port 36412
```

## Verification

### Check Open5GS Logs

```bash
# MME logs
tail -f /var/log/open5gs/mme.log

# SGWU logs
tail -f /var/log/open5gs/sgwu.log

# UPF logs
tail -f /var/log/open5gs/upf.log
```

**Expected Messages**:
```
[mme] INFO: S1 setup request (mme.c:123)
[mme] INFO: Attach request (mme.c:456)
[mme] INFO: Attach accept (mme.c:789)
[upf] INFO: UE F-SEID[UP:0x1 CP:0x1] (upf.c:234)
```

### Check Subscriber Status

**WebUI**:
- Go to "Subscriber" menu
- Check "Online" status
- View session details

**CLI**:
```bash
sudo /usr/bin/open5gs-dbctl showall
```

## Troubleshooting

### UE Not Attaching

**Check PLMN**:
- Verify MCC/MNC match in MME, eNodeB, UE
- Check TAC configuration

**Check Subscriber**:
- Verify IMSI provisioned in HSS
- Check K and OPc values match
- Verify APN configured

**Check Logs**:
```bash
# MME logs for attach request
grep "Attach request" /var/log/open5gs/mme.log

# Check for authentication errors
grep "Authentication" /var/log/open5gs/mme.log
```

### No Internet Access

**Check IP Forwarding**:
```bash
sysctl net.ipv4.ip_forward
```

**Check NAT Rules**:
```bash
sudo iptables -t nat -L -n -v
```

**Check Routing**:
```bash
# On UE
ip route show

# Should have default route via tun_srsue
```

### eNodeB Not Connecting

**Check MME Address**:
- Verify MME address in enb.conf
- Check MME S1AP listening: `netstat -an | grep 36412`

**Check Firewall**:
```bash
sudo ufw status
# If enabled, allow S1AP
sudo ufw allow 36412/sctp
```

## Performance Tuning

### Increase Throughput

**Adjust RF Parameters**:
```ini
[rf]
tx_gain = 90  # Increase if signal weak
rx_gain = 50  # Increase if signal weak
```

**Enable Carrier Aggregation**:
```ini
[enb]
n_prb = 100  # Use maximum PRBs
```

### Reduce Latency

**Optimize Scheduling**:
```ini
[scheduler]
policy = time_rr  # Round-robin scheduling
```

**Reduce Processing Delay**:
```ini
[expert]
nof_phy_threads = 4  # Use more threads
```

## Advanced Configuration

### Multiple UEs

**Add More Subscribers**:
```bash
# Add subscriber 2
sudo /usr/bin/open5gs-dbctl add 001010000000002 \
  465B5CE8B199B49FAA5F0A2EE238A6BC \
  E8ED289DEBA952E4283B54E88E6183CA

# Start second UE with different IMSI
sudo srsue /etc/srsran/ue2.conf
```

### QoS Configuration

**Configure QCI in HSS**:
- WebUI → Subscriber → QoS
- Set QCI (1-9)
- Configure bandwidth limits

### Network Slicing

**Configure Slice in MME**:
```yaml
mme:
  slice:
    - sst: 1  # eMBB
      sd: 0x000001
    - sst: 2  # URLLC
      sd: 0x000002
```

## Summary

You've successfully set up your first LTE network:

**Components Deployed**:
- Open5GS EPC (MME, HSS, SGWU, UPF)
- srsRAN eNodeB (simulated)
- srsRAN UE (simulated)

**Capabilities**:
- UE attachment
- Internet connectivity
- Data sessions
- Multiple UEs support

**Next Steps**:
- Add more subscribers
- Configure QoS
- Implement network slicing
- Deploy on real hardware

**Key Takeaway**: Open5GS and srsRAN provide a complete, open-source LTE network stack for learning, testing, and development of mobile network applications.
