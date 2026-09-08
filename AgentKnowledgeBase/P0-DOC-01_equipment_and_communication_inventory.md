# P0-DOC-01 — Equipment and Planned Communication Inventory

**Project:** Vehicle Harness Functional Tester  
**Phase:** P0 — Requirements, documentation, and safety inputs  
**Task ID:** P0-DOC-01  
**Document status:** Draft — requires physical inspection and responsible-engineer review  
**Evidence basis:** Two user-supplied planning images, identified below  
**Purpose:** Provide the project agent with a structured inventory of the intended rack equipment, power arrangement, computer connections, and unresolved interfaces.

> This document records a proposed architecture shown in planning drawings. It is not an as-built drawing, electrical schematic, network configuration, command authorization, or permission to energize the system.

---

## 1. Source Evidence

### Source S1 — Rack layout

File label: `Photo 1.jpg`

The drawing shows the proposed rack layout and the following labels:

- Control & Safety Panel
- AC Power Strip
- B&K DAQ3120, described as a 60-channel DAQ with DM301 card, 3U, 120–240 VAC
- Tektronix TCPA400 Current Amplifier, 3U, 120–240 VAC
- Tektronix TBS2104B 100 MHz, four-channel oscilloscope, TekVPI, 5U, 120–240 VAC
- “B&K IT-E151 Rack Kit,” 3U, 120–240 VAC — manufacturer/label must be verified
- Two B&K 2831E DMMs, 3U, 120–240 VAC
- I-Tech/ITECH IT-M3906B-32-240 regenerative DC power supply, 0–32 VDC, 0–240 A, 6 kW, 1U, 208–480 VAC three-phase
- AC power-distribution area with circuit breaker/contactor, approximately 2U–3U

### Source S2 — Communication concept

File label: `Photo 2.jpg`

The drawing is titled **Vehicle Harness Functional Tester Communication** and shows:

- Main test PC with one LAN port and three labeled USB ports
- One Ethernet router/switch with a PC/uplink port and multiple LAN ports
- Two B&K 2831E DMMs, each with USB shown
- B&K DAQ3120 with LAN and USB shown
- Tektronix TBS2104B four-channel oscilloscope with LAN and USB shown
- A DC power supply labeled “REGGEAR DC POWER SUPPLY DUT 0–32 V 240 A,” with LAN and USB shown
- Planned LAN links from the router to the power supply, oscilloscope, and DAQ
- Planned LAN link between the main test PC and router
- Planned direct USB links from the main test PC to both DMMs
- Supply terminals labeled DC+, DC+ SENSE, DC− SENSE, and DC−
- DC high-current terminals connected to the four supply-output/sense conductors in the concept drawing
- A current sensor/probe or shunt indicated near the DC− high-current path

The arrows in S2 are treated as connection paths, not proof of one-way data flow.

---

## 2. Proposed System Summary

The proposed test station uses two communication groups:

1. **Direct USB instruments:** The two B&K 2831E DMMs connect individually to USB ports on the main test PC.
2. **Ethernet instruments:** The ITECH/“REGGEAR” DC supply, Tektronix TBS2104B oscilloscope, and B&K DAQ3120 connect to a dedicated Ethernet router/switch, which connects to the main test PC.

The Tektronix TCPA400 current amplifier is shown in the rack layout but not as a network or USB device in the communication drawing. It is therefore treated as part of the analog current-measurement chain, with its exact probe, output, oscilloscope channel, scaling, zero/degauss procedure, and power connection still to be documented.

The physical Control & Safety Panel and the AC breaker/contactor area are shown in the rack layout, but no PC, DAQ, or hardwired status/control connections are shown for them. Their interface must be defined before software safety states can be commissioned.

---

## 3. Equipment Inventory

| Equipment ID | Equipment shown | Manufacturer/model as shown | Qty. | Planned role | Power shown in S1 | Communication shown in S2 | Verification status |
|---|---|---|---:|---|---|---|---|
| EQ-001 | Main test PC | Model TBD | 1 | Runs the Python GUI, test engine, logging, database, and reports | TBD | 1 LAN; USB1, USB2, USB3 | Physical model, OS, ports, security policy, and ownership TBD |
| EQ-002 | Ethernet router/switch | Model TBD | 1 | Local instrument network aggregation | TBD | PC/uplink plus multiple LAN ports | Model, managed/unmanaged type, port count, addressing, and IT approval TBD |
| EQ-003 | Digital multimeter A | B&K Precision 2831E | 1 | Harness electrical measurement; exact assigned function TBD | 120–240 VAC; rack allocation included with two DMMs | Direct USB to PC USB1 in the concept | Serial number, firmware, calibration, USB mode/driver, assigned measurement role TBD |
| EQ-004 | Digital multimeter B | B&K Precision 2831E | 1 | Second harness electrical measurement; exact assigned function TBD | 120–240 VAC; rack allocation included with two DMMs | Direct USB to PC USB2 in the concept | Serial number, firmware, calibration, USB mode/driver, assigned measurement role TBD |
| EQ-005 | Data-acquisition unit | B&K Precision DAQ3120 | 1 | Multi-channel harness measurement/switching according to installed modules and fixture design | 120–240 VAC; 3U shown | LAN to router planned; USB port also shown but not selected | Serial number, firmware, exact modules, module slots, terminal blocks, channel map, calibration TBD |
| EQ-006 | DAQ module | DM301 card, as labeled | At least 1 shown | Provides DAQ measurement capability; exact channel/function allocation TBD | Installed in DAQ3120 | Internal to EQ-005 | Exact model suffix, quantity, slot, channel capabilities, and wiring must be verified |
| EQ-007 | Oscilloscope | Tektronix TBS2104B, 100 MHz, 4 channel, TekVPI | 1 | Transient/waveform acquisition and current-probe measurement | 120–240 VAC; 5U shown | LAN to router planned; USB also available/shown but not selected | Serial number, firmware, calibration, IP setup, channel allocation, probe scaling TBD |
| EQ-008 | Current-probe amplifier | Tektronix TCPA400 Current Amplifier | 1 | Conditions current-probe signal for oscilloscope measurement | 120–240 VAC; 3U shown | No digital connection shown | Exact compatible current probe, output-to-scope channel, range, scaling, bandwidth, zero/degauss, calibration TBD |
| EQ-009 | DC power supply | I-Tech/ITECH IT-M3906B-32-240 in S1; “REGGEAR” 0–32 V, 240 A in S2 | 1 | Controlled DUT DC source; regenerative capability stated in S1 | 208–480 VAC three-phase; 1U; 0–32 VDC, 0–240 A, 6 kW shown | LAN to router planned; USB also shown but not selected | **Naming/model discrepancy to resolve.** Verify nameplate, exact manufacturer/model, serial, firmware, ratings, manual, remote interface, calibration, and facility feed |
| EQ-010 | Rack kit | “B&K IT-E151 Rack Kit” as labeled | 1 | Mechanical/rack mounting; functional purpose TBD | 120–240 VAC; 3U shown | None shown | Manufacturer and model may be mislabeled; verify physical item and whether it is powered equipment |
| EQ-011 | Control & Safety Panel | Model/design TBD | 1 | Physical power control, indication, E-stop, and safety functions | Panel shown above AC strip | No software interface shown | Electrical schematic, safety functions, E-stop channels, interlocks, feedback, reset behavior, and standards review TBD |
| EQ-012 | AC power strip | Model/rating TBD | 1 | AC distribution for approved rack instruments | Located below safety panel | None | Input rating, outlets, branch protection, switch behavior, and load calculation TBD |
| EQ-013 | AC distribution/breaker/contactor assembly | Custom or model TBD | 1 | Facility-power isolation and controlled AC distribution | 2U–3U shown | No software interface shown | Breaker, contactor, coil control, auxiliary feedback, SCCR, branch protection, wiring, grounding, and drawings TBD |
| EQ-014 | Current sensor/probe or shunt | Model TBD | 1 or more | Measures DUT current on high-current path | Not specified | Analog measurement path not completely shown | Determine whether this is the TCPA400-compatible probe, a separate shunt, or both; document ratings and connections |
| EQ-015 | DC high-current terminal assembly | Model/design TBD | 1 | Brings supply output/sense connections to fixture/DUT interface | DC output side | DC+, DC−, and sense connections shown | Connector/terminal ratings, polarity, guarding, fuse/protection, remote-sense connection point, and fixture interface TBD |

---

## 4. Planned Communication Matrix

| Link ID | Endpoint A | Endpoint B | Planned medium | Intended use | Status from drawings | Required confirmation |
|---|---|---|---|---|---|---|
| COM-001 | Main test PC LAN | Ethernet router/switch PC/uplink port | Ethernet | PC access to LAN instruments | Explicitly shown in S2 | Cable type/category, port number, IP plan, subnet, isolation, firewall, IT ownership |
| COM-002 | Router LAN port TBD | DC power supply LAN | Ethernet | Remote status/configuration and eventually approved output control | Explicitly shown in S2 | Exact supply identity, port, protocol, IP, command manual, timeout, remote/local behavior |
| COM-003 | Router LAN port TBD | Tektronix TBS2104B LAN | Ethernet | Remote configuration, measurements, and waveform transfer | Explicitly shown in S2 | Port, IP, protocol/VISA resource, firmware, timeouts, transfer format |
| COM-004 | Router LAN port TBD | B&K DAQ3120 LAN | Ethernet | Remote measurement/channel operation | Explicitly shown in S2 | Port, IP, protocol/VISA resource, module/channel map, timeouts |
| COM-005 | Main test PC USB1 | B&K 2831E DMM A USB | USB | Direct DMM communication | Explicitly shown in S2 | Physical USB port, cable, driver, USBTMC vs virtual COM mode, VISA/COM resource, serial number mapping |
| COM-006 | Main test PC USB2 | B&K 2831E DMM B USB | USB | Direct second-DMM communication | Explicitly shown in S2 | Physical USB port, cable, driver, USBTMC vs virtual COM mode, VISA/COM resource, serial number mapping |
| COM-007 | Main test PC USB3 | Unassigned | USB | Spare/future connection | Port shown, no endpoint shown | Reserve or assign; document allowed use |
| COM-008 | Control & Safety Panel | PC, DAQ, or hardwired control system | TBD | E-stop/interlock/contactor/output-permit status and any reset request | **Not shown** | Safety architecture and schematic required; software may monitor but must not replace safety circuit |
| COM-009 | Current sensor/probe/shunt | TCPA400 and/or oscilloscope/DAQ | Analog, exact chain TBD | DUT current measurement | Only sensor location is suggested | Exact sensor, conductor, polarity, amplifier connection, scope channel, scaling, isolation, calibration |

### Planned logical topology

```text
                               MAIN TEST PC
                         ┌──────────┴──────────┐
                         │                     │
                       Ethernet              USB
                         │               ┌─────┴─────┐
                  Ethernet router        │           │
                 ┌───────┼───────┐    DMM A       DMM B
                 │       │       │    2831E       2831E
              DC PSU   Scope    DAQ
              IT-M...  TBS2104B DAQ3120

Analog/current-measurement chain, exact implementation TBD:

DC high-current conductor → current probe and/or shunt → TCPA400 and/or
measurement input → oscilloscope/DAQ → software reading

Safety chain, exact implementation TBD:

E-stop/interlocks/protection → safety-rated hardwired control → contactor/output
inhibit, independent of PC; status feedback to software is not yet defined
```

---

## 5. Rack and Power Arrangement Shown

### Proposed rack order from top to bottom

1. Control & Safety Panel
2. AC Power Strip
3. B&K DAQ3120 and Tektronix TCPA400 current amplifier in the upper equipment area
4. Tektronix TBS2104B oscilloscope
5. IT-E151 rack kit area and two B&K 2831E DMMs
6. ITECH IT-M3906B-32-240 regenerative DC power supply
7. AC distribution area containing circuit breaker/contactor

This is a conceptual arrangement. Final rack placement must consider manufacturer airflow/clearance requirements, weight/support, service access, high-current conductor routing, separation of AC/DC/signal wiring, electromagnetic interference, bend radius, touch protection, emergency access, and facility installation requirements.

### Power categories recorded from S1

| Power group | Equipment | Rating shown | Status |
|---|---|---|---|
| Single-phase rack AC | DAQ3120 | 120–240 VAC | Verify nameplate and branch load |
| Single-phase rack AC | TCPA400 amplifier | 120–240 VAC | Verify nameplate and branch load |
| Single-phase rack AC | TBS2104B oscilloscope | 120–240 VAC | Verify nameplate and branch load |
| Single-phase rack AC | Two 2831E DMMs | 120–240 VAC | Verify each nameplate and branch load |
| Unclear/potential labeling issue | “IT-E151 Rack Kit” | 120–240 VAC shown | Verify whether this is powered equipment and correct manufacturer/model |
| Three-phase facility AC | IT-M3906B-32-240 supply | 208–480 VAC three-phase | Facility electrical design and exact nameplate/manual verification required |
| DC high-current output | DUT circuit | 0–32 VDC, 0–240 A, up to 6 kW shown | These are equipment capability labels, **not approved test settings** |

No conductor sizes, connector ratings, fuses, breaker values, contactor ratings, short-circuit current rating, protective earth plan, remote-inhibit circuit, discharge time, or approved test limits are established by the photos.

---

## 6. DC Output and Current-Measurement Concept

S2 shows four supply-related terminals/conductors:

- `DC+`
- `DC+ SENSE`
- `DC− SENSE`
- `DC−`

All four are drawn toward a block labeled **DC POWER HI CURR TERMINALS**. A label for **CURR SENSOR PROBE OR SHUNT** is drawn near the negative-current path.

The following must remain unresolved until a reviewed electrical schematic is supplied:

- Whether remote sense is connected at the supply terminals, high-current terminal block, fixture, or DUT
- Whether the sense leads are fused/protected and how open-sense conditions are handled
- Whether the current measurement uses a clamp/probe, an inline shunt, the supply’s internal measurement, or multiple methods
- Which conductor the sensor surrounds or interrupts, and its polarity
- The relationship between the sensor and TCPA400 amplifier
- The TCPA400 output connection and oscilloscope channel
- Shunt resistance, rating, isolation, cooling, and Kelvin measurement details if a shunt is used
- High-current cable size, length, voltage drop, termination torque, guarding, polarity keying, fuse/protection, and discharge arrangement
- Contactor location and whether it isolates AC input, DC output, remote enable, or a combination

The application must not encode a current scaling factor, remote-sense behavior, current path, or safe output sequence until these items are approved.

---

## 7. Observed Discrepancies and Ambiguities

| Issue ID | Observation | Risk if assumed | Required resolution |
|---|---|---|---|
| OBS-001 | S1 identifies an ITECH IT-M3906B-32-240; S2 labels the device “REGGEAR DC POWER SUPPLY DUT 0–32V 240A.” | Wrong driver/manual/commands or wrong electrical assumptions | Photograph the installed nameplate and front/rear panels; record exact manufacturer, model, option codes, serial, and firmware |
| OBS-002 | “B&K IT-E151 Rack Kit” may be a manufacturer/model labeling error. | Incorrect inventory or power allocation | Inspect the item and record exact nameplate/part number and function |
| OBS-003 | DAQ3120 is described as 60 channel with a DM301 card, but installed modules/slots are not fully shown. | Unsupported channel count/routing or unsafe connection | Record every installed module, slot, terminal block, channel type, and fixture route |
| OBS-004 | Control & Safety Panel is shown without a schematic or status interface. | Software may report an assumed or false safety state | Provide safety schematic, truth table, device list, feedback points, and independent-operation verification plan |
| OBS-005 | Current probe/shunt is shown without a complete signal chain. | Incorrect scaling, bandwidth, polarity, isolation, or overrange behavior | Provide sensor/probe/shunt models, wiring, ratings, amplifier configuration, scope channel, and calibration method |
| OBS-006 | Router is called an Ethernet router; its exact function is unclear. | Addressing, security, or routing conflicts | Determine whether a simple isolated switch, router, or managed device is required and obtain IT approval |
| OBS-007 | USB modes are not specified for the DMMs. | Driver/resource mismatch and unstable device mapping | Verify USBTMC versus USB virtual COM, drivers, serial parameters if applicable, and map by serial number |
| OBS-008 | USB ports on LAN instruments are shown but not selected. | Accidental dual control or ambiguous resource ownership | Declare one production transport per instrument and document fallback/maintenance use |
| OBS-009 | No fixture, harness connectors, relay/matrix routing, or loads are shown. | Requested automatic tests may be physically impossible or unsafe | Provide fixture schematic, connector/pin map, switching matrix, loads, protection, and coverage matrix |
| OBS-010 | Capability ratings are visible, but approved operating/test limits are absent. | Software could apply unsafe values within the instrument’s capability | Obtain engineer-approved station ceilings and per-recipe limits; never infer them from the nameplate maximum |

---

## 8. Required Information to Complete P0-DOC-01

### Equipment identification

- [ ] Photograph each instrument’s front, rear, and nameplate
- [ ] Record manufacturer, exact model, option codes, serial number, and firmware
- [ ] Record calibration date/due date and certificate location
- [ ] Record rack U position and required ventilation/service clearance
- [ ] Verify the IT-E151 label and purpose
- [ ] Resolve ITECH versus “REGGEAR” supply identity

### DAQ and fixture

- [ ] Record all DAQ modules, slots, terminal blocks, and capabilities
- [ ] Supply the fixture electrical schematic and connector/pin map
- [ ] Supply the relay/multiplexer/matrix route table and forbidden combinations
- [ ] Identify which measurements each DMM performs
- [ ] Identify how the DAQ, DMMs, and fixture connect to one another
- [ ] Document de-energized verification before resistance/continuity measurement

### Communications

- [ ] Record Ethernet device make/model and whether it is a router or switch
- [ ] Obtain IT/security approval and define the isolated-network policy
- [ ] Assign and record approved static/reserved IP addresses and physical port numbers
- [ ] Record VISA resource strings only after read-only discovery
- [ ] Record USB mode, driver, cable, PC port, and serial-number mapping for each DMM
- [ ] Define ownership rules so only one application/session controls an instrument
- [ ] Record connection/response timeouts after bench characterization

### Safety and power

- [ ] Provide the control/safety-panel and AC-distribution schematics
- [ ] Define E-stop, interlock, contactor, breaker, fuse, remote-inhibit, and reset behavior
- [ ] Identify software-visible safety feedback and its fail-safe states
- [ ] Document physical proof that hazardous energy is removed without the PC
- [ ] Complete AC load calculation, branch protection, grounding, and facility review
- [ ] Define approved voltage/current/power/energy ceilings and discharge time
- [ ] Define high-current conductor, connector, fuse, guarding, torque, and polarity controls
- [ ] Define remote-sense wiring and fault handling
- [ ] Define current sensor/probe/shunt chain, scaling, range, direction, isolation, and calibration

### Documentation

- [ ] Obtain exact user and programming manuals for every model/firmware
- [ ] Add document names, revisions, and controlled storage locations
- [ ] Start `command_register.md`; leave commands unimplemented until reviewed
- [ ] Obtain responsible-engineer review and list open TBD owners/dates

---

## 9. Software Configuration Placeholders

The agent may use the following identifiers in example configuration, but it must not invent addresses or commands:

```yaml
station:
  name: Vehicle Harness Functional Tester
  mode_default: SIMULATION
  real_mode_enabled: false

instruments:
  dmm_a:
    model_expected: BK_2831E
    transport_planned: USB
    resource: TBD
    required: TBD
  dmm_b:
    model_expected: BK_2831E
    transport_planned: USB
    resource: TBD
    required: TBD
  daq:
    model_expected: BK_DAQ3120
    transport_planned: LAN
    resource: TBD
    installed_modules: TBD
    required: TBD
  oscilloscope:
    model_expected: TEKTRONIX_TBS2104B
    transport_planned: LAN
    resource: TBD
    required: TBD
  power_supply:
    model_expected: ITECH_IT_M3906B_32_240_PENDING_PHYSICAL_VERIFICATION
    transport_planned: LAN
    resource: TBD
    real_output_control_enabled: false
    approved_voltage_ceiling_v: TBD
    approved_current_ceiling_a: TBD
    approved_power_ceiling_w: TBD

safety:
  physical_estop_independent: REQUIRED_NOT_YET_VERIFIED
  interlock_feedback_interface: TBD
  contactor_feedback_interface: TBD
  output_off_verification_interface: TBD
```

These are documentation placeholders, not final runtime settings.

---

## 10. P0-DOC-01 Acceptance Criteria

### Current gate assessment

**Status: INCONCLUSIVE / OPEN**

The source images are sufficient to create a preliminary equipment and communication inventory. They are not sufficient to close the task as a verified as-built record.

P0-DOC-01 can be marked **PASS** only when:

1. Every equipment identity is verified from its physical label/nameplate.
2. The ITECH/REGGEAR and IT-E151 discrepancies are resolved.
3. All installed DAQ modules and their slots are recorded.
4. The planned USB/LAN link for each instrument is confirmed and assigned.
5. The safety panel, contactor, interlock, E-stop, and feedback interfaces are documented from reviewed schematics.
6. The current measurement chain and DC output/sense wiring are documented.
7. The fixture, switching, protection, and harness interface are identified or explicitly assigned to a separate tracked document with an owner.
8. Responsible engineering and applicable IT/facilities/safety reviewers have reviewed the inventory.
9. Every remaining TBD has an owner and target date.

No real hardware command, switching action, or power-output action is authorized by completion of this documentation task.

---

## 11. Instructions for the Project Agent

Use this document only as a preliminary Phase 0 source.

- Preserve the distinction between **shown in the planning images**, **physically verified**, **engineer approved**, and **software validated**.
- Do not convert a shown maximum capability into an operating limit.
- Do not generate SCPI/VISA/serial commands from these images.
- Do not assume the supply model until OBS-001 is resolved.
- Do not assume that the DAQ provides switching routes not established by its installed modules and the fixture schematic.
- Do not claim the TCPA400, current probe/shunt, safety panel, or contactor interfaces are complete.
- Keep Real mode and real output control disabled.
- Work only on completing P0-DOC-01 evidence; do not advance to implementation.

### Mandatory phase-end response

The agent must end its next response with:

```text
CURRENT GATE: INCONCLUSIVE

DO THIS NEXT:
1. Photograph the front, rear, and nameplate of the DC power supply.
2. Photograph/nameplate the item labeled IT-E151.
3. Record every DAQ module and slot.
4. Obtain the safety-panel/contactor schematic and fixture I/O map.
5. Complete the equipment identification fields and communication assignments.

SEND BACK:
- The nameplate text/photos for every instrument, especially the supply and IT-E151
- Instrument serial numbers and firmware versions, redacted if company policy requires
- DAQ module/slot list
- Router/switch model and proposed port/IP table, with sensitive details redacted
- Safety-panel and AC-distribution schematic review status
- Fixture/pin/relay map status
- Current sensor/probe/shunt model and signal-chain drawing
- Remaining TBD list with an owner and target date for each item
```

The agent must not mark P0-DOC-01 complete or start P0-DOC-02 until the acceptance criteria above are satisfied.
