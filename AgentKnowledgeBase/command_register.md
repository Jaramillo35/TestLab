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
| `TRANSCRIBED` | Syntax copied verbatim from a manufacturer manual in this repo **for the exact model**, with page citation. Not yet reviewed. Not yet bench-verified. Simulation use only. |
| `TRANSCRIBED-PROVISIONAL` | Syntax from a manufacturer manual for a **related but different series**. Usable to design and unit-test a *simulated* driver only. **Never in Real mode.** Every entry must be re-verified against the correct-model manual, and no constant from it may be hard-coded. |
| `BLOCKED` | No manufacturer programming manual is available for this instrument. **No command may be written, guessed, or adapted from a sibling model.** |
| `APPROVED` | Reviewed by a named engineer against the manual for the exact model *and firmware*, and bench-verified. **Currently: none.** |

**Firmware caveat.** Every `TRANSCRIBED` entry below is transcribed from a manual whose own example `*IDN?` response is `2831E Multimeter,Ver1.0.09.12.03`. If the installed unit reports a different firmware version, **every entry reverts to unverified** until re-checked against the matching manual revision.

**Current count: 0 APPROVED. 1 of 4 instruments fully BLOCKED (ITECH). 1 provisional (Tektronix).**

---

## 1. Instrument transport summary

| Instrument | Manual in repo? | Transport | Register status |
|---|---|---|---|
| B&K 2831E DMM ×2 | **Yes** — `bk_precision_2831e_manual.pdf` | USB Virtual COM (serial, CP210x), 8N1, 9600 default, `<LF>` or `<CR>` | `TRANSCRIBED` |
| B&K DAQ3120 | **Yes** — `manuals/DAQ3120_programming_manual.pdf` | LAN / USBTMC / USBVCP / micro-GPIB | `TRANSCRIBED` |
| Tektronix TBS2104B | **Wrong series** — `manuals/TBS2000-Programmer-077114902.pdf` is TBS2000, not TBS2000**B** | LAN / USBTMC | `TRANSCRIBED-PROVISIONAL` |
| ITECH IT-M3906B-32-240 | **No programming guide.** User manual present (`manuals/IT-M3900B-User-Manual.pdf`) — hardware interfaces only | LAN / USB / CAN / P-IO | `BLOCKED` |

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
| USB bridge chip | **Silicon Labs CP210x USB-to-UART Bridge** | B&K `Bench_Multimeter_USB_Drivers.zip` → `slabvcp.inf` (SRC-09) |
| USB VID / PID | **`0x10C4` / `0xEA60`** (dual-port variants use `0xEA70` + `Mi_00`/`Mi_01`) | SRC-09 `slabvcp.inf` |
| Bundled driver version | 6.6.0.0, dated 2012-10-05 — **predates Windows 10/11; obtain a current CP210x VCP driver** | SRC-09 `ReleaseNotes.txt` |

> **Port mapping (closes the OBS-007 action).** Enumerate by `VID_10C4` + `PID_EA60` + **serial number**, never by COM-port order — `pyserial`'s `comports()` exposes `vid`, `pid` and `serial_number`. **Caveat R-DMM-02:** CP210x devices are often shipped with identical factory serial strings. Test with both meters connected before relying on serial-based identification; if the serials collide, fall back to a documented physical-port binding and make it a commissioning checklist item.

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

## 3. B&K Precision DAQ3120 — TRANSCRIBED

**Source document:** `manuals/DAQ3120_programming_manual.pdf` (SRC-07), *DAQ3120 Series Programming Manual*, version stamp **January 7, 2026**, 139 pp. SHA-256 (first 16) `563c57bf11cae55a`. Retrieved from B&K Precision's media bucket — see `P0-DOC-03_internet_research_findings.md` §2.
**Model scope:** DAQ3120 Series.
**Reviewer:** *(none — unreviewed)*
**Bench verification:** *(none)*
**Firmware caveat:** unverified against the installed unit. `*IDN?` returns the firmware version — record it and re-check this register against the matching manual revision.

> **Switching commands are the highest-risk commands in this project.** A wrong route can connect a resistance measurement path to an energized circuit, or short two harness pins together. Nothing in §3.6 may be emitted until the fixture schematic, the channel map and the forbidden-combination table exist and have been reviewed (`P0-DOC-01` OBS-009, T-04).

### 3.1 Syntax and data types (SRC-07 ch. 2–3)

- Standard SCPI: long/short forms, case-insensitive, responses return short form uppercase.
- `<NRf>` accepts `<NR1>` integer, `<NR2>` decimal, `<NR3>` exponent.
- `<Boolean>`: `ON`/`1`, `OFF`/`0`.
- `<String>`: double-quoted; the quotes are part of the syntax.
- Special keywords: `MIN`, `MAX`, `DEF`, `AUTO`.

**Channel list `(@<ch_list>)` — SRC-07 §3.3, p.18:**

| Form | Example |
|---|---|
| Single | `(@101)` |
| Multiple | `(@101,102,105)` |
| Range | `(@101:105)` |
| Combined | `(@101:105,201)` |

Channel numbers are `<slot><channel>`: slot 1 → `1xx`, slot 2 → `2xx`, slot 3 → `3xx`. Computed "Computer Channels" are **401–420** (DAQ3120 user manual §5.6.1).

### 3.2 Common commands (SRC-07 ch. 5, pp.22–26)

| ID | Command | Response | Notes |
|---|---|---|---|
| `CR-DAQ-001` | `*IDN?` | `B&K Precision, DAQ3120, <Serial Number>, <Firmware Version>` | **Serial and firmware are machine-readable** — automate the identity check |
| `CR-DAQ-002` | `*RST` | — | Factory default. **Aborts any scan and clears the scan list** |
| `CR-DAQ-003` | `*CLS` | — | Clear status |
| `CR-DAQ-004` | `*ESE` / `*ESR?` | — / `<NR1>` | Standard event status enable / read |
| `CR-DAQ-005` | `*OPC` / `*OPC?` | — / `<NR1>` | Operation complete |
| `CR-DAQ-006` | `*SRE` / `*STB?` | — / `<NR1>` | Service request enable / status byte |
| `CR-DAQ-007` | `*TRG` | — | Software trigger. **Prerequisite: `TRIGger:SOURce BUS`** |
| `CR-DAQ-008` | `*TST?` | `0` = pass, non-zero = fail | Complete self-test |
| `CR-DAQ-009` | `*WAI` | — | Wait for pending operations |
| `CR-DAQ-010` | `*SAV` / `*RCL` | — | Save / recall instrument state |
| `CR-DAQ-011` | `*PSC` | — | Power-on status clear |

### 3.3 Acquisition control (SRC-07 ch. 6, pp.28–30)

| ID | Command | Description |
|---|---|---|
| `CR-DAQ-020` | `ABORt` | Aborts a scan in progress, returns to trigger idle. **Starting a new scan after an abort clears reading memory** |
| `CR-DAQ-021` | `INITiate[:IMMediate]` | Idle → wait-for-trigger. **Clears the previous set of measurements from reading memory** |
| `CR-DAQ-022` | `FETCh?` | Waits for completion, copies all available measurements to the output buffer. **Does not erase readings** — the same data can be retrieved repeatedly |
| `CR-DAQ-023` | `READ?` | Starts a new scan and waits for completion. **Equivalent to `ABORt` + `INITiate` + `FETCh?`** |
| `CR-DAQ-024` | `R? <NR1>` | Reads **and erases** up to `<NR1>` (1–100000) oldest readings. Returns block data (e.g. `#279…`). **Does not wait for completion** |
| `CR-DAQ-025` | `INSTrument:DMM <Boolean>` / `?` | Enable/disable the internal DMM |
| `CR-DAQ-026` | `TIME:SYNC:SERVer "<url>"` / `?` | NTP server |
| `CR-DAQ-027` | `UNIT:TEMPerature C\|F\|K [,(@<ch_list>)]` / `?` | Temperature units |

> **`CR-DAQ-025` is architecturally important and has a trap.** Manual, §6.4: *"When disabled, the instrument acts as a switch, allowing external instruments to measure signals routed through the multiplexer modules."* — this is how the DAQ routes harness pins to the two external 2831E DMMs. **But: *"Changing the state of the internal DMM triggers a Factory Reset (`*RST`)."*** So it is a connect-time decision only. Never toggle it mid-sequence: it silently discards the scan list and all channel configuration.

> **Reading memory is 100,000 readings and wraps** — *"If memory overflows, the oldest readings are overwritten."* For long scans use `R?` to drain periodically, and never assume `FETCh?` returned everything.

### 3.4 CONFigure subsystem (SRC-07 ch. 8, pp.39–45)

| ID | Command | Parameters |
|---|---|---|
| `CR-DAQ-030` | `CONFigure? [(@<ch_list>)]` | Returns e.g. `"VOLT +1.000000E+01,+3.000000E-06"` |
| `CR-DAQ-031` | `CONFigure:RESistance\|FRESistance [<range>[,<resolution>]][,(@<ch_list>)]` | `<range>`: value \| `AUTO` \| `MIN` \| `MAX` \| `DEF` (**100 Ω to 100 MΩ**). `FRESistance` = 4-wire |
| `CR-DAQ-032` | `CONFigure[:VOLTage]:AC\|DC [<range>[,<resolution>]][,(@<ch_list>)]` | |
| `CR-DAQ-033` | `CONFigure:CURRent:AC\|DC [<range>[,<resolution>]][,(@<ch_list>)]` | **DM301 channels 21/22 and DM309 current channels only** |
| `CR-DAQ-034` | `CONFigure:FREQuency\|PERiod [<range>[,<resolution>]][,(@<ch_list>)]` | Auto range only; value ignored |
| `CR-DAQ-035` | `CONFigure:DIODe [(@<ch_list>)]` | |
| `CR-DAQ-036` | `CONFigure:CAPacitance [<range>[,<resolution>]][,(@<ch_list>)]` | 1 nF to 100 µF |
| `CR-DAQ-037` | `CONFigure:TEMPerature …` | Thermocouple / RTD / thermistor |
| `CR-DAQ-038` | `CONFigure:STRain:…` | Direct / quarter / half / full bridge |
| `CR-DAQ-039` | `CONFigure:TOTalize` | DM307 |
| `CR-DAQ-040` | `CONFigure:DIGital[:BYTE]`, `CONFigure:DAC:OUTPut`, `CONFigure:DAC:SENSe` | DM307 |

Example, verbatim from the manual: `CONF:RES 10k,(@101)`

### 3.5 MEASure subsystem (SRC-07 ch. 14, pp.62–67)

`MEASure:…?` configures **and** immediately returns a value. Same parameter shapes as `CONFigure`.

| ID | Query |
|---|---|
| `CR-DAQ-050` | `MEASure:RESistance\|FRESistance? [<range>[,<resolution>]][,(@<ch_list>)]` — e.g. `MEAS:RES? 10k,(@101)` |
| `CR-DAQ-051` | `MEASure[:VOLTage]:AC\|DC? …` |
| `CR-DAQ-052` | `MEASure:CURRent:AC\|DC? …` |
| `CR-DAQ-053` | `MEASure:FREQuency\|PERiod? …` |
| `CR-DAQ-054` | `MEASure:DIODe? [(@<ch_list>)]` |
| `CR-DAQ-055` | `MEASure:CAPacitance? …` |
| `CR-DAQ-056` | `MEASure:TEMPerature? …` |
| `CR-DAQ-057` | `MEASure:TOTalize?`, `MEASure:DIGital[:BYTE]?`, `MEASure:DAC:OUTPut?`, `MEASure:DAC:SENSe?` |
| `CR-DAQ-058` | `MEASure:STRain:…?` |

### 3.6 ROUTe subsystem — SWITCHING, HIGHEST RISK (SRC-07 ch. 17, pp.74–77)

| ID | Command | Description |
|---|---|---|
| `CR-DAQ-060` | `ROUTe:CLOSe (@<ch_list>)` / `ROUTe:CLOSe? (@<ch_list>)` | Closes the specified channels. **Allows multiple channels closed simultaneously.** Does **not** open anything else |
| `CR-DAQ-061` | `ROUTe:CLOSe:EXCLusive (@<ch_list>)` | Closes the channel and **opens all other channels on the same bank (break-before-make)** |
| `CR-DAQ-062` | `ROUTe:OPEN (@<ch_list>)` / `?` | Opens the specified channels |
| `CR-DAQ-063` | `ROUTe:DONE?` | Returns `1` when all relay operations are finished |
| `CR-DAQ-064` | `ROUTe:SCAN (@<ch_list>)` / `?` | Defines the scan list. **`ROUTe:SCAN (@)` clears it** |
| `CR-DAQ-065` | `ROUTe:SCAN:SIZE?` | Number of channels in the scan list |
| `CR-DAQ-066` | `ROUTe:MONitor (@<ch_list>)` / `?` | Channel to monitor continuously. **Only one at a time** |
| `CR-DAQ-067` | `ROUTe:MONitor:STATe <Boolean>` / `?` | Enable monitor mode |

**Mandatory design rules for the route layer:**

1. **Default to `CR-DAQ-061` (`ROUTe:CLOSe:EXCLusive`).** Plain `ROUTe:CLOSe` leaves previously closed channels closed, which on a harness fixture means unintended pin-to-pin connections. Emitting `ROUTe:CLOSe` must require an explicit, reviewed multi-point intent that has been checked against the forbidden-combination table.
2. **Synchronize on `ROUTe:DONE?`, never on a fixed sleep.**
3. **Open before de-energizing and after every sequence**, including abort, timeout, exception and application close.
4. No route may be emitted at all until T-04 (fixture schematic, pin map, route table, forbidden combinations) exists and is reviewed.

### 3.7 SENSe — resistance (SRC-07 ch. 18.8, pp.89–92)

| ID | Command | Parameters |
|---|---|---|
| `CR-DAQ-070` | `[SENSe:]RESistance\|FRESistance:NPLCycles <PLCs> [,(@<ch_list>)]` / `?` | **0.02 to 200** |
| `CR-DAQ-071` | `[SENSe:]RESistance\|FRESistance:APERture <seconds>` / `?` | Integration time in seconds |
| `CR-DAQ-072` | `[SENSe:]RESistance\|FRESistance:APERture:ENABle <state>` / `?` | Use aperture instead of NPLC |
| `CR-DAQ-073` | `[SENSe:]RESistance\|FRESistance:OCOMpensated <state>` / `?` | **Offset compensation — cancels thermal EMF.** e.g. `RES:OCOM ON,(@101)` |
| `CR-DAQ-074` | `[SENSe:]RESistance\|FRESistance:POWer:LIMit[:STATe] <state>` / `?` | **Low-power mode — prevents self-heating** |
| `CR-DAQ-075` | `[SENSe:]RESistance\|FRESistance:RANGe <range>` / `?` | 100 Ω to 100 MΩ |
| `CR-DAQ-076` | `[SENSe:]RESistance\|FRESistance:RANGe:AUTO <state>` / `?` | `OFF` \| `ON` \| `ONCE` |
| `CR-DAQ-077` | `[SENSe:]RESistance\|FRESistance:ZERO:AUTO <state>` / `?` | `OFF` \| `ON` \| `ONCE` |

> For milliohm-level harness continuity, prefer **`FRESistance`** (4-wire) with **`OCOMpensated ON`**. The datasheet warns that 2-wire without a math null adds **2 Ω** of error, and module thermal offset is <1–4 µV, which at 1 mA test current is ~1–4 mΩ. Both settings belong in the reviewed recipe, not in driver defaults.

Other `SENSe` branches follow the same shape: `[SENSe:]FUNCtion[:ON]`, `AVERage:*`, `VOLTage:*` (incl. `[SENSe:]VOLTage[:DC]:IMPedance:AUTO`), `CURRent:*`, `FREQuency|PERiod:*`, `TEMPerature:*`, `STRain:*`, `TOTalize:*`, `CAPacitance:*`, `DIODe:ZERO:AUTO`, `DIGital:DATA…?`.

### 3.8 TRIGger subsystem (SRC-07 ch. 22, pp.139–140)

| ID | Command | Parameters |
|---|---|---|
| `CR-DAQ-080` | `TRIGger:SOURce IMMediate\|TIMer\|EXTernal\|BUS\|ALARm1..4` / `?` | `IMM` scans immediately after `INITiate`; `TIM` uses `TRIGger:TIMer`; `EXT` waits for a TTL pulse on the rear-panel Ext Trig input; `BUS` waits for `*TRG` |
| `CR-DAQ-081` | `TRIGger:COUNt <count>\|MIN\|MAX\|DEF\|INFinity` / `?` | 1 to 1,000,000, or `INFinity` (**scans until `ABORt`**) |
| `CR-DAQ-082` | `TRIGger:TIMer <seconds>\|MIN\|MAX\|DEF` / `?` | 0 to 360000 s, 1 ms resolution |
| `CR-DAQ-083` | `TRIGger:SLOPe POSitive\|NEGative` / `?` | External trigger edge. Only relevant with `TRIGger:SOURce EXTernal` |

### 3.9 CALCulate — limits and scaling (SRC-07 ch. 7, pp.33–37)

| ID | Command | Parameters |
|---|---|---|
| `CR-DAQ-090` | `CALCulate:LIMit:LOWer <value> [,(@<ch_list>)]` / `?` | −1.0E+9 to 1.0E+9 |
| `CR-DAQ-091` | `CALCulate:LIMit:UPPer <value> [,(@<ch_list>)]` / `?` | −1.0E+9 to 1.0E+9 |
| `CR-DAQ-092` | `CALCulate:LIMit:STATe <Boolean> [,(@<ch_list>)]` / `?` | Per-channel limit testing |
| `CR-DAQ-093` | `CALCulate:SCALe:GAIN` / `:OFFSet` / `:STATe` | Mx+B scaling |
| `CR-DAQ-094` | `CALCulate:AVERage:ALL?` / `:AVERage?` / `:MINimum?` / `:MAXimum?` / `:COUNt?` / `:CLEar` | Statistics |
| `CR-DAQ-095` | `CALCulate:SMOothing:RESPonse` / `:STATe` | |

> **`CALCulate:LIMit` does not replace application-side pass/fail.** Unlike the 2831E, the DAQ *can* evaluate limits — but the run record must still store the **raw reading** and the application must still compute the verdict. Instrument limit state may be used for alarm outputs and early abort, never as the sole recorded verdict.

### 3.10 SYSTem subsystem — identity, errors, LAN (SRC-07 ch. 21, pp.121–137)

| ID | Command | Description |
|---|---|---|
| `CR-DAQ-100` | `SYSTem:CTYPe? <slot>` | **Queries the module installed in slot 1–3.** e.g. `SYST:CTYP? 1` |
| `CR-DAQ-101` | `SYSTem:ERRor?` | **Queries and clears the next error** — code and message string |
| `CR-DAQ-102` | `SYSTem:SERial?` | Instrument serial number |
| `CR-DAQ-103` | `SYSTem:VERSion?` | SCPI version |
| `CR-DAQ-104` | `SYSTem:LFRequency?` | **Detected power line frequency (50 or 60 Hz)** |
| `CR-DAQ-105` | `SYSTem:CPON` | Card power on — reinitializes the plug-in modules |
| `CR-DAQ-106` | `SYSTem:LOCal` / `SYSTem:REMote` | Front panel unlock / lock |
| `CR-DAQ-107` | `SYSTem:PRESet` | |
| `CR-DAQ-108` | `SYSTem:RELay:CYCLes?` / `:CLEar` / `:FACTory?` | **Relay cycle counters — preventive-maintenance data** |
| `CR-DAQ-109` | `SYSTem:TEMPerature?`, `SYSTem:UPTime?`, `SYSTem:DATE`, `SYSTem:TIME`, `SYSTem:TIME:SCAN?` | |
| `CR-DAQ-110` | `SYSTem:SLOT:LABel`, `SYSTem:WMESsage`, `SYSTem:ALARm?`, `SYSTem:BEEPer…`, `SYSTem:CLICk:STATe` | |
| `CR-DAQ-111` | `SYSTem:SCPi:MODE`, `SYSTem:SCPi:AUTO:SAVE`, `SYSTem:PERSona…` | Emulation/identity spoofing — **do not change** |
| `CR-DAQ-112` | `SYSTem:COMMunicate:LAN:DHCP\|IPADdress\|SMASk\|GATeway\|DNS\|HOSTname\|MAC?\|DOMain?\|WINS\|UPDate\|TIMeout` | LAN configuration |
| `CR-DAQ-113` | `SYSTem:COMMunicate:LAN:TCP:ENABle` / `:TCP:PORT` | Raw socket. Manual example port **5025** |
| `CR-DAQ-114` | `SYSTem:COMMunicate:LAN:TELNet:ENABle\|PORT\|ECHO\|TIMeout\|PROMpt\|WMESsage` | Telnet. **Default port 5024** |
| `CR-DAQ-115` | `SYSTem:COMMunicate:LAN:WEB:ENABle` | **Web interface on/off** |
| `CR-DAQ-116` | `SYSTem:COMMunicate:GPIB:ADDRess` | 0–30, default 15 |

> **`CR-DAQ-100` and `CR-DAQ-101` change what the application can guarantee.** `SYSTem:CTYPe?` lets the app **verify the installed module in each slot at connect time** and refuse to run if the configuration does not match the reviewed channel map. `SYSTem:ERRor?` gives real error reporting — drain the queue after every command batch. Neither has an equivalent on the 2831E.
>
> **`CR-DAQ-111` `SYSTem:PERSona`** changes the identity string the instrument reports. It must never be used: it would defeat the identity check the project depends on.
>
> **Security:** Telnet (`CR-DAQ-114`) and the web interface (`CR-DAQ-115`) should be **disabled** on a production station unless IT approves otherwise, and the decision recorded (`P0-DOC-01` OBS-006).

### 3.11 Other subsystems available

`DATA:LAST?`, `DATA:POINts?`, `DATA:POINts:EVENt:THReshold`, `DATA:REMove?` (ch. 9) · `DIGital:INTerface:MODE\|DATA:OUTPut\|DATA:SETup` (ch. 10) · `DISPlay`, `DISPlay:TEXT`, `DISPlay:TEXT:CLEar` (ch. 11) · `FORMat:READing:ALARm\|CHANnel\|DATE\|TIME\|TIME:TYPE\|UNIT` (ch. 12) · `HCOPy:SDUMp:DATA?\|FORMat` screen dump (ch. 13) · `MMEMory:FORMat:READing:*`, `MMEMory:LOG[:ENABle]` (ch. 15) · `OUTPut:ALARm:CLEar\|MODE\|SLOPe` (ch. 16) · `SOURce:CURRent\|VOLTage\|MODE\|MODE:LOCK\|DIGital:DATA[:BYTE]\|:WORD` (ch. 19, DM307) · `STATus:ALARm\|OPERation\|QUEStionable :CONDition?\|:ENABle\|[:EVENt]?`, `STATus:PRESet` (ch. 20).

> **`FORMat:READing:CHANnel ON` is strongly recommended.** It prefixes each value with its channel number, so a returned block cannot be silently mis-associated with the wrong harness pin. Likewise `FORMat:READing:DATE`/`TIME` for traceable run records.

### 3.12 Deterministic scan sequence (composed from the above)

```
*RST                                  # CR-DAQ-002  clears scan list and config
SYST:ERR?                             # CR-DAQ-101  drain the error queue
*IDN?                                 # CR-DAQ-001  record serial + firmware
SYST:CTYP? 1                          # CR-DAQ-100  verify module in each slot
SYST:LFR?                             # CR-DAQ-104  read line frequency, do not assume
FORM:READ:CHAN ON                     # CR-DAQ-...  channel number with every reading
CONF:FRES 100,(@101:110)              # CR-DAQ-031  4-wire, reviewed range
FRES:OCOM ON,(@101:110)               # CR-DAQ-073  cancel thermal EMF
FRES:NPLC 10,(@101:110)               # CR-DAQ-070  reviewed integration time
ROUT:SCAN (@101:110)                  # CR-DAQ-064  reviewed scan list
TRIG:SOUR BUS                         # CR-DAQ-080
TRIG:COUN 1                           # CR-DAQ-081
INIT                                  # CR-DAQ-021
*TRG                                  # CR-DAQ-007
FETC?                                 # CR-DAQ-022
SYST:ERR?                             # CR-DAQ-101  confirm no error was raised
```

**This sequence is `TRANSCRIBED`, not `APPROVED`.** The channel list is illustrative — real channels require the fixture map (T-04) and the module list (T-08).

### 3.13 DAQ3120 items still requiring the user manual or bench work

| ID | Item | Status |
|---|---|---|
| `CR-DAQ-OPEN-01` | `SYSTem:CTYPe?` response string format | Not shown in the programming manual — capture it on the bench |
| `CR-DAQ-OPEN-02` | `SYSTem:ERRor?` error-code table | Not in the programming manual |
| `CR-DAQ-OPEN-03` | Exact per-module channel numbering (which channel numbers are the DM301 current channels; the manual body says current is on **channels 21 and 22** of DM301, i.e. `(@121)`/`(@122)` in slot 1 — **confirm on the bench before use**) | Partly documented, needs confirmation |
| `CR-DAQ-OPEN-04` | Default raw-socket port on the installed unit (manual *example* uses 5025) | Confirm by query |
| `CR-DAQ-OPEN-05` | `R?` block-data format (`#279…`) parsing rules | Confirm on the bench |

---

## 4. Tektronix TBS2104B — TRANSCRIBED-PROVISIONAL (wrong-series source)

**Source document:** `manuals/TBS2000-Programmer-077114902.pdf` (SRC-11) — *TBS2000 Series Digital Oscilloscopes Programmer*, `077-1149-02` Rev A, 342 pp.
**Model scope: TBS2000 series. Our instrument is a TBS2104B — TBS2000B series.**
**Reviewer:** *(none)* · **Bench verification:** *(none)*

> ### ⚠ Why this is PROVISIONAL and not TRANSCRIBED
>
> Tektronix publishes a **separate** TBS2000B programmer manual; the existence of a separate publication is itself evidence the two differ. SRC-11 mentions `TBS2000B` exactly once — a B-specific `*IDN?` response format on p.168 — which shows awareness of the B series, not coverage of it.
>
> **A concrete, proven difference (F-SCOPE-01).** SRC-11 pp.34 and 53 state that waveforms are **≤2500 data points** and that *"the instrument truncates waveforms longer than 2500 data points"*, and that `DATa:STOP 2500` *"always sends the entire waveform"*. **The TBS2104B has a 5 M point record** — 2500 points is **0.05%** of it. A driver carrying that constant over would return a plausible waveform that silently discards 99.95% of the acquisition, with no error raised.
>
> **Permitted:** designing and unit-testing the *simulated* scope driver in Phase 1, which touches no hardware.
> **Forbidden:** any use in Real mode; hard-coding any record-length, preamble or scaling constant from this manual; treating any entry as verified for the TBS2104B.
> **To promote to `TRANSCRIBED`:** obtain the TBS2000B programmer manual (`P0-DOC-03` §5 #1) and re-verify every entry, `DATa:STOP` and record-length handling first.

### 4.1 Command groups (SRC-11 TOC)

Acquisition · Alias · Bus · Calibration · Cursor · Display · Ethernet · File System · Hard Copy · Horizontal · Math · Measurement · Miscellaneous · Save and Recall · Status and Error · Trigger · Vertical · **Waveform** · Zoom

### 4.2 Core commands — PROVISIONAL

| ID | Command | Notes |
|---|---|---|
| `CR-TBS-P001` | `*IDN?` | `TEKTRONIX,<model>,<serial>,CF:91.1CT FV:v<fw>`. **TBS2000B returns a different format** adding `TBS2XXXV:v<module fw>` (SRC-11 p.168) |
| `CR-TBS-P002` | `ACQuire:STATE` | Start/stop acquisitions |
| `CR-TBS-P003` | `ACQuire:STOPAfter` | When to stop acquiring |
| `CR-TBS-P004` | `ACQuire:MODe` | SAMple \| PEAKdetect \| AVErage \| HIRes |
| `CR-TBS-P005` | `ACQuire:NUMAVg` | Averaging count |
| `CR-TBS-P006` | `ACQuire:NUMACq?` | Acquisitions taken |
| `CR-TBS-P007` | `SELect:CH<x>` | Channel display on/off |
| `CR-TBS-P008` | `MEASUrement:IMMed:VALue?` | Immediate measurement result |
| `CR-TBS-P009` | `CURVe` / `CURVe?` | Waveform data transfer, binary or ASCII |
| `CR-TBS-P010` | `DATa:SOUrce` | Which waveform to transfer |
| `CR-TBS-P011` | `DATa:STARt` / `DATa:STOP` | **DANGER — see F-SCOPE-01. Do not carry 2500 over.** |
| `CR-TBS-P012` | `DATa:WIDth` | Bytes per data point |
| `CR-TBS-P013` | `DATa:ENCdg` | `ASCII` \| `RIBinary` \| `RPBinary` \| `SRIbinary` \| `SRPbinary` |
| `CR-TBS-P014` | `WAVFrm?` | Returns `WFMPre?` + `CURVe?` together |
| `CR-TBS-P015` | `WFMPre:` / `WFMInpre:` | Preamble: `XINcr`, `BIT_Nr`, `BYT_Nr`, `NR_Pt?` — scaling source |
| `CR-TBS-P016` | `BUSY?` | Instrument status |
| `CR-TBS-P017` | `*OPC` / `*OPC?` / `*WAI` | Synchronization |

### 4.3 Waveform encoding — PROVISIONAL

Internally 8 bits per point regardless of acquisition mode. `DATa:WIDth 2` multiplies by 256 on send, truncates (divides by 256) on receive. Binary ranges: 1 byte signed −128…127 / unsigned 0…255; 2 byte signed −32768…32767 / unsigned 0…65535. `RIBinary`/`RPBinary` MSB-first; `SRIbinary`/`SRPbinary` LSB-first; byte order ignored when `DATa:WIDth` is 1.

### 4.4 Socket server

Enabled from the front panel: `Utility → Config → Socket Server`, protocol `None` or `Terminal`, port settable. **No default port is stated in SRC-11 — read it off the instrument.**

### 4.5 Non-command requirement, unchanged

Automatic probe scaling does not apply to this scope with the TCPA400 (`P0-DOC-02` §5.3). The application applies **1 A/mV → 1000 A/V** itself, from reviewed configuration, never a driver constant.

## 5. ITECH IT-M3906B-32-240 — BLOCKED (highest hazard)

**Commands: still BLOCKED.** The **Programming Guide is not in this repo.** `manuals/IT-M3900B-User-Manual.pdf` (SRC-10, 348 pp) is the *User Manual*; it documents operation and hardware interfaces but contains **no SCPI command set**, and explicitly defers to a separate publication (SRC-10 p.73: *"please refer to the instructions of 'ARB Subsystem' in the Programming Guide"*). `itech-it-m3900b-pv3900-software-user-manual.pdf` is the PV3900 **PC software** manual and contains zero SCPI.

**To unblock:** `https://cdn.itechate.com/uploadfiles/%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C/user%20manual/it-m3900b/IT-M3900B%20Programming%20Guide-EN.pdf`

| ID | Item | Status |
|---|---|---|
| `CR-ITM3906B-000` | Entire command set | **BLOCKED** |
| `CR-ITM3906B-001` | Output on/off | **BLOCKED — and additionally gated by engineer authorization even once documented** |
| `CR-ITM3906B-002` | Voltage / current / power setpoints | **BLOCKED** |
| `CR-ITM3906B-003` | Source ↔ Load mode selection | **BLOCKED** |
| `CR-ITM3906B-004` | Protection (OVP / OCP / OPP) configuration | **BLOCKED** |
| ~~`CR-ITM3906B-005`~~ | P-IO digital I/O pinout | ✅ **DOCUMENTED** — see §5.1 below (SRC-10 §6.11). This is a *hardware interface*, not a command. |

This instrument can source **6 kW at up to 240 A**, can **sink** current, and can **feed energy back into the building supply**. It is the single most dangerous device on the station.

Constraints that hold **regardless** of what the manual eventually says:

1. `real_output_control_enabled` stays `false` until the responsible engineer authorizes energized commissioning in writing.
2. Hazardous energy removal must be provable **without the PC** (`P0-DOC-01` §8). A software "output off" command is never the safety function.
3. The **Source/Load mode is a front-panel state** (datasheet p.4). The application must read and display it and must never assume Source.
4. `P-IO` is a candidate hardwired interlock/inhibit path (COM-008). Its pinout must come from the manual and its use must be decided by the responsible engineer — **not inferred**.
5. Approved voltage/current/power ceilings (`P0-DOC-01` §9 placeholders) must be set and reviewed **before** any setpoint command is enabled, and they are **not** the instrument's protection trip points.

### 5.1 P-IO digital interface — DOCUMENTED (SRC-10 §6.11, pp.189–204)

Not commands — a hardware interface. Recorded here because it is the candidate safety path (COM-008).

| Pin | Default function | Signal |
|---:|---|---|
| 1 | `Ps-Fault-Clear` — clear the protection state | Pulse |
| 2 | `Ps` — protection state indicator | Level |
| 3 | `Off-Status` — On/Off status indicator | Level |
| 4 | `Trig(in)` — trigger signal | Pulse |
| 5 | **`INH-Living` — turn off the output under emergency status** | Pulse |
| 6 | `Sync-On` — synchronous on control | Pulse |
| 7 | `Sync-Off` — synchronous off control | Pulse |
| GND | Ground, negative terminal for all 7 pins | Level |

Input high 1.6–15 V (typ 5 V), input low −5–0.8 V, ≤100 mA. Output 5 V / 0 V. Pulse: rise 10 µs, fall 2 µs, width 30 µs, min low hold 30 µs. All pulses switch **high → low**. Each pin has `Invert` / `Not-Invert`.

> **F-PSU-03 — the default inhibit mode auto-recovers.**
> `Inhibit-Living` (**factory default**): drive pin 5 low and output goes to 0, but the `[On/Off]` light **stays lit** and the VFD **still displays `On`** (with `INH`); *"when pin 5 receives high level signal again, the output state is recovered"* — **automatically, with no human action**.
> `Inhibit-Latch`: a pulse turns `[On/Off]` **off** and latches; *"the user needs to manually turn on `[On/Off]`"*.
>
> **Only `Inhibit-Latch` is defensible in a safety tie-in.** A 240 A output that re-energizes by itself when a contact recloses is not acceptable. And under `Inhibit-Living` the front panel reads `On` while the output is 0 — the panel does not tell an operator the truth about the hazard.
>
> This remains a **control input on the instrument**. It is never a substitute for hardwired removal of hazardous energy that works with the PC and the instrument both powered off. Pins **2** and **3** are the interesting pair for software: level outputs that would make protection and output state *machine-observable* rather than inferred. Wiring any of this requires a reviewed schematic and the responsible engineer's decision.

### 5.2 LAN and remote interfaces — DOCUMENTED (SRC-10 §2.5)

| Item | Value |
|---|---|
| Default IP | **`192.168.200.100`** |
| Telnet port | **23** |
| Socket port | Configurable; must match on both ends |
| Max connections | **6** simultaneous socket + telnet, any combination |
| Termination | All commands and query responses terminated with a **newline** |
| Web server | `http://<ip>` — Home, Information, Web Control, Manual, **Upload (firmware upgrade)** |
| CAN | `H`=CAN_H, `L`=CAN_L, `GND`=CAN_GND; address 0–127; baud 5k–1000k; protocol `DeviceNet` or `BMS` |
| Self-test | `*TST?` → 0 pass, 1 fail |

> **F-PSU-04:** the web interface exposes a **firmware upload** page and the default IP is a published constant. Both belong in the network policy decision (OBS-006, T-10).

---

## 6. Review log

| Date | Register version | Reviewer | Scope reviewed | Outcome |
|---|---|---|---|---|
| — | initial draft | *(none)* | — | **No entry in this register is approved for hardware execution.** |

## 7. Change control

Any addition to this register must record: source document filename, document revision/date, exact model, exact firmware, page/section, verbatim syntax, response format, units, prerequisites, error conditions, reviewer name, review date, and bench-verification evidence. An entry missing any field stays `TRANSCRIBED` or `BLOCKED`.
