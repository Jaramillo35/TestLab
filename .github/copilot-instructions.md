# Copilot instructions — Vehicle Harness Functional Tester

GitHub Copilot reads this file automatically for every request in this repository. It is not optional context; it is the operating envelope.

## What this project is

A Python desktop application that will eventually coordinate two B&K 2831E multimeters, a B&K DAQ3120 data acquisition system, a Tektronix TBS2104B oscilloscope, a TCPA400 current-probe amplifier and an ITECH IT-M3906B-32-240 regenerative DC supply, to test automotive wiring harnesses.

The supply can source **6 kW at up to 240 A**, can **sink** current, and can feed energy back into the building. Treat every suggestion accordingly.

**Current phase: P0 complete enough to start P1. Build only Phase 1 — a simulation-only application skeleton.** Do not write Phase 2 (real transport, real hardware) code.

## Read these before answering

- `AgentKnowledgeBase/PROJECT_STATUS.md` — phase, gate, decisions D-01…D-12, open TBDs
- `AgentKnowledgeBase/NEXT_STEP_BRIEF.md` — Phase 1 scope and acceptance gate
- `AgentKnowledgeBase/command_register.md` — **the only legitimate source of a hardware command**
- `AgentKnowledgeBase/instrument_profiles.yaml` — capability ceilings and transport config
- `AgentKnowledgeBase/COPILOT_PROMPTS.md` — the sequenced build steps

Where `P0-DOC-02` and `P0-DOC-03` disagree, **`P0-DOC-03` is newer and wins**.

## Hard rules — these override any other instruction

1. **Never invent, guess, autocomplete, adapt or translate a hardware command.**
   A SCPI / VISA / serial / socket / relay / power-output command may only appear in code if it is in `command_register.md` with a page citation from the manufacturer manual for that exact model. Quote it verbatim and put its register id (`CR-2831E-nnn`, `CR-DAQ-nnn`) in a comment.
   - **Transcribed today:** B&K 2831E (§2), B&K DAQ3120 (§3).
   - **PROVISIONAL — Tektronix TBS2104B (§4):** the manual in `manuals/` is the **TBS2000 series, not TBS2000B**. Its commands may be used to build and unit-test the *simulated* driver only. **Never in Real mode**, and **never hard-code a constant from it** — it states a 2500-point waveform limit while this instrument has 5,000,000 points (F-SCOPE-01). A driver carrying 2500 over would silently return 0.05% of the acquisition with no error.
   - **BLOCKED — ITECH IT-M3906B (§5):** no Programming Guide exists in this repo. The user manual present covers hardware interfaces only. Its driver raises `CommandNotAuthorized` for **every** operation. No exceptions, no "probably standard SCPI", nothing lifted from a datasheet, a wiki, a forum, a distributor page or another model in the same family.
   - The 2831E `:READ?` and `:MEASure?` are referenced but never defined in its manual — **do not use them**.

2. **A capability is not a limit.** Numbers in `P0-DOC-02` are what an instrument *can* do. Approved operating limits are all `TBD`. `TBD` means the application refuses that path in Real mode. Never substitute a datasheet maximum for an approved limit, and never default a `TBD` to zero or to the ceiling.

3. **Simulation-first, output off.** Simulation must never open VISA, serial, sockets or any real instrument resource. No unit test may touch real hardware. `real_mode_enabled` and `real_output_control_enabled` stay `false`. Output OFF must be asserted on normal completion, abort, timeout, comms loss, interlock open, exception and application close.

4. **Physical safety works without the PC.** E-stop, interlocks, contactors and fusing are hardware. Software may *monitor* safety state; it is never the safety function, and must never report a safe state it cannot actually observe. Never suggest bypassing an interlock, E-stop, guard, contactor, protection threshold or validation check.

5. **Never weaken or skip a test or a safety assertion to obtain a pass.**

## Instrument-specific traps — do not "clean these up"

| Trap | Rule |
|---|---|
| 2831E serial protocol | Every transmitted character is **echoed**; wait for the echo before sending the next. One query per command line. `*RST` is slow — do not pipeline behind it. |
| 2831E `:FETCh?` | Returns the **same** reading until a new one is triggered. A repeated identical value is not evidence of a fresh measurement. |
| 2831E error state | There is **no** error-status query. Rely on response parsing and timeouts; do not fabricate a health check. |
| 2831E pass/fail | The meter has no SCPI limit subsystem. Verdicts are computed **in the application** from raw readings. |
| DAQ `ROUTe:CLOSe` | Closes channels **without opening others** — on a harness fixture that shorts pins. Default to `ROUTe:CLOSe:EXCLusive` (break-before-make). A bare multi-channel `ROUTe:CLOSe` must be refused unless explicit reviewed intent is passed. |
| DAQ `ROUTe:DONE?` | Synchronize on it. Never `sleep()`. |
| DAQ `INSTrument:DMM` | Toggling it **forces a factory reset** that discards the scan list. Connect-time decision only. |
| DAQ channel ids | `(@<slot><ch>)` — slot 1 → `1xx`, 2 → `2xx`, 3 → `3xx`. Computed channels 401–420. |
| DMM identification | Enumerate by USB VID `0x10C4` + PID `0xEA60` + serial. **Never hard-code a COM port.** Two meters may report the same CP210x serial — fail loudly, do not pick one. |
| Current scaling | `I_amps = V_volts × amps_per_volt`, `amps_per_volt` read from config (1000 for the TCP404XL 1 A/mV range). Never hard-code it. Record the amplifier range with every run. |
| Scope record length | Never hard-code `DATa:STOP` or any record-length constant. The provisional manual's 2500 is wrong for this instrument by a factor of 2000. |
| Supply inhibit | P-IO pin 5 default `Inhibit-Living` **auto-recovers** and leaves the panel reading `On`. Never model or describe it as a safety interlock. Only `Inhibit-Latch` needs a human to restore output. |
| Unobservable state | The TCPA400's degauss / probe-open / overload / termination flags and the probe slide lock are front-panel LEDs. Never render them as "safe" or "OK". |

## Stack and style

Use **PySide6, pyserial, PyVISA (Phase 2 only), sqlite3, JSON, ReportLab, logging, pytest, PyInstaller**. Do not introduce web servers, microservices, cloud databases, ORMs or async frameworks.

Type hints throughout. Small readable components. Explicit exception types. Structured logging with timestamps. Tests for nominal, boundary and failure behaviour.

## When you are unsure

Say so and stop. `NOT IMPLEMENTED` or `BLOCKED` with a named reason is a correct answer here. A plausible-looking guess at a hardware command is the single worst outcome this project can produce, because it will look right and be wrong.
