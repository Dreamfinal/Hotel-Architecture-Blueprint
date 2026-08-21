# Hotel Control Plane

Hotel vNext separates three Git concepts that may point to the same branch in a simple project but have different responsibilities.

## `hotel_base_sha`

Immutable audit origin for the Hotel. It records where Hotel construction began. It does not move when Rooms are accepted.

## `control_ref`

Authoritative moving ref for Hotel execution/control state while the Hotel exists.

The latest commit on `control_ref` owns the current:

- `HOTEL_MANIFEST.json` lifecycle and `claims_enabled` flag;
- `RECEPTION.md` dependency-ready/blocked Room view;
- Room manifests and resolved `claim_base_sha` values;
- reviewer/coordinator state needed to decide which Rooms can be claimed next;
- Hotel closure/demolition control material until it is absorbed/removed.

A Guest must fetch/read the latest remote `control_ref` before selecting a Room. Do not select a Room from a copied prompt, stale local branch, chat history, or an older Reception commit.

## `integration_ref`

Moving ref/line where coordinator-reviewed accepted Room output is materialized during Hotel execution.

`control_ref` and `integration_ref` MAY be the same ref for a simple Hotel. They are separate fields because some projects want control packets isolated from the production/integration line.

## Dependency transition

When upstream Room output is accepted:

1. reviewer/coordinator integrates/materializes it on `integration_ref`;
2. verifies the integration commit;
3. compiles any downstream input/Room packet changes required by that accepted output;
4. resolves each newly unblocked downstream Room `claim_base_sha` to a commit containing the exact packet + dependency output it must consume;
5. transitions those Room manifests to `READY` on `control_ref`;
6. refreshes Reception on `control_ref`;
7. pushes and verifies the remote control commit;
8. only then may a fresh Guest see/claim the downstream Room.

The claim branch itself pins the selected Room to its `claim_base_sha`, so later control-ref movement cannot silently change that Guest's contract mid-run.

## Project current state

Root `CURRENT_STATE.md` remains the project-level human reconstruction point. While a Hotel is active it must identify the active Hotel and its `control_ref` (or an unambiguous pointer to it) so a future coordinator/session can locate authoritative Hotel control state without chat history.

`CURRENT_STATE.md` does not replace Reception and should not duplicate Room occupancy/transcripts.

## Opening

Opening requires the intended `control_ref` and `integration_ref` to exist/resolve under the chosen project policy. The opening commit sets `OPEN` + `claims_enabled=true` on `control_ref`, is pushed, and is remotely verified before any Guest claim.

## Closing / demolition

At `CLOSING`, new claims are disabled on `control_ref` first. At closure, durable project output/state is reconciled before temporary Hotel control material is demolished. The final minimal Hotel history record records enough commit/ref evidence to reconstruct what was accepted without retaining the full control plane.