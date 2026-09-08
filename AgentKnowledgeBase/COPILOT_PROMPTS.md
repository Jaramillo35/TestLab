# GitHub Copilot — Phase 1 build sequence

**Date:** 2026-09-08
**Phase:** 1 — simulation-only application skeleton
**Audience:** whoever is driving GitHub Copilot Chat in VS Code

Five prompts, in order. Each is one commit's worth of work with its own acceptance check. Do not merge them into one request — the whole point of the sequence is that you review and run each step before the next.

---

## Before you start

### 1. Confirm Copilot is reading the repo rules

`.github/copilot-instructions.md` is in this repository. VS Code Copilot Chat picks it up automatically when the setting **`github.copilot.chat.codeGeneration.useInstructionFiles`** is enabled (it is on by default in current versions).

Verify it is actually loaded before writing any code. Ask Copilot Chat:

```text
What are the hard rules for this repository, and which two instruments are
BLOCKED from having any command written for them?
```

It must answer: never invent a hardware command; a capability is not a limit; simulation-first with output off; physical safety works without the PC; never weaken a test. And the blocked instruments are the **Tektronix TBS2104B** and the **ITECH IT-M3906B**.

**If it cannot answer that, stop and fix the setup.** Everything below assumes those rules are in force.

### 2. Attach context to every prompt

In Copilot Chat, reference the files explicitly so it is not guessing:

```text
#file:AgentKnowledgeBase/command_register.md
#file:AgentKnowledgeBase/instrument_profiles.yaml
#file:AgentKnowledgeBase/NEXT_STEP_BRIEF.md
```

For agent-style edits use **Copilot Edits** (multi-file) rather than inline completion — these steps each touch several files.

### 3. Working rhythm

For every step: read the diff before accepting → run the commands yourself → capture the real output → commit only when the step's acceptance check passes. Copilot proposes; you verify. A Copilot claim that something works is not evidence.

---

## Step 1 — Project scaffold and configuration loader

```text
Phase 1, step 1 of 5. Simulation only. Follow .github/copilot-instructions.md.

TASK
Create the project scaffold and a typed configuration loader that reads
AgentKnowledgeBase/instrument_profiles.yaml.

FILES YOU MAY CREATE OR CHANGE — nothing else
  pyproject.toml
  src/harness_tester/__init__.py
  src/harness_tester/config.py
  tests/test_config.py

REQUIREMENTS
- Parse instrument_profiles.yaml into frozen dataclasses. Do not use pydantic.
- Treat the string "TBD" as a first-class sentinel meaning "not available in
  Real mode". Model it as an explicit type, not as None and not as a default.
  Never coerce TBD to zero and never fall back to the capability ceiling.
- Expose capability ceilings for input validation, separately from
  approved_* limits.
- A helper that answers: "may this path run in Real mode?" — false whenever any
  approved_* limit it needs is TBD, with a message naming the missing limit.
- Type hints throughout, explicit exception types, structured logging.

TESTS (pytest) — nominal, boundary, failure
- the real instrument_profiles.yaml loads without error
- a TBD approved limit blocks Real mode and the message names the field
- a malformed YAML file raises a typed error, not a KeyError or AttributeError
- capability ceilings are exposed and are NOT the same objects as approved limits

AFTERWARDS RUN
  python -m pytest -v
Report the full output and any assumption you had to make.
```

**Acceptance:** tests pass; a `TBD` limit demonstrably blocks Real mode with a message that names the field.

---

## Step 2 — Instrument abstraction and blocked stubs

```text
Phase 1, step 2 of 5. Simulation only. Follow .github/copilot-instructions.md.

TASK
Define the instrument abstraction and the drivers for the two BLOCKED
instruments.

FILES YOU MAY CREATE OR CHANGE — nothing else
  src/harness_tester/instruments/__init__.py
  src/harness_tester/instruments/base.py
  src/harness_tester/instruments/blocked.py
  tests/test_blocked_instruments.py

REQUIREMENTS
- base.py: an Instrument Protocol (connect, disconnect, identify, close) plus a
  SimulatedInstrument base class. Simulation must never open VISA, serial or
  sockets — make that structurally impossible, not merely a convention.
- A typed CommandNotAuthorized exception carrying: instrument name, the
  operation attempted, and the exact manual that is missing.
- blocked.py: OscilloscopeDriver and PowerSupplyDriver. EVERY operation raises
  CommandNotAuthorized. They must be impossible to use accidentally — no
  partially working method, no pass-through, no TODO that returns a value.
- Do NOT write a single SCPI string for the TBS2104B or the IT-M3906B. The
  missing documents are the Tektronix TBS2000B Series Programmer Manual and
  the ITECH IT-M3900B Series Programming Guide.

TESTS
- every public method of both blocked drivers raises CommandNotAuthorized
- the exception message names the missing manual
- a test that fails if any blocked driver method ever returns normally
  (enumerate the methods by reflection so new ones are covered automatically)

AFTERWARDS RUN
  python -m pytest -v
```

**Acceptance:** the reflection test proves no blocked method can return a value — including methods added later.

---

## Step 3 — B&K 2831E simulated driver

```text
Phase 1, step 3 of 5. Simulation only. Follow .github/copilot-instructions.md.

TASK
Implement the B&K 2831E driver against a SIMULATED serial transport. The
command strings are real; the transport is fake.

FILES YOU MAY CREATE OR CHANGE — nothing else
  src/harness_tester/instruments/bk2831e.py
  src/harness_tester/transports/__init__.py
  src/harness_tester/transports/simulated_serial.py
  tests/test_bk2831e.py

COMMANDS
Use ONLY command_register.md section 2, quoted exactly, each with its
CR-2831E-nnn id in a comment. The only documented read sequence is section
2.12: TRIGger:SOURce BUS -> *TRG -> :FETCh?. Do NOT use :READ? or :MEASure? —
they are referenced but never defined in the manual.

MODEL THESE DOCUMENTED BEHAVIOURS in the simulated transport, so the real
driver later becomes a transport swap and not a rewrite
- per-character echo handshake: every byte written is echoed, and the driver
  must wait for the echo before sending the next byte
- one query per command line
- :FETCh? returns the SAME reading until a new measurement is triggered
- response format SD.DDDDDDESDDD<NL>
- *RST takes a long time; the driver must not pipeline behind it
- 8N1, 9600 default, terminator LF or CR from config

PORT MAPPING
Enumerate by USB VID 0x10C4 + PID 0xEA60 + serial number. Never hard-code a COM
port. If two devices report the SAME serial string, raise a clear typed error
naming both — do not pick one arbitrarily.

TESTS — nominal, boundary, failure
- the documented sequence returns a correctly parsed float
- :FETCh? staleness is DETECTED, not silently accepted
- a dropped echo produces a typed error, not a hang or a wrong value
- SD.DDDDDDESDDD parsing: positive, negative, exponent, and a malformed string
- duplicate CP210x serials raise the typed error naming both devices

AFTERWARDS RUN
  python -m pytest -v
```

**Acceptance:** the staleness test and the duplicate-serial test both pass. These are the two failure modes most likely to produce a silently wrong measurement later.

---

## Step 4 — DAQ3120 simulated driver and the route layer

```text
Phase 1, step 4 of 5. Simulation only. Follow .github/copilot-instructions.md.
This step contains the highest-risk logic in the project. Be conservative.

TASK
Implement the B&K DAQ3120 driver and its routing layer against a simulated
transport.

FILES YOU MAY CREATE OR CHANGE — nothing else
  src/harness_tester/instruments/daq3120.py
  src/harness_tester/instruments/routing.py
  src/harness_tester/transports/simulated_socket.py
  tests/test_daq3120.py
  tests/test_routing.py

COMMANDS
Use ONLY command_register.md section 3, quoted exactly, each with its
CR-DAQ-nnn id in a comment. Section 3.12 has the deterministic scan sequence.

ROUTING SAFETY — non-negotiable
- ROUTe:CLOSe:EXCLusive is the DEFAULT close (break-before-make).
- A bare ROUTe:CLOSe with more than one channel must be REFUSED unless an
  explicit reviewed-multi-point-intent object is passed in. A boolean flag is
  not sufficient — make the caller construct something deliberate.
- Always synchronize on ROUTe:DONE?. Never sleep().
- Open all channels on exit, including abort, timeout, exception and close.
- Channel ids are (@<slot><ch>): slot 1 -> 1xx, 2 -> 2xx, 3 -> 3xx.
  Support single, list, range and combined forms.

OTHER DOCUMENTED BEHAVIOURS TO MODEL
- INSTrument:DMM toggling forces a factory reset: the simulated state must
  actually be discarded, and the driver must REFUSE to toggle it mid-sequence.
- Reading memory holds 100000 readings and WRAPS, overwriting oldest.
- SYSTem:CTYPe? <slot> verifies the installed module against config at connect
  time and refuses to run on mismatch.
- SYSTem:ERRor? drained after every command batch.
- SYSTem:LFRequency? read, never assumed.
- FORMat:READing:CHANnel ON so readings carry their channel number.

TESTS — nominal, boundary, failure
- the section 3.12 sequence produces parsed readings tagged with channel ids
- default close emits ROUTe:CLOSe:EXCLusive
- a bare multi-channel ROUTe:CLOSe is refused without explicit intent
- ROUTe:DONE? is polled; assert sleep() is never called
- SYSTem:CTYPe? mismatch against config blocks the run
- toggling INSTrument:DMM mid-sequence is refused
- reading-memory wrap is handled without silently losing data
- channel-id parsing: single, list, range, combined, and an invalid id

NOTE
Use clearly fictitious channel numbers in tests. No channel list in this repo
is a real harness mapping — the fixture schematic does not exist yet (T-04).

AFTERWARDS RUN
  python -m pytest -v
```

**Acceptance:** the refusal tests pass — bare multi-channel close, `CTYPe?` mismatch, and mid-sequence `INSTrument:DMM` toggle are all rejected.

---

## Step 5 — Safety state, current scaling, and the application shell

```text
Phase 1, step 5 of 5. Simulation only. Follow .github/copilot-instructions.md.

TASK
Add the safety-state model and current scaling, then wire everything into a
PySide6 shell that opens in SIMULATION / Disconnected and closes cleanly.

FILES YOU MAY CREATE OR CHANGE — nothing else
  src/harness_tester/safety.py
  src/harness_tester/scaling.py
  src/harness_tester/ui/__init__.py
  src/harness_tester/ui/main_window.py
  src/harness_tester/app.py
  tests/test_safety.py
  tests/test_scaling.py

SAFETY
- SafetyState with fail-safe defaults: UNKNOWN is treated as UNSAFE.
- Output OFF asserted on: normal completion, abort, timeout, communication
  loss, interlock open, exception, application close.
- The model must be able to represent "I cannot observe this" distinctly from
  "this is safe". Never report a safe state the software cannot actually see.
  The TCPA400 amplifier's degauss / probe-open / overload / termination flags
  are front-panel LEDs and are NOT machine-readable — model them as
  unobservable, and surface that in the UI.

SCALING
- I_amps = V_volts * amps_per_volt, amps_per_volt read from config
  (1000 for the TCP404XL 1 A/mV range). Never hard-code it.
- The amplifier range setting must be written into every run record. A later
  range change must not be able to silently invalidate stored results.

UI SHELL
- Opens in SIMULATION mode, Disconnected state. Mode and connection state are
  visible at a glance. Closes cleanly with no orphaned threads.
- Log startup and shutdown with timestamps.

TESTS
- output OFF is asserted on EVERY abnormal exit path (parametrise them)
- UNKNOWN safety state is treated as unsafe
- unobservable amplifier flags never render as "safe" or "OK"
- scale factor comes from config and lands in the run record
- a changed scale factor is detectable in historical records

AFTERWARDS RUN
  python -m pytest -v
  python -m harness_tester.app
Capture a screenshot of the opening window and the startup/shutdown log.
```

**Acceptance:** all of `NEXT_STEP_BRIEF.md` §2.3 (items 1–11). App opens in SIMULATION/Disconnected, closes cleanly, full pytest output captured, screenshot taken.

---

## When Copilot goes wrong

It will occasionally suggest a SCPI command for the oscilloscope or the power supply, because those instruments are famous and their command sets are all over its training data. That is exactly the failure this repository is built to prevent.

Reject it and say:

```text
That instrument is BLOCKED. There is no manufacturer programming manual for it
in this repository. Per .github/copilot-instructions.md rule 1, raise
CommandNotAuthorized instead and name the missing manual. Do not suggest a
command for it again.
```

Other patterns worth watching for:

| Copilot does this | Why it is wrong |
|---|---|
| Defaults a `TBD` limit to `0` or to the capability ceiling | Rule 2. `TBD` means refuse, not zero and not maximum. |
| Adds `time.sleep()` after a route change | Synchronize on `ROUTe:DONE?`. |
| Simplifies the 2831E echo handshake away | It is a documented protocol requirement; removing it desynchronizes the link. |
| Uses `:READ?` on the 2831E | Referenced but never defined in that manual. |
| Adds `pydantic`, `asyncio`, FastAPI, an ORM | Not in the stack. Say no. |
| Marks a test `xfail`/`skip` to get green | Rule 5. Never. |
| Writes "this is safe" for an unobservable state | Rule 4. Unobservable is not safe. |

---

## After Phase 1

Do not start Phase 2. Return the evidence listed in `NEXT_STEP_BRIEF.md` §6 (`SEND BACK`) and get the gate assessed first.

Phase 2 needs the two missing manuals — the Tektronix TBS2000B Programmer Manual and the ITECH IT-M3900B Programming Guide and User Manual — plus the fixture schematic and the engineer-approved operating limits. URLs are in `P0-DOC-03` §5.
