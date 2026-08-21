# Minimal Hotel vNext Example

This example demonstrates dependency-aware preparation without requiring Team Repo or a running orchestration engine.

Initial state:

```text
R001 READY   → claim_base_sha resolved
  ↓
R002 BLOCKED → waits for R001 ACCEPTED + integrated output + new claim_base_sha
```

From the repository root, validate with:

```bash
python vnext/tools/validate_hotel.py vnext/examples/minimal-project/hotels/demo-01
```

Expected initial result:

```text
OK: Hotel demo-01 structural validation passed; claimable=R001
```

The example Hotel is intentionally `READY_TO_OPEN` with `claims_enabled=false`. Validation passing does not open it. A real Project would perform the explicit opening control transition, pin real commit SHAs/refs, update `CURRENT_STATE.md`, push, verify remote state, and only then permit Guest claims.

After R001 is accepted/integrated, a coordinator would materialize `source/output-a.md`, change R001 to `ACCEPTED`, resolve R002 `claim_base_sha` to the integration commit, change R002 to `READY`, refresh Reception, and rerun validation.