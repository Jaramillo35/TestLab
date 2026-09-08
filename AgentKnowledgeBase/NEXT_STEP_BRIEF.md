# Next-Step Brief for the Coding Agent

**Project:** Vehicle Harness Functional Tester
**Date:** 2026-09-08
**Prepared from:** the six manufacturer PDFs in this repository, extracted into `P0-DOC-02_instrument_datasheet_extract.md`, `command_register.md` and `instrument_profiles.yaml`
**Audience:** the coding agent (VS Code Copilot / Claude Code) that will write the Python application, and the coordinator agent that reviews its evidence

---

## 1. Where the project actually stands

`P0-DOC-01` closed with **CURRENT GATE: INCONCLUSIVE** and instructed the agent to gather Phase-0 evidence and not advance to implementation.

The datasheet extraction changes what is *knowable*, not what is *approved*. Specifically:

**Now established from manufacturer documents:**
- The complete SCPI command set, serial parameters and protocol quirks of the **B&K 2831E DMMs** — the only instrument in the rack with a programming manual on hand.
- Every instrument's transport options, capability ceilings, protection ratings and physical/power requirements.
- The identity and full specification of the current-measurement chain, including two hardware items that are probably missing.
- Seven new findings (F-DAQ-01…03, F-TCPA-01/02, F-PSU-01/02) that change the fixture design, the current-measurement software, and the facility electrical review.

**Still blocked, unchanged:**
- No programming manual for the **DAQ3120**, **TBS2104B** or **IT-M3906B**. Their command registers are empty and must stay empty.
- No fixture schematic, pin map, or relay route table.
- No safety-panel schematic; COM-008 is fully open.
- No engineer-approved operating limits.

**Conclusion: Phase 0 is not closed, but Phase-1 simulation work is no longer blocked on documentation.** There is now enough to build the application skeleton, the instrument abstraction layer, the configuration loader and a fully-simulated 2831E driver — none of which touches hardware.

---

## 2. What the coding agent should build next

**Scope: Phase 1 — application skeleton in SIMULATION mode. No real I/O of any kind.**

### 2.1 In scope

1. **Project skeleton** — PySide6 desktop app that opens in `SIMULATION` mode and `Disconnected` state, closes cleanly, logs startup and shutdown.
2. **Configuration loader** — parse `instrument_profiles.yaml` into typed dataclasses. Must:
   - treat `TBD` as a first-class value meaning *not available in Real mode*, never as a default or a zero;
   - refuse to start in Real mode if any `approved_*` limit needed by the selected recipe is `TBD`;
   - expose capability ceilings for input validation.
3. **Instrument abstraction layer** — a `Instrument` protocol plus a `SimulatedInstrument` base. Four concrete profiles: `dmm_a`, `dmm_b`, `daq`, `oscilloscope`, `power_supply`.
4. **2831E driver, simulation-only** — implements the documented sequence from `command_register.md` §2.12 against a **simulated transport**. The command strings are real and cited; the transport is fake. Model the documented quirks explicitly so the real driver is a transport swap, not a rewrite:
   - per-character echo handshake,
   - one query per command line,
   - `:FETCh?` returns the *same* reading until a new one is triggered (staleness hazard),
   - `SD.DDDDDDESDDD<NL>` response parsing,
   - `*RST` latency.
5. **Blocked-instrument stubs** — `daq`, `oscilloscope`, `power_supply` drivers that raise a typed `CommandNotAuthorized` error naming the missing manual for **every** operation. They must be impossible to accidentally use.
6. **Current-scaling module** — `I_amps = V_volts × amps_per_volt`, with `amps_per_volt` read from config, never hard-coded, and recorded into every run record.
7. **Safety-state model** — `SafetyState` with fail-safe defaults: unknown = unsafe. Output OFF asserted on normal completion, abort, timeout, comms loss, interlock open, exception, and app close.
8. **Tests** — pytest, nominal / boundary / failure for each of the above. No real hardware, no VISA, no serial, no sockets.

### 2.2 Explicitly out of scope

- Any real transport. Simulation must never open VISA, serial, sockets or instrument resources.
- Any DAQ, scope, or power-supply command string.
- Any relay route or switching logic — no fixture schematic exists.
- Any test recipe with real limits — no approved limits exist.
- Web servers, microservices, cloud databases, ORMs. Stack is PySide6, PyVISA (later), pyserial (later), sqlite3, JSON, ReportLab, logging, pytest, PyInstaller.

### 2.3 Acceptance gate for Phase 1

1. App opens in `SIMULATION` + `Disconnected`, closes cleanly; startup/shutdown log captured.
2. `instrument_profiles.yaml` loads; a `TBD` approved limit blocks Real mode with a clear message.
3. Attempting any DAQ / scope / PSU operation raises `CommandNotAuthorized` naming the missing manual.
4. The 2831E simulated read sequence returns a parsed float via the documented `TRIGger:SOURce BUS` → `*TRG` → `:FETCh?` path.
5. A test proves `:FETCh?` staleness is detected rather than silently accepted.
6. A test proves the current scale factor comes from config and is written into the run record.
7. A test proves output-OFF is asserted on every abnormal exit path.
8. Full pytest output captured; no test skipped or weakened to pass.

---

## 3. Ready-to-paste prompt for the coding agent

```text
CONTEXT
Project: Vehicle Harness Functional Tester. Phase 1 — application skeleton,
SIMULATION mode only. Read these files in AgentKnowledgeBase/ first and treat
them as authoritative: P0-DOC-01_equipment_and_communication_inventory.md,
P0-DOC-02_instrument_datasheet_extract.md, command_register.md,
instrument_profiles.yaml.

TASK
Create the application skeleton and instrument abstraction layer. The app must
open in SIMULATION mode and Disconnected state, load instrument_profiles.yaml
into typed configuration objects, and close cleanly.

FILES YOU MAY CREATE OR CHANGE
  src/harness_tester/__init__.py
  src/harness_tester/config.py          # YAML -> typed dataclasses
  src/harness_tester/safety.py          # SafetyState, fail-safe defaults
  src/harness_tester/scaling.py         # current scale factor from config
  src/harness_tester/instruments/base.py
  src/harness_tester/instruments/simulated.py
  src/harness_tester/instruments/bk2831e.py
  src/harness_tester/instruments/blocked.py
  src/harness_tester/ui/main_window.py
  src/harness_tester/app.py
  tests/...
  pyproject.toml
Do not modify any file in AgentKnowledgeBase/ and do not add files outside
this list.

HARD CONSTRAINTS
- SIMULATION mode must never open VISA, serial, sockets, or any real
  instrument resource. No unit test may touch real hardware.
- Do NOT write, guess, adapt, or autocomplete any command string for the
  DAQ3120, TBS2104B, or IT-M3906B. Their drivers raise CommandNotAuthorized
  naming the missing manual, for every operation. There are no exceptions and
  no "probably standard SCPI" fallbacks.
- The only real command strings allowed are the 2831E entries in
  command_register.md, quoted exactly, each with its CR-2831E-nnn id in a
  comment. Use only the documented sequence in section 2.12. Do not use
  :READ? or :MEASure? — they are referenced but never defined in the manual.
- Treat YAML `TBD` as "not available in Real mode", never as a default,
  never as zero, never as the capability ceiling.
- real_mode_enabled and real_output_control_enabled stay false.
- Output OFF must be asserted on normal completion, abort, timeout,
  communication loss, interlock open, exception, and application close.
- Never weaken or skip a safety assertion or test to get a pass.

DESIGN REQUIREMENTS
- Type hints throughout. Small, readable components. Explicit exception types.
- Structured logging with timestamps.
- Model these documented 2831E protocol behaviours in the simulated transport
  so the real driver is a transport swap rather than a rewrite:
    * per-character echo handshake (wait for echo before next character)
    * one query per command line
    * :FETCh? returns the SAME reading until a new one is triggered
    * response format SD.DDDDDDESDDD<NL>
    * *RST takes a long time; do not pipeline behind it
- Current conversion: I_amps = V_volts * amps_per_volt, amps_per_volt read
  from config (1000 for the TCP404XL 1 A/mV range). Never hard-code it.
  Record the amplifier range setting in every run record.

TESTS REQUIRED (pytest, nominal / boundary / failure)
- config loads; TBD approved limit blocks Real mode with a clear message
- every blocked-instrument operation raises CommandNotAuthorized
- 2831E simulated read returns a parsed float via BUS trigger -> *TRG -> :FETCh?
- :FETCh? staleness is detected, not silently accepted
- scale factor comes from config and lands in the run record
- output OFF asserted on each abnormal exit path

AFTERWARDS, RUN AND REPORT
  python -m pytest -v
  python -m harness_tester.app     (screenshot of the opening window)
Return: full pytest output, the startup and shutdown log, the screenshot, and
a list of any assumption you had to make. Do not proceed to Phase 2.
```

---

## 4. Findings the coding agent must not "optimize away"

| Finding | Why it constrains the code |
|---|---|
| **F-TCPA-01** — no automatic probe scaling on this scope | The app converts volts→amps itself. The scale factor is reviewed config, not a constant, and must be stored per run. |
| **F-TCPA-02** — no 50 Ω input on the TBS2104B | An external feedthrough is required. The amplifier's termination-error flag is a front-panel LED the software cannot read. The app must not claim a verified current reading. |
| **F-DAQ-02** — DAQ max 1–2 A vs 240 A DUT | Never route DUT current through a DAQ current channel. Enforce in the route validator when one is eventually written. |
| **F-DAQ-03** — 4-wire pairs bank 1 with bank 2 | Channel budgeting for the pin map must use 4-wire counts, roughly halving usable points. |
| **F-PSU-01** — bidirectional source *and* load, front-panel mode switch | The app must read and display Source/Load mode and must never assume Source. |
| **2831E `:FETCh?` staleness** | A poll loop can return an old reading forever. A repeated identical value is not evidence of a fresh measurement. |
| **2831E has no error-status query** | Instrument error state is not machine-readable. Rely on response parsing and timeouts; do not fabricate a health check. |
| **2831E has no SCPI limit subsystem** | Pass/fail is evaluated in the application from raw readings, never delegated to the meter. |
| **2831E low-Ω ranges specified only under REL** | A continuity recipe that skips the null is out of specification. |
| **DAQ 2-wire without null adds 2 Ω** | Decisive for milliohm harness continuity. Prefer 4-wire, or mandate the null. |

---

## 5. What must come from a human before Phase 2

Ordered by how much downstream work each unblocks:

1. **Programming manuals** — DAQ3120; Tektronix `077-1149-xx`; IT-M3906B user + programming manual **including the P-IO pinout**. Without these, three of four instruments stay permanently stubbed.
2. **Fixture schematic, connector/pin map, relay route table, forbidden combinations.** Without these there is no test to run.
3. **DAQ3120 installed module and slot list** — determines how many harness pins are reachable (finding F-DAQ-01).
4. **Safety-panel and AC-distribution schematics**, E-stop/interlock/contactor architecture and feedback points (COM-008).
5. **Engineer-approved operating ceilings** — voltage, current, power, discharge time. Not the instrument protection trips.
6. **Nameplate photographs** — all instruments, especially the supply (OBS-001) and the item labelled IT-E151 (OBS-002; look for `IT-E155A/B/C`).
7. **Current-chain confirmation** — is the probe a TCP404XL? Is the `011-0049-02` 50 Ω feedthrough fitted? Is the `TPA-BNC` adapter present? Which conductor, which polarity, which scope channel?
8. **Network decisions** — router vs switch, model, IP plan, IT approval, Wi-Fi disabled on the scope.
9. **One declared production transport per instrument**, in writing.

---

## 6. Phase-end status block

```text
CURRENT GATE: INCONCLUSIVE
  P0-DOC-01 remains open. P0-DOC-02 is PARTIAL: datasheet extraction is
  complete, physical verification and three programming manuals are not.
  Phase 1 simulation work is unblocked and may begin.

RESOLVED SINCE LAST REVIEW:
  OBS-007  2831E is USB Virtual COM (8N1, 9600 default, LF or CR) - not USBTMC.
  OBS-005  TCPA400's only compatible probe is the TCP404XL; scale 1 A/mV;
           manual scaling required; 50 ohm feedthrough and TPA-BNC required;
           amplifier status flags are not machine-readable.
  OBS-002  "IT-E151" is almost certainly the ITECH IT-E155A/B/C rack mount kit,
           an ITECH accessory, not a B&K item, and not powered equipment.
  OBS-010  All instrument capability ceilings are now documented (still not
           approved operating limits).

DO THIS NEXT:
  1. Obtain the three missing programming manuals: DAQ3120; Tektronix
     077-1149-xx; ITECH IT-M3906B user + programming manual with P-IO pinout.
  2. Photograph the front, rear and nameplate of the DC power supply and of the
     item labelled "IT-E151" (expect IT-E155A/B/C).
  3. Record every installed DAQ3120 module and its slot - resolve whether
     "60 channel" means three DM301 modules.
  4. Confirm the current chain: is the probe a TCP404XL? Is a 50 ohm
     feedthrough (011-0049-02) fitted? Is a TPA-BNC adapter present? Which
     conductor, which polarity, which scope channel?
  5. Obtain the safety-panel, contactor and AC-distribution schematics, and
     decide whether the supply's P-IO is part of the safety chain.
  6. Start Phase 1 simulation-mode implementation using the prompt in section 3.

SEND BACK:
  - The three programming manuals, with revision and date
  - Nameplate photographs and serial/firmware for every instrument
  - DAQ3120 module and slot list
  - Current-chain photographs: probe model, terminator, adapter, conductor,
     scope channel
  - Router/switch model and proposed port/IP table, sensitive details redacted
  - Safety-panel and AC-distribution schematic review status
  - Fixture / pin / relay map status
  - Engineer-approved voltage, current, power and discharge-time ceilings
  - For Phase 1: full pytest output, startup/shutdown log, opening-window
     screenshot, and the list of assumptions made
  - Updated TBD list with an owner and target date for each item
```

**No hardware command, switching action, or power-output action is authorized by any document in this repository.**
