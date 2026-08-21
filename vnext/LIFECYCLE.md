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

- `HOTEL_MANIFEST.json`;
- dependency graph;
- `RECEPTION.md` draft;
- one complete Room packet per planned Room;
- compiled Room skills/loadouts;
- authority/write ownership map;
- deterministic Hotel/Room validation result.

### Design rule

A Room is not complete merely because it has a task title. A fresh Guest must be able to execute it without studying the full project or Team Repo.

## B. Validate / Ready to Open

Before `READY_TO_OPEN`, verify:

1. manifests conform to schema;
2. Room IDs/dependencies form a valid graph;
3. every dependency refers to a real Room;
4. all initially READY Rooms have resolved `claim_base_sha`;
5. all required inputs/source paths exist;
6. Room packets contain objective, context, loadout, authority, write allowlist, checks, acceptance, return, and escalation contract;
7. simultaneously claimable Rooms have no forbidden write overlap;
8. Room-local skills exist without requiring Team Repo;
9. `hotel_base_sha` exists and identifies the intended immutable opening origin;
10. integration ref/branch exists when the Hotel uses one;
11. Reception matches dependency readiness;
12. claim namespace/prefix is reserved for this Hotel and no stale prior-Hotel refs collide;
13. project `CURRENT_STATE.md` is ready to point to this Hotel when opened.

Validation success moves `DRAFT → VALIDATED → READY_TO_OPEN`. Claims remain disabled.

## C. Open Hotel (Mode 4.2)

Opening is a coordinator/owner-authorized control transition:

1. revalidate the exact content being opened;
2. pin `hotel_base_sha` and any initial Room `claim_base_sha` values;
3. set lifecycle `OPEN` and `claims_enabled=true` in Hotel control state;
4. publish/update Reception;
5. update project `CURRENT_STATE.md` with active Hotel ID, phase, current gate, and next action;
6. commit/push the opening control state;
7. verify the remote opening commit/ref;
8. only after remote verification may Guests claim Rooms.

A copied prompt, chat statement, old lobby, or unpushed local file cannot open a Hotel.

## D. Execution

While OPEN:

- Guests claim exactly one dependency-ready Room through the atomic claim protocol;
- Guest writes stay within Room authority/allowlists;
- returns are delivered on claim branches;
- reviewer/coordinator verifies checks, diff scope, acceptance criteria, and domain quality;
- accepted output is integrated/materialized into the Hotel integration line/project source;
- dependent Room bases are resolved only after required upstream acceptance/integration;
- Reception/control state is refreshed when dependency readiness changes materially;
- project `CURRENT_STATE.md` stays concise and points to the Hotel rather than copying Room transcripts.

## E. Rework / Blocked / Stale

- `REWORK`: reviewer returns bounded evidence/criteria; coordinator may reset the Room for another attempt.
- `BLOCKED`: missing dependency, authority, source, decision, or tool; do not disguise as failure.
- `STALE`: derived from abandoned claim policy; only coordinator/housekeeping may recover it through `CLAIM_PROTOCOL.md`.

Retries preserve attempt evidence without expanding context for new Guests.

## F. Close Hotel (Mode 4.3 — closure)

Enter `CLOSING` by disabling new claims first.

Closure gate requires:

1. all required Rooms `ACCEPTED` or explicitly waived by an owner decision;
2. accepted outputs integrated/materialized into canonical project source;
3. no accepted result exists only on a temporary claim branch;
4. required deterministic/project checks pass or documented owner exception exists;
5. unresolved blockers/waivers are reflected in project truth;
6. durable decisions are in `DECISION_LOG.md`;
7. `CURRENT_STATE.md` states the phase result and next project action;
8. `DESIGN_SPEC.md`/`ROADMAP.md` are amended only if durable scope/direction changed;
9. a minimal Hotel completion record is prepared;
10. temporary refs/worktrees/packets are inventoried for retention/demolition.

After the closure commit is remotely verified, lifecycle may become `CLOSED`.

## G. Demolish Hotel (Mode 4.3 — cleanup)

Demolition is separate from closure and must be reversible/auditable until its final control commit.

### Preserve permanently

- accepted project output/source;
- project state/decisions/roadmap/spec changes that remain relevant;
- `hotels/history/<hotel-id>.json` minimal completion record;
- explicitly retained audit refs/evidence required by policy.

### Eligible for removal after gate

- Room packets already absorbed/reviewed;
- claim branches and temporary attempt refs not retained by policy;
- generated source copies;
- transient return reports whose necessary evidence is summarized durably;
- scratch validation output;
- temporary worktrees;
- active Reception/control files for the completed Hotel.

### Demolition sequence

1. verify Hotel is `CLOSED` and claims disabled;
2. verify minimal history record against accepted integration/source;
3. archive required refs/evidence;
4. delete approved temporary remote refs/worktrees;
5. remove `hotels/<hotel-id>/` execution scaffolding in a reviewed commit;
6. keep `hotels/history/<hotel-id>.json`;
7. update `CURRENT_STATE.md` so no completed/demolished Hotel is presented as active;
8. push and verify the demolition control commit;
9. mark history record lifecycle `DEMOLISHED`.

Never demolish simply because all Guests stopped talking. Closure acceptance and retention checks must exist first.