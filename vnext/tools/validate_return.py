#!/usr/bin/env python3
"""Reviewer-side structural/Git validator for a returned Hotel Room claim branch.

This does not make the domain acceptance decision. It proves identity/pins, actual diff scope,
return self-report consistency, and required-check accounting before reviewer judgment.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from validate_hotel import covers, overlaps, normalize_rule


def git_text(root: Path, *args: str) -> str | None:
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return proc.stdout if proc.returncode == 0 else None


def rev(root: Path, ref: str) -> str | None:
    value = git_text(root, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    return value.strip() if value else None


def json_at(root: Path, commit: str, path: str) -> dict | None:
    raw = git_text(root, "show", f"{commit}:{path}")
    if raw is None:
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def diff_paths(root: Path, base: str, head: str) -> list[str] | None:
    raw = git_text(root, "diff", "--name-only", "--no-renames", base, head)
    if raw is None:
        return None
    return sorted(line.strip() for line in raw.splitlines() if line.strip())


def is_ancestor(root: Path, base: str, head: str) -> bool:
    proc = subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", base, head],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return proc.returncode == 0


def allowed(path: str, rules: list[str]) -> bool:
    return any(covers(rule, path) for rule in rules)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root")
    parser.add_argument("--hotel-id", required=True)
    parser.add_argument("--room-id", required=True)
    parser.add_argument("--return-ref", required=True, help="Exact returned fixed claim ref/branch")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    hotel_id = args.hotel_id
    room_id = args.room_id
    return_ref = args.return_ref
    errors: list[str] = []

    return_head = rev(root, return_ref)
    if return_head is None:
        print(f"ERROR: return ref does not resolve: {return_ref}")
        return 1

    return_dir = f"hotels/{hotel_id}/rooms/{room_id}/return"
    claim_path = f"{return_dir}/CLAIM.json"
    claim = json_at(root, return_head, claim_path)
    if claim is None:
        errors.append(f"missing/invalid claim record at returned head: {claim_path}")
        control_commit = None
        claim_base = None
    else:
        control_commit = claim.get("control_commit_sha")
        claim_base = claim.get("claim_base_sha")
        if claim.get("hotel_id") != hotel_id:
            errors.append("CLAIM.json hotel_id mismatch")
        if claim.get("room_id") != room_id:
            errors.append("CLAIM.json room_id mismatch")
        if claim.get("control_ref") is None:
            errors.append("CLAIM.json missing control_ref")
        if not isinstance(control_commit, str) or rev(root, control_commit) is None:
            errors.append(f"CLAIM.json control_commit_sha does not resolve: {control_commit!r}")
        if not isinstance(claim_base, str) or rev(root, claim_base) is None:
            errors.append(f"CLAIM.json claim_base_sha does not resolve: {claim_base!r}")

    room_manifest_path = f"hotels/{hotel_id}/rooms/{room_id}/ROOM_MANIFEST.json"
    hotel_manifest_path = f"hotels/{hotel_id}/HOTEL_MANIFEST.json"
    room = json_at(root, control_commit, room_manifest_path) if isinstance(control_commit, str) else None
    hotel = json_at(root, control_commit, hotel_manifest_path) if isinstance(control_commit, str) else None
    if room is None:
        errors.append(f"Room manifest missing/invalid at pinned control commit: {room_manifest_path}")
    if hotel is None:
        errors.append(f"Hotel manifest missing/invalid at pinned control commit: {hotel_manifest_path}")

    if room is not None:
        if room.get("hotel_id") != hotel_id or room.get("room_id") != room_id:
            errors.append("pinned Room manifest identity mismatch")
        if room.get("claim_base_sha") != claim_base:
            errors.append("CLAIM.json claim_base_sha differs from pinned Room manifest")

    if hotel is not None and claim is not None:
        if claim.get("control_ref") != hotel.get("control_ref"):
            errors.append("CLAIM.json control_ref differs from pinned Hotel manifest")

    return_contract = room.get("return_contract", {}) if room else {}
    return_path = return_contract.get("report_path")
    expected_return_path = f"{return_dir}/ROOM_RETURN.json"
    if return_path != expected_return_path:
        errors.append(f"Room return path must be {expected_return_path}, got {return_path!r}")
        return_path = expected_return_path

    returned = json_at(root, return_head, return_path)
    if returned is None:
        errors.append(f"missing/invalid ROOM_RETURN.json at returned head: {return_path}")
    elif claim is not None:
        for field in ("hotel_id", "room_id", "claim_id", "session_id", "control_ref", "control_commit_sha", "claim_base_sha"):
            if returned.get(field) != claim.get(field):
                errors.append(f"ROOM_RETURN.json {field} differs from CLAIM.json")

    if isinstance(claim_base, str) and rev(root, claim_base):
        if not is_ancestor(root, claim_base, return_head):
            errors.append("returned claim head is not descended from claim_base_sha")
        actual = diff_paths(root, claim_base, return_head)
    else:
        actual = None

    if actual is None:
        errors.append("could not compute actual claim diff")
        actual = []

    write_rules = room.get("write_allowlist", []) if room else []
    return_rules = room.get("return_allowlist", []) if room else []
    forbidden = hotel.get("forbidden_write_paths", []) if hotel else []
    combined_allowed = list(write_rules) + list(return_rules)

    for path in actual:
        try:
            normalize_rule(path)
        except ValueError as exc:
            errors.append(f"unsafe changed path {path!r}: {exc}")
            continue
        if not allowed(path, combined_allowed):
            errors.append(f"actual changed path outside Room allowlists: {path}")
        for rule in forbidden:
            try:
                if overlaps(path, rule):
                    errors.append(f"actual changed path overlaps Hotel forbidden write path: {path} <> {rule}")
            except ValueError as exc:
                errors.append(f"invalid forbidden/path comparison: {exc}")

    if returned is not None:
        reported_paths = returned.get("changed_paths")
        if not isinstance(reported_paths, list):
            errors.append("ROOM_RETURN.json changed_paths must be an array")
        else:
            reported = sorted(set(str(x) for x in reported_paths))
            if reported != actual:
                errors.append(f"ROOM_RETURN.json changed_paths mismatch actual diff: reported={reported} actual={actual}")

        scope = returned.get("allowlist_self_check", {})
        if scope.get("result") != "PASS" or scope.get("outside_allowlist_paths"):
            errors.append("Guest allowlist self-check is not PASS/empty")

        configured_checks = {item.get("id"): item for item in (room.get("checks", []) if room else []) if isinstance(item, dict)}
        run_items = returned.get("checks_run", [])
        unrun_items = returned.get("checks_unrun", [])
        run_by_id = {item.get("id"): item for item in run_items if isinstance(item, dict)}
        unrun_by_id = {item.get("id"): item for item in unrun_items if isinstance(item, dict)}
        unknown = (set(run_by_id) | set(unrun_by_id)) - set(configured_checks)
        if unknown:
            errors.append(f"return references unknown check IDs: {sorted(unknown)}")
        duplicate_accounting = set(run_by_id) & set(unrun_by_id)
        if duplicate_accounting:
            errors.append(f"checks cannot be both run and unrun: {sorted(duplicate_accounting)}")

        required_ids = {check_id for check_id, item in configured_checks.items() if item.get("required")}
        missing_required = required_ids - set(run_by_id) - set(unrun_by_id)
        if missing_required:
            errors.append(f"required checks not accounted for: {sorted(missing_required)}")
        failed_required = [
            check_id for check_id in required_ids if check_id in run_by_id and run_by_id[check_id].get("result") != "PASS"
        ]
        if failed_required and returned.get("status") == "RETURNED":
            errors.append(f"RETURNED status cannot contain failed required checks: {sorted(failed_required)}")
        if required_ids & set(unrun_by_id) and returned.get("status") == "RETURNED":
            errors.append("RETURNED status cannot leave required checks unrun")

        implementation_sha = returned.get("implementation_commit_sha")
        if implementation_sha is not None:
            if not isinstance(implementation_sha, str) or rev(root, implementation_sha) is None:
                errors.append(f"implementation_commit_sha does not resolve: {implementation_sha!r}")
            elif not is_ancestor(root, implementation_sha, return_head):
                errors.append("implementation_commit_sha is not an ancestor of return_head_sha")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} error(s); return_head_sha={return_head}")
        return 1

    print(
        f"OK: returned Room {room_id} structural/Git validation passed; "
        f"return_head_sha={return_head}; changed_paths={len(actual)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
