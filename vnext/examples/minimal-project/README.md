# Minimal Hotel vNext Example

This example demonstrates dependency-aware Hotel preparation without Team Repo, Rin, or a continuously running orchestration engine.

## Initial control state

```text
control_ref → Reception + Room packets

R001 READY
  control packet: compiled input/skill exist
  claim_base_sha: resolved code/source base
  ↓ accepted + integrated
R002 BLOCKED
  compiled dependency input: intentionally absent
  claim_base_sha: null
```

A real Guest pins two immutable commits:

```text
control_commit_sha = exact control-ref head containing Room contract/context
claim_base_sha     = exact project code/integration base for the claim branch
```

The Room packet does not need to exist inside `claim_base_sha`.

## Structural validation

From the protocol repository root:

```bash
python vnext/tools/validate_hotel.py vnext/examples/minimal-project/hotels/demo-01
```

Expected initial result:

```text
OK: Hotel demo-01 structural validation passed; claimable=R001
```

The example Hotel is intentionally `READY_TO_OPEN` with `claims_enabled=false`. Structural validation does **not** open it and the placeholder SHAs/refs are not expected to resolve.

## Real opening

A real Project would:

1. replace placeholder SHAs/refs with real project commits/refs;
2. commit the intended control packet on `control_ref`;
3. run `validate_hotel.py ... --check-git-refs` from that exact control checkout;
4. run remote claim-namespace/opening checks;
5. set `OPEN` + `claims_enabled=true` on the control plane;
6. update project `CURRENT_STATE.md` with the active Hotel/control pointer;
7. push and verify the remote opening state;
8. only then permit Guest claims.

## Dependency transition

After R001 is returned and accepted:

1. reviewer/coordinator integrates `source/output-a.md` on `integration_ref`;
2. writes the compiled dependency note `rooms/R002/input/r001-accepted.md` on `control_ref`;
3. changes R001 to `ACCEPTED`;
4. resolves R002 `claim_base_sha` to the integration commit;
5. changes R002 to `READY`;
6. refreshes Reception;
7. pushes/verifies the new control commit.

A fresh R002 Guest then pins that newer `control_commit_sha`, creates its fixed claim branch from the new `claim_base_sha`, and works against the frozen dual-pin contract.