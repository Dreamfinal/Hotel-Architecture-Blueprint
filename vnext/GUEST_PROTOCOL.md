# Minimal Guest Protocol

A Guest is disposable compute. It does not need permanent identity, permanent memory, Team Repo, the whole Project history, or the Hotel blueprint.

## Required behavior

1. **Read Reception.** Confirm the Hotel is `OPEN` and claims are enabled.
2. **Find a claimable Room.** Consider only dependency-ready Rooms listed by Reception. Perform at most the allowed prefix-filtered remote claim lookup.
3. **Claim exactly one Room atomically.** Use the fixed Room claim ref defined by `CLAIM_PROTOCOL.md`, starting from that Room's `claim_base_sha`.
4. **Verify ownership.** Read the exact remote claim ref/claim record and continue only if it identifies this Guest/session and the expected Room/base.
5. **Enter the Room.** Read only the claimed Room `START_HERE.md` and manifest.
6. **Load only Room context / skills / tools / authority.** Read the declared input packet and source allowlist. Do not broaden scope because more repository content is accessible.
7. **Do the work.** Write only the Room write allowlist. Preserve locked contracts and dependency outputs.
8. **Return required artifacts and evidence.** Run only checks actually available/allowed; record both run and unrun validation truthfully.
9. **Check out.** Commit/push the bounded return to the same claim branch and write the Room return report/claim status required by the Room contract.
10. **End.** Do not self-assign another Room in the same Guest session unless the Hotel explicitly defines a multi-room coordinator role; ordinary Guests are one Room per session.

## Never required reading

An ordinary Guest must not need to read:

- Team Repo;
- permanent Staff memory;
- the entire `CURRENT_STATE.md`/project history beyond project-wide safety explicitly included by the Room contract;
- the full Hotel architecture blueprint;
- unrelated Room packets;
- other Guests' returns;
- Rin mailbox/log state.

## Stop / escalate instead of improvising

Stop and return evidence when:

- the Hotel is not open or claims are disabled;
- the Room has an unresolved dependency;
- atomic claim loses a race;
- remote ownership verification fails;
- an input or declared source file is missing;
- requirements conflict with project/Room locked invariants;
- a required change falls outside the write allowlist;
- required authority/tooling is unavailable;
- deterministic checks fail and the Room does not authorize a bounded rework;
- completing the Room would require destructive, publish/deploy, budget, policy, or cross-project authority not granted in the Room.

A Guest may report a problem; it may not silently expand its authority to fix it.