# P0-DOC-02 — Instrument Datasheet and Manual Extract

**Project:** Vehicle Harness Functional Tester
**Phase:** P0 — Requirements, documentation, and safety inputs
**Task ID:** P0-DOC-02
**Document status:** Draft — derived entirely from manufacturer documents present in this repository
**Purpose:** Give the coding agent every fact that the supplied PDFs actually establish, with a page citation for each, and name precisely what the PDFs do **not** establish.

> **Scope of authority.** Everything here is a *manufacturer capability statement transcribed from a document*. Nothing here is a physically verified as-built fact, an engineer-approved operating limit, or authorization to energize anything. The distinction defined in `P0-DOC-01` §11 — *shown in a document* vs. *physically verified* vs. *engineer approved* vs. *software validated* — applies to every line below. Every value in this document is at the first level only.

---

## 1. Source document register

| Doc ID | File in repo | Type | Pages | SHA-256 (first 16) | Covers |
|---|---|---|---:|---|---|
| SRC-01 | `bk_precision_2831e_datasheet.pdf` | Datasheet, rev `v030210` | 4 | `c72b31c459da058f` | B&K 2831E — specs, interface class |
| SRC-02 | `bk_precision_2831e_manual.pdf` | **User + programming manual** | 71 | `f22710211fab325e` | B&K 2831E — **full SCPI command set**, serial settings |
| SRC-03 | `DAQ3120_datasheet.pdf` | Datasheet, rev `v030625` | 10 | `0228b9b183737b11` | B&K DAQ3120 + DM300/301/303/304/309 modules |
| SRC-04 | `Tektronix_TBS2104b.pdf` | Datasheet (TBS2000B series) | 17 | `ebb87d62445c3b3f` | Tektronix TBS2104B |
| SRC-05 | `TCPA400.pdf` | Datasheet `60W-16458-10`, 29 Jan 2016 | 6 | `a7baee3fb0a9742b` | Tektronix TCPA300/TCPA400 + probes |
| SRC-06 | `IT-M3906B-32-240_en.pdf` | Datasheet (IT-M3900B series) | 16 | `7a5da94618539aa0` | ITECH IT-M3906B-32-240 |

**Critical property of this set:** only **SRC-02 is a programming manual**. SRC-03, SRC-04, SRC-05 and SRC-06 are marketing/specification datasheets and contain **zero remote-control commands**. See §8.

---

## 2. B&K Precision 2831E — Digital Multimeters (EQ-003, EQ-004)

### 2.1 Remote interface — this resolves OBS-007

| Property | Value | Source |
|---|---|---|
| Remote interface | **USB (Virtual COM) only** — the PC sees a serial COM port, **not** USBTMC | SRC-02 p.71 "Remote Interface: USB (Virtual COM)"; p.40 §5.2.1; SRC-01 p.1 |
| Physical port | USB Device Port, rear panel | SRC-02 p.13 §2.5 item 1 |
| RS-232 port | **Model 5491B only — the 2831E does not have one** | SRC-02 p.13 §2.5 item 4 |
| Programming language | SCPI | SRC-02 p.40 §5.1 |
| Frame format | **8 data bits, 1 stop bit, no parity** | SRC-02 p.40 §5.2.2 |
| Baud rates | 600, 1200, 2400, 4800, 9600, 19.2k, 38.4k | SRC-02 p.40 §5.2.3 |
| Baud default | **9600** | SRC-02 p.41 |
| Termination char | `<LF>` or `<CR>`, selectable front panel (`SYS MEU → 3: TX TERM`) | SRC-02 p.40 §5.2.2, p.38–39 §4.5.3 |
| Baud set path | Front panel `SYS MEU → 2: BAUD RAT` | SRC-02 p.38 §4.5.2 |
| Reading format | `SD.DDDDDDESDDD<NL>` — sign, 6-decimal mantissa, exponent sign, 3-digit exponent, NL = ASCII 10 | SRC-02 p.41 §5.3 |

### 2.2 Serial protocol behaviour the driver MUST implement

These are not optional style points; they are stated protocol requirements in SRC-02 p.41 §5.2.4, and a naive `write()/readline()` driver **will** desynchronize:

1. **Character echo handshake.** Every character sent is echoed back by the meter. The controller must not send the next character until the previous echo is received correctly. A lost echo means: wrong wiring, baud mismatch, or the meter was busy — resend the character.
2. **Query responses are immediate.** If a compound command line contains two queries, the controller must perform **two** reads. The manual explicitly recommends **one query per command line**.
3. **Slow commands.** `*RST` and similar take significant time; the controller must wait rather than pipeline, or the following command is lost.
4. The meter transmits only in two cases: the echo handshake, and a query response.

> **Driver implication:** the 2831E transport is a byte-echoed serial link, not a clean line protocol. Treat it as its own transport class. Do **not** reuse a USBTMC/VISA-message driver for it.

### 2.3 SCPI subsystems available (SRC-02 p.45 §6.3)

Subsystems: `DISPlay`, `FUNCtion`, `VOLTage`, `CURRent`, `RESistance`, `FREQuency`, `PERiod`, `HOLD`, `TRIGger`, `FETCh`.
Common commands: `*RST`, `*TRG`, `*IDN?` — **only these three.**

Full verbatim syntax is transcribed into `command_register.md`. Highlights relevant to harness testing:

| Need | Command | Source |
|---|---|---|
| Identify instrument | `*IDN?` → `<product>,<version><LF^END>`, e.g. `2831E Multimeter,Ver1.0.09.12.03` | SRC-02 p.63 |
| Select 2-wire resistance | `:FUNCtion RESistance` | SRC-02 p.47 |
| Select continuity | `:FUNCtion CONTinuity` | SRC-02 p.47 |
| Select DC volts | `:FUNCtion VOLTage:DC` | SRC-02 p.47 |
| Set resistance range | `:RESistance:RANGe[:UPPer] <n>`, `<n>` = expected reading, 0 to 20e6 | SRC-02 p.57 |
| Resistance autorange | `:RESistance:RANGe:AUTO <b>` | SRC-02 p.57 |
| Null lead resistance | `:RESistance:REFerence:ACQuire` then `:RESistance:REFerence:STATe ON` | SRC-02 p.58–59 |
| Integration time | `:RESistance:NPLCycles <n>` (and per-function equivalents) | SRC-02 p.56 |
| Trigger source | `TRIGger:SOURce IMMediate\|BUS\|MANual` | SRC-02 p.62 |
| Bus trigger | `*TRG` | SRC-02 p.63 |
| Read last value | `:FETCh?` | SRC-02 p.62 |

### 2.4 Documented gap in the 2831E manual — do not paper over it

SRC-02 p.62 §6.3.8 states that `:FETCh?` *"will be automatically asserted when `:READ?` or `:MEASure?` command is sent."* **`:READ?` and `:MEASure?` are never defined anywhere else in the manual** — they appear in no subsystem table and have no syntax section.

Consequence: the only *documented* acquisition sequence is
`TRIGger:SOURce BUS` → `*TRG` → `:FETCh?`.
`:READ?` and `:MEASure?` are **NOT IMPLEMENTED / BLOCKED** pending a manual revision that defines them. Do not guess their syntax. See `command_register.md` entry `CR-2831E-BLOCKED-01`.

### 2.5 2831E measurement capability (SRC-02 p.65–71, SRC-01 p.3–4)

Accuracy is ±(% of reading + % of range), 1-year, 23 °C ± 5 °C, after ≥30 min warm-up.

**Resistance** — the harness continuity/isolation workhorse:

| Range | Resolution | Full scale | Test current | Accuracy (1 yr) |
|---|---|---|---|---|
| 200.00 Ω | 10 mΩ | 210.00 | 0.5 mA | 0.10% + 0.05% *(REL)* |
| 2.0000 kΩ | 100 mΩ | 2.1000 | 0.45 mA | 0.10% + 0.025% *(REL)* |
| 20.000 kΩ | 1 Ω | 21.000 | 45 µA | 0.10% + 0.025% *(REL)* |
| 200.00 kΩ | 10 Ω | 210.00 | 4.5 µA | 0.10% + 0.025% |
| 2.0000 MΩ | 100 Ω | 2.1000 | 450 nA | 0.15% + 0.025% |
| 20.000 MΩ | 1 kΩ | 21.000 | 45 nA | 0.3% + 0.05% |

- Max input protection: 1000 VDC or 750 VAC, all ranges.
- **Open-circuit voltage: max 5.5 VDC.**
- Above 100 kΩ, a **shielded** test cable is recommended (noise).
- Ranges ≤20 kΩ are specified *only under REL* — the null must be taken, or the accuracy figure does not apply.

**Continuity:** 200 Ω range, 100 mΩ resolution, 0.5 mA test current, 0.1% + 0.1%, threshold = **5% of range (≈10 Ω)**, open-circuit < 5.5 VDC.

**DC Voltage:** 200 mV / 2 V / 20 V / 200 V / 1000 V; basic 0.03% + 0.02%; input Z 10 MΩ (>10 MΩ on low ranges); **max input 1000 VDC or peak AC, all ranges**.

**DC Current:** 2 mA / 20 mA / 200 mA / 2 A / 20 A. **Input protected by a 1 A / 250 V fuse.** On the 20 A range, 10–20 A DC is readable for **20 seconds maximum**.

**Reading rates** (SRC-02 p.64), readings/s: DCV/DCA/ACV/ACA — Slow 5, Med 10, Fast 25. Ω below 2 MΩ — 5 / 10 / 25. Ω at 20 MΩ and above — 1.3 / 2.6 / 5.6. Dual display drops everything to ≈0.9/s.

> **Cycle-time implication:** a per-pin resistance measurement on the 2831E costs ≥40 ms at Fast and ≥200 ms at Slow, **before** switching settling. The test-engine timing budget must be built from these numbers, not from an assumption.

**General:** 110/220 V ±10%, 50/60 Hz ±5%, ≤10 VA; 0–40 °C; warm-up ≥30 min; 225 × 100 × 355 mm; 2.5 kg. Line fuse 220 V/500 mA or 110 V/1 A. Math: Rel, Max/Min, dBm, dB, Compare limit test, %.

---

## 3. B&K Precision DAQ3120 — Data acquisition system (EQ-005, EQ-006)

### 3.1 Remote interfaces — richer than P0-DOC-01 assumed

| Property | Value | Source |
|---|---|---|
| Interfaces | **LAN**, **USB device (USBTMC *and* USBVCP)**, USB host port, 9-pin D-sub Digital I/O, optional micro-GPIB (`-GPIB` model only) | SRC-03 p.1, p.5, p.9 |
| Built-in web interface | Yes — virtual front panel, no software install, IP or hostname in a Java-enabled browser, optional password | SRC-03 p.2 |
| Digital I/O | 4 alarm outputs, 1 end-of-measurement (EOM) output, 1 external trigger input | SRC-03 p.5, p.9 |
| Vendor PC software | "DAQ-Data Logger", up to 4 units | SRC-03 p.2 |

> The USB port on the DAQ3120 is **not** merely a fallback — it is a full USBTMC device port. `P0-DOC-01` OBS-008 (declare exactly one production transport) therefore still stands, and the choice is a real one. LAN is recommended by the concept drawing (S2, COM-004); confirm and record it.

### 3.2 Base unit

| Property | Value |
|---|---|
| Built-in DMM | 6½ digit |
| Slots | **3** module slots |
| Max channels/system | **120** (3 × DM303) |
| Basic DCV accuracy | 0.0035% |
| Internal memory | 100 kSa non-volatile, with time stamps |
| Max reading rate | 38 400 readings/s (at 4½ digits) |
| Display | 4.3" WQVGA 480×272 |
| AC input | 100–240 VAC ±10%, 50/60 Hz, max 50 VA |
| Operating temp | 0 °C to 55 °C |
| Weight | 4.5 kg (9.92 lb) |
| Rack dims (no boot) | 220 × 88 × 348.6 mm (8.7 × 3.5 × 13.7 in) → **2U**, not 3U |
| Rackmount kit | **RKDAQ** |
| Warranty | 3 years |
| Stabilization | **1 hour** before specifications apply (60 min for AC) |

> **Note the 2U/3U discrepancy:** SRC-03 p.9 gives a rack height of 88 mm ≈ 2U, while `P0-DOC-01` S1 shows the DAQ3120 allocated 3U. Not a safety issue, but the rack elevation drawing must be corrected or the extra U explained.

### 3.3 Module comparison — this constrains the fixture design (SRC-03 p.1, p.4)

| | DM300 | **DM301** | DM303 | DM304 | DM309 |
|---|---|---|---|---|---|
| Channels | 20 | **20 + 2 current** | 40 single-ended | 32 cross-points (4×8 matrix) | 8 + 2 current |
| Switching | 2-wire solid-state | **2-wire armature** | single-wire armature | 2-wire armature | 2-wire armature |
| Scan speed | 450 ch/s | **80 ch/s** | 80 ch/s | 3 ms switching | 60 ch/s |
| Max voltage | 120 V | **300 V** | 300 V | 300 V | 600 VDC / 400 Vrms |
| Max current | — | **1 A per current ch** | — | — | 2 A per current ch |
| Bandwidth | 10 MHz | 10 MHz | 10 MHz | 10 MHz | 10 MHz |
| Thermal offset | < 4 µV | < 4 µV | < 1 µV | < 1 µV | < 4 µV |
| AC/DC voltage | ✓ | ✓ | ✓ | — | ✓ |
| AC/DC current | — | ✓ | — | — | ✓ |
| Freq/period | ✓ | ✓ | ✓ | — | ✓ |
| Resistance 2W/4W | ✓ | ✓ | 2-wire only | — | ✓ |
| Thermocouple | ✓ | ✓ | — | — | ✓ (needs external CJC) |
| RTD | — | ✓ | 2-wire | — | ✓ |
| Thermistor | — | ✓ | ✓ | — | ✓ |
| Capacitance | — | ✓ | ✓ | — | ✓ |

Additional module facts:
- **DM300:** 20 ch in two 10-ch banks, both high and low lines switched, fully isolated. 4-wire pairs bank 1 with bank 2.
- **DM301:** two banks, 2-wire and 4-wire channels can be mixed on the same module; built-in cold-junction reference.
- **DM303:** all 40 inputs share a common signal ground, isolated, floatable to 300 V. Supports 2-wire measurement **except current**.
- **DM304:** **does not connect to the built-in DMM** (SRC-03 p.9 footnote). It is a pure switch matrix for routing *external* instruments to the DUT. Expandable to 96 cross-points.
- **DM309:** each current channel is individually fused, fuse located in the module.

### 3.4 Three findings that change the fixture and test design

**F-DAQ-01 — the "60-channel with DM301" description in P0-DOC-01 does not match one DM301.**
One DM301 is 20 mux channels + 2 current channels. 60 channels requires **three** DM301 modules (= 60 mux + 6 current, filling all 3 slots), or a different module mix. Either the drawing means "3 × DM301" or a module is mis-identified. **This must be resolved by physically listing modules and slots** — it directly determines how many harness pins can be reached. Feeds `P0-DOC-01` OBS-003.

**F-DAQ-02 — the DAQ cannot measure DUT current.**
Max current per DAQ current channel is 1 A (DM301) or 2 A (DM309). The DUT supply is rated 240 A. The DAQ is therefore **not** part of the high-current measurement path under any module configuration. This confirms an external probe/shunt chain is mandatory — see §5.

**F-DAQ-03 — 4-wire resistance consumes channels in pairs.**
On DM300 and DM301, a 4-wire measurement pairs a bank-1 channel with a bank-2 channel. A 20-channel module therefore yields **10** 4-wire points. Channel-count budgeting for the harness pin map must use the 4-wire number wherever lead resistance matters (which, for milliohm-level harness continuity, is most places).

### 3.5 DAQ3120 measurement capability (selected, SRC-03 p.6–8)

**DC voltage** (1-year, TCAL ±5 °C): 100 mV 0.0050+0.0060 · 1 V 0.0048+0.0007 · 10 V 0.0035+0.0005 · 100 V 0.0050+0.0006 · 600 V 0.0050+0.0020. Input protection 600 V all ranges. Input Z 10 MΩ or >10 GΩ (auto) on ≤10 V ranges.

**Resistance** (1-year): 100 Ω @1 mA 0.010+0.004 · 1 kΩ @1 mA 0.010+0.001 · 10 kΩ @100 µA · 100 kΩ @10 µA · 1 MΩ @5 µA · 10 MΩ @500 nA 0.040+0.001 · 100 MΩ, 1 GΩ (2-wire only).
Specs apply to **4-wire, or 2-wire with math null**. Without null, **add 2 Ω of error** — decisive for harness continuity limits.
Max lead resistance: 10% of range per lead on 100 Ω/1 kΩ ranges; 1 kΩ per lead elsewhere.

**DC current** (1-year): 1 mA 0.050+0.006 · 10 mA 0.050+0.020 · 100 mA 0.050+0.005 · 2 A 0.200+0.020. Internal 250 V fuse for 2 A. Burden voltage at 2 A: < 0.8 V, 0.1 Ω shunt.

**Reading rate vs. digits:** 5/20/60/100 rd/s → 6½ digits · 400/1200/2400 → 5½ · 4800…38400 → 4½. DC specs require the **5/s speed with A-Zero**.

**AC:** true-RMS AC-coupled, tolerates up to 400 VDC bias; crest factor max 5:1; ACV bandwidth to 300 kHz, ACI to 10 kHz; ACV input protection 400 Vrms.

**Temperature:** thermocouples E/J/T/K/N/R/S/B, RTD (Pt100), thermistor 2.2k/5k/10k/user. K-type 90-day/1-year accuracy 0.3 °C.

---

## 4. Tektronix TBS2104B — Oscilloscope (EQ-007)

### 4.1 Remote interfaces

| Property | Value | Source |
|---|---|---|
| LAN | RJ-45, **10/100BASE-T** | SRC-04 p.12 |
| USB device port | Rear panel, **USBTMC**; also GPIB via TEK-USB-488 adapter | SRC-04 p.3, p.12 |
| USB host ports | One front, one rear (storage, Wi-Fi dongle) | SRC-04 p.12 |
| Wi-Fi | Via dongle (TEK-USB-WIFI or listed NETGEAR/D-LINK/TP-LINK) | SRC-04 p.1, p.12 |
| Built-in web page | Remote control of horizontal/vertical scale, trigger, measurements; save waveform and image to USB | SRC-04 p.12 |
| Command set | "fully-documented command set" — **document is Tektronix programmer manual `077-1149-xx`, NOT included in this repo** | SRC-04 p.5, p.14 |

> **Wi-Fi must be disabled** on a test-station instrument unless IT explicitly approves it (`P0-DOC-01` OBS-006). Record the decision.

### 4.2 Acquisition specification (SRC-04 p.9–11)

| Property | Value |
|---|---|
| Model | TBS2104B — 100 MHz, **4 analog channels** |
| Sample rate | 2 GS/s half-channel, **1 GS/s with all channels on** |
| Record length | 5 M points, all channels |
| Vertical resolution | **8 bits** |
| Input impedance | **1 MΩ ± 1%, 13 pF ± 1.5 pF — there is no 50 Ω input** |
| Input coupling | DC or AC |
| Sensitivity | 1 mV/div to 10 V/div |
| Max input (1 MΩ) | 300 Vrms CAT II, peaks ≤ ±450 V |
| Bandwidth limit | 20 MHz hardware |
| DC gain accuracy, typ. | ±2% (10 V/div–5 mV/div); ±3% (1 mV/div, 2 mV/div) |
| Acquisition modes | Sample, Peak Detect (glitches ≥3.5 ns), Average (2–512), Hi-Res, Roll |
| Time base | 1 ns/div to 100 s/div; accuracy ±25 ppm; deskew range ±100 ns |
| Max capture at full rate, all ch | **5 ms** |
| Triggers | Edge, Pulse width, Runt. Modes Auto/Normal/Single. Holdoff 20 ns–8 s |
| Math | Ch1±Ch2, Ch1×Ch2, Ch3±Ch4, Ch3×Ch4, FFT |
| Measurements | 32 automated, max 6 on screen; incl. RMS, Cycle RMS, Mean, Max, Min, Area, Rise/Fall time, Overshoot |
| Power | 100–240 VAC ±10%, 47–63 Hz, ≤80 W |
| Dimensions (4-ch) | 201.5 × 412.8 × 128.1 mm; 4.17 kg |
| Cooling clearance | **50 mm required on left side and rear** |
| Rackmount kit | **RMB2040** (for TBS2074B/2104B/2204B) |
| Temp / warranty | 0–50 °C; 5 years |

> **Design consequence:** 8-bit vertical resolution and a 5 ms full-rate record are hard ceilings. Any inrush/transient recipe must fit inside 5 ms at 1 GS/s, or run at a reduced sample rate. The `Cycle RMS` / `Mean` automated measurements exist and should be preferred over host-side math on transferred waveforms where they suffice.

### 4.3 Probe interface — the TCPA400 connection problem

The TBS2000B front panel is **TekVPI**. TekVPI probes self-report scale factors, ranges and status, and the scope auto-scales (SRC-04 p.5). The TCPA400 is **not** a TekVPI probe. See §5.3.

Recommended accessory in SRC-04 p.15: **`TPA-BNC` — TekVPI to TekProbe BNC adapter.**
Native TekVPI current probes listed for this scope: TCP0020 (20 A), TCP0030A (30 A), TCP0150 (150 A), TCP2020 (50 A BNC). **None of them reaches 240 A** — which is why the TCPA400/TCP404XL chain exists in this rack.

---

## 5. Tektronix TCPA400 — Current probe amplifier (EQ-008) and the current sensor (EQ-014)

### 5.1 The probe question is answered — this resolves the identity half of OBS-005

SRC-05 p.4–5 is unambiguous:

> "TCPA400 Amplifier AC/DC current probe, DC to 50 MHz, **(Requires TCP404XL probe)**"
> "TCP404XL Probe AC/DC current, DC to 2 MHz; 500 A DC (750 A DC derated with duty cycle) **(Requires TCPA400 amplifier)**"

**The TCPA400 has exactly one compatible probe: the TCP404XL.** The unidentified "CURR SENSOR PROBE OR SHUNT" in drawing S2 is therefore either a TCP404XL, or it is not connected to the TCPA400 at all. There is no third option within this product family. Confirm which by physical inspection.

### 5.2 TCP404XL with TCPA400 — capability (SRC-05 p.2–3)

| Property | Value |
|---|---|
| Bandwidth | **DC – 2 MHz** (the *amplifier* is DC–50 MHz; the **probe** is the limit) |
| Rise time | ≤ 175 ns |
| DC accuracy | **±3% of reading** (guaranteed); ±1% typical |
| Sensitivity range | **1 A/mV** (i.e. 1000 A/V) — the only range for this probe |
| DC continuous | **500 A** (750 A derated with duty cycle) |
| RMS sinusoidal | 500 A |
| Peak | 750 A |
| Lowest measurable current (±3% at DC) | **1 A** (scope at 1 mV/div, 20 MHz BW limit) |
| Max amp-second product | N/A at 1 A/mV |
| Displayed RMS noise, typ. | **≤ 250 mA RMS** at 20 MHz BW limit |
| Max wire voltage | 600 V CAT I & II bare; 300 V CAT III insulated |
| Insertion impedance | 0.1 mΩ @10 kHz; 0.6 mΩ @100 kHz; 8 mΩ @1 MHz; 16 mΩ @2 MHz |
| Signal delay to output BNC | **80 ns** |
| Max conductor size | **21 × 25 mm (0.83 × 1.0 in)** |
| Cable length | 8 m |
| AC-coupled LF bandwidth | < 7 Hz |
| Amplifier power | 90–264 V, 47–440 Hz, 50 W, CAT II, auto-switching |
| Amplifier size / weight | 173 × 167 × 91.4 mm; 1.14 kg |
| Operating temp | 0 to +50 °C |

**Fit against this application:** DUT current is 0–240 A (§6). 240 A sits at 48% of the 500 A continuous rating — comfortable. But note the cost of that headroom:

- **Noise floor ≈ 250 mA RMS** and **lowest accurate current 1 A**. Any harness test that needs to resolve leakage or small quiescent currents **cannot use this chain** — it must use a DMM or DAQ current channel instead.
- **±3% of reading** guaranteed. A 240 A reading carries ±7.2 A of guaranteed uncertainty. Any pass/fail limit tighter than that is not defensible on this instrument.
- **80 ns signal delay** must be deskewed against voltage channels for any power/energy math (scope deskew range is ±100 ns — it fits, barely).
- Conductor must fit **21 × 25 mm**. A 240 A conductor is large; confirm the actual cable cross-section clears the jaw *before* assuming this probe can be installed.

### 5.3 F-TCPA-01 — automatic scaling will NOT work on this scope. Plan for manual scaling.

SRC-05 p.1 footnote 2 and p.2 list which scopes get automatic on-screen scaling and units from the TCPA300/400:

> "Requires a TDS TEKSCOPE oscilloscope or a TekConnect oscilloscope with TCA-BNC adapter"
> …auto scaling is provided for TDS3000, TDS500/600/700, TDS5000, TDS6000, TDS7000B; and for DPO3000, MDO/MSO/DPO4000, MSO/DPO5000, DPO7000 "the TPA-BNC adapter is required".

**The TBS2000B series is not on either list.** SRC-05 p.2 gives the fallback explicitly:

> "Even non-TEKPROBE systems can use the TCPA300/400 series to make proper current measurements by simply multiplying the measured output voltage on the oscilloscope by the TCPA300/400 series range setting."

**Software consequence — this is a real requirement, not a footnote:**
1. The scope will read **volts**, not amps. The application must apply the conversion itself: `I[A] = V_scope[V] × 1000` for the TCP404XL 1 A/mV range.
2. The **1000 A/V scale factor is a configuration value that must be recorded, reviewed and version-controlled**, not hard-coded from this document. If the amplifier range is ever changed, every stored result taken before the change becomes wrong. Store the amplifier range setting **with each run record**.
3. The amplifier's **degauss/autobalance state, overload flag, probe-open flag and "not terminated into 50 Ω" flag are front-panel LEDs** (SRC-05 p.1, "Status indicators"). They are **not** readable over any bus. The software therefore **cannot** verify probe health. This must be an operator checklist step in the commissioning procedure, and the application must not claim a verified current measurement.

### 5.4 F-TCPA-02 — a 50 Ω termination is required and the scope cannot provide it

The TCPA400 output is a 50 Ω source; the amplifier has a "not terminated into 50 Ω" error indicator (SRC-05 p.1). The TBS2104B input is **1 MΩ only** (§4.2) — this scope has **no 50 Ω input setting**.

Therefore the chain needs an **external 50 Ω feedthrough terminator**, listed as a recommended accessory in SRC-05 p.4: **`011-0049-02`**. Also relevant: `012-0117-00` 50 Ω BNC-to-BNC coaxial cable, and `012-1605-00` TEKPROBE interface cable.

**Without the feedthrough, the amplitude will be wrong by roughly 2× and the amplifier will flag an error the software cannot see.** Add `011-0049-02` (or an equivalent reviewed terminator) to the parts list, and add "50 Ω terminator fitted, amplifier not showing termination error" to the commissioning checklist.

### 5.5 Resulting current-chain bill of materials to verify

| Item | Part | Status |
|---|---|---|
| Current probe | Tektronix **TCP404XL** | Presence to be physically confirmed |
| Amplifier | Tektronix **TCPA400** | Shown in rack drawing S1 |
| Amplifier→scope cable | `012-1605-00` TEKPROBE cable, or `012-0117-00` 50 Ω BNC-BNC | To be confirmed |
| 50 Ω termination | **`011-0049-02`** feedthrough | **Likely missing — verify** |
| TekVPI→BNC adapter | **`TPA-BNC`** | **Likely missing — verify** |
| Scope channel assignment | TBD | To be assigned and recorded |
| Calibration adapter (service) | `174-4765-00` | Optional |

---

## 6. ITECH IT-M3906B-32-240 — Regenerative DC power system (EQ-009)

### 6.1 Identity — OBS-001 advances but does not close

SRC-06 p.3 lists `IT-M3906B-32-240` in the 32 V family of the **IT-M3900B** series, and p.10 gives its full specification table. The model number in drawing S1 is therefore **a real ITECH part number with matching 0–32 V / 240 A / 6 kW ratings**, exactly as the S2 drawing labels the supply informally as "REGGEAR DC POWER SUPPLY DUT 0–32 V 240 A".

**"REGGEAR" is not an ITECH product name and appears nowhere in SRC-06.** Most probable reading: it is a shorthand for *regenerative gear* on the concept sketch. **OBS-001 still requires a nameplate photograph to close** — a datasheet matching a hand-drawn label is corroboration, not verification.

### 6.2 F-PSU-01 — this is a bidirectional source *and* a regenerative load

The IT-M3900B is a two-in-one unit: a bidirectional DC supply **and** an independent regenerative electronic load, switched by **one button on the front panel** (SRC-06 p.4). Its output current range is **−240 A to +240 A** and power **−6000 W to +6000 W**.

This is a first-order safety and software fact that `P0-DOC-01` did not capture:

- The instrument can **sink** current from the DUT and **feed energy back into the grid** (up to 95% regeneration, SRC-06 p.6).
- Whether it is in **Source** or **Load** mode is a **front-panel state**. The application must **read and display** the mode and must never assume Source.
- Anti-islanding and power-grid detection are named protections — meaning the unit interacts with the facility supply in ways an ordinary bench supply does not. This belongs in the facility electrical review, not just the rack review.

### 6.3 Specification — IT-M3906B-32-240 (SRC-06 p.10)

**Source (power supply) mode:**

| Parameter | Value |
|---|---|
| Voltage | 0 – 32 V |
| Current | 0 – 240 A |
| Power | 0 – 6000 W |
| Load resistance (CC priority) | 0.005 Ω – 400 Ω |
| Setup resolution | 0.001 V / 0.01 A / 1 W / 0.001 Ω |
| Readback resolution | 0.001 V / 0.01 A / 1 W |
| Setup accuracy | V ≤0.05%+0.05%FS · I ≤0.1%+0.1%FS · P ≤0.5%+0.5%FS |
| Readback accuracy | V ≤0.05%+0.05%FS · I ≤0.1%+0.1%FS · P ≤0.5%+0.5%FS |
| Current slew rate | 240 A/ms rising and falling |
| Power regulation rate | ≤0.01%+0.01%FS (V), ≤0.03%+0.03%FS (I) |
| Load regulation rate | ≤0.02%+0.02%FS (V), ≤0.05%+0.05%FS (I) |
| Min. operation voltage | 0.5 V at 240 A |
| **Remote sense compensation** | **≤ 10 V** |

**Load mode:** voltage 0–32 V, current −240 to +240 A, power −6000 to +6000 W, series IR 0–0.06 Ω, load resistance 0.005–400 Ω, voltage ripple ≤80 mVpp / ≤30 mV RMS, rise time ≤30 ms (no load) / ≤100 ms (full load), fall time ≤60 ms (no load) / ≤30 ms (full load).

**Protection trip values as printed** (SRC-06 p.10 — the two-column layout in the source PDF makes column assignment ambiguous; **verify against the printed page before encoding**):
OCP 244.8 A and/or ±247.2 A · OVP 33 V and/or 35 V · OPP ±6120 W.
These are *instrument* protection trips, i.e. the outer envelope. **They are not test limits.**

**AC input:**

| Parameter | Value |
|---|---|
| Voltage | **3φ 200–480 V**, or **1φ 100–240 V** |
| Frequency | 50/60 Hz |
| Max apparent power | **6.5 kVA** |
| Max AC current | **12.5 Aac** (hard limit — power derates at low line) |
| Max efficiency | 90% |
| Power factor | 0.99 |
| DC component | ≤0.2 A |
| Current harmonic | ≤3% |

SRC-06 note *3 worked examples: 3-phase at 200 V line → P = 200 × 12.5 × 1.732 = **4330 VA**; single-phase at 200 V → **2500 VA**.
**Implication:** the nameplate 6 kW is *not* available at every supply voltage. The facility feed determines the real ceiling. This must be settled in the electrical review before any output ceiling is approved.

**General:** working temp 0–40 °C · storage −10 to +70 °C · **programming response time 0.1 ms** · withstand voltage 200 Vdc / 2100 Vac to ground · air cooled · 1U at 6 kW.

**Modes:** 8 source modes — CC / CV / CW / CR / CC+CV / CV+CR / CR+CC / CC+CV+CW+CR. Load mode CC/CV/CP/CR. CC and CV priority selectable. Adjustable output impedance. Voltage/current/power slope settable. Dynamic driving-condition simulation up to 10 million points.

**Protections:** OVP, ±OCP, ±OPP, OTP, voltage transient drop protection, anti-islanding, power grid detection.

**Automotive standards (partial pre-compliance, SRC-06 p.4):** LV123, LV148, DIN40839, ISO-16750-2, SAEJ1113-11, LV124, ISO21848. *Partial* and *not available for 10 V models*. Do not represent the station as compliant to any of these.

### 6.4 Rear-panel interfaces (SRC-06 p.8, item list 1–9)

1 CAN · 2 Digital I/O (**P-IO**) · 3 **LAN** · 4 optional-accessory slot · 5 **Sense terminals (Vs+, Vs−)** · 6 **USB** · 7 outer-ring optical fibre (TX/RX, for parallel operation) · 8 AC terminals (L1, L2, L3, PE) · 9 DC output terminals.

Built-in: **USB / CAN / LAN / digital I/O**. Optional: **IT-E176 GPIB** card, **IT-E177 RS232 & analog** card.

> The **P-IO digital I/O** is the most safety-relevant interface on this instrument and is not mentioned anywhere in `P0-DOC-01`. On ITECH M-series units P-IO commonly carries external-enable / inhibit and fault signalling. **Its pinout and function are NOT in this datasheet** — obtain the user manual and treat P-IO as a candidate hardwired interlock/inhibit path for the safety chain (COM-008). Do not assume any specific pin behaviour.

### 6.5 F-PSU-02 — "IT-E151 Rack Kit" is very likely a transcription error

SRC-06 p.8 lists ITECH optional accessories including:

- **`IT-E155A/B/C` — Rack mount kits** ("Cabinet rack mount installation")
- `IT-E168` optical fibre cable kit
- `IT-E165A-250 / -400 / -500` anti-reverse protection units (250 A / 400 A / 400 A)
- `IT-E165B` anti-EMF unit 1200 V/200 A
- `IT-E176` GPIB card, `IT-E177` RS232 & analog card
- `IT-E258` series AC input power cords

The item labelled **"B&K IT-E151 Rack Kit"** in drawing S1 is almost certainly the **ITECH IT-E155x rack mount kit** — an *ITECH* accessory, not a B&K one, which also explains the manufacturer mismatch flagged as OBS-002. It is a mechanical kit and **should not be drawing 120–240 VAC** as S1 shows.

**Also worth checking while inspecting:** `IT-E165A-250` is an **anti-reverse protection unit rated 250 A**. On a 240 A bidirectional supply feeding an automotive harness, reverse-connection protection is exactly the kind of accessory that should be present. Confirm whether one is installed. If not, raise it with the responsible engineer.

**OBS-002 is not closed by this** — it still needs a nameplate photograph. But the search is now specific: look for `IT-E155A`, `IT-E155B`, or `IT-E155C`.

---

## 7. Consolidated capability ceilings (NOT approved test limits)

Reproduced for the coding agent as **guard rails for input validation only**. Per `P0-DOC-01` §5 and OBS-010, a capability is not an operating limit. The application must refuse any value above these, **and** must additionally refuse any value above the engineer-approved ceilings, which are still TBD.

| Quantity | Instrument capability | Source | Approved operating limit |
|---|---|---|---|
| DUT supply voltage | 0–32 V | SRC-06 p.10 | **TBD — REQUIRED** |
| DUT supply current | 0–240 A (sink to −240 A) | SRC-06 p.10 | **TBD — REQUIRED** |
| DUT supply power | ±6000 W, AC-limited (see §6.3) | SRC-06 p.10 | **TBD — REQUIRED** |
| Remote sense compensation | ≤10 V | SRC-06 p.10 | **TBD** |
| Current probe continuous | 500 A (750 A derated) | SRC-05 p.3 | **TBD** |
| Current probe minimum usable | 1 A; noise ≈250 mA RMS | SRC-05 p.2 | n/a |
| Scope max input | 300 Vrms CAT II, ±450 V peak | SRC-04 p.9 | **TBD** |
| DAQ max input (DM301) | 300 V, 1 A per current channel | SRC-03 p.4 | **TBD** |
| DAQ max input (DM309) | 600 VDC / 400 Vrms, 2 A per current channel | SRC-03 p.4 | **TBD** |
| DMM max input | 1000 VDC / 750 VAC; 20 A DC for ≤20 s | SRC-02 p.65–66 | **TBD** |
| DMM Ω open-circuit voltage | ≤5.5 VDC | SRC-02 p.67 | n/a |

---

## 8. What these PDFs do NOT provide

This section exists so no downstream agent mistakes this repository for a sufficient basis to write instrument control code.

### 8.1 Missing programming manuals — hard blockers

| Instrument | Document required | Identifier | Consequence today |
|---|---|---|---|
| B&K DAQ3120 | Programming / SCPI manual | not stated in SRC-03 | **All DAQ commands BLOCKED** |
| Tektronix TBS2104B | Programmer manual | **`077-1149-xx`** (named in SRC-04 p.14, obtainable from tek.com) | **All scope commands BLOCKED** |
| ITECH IT-M3906B-32-240 | User + programming manual, and **P-IO pinout** | not stated in SRC-06 | **All supply commands BLOCKED** |
| B&K 2831E | — | **Have it: SRC-02** | Commands available, transcribed |

Per the agent instructions in `m365_copilot_agent_setup_for_harness_tester (1).md`: *"Never invent, autocomplete, infer, or translate an SCPI, VISA, serial, socket, relay-switching, or power-output command."* An instrument whose manual is absent is **NOT IMPLEMENTED**, and its driver is a simulation-only stub. There is no exception for "the SCPI standard probably works this way."

### 8.2 Also absent from these PDFs

- Any fixture, harness connector, pin map, relay route table, or DUT interface.
- The control/safety panel and AC distribution schematics (COM-008 remains fully open).
- Serial numbers, firmware versions, calibration dates, installed DAQ module list.
- IP addressing, VISA resource strings, network topology, switch model.
- Which physical conductor the current probe surrounds, and its polarity.
- Where remote sense (Vs+/Vs−) is landed — supply, terminal block, fixture, or DUT.
- Approved test recipes, limits, or sequences.

---

## 9. Impact on the P0-DOC-01 open items

| P0-DOC-01 item | Status after this extract | What still closes it |
|---|---|---|
| OBS-001 supply identity | **Advanced** — model number and all ratings confirmed against ITECH's own datasheet; "REGGEAR" is not a product name | Nameplate photograph (front + rear + label) |
| OBS-002 "IT-E151 Rack Kit" | **Advanced** — almost certainly ITECH `IT-E155A/B/C` rack mount kit, not a B&K item, and not powered | Photograph the item's part number |
| OBS-003 DAQ modules | **Advanced** — DM301 is 20+2 ch, so "60 channel" implies 3× DM301; DM304 does not connect to the internal DMM | Physical module + slot list |
| OBS-004 safety panel | **Unchanged — fully open** | Reviewed schematic; also evaluate PSU **P-IO** as an interlock path |
| OBS-005 current chain | **Substantially advanced** — probe must be TCP404XL; scale 1 A/mV; manual scaling required; 50 Ω feedthrough and TPA-BNC required; status flags are not machine-readable | Confirm probe model, conductor, polarity, scope channel, terminator |
| OBS-006 router/switch | **Unchanged** | Model, type, IT approval; decide Wi-Fi = off |
| OBS-007 DMM USB mode | **CLOSED by SRC-02** — 2831E is **USB Virtual COM**, 8N1, default 9600, LF or CR terminator. Not USBTMC | Record per-unit COM port and serial number mapping |
| OBS-008 transport selection | **Advanced** — DAQ3120 offers USBTMC *and* USBVCP *and* LAN; scope offers USBTMC *and* LAN *and* Wi-Fi; PSU offers USB *and* LAN *and* CAN | Declare one production transport per instrument in writing |
| OBS-009 fixture | **Unchanged — fully open** | Fixture schematic and pin map |
| OBS-010 approved limits | **Advanced** — every capability ceiling is now documented (§7) | Engineer-approved station ceilings and per-recipe limits |

**New findings raised by this document:** F-DAQ-01, F-DAQ-02, F-DAQ-03, F-TCPA-01, F-TCPA-02, F-PSU-01, F-PSU-02, plus the DAQ3120 2U/3U rack discrepancy and the 2831E `:READ?`/`:MEASure?` documentation gap (§2.4).

---

## 10. Acceptance criteria for P0-DOC-02

**Status: PARTIAL — datasheet extraction complete, verification and manuals outstanding.**

P0-DOC-02 may be marked PASS only when:

1. Every value here is confirmed against the physical nameplate of the installed unit (not the datasheet).
2. Serial number, firmware version and calibration status are recorded for each instrument.
3. The DAQ3120 installed module list and slot assignment is recorded.
4. The programming manuals in §8.1 are obtained, registered, and their revisions recorded.
5. The current-chain BOM in §5.5 is confirmed present, including the 50 Ω terminator and TPA-BNC adapter.
6. The IT-M3906B **P-IO** pinout is obtained and its role in the safety chain decided by the responsible engineer.
7. One production transport per instrument is declared in writing.

No hardware command, switching action, or power-output action is authorized by completion of this document.
