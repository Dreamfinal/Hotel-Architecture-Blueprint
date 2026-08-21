# R002 — Consume accepted R001 output

This Room is intentionally `BLOCKED` in the initial Hotel packet.

Do not claim it until:

1. R001 is `ACCEPTED`;
2. `source/output-a.md` is integrated/materialized;
3. coordinator resolves R002 `claim_base_sha` to the integration commit;
4. R002 transitions to `READY` and Reception is refreshed.

After a later verified atomic claim, read only this Room manifest + accepted `source/output-a.md`, create `source/output-b.md`, return through this Room's claim branch, and end the session.