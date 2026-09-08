# P0-DOC-04 — Extract of the Uploaded Manuals

**Project:** Vehicle Harness Functional Tester
**Phase:** P0 — Requirements, documentation, and safety inputs
**Task ID:** P0-DOC-04
**Date:** 2026-09-08
**Evidence tier:** **TIER-A throughout** — every document below was retrieved in full and read directly. Contrast with `P0-DOC-03` §4, which is search-summary material.

---

## 1. What arrived

Five PDFs were committed to `AgentKnowledgeBase/manuals/` on 2026-09-08.

| Doc ID | File | Pages | What it is |
|---|---|---:|---|
| SRC-10 | `IT-M3900B-User-Manual.pdf` | **348** | ITECH IT-M3900B Series **User Manual** — operation, interfaces, **P-IO pinout** |
| SRC-11 | `TBS2000-Programmer-077114902.pdf` | **342** | Tektronix **TBS2000 Series** Programmer, `077-1149-02` Rev A — **non-B series** |
| SRC-12 | `TCPA300-400-…-User-Manual-077118302.pdf` | 82 | Tektronix TCPA300/400 Amplifiers & TCP300A/400 Probes User Manual |
| SRC-13 | `ITECH-Rack-Mount-Kits-Selection-Guide.pdf` | 8 | ITECH rack mount kit selection guide |
| SRC-14 | `itech-it-m3900b-pv3900-software-user-manual.pdf` | 107 | ITECH **PV3900 PC software** user manual |

## 2. What did NOT arrive — read this before assuming the supply is unblocked

**The ITECH IT-M3900B Series *Programming Guide* is still missing.** SRC-14 is the **PV3900 PC software** manual, which is a different document — it contains **zero** SCPI commands (verified by search across all 107 pages).

SRC-10 confirms the Programming Guide is a separate publication. Quoting the user manual directly (p.73):

> "Programming via SCPI instructions — For detailed instructions and parameter introduction, please refer to the instructions of **"ARB Subsystem" in the Programming Guide**."

**The ITECH IT-M3906B therefore remains `BLOCKED` for every command.** What SRC-10 *does* unblock is the P-IO hardware interface and the LAN configuration — see §3. That is genuinely valuable, and it is not the same as being able to command the supply.

Still needed: `https://cdn.itechate.com/uploadfiles/%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C/user%20manual/it-m3900b/IT-M3900B%20Programming%20Guide-EN.pdf`

---

## 3. ITECH IT-M3900B — P-IO digital interface (SRC-10 §6.11, pp.189–204)

This closes the largest open safety question in `P0-DOC-01` (COM-008) at the *information* level. It does not close it at the *engineering* level — that still needs a reviewed schematic and a responsible engineer.

### 3.1 Pin assignment — VERIFIED PRIMARY SOURCE

| Pin | Type | Default function | Signal |
|---:|---|---|---|
| 1 | Input/Output | `Ps-Fault-Clear` — clear the protection state | **Pulse** |
| 2 | Input/Output | `Ps` — protection state indicator | Level |
| 3 | Input/Output | `Off-Status` — On/Off status indicator | Level |
| 4 | Input/Output | `Trig(in)` — trigger signal | **Pulse** |
| 5 | Input/Output | **`INH-Living` — turn off the output under emergency status** | **Pulse** |
| 6 | Input/Output | `Sync-On` — synchronous on control | **Pulse** |
| 7 | Input/Output | `Sync-Off` — synchronous off control | **Pulse** |
| GND | — | Ground terminal, the negative terminal corresponding to each of the above 7 pins | Level |

> The unverified list in `P0-DOC-03` §4.4 was **substantially correct**, and is now superseded by this verified table. It was right to refuse to act on it until now.

**Electrical characteristics (SRC-10 p.190):**

| | |
|---|---|
| Input high | Typical 5 V, range **1.6 V – 15 V**, current ≤100 mA |
| Input low | Typical 0 V, range **−5 V – 0.8 V**, current ≤100 mA |
| Output high / low | 5 V / 0 V |
| Pulse rise slope | 10 µs |
| Pulse fall slope | 2 µs |
| Pulse width | 30 µs |
| Minimum low-level hold | 30 µs |

All pulse signals in the digital I/O function are **switched from high level to low level**. Every pin can be re-purposed as generic `Input` or `Output` (including PWM out), and each has an `Invert` / `Not-Invert` setting.

### 3.2 F-PSU-03 — the two inhibit modes are NOT equivalent, and the default is the wrong one for a safety tie-in

Pin 5 can be set to `Inhibit`, `Input` or `Output`. Under `Inhibit` there are two sub-modes, and the difference is decisive:

**`Inhibit-Living` (the default), SRC-10 p.201–202 — level controlled, AUTO-RECOVERING:**
- Pin unconnected → input reads high → no effect on output.
- With `[On/Off]` on, drive pin 5 **low** → *"The `[On/Off]` button light is lighted on and VFD still displays On, but the actual output is 0"*; the VFD shows `INH`.
- *"when pin 5 receives high level signal again, **the output state is recovered**."*

**`Inhibit-Latch`, SRC-10 p.202–203 — pulse controlled, LATCHING:**
- Apply a pulse to pin 5 → `[On/Off]` is **turned off**, button light off, VFD displays `Off` and `Inhibit-Ps`.
- *"After confirming that the `[On/Off]` can be turned on again, the user needs to **manually turn on `[On/Off]`**."*

**Why this matters, and it is not a subtlety:**

1. **`Inhibit-Living` auto-recovers the instant the inhibit signal is released.** A 240 A output that re-energizes by itself when a contact closes again is not acceptable behaviour for an E-stop or interlock path. Only `Inhibit-Latch` requires a deliberate human action to restore output.
2. **`Inhibit-Living` is the factory default.** Out of the box, this instrument is in the auto-recovering mode.
3. **Under `Inhibit-Living` the front panel lies about state in a specific way:** the `[On/Off]` light stays lit and the VFD still says `On` while the actual output is 0. An operator glancing at the panel sees "On". Conversely, someone who inhibits the output and walks away has not made the station safe — it will come back.

**Recommendation to the responsible engineer (not a decision this document may make):** if P-IO pin 5 is used at all in the safety chain, it should be configured `Inhibit → Latch`, and the configuration must be verified after every firmware update or factory reset. And it remains a **control input on the instrument** — never a substitute for hardwired removal of hazardous energy that works with the PC and the instrument both powered off.

### 3.3 Other P-IO functions worth recording

- **Pin 1 `Ps-Fault-Clear`** — a pulse clears the protection state. Referenced twice more in SRC-10 (pp. ~2383, ~4996) as the documented way to clear protection remotely. Anything that can clear a protection latch belongs in the safety review.
- **Pin 2 `Ps`** — protection state indicator, a level output. This is a **machine-observable protection signal**, if wired to a DAQ digital input.
- **Pin 3 `Off-Status`** — On/Off status indicator, level output. Also machine-observable.
- **Pin 4 `Trig(in)`** — external trigger; SRC-10 notes it connects to *"pin 4 of the digital I/O interface (P-IO) and set pin 4 to `Ext-Trig`"*.
- **Pins 6/7 `Sync-On` / `Sync-Off`** — synchronous on/off control across units.

> Pins 2 and 3 are the interesting pair for software: they would let the application *observe* protection and output state over hardware rather than inferring it. That is exactly the kind of independent feedback `P0-DOC-01` COM-008 asks for. It needs a schematic and a decision, not an assumption.

### 3.4 ITECH LAN and remote interfaces (SRC-10 §2.5)

| Item | Value |
|---|---|
| **Default IP address** | **`192.168.200.100`** |
| Web server | Built-in; browse to `http://<ip>`. Pages: Home, Information, Web Control, Manual, **Upload (firmware upgrade)** |
| Telnet port | **23** |
| Socket port | Configurable; instrument and PC must match |
| Max connections | *"any combination of up to **six** simultaneous socket and telnet connections"* |
| Message termination | *"All commands must be terminated with a **newline**… All query responses will also be terminated with a newline."* |
| CAN pins | `H` = CAN_H, `L` = CAN_L, `GND` = CAN_GND |
| CAN address / baud | 0–127; 5k…1000k |
| CAN protocol | `DeviceNet` (standard CAN) or `BMS` |
| Self-test | `*TST?` — 0 = pass, 1 = fail (SRC-10 p.~12212) |

> **Two security items for the IT review (OBS-006, T-10).** The web interface exposes a **firmware upload** page — on a station controlling 6 kW that is a meaningful attack surface, and the default IP is a well-known constant. Both belong in the network policy decision.

---

## 4. Tektronix TBS2000 Programmer `077-1149-02` — PROVISIONAL, wrong series

### 4.1 The applicability problem, stated plainly

SRC-11 is titled **"TBS2000 Series Digital Oscilloscopes Programmer"**. Our instrument is a **TBS2104B**, a TBS2000**B** series unit. Tektronix publishes a **separate** TBS2000B programmer manual — the one requested in `P0-DOC-03` §5 #1 — and the existence of a separate publication is itself evidence that the two differ.

Model strings appearing in SRC-11: `TBS2000` ×348, `TBS2104` ×3, `TBS2102` ×2, `TBS2000B` ×1.

The single `TBS2000B` mention is a genuine B-series accommodation (p.168, `*IDN?` returns a different format for TBS2000B instruments), which shows this revision is *aware* of the B series. It is not a statement that the manual covers it.

### 4.2 F-SCOPE-01 — a concrete, material difference proving the manual must not be used verbatim

SRC-11 p.34 and p.53 state:

> *"Setting `DATa:STARt` to 1 and `DATa:STOP` to **2500** always sends the entire waveform, regardless of the acquisition mode."*
> *"The instrument stores waveforms that are **≤2500 data points** long. The instrument **truncates** waveforms longer than 2500 data points."*

**The TBS2104B has a 5 M point record length** (`P0-DOC-02` §4.2, from the datasheet). 2500 points is **0.05%** of that.

A driver written from SRC-11 that hard-codes `DATa:STOP 2500` would return a plausible-looking waveform that silently discards 99.95% of the acquisition. No error, no exception, no flag — just wrong data that passes every test you thought to write. This is precisely the failure mode `command_register.md` §4 warned about when it said a wrong preamble assumption *"produces plausible but wrong numbers, which is worse than an error."*

**Conclusion:** SRC-11 is registered as **`TRANSCRIBED-PROVISIONAL`**, not `TRANSCRIBED`.

- **Permitted:** using it to design and unit-test the *simulated* oscilloscope driver in Phase 1, where nothing touches hardware.
- **Forbidden:** using any command from it in Real mode; hard-coding any record-length, preamble, or scaling constant taken from it; treating any of it as verified for the TBS2104B.
- Every command must be re-verified against the TBS2000B programmer manual before Phase 2, and `DATa:STOP` / record-length handling must be re-derived, never carried over.

### 4.3 What SRC-11 does establish (provisionally)

**Command groups:** Acquisition, Alias, Bus, Calibration, Cursor, Display, Ethernet, File System, Hard Copy, Horizontal, Math, Measurement, Miscellaneous, Save and Recall, Status and Error, Trigger, Vertical, **Waveform**, Zoom.

**Core commands relevant to this project:**

| Command | Purpose |
|---|---|
| `*IDN?` | `TEKTRONIX,<model>,<serial>,CF:91.1CT FV:v<fw>` — and a **different format on TBS2000B** (adds `TBS2XXXV:v<module fw>`) |
| `ACQuire:STATE` | Start/stop acquisitions |
| `ACQuire:STOPAfter` | When to stop acquiring |
| `ACQuire:MODe` | SAMple / PEAKdetect / AVErage / HIRes |
| `ACQuire:NUMAVg` | Averaging count |
| `SELect:CH<x>` | Turn a channel's display on/off |
| `MEASUrement:IMMed:VALue?` | Immediate measurement result |
| `CURVe` / `CURVe?` | Transfer waveform data, binary or ASCII |
| `DATa:SOUrce` | Which waveform to transfer |
| `DATa:STARt` / `DATa:STOP` | First/last data point — **see F-SCOPE-01** |
| `DATa:WIDth` | Bytes per data point |
| `DATa:ENCdg` | `ASCII` \| `RIBinary` \| `RPBinary` \| `SRIbinary` \| `SRPbinary` |
| `WAVFrm?` | Returns `WFMPre?` + `CURVe?` together |
| `WFMPre:` / `WFMInpre:` | Waveform preamble — scaling, `XINcr`, `BIT_Nr`, `BYT_Nr`, `NR_Pt?` |
| `BUSY?` | Instrument status |
| `*OPC` / `*WAI` | Synchronization |

**Waveform data encoding (provisional):** internally 8 bits per point regardless of acquisition mode. `DATa:WIDth 2` multiplies each point by 256 on send and truncates on receive. Binary ranges: 1 byte signed −128…127 / unsigned 0…255; 2 byte signed −32768…32767 / unsigned 0…65535. `RIBinary`/`RPBinary` are MSB-first; `SRIbinary`/`SRPbinary` are LSB-first; byte order is ignored when `DATa:WIDth` is 1.

**Socket server:** enabled from the front panel under `Utility → Config → Socket Server`, with a settable port and a `None` / `Terminal` protocol choice. **No default port number is stated** — read it off the instrument.

---

## 5. Tektronix TCPA300/400 user manual — the current chain, confirmed

Everything `P0-DOC-03` §4.3 flagged from search summaries is now confirmed from the primary source, plus two new operational requirements.

### 5.1 Termination — confirmed, with a placement rule

> *"If the oscilloscope does not have an input that can be set to 50 Ω impedance, you need a feedthrough 50 Ω termination. **This termination is included as a standard accessory** with your TCPA300 and TCPA400 Current Probe Amplifiers."* (SRC-12 p.2)

> *"The input impedance of the oscilloscope channel must be 50 Ω, or you will encounter **slowed pulse response, increased aberrations, or incorrect DC measurement amplitudes**. If your oscilloscope provides only 1 MΩ inputs, you need to attach a 50 Ω feed-through termination between the oscilloscope input and the BNC cable. **Do not install this termination at the amplifier end of the BNC cable.**"* (SRC-12 p.~586)

**New actionable detail:** the terminator goes at the **oscilloscope end**, not the amplifier end. The TBS2104B is 1 MΩ-only, so this applies directly. Look in the amplifier's accessory kit before ordering `011-0049-02` (T-18).

### 5.2 Degauss — now a documented, mandatory procedure

> *"**Failure to degauss the probe is a leading cause of measurement errors.** The DEGAUSS LED flashes until you degauss the probe."* (SRC-12 p.~671)

Degauss is required in **all** of these cases:
- After turning on the amplifier and allowing a **20-minute warm-up**.
- **Before connecting the probe to a conductor.**
- Whenever a current or thermal overload occurs.
- Whenever a new probe is connected.
- Whenever the probe is subjected to a strong external magnetic field.
- **Periodically during normal use.**

Procedure: disconnect the probe from the test circuit **or ensure the conductor under test has no power**, close and lock the slide, press `PROBE DEGAUSS AUTOBALANCE`.

### 5.3 Two safety facts new to this project

**F-TCPA-03 — the probe slide must be locked, and it is not machine-readable.**
> *"The slide must be locked closed to accurately measure current or to degauss the probe. If a probe is unlocked, the `PROBE OPEN` indicator on the amplifier will light."*

An unlocked probe gives wrong readings and signals only via a front-panel LED. The software cannot see it. Operator checklist item.

**F-TCPA-04 — the circuit must be de-energized to fit or remove the probe on uninsulated wire.**
> *"The current probes can be used to measure current on uninsulated wires. However, **the circuit must be de-energized when connecting or removing the current probe**."*

This belongs in the written commissioning and operating procedure for a 240 A DC bus.

### 5.4 Bandwidth rule

> *"To utilize the full bandwidth capability… the oscilloscope bandwidth must be approximately **five times** that of the current probe."*

TCP404XL is DC–2 MHz → ~10 MHz of scope bandwidth needed. The TBS2104B is 100 MHz. **Comfortably satisfied** — the probe, not the scope, is the bandwidth limit, as `P0-DOC-02` §5.2 already stated.

---

## 6. Rack kit question — CLOSED, and the answer is "wrong kit"

SRC-13, ITECH's own selection guide, settles OBS-002 / T-15 definitively.

| Kit | What it is for |
|---|---|
| **`IT-E151`** | *"Mounts **half-rack-width 2U-high** instruments in **3U-high** rack space. 3U (5.25 in.) high."* Compatible models: **IT-M3100, IT-M3100D, IT-M3200, IT-M3300, IT-M3400, IT-M3600** |
| `IT-E151A` | Same but mounts half-rack-width 2U instruments in 2U rack space |
| **`IT-E155` series** | *"For **full-rack** models. **1U** (1.75 in.) high."* Compatible: **IT-M3900B/C/D (1U)**, IT-M3800 (1U), IT-M7723 |

And the guide is explicit about what the IT-M3900B needs:

> *"IT-M3900B/C/D (1U), IT-M3800 (1U) and IT-M7723 — Without mounting handle IT-E155A, thus **IT-E155A is mandatory**. If the rack has no tray, you can purchase the combination of IT-E155A+IT-E155B or IT-E155A+IT-E155C."*
> *"IT-M3900B/C/D (1U), IT-M3800 (1U), and IT-M7723 models **must purchase the IT-E155A**."*

**Conclusion — R-PSU-01 resolved:**

`IT-E151` is a real ITECH part, and it is the **wrong kit** for this supply — not by a small margin, but by form factor: it mounts **half-rack-width 2U** instruments, while the IT-M3906B-32-240 is a **full-rack 1U** unit. The correct kit is **`IT-E155A`** (mandatory), plus `IT-E155B` or `IT-E155C` if the cabinet has no tray.

**Correction to `P0-DOC-03` §4.1:** that section, working from search summaries, associated `IT-E151/IT-E151A` with the *IT6900A / IT6300 / IT6700 / IT8500+* families. The primary source says **IT-M3100 / IT-M3100D / IT-M3200 / IT-M3300 / IT-M3400 / IT-M3600**. The secondary source was wrong on the detail while right on the conclusion — a good illustration of why the evidence tiers exist.

**Action:** photograph the installed kit's part number. If it is an IT-E151, the supply is mechanically mounted with a kit not designed for its chassis — raise it with the responsible engineer before the rack is energized.

---

## 7. Updated register and TBD status

| Item | Before | After |
|---|---|---|
| **T-02** Tektronix programmer manual | MISSING | **PARTIAL** — the non-B `077-1149-02` is in `manuals/`, registered `TRANSCRIBED-PROVISIONAL`. The **TBS2000B** manual is still needed before Phase 2 |
| **T-03** ITECH manual + P-IO pinout | MISSING | **PARTIAL** — the User Manual is in `manuals/` and the **P-IO pinout is closed**. The **Programming Guide is still missing**, so the supply stays `BLOCKED` for commands |
| **T-15** Correct rack kit | OPEN | ✅ **CLOSED** — `IT-E155A` is mandatory; `IT-E151` is for half-rack 2U instruments and is the wrong kit |
| **T-18** 50 Ω feedthrough | OPEN | **ADVANCED** — confirmed a standard accessory; check the amplifier's kit. Must be fitted at the **scope** end |
| **COM-008** Safety interface | FULLY OPEN | **ADVANCED** — P-IO pins 1–7 documented; pins 2 and 3 are candidate machine-observable feedback; pin 5 `Inhibit-Latch` is the only non-auto-recovering mode. Still needs a reviewed schematic and engineer sign-off |

## 8. New findings

| ID | Finding |
|---|---|
| **F-PSU-03** | P-IO pin 5 has two inhibit modes. `Inhibit-Living` (the **default**) auto-recovers output when the signal is released and leaves the front panel showing `On`. Only `Inhibit-Latch` requires manual restoration. |
| **F-PSU-04** | The ITECH web interface exposes a **firmware upload** page, and the default IP is a published constant (`192.168.200.100`). Network policy item. |
| **F-SCOPE-01** | The non-B programmer manual states a **2500-point** waveform limit; the TBS2104B has a **5 M point** record. Any constant carried over from that manual silently truncates to 0.05% of the acquisition. |
| **F-TCPA-03** | The probe slide must be **locked closed** to measure or degauss; `PROBE OPEN` is a front-panel LED only — not machine-readable. |
| **F-TCPA-04** | The circuit **must be de-energized** when fitting or removing the current probe on uninsulated wire. |
| **R-PSU-01 (resolved)** | `IT-E151` is a genuine part for half-rack 2U instruments. The IT-M3906B-32-240 is full-rack 1U and **requires `IT-E155A`**. |

---

## 9. Acceptance criteria for P0-DOC-04

**Status: PARTIAL.**

Closes when:

1. The **ITECH IT-M3900B Programming Guide** is obtained — until then the supply has no commands.
2. The **Tektronix TBS2000B** programmer manual is obtained, and every provisional entry in `command_register.md` §4 is re-verified against it, `DATa:STOP` and record-length handling first.
3. The installed rack kit part number is photographed and checked against §6.
4. The responsible engineer decides whether P-IO pins 1, 2, 3 and 5 form part of the safety architecture, and in which inhibit mode.

No hardware command is approved for execution. The register still holds **0 `APPROVED` entries**.
