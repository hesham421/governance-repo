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
`CORE → DATA-DOM → SVC-API → DOC → INT-C → INT-R → DB-ALIGNMENT → API-ALIGNMENT → F1 → F2 → F3 → SEC → ALIGN`

Only include phases that actually exist in the scanned structure.

`DB-ALIGNMENT` and `API-ALIGNMENT` are audit/reconciliation phases, not
CRUD-task phases — see "Special phase execution" in Step 3 for how
`API-ALIGNMENT` is handled differently by execute.md. `API-ALIGNMENT` MUST
be COMPLETE before F1 is allowed to start (see STEP 0.4).

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
- `blocked`, `deferred_xm`, and `api_doc_gaps` start as empty arrays

### Format:
```json
{
  "module": "[MODULE]",
  "generated_at": "[today's date]",
  "current_phase": "[FIRST_PHASE]",
  "current_sub": "[FIRST_SUB or null]",
  "api_docs_path": "governance-repo/modules/[MODULE]/api-docs/",
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
  "deferred_xm": [],
  "api_doc_gaps": []
}
```

### `api_doc_gaps[]` entry format (populated by the API-ALIGNMENT phase and, as a
safety net, during F1/F2/F3 execution — see execute.md's API-ALIGNMENT
procedure and STEP 1.5):
```json
{
  "type": "MISSING_IN_DOCS | CONFLICT_RESOLVED_VIA_PLAN_UPDATE | CONFLICT_FLAGGED_BACKEND_FIX | CONFLICT_PENDING_DECISION",
  "phase": "[PHASE]",
  "sub": "[SUB or null]",
  "endpoint": "[METHOD] [path]",
  "detail": "[what was missing, or what execution-plan.md said vs what api-docs says]",
  "resolution": "[what was done: 'edited execution-plan.md task [X] to match api-docs' / 'flagged for backend fix — SRS/plan intent is correct, backend deviates' / 'resolved via backend source: <path>' / 'implemented per api-docs provisionally — awaiting your decision']",
  "decided_by": "user | provisional",
  "recorded_at": "[timestamp]"
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

### 0.4 — API-ALIGNMENT Precondition Check (frontend phases only: F1, F2, F3)

This check runs ONLY when the requested phase is F1, F2, or F3. It does NOT
run for CORE, DATA-DOM, SVC-API, DOC, INT-C, INT-R, DB-ALIGNMENT,
API-ALIGNMENT itself, SEC, or ALIGN.

1. Read `execution-state.json`, find the phase entry with `id: "API-ALIGNMENT"`.
2. If that phase does not exist in `phases[]`, or its `status` is not
   `COMPLETE`:

```
══════════════════════════════════════════════════════
⛔ API-ALIGNMENT PRECONDITION FAILED — module: [MODULE]
══════════════════════════════════════════════════════
Phase status  : [MISSING / PENDING / IN_PROGRESS]

Frontend execution cannot start until API-ALIGNMENT is COMPLETE.
This phase reconciles api-docs (real backend) against execution-plan.md's
API references before any frontend code is written against them.

Action required:
  /project:execute [MODULE] API-ALIGNMENT

══════════════════════════════════════════════════════
```

   STOP here. Do not proceed to 0.5, do not execute any task.

3. If API-ALIGNMENT is COMPLETE → proceed to 0.5.

### 0.5 — Print assessment and wait for confirmation

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

## API-ALIGNMENT — Special Phase Procedure

If the requested `[PHASE]` is `API-ALIGNMENT`, follow THIS procedure instead
of the generic per-sub loop in STEP 1. This phase reconciles `api-docs`
(the real, implemented backend) against `execution-plan.md`'s API references
(B2/INT) for every endpoint the upcoming F1/F2/F3 tasks will depend on.
It never writes application code.

### A1 — Precondition
Confirm `api-docs/index.md` exists at `[api_docs_path]` (default
`governance-repo/modules/[MODULE]/api-docs/`). If missing:

```
⛔ api-docs not found at [api_docs_path]
Generate it first (outside this session):
  python3 generate.py --module [MODULE] --function generate
```
STOP here — do not mark API-ALIGNMENT COMPLETE.

### A2 — Diff every referenced endpoint
For every endpoint that execution-plan.md's B2/INT sections reference for
this module:
1. Read the contract from `api-docs/endpoints/<group>/<slug>.md`.
2. Read execution-plan.md's description of that same endpoint's contract.
3. Diff: path, method, request/response fields, types, required/optional,
   validation, enums, error codes.
4. Record every mismatch found.

### A3 — Present conflicts and ask for a per-conflict decision
Never resolve a conflict unilaterally — this is a judgment call (SRS intent
vs actual backend), not something to auto-decide. For each mismatch:

```
══════════════════════════════════════════════════════
⚠ API-ALIGNMENT CONFLICT [n] — module: [MODULE]
══════════════════════════════════════════════════════
Endpoint          : [METHOD] [path]
execution-plan.md : [what the plan says]
api-docs (real)   : [what the backend actually does]
──────────────────────────────────────────────────────
How should this be resolved?
  (a) Plan is outdated — update execution-plan.md to match api-docs
  (b) Backend is wrong — SRS/plan intent is correct, flag backend for a fix
══════════════════════════════════════════════════════
```

WAIT for the user's choice on each conflict (batch multiple conflicts into
one prompt if there are several — but do not proceed on any of them without
an explicit answer).

- **(a) chosen** → edit the referenced contract note in execution-plan.md's
  task description to match api-docs. Log:
  `{ "type": "CONFLICT_RESOLVED_VIA_PLAN_UPDATE", "resolution": "edited execution-plan.md task [X] to match api-docs", "decided_by": "user" }`
- **(b) chosen** → do NOT edit execution-plan.md or api-docs. Log:
  `{ "type": "CONFLICT_FLAGGED_BACKEND_FIX", "resolution": "flagged for backend fix — SRS/plan intent is correct, backend deviates", "decided_by": "user" }`
  This blocks nothing by itself, but the flagged endpoint stays a known,
  visible discrepancy until the backend team resolves it.

### A4 — Complete the phase
Once every conflict found in A2 has a logged decision (a or b) — mark
`API-ALIGNMENT` phase `COMPLETE` in `execution-state.json` and print:

```
══════════════════════════════════════════════════════
API-ALIGNMENT COMPLETE — module: [MODULE]
══════════════════════════════════════════════════════
Endpoints checked      : [N]
Conflicts found        : [N]
  → resolved via plan update : [N]
  → flagged for backend fix  : [N]
Clean (no conflict)    : [N]
──────────────────────────────────────────────────────
F1 is now unblocked. Next: /project:execute [MODULE] F1
══════════════════════════════════════════════════════
```

If any conflicts were flagged for backend fix (option b), repeat that count
prominently — F1 is still unblocked (frontend work can proceed against
api-docs, which is real and callable), but those endpoints carry a known,
open discrepancy until backend is fixed.

---

## STEP 1 — Execution (after confirmation)

This generic per-sub loop applies to every phase EXCEPT `API-ALIGNMENT`
(see its own procedure above).

### Per sub:

1. Read sub file completely:
   `governance-repo/modules/[MODULE]/packages/execution/[PHASE]/[SUB].md`
   (if no sub → `[PHASE]/index.md`)
2. Identify all tasks in the sub
2.5. **[Frontend phases F1/F2/F3 only] API Contract Resolution** — see STEP 1.5
   below. Resolve every endpoint contract this sub's tasks depend on BEFORE
   writing implementation code for those tasks.
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

## STEP 1.5 — API Contract Resolution (frontend phases F1/F2/F3 only)

This step runs for every task in F1/F2/F3 that calls or models a backend
endpoint, before that task's code is written. It does NOT apply to
CORE/DATA-DOM/SVC-API/DOC/INT-C/INT-R/SEC/ALIGN — those phases either
implement the backend itself or don't touch API contracts directly.

**Priority order for API contract facts (path, method, request/response
fields, types, required/optional, validation, enums, headers, error codes,
permissions):**

```
1st — api-docs/endpoints/<group>/<slug>.md   (real backend, generated)
2nd — backend source directly                (ONLY if api-docs doesn't have it)
      (controller / DTO / service under the module's backend source root)
3rd — never invent a field, type, path, or endpoint name, under any
      circumstance, regardless of what execution-plan.md implies
```

execution-plan.md (B2 APIs / INT Summary) tells you WHICH endpoint a task
calls and WHY (the flow/logic). api-docs tells you WHAT the endpoint's real
contract is. Both are needed — neither replaces the other.

### 1.5.1 — Resolve from api-docs (default path)
1. From the task, identify the endpoint (method + path, or operationId)
   referenced in execution-plan.md.
2. Open the matching `api-docs/endpoints/<group>/<slug>.md`.
3. Extract the fields/contract details the task needs.
4. Implement the task against these values.

### 1.5.2 — Conflict detected mid-execution (post-alignment drift)
This should be rare — API-ALIGNMENT already reconciled every endpoint
execution-plan.md references before F1 started. If one still surfaces here
(e.g. a task touches an endpoint API-ALIGNMENT didn't cover, or something
shifted since), do NOT silently decide which side is right — that's a
judgment call, same as in API-ALIGNMENT.
- Implement the task against **api-docs** provisionally, so work isn't
  blocked (api-docs is real and callable).
- Record it:
  ```
  // TODO: api_doc_gap CONFLICT_PENDING_DECISION — execution-plan.md said "[X]",
  // api-docs says "[Y]" — implemented per api-docs provisionally, pending your decision
  ```
- Add an entry to `api_doc_gaps[]`:
  `{ "type": "CONFLICT_PENDING_DECISION", "phase", "sub", "endpoint", "detail", "resolution": "implemented per api-docs provisionally — awaiting your decision", "decided_by": "provisional" }`
- Surface every `CONFLICT_PENDING_DECISION` entry prominently in the Session
  Completion Report (STEP 2) so it gets a real decision afterward — same
  two options as A3 (update plan / flag backend).
- Continue execution — do not stop the session for this.

### 1.5.3 — Detail missing from api-docs entirely (last resort only)
Only when api-docs genuinely has no answer — matches the tool's documented
best-effort gaps (per-endpoint error responses, undiscoverable enum/operator
values, best-effort permissions, etc.) — go directly to the backend source:
1. Locate the controller/DTO/service in the module's backend source tree.
2. Read only what's needed to resolve the specific missing detail — do not
   re-derive the whole contract from source when api-docs already covers it.
3. Implement against what you found.
4. Record it:
   ```
   // TODO: api_doc_gap MISSING_IN_DOCS — [detail] not in api-docs,
   // resolved from backend source: [path]
   ```
5. Add an entry to `api_doc_gaps[]`:
   `{ "type": "MISSING_IN_DOCS", "phase", "sub", "endpoint", "detail", "resolution": "resolved via backend source: <path>" }`
6. Continue execution — do not stop the session for this.

**Never skip straight to backend source as a shortcut** — 1.5.1 (api-docs)
is always tried first; 1.5.3 is a documented exception path, not a default.

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
API Doc Gaps  : [count — MISSING_IN_DOCS: N, CONFLICT_PENDING_DECISION: N / none]
  [If CONFLICT_PENDING_DECISION > 0:]
  ⚠ [N] endpoint(s) need your decision (plan update vs backend fix) — see api_doc_gaps[]
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
- NEVER start F1/F2/F3 execution unless the `API-ALIGNMENT` phase is
  `COMPLETE` in execution-state.json (STEP 0.4)
- NEVER resolve an API-ALIGNMENT conflict (execution-plan.md vs api-docs)
  unilaterally — always present both sides and wait for the user's
  decision (update plan / flag backend fix); this applies both inside the
  API-ALIGNMENT phase (A3) and to any drift caught later during F1/F2/F3 (1.5.2)
- NEVER mark API-ALIGNMENT COMPLETE while any detected conflict lacks a
  logged decision
- NEVER implement a frontend task that calls a backend endpoint without
  first resolving its contract from api-docs (STEP 1.5.1)
- NEVER go directly to backend source for a frontend task's API contract
  unless the detail is confirmed absent from api-docs (STEP 1.5.3) —
  and always log that fallback in api_doc_gaps[]
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
API-ALIGNMENT phase detected : [✓ found in scan / ✗ not found — add it before running F1]
F1/F2/F3 gated on API-ALIGNMENT COMPLETE + wired to STEP 1.5 : ✓
api_docs_path         : governance-repo/modules/[MODULE]/api-docs/
  (must be generated manually beforehand via api-doc-generator's
   `python3 generate.py --module [MODULE] --function generate` —
   this setup script does not check for it; the API-ALIGNMENT phase
   checks at runtime)

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
