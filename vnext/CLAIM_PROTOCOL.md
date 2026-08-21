# Atomic Claim Protocol

## 1. Two pins, two responsibilities

A Guest claim is bound to two immutable SHAs:

- `control_commit_sha` — the exact commit read from the latest remote `control_ref`; it pins Reception, Room manifest, compiled `input/`, Room-local `skills/`, authority, checks, acceptance, and return contract.
- `claim_base_sha` — the project code/integration commit from which the Guest working claim branch is created.

These MUST be separate concepts. Requiring a Room manifest to live inside the same commit whose SHA it contains would create an impossible Git self-reference.

## 2. Claim primitive

Each Room has one fixed remote claim branch:

```text
hotel/<hotel-id>/claims/<room-id>
```

Branch existence is the occupancy lock. The branch is created from the Room's exact `claim_base_sha` using non-force atomic ref creation. GitHub create-ref/create-branch or normal non-force `git push <sha>:refs/heads/<claim-ref>` are equivalent implementations.

If the ref already exists, the claim fails. The losing Guest must not modify/delete/force the winner's branch.

## 3. Why the fixed ref is atomic

Guests do not claim by writing a shared lobby file or by observing that a Room “looks vacant.” Two concurrent Guests may both observe vacancy, but only one remote ref creation can succeed at the fixed Room claim name.

The claim ref is also the Room working/return branch, so no second occupancy system is required.

## 4. Claim sequence

A Guest:

1. fetches the authoritative remote `control_ref` and records its exact head as `control_commit_sha`;
2. reads Reception + the candidate Room manifest from that pinned control commit;
3. confirms lifecycle `OPEN`, `claims_enabled=true`, Room dependency readiness, and a resolved `claim_base_sha`;
4. reads only the allowed claim prefix occupancy listing;
5. selects one dependency-ready Room whose exact fixed claim ref is absent;
6. creates `hotel/<hotel-id>/claims/<room-id>` from that Room's `claim_base_sha` without force;
7. writes `hotels/<hotel-id>/rooms/<room-id>/return/CLAIM.json` on the claim branch with:
   - `hotel_id`;
   - `room_id`;
   - stable `session_id` / `claim_id`;
   - `claimed_at_utc`;
   - `control_ref`;
   - `control_commit_sha`;
   - `claim_base_sha`;
   - `status: CLAIMED`;
8. commits/pushes the claim record to the same branch;
9. fetches/reads the exact remote claim branch/ref and claim record;
10. continues only if Hotel/Room/session/control/base all match the values selected before the claim.

A runtime that cannot immediately write the claim record may treat successful fixed-ref creation as provisional ownership, but it must verify the exact remote ref before modifying production paths and create the claim record before return.

## 5. Where Guest reads come from

After claim verification:

- Room `START_HERE.md`, `ROOM_MANIFEST.json`, compiled `input/`, and Room-local `skills/` are read from the pinned `control_commit_sha`.
- project source paths in `source_read_allowlist` are read from the claim branch, whose initial tree is `claim_base_sha`.
- production writes and return evidence are written only to the claim branch under Room/Hotel allowlists.

Later movement of `control_ref` cannot silently change the active Guest's Room contract; later movement of `integration_ref` cannot silently change its code base.

## 6. Claim scope

One ordinary Guest session owns one Room. The Guest may not probe individual foreign Room branches, modify a winner's claim, delete claim refs, or claim a second Room after completing the first.

## 7. Return on the claim branch

The Guest writes standard `ROOM_RETURN.json` on the claim branch with at least:

```text
status: RETURNED | IMPLEMENTED_UNVERIFIED | BLOCKED
control_ref: ...
control_commit_sha: ...
claim_base_sha: ...
implementation_commit_sha: ...   # optional if the Guest created a known implementation commit before final metadata
changed_paths: ...
checks_run: ...
checks_unrun: ...
unresolved: ...
```

The return file does **not** declare the SHA of the commit that contains itself. After the Guest pushes, reviewer/coordinator resolves the exact remote fixed claim ref and records that externally as `return_head_sha`.

Only reviewer/coordinator action can transition durable Room state to `ACCEPTED`.

## 8. Dependency-aware bases

The Hotel has immutable `hotel_base_sha`, while every Room has its own `claim_base_sha` declared in a Room manifest on the control plane.

- Independent Room: `claim_base_sha` may equal `hotel_base_sha` or the verified integration tip at opening.
- Dependent Room: `claim_base_sha` is resolved only after dependencies are `ACCEPTED` and required output is integrated/materialized.

Coordinator then commits the updated downstream Room manifest/Reception on `control_ref`. The resulting new control commit pins the packet; the `claim_base_sha` itself pins the code tree. No self-reference is required.

A Room with unresolved `claim_base_sha` is not claimable.

## 9. Stale claim detection

Staleness is policy, not a background runtime requirement. `HOTEL_MANIFEST.json` may define `claim_stale_after_hours`. A claim can be considered for recovery only when:

- it has exceeded that threshold or the owner explicitly declares it abandoned;
- no accepted integration references its unreviewed tip;
- there is no credible active Guest continuation;
- coordinator/housekeeping has authority to recover it.

No ordinary Guest may reclaim/delete a stale-looking branch itself.

## 10. Recovery procedure

Coordinator/housekeeping:

1. fetches the exact claim branch and claim/return evidence, including its pinned control commit;
2. resolves the actual stale branch head and writes a recovery audit note containing previous claim/session/control/base/head and reason;
3. preserves that stale tip under an audit ref such as `refs/archive/hotel/<hotel-id>/<room-id>/attempt-<n>`;
4. verifies the archive ref points to the expected stale tip;
5. deletes the fixed active claim branch under explicit recovery authority;
6. resets Room logical state to `READY` or `REWORK` on `control_ref`, resolving a new `claim_base_sha` if required;
7. refreshes Reception/control state and verifies the remote control commit;
8. a later fresh Guest may atomically create the fixed claim ref again.

This keeps attempt history without making new Guests carry old attempts in context.

## 11. Acceptance and cleanup

After a Room is accepted/integrated, its claim branch may remain until Hotel closure for audit or be archived earlier according to retention policy. Deletion must never be the only copy of accepted output: accepted source/integration commit and required evidence must already be durable.

At Hotel demolition, temporary claim refs are removed only after closure/retention gates pass.