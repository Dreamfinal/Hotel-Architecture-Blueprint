#!/usr/bin/env python3
"""Dependency-free structural validator for a Hotel Architecture folder."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_HOTEL = {"schema_version", "hotel_id", "title", "objective", "lifecycle", "claims_enabled", "baseline", "rooms"}
REQUIRED_ROOM = {
    "schema_version", "hotel_id", "room_id", "title", "status", "objective",
    "owner_role", "depends_on", "inputs", "write_allowlist", "outputs",
    "acceptance_criteria", "checks", "reviewer_role", "next_to", "escalate_when"
}
REQUIRED_GIT = {
    "schema_version", "hotel_id", "repository_root", "remote", "target_branch",
    "baseline_ref", "baseline_sha", "branch_pattern", "worktree_pattern",
    "claim_mechanism", "force_push_allowed", "integration_strategy",
    "integration_owner", "required_checks", "post_merge_checks",
    "rollback_strategy", "permissions"
}


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"cannot read JSON {path}: {exc}") from exc


def missing(obj, fields):
    return sorted(fields - set(obj))


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    hotel_path = root / "HOTEL_MANIFEST.json"
    if not hotel_path.is_file():
        return [f"missing {hotel_path}"]
    try:
        hotel = load_json(hotel_path)
    except ValueError as exc:
        return [str(exc)]
    absent = missing(hotel, REQUIRED_HOTEL)
    if absent:
        errors.append(f"hotel missing fields: {', '.join(absent)}")
    rooms = hotel.get("rooms", [])
    git_policy_rel = hotel.get("git_policy")
    if git_policy_rel:
        git_path = root / git_policy_rel
        if not git_path.is_file():
            errors.append(f"missing Git policy {git_path}")
        else:
            try:
                git_policy = load_json(git_path)
                absent = missing(git_policy, REQUIRED_GIT)
                if absent:
                    errors.append(f"Git policy missing fields: {', '.join(absent)}")
                if git_policy.get("hotel_id") != hotel.get("hotel_id"):
                    errors.append("Git policy hotel_id mismatch")
                if hotel.get("claims_enabled") and git_policy.get("baseline_sha") in {None, "", "UNPINNED"}:
                    errors.append("claims are enabled but Git baseline_sha is not pinned")
                if git_policy.get("force_push_allowed") is not False:
                    errors.append("force_push_allowed must be false for the standard blueprint")
            except ValueError as exc:
                errors.append(str(exc))
    if not isinstance(rooms, list) or not rooms:
        errors.append("hotel.rooms must be a non-empty list")
        return errors
    room_ids = [r.get("room_id") for r in rooms if isinstance(r, dict)]
    if len(room_ids) != len(set(room_ids)):
        errors.append("duplicate room_id in hotel manifest")
    known = set(room_ids)
    write_scopes: dict[str, str] = {}
    for entry in rooms:
        if not isinstance(entry, dict):
            errors.append("hotel room entry must be an object")
            continue
        rel = entry.get("manifest")
        room_id = entry.get("room_id", "<unknown>")
        if not rel:
            errors.append(f"{room_id}: missing manifest path")
            continue
        path = root / rel
        if not path.is_file():
            errors.append(f"{room_id}: missing manifest file {path}")
            continue
        try:
            room = load_json(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        absent = missing(room, REQUIRED_ROOM)
        if absent:
            errors.append(f"{room_id}: missing fields: {', '.join(absent)}")
        if room.get("room_id") != room_id:
            errors.append(f"{room_id}: room_id mismatch in room manifest")
        if room.get("hotel_id") != hotel.get("hotel_id"):
            errors.append(f"{room_id}: hotel_id mismatch")
        unknown = set(room.get("depends_on", [])) - known
        if unknown:
            errors.append(f"{room_id}: unknown dependencies: {', '.join(sorted(unknown))}")
        if room_id in set(room.get("depends_on", [])):
            errors.append(f"{room_id}: room cannot depend on itself")
        allowlist = room.get("write_allowlist", [])
        if not allowlist:
            errors.append(f"{room_id}: write_allowlist must not be empty")
        for scope in allowlist:
            if scope in write_scopes:
                errors.append(f"write scope collision: {scope} used by {write_scopes[scope]} and {room_id}")
            else:
                write_scopes[scope] = room_id
        if not room.get("acceptance_criteria"):
            errors.append(f"{room_id}: acceptance_criteria must not be empty")
    return errors


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    errors = validate(root)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
