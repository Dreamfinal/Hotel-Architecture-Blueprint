# Hotel Control Plane

Hotel vNext separates three Git concepts that may point to the same branch in a simple project but have different responsibilities.

## `hotel_base_sha`

Immutable audit origin for the Hotel. It records where Hotel construction began and does not move when Rooms are accepted.

## `control_ref`

Authoritative moving ref for Hotel execution/control state while the Hotel exists.

The latest commit on `control_ref` owns the current:

- `HOTEL_MANIFEST.json` lifecycle and `claims_enabled` flag;
- `RECEPTION.md` dependency-ready/blocked Room view;
- Room manifests and resolved `claim_base_sha` values;
- compiled Room `input/` and Room-local `skills/`;
- reviewer/coordinator state needed to decide which Rooms can be claimed next;
- Hotel closure/demolition control material until absorbed/removed.

A Guest fetches the latest remote `control_ref` before selecting a Room and pins that exact head as `control_commit_sha`. Do not select work from copied prompts, stale local branches, chat history, or older Reception commits.

## `integration_ref`

Moving ref/line where coordinator-reviewed accepted production output is materialized during Hotel execution.

`control_ref` and `integration_ref` MAY be the same ref for a simple Hotel. They are separate fields because some projects want control packets isolated from the production/integration line.

## Dual-pin rule

A claimed Room is frozen by two different SHAs:

- `control_commit_sha` pins Room packet/context/skills/authority/acceptance.
- `claim_base_sha` pins project code/source used to create the working claim branch.

The Room manifest stores `claim_base_sha`; the Guest derives `control_commit_sha` from the fetched control ref. The claim base does **not** need to contain the Room packet. This is intentional and avoids Git self-reference.

## Dependency transition

When upstream Room output is accepted:

1. reviewer/coordinator integrates/materializes production output on `integration_ref`;
2. verifies the integration commit;
3. compiles downstream dependency context into that Room's control-plane `input/` packet;
4. resolves each newly-unblocked downstream Room `claim_base_sha` to the integration/source commit containing the accepted production output it must consume;
5. transitions those Room manifests to `READY` on `control_ref`;
6. refreshes Reception on `control_ref`;
7. pushes/verifies the new remote control commit;
8. only then may a fresh Guest fetch that control snapshot and claim the downstream Room.

The claim branch pins code to `claim_base_sha`; the claim record pins the selected Room contract to `control_commit_sha`. Later movement of either moving ref cannot silently change an active Guest run.

## Project current state

Root `CURRENT_STATE.md` remains the project-level human reconstruction point. While a Hotel is active it identifies the active Hotel and its `control_ref` (or an unambiguous pointer) so a future coordinator/session can locate authoritative Hotel control state without chat history.

`CURRENT_STATE.md` does not replace Reception and should not duplicate Room occupancy/transcripts.

## Opening

Opening requires intended `control_ref` and `integration_ref` to exist/resolve under project policy. The opening commit sets `OPEN` + `claims_enabled=true` on `control_ref`, is pushed, and is remotely verified before any Guest claim.

## Closing / demolition

At `CLOSING`, new claims are disabled on `control_ref` first. At closure, durable project output/state is reconciled before temporary Hotel control material is demolished. The final minimal history record retains final control/integration evidence plus per-Room control/base/head/integration evidence without retaining the entire control plane.