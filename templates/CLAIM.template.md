# Room Claim

- hotel_id: replace-me
- room_id: R001
- worker_id: unique-worker-or-session-id
- baseline: pinned-commit-or-snapshot
- claimed_at: ISO-8601 timestamp
- claim_nonce: globally-unique-value

This claim is valid only after the coordination mechanism verifies that no earlier active claim exists for this room and the stored claim matches this worker/session exactly.
