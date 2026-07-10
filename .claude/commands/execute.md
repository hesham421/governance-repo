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
| 1 MEDIUM sub                | ✅ SAFE — execute in one session |
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
`API-ALIGNMENT` phase `COMPLETE` in `execution-state.json` (adding the phase
entry to `phases[]` if it is not already present) and print:

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

## Weight Map — ORG

| Phase        | Sub                      | Weight | Est. Tasks |
|--------------|--------------------------|--------|------------|
| CORE         | CORE                     | LIGHT  | 1 (architecture/package policy, no per-entity tasks) |
| DATA-DOM     | DATA-DOM-CORE-ENTITIES   | HEAVY  | 8 entities × fields+domain rules+queries, multi-layer |
| DATA-DOM     | DATA-DOM-HEADER          | LIGHT  | 0 (preamble/pointer only) |
| SVC-API      | SVC-API-CRUD             | XL     | 44 endpoints across 7 entities, full backend feature |
| SVC-API      | SVC-API-HEADER           | MEDIUM | 44-row strategy table, audit + repository-layer fixes |
| SVC-API      | SVC-API-TREE             | LIGHT  | 2 (Department/CostCenter tree endpoints) |
| DOC          | DOC                      | LIGHT  | 3 (contract-stabilization audit, no code) |
| INT-C        | INT-C                    | LIGHT  | 1 (XM register audit, no code) |
| INT-R        | INT-R                    | LIGHT  | 1 (vacuous — no outbound XM-IDs) |
| DB-ALIGNMENT | DB-ALIGNMENT             | LIGHT  | 1 (94-field DBF↔FIELD manifest audit, no code) |
| F1           | F1-HEADER                | LIGHT  | 0 (preamble/pointer only) |
| F1           | F1-SCR-ORG-001..007      | LIGHT  | 1 each (single TS model interface) |
| F2           | F2-HEADER                | LIGHT  | 0 (preamble/pointer only) |
| F2           | F2-SCR-ORG-001..007      | MEDIUM | 6–8 each (Service + Facade, 2 layers) |
| F3           | F3-HEADER                | LIGHT  | 0 (preamble/pointer only) |
| F3           | F3-SCR-ORG-001..007      | LIGHT  | 1–2 each (entry-form validation notes) |
| SEC          | SEC                      | MEDIUM | 7 screens × VIEW/CREATE/UPDATE/DEACTIVATE permission wiring |
| ALIGN        | ALIGN                    | LIGHT  | auto-run consistency gate, no code |

`API-ALIGNMENT` has no static sub file — it is a procedural phase (see
"API-ALIGNMENT — Special Phase Procedure" above), driven by diffing
`api-docs/` against `execution-plan.md` at run time.

---

## Phase Map — ORG

```
CORE          → CORE
DATA-DOM      → DATA-DOM-CORE-ENTITIES, DATA-DOM-HEADER
SVC-API       → SVC-API-CRUD, SVC-API-HEADER, SVC-API-TREE
DOC           → DOC
INT-C         → INT-C
INT-R         → INT-R
DB-ALIGNMENT  → DB-ALIGNMENT
API-ALIGNMENT → (procedural — no sub files, see Special Phase Procedure)
F1            → F1-HEADER, F1-SCR-ORG-001, F1-SCR-ORG-002, F1-SCR-ORG-003,
                 F1-SCR-ORG-004, F1-SCR-ORG-005, F1-SCR-ORG-006, F1-SCR-ORG-007
F2            → F2-HEADER, F2-SCR-ORG-001, F2-SCR-ORG-002, F2-SCR-ORG-003,
                 F2-SCR-ORG-004, F2-SCR-ORG-005, F2-SCR-ORG-006, F2-SCR-ORG-007
F3            → F3-HEADER, F3-SCR-ORG-001, F3-SCR-ORG-002, F3-SCR-ORG-003,
                 F3-SCR-ORG-004, F3-SCR-ORG-005, F3-SCR-ORG-006, F3-SCR-ORG-007
SEC           → SEC
ALIGN         → ALIGN
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
