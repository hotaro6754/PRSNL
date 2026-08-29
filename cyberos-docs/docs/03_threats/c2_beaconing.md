# Command & Control (C2) Beaconing

## What is C2 Beaconing?
Malware periodically "calls home" to an attacker-controlled server to request instructions. 

## Detection Implementation
* **Detector**: `beacon_stateful_v2`
* **Features**: IAT Mean, IAT Standard Deviation, IAT Coefficient of Variation (CV).
* **Logic**: If a connection to the same destination occurs over multiple windows with an IAT CV near zero, it is a rigid beacon. If it has high statistical periodicity, it is a jittered beacon.

## Validation
* **T5**: Rigid Beacon (Passed)
* **T6**: Jittered Beacon (Passed)