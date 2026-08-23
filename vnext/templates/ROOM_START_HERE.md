# <ROOM_ID> — <ROOM_TITLE>

You own only this Room after a verified atomic claim.

This file is part of the Room packet pinned by the claim's `control_commit_sha`; it is not required to exist in the claim code-base commit.

## Objective

<One measurable outcome.>

## Claim identity

- Hotel: `<HOTEL_ID>`
- Room: `<ROOM_ID>`
- Control ref: read from Hotel manifest / Reception.
- Control commit: pin the exact remote control-ref head before claim.
- Claim base: read `ROOM_MANIFEST.json -> claim_base_sha` from that pinned control commit.
- Claim ref: `hotel/<hotel-id>/claims/<room-id>`

Do not begin implementation until the remote fixed claim ref and claim record verify this session as owner with the same `control_commit_sha` and `claim_base_sha`.

## Read exactly this

From the pinned `control_commit_sha`:

1. this `START_HERE.md`;
2. `ROOM_MANIFEST.json`;
3. every required path under manifest `inputs`;
4. Room-local skill payloads listed under `skills`.

From the verified claim branch initialized at `claim_base_sha`:

5. existing project source paths listed under `source_read_allowlist`.

Do not scan the repository or load unrelated Rooms/plans/history.

## Authority

Use only manifest `authority.allowed`. Anything in `authority.forbidden` or Hotel `forbidden_write_paths` remains forbidden even if your runtime/tool can perform it.

## Write boundary

Write only production `write_allowlist` plus `return_allowlist` on the claim branch. Packet inputs/skills and source reads are read-only unless a production path is separately allowlisted for write.

## Validation

Run manifest checks that are both required and available in this runtime. Record exact commands/results. If a required capability is unavailable, follow the Room return contract; never claim an unrun check passed.

## Acceptance

Satisfy every `acceptance_criteria` item. A successful push is return/delivery evidence only; reviewer/coordinator decides `ACCEPTED`.

## Return

Write the report at `return_contract.report_path` with all `required_fields`, including the pinned control/base identifiers when required; commit/push the bounded result to the same claim branch, verify the remote head, report branch + head commit, then end the Guest session.

## Escalate

Stop and report when any manifest `escalation_conditions` trigger, when a required change is outside write scope, or when project/Room contracts contradict.