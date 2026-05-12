# O-RAN Architecture Overview

**Source**: O-RAN Alliance specifications and technical documentation

## Overview

O-RAN (Open Radio Access Network) is an architecture that disaggregates traditional RAN into modular components with open interfaces, enabling multi-vendor interoperability and intelligent automation.

## Core Principles

### 1. Disaggregation
- Split monolithic RAN into smaller functional units
- Each unit can be from different vendors
- Enables best-of-breed component selection

### 2. Open Interfaces
- Standardized interfaces between components
- Vendor-neutral specifications
- Promotes competition and innovation

### 3. Intelligence & Automation
- AI/ML-driven RAN optimization
- Near-real-time and non-real-time control
- Data-driven decision making

## O-RAN Architecture Components

### 1. O-RU (O-RAN Radio Unit)

**Function**: Radio frequency processing and antenna interface

**Responsibilities:**
- RF transmission and reception
- Digital beamforming (optional)
- FFT/iFFT processing
- Cyclic Prefix addition/removal
- PRACH filtering
- Digital Front End (DFE): DUC, DDC, DPD, CFR

**Interfaces:**
- **Fronthaul**: Connects to O-DU via enhanced CPRI or eCPRI
- **Management**: O1 interface to SMO

**Deployment:**
- At cell site (tower, rooftop)
- Outdoor or indoor units
- Supports massive MIMO

### 2. O-DU (O-RAN Distributed Unit)

**Function**: Real-time Layer 1 (high PHY) and Layer 2 processing

**Responsibilities:**
- **High PHY**: Channel coding, rate matching, scrambling
- **MAC Layer**: Scheduling, HARQ, multiplexing
- **RLC Layer**: Segmentation, ARQ, reordering

**Interfaces:**
- **Fronthaul (F1)**: Connects to O-RU via eCPRI
- **Midhaul (F1)**: Connects to O-CU via F1 interface
- **E2**: Connects to Near-RT RIC
- **O1**: Connects to SMO for management

**Deployment:**
- Edge data center or cell site
- Virtualized (VNF) or containerized (CNF)
- Commercial off-the-shelf (COTS) servers

### 3. O-CU (O-RAN Central Unit)

**Function**: Non-real-time Layer 2 and Layer 3 processing

**Split into two sub-components:**

#### O-CU-CP (Control Plane)
**Responsibilities:**
- RRC (Radio Resource Control)
- PDCP-C (Control plane PDCP)
- Connection management
- Mobility management
- UE context management

**Interfaces:**
- **E1**: Connects to O-CU-UP
- **F1-C**: Control plane to O-DU
- **Xn-C**: Inter-gNB control plane
- **N2**: Connects to AMF (5GC)
- **E2**: Connects to Near-RT RIC
- **O1**: Connects to SMO

#### O-CU-UP (User Plane)
**Responsibilities:**
- PDCP-U (User plane PDCP)
- SDAP (Service Data Adaptation Protocol)
- QoS flow handling
- Header compression
- Encryption

**Interfaces:**
- **E1**: Connects to O-CU-CP
- **F1-U**: User plane to O-DU
- **Xn-U**: Inter-gNB user plane
- **N3**: Connects to UPF (5GC)
- **E2**: Connects to Near-RT RIC
- **O1**: Connects to SMO

**Deployment:**
- Regional data center
- Virtualized or containerized
- Can serve multiple O-DUs

### 4. Near-RT RIC (Near Real-Time RAN Intelligent Controller)

**Function**: Near real-time RAN optimization and control (10ms - 1s)

**Responsibilities:**
- RAN resource optimization
- Traffic steering
- QoS management
- Interference management
- Load balancing
- Handover optimization

**Key Features:**
- **xApps**: Pluggable applications for specific optimization tasks
- **E2 Interface**: Communicates with O-CU and O-DU
- **A1 Interface**: Receives policies from Non-RT RIC

**xApp Examples:**
- Traffic Steering xApp
- QoS Optimization xApp
- Anomaly Detection xApp
- Energy Savings xApp

**Deployment:**
- Edge or regional data center
- Kubernetes-based platform
- Supports multiple xApps concurrently

### 5. Non-RT RIC (Non Real-Time RAN Intelligent Controller)

**Function**: Non-real-time RAN optimization and policy management (>1s)

**Responsibilities:**
- RAN analytics and insights
- Policy-based guidance to Near-RT RIC
- ML model training
- Long-term optimization
- Configuration management

**Key Features:**
- **rApps**: Applications for analytics and policy
- **A1 Interface**: Sends policies to Near-RT RIC
- **O1/O2 Interfaces**: Management and data collection

**rApp Examples:**
- Traffic Prediction rApp
- Coverage Optimization rApp
- Capacity Planning rApp
- Anomaly Detection Training rApp

**Deployment:**
- Centralized data center
- Part of SMO (Service Management and Orchestration)

### 6. SMO (Service Management and Orchestration)

**Function**: End-to-end management and orchestration

**Responsibilities:**
- Lifecycle management of RAN functions
- Configuration management
- Performance management
- Fault management
- Software management

**Components:**
- Non-RT RIC
- O&M (Operations and Maintenance)
- Orchestration functions

**Interfaces:**
- **O1**: Management interface to all O-RAN components
- **O2**: Cloud infrastructure management
- **A1**: Policy interface to Near-RT RIC

## O-RAN Interfaces

### Fronthaul Interfaces

**eCPRI (enhanced Common Public Radio Interface)**
- **Between**: O-RU ↔ O-DU
- **Purpose**: Transport IQ samples and control
- **Split Options**: 7-2x (most common)
- **Transport**: Ethernet-based
- **Latency**: <100 microseconds
- **Bandwidth**: 10-25 Gbps per sector

**Open Fronthaul M-Plane**
- **Purpose**: Management and synchronization
- **Protocol**: NETCONF/YANG
- **Functions**: Configuration, fault management, performance monitoring

### Midhaul Interface

**F1 Interface**
- **Between**: O-DU ↔ O-CU
- **Standard**: 3GPP TS 38.470 series
- **Split**: F1-C (control) and F1-U (user)
- **Transport**: IP-based
- **Latency**: <10 milliseconds
- **Bandwidth**: Varies by traffic

### E2 Interface

**Purpose**: Near-RT RIC ↔ O-CU/O-DU communication

**Functions:**
- RAN monitoring (KPMs)
- RAN control (policies, parameters)
- Subscription management

**Services:**
- **REPORT**: Periodic or event-driven reports
- **INSERT**: Inject control messages
- **CONTROL**: Modify RAN behavior
- **POLICY**: Apply policies

**Protocol**: E2AP (E2 Application Protocol)

### A1 Interface

**Purpose**: Non-RT RIC ↔ Near-RT RIC communication

**Functions:**
- Policy delivery
- ML model deployment
- Enrichment information

**Protocol**: RESTful API (HTTP/JSON)

### O1 Interface

**Purpose**: SMO ↔ All O-RAN components management

**Functions:**
- Configuration management
- Fault management
- Performance management
- Software management

**Protocol**: NETCONF/YANG, REST

### O2 Interface

**Purpose**: SMO ↔ Cloud infrastructure management

**Functions:**
- Infrastructure resource management
- VM/container lifecycle
- Infrastructure monitoring

**Protocol**: O-Cloud API

## Functional Splits

### Split 7-2x (Most Common in O-RAN)

**O-RU Functions:**
- RF processing
- FFT/iFFT
- Cyclic Prefix
- PRACH filtering
- Digital beamforming (optional)

**O-DU Functions:**
- Resource element mapping
- Precoding
- Layer mapping
- Modulation/demodulation
- Channel coding/decoding
- MAC, RLC

**Advantages:**
- Balanced processing load
- Manageable fronthaul bandwidth
- Flexible deployment

### Split 2 (PDCP-RLC Split)

**O-DU Functions:**
- RLC, MAC, PHY

**O-CU Functions:**
- PDCP, RRC

**Used for**: F1 interface (midhaul)

## Intelligence and Automation

### RIC Architecture

```
Non-RT RIC (SMO)
    │ A1 (policies, ML models)
    ▼
Near-RT RIC
    │ E2 (control, monitoring)
    ▼
O-CU / O-DU
    │ F1
    ▼
O-RU
```

### xApps (Near-RT RIC Applications)

**Characteristics:**
- Microservices architecture
- Containerized deployment
- Lifecycle managed by RIC platform
- Access to RAN data via E2

**Common xApps:**
1. **Traffic Steering**: Optimize UE-cell associations
2. **QoS Optimization**: Dynamic QoS parameter adjustment
3. **Load Balancing**: Distribute load across cells
4. **Interference Management**: Coordinate interference mitigation
5. **Energy Savings**: Optimize power consumption

### rApps (Non-RT RIC Applications)

**Characteristics:**
- Long-term analytics
- ML model training
- Policy generation
- Historical data analysis

**Common rApps:**
1. **Traffic Prediction**: Forecast traffic patterns
2. **Coverage Optimization**: Identify coverage holes
3. **Capacity Planning**: Predict capacity needs
4. **Anomaly Detection**: Identify unusual patterns

## Deployment Scenarios

### Scenario 1: Macro Cell

```
Cell Site:
  - O-RU (outdoor)
  
Edge DC:
  - O-DU (virtualized)
  - Near-RT RIC
  
Regional DC:
  - O-CU-CP, O-CU-UP
  
Central DC:
  - SMO
  - Non-RT RIC
```

### Scenario 2: Small Cell

```
Small Cell Site:
  - O-RU (indoor/outdoor)
  - O-DU (co-located or edge)
  
Regional DC:
  - O-CU
  - Near-RT RIC
  
Central DC:
  - SMO
```

### Scenario 3: Indoor (Enterprise)

```
Enterprise Site:
  - O-RU (indoor)
  - O-DU (on-premises edge)
  - O-CU (on-premises or cloud)
  
Central:
  - SMO
  - Near-RT RIC (shared)
```

## Benefits of O-RAN

### 1. Vendor Diversity
- Multi-vendor RAN deployment
- Avoid vendor lock-in
- Best-of-breed selection

### 2. Cost Reduction
- COTS hardware (vs proprietary)
- Increased competition
- Operational efficiency

### 3. Innovation
- Open ecosystem
- Rapid feature deployment
- AI/ML-driven optimization

### 4. Flexibility
- Modular architecture
- Scalable deployment
- Cloud-native design

### 5. Performance
- Intelligent automation
- Real-time optimization
- Data-driven decisions

## Challenges

### 1. Integration Complexity
- Multi-vendor integration testing
- Interface compatibility
- End-to-end validation

### 2. Performance
- Fronthaul latency requirements
- Synchronization accuracy
- Processing overhead

### 3. Security
- Increased attack surface
- Multi-vendor security coordination
- Open interface protection

### 4. Maturity
- Evolving specifications
- Limited commercial deployments
- Ecosystem development

## O-RAN Alliance

### Mission
Develop open RAN specifications and promote ecosystem

### Working Groups
- WG1: Use Cases and Requirements
- WG2: Non-RT RIC and A1
- WG3: Near-RT RIC and E2
- WG4: Open Fronthaul
- WG5: Open F1/W1/E1/X2/Xn
- WG6: Cloudification and Orchestration
- WG7: White-box Hardware
- WG8: Stack Reference Design
- WG9: Open X-haul Transport
- WG10: OAM Architecture
- WG11: Security

### Key Specifications
- O-RAN Architecture Description
- O-RAN Fronthaul Specification
- O-RAN E2 Interface Specification
- O-RAN A1 Interface Specification
- O-RAN O1 Interface Specification

## Summary

O-RAN transforms traditional RAN through:

**Disaggregation**: Modular components (O-RU, O-DU, O-CU)
**Open Interfaces**: Standardized interfaces (eCPRI, F1, E2, A1, O1)
**Intelligence**: RIC-based automation (Near-RT and Non-RT)
**Flexibility**: Cloud-native, multi-vendor deployment

**Key Takeaway**: O-RAN enables operator control, vendor diversity, and AI-driven optimization through open, disaggregated architecture - representing the future of mobile network infrastructure.
