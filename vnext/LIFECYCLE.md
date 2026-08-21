# Hotel Lifecycle Gates

## A. Design Hotel (Mode 4.1)

Performed by permanent Staff / Architect, not an ordinary Guest.

### Inputs

- `DESIGN_SPEC.md`;
- `ROADMAP.md`;
- `CURRENT_STATE.md`;
- active `DECISION_LOG.md` decisions;
- phase objective;
- source/code/artifact state required for this phase.

### Design outputs

- `HOTEL_MANIFEST.json` including `control_ref`, `integration_ref`, `forbidden_write_paths`, and retention policy;
- dependency graph;
- `RECEPTION.md` draft;
- one Room manifest + `START_HERE.md` per planned Room;
- compiled Room `input/` and `skills/` available now or explicit BLOCKED dependency-produced packet requirements;
- authority/write ownership map;
- deterministic validation result.

### Design rule

A Room is not complete merely because it has a task title. A fresh Guest must be able to execute a READY Room from its pinned control packet + claim-base source without studying the full project or Team Repo.

## B. Validate / Ready to Open

Before `READY_TO_OPEN`, verify:

1. manifests conform to schema;
2. Room IDs/dependencies form a valid DAG and manifest/entry paths are complete;
3. every dependency refers to a real Room;
4. all initially READY Rooms have resolved `claim_base_sha`;
5. all required compiled inputs/skills for initially READY Rooms exist on control plane;
6. required source-read paths for initially READY Rooms exist in their claim-base trees;
7. Room packets contain objective, context, loadout, authority, write/return allowlists, checks, acceptance, return, and escalation contract;
8. simultaneously claimable Rooms have no production write overlap and no Room write overlaps Hotel-wide forbidden paths;
9. `hotel_base_sha` identifies the intended immutable Hotel origin;
10. intended `control_ref` and `integration_ref` strategy is explicit;
11. Reception matches dependency readiness and states its control ref;
12. claim namespace is reserved for this Hotel and remote collision checks are defined;
13. project `CURRENT_STATE.md` is ready to point to the active Hotel/control ref when opened.

Validation success moves `DRAFT → VALIDATED → READY_TO_OPEN`. Claims remain disabled.

## C. Open Hotel (Mode 4.2)

Opening is a coordinator/owner-authorized control transition:

1. commit the exact intended control packet on `control_ref`;
2. run structural + Git opening validation on that exact control-ref head;
3. verify `hotel_base_sha`, initial READY Room `claim_base_sha` values, and integration ref;
4. perform remote opening checks, including absence of active claim refs for this Hotel instance;
5. set lifecycle `OPEN` + `claims_enabled=true` and refresh Reception on `control_ref`;
6. update project `CURRENT_STATE.md` with active Hotel ID/phase/control pointer and next action under project policy;
7. commit/push the opening control/project state;
8. verify the exact remote `control_ref` opening commit and project pointer;
9. only then may Guests claim Rooms.

A copied prompt, chat statement, old Reception, stale local branch, or unpushed file cannot open a Hotel.

## D. Guest execution

While OPEN:

- Guest fetches latest remote `control_ref` and pins `control_commit_sha` before selecting a Room;
- Guest atomically creates exactly one fixed claim branch from that Room's `claim_base_sha`;
- claim record preserves `control_ref`, `control_commit_sha`, `claim_base_sha`, session/claim identity;
- Room packet inputs/skills are read from pinned control commit;
- project source is read/written on the claim branch under source/write/return boundaries;
- returns preserve both pins and final head;
- reviewer evaluates the exact pinned Room contract, not a newer moving control ref.

## E. Acceptance / dependency transition

For an accepted Room:

1. verify return evidence, diff scope, checks, acceptance criteria, and domain quality against pinned control contract;
2. integrate/materialize accepted output on `integration_ref` / canonical source under project policy;
3. record accepted claim head + integration commit;
4. compile newly available dependency context into downstream Room `input/` packet(s);
5. resolve downstream `claim_base_sha` to the intended integration/source commit;
6. transition newly-unblocked Rooms to READY on `control_ref`;
7. refresh Reception;
8. push/verify the new remote control commit before exposing those Rooms.

## F. Rework / Blocked / Stale

- `REWORK`: reviewer returns bounded evidence/criteria; a new control snapshot/base may be issued.
- `BLOCKED`: unresolved dependency/input/base/authority/source/decision/tool; do not disguise as failure or readiness.
- `STALE`: derived abandoned-claim condition; only coordinator/housekeeping may archive/recover it through `CLAIM_PROTOCOL.md`.

Retries preserve attempt evidence without expanding context for new Guests.

## G. Close Hotel (Mode 4.3 — closure)

Enter `CLOSING` by disabling new claims on `control_ref` first and remotely verifying that transition.

Closure gate requires:

1. all required Rooms `ACCEPTED` or explicitly waived by durable owner decision;
2. accepted outputs integrated/materialized into canonical project source;
3. no accepted result exists only on a temporary claim branch;
4. required deterministic/project checks pass or documented owner exception exists;
5. unresolved blockers/waivers are reflected in project truth;
6. durable decisions are in `DECISION_LOG.md`;
7. `CURRENT_STATE.md` states phase result and next project action;
8. `DESIGN_SPEC.md`/`ROADMAP.md` change only when durable scope/direction changed;
9. minimal Hotel history is prepared with per-Room control/base/head/integration evidence;
10. temporary refs/worktrees/packets are inventoried for retention/demolition.

After the closure control/project commits are remotely verified, lifecycle may become `CLOSED`.

## H. Demolish Hotel (Mode 4.3 — cleanup)

Demolition is separate from closure.

### Preserve permanently

- accepted project output/source;
- relevant project state/decisions/roadmap/spec changes;
- `hotels/history/<hotel-id>.json` with final control/integration and per-Room evidence;
- explicitly retained attempt/audit refs required by policy.

### Eligible for removal after gate

- Room control packets already represented by history + accepted source;
- claim branches and attempt refs not retained by policy;
- generated source/context copies;
- transient return reports whose required evidence is summarized durably;
- scratch validation output and temporary worktrees;
- active Reception/manifests for the completed Hotel.

### Demolition sequence

1. verify Hotel is `CLOSED` and claims disabled;
2. verify history record against accepted control/base/head/integration evidence;
3. archive required refs/evidence;
4. delete approved temporary remote refs/worktrees;
5. remove `hotels/<hotel-id>/` execution scaffolding in reviewed project/control change;
6. retain `hotels/history/<hotel-id>.json`;
7. update `CURRENT_STATE.md` so completed/demolished Hotel is not presented as active;
8. push/verify the final project/control state;
9. record lifecycle `DEMOLISHED` in retained history.

Never demolish merely because Guests stopped talking. Closure acceptance and retention checks must exist first.