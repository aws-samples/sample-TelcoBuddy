# 3GPP Cause Codes Reference

## NAS-EMM Cause Codes (4G LTE)

### Cause Code 2: IMSI unknown in HSS
**Description:** The IMSI provided by the UE is not recognized in the HSS database.
**Troubleshooting:** Check HSS subscription data. Verify IMSI provisioning. Confirm subscriber is active in billing system.
**Impact:** UE cannot attach to network.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 3: Illegal UE
**Description:** The UE is not allowed to operate in the network.
**Troubleshooting:** Check IMEI blacklist. Verify device certification. Review security policies.
**Impact:** UE is permanently barred from network access.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 5: IMEI not accepted
**Description:** The IMEI is not accepted by the network.
**Troubleshooting:** Verify IMEI is not blacklisted. Check EIR database. Confirm device type approval.
**Impact:** Device cannot register on network.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 6: Illegal ME
**Description:** Mobile Equipment is not allowed to operate.
**Troubleshooting:** Check EIR blacklist. Verify device is not stolen/lost. Review device certification.
**Impact:** Device permanently barred.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 7: EPS services not allowed
**Description:** UE is not authorized for EPS services.
**Troubleshooting:** Check subscription profile and APN configuration. Verify EPS subscription is active. Review roaming agreements if applicable.
**Impact:** UE cannot access LTE data services.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 8: EPS services and non-EPS services not allowed
**Description:** UE cannot access any services.
**Troubleshooting:** Check subscription status. Verify account is active. Review service restrictions.
**Impact:** Complete service denial.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 9: UE identity cannot be derived
**Description:** Network cannot determine UE identity.
**Troubleshooting:** Check IMSI/GUTI validity. Review identity request/response procedures. Verify HSS connectivity.
**Impact:** Attach procedure fails.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 10: Implicitly detached
**Description:** UE was implicitly detached by network.
**Troubleshooting:** Check for network-initiated detach reasons. Review inactivity timers. Verify MME logs.
**Impact:** UE must re-attach.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 11: PLMN not allowed
**Description:** The PLMN is not allowed for this subscriber.
**Troubleshooting:** Check roaming agreements. Verify PLMN restrictions in subscription. Review forbidden PLMN list.
**Impact:** UE cannot register on this PLMN.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 12: Tracking area not allowed
**Description:** The tracking area is not allowed for this subscriber.
**Troubleshooting:** Check TA restrictions in subscription. Verify regional roaming settings. Review TA list configuration.
**Impact:** UE cannot camp in this TA.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 13: Roaming not allowed in this tracking area
**Description:** Roaming is restricted in this TA.
**Troubleshooting:** Check roaming agreements for this region. Verify TA-specific roaming restrictions. Review subscription roaming profile.
**Impact:** Roaming UE cannot access services in this TA.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 15: No suitable cells in tracking area
**Description:** No acceptable cells found in the TA.
**Troubleshooting:** Check cell availability. Verify cell barring status. Review access class restrictions.
**Impact:** UE cannot find suitable cell.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 17: Network failure
**Description:** General network failure occurred.
**Troubleshooting:** Check S1/S6a interface connectivity and HSS availability. Review MME CPU/memory. Verify core network element status.
**Impact:** Service disruption.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 18: CS domain not available
**Description:** Circuit-switched domain is unavailable.
**Troubleshooting:** Check MSC connectivity. Verify CSFB configuration. Review SGs interface status.
**Impact:** Voice calls may fail.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 19: ESM failure
**Description:** EPS Session Management procedure failed.
**Troubleshooting:** Check bearer establishment logs. Verify PGW/SGW connectivity. Review QoS parameters.
**Impact:** Data bearer cannot be established.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 20: MAC failure
**Description:** Message Authentication Code verification failed.
**Troubleshooting:** Check security keys. Verify authentication vectors. Review HSS-MME synchronization.
**Impact:** Security failure, attach rejected.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 21: Synch failure
**Description:** Synchronization failure in authentication.
**Troubleshooting:** Check sequence number synchronization. Verify HSS authentication parameters. Review AUTS handling.
**Impact:** Authentication fails, requires re-sync.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 22: Congestion
**Description:** Network congestion detected.
**Troubleshooting:** Check MME CPU/memory, S1AP message queues. Review load balancing. Verify capacity planning.
**Impact:** Service delays or rejections.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 23: UE security capabilities mismatch
**Description:** UE and network security capabilities don't match.
**Troubleshooting:** Check supported encryption algorithms. Verify security policy configuration. Review UE capabilities.
**Impact:** Security mode command fails.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 24: Security mode rejected, unspecified
**Description:** Security mode command rejected.
**Troubleshooting:** Check security configuration. Verify encryption/integrity algorithms. Review UE security logs.
**Impact:** Attach procedure fails.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 25: Not authorized for this CSG
**Description:** UE not authorized for Closed Subscriber Group.
**Troubleshooting:** Check CSG membership list. Verify CSG subscription. Review femtocell access control.
**Impact:** Cannot access CSG cell.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

### Cause Code 40: No EPS bearer context activated
**Description:** No active EPS bearer exists.
**Troubleshooting:** Check bearer establishment procedures. Verify default bearer activation. Review S11/S5 interface.
**Impact:** No data connectivity.
**Related Spec:** 3GPP TS 24.301 Section 9.9.3.9

---

## NAS-5GMM Cause Codes (5G)

### Cause Code 3: Illegal UE
**Description:** UE is not allowed to operate in 5G network.
**Troubleshooting:** Check SUPI/SUCI validation. Verify 5G subscription. Review security policies.
**Impact:** UE barred from 5G access.
**Related Spec:** 3GPP TS 24.501 Section 9.11.3.2

### Cause Code 5: PEI not accepted
**Description:** Permanent Equipment Identifier not accepted.
**Troubleshooting:** Check 5G-GUTI/PEI validation. Verify device certification. Review EIR database.
**Impact:** Device cannot register.
**Related Spec:** 3GPP TS 24.501 Section 9.11.3.2

### Cause Code 7: 5GS services not allowed
**Description:** UE not authorized for 5GS services.
**Troubleshooting:** Check AMF subscription data and network slice configuration. Verify 5G subscription profile. Review DNN access.
**Impact:** Cannot access 5G services.
**Related Spec:** 3GPP TS 24.501 Section 9.11.3.2

### Cause Code 10: Implicitly de-registered
**Description:** UE implicitly de-registered by network.
**Troubleshooting:** Check de-registration triggers. Review inactivity timers. Verify AMF logs.
**Impact:** UE must re-register.
**Related Spec:** 3GPP TS 24.501 Section 9.11.3.2

### Cause Code 11: PLMN not allowed
**Description:** PLMN not allowed for this subscriber.
**Troubleshooting:** Check 5G roaming agreements. Verify PLMN restrictions. Review forbidden PLMN list.
**Impact:** Cannot register on this PLMN.
**Related Spec:** 3GPP TS 24.501 Section 9.11.3.2

### Cause Code 12: Tracking area not allowed
**Description:** Registration area not allowed.
**Troubleshooting:** Check RA restrictions. Verify regional access policies. Review TAC configuration.
**Impact:** Cannot camp in this area.
**Related Spec:** 3GPP TS 24.501 Section 9.11.3.2

### Cause Code 15: No suitable cells in tracking area
**Description:** No acceptable cells in registration area.
**Troubleshooting:** Check gNB availability. Verify cell barring. Review access restrictions.
**Impact:** Cannot find suitable cell.
**Related Spec:** 3GPP TS 24.501 Section 9.11.3.2

### Cause Code 20: MAC failure
**Description:** Message Authentication Code failed.
**Troubleshooting:** Check 5G security keys. Verify AUSF authentication. Review key derivation.
**Impact:** Security failure.
**Related Spec:** 3GPP TS 24.501 Section 9.11.3.2

### Cause Code 21: Synch failure
**Description:** Authentication synchronization failed.
**Troubleshooting:** Check sequence numbers. Verify UDM/AUSF sync. Review AUTS handling.
**Impact:** Authentication requires re-sync.
**Related Spec:** 3GPP TS 24.501 Section 9.11.3.2

### Cause Code 22: Congestion
**Description:** Network congestion in 5GC.
**Troubleshooting:** Check AMF load. Review NGAP message queues. Verify capacity.
**Impact:** Service delays.
**Related Spec:** 3GPP TS 24.501 Section 9.11.3.2

### Cause Code 27: N1 mode not allowed
**Description:** N1 mode operation not permitted.
**Troubleshooting:** Check UE mode capabilities. Verify AMF configuration. Review subscription settings.
**Impact:** Cannot operate in N1 mode.
**Related Spec:** 3GPP TS 24.501 Section 9.11.3.2

### Cause Code 31: Redirection to EPC required
**Description:** UE must redirect to 4G EPC.
**Troubleshooting:** Check interworking configuration. Verify EPS fallback settings. Review coverage.
**Impact:** Must use 4G instead of 5G.
**Related Spec:** 3GPP TS 24.501 Section 9.11.3.2

### Cause Code 62: No network slices available
**Description:** Requested network slice not available.
**Troubleshooting:** No network slices available - verify NSSAI configuration. Check slice availability. Review AMF slice support. Verify UDM subscription.
**Impact:** Cannot access requested slice.
**Related Spec:** 3GPP TS 24.501 Section 9.11.3.2

### Cause Code 65: Maximum number of PDU sessions reached
**Description:** PDU session limit exceeded.
**Troubleshooting:** Check active PDU sessions. Verify session limits. Review SMF configuration.
**Impact:** Cannot establish new PDU session.
**Related Spec:** 3GPP TS 24.501 Section 9.11.3.2

### Cause Code 67: Insufficient resources for specific slice and DNN
**Description:** Resources unavailable for slice/DNN combination.
**Troubleshooting:** Check SMF/UPF capacity. Verify slice resources. Review DNN configuration.
**Impact:** Service unavailable for this slice/DNN.
**Related Spec:** 3GPP TS 24.501 Section 9.11.3.2

### Cause Code 69: Insufficient resources for specific slice
**Description:** Slice resources exhausted.
**Troubleshooting:** Check slice capacity. Verify resource allocation. Review slice SLA.
**Impact:** Slice services unavailable.
**Related Spec:** 3GPP TS 24.501 Section 9.11.3.2

### Cause Code 72: Non-3GPP access to 5GCN not allowed
**Description:** Non-3GPP access restricted.
**Troubleshooting:** Check N3IWF configuration. Verify untrusted access policies. Review subscription.
**Impact:** WiFi calling/access denied.
**Related Spec:** 3GPP TS 24.501 Section 9.11.3.2

### Cause Code 73: Serving network not authorized
**Description:** Current serving network not authorized.
**Troubleshooting:** Check roaming agreements. Verify network authorization. Review PLMN policies.
**Impact:** Cannot use this network.
**Related Spec:** 3GPP TS 24.501 Section 9.11.3.2

---

## S1AP Cause Codes (4G RAN-Core Interface)

### Cause Code 0: Unspecified
**Description:** Radio network layer cause unspecified.
**Troubleshooting:** Check detailed S1AP logs. Review eNodeB and MME traces. Correlate with other events.
**Impact:** Generic failure indication.
**Related Spec:** 3GPP TS 36.413 Section 9.2.1.3

### Cause Code 12: No radio resources available in target cell
**Description:** Target cell has no capacity.
**Troubleshooting:** No radio resources - check eNodeB PRB utilization and admission control. Verify cell capacity. Review load balancing.
**Impact:** Handover fails.
**Related Spec:** 3GPP TS 36.413 Section 9.2.1.3

### Cause Code 13: Unknown MME UE S1AP ID
**Description:** MME doesn't recognize UE context.
**Troubleshooting:** Check UE context synchronization. Verify S1AP signaling. Review MME logs.
**Impact:** S1AP procedure fails.
**Related Spec:** 3GPP TS 36.413 Section 9.2.1.3

### Cause Code 14: Unknown eNB UE S1AP ID
**Description:** eNodeB doesn't recognize UE context.
**Troubleshooting:** Check eNodeB UE context. Verify S1AP messaging. Review context release.
**Impact:** S1AP procedure fails.
**Related Spec:** 3GPP TS 36.413 Section 9.2.1.3

### Cause Code 20: User inactivity
**Description:** UE inactive, context released.
**Troubleshooting:** Check inactivity timers. Verify UE activity. Review RRC idle transition.
**Impact:** Context cleanup, UE must re-establish.
**Related Spec:** 3GPP TS 36.413 Section 9.2.1.3

### Cause Code 21: Radio connection with UE lost
**Description:** Radio link failure detected.
**Troubleshooting:** Radio connection lost - check RRC connection stability, UE signal strength. Verify RSRP/RSRQ. Review interference. Check UE mobility.
**Impact:** Connection dropped.
**Related Spec:** 3GPP TS 36.413 Section 9.2.1.3

### Cause Code 22: Load balancing TAU required
**Description:** TAU needed for load distribution.
**Troubleshooting:** Check MME load. Verify load balancing algorithm. Review TAU procedures.
**Impact:** UE must perform TAU.
**Related Spec:** 3GPP TS 36.413 Section 9.2.1.3

### Cause Code 23: CS fallback triggered
**Description:** Circuit-switched fallback initiated.
**Troubleshooting:** Check CSFB configuration. Verify MSC connectivity. Review SGs interface.
**Impact:** UE moves to 2G/3G for voice.
**Related Spec:** 3GPP TS 36.413 Section 9.2.1.3

---

## NGAP Cause Codes (5G RAN-Core Interface)

### Cause Code 0: Unspecified
**Description:** Generic NGAP failure.
**Troubleshooting:** Check detailed NGAP traces. Review gNB and AMF logs. Correlate events.
**Impact:** Generic failure.
**Related Spec:** 3GPP TS 38.413 Section 9.3.1.2

### Cause Code 12: No radio resources available in target cell
**Description:** Target cell capacity exhausted.
**Troubleshooting:** Check gNB resource utilization. Verify admission control. Review capacity planning.
**Impact:** Handover rejected.
**Related Spec:** 3GPP TS 38.413 Section 9.3.1.2

### Cause Code 19: User inactivity
**Description:** UE inactive, releasing context.
**Troubleshooting:** Check inactivity timers. Verify UE state. Review RRC idle procedures.
**Impact:** Context released.
**Related Spec:** 3GPP TS 38.413 Section 9.3.1.2

### Cause Code 20: Radio connection with UE lost
**Description:** Radio link failure in 5G.
**Troubleshooting:** Radio connection lost - check gNB logs, UE RSRP/SINR values. Verify beam management. Review interference. Check UE mobility.
**Impact:** Connection lost.
**Related Spec:** 3GPP TS 38.413 Section 9.3.1.2

### Cause Code 25: Unknown PDU session ID
**Description:** PDU session not recognized.
**Troubleshooting:** Check PDU session context. Verify SMF signaling. Review session establishment.
**Impact:** PDU session procedure fails.
**Related Spec:** 3GPP TS 38.413 Section 9.3.1.2

---

## Diameter Cause Codes

### Result Code 2001: DIAMETER_SUCCESS
**Description:** Request successfully completed.
**Troubleshooting:** Normal operation, no action needed.
**Impact:** None.
**Related Spec:** RFC 6733

### Result Code 3002: DIAMETER_UNABLE_TO_DELIVER
**Description:** Message could not be delivered.
**Troubleshooting:** Check routing tables. Verify peer connectivity. Review realm configuration.
**Impact:** Request fails.
**Related Spec:** RFC 6733

### Result Code 3004: DIAMETER_TOO_BUSY
**Description:** Diameter node overloaded.
**Troubleshooting:** Check HSS/PCRF load. Verify capacity. Review traffic patterns.
**Impact:** Request rejected.
**Related Spec:** RFC 6733

### Result Code 5001: DIAMETER_AVP_UNSUPPORTED
**Description:** AVP not supported.
**Troubleshooting:** Check AVP compatibility. Verify protocol version. Review message format.
**Impact:** Request rejected.
**Related Spec:** RFC 6733

### Result Code 5003: DIAMETER_AUTHORIZATION_REJECTED
**Description:** Authorization failed.
**Troubleshooting:** Check subscription data. Verify authorization rules. Review policy configuration.
**Impact:** Service denied.
**Related Spec:** RFC 6733

### Result Code 5030: DIAMETER_USER_UNKNOWN
**Description:** User not found in HSS.
**Troubleshooting:** User unknown in HSS - verify IMSI provisioning. Check HSS database. Verify subscriber activation. Review billing system sync.
**Impact:** Authentication fails.
**Related Spec:** 3GPP TS 29.272

### Result Code 5420: DIAMETER_ERROR_UNKNOWN_EPS_SUBSCRIPTION
**Description:** EPS subscription data not found.
**Troubleshooting:** Unknown EPS subscription - check HSS subscription data. Verify APN configuration. Review subscription profile. Check provisioning.
**Impact:** Attach rejected.
**Related Spec:** 3GPP TS 29.272

### Result Code 5421: DIAMETER_ERROR_RAT_NOT_ALLOWED
**Description:** Radio Access Type not permitted.
**Troubleshooting:** Check RAT restrictions in subscription. Verify roaming agreements. Review access policies.
**Impact:** Access denied for this RAT.
**Related Spec:** 3GPP TS 29.272

### Result Code 5422: DIAMETER_ERROR_EQUIPMENT_UNKNOWN
**Description:** Equipment (IMEI) unknown.
**Troubleshooting:** Check EIR database. Verify IMEI provisioning. Review device certification.
**Impact:** Device not recognized.
**Related Spec:** 3GPP TS 29.272

### Result Code 5423: DIAMETER_ERROR_UNKNOWN_SERVING_NODE
**Description:** Serving node not recognized.
**Troubleshooting:** Check MME/SGSN registration. Verify node configuration in HSS. Review topology.
**Impact:** Location update fails.
**Related Spec:** 3GPP TS 29.272
