# Command Register

**Project:** Vehicle Harness Functional Tester
**Document status:** Draft — **NOT reviewed, NOT approved for hardware execution**
**Created by:** P0 documentation extraction from manufacturer manuals held in this repository
**Governing rule:** `m365_copilot_agent_setup_for_harness_tester (1).md` §3 — *"Never invent, autocomplete, infer, or translate an SCPI, VISA, serial, socket, relay-switching, or power-output command. Accept a hardware command only when the user provides an exact excerpt from the programming manual for the exact model/firmware and the reviewed command register identifies the document, revision, page/section, syntax, response, units, prerequisites, and reviewer."*

---

## 0. How to read this register

Every row carries a **Review status**. Only `APPROVED` entries may ever be transmitted to real hardware, and only after Real mode is enabled by the responsible engineer.

| Status | Meaning |
|---|---|
| `TRANSCRIBED` | Syntax copied verbatim from a manufacturer manual in this repo, with page citation. **Not yet reviewed. Not yet bench-verified. Simulation use only.** |
| `BLOCKED` | No manufacturer programming manual is available for this instrument. **No command may be written, guessed, or adapted from a sibling model.** |
| `APPROVED` | Reviewed by a named engineer against the manual for the exact model *and firmware*, and bench-verified. **Currently: none.** |

**Firmware caveat.** Every `TRANSCRIBED` entry below is transcribed from a manual whose own example `*IDN?` response is `2831E Multimeter,Ver1.0.09.12.03`. If the installed unit reports a different firmware version, **every entry reverts to unverified** until re-checked against the matching manual revision.

**Current count: 0 APPROVED. 3 of 4 instruments fully BLOCKED.**

---

## 1. Instrument transport summary

| Instrument | Manual in repo? | Transport | Register status |
|---|---|---|---|
| B&K 2831E DMM ×2 | **Yes** — `bk_precision_2831e_manual.pdf` | USB Virtual COM (serial), 8N1, 9600 default, `<LF>` or `<CR>` | `TRANSCRIBED` |
| B&K DAQ3120 | **No** | LAN / USBTMC / USBVCP / micro-GPIB | `BLOCKED` |
| Tektronix TBS2104B | **No** (programmer manual is `077-1149-xx`) | LAN / USBTMC | `BLOCKED` |
| ITECH IT-M3906B-32-240 | **No** | LAN / USB / CAN / P-IO | `BLOCKED` |

---

## 2. B&K Precision 2831E — TRANSCRIBED

**Source document:** `bk_precision_2831e_manual.pdf` (SRC-02), Chapters 5–6.
**Model scope:** 2831E. The same manual also documents model 5491B — **5491B ranges and accuracies differ and must not be used for the 2831E.**
**Reviewer:** *(none — unreviewed)*
**Bench verification:** *(none)*

### 2.1 Transport parameters

| Setting | Value | Manual page |
|---|---|---|
| Interface | USB Virtual COM (behaves as RS-232 serial port) | p.40 §5.2.1; p.71 |
| Data bits / stop bits / parity | 8 / 1 / none | p.40 §5.2.2 |
| Baud rate | 600 / 1200 / 2400 / 4800 / 9600 / 19200 / 38400 | p.40 §5.2.3 |
| Baud default | 9600 | p.41 |
| Termination character | `<LF>` (ASCII 10) or `<CR>`, selectable on the instrument | p.40 §5.2.2; p.38–39 §4.5.3 |
| Reading data format | `SD.DDDDDDESDDD<NL>` | p.41 §5.3 |
| Echo handshake | **Every transmitted character is echoed; wait for it before sending the next** | p.41 §5.2.4 item 3 |
| Queries per line | **One** query per command line recommended; two queries require two reads | p.41 §5.2.4 item 5 |

### 2.2 Command syntax rules (p.42–45)

- Case-insensitive: `FUNC:VOLT:DC` = `func:volt:dc`.
- Short form: drop the 4th letter and everything after it if the 4th letter is a vowel (`:immediate` → `:imm`); keep it if a consonant (`:format` → `:form`); exception `:TCouple` → `:tc`.
- Brackets `[ ]` mark optional keywords — do not transmit the brackets.
- Angle brackets `< >` mark parameter types — do not transmit the brackets.
- A space separates command and parameter. No space before or after a colon.
- `;` separates commands at the same level; `;:` restarts from the root.
- Parameter types: `<b>` boolean (`0`/`OFF`/`1`/`ON`), `<n>` numeric or `DEFault`/`MINimum`/`MAXimum`, `<NRf>` number, `<name>` enumerated.

### 2.3 Common commands (p.62–63)

| ID | Command | Type | Response | Description | Page |
|---|---|---|---|---|---|
| `CR-2831E-001` | `*IDN?` | Query | `<product>,<version><LF^END>` e.g. `2831E Multimeter,Ver1.0.09.12.03` | Identify instrument | p.63 |
| `CR-2831E-002` | `*RST` | Command | none | Reset instrument. **Takes a long time — controller must wait, do not pipeline (p.41 §5.2.4 item 7)** | p.62–63 |
| `CR-2831E-003` | `*TRG` | Command | none | Trigger a measurement. **Prerequisite: `TRIGger:SOURce BUS`** | p.63 |

> The 2831E supports **only** these three common commands (p.45 §6.3). `*OPC?`, `*CLS`, `*ESR?`, `*STB?`, `*WAI` are **not documented** — treat as NOT IMPLEMENTED.

### 2.4 FUNCtion subsystem (p.47)

| ID | Command | Response | Description |
|---|---|---|---|
| `CR-2831E-010` | `:FUNCtion <name>` | none | Select measurement function |
| `CR-2831E-011` | `:FUNCtion?` | `<name>` | Query current function |

`<name>` ∈ `VOLTage:AC`, `VOLTage:DC`, `CURRent:AC`, `CURRent:DC`, `RESistance`, `FREQuency`, `PERiod`, `DIODe`, `CONTinuity`.

> Each function retains its own range / speed / filter / rel setup (p.47). Do not assume a range set under one function applies after switching.

### 2.5 RESistance subsystem (p.56–59) — primary harness continuity path

| ID | Command | Parameter | Default | Description | Page |
|---|---|---|---|---|---|
| `CR-2831E-020` | `:RESistance:NPLCycles <n>` | 0.5–2; `DEFault`=1, `MINimum`=0.1, `MAXimum`=10 | 1 | Integration period in power line cycles | p.56 |
| `CR-2831E-021` | `:RESistance:NPLCycles?` | — | — | Query NPLC | p.56 |
| `CR-2831E-022` | `:RESistance:RANGe[:UPPer] <n>` | 0 to 20e6 (expected reading, ohms) | 20e6 | Manual range select; sending a valid value **disables autorange** | p.57 |
| `CR-2831E-023` | `:RESistance:RANGe[:UPPer]?` | — | — | Query range | p.57 |
| `CR-2831E-024` | `:RESistance:RANGe:AUTO <b>` | `ON`/`1`/`OFF`/`0` | ON | Autorange | p.57 |
| `CR-2831E-025` | `:RESistance:RANGe:AUTO?` | — | — | Query autorange | p.57 |
| `CR-2831E-026` | `:RESistance:REFerence <n>` | 0 to 20e6 | 0 | Set REL reference. Reading = input − reference | p.58 |
| `CR-2831E-027` | `:RESistance:REFerence?` | — | — | Query reference. **Errors if no reference was ever set** | p.58 |
| `CR-2831E-028` | `:RESistance:REFerence:STATe <b>` | `ON`/`OFF` | OFF | Enable/disable REL | p.58 |
| `CR-2831E-029` | `:RESistance:REFerence:STATe?` | — | — | Query REL state | p.58 |
| `CR-2831E-030` | `:RESistance:REFerence:ACQuire` | — | — | Acquire present input as reference (lead-resistance null) | p.58–59 |

**`:ACQuire` prerequisites and error conditions (p.59) — enforce all three in the driver:**
1. The instrument must already be on the resistance function; sending it in another function **causes an error**.
2. The last reading must not have been an **overflow**.
3. A reading must have been **triggered**; if none has, an error occurs.

**Accuracy prerequisite:** the 200 Ω, 2 kΩ and 20 kΩ range accuracies are specified **only under REL** (p.67 footnote 2). A continuity/resistance recipe that skips the null is out of specification.

### 2.6 VOLTage subsystem (p.48–51)

| ID | Command | Parameter | Default |
|---|---|---|---|
| `CR-2831E-040` | `:VOLTage:DC:NPLCycles <n>` / `?` | 0.5–2; `DEF`=1, `MIN`=0.5, `MAX`=2 | 1 |
| `CR-2831E-041` | `:VOLTage:DC:RANGe[:UPPer] <n>` / `?` | 0 to 1010 | 1000 |
| `CR-2831E-042` | `:VOLTage:DC:RANGe:AUTO <b>` / `?` | `ON`/`OFF` | ON |
| `CR-2831E-043` | `:VOLTage:DC:REFerence <n>` / `?` | −1010 to 1010 | 0 |
| `CR-2831E-044` | `:VOLTage:DC:REFerence:STATe <b>` / `?` | `ON`/`OFF` | OFF |
| `CR-2831E-045` | `:VOLTage:DC:REFerence:ACQuire` | — | — |
| `CR-2831E-046` | `:VOLTage:AC:NPLCycles <n>` / `?` | 0.5–2 | 1 |
| `CR-2831E-047` | `:VOLTage:AC:RANGe[:UPPer] <n>` / `?` | 0 to 757.5 | 757.5 |
| `CR-2831E-048` | `:VOLTage:AC:RANGe:AUTO <b>` / `?` | `ON`/`OFF` | ON |
| `CR-2831E-049` | `:VOLTage:AC:REFerence <n>` / `?` | −757.5 to 757.5 | 0 |
| `CR-2831E-050` | `:VOLTage:AC:REFerence:STATe <b>` / `?` | `ON`/`OFF` | OFF |
| `CR-2831E-051` | `:VOLTage:AC:REFerence:ACQuire` | — | — |

Range is specified as the **expected reading**, not the range name: to select the 200 mV range, send `0.02` (p.49).

### 2.7 CURRent subsystem (p.52–55)

| ID | Command | Parameter | Default |
|---|---|---|---|
| `CR-2831E-060` | `:CURRent:DC:NPLCycles <n>` / `?` | 0.1–10; `DEF`=1, `MIN`=0.5, `MAX`=2 *(as printed p.53)* | 1 |
| `CR-2831E-061` | `:CURRent:DC:RANGe[:UPPer] <n>` / `?` | −20 to 20 | 20 |
| `CR-2831E-062` | `:CURRent:DC:RANGe:AUTO <b>` / `?` | `ON`/`OFF` | ON |
| `CR-2831E-063` | `:CURRent:DC:REFerence <n>` / `?` | 0 to 20 *(as printed)* | 0 |
| `CR-2831E-064` | `:CURRent:DC:REFerence:STATe <b>` / `?` | `ON`/`OFF` | OFF |
| `CR-2831E-065` | `:CURRent:DC:REFerence:ACQuire` | — | — |
| `CR-2831E-066` | `:CURRent:AC:NPLCycles <n>` / `?` | 0.1–10 | 1 |
| `CR-2831E-067` | `:CURRent:AC:RANGe[:UPPer] <n>` / `?` | 0 to 20 | 20 |
| `CR-2831E-068` | `:CURRent:AC:RANGe:AUTO <b>` / `?` | `ON`/`OFF` | ON |
| `CR-2831E-069` | `:CURRent:AC:REFerence <n>` / `?` | −20 to 20 *(as printed)* | 0 |
| `CR-2831E-070` | `:CURRent:AC:REFerence:STATe <b>` / `?` | `ON`/`OFF` | OFF |
| `CR-2831E-071` | `:CURRent:AC:REFerence:ACQuire` | — | — |

> **Manual inconsistencies to raise with the reviewer, not to silently "fix":**
> (a) p.53 gives the NPLC parameter range as `0.1 to 10` but `MINimum` = 0.5 and `MAXimum` = 2, which contradicts it.
> (b) p.52 table gives DC reference as −20 to 20 and AC as 0 to 20; p.54 body text gives AC as −20 to 20 and DC as 0 to 20 — the two are swapped.
> Encode the **narrower** of the two readings and flag both to the reviewer.

### 2.8 FREQuency / PERiod subsystem (p.59–61)

| ID | Command | Parameter | Default |
|---|---|---|---|
| `CR-2831E-080` | `:FREQuency:THReshold:VOLTage:RANGe <n>` / `?` | 0 to 1010 *(p.60)* / 0 to 750 *(p.59 table)* | 20 |
| `CR-2831E-081` | `:FREQuency:REFerence <n>` / `?` | 0 to 1.0e6 | 0 |
| `CR-2831E-082` | `:FREQuency:REFerence:STATe <b>` / `?` | `ON`/`OFF` | OFF |
| `CR-2831E-083` | `:FREQuency:REFerence:ACQuire` | — | — |
| `CR-2831E-084` | `:PERiod:THReshold:VOLTage:RANGe <n>` / `?` | 0 to 1010 / 0 to 750 | 20 |
| `CR-2831E-085` | `:PERiod:REFerence <n>` / `?` | 0 to 1 | 0 |
| `CR-2831E-086` | `:PERiod:REFerence:STATe <b>` / `?` | `ON`/`OFF` | OFF |
| `CR-2831E-087` | `:PERiod:REFerence:ACQuire` | — | — |

*(Threshold range printed inconsistently between p.59 and p.60 — flag to reviewer.)*

### 2.9 TRIGger subsystem (p.61–62)

| ID | Command | Parameter | Default |
|---|---|---|---|
| `CR-2831E-090` | `TRIGger:SOURce <name>` | `IMMediate` \| `BUS` \| `MANual` (a.k.a. `EXTernal`) | `IMMediate` |
| `CR-2831E-091` | `TRIGger:SOURce?` | — | — |

`IMMediate` = internal/continuous. `BUS` = triggered via USB/RS-232 by `*TRG`. `MANual` = front-panel Trig key.

### 2.10 FETCh subsystem (p.62)

| ID | Command | Response | Description |
|---|---|---|---|
| `CR-2831E-100` | `:FETCh?` | Reading in `SD.DDDDDDESDDD<NL>` format | **Returns the last available reading. Does NOT trigger a measurement and does NOT change configuration. Returns the same value repeatedly until a new reading occurs.** |

> **Staleness hazard — must be handled in the driver.** Because `:FETCh?` returns the *same* value until a new reading exists, a poll loop can silently return a stale reading and the test would pass on old data. The driver must use the documented deterministic sequence (§2.12) and must never treat a repeated identical value as a fresh measurement.

### 2.11 DISPlay subsystem (p.46)

| ID | Command | Parameter | Description |
|---|---|---|---|
| `CR-2831E-110` | `:DISPlay:ENABle <b>` | `ON`/`OFF` | Disable the front-panel display to run faster. **While disabled the display is frozen and all front-panel controls except LOCAL are disabled** |
| `CR-2831E-111` | `:DISPlay:ENABle?` | — | Query display state |

> **Do not use `:DISPlay:ENABle OFF` in production recipes.** Freezing the display and locking the front panel removes the operator's ability to see what the instrument is doing during an energized test. The speed gain is not worth it. If it is ever used, the application must guarantee re-enable on every exit path including exception, abort and timeout.

### 2.12 Only documented deterministic read sequence

```
TRIGger:SOURce BUS      # CR-2831E-090
:FUNCtion RESistance    # CR-2831E-010
:RESistance:RANGe:AUTO ON   # or an explicit range, CR-2831E-024 / -022
*TRG                    # CR-2831E-003  — trigger one measurement
:FETCh?                 # CR-2831E-100  — read it back
```

Each line is transmitted with the configured terminator, respecting the per-character echo handshake and one-query-per-line rule of §2.1.

### 2.13 BLOCKED items within the 2831E

| ID | Item | Why blocked |
|---|---|---|
| `CR-2831E-BLOCKED-01` | `:READ?` and `:MEASure?` | Referenced once on p.62 as commands that auto-assert `:FETCh?`, but **defined nowhere in the manual** — no syntax, no subsystem entry, no response format. **Do not guess.** Use §2.12 instead. |
| `CR-2831E-BLOCKED-02` | `HOLD` subsystem | Listed as an available subsystem on p.45 and referenced syntactically on p.42–43 (`:HOLD:STATe <b>`), but **has no §6.3 reference section** in this manual revision. Parameters, defaults and behaviour undocumented. |
| `CR-2831E-BLOCKED-03` | Limit / compare (HI-IN-LO) remote control | Limit mode is a headline datasheet feature (SRC-01 p.2) and is settable from the front panel (`MATH MEU → HI LIMIT / LO LIMIT`), but **no SCPI subsystem for it appears in Chapter 6.** Pass/fail limits must be evaluated **in the application**, from raw readings — not delegated to the meter. |
| `CR-2831E-BLOCKED-04` | Error / status queue readout | No `*ESR?`, `*STB?`, `SYSTem:ERRor?` documented. The `ERR` front-panel annunciator (p.~17) is **not machine-readable**. The driver cannot query instrument error state; it must rely on response parsing and timeouts. |
| `CR-2831E-BLOCKED-05` | Chapter 8 programming examples | Referenced on p.41 (*"Please refer to Chapter 8 for serial interface programming examples"*) but **the manual ends at Chapter 7 / p.71.** No examples exist in this document. |

---

## 3. B&K Precision DAQ3120 — BLOCKED

**Manual in repo:** none. `DAQ3120_datasheet.pdf` is a datasheet and contains **no commands**.

| ID | Item | Status |
|---|---|---|
| `CR-DAQ3120-000` | Entire command set | **BLOCKED** |

**Nothing may be written for this instrument** — no channel configuration, no scan list, no route, no read, not even `*IDN?`. In particular:

- Do **not** assume DAQ3120 SCPI resembles Keysight 34970A/DAQ970A syntax (`ROUT:SCAN`, `MEAS:VOLT:DC? (@101)`, …). Similarity of function is not evidence of syntax.
- Do **not** assume `*IDN?` works merely because it is an IEEE-488.2 common command.
- The **relay-switching commands are the highest-risk commands in this project** — a wrong route can connect a resistance measurement path to an energized circuit. They require the manual *and* the fixture schematic *and* the forbidden-combination table before a single line is written.

**To unblock:** obtain the B&K Precision DAQ3120 programming manual for the installed firmware from bkprecision.com, register it here with revision and date, transcribe with page citations, then review.

---

## 4. Tektronix TBS2104B — BLOCKED

**Manual in repo:** none. `Tektronix_TBS2104b.pdf` is a datasheet.
**Required document:** Tektronix programmer manual **`077-1149-xx`**, named in the datasheet's Standard Accessories list (p.14) and available from tek.com.

| ID | Item | Status |
|---|---|---|
| `CR-TBS2104B-000` | Entire command set | **BLOCKED** |

Do not carry over command knowledge from TDS/DPO/MDO/MSO series. Waveform-transfer commands in particular (preamble, encoding, byte order, scaling) differ between families and a wrong preamble assumption produces **plausible but wrong numbers**, which is worse than an error.

**Additional non-command requirement:** because automatic probe scaling does not apply to this scope with the TCPA400 (see `P0-DOC-02` §5.3), the application must apply the **1 A/mV → 1000 A/V** factor itself. That scale factor is a **reviewed configuration value**, and belongs in the reviewed configuration file — not in a driver constant.

---

## 5. ITECH IT-M3906B-32-240 — BLOCKED (highest hazard)

**Manual in repo:** none. `IT-M3906B-32-240_en.pdf` is a series datasheet.

| ID | Item | Status |
|---|---|---|
| `CR-ITM3906B-000` | Entire command set | **BLOCKED** |
| `CR-ITM3906B-001` | Output on/off | **BLOCKED — and additionally gated by engineer authorization even once documented** |
| `CR-ITM3906B-002` | Voltage / current / power setpoints | **BLOCKED** |
| `CR-ITM3906B-003` | Source ↔ Load mode selection | **BLOCKED** |
| `CR-ITM3906B-004` | Protection (OVP / OCP / OPP) configuration | **BLOCKED** |
| `CR-ITM3906B-005` | P-IO digital I/O behaviour and pinout | **BLOCKED — pinout not published in the datasheet** |

This instrument can source **6 kW at up to 240 A**, can **sink** current, and can **feed energy back into the building supply**. It is the single most dangerous device on the station.

Constraints that hold **regardless** of what the manual eventually says:

1. `real_output_control_enabled` stays `false` until the responsible engineer authorizes energized commissioning in writing.
2. Hazardous energy removal must be provable **without the PC** (`P0-DOC-01` §8). A software "output off" command is never the safety function.
3. The **Source/Load mode is a front-panel state** (datasheet p.4). The application must read and display it and must never assume Source.
4. `P-IO` is a candidate hardwired interlock/inhibit path (COM-008). Its pinout must come from the manual and its use must be decided by the responsible engineer — **not inferred**.
5. Approved voltage/current/power ceilings (`P0-DOC-01` §9 placeholders) must be set and reviewed **before** any setpoint command is enabled, and they are **not** the instrument's protection trip points.

---

## 6. Review log

| Date | Register version | Reviewer | Scope reviewed | Outcome |
|---|---|---|---|---|
| — | initial draft | *(none)* | — | **No entry in this register is approved for hardware execution.** |

## 7. Change control

Any addition to this register must record: source document filename, document revision/date, exact model, exact firmware, page/section, verbatim syntax, response format, units, prerequisites, error conditions, reviewer name, review date, and bench-verification evidence. An entry missing any field stays `TRANSCRIBED` or `BLOCKED`.
