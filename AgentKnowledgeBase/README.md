# AgentKnowledgeBase — reading order

Knowledge base for the **Vehicle Harness Functional Tester** project. Read in this order.

| # | File | What it is |
|---|---|---|
| 0 | `HANDOFF.md` | **New machine or new agent? Start here instead.** Clone-and-resume steps, machine requirements, state at handoff, and the gotchas. |
| 1 | `PROJECT_STATUS.md` | **Start here.** Current phase, gate, decisions, open TBDs, single next action. |
| 2 | `NEXT_STEP_BRIEF.md` | What to build next, the acceptance gate, and a ready-to-paste coding prompt. |
| 2b | `COPILOT_PROMPTS.md` | **Driving GitHub Copilot?** The Phase 1 build as five sequenced, ready-to-paste prompts, plus what to reject when Copilot goes wrong. |
| 3 | `P0-DOC-01_equipment_and_communication_inventory.md` | Equipment and planned communication inventory, from two planning drawings. |
| 4 | `P0-DOC-02_instrument_datasheet_extract.md` | Every fact the manufacturer PDFs establish, with page citations — plus what they don't. **Two conclusions corrected by doc 5.** |
| 5 | `P0-DOC-03_internet_research_findings.md` | What public manufacturer documentation added, what it corrected, and the exact URLs for the manuals still missing. |
| 5b | `P0-DOC-04_uploaded_manuals_extract.md` | The five manuals uploaded 2026-09-08: ITECH **P-IO pinout**, the provisional Tektronix manual, TCPA degauss/termination, and the rack-kit answer. **Corrects P0-DOC-03 §4.1.** |
| 6 | `command_register.md` | The only place a hardware command may come from. 0 approved entries today. |
| 7 | `instrument_profiles.yaml` | Machine-readable configuration the application loads. |
| — | `m365_copilot_agent_setup_for_harness_tester (1).md` | Configuration for the M365 coordinator agent. Reference. |
| — | `../.github/copilot-instructions.md` | Repo-wide rules GitHub Copilot loads automatically. Not optional context. |

## Source PDFs (repository root)

| File | Type | Contains commands? |
|---|---|---|
| `bk_precision_2831e_manual.pdf` | User + programming manual, 71 pp | **Yes — full SCPI set** |
| `bk_precision_2831e_datasheet.pdf` | Datasheet | No |
| `DAQ3120_datasheet.pdf` | Datasheet | No |
| `Tektronix_TBS2104b.pdf` | Datasheet | No |
| `TCPA400.pdf` | Datasheet | No |
| `IT-M3906B-32-240_en.pdf` | Datasheet | No |
| `manuals/DAQ3120_programming_manual.pdf` | **Programming manual, 139 pp, v2026-01-07** | **Yes — full SCPI set** |
| `manuals/IT-M3900B-User-Manual.pdf` | User manual, 348 pp | No — hardware interfaces + **P-IO pinout** |
| `manuals/TBS2000-Programmer-077114902.pdf` | Programmer, 342 pp — **TBS2000, NOT TBS2000B** | **Provisional only** — simulated driver design, never Real mode |
| `manuals/TCPA300-400-…-077118302.pdf` | User manual, 82 pp | No — degauss, termination, safety |
| `manuals/ITECH-Rack-Mount-Kits-Selection-Guide.pdf` | Selection guide, 8 pp | No |
| `manuals/itech-it-m3900b-pv3900-software-user-manual.pdf` | PC software manual, 107 pp | **No — contains zero SCPI** |

## Three rules that override anything else

1. **Never invent a hardware command.** A command may be used only if it appears in `command_register.md` with a manual page citation for the exact model *and* firmware. Two of the four instruments are `BLOCKED` because their manuals are not here. Similarity to another model is not evidence, and neither is a search-engine summary, a distributor page, or a wiki — see the evidence tiers in `P0-DOC-03` §0.
2. **A capability is not a limit.** Every number in `P0-DOC-02` is what the instrument *can* do. Approved operating limits are all `TBD`, and `TBD` means the application refuses to run that path in Real mode.
3. **Simulation-first, output off.** `real_mode_enabled` and `real_output_control_enabled` stay `false`. Simulation must never open VISA, serial, sockets, or any real instrument resource. Physical safety — E-stop, interlocks, contactors, fusing — must work without the PC.
