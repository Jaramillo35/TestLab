# P0-DOC-03 — Internet Research Findings

**Project:** Vehicle Harness Functional Tester
**Phase:** P0 — Requirements, documentation, and safety inputs
**Task ID:** P0-DOC-03
**Date:** 2026-09-08
**Purpose:** Close as many `P0-DOC-01` / `P0-DOC-02` open items as public manufacturer documentation allows, and record exactly where the remaining gaps are and how to close them.

---

## 0. Evidence tiers — read this before using anything below

This document mixes two very different grades of evidence. They are labelled on every finding and **must not be conflated**.

| Tier | Meaning | May it feed `command_register.md`? |
|---|---|---|
| **TIER-A — Primary, retrieved** | The manufacturer document was downloaded in full and read directly. The file is either committed to this repo or its SHA-256 is recorded here. | **Yes**, with page citations, at `TRANSCRIBED` status. |
| **TIER-B — Secondary, search-summary only** | The fact came from a web search result summary, a distributor listing, or a wiki. The primary document was **not** retrieved — the network egress policy blocked it. | **No. Never.** Leads and shopping lists only. |

The governing rule from `m365_copilot_agent_setup_for_harness_tester (1).md` is unchanged: *"Accept a hardware command only when the user provides an exact excerpt from the programming manual for the exact model/firmware."* A distributor page, a forum post, a wiki, or a search-engine summary is **not** a programming manual. No TIER-B item may become a command.

---

## 1. Headline result

**One of the three missing programming manuals was recovered in full.** The B&K Precision DAQ3120 is no longer blocked.

| Instrument | Before | After |
|---|---|---|
| B&K 2831E DMM ×2 | `TRANSCRIBED` | `TRANSCRIBED` + **USB driver and USB IDs now identified** |
| **B&K DAQ3120** | **`BLOCKED`** | **`TRANSCRIBED` — full 139-page SCPI manual retrieved and committed** |
| Tektronix TBS2104B | `BLOCKED` | `BLOCKED` — exact document identified, **download blocked by network policy** |
| ITECH IT-M3906B | `BLOCKED` | `BLOCKED` — exact document identified, **download blocked by network policy** |

**Why two are still blocked:** this session's egress proxy enforces a narrow domain allowlist. `bkpmedia.s3.*.amazonaws.com` (B&K's media bucket) is permitted; `download.tek.com`, `www.tek.com`, `cdn.itechate.com`, `www.itechate.com`, `manualslib.com` and every mirror tried are **denied at the proxy**. This is an environment limitation, not a documentation gap — §5 gives the exact URLs for a human to download in one minute each.

---

## 2. TIER-A — Documents retrieved and read

| Doc ID | Document | Source URL | Pages | SHA-256 (first 16) | In repo? |
|---|---|---|---:|---|---|
| SRC-07 | **DAQ3120 Series Programming Manual**, version stamp **January 7, 2026** | `https://bkpmedia.s3.us-west-1.amazonaws.com/downloads/programming_manuals/en-us/DAQ3120_Series_programming_manual.pdf` | 139 | `563c57bf11cae55a` | **Yes** — `AgentKnowledgeBase/manuals/` |
| SRC-08 | **DAQ3120 Series User Manual** | `https://bkpmedia.s3.us-west-1.amazonaws.com/downloads/manuals/en-us/DAQ3120_Series_manual.pdf` | 147 | *(134 MB — see note)* | **No** |
| SRC-09 | **B&K Bench Multimeter USB Drivers** (for 2831E / 5491B) | `https://bkpmedia.s3.amazonaws.com/downloads/software/Bench_Multimeter_USB_Drivers.zip` | — | *(3.7 MB zip)* | **No** |

> **SRC-08 is not committed** because it is **134 MB** — above GitHub's 100 MB file limit. Download it from the URL above; it is the source for §3.3 and §3.4.
> **SRC-09 is not committed** because it is a Windows driver installer; it should be distributed through the IT-approved channel, not a git repo.

---

## 3. TIER-A findings

### 3.1 DAQ3120 — command set recovered (SRC-07)

The full SCPI reference is now transcribed into `command_register.md` §3. Structure: 22 chapters covering common commands, `ABORt`/`INITiate`/`READ?`/`FETCh?`/`R?`, `CALCulate`, `CONFigure`, `DATA`, `DIGital`, `DISPlay`, `FORMat`, `HCOPy`, `MEASure`, `MMEMory`, `OUTPut`, **`ROUTe`**, `SENSe`, `SOURce`, `STATus`, `SYSTem`, `TRIGger`.

The five facts that most change the design:

**R-DAQ-01 — Channel addressing is `<slot><channel>`.**
`(@101)` = slot 1 channel 01. Lists support single `(@101)`, multiple `(@101,102,105)`, ranges `(@101:105)` and combinations `(@101:105,201)` (SRC-07 §3.3, p.18). Slot 1 → 1xx, slot 2 → 2xx, slot 3 → 3xx. **Computer (computed) channels are 401–420** (SRC-08 §5.6.1). `SYSTem:CTYPe? <slot>` (slot = 1..3) reports which module is installed — so the software can **verify the module configuration at connect time** instead of trusting a config file.

**R-DAQ-02 — `INSTrument:DMM OFF` turns the DAQ into a pure switch matrix.**
> *"Enables or disables the internal DMM. When disabled, the instrument acts as a switch, allowing external instruments to measure signals routed through the multiplexer modules."* (SRC-07 §6.4, p.29)

This is the missing architectural link between the DAQ and the two 2831E DMMs: the DAQ routes harness pins, the external DMMs measure. **Gotcha, stated in the manual:** *"Changing the state of the internal DMM triggers a Factory Reset (`*RST`)."* So this is a session-setup decision, never a mid-test toggle, and it silently discards the scan list and all configuration.

**R-DAQ-03 — `ROUTe:CLOSe:EXCLusive` is the safe switching primitive.**
`ROUTe:CLOSe (@…)` closes channels **without opening anything else** — on a harness fixture that is how two pins get shorted together by accident. `ROUTe:CLOSe:EXCLusive (@101)` *"Closes the specified channel and opens all other channels on the same bank (Break-Before-Make)"* (SRC-07 §17.2, p.74).
**Design rule for the route validator: default to `ROUTe:CLOSe:EXCLusive`. Plain `ROUTe:CLOSe` is a deliberate, reviewed, multi-point operation only, and must be checked against the forbidden-combination table before it is ever emitted.**
`ROUTe:DONE?` returns 1 when all relay operations are finished — use it to synchronize, never a fixed sleep.

**R-DAQ-04 — Resistance features that matter for milliohm harness measurement.**
- `[SENSe:]RESistance|FRESistance:OCOMpensated ON,(@…)` — offset compensation, *"to cancel thermal EMF"* (SRC-07 §18.8.4). Relevant: module thermal offset is <1–4 µV, and at 1 mA test current 1 µV ≈ 1 mΩ.
- `[SENSe:]RESistance|FRESistance:POWer:LIMit ON` — low-power mode *"to prevent self-heating"* (§18.8.5).
- `FRESistance` = 4-wire; `RESistance` = 2-wire. Datasheet already warned that 2-wire without null adds **2 Ω** of error.
- NPLC range **0.02 to 200** (§18.8.3) — far wider than the 2831E's 0.5–2.
- `[SENSe:]RESistance:ZERO:AUTO OFF|ON|ONCE` (§18.8.8).

**R-DAQ-05 — the DAQ has real status and error reporting, unlike the 2831E.**
`SYSTem:ERRor?` returns code + message and clears the queue (§21.1.9). Also `*ESR?`, `*STB?`, `*TST?` (returns 0 = pass), `*OPC`/`*OPC?`, `*WAI`, and a full `STATus:QUEStionable` / `STATus:OPERation` / `STATus:ALARm` tree (ch. 20). `*IDN?` returns `B&K Precision, DAQ3120, <Serial Number>, <Firmware Version>` (§5.4) — **serial and firmware are machine-readable**, so the identity check the project needs can be automated for this instrument.

Also worth noting: `SYSTem:LFRequency?` reports the detected line frequency (50/60 Hz) — the app should read it rather than assume, because every NPLC-based timing budget depends on it.

### 3.2 DAQ3120 — LAN and transport detail (SRC-07 ch. 21.2, SRC-08 ch. 18)

| Item | Value | Source |
|---|---|---|
| LAN config commands | `SYSTem:COMMunicate:LAN:` `DHCP`, `IPADdress`, `SMASk`, `GATeway`, `DNS`, `HOSTname`, `MAC?`, `DOMain?`, `WINS`, `UPDate`, `TIMeout` | SRC-07 §21.2 |
| Raw socket | `SYSTem:COMMunicate:LAN:TCP:ENABle`, `…:TCP:PORT` — manual's example uses **5025** | SRC-07 §21.2.10–11 |
| Telnet | `…:TELNet:ENABle` / `:PORT` (**default 5024**) / `:ECHO` / `:TIMeout` (0–3600 s) / `:PROMpt` (e.g. `"DAQ>"`) | SRC-07 §21.2.12–17 |
| Web interface | `SYSTem:COMMunicate:LAN:WEB:ENABle` — **can be disabled from software** | SRC-07 §21.2.20 |
| Ethernet speed | 10BaseT / 100BaseTx | SRC-08 §18.4 |
| USB device port | Selectable **TMC or CDC** from the front panel (`INTERFACE CONFIGURATION` menu). CDC = virtual COM port; TMC = NI-VISA | SRC-08 §18.2.1 |
| USB speed | USB 2.0 **full speed**; unit side = rear panel Type B | SRC-08 Table 18.1 |
| GPIB | Address 0–30, **default 15** | SRC-08 Table 18.2 |
| NTP | `TIME:SYNC:SERVer "time.nist.gov"` | SRC-07 §6.7 |

> **Security note for the IT review (OBS-006):** Telnet and the web interface are both enabled/disabled by SCPI. On a production test station both should be **off** unless there is a documented reason, and the decision recorded. The DAQ also accepts an NTP server — decide whether the station is allowed to reach one.

### 3.3 DAQ3120 — digital I/O pinout recovered (SRC-08 ch. 15) — new safety-relevant interface

Connector: **DB-9 female**, rear panel.

| Pin | Definition | Description |
|---:|---|---|
| 1 | `Alarm_OUT1` | TTL-compatible. Selectable TTL logic Hi or Lo alarm output |
| 2 | `Alarm_OUT2` | TTL-compatible. Selectable Hi or Lo |
| 3 | `Alarm_OUT3` | TTL-compatible. Selectable Hi or Lo |
| 4 | `Alarm_OUT4` | TTL-compatible. Selectable Hi or Lo |
| 5 | `EOM` (End of Measurement) Out | Activates when a compare measurement is completed; also available in other measurements |
| 6 | `External Trigger In` | Accepts external trigger signals. **Pulse ≥ 10 µs required** |
| 7 | `Digital Ground` | Chassis ground for digital circuits |
| 8 | NC | Not connected |
| 9 | NC | Not connected |

Alarm limits are per channel, modes `OFF | High+Low | High | Low`, and any of the 4 outputs can be assigned to any input channel. Software equivalents: `CALCulate:LIMit:UPPer/:LOWer/:STATe` (per channel, SRC-07 §7.7–7.9) and `OUTPut:ALARm:MODE / :SLOPe / :CLEar` (§16), with `STATus:ALARm:CONDition?` to read state.

> **This is a candidate contribution to the safety architecture (COM-008), and it is genuinely useful — but read the limits carefully.** These are **TTL signalling** pins, not a safety-rated interface. They may drive an indicator, feed a PLC input, or let external hardware trigger a scan. They are **not** an interlock, **not** rated for safety functions, and must never be presented as proof that hazardous energy is removed. Whether they play any part at all is the responsible engineer's decision.

### 3.4 DAQ3120 — the module lineup is larger than the datasheet says (SRC-08 Table 3.4)

The datasheet in this repo lists **five** modules. The user manual lists **seven**:

| Module | Input type | Ch | Speed | Max V | Max I | Internal DMM |
|---|---|---:|---:|---|---|---|
| DM300 | 2-wire solid-state (4-wire selectable) | 20 | 450 ch/s | 120 V | — | ✓ |
| DM301 | 2-wire armature (4-wire selectable) | 20 + 2 current | 80 ch/s | 300 V | 1 A | ✓ |
| DM303 | 1-wire armature (common low) | 40 | 80 ch/s | 300 V | — | ✓ |
| DM304 | 2-wire armature, 4×8 matrix | 32 | — | 300 V | — | **✗** |
| **DM307** *(new)* | **Multifunction:** 16-bit digital I/O (two 8-bit registers), 100 kHz totalizer input ×1, **18-bit DAC output ×2** | 16 / 1 / 2 | — | 42 V (DIO & totalizer), **±12 V DAC** | **±24 mA DAC** | ✗ |
| **DM308** *(new)* | **Actuator / general-purpose switch, SPDT Form C relay** | 20 | — | 300 V | — | ✗ |
| DM309 | 2-wire armature (4-wire selectable) | 8 + 2 current | 60 ch/s | 600 VDC / 400 VAC | 2 A | ✓ |

**Why this matters for the harness fixture:**
- **DM308** is a 20-channel **Form C actuator relay** module — the natural way to *actuate* a fixture (energize a load, switch a path, drive a contactor coil) rather than merely measure it. Nothing in `P0-DOC-01` considered it.
- **DM307** provides 2 analog outputs (±12 V, ±24 mA) and 16 digital I/O — a stimulus source for harness circuits that need one.
- Supported-function table confirms: **DM300 does not support current, RTD, thermistor or capacitance**; **DM303 has no 4-wire and no current**; **DM309 thermocouples require an external cold junction and manual reference setting**.

This widens the module-selection question in finding F-DAQ-01. The physical module list (T-08) is now even more clearly the gating item.

### 3.5 B&K 2831E — USB driver identified from B&K's own driver package (SRC-09)

Contents of `Bench_Multimeter_USB_Drivers.zip`: `CP210x_VCP_Windows/` — the **Silicon Labs CP210x USB-to-UART Bridge VCP driver**.

Read directly from `slabvcp.inf`:

| Item | Value |
|---|---|
| Bridge chip | **Silicon Labs CP210x USB to UART Bridge** |
| USB VID | **`0x10C4`** |
| USB PID | **`0xEA60`** (single-port CP210x) |
| Also in .inf | `0xEA70` + `Mi_00`/`Mi_01` (dual-port CP210x variants) |
| Driver version | **6.6.0.0, dated 2012-10-05** |
| Stated OS support | Windows XP / 2003 / Vista / 7 / 8 (32 & 64-bit) |

**Three consequences for the application:**

1. **The bundled driver is from 2012 and predates Windows 10/11.** Do not plan on shipping this zip. Obtain the current CP210x VCP driver from Silicon Labs (or a newer B&K package) and record the version actually installed. This is an IT/deployment action item, not a coding one.
2. **Enumerate by `VID_10C4 & PID_EA60` + serial number.** OBS-007 required mapping each DMM by serial rather than COM-port order. On Windows, `pyserial`'s `comports()` exposes `vid`, `pid`, and `serial_number` — so the mapping the project needs is achievable with the standard library the plan already specifies. **No COM-port number should ever be hard-coded.**
3. **CP210x devices frequently share the same factory serial string.** Two identical 2831E meters may enumerate with indistinguishable serials. Verify this on the bench with both meters connected; if the serials collide, the mapping must fall back to a documented physical-port binding, and that binding becomes a commissioning checklist item. **Do not assume the serials are unique until it is tested.**

---

## 4. TIER-B findings — leads only, NOT usable as command or design authority

Everything in this section came from search-result summaries or distributor pages. The primary documents were blocked. **Verify each against the manufacturer document before acting.**

### 4.1 CORRECTION to `P0-DOC-02` §6.5 / finding F-PSU-02 — "IT-E151" may be a real part

`P0-DOC-02` asserted that *"IT-E151 does not appear"* in ITECH's catalogue and was probably a mis-transcription of `IT-E155A/B/C`. **That was too confident and is partly wrong.**

Search results show **both** parts exist:

| Part | Vendor listing | Apparent purpose |
|---|---|---|
| `IT-E151` | listed by DigiKey **under B&K Precision** | rack mount kit |
| `IT-E151A` | listed by DigiKey under ITECH Electronic | rack mount kit, associated with **IT6900A / IT6300 / IT6700 / IT8500+** series |
| `IT-E155A` | 4Test / Altoo listings | rack mount kit for **IT-M3900B/C/D, IT-M3800, IT-M7723 1U** models — mounts the **front** |
| `IT-E155B` | 4Test / Altoo listings | **rear** mount for the same 1U models — **requires IT-E155A** |
| `IT-E155C` | Altoo listing | **side** mount for the same 1U models — **requires IT-E155A** |

**Revised reading — and it is a more useful finding than the original.** B&K Precision resells ITECH hardware under B&K part numbers, so *"B&K IT-E151 Rack Kit"* on drawing S1 is plausibly a genuine label. But `IT-E151/IT-E151A` is associated with the **IT6900/IT6300/IT6700/IT8500+** families, whereas the **IT-M3900B 1U** models take **`IT-E155A`** (plus `B` or `C` if the cabinet has no tray).

**So the actionable question is no longer "is the label a typo?" but "is the correct rack kit fitted?"** If an IT-E151 is installed on the IT-M3906B, it is likely the **wrong kit for this chassis** — a mechanical mounting concern on a 1U, ~6 kW, air-cooled unit that must be raised with the responsible engineer. Photograph the part number and check it against ITECH's rack-kit selection guide.

*Sources: DigiKey product listings for `IT-E151` (B&K Precision) and `IT-E151A` (ITECH); 4Test/Altoo listings for `IT-E155A/B/C`; "ITECH Rack Mount Kits Selection Guide".*

### 4.2 CORRECTION to `P0-DOC-02` §5.3–5.5 / finding F-TCPA-02 — the TPA-BNC adapter is probably NOT needed

`P0-DOC-02` listed `TPA-BNC` as **required**. Two independent search-level facts say otherwise:

- **TekWiki, "TekVPI connector":** the TekVPI connector *"consists of a plain BNC connector that allows traditional BNC based connections such as from passive probes, with additional surrounding contact pads carrying power and data."*
- **Tektronix TPA-BNC material:** probe types using a plain BNC connection *"connect directly to the oscilloscope's TekVPI probe interface and do not require a TPA-BNC adapter."* TPA-BNC exists to give **TekProbe-BNC** products their power/serial/offset communication.
- Distributor listings for TPA-BNC name DPO2000/3000/4000, MSO2000/3000/4000, DPO7000 as compatible instruments. **TBS2000 is not on that list.**

Since `P0-DOC-02` §5.3 already established that this scope will **not** auto-scale with a TCPA300/400 anyway, the TekProbe-II communication the adapter provides buys nothing here.

**Revised recommendation:** connect the TCPA400 BNC output → 50 Ω feedthrough → **directly into a TekVPI input with a plain 50 Ω BNC cable**. Treat `TPA-BNC` as *not required*, pending confirmation from the TCPA300/400 user manual and the TBS2000B user manual. Remove it from the must-buy list; keep it on the verify list.

### 4.3 REFINEMENT to F-TCPA-02 — the 50 Ω feedthrough ships with the amplifier

Search summaries of the **TCPA300/400 Amplifiers user manual** (Tektronix `077-1183-02`) indicate:

- If the oscilloscope has no switchable 50 Ω input, a **feedthrough 50 Ω termination is required** — and it *"is included as a standard accessory with your TCPA300 and TCPA400 Current Probe Amplifiers."*
- **`NOT TERMINATED INTO 50 Ω` is only detected during the DEGAUSS/AUTOBALANCE operation.**

**Two consequences.** First, the terminator is probably already in the rack's accessory kit rather than something to buy — look for it before ordering `011-0049-02`. Second, and more important: because the termination fault is only detected at degauss, **a degauss/autobalance must be part of the documented pre-test operator procedure**, otherwise a missing terminator produces a roughly 2× amplitude error that the instrument never flags and the software cannot see.

### 4.4 ITECH IT-M3900 series — LAN and P-IO leads (UNVERIFIED)

| Item | Search-level indication | Status |
|---|---|---|
| LAN socket port | **30000** for `TCPIP::…::INSTR`, per IT-M3900**D** user manual | **UNVERIFIED — different series variant** |
| LAN services | MDNS, PING, Telnet-SCPI, Web, VXI-11, Raw Socket — individually configurable | **UNVERIFIED** |
| P-IO pin functions | IO-1 `Ps-Clear`, IO-2 `Ps`, IO-3 `Off-Status`, IO-4 `Trig(in)`, IO-5 `INH-Living`, IO-6 `Sync-On`, IO-7 `Sync-Off` — all "Not-Invert" by default, per IT-M3900**D** manual | **UNVERIFIED — DO NOT WIRE ANYTHING FROM THIS** |

> **Explicit warning.** The P-IO pin list above came from a **search-engine summary of the IT-M3900D manual**, not the IT-M3900**B** manual, and not from a document anyone in this project has read. `IO-5 INH-Living` looks like an inhibit input and is exactly the pin the safety discussion (COM-008) needs — which is precisely why it must not be trusted at this grade of evidence. **Wiring a 6 kW bidirectional supply's inhibit line from a search summary is not acceptable.** Treat this only as confirmation that a P-IO inhibit function plausibly exists, and get the real IT-M3900B manual before anyone touches the connector.

### 4.5 Tektronix TBS2000B remote-control leads (UNVERIFIED)

- Remote control is available via **e*Scope** (built-in web server, browse to the scope's IP) and via **VXI-11**; a password can be set on the web/VXI control panel.
- TekVISA supports both VXI-11 and raw socket connections; PyVISA addresses Tektronix scopes over LAN as `TCPIP0::<ip>::inst0::INSTR`.
- Tektronix instruments commonly need generous VISA timeouts (~10 s) — relevant to the timeout characterization the plan requires.
- **No raw socket port number was confirmed for the TBS2000B.** Get it from the user manual.

---

## 5. What a human must download — exact URLs

Two documents remain blocked by this environment's egress policy. Each takes about a minute to fetch from a normal browser. Save them into `AgentKnowledgeBase/manuals/` and register them in `command_register.md`.

| # | Document | URL | Unblocks |
|---|---|---|---|
| 1 | **Tektronix TBS2000B Series Programmer Manual** | `https://www.tek.com/en/manual/oscilloscope/tbs2000b-series-programmer-manual-tbs2000` | All oscilloscope commands (T-02) |
| 1b | *Fallback* — TBS2000 (non-B) Programmer `077-1149-02` | `https://download.tek.com/manual/TBS2000-Programmer-077114902.pdf` | **Non-B series — verify applicability before relying on it** |
| 2 | **ITECH IT-M3900B Series Programming Guide (EN)** | `https://cdn.itechate.com/uploadfiles/用户手册/user manual/it-m3900b/IT-M3900B Programming Guide-EN.pdf` | All power-supply commands (T-03) |
| 3 | **ITECH IT-M3900B Series User Manual** | `https://www.altoo.dk/files/itech/manuals/IT-M3900B-User-Manual.pdf` | **P-IO pinout** and LAN settings (T-03, COM-008) |
| 4 | **Tektronix TCPA300/400 Amplifiers & TCP300A/400 Probes User Manual** (`077-1183-02`) | `https://download.tek.com/manual/TCPA300-400-Amplifiers-and-TCP300A-400-Current-Probe-User-Manual-077118302.pdf` | Degauss procedure, termination, accessory list (T-09) |
| 5 | **TBS2000B Series User Manual** (`077-1525-01`) | `https://www.tek.com/en/oscilloscope/tbs2000-basic-oscilloscope-manual-077152501/tbs2000b-series-oscilloscope` | Scope LAN/socket config, probe menu |
| 6 | **DAQ3120 Series User Manual** — retrieved and read, **too large to commit (134 MB)** | `https://bkpmedia.s3.us-west-1.amazonaws.com/downloads/manuals/en-us/DAQ3120_Series_manual.pdf` | Already mined for §3.3, §3.4 |
| 7 | **Current CP210x VCP driver** (replace the 2012 one) | Silicon Labs CP210x VCP downloads | Windows 10/11 support for the DMMs |
| 8 | *Optional* — ITECH Rack Mount Kits Selection Guide | `https://www.4test.no/files/itech/catalog/ITECH-Rack-Mount-Kits-Selection-Guide.pdf` | Settles the IT-E151 vs IT-E155 question (§4.1) |

---

## 6. Updated status of every open item

| Item | Before research | After research |
|---|---|---|
| **T-01 DAQ3120 programming manual** | MISSING | ✅ **RETRIEVED, committed, transcribed** |
| T-02 Tektronix programmer manual | MISSING | URL identified; **download blocked here** — §5 #1 |
| T-03 ITECH manual + P-IO pinout | MISSING | URLs identified; **download blocked here** — §5 #2, #3. Unverified pin list in §4.4 |
| T-04 Fixture schematic / pin map | MISSING | Unchanged — **only a human can supply this** |
| T-05 Safety-panel schematics | MISSING | Unchanged. DAQ DB-9 (§3.3) is a *signalling* candidate only |
| T-06 Approved ceilings | MISSING | Unchanged — engineering decision, not a research item |
| T-07 Nameplates / serial / firmware | MISSING | DAQ3120 serial + firmware now **machine-readable** via `*IDN?` (§3.1) |
| T-08 DAQ module + slot list | MISSING | `SYSTem:CTYPe? <slot>` can read it **once connected**; module catalogue expanded to 7 (§3.4) |
| T-09 Current chain | OPEN | Advanced: TPA-BNC likely unnecessary (§4.2); terminator likely already supplied (§4.3) |
| T-10 Network / IP plan | OPEN | DAQ LAN + Telnet + web are SCPI-configurable (§3.2); disable-by-default recommended |
| T-11 Production transport per instrument | OPEN | DAQ options fully documented; decision still owed |
| OBS-002 IT-E151 | "probably a typo" | **Corrected** — likely a real part, possibly the **wrong kit** for this chassis (§4.1) |
| OBS-007 DMM USB mode | closed | Strengthened — CP210x, VID `10C4` / PID `EA60`, enumerate by serial (§3.5) |

---

## 7. New findings raised by this research

| ID | Finding |
|---|---|
| **R-DAQ-01** | Channel addressing `(@<slot><ch>)`; computed channels 401–420; `SYSTem:CTYPe?` verifies modules at connect time |
| **R-DAQ-02** | `INSTrument:DMM OFF` makes the DAQ a pure switch for the external DMMs — **and forces a factory reset when toggled** |
| **R-DAQ-03** | `ROUTe:CLOSe:EXCLusive` (break-before-make) must be the default; plain `ROUTe:CLOSe` can short fixture points |
| **R-DAQ-04** | `OCOMpensated` and `POWer:LIMit` are needed for credible milliohm harness resistance |
| **R-DAQ-05** | DAQ has full error/status reporting and machine-readable serial + firmware — unlike the 2831E |
| **R-DAQ-06** | Module lineup is 7, not 5; **DM308** (Form C actuator) and **DM307** (DAC + digital I/O) were previously unknown |
| **R-DAQ-07** | DB-9 digital I/O pinout recovered: 4 alarm outs, EOM out, ext trigger in (≥10 µs), digital ground. **TTL signalling, not safety-rated** |
| **R-DMM-01** | 2831E USB bridge is CP210x, VID `0x10C4` / PID `0xEA60`; bundled driver is 2012-era and predates Win10/11 |
| **R-DMM-02** | CP210x serials may collide between two identical meters — **test before relying on serial-based mapping** |
| **R-TCPA-01** | TPA-BNC adapter is **probably not required** (TekVPI accepts plain BNC); TBS2000 is not on its compatibility list |
| **R-TCPA-02** | 50 Ω feedthrough ships **with** the amplifier; termination fault is detected **only during degauss/autobalance** — so degauss must be a mandatory pre-test step |
| **R-PSU-01** | `IT-E151` appears to be a real B&K/ITECH part, but for the **IT6900/IT8500+** families — the IT-M3900B 1U takes `IT-E155A` (+B or C). Possible wrong-kit issue |

---

## 8. Acceptance criteria for P0-DOC-03

**Status: PARTIAL — one of three manuals recovered; two blocked by environment, not by availability.**

P0-DOC-03 may be marked PASS when:

1. The documents in §5 rows 1–5 are downloaded, registered with revision and date, and stored in `AgentKnowledgeBase/manuals/`.
2. Every TIER-B item in §4 is either confirmed against its primary document or struck.
3. The IT-E151 vs IT-E155 question (§4.1) is settled by photographing the installed part.
4. The current-chain BOM is re-checked against §4.2 and §4.3 before anything is purchased.
5. The CP210x serial-collision test (§3.5, R-DMM-02) is run with both meters connected.

No hardware command, switching action, or power-output action is authorized by this document. The DAQ3120 entries in `command_register.md` are `TRANSCRIBED`, **not** `APPROVED`.
