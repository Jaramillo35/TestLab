# PROJECT_STATUS

**Project:** Vehicle Harness Functional Tester
**Last updated:** 2026-09-08
**Updated by:** P0 internet research pass (follows the datasheet extraction pass)
**Current phase:** P0 — Requirements, documentation and safety inputs
**Current gate:** **INCONCLUSIVE**

> This file is the running state of the project. The coordinator agent asks for it first;
> keep it current and keep it short. Detail lives in the P0-DOC-* documents.

---

## 1. Mode and safety state

| Flag | Value |
|---|---|
| `mode_default` | `SIMULATION` |
| `real_mode_enabled` | **false** |
| `real_output_control_enabled` | **false** |
| Physical E-stop verified independent of PC | **NOT YET VERIFIED** |
| Engineer authorization for energized commissioning | **NOT GRANTED** |
| Approved operating ceilings | **NONE SET** |

---

## 2. Documents

| Document | Status |
|---|---|
| `P0-DOC-01_equipment_and_communication_inventory.md` | Draft — INCONCLUSIVE, awaiting physical verification |
| `P0-DOC-02_instrument_datasheet_extract.md` | Draft — PARTIAL. **Two conclusions corrected by P0-DOC-03; read them together** |
| `P0-DOC-03_internet_research_findings.md` | Draft — PARTIAL (1 of 3 missing manuals recovered; 2 blocked by network policy, not availability) |
| `command_register.md` | Draft — **0 approved entries**, 2 of 4 instruments transcribed, 2 blocked |
| `instrument_profiles.yaml` | Draft — unreviewed, simulation only |
| `NEXT_STEP_BRIEF.md` | Current — Phase 1 scope and coding prompt |
| `COPILOT_PROMPTS.md` | Current — Phase 1 as five sequenced GitHub Copilot prompts |
| `HANDOFF.md` | Current — resuming on another machine |
| `.github/copilot-instructions.md` | Current — repo-wide Copilot operating envelope |
| `m365_copilot_agent_setup_for_harness_tester (1).md` | Reference — coordinator agent configuration |
| Fixture schematic / pin map / route table | **MISSING** |
| Safety-panel and AC-distribution schematics | **MISSING** |
| DAQ3120 programming manual | ✅ **RETRIEVED** — `manuals/DAQ3120_programming_manual.pdf`, 139 pp, v2026-01-07 |
| DAQ3120 user manual | Read (147 pp); **not committed — 134 MB**, URL in `P0-DOC-03` §5 |
| Tektronix programmer manual `077-1149-xx` | **MISSING** — URL identified, download blocked by network policy |
| ITECH IT-M3906B user + programming manual (incl. P-IO pinout) | **MISSING** — URLs identified, download blocked by network policy |

---

## 3. Completed work

- **P0-DOC-01** — equipment and communication inventory drafted from two planning drawings; 15 equipment IDs, 9 communication links, 10 observations raised.
- **P0-DOC-02** — all six manufacturer PDFs in this repository extracted with page citations; capability ceilings, transports and protection ratings recorded; seven new findings raised.
- **command_register.md** — started, as required by P0-DOC-01 §8. Full B&K 2831E SCPI set transcribed verbatim with page citations and 5 internal documentation gaps flagged. Three instruments explicitly blocked.
- **instrument_profiles.yaml** — machine-readable configuration reference created for the application to load.
- **P0-DOC-03** — public manufacturer documentation searched. The **DAQ3120 programming manual (139 pp) was recovered in full and committed**, unblocking that instrument. The DAQ3120 user manual and B&K's DMM USB driver package were also retrieved and mined. Two earlier conclusions were corrected. Exact download URLs recorded for the two manuals this environment cannot reach.

---

## 4. Decisions made

| # | Decision | Basis |
|---|---|---|
| D-01 | 2831E DMMs are driven as **serial (USB Virtual COM)**, not USBTMC | Manufacturer manual p.40, p.71 |
| D-02 | The 2831E acquisition sequence is `TRIGger:SOURce BUS` → `*TRG` → `:FETCh?` | Only documented deterministic path; `:READ?`/`:MEASure?` undefined in the manual |
| D-03 | Pass/fail limits are evaluated **in the application**, not by instrument limit modes | 2831E has no SCPI limit subsystem |
| D-04 | Current is converted **in software**: `I = V × 1000` for the TCP404XL 1 A/mV range | TBS2000B is not on Tektronix's automatic-scaling list |
| D-05 | The current scale factor is **reviewed configuration**, stored with every run record | A later range change would silently invalidate stored results |
| D-06 | DAQ, scope and PSU drivers are **stubs that raise**, until manuals exist | Governing rule: never invent a hardware command |
| D-07 | Phase 1 (simulation skeleton) may begin; Phase 2 may not | Phase 1 requires no hardware documentation |
| D-08 | DAQ route layer defaults to `ROUTe:CLOSe:EXCLusive` (break-before-make) | Plain `ROUTe:CLOSe` leaves other channels closed and can short fixture points |
| D-09 | `INSTrument:DMM` is a connect-time decision, never toggled mid-sequence | Toggling it forces a factory reset that discards the scan list |
| D-10 | DMMs are enumerated by USB VID `0x10C4` + PID `0xEA60` + serial, never by COM-port order | CP210x bridge confirmed from B&K's own driver `.inf` |
| D-11 | `TPA-BNC` removed from the required-parts list | TekVPI accepts plain BNC directly; the adapter buys nothing without auto-scaling |
| D-12 | Degauss/autobalance becomes a mandatory pre-test operator step | The 50 Ω termination fault is detected only during degauss |

---

## 5. Open TBDs — every one needs an owner and a date

| ID | Item | Owner | Target |
|---|---|---|---|
| ~~T-01~~ | ~~DAQ3120 programming manual~~ | — | ✅ **CLOSED 2026-09-08** |
| T-02 | Tektronix programmer manual `077-1149-xx` — **URL in `P0-DOC-03` §5 #1**. *Upload attempted 2026-09-08; not present on `main` — re-check the commit landed* | **TBD** | **TBD** |
| T-03 | ITECH IT-M3906B manual **incl. P-IO pinout** — **URLs in `P0-DOC-03` §5 #2, #3**. *Upload attempted 2026-09-08; not present on `main` — re-check the commit landed* | **TBD** | **TBD** |
| T-04 | Fixture schematic, pin map, route table, forbidden combinations | **TBD** | **TBD** |
| T-05 | Safety-panel / contactor / AC-distribution schematics (COM-008) | **TBD** | **TBD** |
| T-06 | Engineer-approved V / I / P / discharge-time ceilings | **TBD** | **TBD** |
| T-07 | Nameplate photos, serial numbers, firmware, calibration — all instruments | **TBD** | **TBD** |
| T-08 | DAQ3120 installed module and slot list (F-DAQ-01) — **now readable via `SYSTem:CTYPe? <slot>` once connected** | **TBD** | **TBD** |
| T-09 | Current chain: probe model, 50 Ω feedthrough `011-0049-02`, `TPA-BNC` adapter, conductor, polarity, scope channel | **TBD** | **TBD** |
| T-10 | Router/switch model, IP plan, IT approval, Wi-Fi disabled | **TBD** | **TBD** |
| T-11 | One declared production transport per instrument | **TBD** | **TBD** |
| T-12 | Remote-sense (Vs+/Vs−) landing point and fault handling | **TBD** | **TBD** |
| T-13 | Facility three-phase feed vs. 6.5 kVA / 12.5 Aac derating | **TBD** | **TBD** |
| T-14 | Whether an ITECH anti-reverse protection unit is installed | **TBD** | **TBD** |
| T-15 | Is the **correct** rack kit fitted to the supply? IT-M3900B 1U needs `IT-E155A` (+B or C), not `IT-E151` | **TBD** | **TBD** |
| T-16 | CP210x serial-collision test with **both** DMMs connected (R-DMM-02) | **TBD** | **TBD** |
| T-17 | Current CP210x VCP driver for Win10/11 — the bundled one is from 2012 | **TBD** | **TBD** |
| T-18 | Confirm the 50 Ω feedthrough in the TCPA400 accessory kit before ordering one | **TBD** | **TBD** |

---

## 6. Known defects and hazards carried forward

| ID | Item |
|---|---|
| F-DAQ-01 | "60 channel with DM301" is inconsistent with one DM301 (20+2 ch). Implies 3× DM301, or a mis-identified module. |
| F-DAQ-02 | DAQ current channels are 1 A (DM301) / 2 A (DM309) — cannot measure the 240 A DUT path. |
| F-DAQ-03 | 4-wire measurement pairs bank-1 with bank-2 channels, roughly halving usable 4-wire points. |
| F-TCPA-01 | No automatic probe scaling on the TBS2000B — software must convert V→A. |
| F-TCPA-02 | TBS2104B has no 50 Ω input; external feedthrough required; amplifier fault flags are not machine-readable. |
| F-PSU-01 | Supply is bidirectional and grid-regenerative; Source/Load is a front-panel state. Belongs in the facility electrical review. |
| F-PSU-02 | "IT-E151 Rack Kit" is almost certainly ITECH `IT-E155A/B/C` — and should not be drawing AC power. |
| — | DAQ3120 rack height is 2U per datasheet vs 3U in drawing S1. |
| — | 2831E `:FETCh?` staleness hazard; no machine-readable error status; low-Ω ranges specified only under REL. |
| R-DAQ-02 | `INSTrument:DMM` toggle forces a factory reset — silently discards scan list and configuration. |
| R-DAQ-03 | Plain `ROUTe:CLOSe` does not open other channels; can short harness pins. Use `:EXCLusive`. |
| R-DAQ-06 | Module lineup is 7, not 5 — `DM307` (DAC + digital I/O) and `DM308` (Form C actuator) newly identified. |
| R-DMM-02 | CP210x bridges often share a factory serial string — serial-based port mapping may not disambiguate two identical meters. |
| R-TCPA-02 | The 50 Ω termination fault is detected **only** during degauss; a missing terminator otherwise gives a silent ~2× amplitude error. |
| R-PSU-01 | `IT-E151` is a real part but for the IT6900/IT8500+ families — possibly the wrong rack kit for this 1U supply. |

---

## 7. Single next action

**Start Phase 1: the simulation-mode application skeleton, using the scope and ready-to-paste prompt in `NEXT_STEP_BRIEF.md` §2–3.** The DAQ3120 now has a real transcribed command set, so its simulated driver can model the actual protocol rather than being a pure stub.

In parallel, a human must download the two manuals listed in `P0-DOC-03` §5 (about a minute each) and begin collecting T-04 through T-09. Phase 2 (any real transport, any hardware command) stays blocked until those land and are reviewed.

**CURRENT GATE: INCONCLUSIVE** — see `NEXT_STEP_BRIEF.md` §6 for the full DO THIS NEXT / SEND BACK block.
