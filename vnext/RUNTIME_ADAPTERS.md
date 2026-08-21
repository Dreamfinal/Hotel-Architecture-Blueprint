# Runtime Adapters — Same Hotel, Different Compute

Hotel vNext defines protocol/state, not one execution engine. ChatGPT and Codex are adapters over the same Git/GitHub contract.

Neither adapter receives extra project authority merely because its tools differ.

## Shared invariants

Both adapters must produce the same logical sequence:

```text
fetch latest control_ref
→ pin control_commit_sha
→ read Reception/Room manifest from that control commit
→ check fixed claim namespace
→ create exact fixed claim ref from claim_base_sha without force
→ verify ownership
→ read compiled packet from control commit
→ read/edit project source on claim branch under allowlists
→ write valid CLAIM/ROOM_RETURN evidence
→ push
→ verify exact remote claim ref head
→ reviewer derives return_head_sha from that remote ref
→ end Guest session
```

`ROOM_RETURN.json` never self-declares the SHA of the commit that contains it. Reviewer/coordinator evaluates the same pinned contract, actual diff, derived returned head, and return schema regardless of runtime.

## ChatGPT Guest adapter

ChatGPT can operate cloud/GitHub-only when repository tools support the required actions.

### Control read

1. resolve/fetch the project's declared `control_ref`;
2. record its exact commit as `control_commit_sha`;
3. fetch `HOTEL_MANIFEST.json`, `RECEPTION.md`, candidate `ROOM_MANIFEST.json`, `START_HERE.md`, `input/`, and Room skills at that exact commit/ref snapshot.

Do not use conversation copies as authoritative control state.

### Occupancy / atomic claim

1. perform the one allowed prefix-filtered remote claim listing;
2. create the fixed branch `hotel/<hotel-id>/claims/<room-id>` from `claim_base_sha` without force;
3. if branch creation reports already-exists/conflict, lose the race and select no work from that Room;
4. write `CLAIM.json` under the Room return path on the new claim branch;
5. fetch branch/file back and verify Room/session/control/base identity.

### Work

- source reads use the claim branch;
- writes use repository file/update operations only for `write_allowlist` + `return_allowlist`;
- compiled packet inputs/skills continue to come from pinned control commit;
- if a binary/tool-heavy task cannot be represented safely through available GitHub/connected tools, return `BLOCKED` or use the Room-authorized unverified state rather than fabricating local execution.

### Return

Write schema-valid `ROOM_RETURN.json`, push it with bounded output/evidence, fetch the exact remote fixed claim ref, report the verified branch/head to coordinator, and stop. That verified branch head becomes reviewer-derived `return_head_sha`; it is not embedded in the return JSON itself.

ChatGPT does not need a persistent local machine for the Hotel to remain durable.

## Codex Guest adapter

Codex may use a local checkout/worktree for richer code/tool execution while obeying the same remote refs.

### Control read

1. `git fetch` the project's control/integration/claim namespaces required by project policy;
2. resolve remote `control_ref` head and record `control_commit_sha`;
3. read control packet files at that exact commit (checkout/read-only worktree or `git show` equivalent).

### Occupancy / atomic claim

Create the fixed remote claim ref from `claim_base_sha` using a **non-force** ref creation/push. A rejected create race means the claim was lost; do not force/delete the winner.

After creation, fetch/verify the exact remote ref and write/verify the same `CLAIM.json` identity used by ChatGPT.

### Work

A Codex adapter may create a temporary local worktree checked out at the verified claim branch. Local filesystem/tool access remains bounded by Room source/write/return rules even if the process can see more.

Run declared checks only when the capability exists and is authorized. Record exact commands/results in `ROOM_RETURN.json`.

### Return

Commit bounded production + return evidence to the fixed claim branch, push without force, fetch/verify the exact remote head, report that head to coordinator for `return_head_sha`, and stop the Guest session. Temporary worktree cleanup is local housekeeping; remote claim cleanup remains coordinator/Hotel lifecycle authority.

## Runtime capability matrix

| Contract operation | ChatGPT | Codex |
|---|---|---|
| Read exact control commit | GitHub/connector fetch | Git fetch/show/worktree |
| Prefix claim occupancy lookup | GitHub branch/ref query | `git ls-remote` / fetched refs |
| Atomic fixed claim | Create branch/ref from SHA | Non-force push/create ref |
| Packet input/skill read | Fetch at control commit | Read at control commit |
| Source read/write | Claim branch file operations | Claim worktree |
| Deterministic local build/test | Only if connected capability exists | Usually available when Room permits |
| Machine-specific GUI/device work | Connected authorized tool only | Local/authorized tool only |
| Standard return | `ROOM_RETURN.json` | Same `ROOM_RETURN.json` |
| Returned-head evidence | Reviewer resolves remote claim ref | Reviewer resolves remote claim ref |
| Acceptance authority | No (Guest) | No (Guest) |

## Adapter failure rule

If a runtime cannot implement one required protocol primitive safely—especially exact commit reads, non-force atomic claim, remote ownership verification, or bounded return—it is not a valid Guest runtime for that Room. Use another runtime rather than weakening Hotel guarantees.

## Portability acceptance test

A Hotel is runtime-portable when:

1. one READY Room can be claimed/returned by a ChatGPT Guest;
2. a different compatible READY Room can be claimed/returned by a Codex Guest;
3. both returns validate against the same Room/Claim/Return schemas;
4. both use the same control/claim namespaces and reviewer process;
5. reviewer derives returned heads the same way from remote claim refs;
6. no Room manifest, Project state, or Hotel lifecycle file requires rewriting because the runtime changed.