# Generate Module Execution Setup

## Your Task

Scan the governance repo for the specified module and generate two files:
1. `.claude/commands/execute.md` — the slash command for phase execution
2. `governance-repo/modules/[MODULE]/execution-state.json` — current state tracker

---

## Input

Module name: **$ARGUMENTS**

Governance repo path: `governance-repo/modules/$ARGUMENTS/`

---

## Step 1 — Scan the governance repo structure

Run the following and capture the output:

```bash
find governance-repo/modules/$ARGUMENTS/packages/execution -type f -name "*.md" | sort
find governance-repo/modules/$ARGUMENTS/packages/test -type f -name "*.md" | sort
```

From the scan results:
- Identify all PHASES (top-level folders under `packages/execution/`)
- For each PHASE, identify all SUBs (files inside the phase folder, excluding `index.md`)
- Preserve the exact order from the filesystem sort
- For each SUB file, read the first 40 lines and count the number of tasks

Expected phases (in strict execution order):
`CORE → DATA-DOM → SVC-API → DOC → INT-C → INT-R → F1 → F2 → F3 → SEC → ALIGN`

Only include phases that actually exist in the scanned structure.

### Weight classification (record for Weight Map in execute.md):

| Weight | Criteria |
|--------|----------|
| LIGHT  | < 5 tasks, single layer |
| MEDIUM | 5–10 tasks, 1–2 layers |
| HEAVY  | > 10 tasks, multi-layer (Entity+Repo+Service+Controller) |
| XL     | Full backend feature OR 3+ frontend screens in one sub |

Record the weight and estimated task count for every sub found.

---

## Step 2 — Generate `execution-state.json`

Create the file at:
`governance-repo/modules/$ARGUMENTS/execution-state.json`

### Rules:
- `module` = the module name from $ARGUMENTS
- `current_phase` = first phase found in scan (status will be PENDING or IN_PROGRESS)
- `current_sub` = first sub of the first phase (null if phase has no subs)
- All phases start as `PENDING`
- All subs inside phases start as `PENDING`
- If a phase has only `index.md` and no sub files → `"subs": []`
- `blocked` and `deferred_xm` start as empty arrays

### Format:
```json
{
  "module": "[MODULE]",
  "generated_at": "[today's date]",
  "current_phase": "[FIRST_PHASE]",
  "current_sub": "[FIRST_SUB or null]",
  "phases": [
    {
      "id": "[PHASE_NAME]",
      "status": "PENDING",
      "subs": [
        { "id": "[SUB_NAME]", "status": "PENDING" }
      ]
    }
  ],
  "blocked": [],
  "deferred_xm": []
}
```

---

## Step 3 — Generate `.claude/commands/execute.md`

Create the file at:
`.claude/commands/execute.md`

### Content to generate:

The file must reference the exact phase names and sub names discovered in Step 1.
For each sub, record its estimated weight based on task count seen during scan:
- LIGHT  = < 5 tasks
- MEDIUM = 5–10 tasks
- HEAVY  = > 10 tasks or multi-layer (backend Entity+Repo+Service+Controller)
- XL     = full backend feature OR 3+ frontend screens in one sub

Generate the file with this structure:

```markdown
# /project:execute

Execute the current phase for the specified module — with context safety check.

## Usage
/project:execute [MODULE] [PHASE]

---

## STEP 0 — Context Safety Assessment (MANDATORY before any execution)

Before writing a single line of code, assess the execution load.

### 0.1 — Read state and identify scope

Read `governance-repo/modules/[MODULE]/execution-state.json`
Identify all PENDING subs in the requested phase.

### 0.2 — Look up sub weights from the Weight Map below

Each sub's weight was estimated at setup time from task count.
Use the Weight Map to classify the phase total without re-reading files.

### 0.3 — Classify phase total and decide chunking

| Phase Total                | Decision |
|----------------------------|----------|
| 1–2 LIGHT subs             | ✅ SAFE — execute all in one session |
| 1 MEDIUM sub               | ✅ SAFE — execute in one session |
| 2+ MEDIUM subs             | ⚠ CHUNK — one sub per session |
| Any HEAVY sub              | ⚠ CHUNK — each HEAVY sub = one session |
| Any XL sub                 | ⚠ CHUNK — split XL into layers across sessions |

### 0.4 — Print assessment and wait for confirmation

```
══════════════════════════════════════════════════════
EXECUTION ASSESSMENT: [PHASE] — module: [MODULE]
══════════════════════════════════════════════════════
Pending subs  : [list from state]
Total weight  : [SAFE / CHUNK RECOMMENDED]

Sub weights:
  [SUB-ID] → [LIGHT/MEDIUM/HEAVY/XL]
  [SUB-ID] → [LIGHT/MEDIUM/HEAVY/XL]

Execution plan:
  [If SAFE]
  → All pending subs in one session ✅
  → Proceed? (confirm to start)

  [If CHUNK]
  → Session 1: [SUB-IDs]
  → Session 2: [SUB-IDs]
  → ...
  → Proceed with Session 1? (confirm to start)
══════════════════════════════════════════════════════
```

WAIT for user confirmation. Do not execute before confirmation.

---

## STEP 1 — Execution (after confirmation)

### Per sub:

1. Read sub file completely:
   `governance-repo/modules/[MODULE]/packages/execution/[PHASE]/[SUB].md`
   (if no sub → `[PHASE]/index.md`)
2. Identify all tasks in the sub
3. Map each task to skill routing table in CLAUDE.md
4. Read required skills from `.github/skills/`
5. Execute all tasks in strict order
6. After last task → run `validate-backend-feature` or `validate-frontend-feature`
7. Update `execution-state.json`:
   - Mark sub as COMPLETE
   - Set `current_sub` to next PENDING sub in same phase
   - If no more subs → mark phase COMPLETE, set `current_phase` to next PENDING phase

### Blocked items — OQ / XM DEFERRED:
- OQ-blocked → skip, add to `blocked[]` in state
  Write in code: `// TODO: OQ-[ID] — pending resolution`
- XM DEFERRED → implement mock, add to `deferred_xm[]` in state
  Write in code: `// TODO: XM-[MOD]-[N] DEFERRED — replace when READY`
- Never stop the session for a blocked item — continue remaining tasks

---

## STEP 2 — Session completion report

```
══════════════════════════════════════════════════════
SESSION COMPLETE
══════════════════════════════════════════════════════
Phase         : [PHASE]
Session       : [1 of N / final]
Subs executed : [list]
Blocked       : [OQ-IDs / none]
XM Deferred   : [XM-IDs / none]
──────────────────────────────────────────────────────
[If more chunks remain:]
  Remaining   : [SUB-IDs]
  Next command: /project:execute [MODULE] [PHASE]
  (resumes from [next SUB-ID] automatically)

[If phase complete:]
  Phase status: ✓ COMPLETE
  Next phase  : [PHASE-NAME] — awaiting your instruction
══════════════════════════════════════════════════════
```

---

## Weight Map — [MODULE]

[Insert the actual weight map discovered in Step 1. Format:]

| Phase    | Sub              | Weight | Est. Tasks |
|----------|-----------------|--------|------------|
| CORE     | CORE            | [W]    | [N]        |
| DATA-DOM | DATA-DOM-MASTER | [W]    | [N]        |
| ...      | ...             | ...    | ...        |

---

## Phase Map — [MODULE]

[Insert the actual phase → subs map discovered in Step 1. Format:]

```
CORE        → CORE
DATA-DOM    → DATA-DOM-MASTER, DATA-DOM-REFERENCE
SVC-API     → SVC-API-CRUD, SVC-API-INT
...
```

---

## Constraints (NON-NEGOTIABLE)

- NEVER skip STEP 0 — assessment is mandatory before every execution
- NEVER execute without user confirmation after assessment
- NEVER skip a sub within the planned chunk
- NEVER invent field or column names — always look up db-script.md
- NEVER copy QRC entries as production code — read intent, write implementation
- NEVER implement a blocked OQ item — mark and skip only
- NEVER advance to next phase without explicit instruction from user
- ALWAYS update execution-state.json after every sub
```

---

## Step 4 — Verify and report

After generating both files, print:

```
══════════════════════════════════════════════════════
MODULE SETUP COMPLETE: [MODULE]
══════════════════════════════════════════════════════
execution-state.json  ✓  governance-repo/modules/[MODULE]/
execute.md            ✓  .claude/commands/

Phases detected       : [count]
Total subs detected   : [count]

Weight map:
  [PHASE] / [SUB]  → [LIGHT/MEDIUM/HEAVY/XL]  ([N] tasks)
  [PHASE] / [SUB]  → [LIGHT/MEDIUM/HEAVY/XL]  ([N] tasks)
  ...

Heavy phases (require chunking):
  [PHASE] → [reason]   (or "none — all phases safe")

To start execution:
  /project:execute [MODULE] [FIRST_PHASE]
  → Assessment will be shown before any code is written
══════════════════════════════════════════════════════
```
