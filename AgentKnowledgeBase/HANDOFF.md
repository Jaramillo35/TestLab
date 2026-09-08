# HANDOFF — resuming this project on another machine

**Last updated:** 2026-09-08
**Repository:** `https://github.com/Jaramillo35/TestLab` — everything needed is on `main`
**Purpose:** let a person or an agent pick this project up cold, on any machine, without reconstructing context.

---

## 1. What this repository is, in three sentences

It is the **knowledge base** for the *Vehicle Harness Functional Tester* — a rack of instruments (two B&K 2831E multimeters, a B&K DAQ3120 data acquisition system, a Tektronix TBS2104B oscilloscope, a TCPA400 current-probe amplifier, and an ITECH IT-M3906B-32-240 regenerative DC supply) that a Python application will eventually drive for automotive wiring-harness testing.

**There is no application code yet.** The repository holds manufacturer documentation, the facts extracted from it, the reviewed command register, and a Phase 1 build brief.

The project is at **Phase 0, gate INCONCLUSIVE**. Phase 1 (a simulation-only application skeleton) is unblocked and is the next thing to build.

---

## 2. Resume in five minutes

```bash
git clone https://github.com/Jaramillo35/TestLab
cd TestLab
```

Then read, in this order — the whole set is about 20 minutes:

| Order | File | Why |
|---:|---|---|
| 1 | `AgentKnowledgeBase/PROJECT_STATUS.md` | Phase, gate, decisions D-01…D-12, open TBDs T-02…T-18, single next action |
| 2 | `AgentKnowledgeBase/NEXT_STEP_BRIEF.md` | Phase 1 scope, acceptance gate, and a **ready-to-paste coding prompt** in §3 |
| 3 | `AgentKnowledgeBase/README.md` | Reading order and the three overriding rules |
| 4 | `AgentKnowledgeBase/command_register.md` | The only legitimate source of a hardware command |

If you are an **agent** being started fresh, this single prompt is enough to begin:

```text
Read AgentKnowledgeBase/PROJECT_STATUS.md and AgentKnowledgeBase/NEXT_STEP_BRIEF.md.
Confirm the current phase and gate back to me, then follow the Phase 1 prompt in
NEXT_STEP_BRIEF.md section 3. Do not start Phase 2.
```

---

## 3. Machine requirements

### To run Claude Code and work on the documents

- **Node.js** — Claude Code is a Node CLI. Node 18+ has been the baseline; check the current requirement in the official install docs rather than trusting this line.
- **Git**, and a GitHub credential that can push to `Jaramillo35/TestLab`.
- **Python 3.11+** with `pypdf` if you want to re-extract text from the PDFs.

That is all the documentation work needs, and it runs comfortably on a Raspberry Pi 4 or 5 with 64-bit Raspberry Pi OS.

### To build and run the Phase 1 application

Phase 1 targets **PySide6** (per the project plan). Two things to verify **before** committing to a particular machine as the app host:

1. **PySide6 on arm64.** Qt wheel availability for `aarch64` Linux has historically been inconsistent. Confirm `pip install PySide6` actually works on your target before designing around it. If it does not, that is a real constraint to raise, not something to work around silently.
2. **A desktop session.** The Phase 1 acceptance gate requires a screenshot of the app window. Headless SSH will not produce one; you need a desktop, VNC, or an X/Wayland forward.

### A decision this repository has NOT made

`P0-DOC-01` lists the **main test PC (EQ-001) as `TBD`** — model, OS, ports, security policy and ownership are all unrecorded.

If a Raspberry Pi is being considered for that role, treat it as an engineering decision and write it down, because the station has to:

- hold a USB serial link to **two** CP210x multimeters plus LAN links to three instruments;
- pull **5 Mpt** waveform records off the oscilloscope;
- run the GUI, the test engine, logging, an SQLite database and PDF reporting;
- and sit in the control path of a **6 kW, 240 A bidirectional supply that can feed energy back into the building.**

None of that makes a Pi wrong. It does make "which machine is EQ-001" something that belongs in `PROJECT_STATUS.md` with an owner, not something that gets decided by whichever laptop happened to be free.

---

## 4. State at handoff

| | |
|---|---|
| Phase / gate | **P0 / INCONCLUSIVE** |
| `real_mode_enabled` | **false** |
| `real_output_control_enabled` | **false** |
| Approved hardware commands | **0** |
| Instruments with a transcribed command set | **2 of 4** — B&K 2831E, B&K DAQ3120 |
| Instruments still blocked | **2** — Tektronix TBS2104B, ITECH IT-M3906B |
| Application code | **none yet** |

**Blocked because two manuals are missing.** Both were located; the environment this work was done in could not reach their hosts. Exact URLs are in `P0-DOC-03_internet_research_findings.md` §5, and were emailed to `martinjaramillo35@gmail.com` on 2026-09-08. Each is a one-minute download on an unrestricted network:

1. Tektronix TBS2000B Series Programmer Manual → unblocks every oscilloscope command.
2. ITECH IT-M3900B Series Programming Guide (EN) → unblocks every power-supply command.
3. ITECH IT-M3900B Series User Manual → the **P-IO pinout**, which is the candidate hardwired interlock path for the safety chain.

Drop them into `AgentKnowledgeBase/manuals/` and the register can be extended.

---

## 5. Rules that must survive the handoff

These are not style preferences. They come from the project's own agent charter and they are the reason this repository is trustworthy.

1. **Never invent a hardware command.** A command may only be used if it appears in `command_register.md` with a page citation from the manufacturer manual for the **exact model and firmware**. Similarity to another model is not evidence. Neither is a search-engine summary, a distributor page, a wiki, or a third-party Python package — `P0-DOC-03` §0 defines the evidence tiers, and only Tier-A may become a command.
2. **A capability is not a limit.** Every number in `P0-DOC-02` is what an instrument *can* do. The engineer-approved operating limits are all `TBD`, and `TBD` means the application refuses to run that path in Real mode. Never substitute a datasheet maximum for an approved limit.
3. **Simulation-first, output off.** Simulation must never open VISA, serial, sockets, or any real instrument resource. Output OFF must be asserted on normal completion, abort, timeout, comms loss, interlock open, exception and application close.
4. **Physical safety works without the PC.** E-stop, interlocks, contactors and fusing are hardware functions. Software may *monitor* safety state; it never *is* the safety function, and it must never claim a verified safe state it cannot actually observe.
5. **Never weaken a test or a safety assertion to get a pass.**

---

## 6. Gotchas that will bite whoever resumes

| Thing | Why it matters |
|---|---|
| `P0-DOC-02` is partly superseded | `P0-DOC-03` corrected three of its conclusions (TPA-BNC, the 50 Ω terminator, and the IT-E151 rack kit) and expanded a fourth. A banner at the top of `P0-DOC-02` lists them. **Where the two disagree, `P0-DOC-03` wins.** |
| The DAQ3120 **user** manual is not in the repo | It is 134 MB, over GitHub's 100 MB file limit. It was read and mined; the URL is in `P0-DOC-03` §5 #6. Do not assume it was overlooked. |
| `manuals/DAQ3120_programming_manual.pdf` **is** in the repo | 139 pp, version 2026-01-07. This is the one that unblocked the DAQ. |
| Plain `ROUTe:CLOSe` can short harness pins | It closes channels without opening others. `ROUTe:CLOSe:EXCLusive` is the mandated default (decision D-08). |
| `INSTrument:DMM` toggling forces a factory reset | It silently discards the scan list and all channel configuration. Connect-time decision only (D-09). |
| The two 2831E meters may share a USB serial | CP210x bridges often ship with identical factory serials. Test with both connected (T-16) before relying on serial-based port mapping. |
| The 2831E has no error-status query | Unlike the DAQ3120. Its error state is not machine-readable — rely on response parsing and timeouts, and do not fabricate a health check. |
| The unverified ITECH P-IO pin list | `P0-DOC-03` §4.4 records one, marked **do-not-wire**. It came from a summary of the IT-M3900**D** manual, not the **B**. Nobody wires a 240 A bidirectional supply's inhibit line from a search result. |

---

## 7. Single next action

**Build the Phase 1 simulation-mode application skeleton**, using the scope in `NEXT_STEP_BRIEF.md` §2 and the ready-to-paste prompt in §3. It needs no hardware and no further documentation.

In parallel, a human should download the three manuals in §4 above and start collecting the physical checks in `PROJECT_STATUS.md` §5 (T-04 through T-09).

Phase 2 — any real transport, any hardware command, any energized test — stays blocked until those land, are reviewed, and the responsible engineer authorizes it.

---

## 8. Git layout

- `main` — current, contains everything described here.
- `claude/gmail-attachment-download-o6dpws` — the working branch these documents were built on. Merged into `main`; kept for history. The branch name is an artifact of how the session started and has nothing to do with the contents.

Nothing is stashed, nothing is uncommitted, and there are no open pull requests.
