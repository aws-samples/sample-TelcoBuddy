# O-RAN Radio Units - O-RU and O-DU Architecture

**Sources**: TechPlayon, O-RAN SC

## Overview

O-RAN (Open Radio Access Network) disaggregates traditional RAN into modular components with open interfaces. The O-RU (Radio Unit) and O-DU (Distributed Unit) are key components of this architecture.

## O-RU (Open Radio Unit)

### Definition

The O-RU is the radio frequency component that handles:
- RF transmission and reception
- Analog-to-digital conversion
- Digital-to-analog conversion
- Low-PHY processing (FFT/IFFT)

### Key Functions

**RF Processing**:
- Power amplification
- Filtering
- Up/down conversion
- Antenna interface

**Digital Front-End**:
- ADC/DAC conversion
- Digital filtering
- Carrier aggregation
- Beamforming (precoding)

**Low-PHY Layer**:
- FFT/IFFT operations
- Cyclic prefix addition/removal
- Resource element mapping
- PRACH filtering

### O-RU Categories

**Category A (Indoor)**:
- Low power (< 2W per carrier)
- Small form factor
- Enterprise deployments
- Indoor coverage

**Category B (Outdoor)**:
- Medium power (2-40W per carrier)
- Macro cell deployments
- Urban/suburban coverage
- Standard outdoor use

**Category C (Massive MIMO)**:
- High power (> 40W per carrier)
- Large antenna arrays (64T64R+)
- High-capacity urban areas
- Advanced beamforming

### Fronthaul Interface

**eCPRI (Enhanced Common Public Radio Interface)**:
- Connects O-RU to O-DU
- Packet-based transport
- Ethernet/IP based
- Reduced bandwidth vs CPRI

**Bandwidth Requirements**:
- Lower than traditional CPRI
- Functional split optimization
- Compression techniques
- Typical: 10-25 Gbps per O-RU

**Latency Requirements**:
- Strict timing constraints
- < 100 μs one-way delay
- Synchronization critical
- PTP (Precision Time Protocol)

## O-DU (Open Distributed Unit)

### Definition

The O-DU handles real-time Layer 1 (high-PHY) and Layer 2 processing:
- High-PHY functions
- MAC layer
- RLC layer
- Scheduling

### Key Functions

**High-PHY Processing**:
- Channel coding/decoding
- Rate matching
- Scrambling
- Modulation/demodulation
- HARQ processing

**MAC Layer**:
- Scheduling decisions
- HARQ management
- Multiplexing/demultiplexing
- Random access handling

**RLC Layer**:
- Segmentation/reassembly
- ARQ (Automatic Repeat Request)
- In-sequence delivery
- Duplicate detection

### O-DU Deployment

**Centralized**:
- Multiple O-RUs per O-DU
- Pooling benefits
- Efficient resource use
- Typical: 3-10 O-RUs per O-DU

**Distributed**:
- O-DU closer to O-RU
- Lower latency
- Edge deployment
- MEC integration

## Functional Split

### 3GPP Split Options

**Split 7.2x (O-RAN Standard)**:
- Low-PHY in O-RU
- High-PHY in O-DU
- Balanced processing
- Optimized fronthaul bandwidth

**Split Characteristics**:
- **O-RU**: FFT/IFFT, CP, RE mapping, beamforming
- **O-DU**: Coding, modulation, HARQ, MAC, RLC
- **Interface**: eCPRI over Ethernet
- **Bandwidth**: Reduced vs traditional CPRI

### Benefits of Split 7.2x

**Reduced Fronthaul**:
- Lower bandwidth requirements
- Cost-effective transport
- Scalable deployment

**Flexibility**:
- Vendor diversity
- Mix-and-match components
- Easier upgrades

**Centralization Benefits**:
- Resource pooling
- Coordinated scheduling
- Interference management

## O-RU to O-DU Interface

### eCPRI Protocol

**Layers**:
- **Application Layer**: User plane, control plane, sync
- **Transport Layer**: UDP/IP or Ethernet
- **Physical Layer**: Ethernet (1G/10G/25G/100G)

**Message Types**:
- IQ data (user plane)
- Control messages (C-plane)
- Synchronization messages (S-plane)

**Compression**:
- Block floating point
- Mu-law compression
- Reduces bandwidth 2-4x
- Configurable per carrier

### Timing and Synchronization

**Requirements**:
- Phase synchronization: ±1.5 μs
- Frequency synchronization: ±0.01 ppm
- Time synchronization: ±1.5 μs

**Mechanisms**:
- PTP (IEEE 1588v2)
- SyncE (Synchronous Ethernet)
- GNSS (GPS/Galileo)

## O-RU Management

### O1 Interface

**Purpose**: Management and orchestration

**Functions**:
- Configuration management
- Performance monitoring
- Fault management
- Software updates

**Protocol**: NETCONF/YANG

### M-Plane (Management Plane)

**Capabilities**:
- O-RU discovery
- Configuration download
- Status monitoring
- Alarm reporting
- File management

## Performance Characteristics

### O-RU Specifications

| Parameter | Typical Value |
|-----------|--------------|
| **Frequency Range** | 600 MHz - 6 GHz (FR1), 24-52 GHz (FR2) |
| **Bandwidth** | Up to 100 MHz (FR1), 400 MHz (FR2) |
| **Output Power** | 2W - 200W per carrier |
| **Antenna Ports** | 2T2R to 64T64R |
| **Latency** | < 100 μs processing |

### O-DU Specifications

| Parameter | Typical Value |
|-----------|--------------|
| **Processing Capacity** | 3-10 O-RUs |
| **Throughput** | Up to 20 Gbps |
| **Latency** | < 1 ms processing |
| **Scheduling** | Sub-millisecond granularity |

## Deployment Scenarios

### Urban Macro

**Configuration**:
- Category B/C O-RUs
- Centralized O-DU pool
- Fronthaul over fiber
- High capacity

**Benefits**:
- Efficient resource use
- Coordinated scheduling
- Cost-effective

### Enterprise/Indoor

**Configuration**:
- Category A O-RUs
- Distributed O-DUs
- Local breakout
- MEC integration

**Benefits**:
- Low latency
- Local processing
- Private network support

### Rural/Remote

**Configuration**:
- Category B O-RUs
- Distributed O-DUs
- Satellite backhaul option
- Extended coverage

**Benefits**:
- Cost-effective coverage
- Flexible deployment
- Reduced transport costs

## Vendor Ecosystem

### O-RU Vendors

**Traditional**:
- Ericsson
- Nokia
- Samsung
- Fujitsu

**New Entrants**:
- Mavenir
- Benetel
- Foxconn
- NEC

### O-DU Vendors

**Software-Based**:
- Mavenir
- Altiostar (Rakuten)
- Parallel Wireless
- Radisys

**Traditional**:
- Ericsson
- Nokia
- Samsung

## Testing and Validation

### O-RAN OTIC (Open Testing and Integration Centre)

**Purpose**:
- Interoperability testing
- Conformance validation
- Performance benchmarking

**Test Areas**:
- eCPRI interface
- Timing/sync
- Functional correctness
- Performance under load

### Plugfests

**Events**:
- Multi-vendor testing
- Integration validation
- Issue identification
- Ecosystem development

## Challenges

### Technical

**Timing/Synchronization**:
- Strict requirements
- Complex deployment
- GPS dependency
- Indoor challenges

**Fronthaul Capacity**:
- High bandwidth needs
- Fiber availability
- Cost considerations
- Latency constraints

**Interoperability**:
- Multi-vendor integration
- Conformance testing
- Bug resolution
- Version compatibility

### Operational

**Complexity**:
- More components to manage
- Distributed architecture
- Troubleshooting challenges
- Skills requirements

**Vendor Management**:
- Multiple vendors
- Integration responsibility
- Support coordination
- Upgrade synchronization

## Best Practices

### Deployment

1. **Plan Fronthaul**: Ensure adequate fiber capacity
2. **Timing Design**: Robust sync architecture
3. **Vendor Selection**: Proven interoperability
4. **Testing**: Thorough pre-deployment validation
5. **Monitoring**: Comprehensive performance tracking

### Operations

1. **Automation**: Automated configuration management
2. **Monitoring**: Real-time performance monitoring
3. **Troubleshooting**: Clear procedures and tools
4. **Upgrades**: Coordinated software updates
5. **Documentation**: Detailed configuration records

## Future Evolution

### Advanced Features

**Enhanced Beamforming**:
- Massive MIMO evolution
- AI-driven beam management
- Dynamic beam adaptation

**Network Slicing**:
- Slice-aware O-RU/O-DU
- Resource isolation
- QoS differentiation

**Energy Efficiency**:
- Dynamic power management
- Sleep modes
- Green RAN initiatives

### 6G Preparation

**Higher Frequencies**:
- Sub-THz support
- Advanced antenna systems
- New split options

**AI Integration**:
- AI-driven optimization
- Predictive maintenance
- Self-healing

## Summary

O-RU and O-DU form the foundation of O-RAN architecture:

**O-RU**:
- RF and low-PHY processing
- eCPRI interface to O-DU
- Multiple categories for different deployments

**O-DU**:
- High-PHY, MAC, RLC processing
- Centralized or distributed deployment
- Manages multiple O-RUs

**Key Benefits**:
- Vendor diversity
- Cost reduction
- Deployment flexibility
- Innovation acceleration

**Key Takeaway**: O-RAN's disaggregated architecture with O-RU and O-DU enables multi-vendor ecosystems, reduces costs, and accelerates innovation in radio access networks.
