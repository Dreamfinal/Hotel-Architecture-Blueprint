#!/usr/bin/env python3
"""Deterministic cross-file validator for Hotel Protocol vNext v0.1.

The validator uses only the Python standard library. JSON Schema validation is expected as
an additional gate. Pass --check-git-refs during a real opening validation to verify the
pinned Hotel/Room commits and integration ref in the Project repository.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")
ROOM_ID = re.compile(r"^R[0-9]{3,}$")
GLOB_CHARS = set("*?[]{}")
CLAIMABLE_STATES = {"READY", "REWORK"}
BASE_REQUIRED_STATES = {
    "READY",
    "CLAIMED",
    "IN_PROGRESS",
    "RETURNED",
    "REVIEW",
    "ACCEPTED",
    "REWORK",
}


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"cannot parse {path}: {exc}") from exc


def normalize_rule(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("path rule must be a non-empty string")
    if "\\" in value:
        raise ValueError(f"path rule must use '/': {value}")
    if value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        raise ValueError(f"absolute path forbidden: {value}")
    parts = value.rstrip("/").split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"unsafe path segments: {value}")
    if any(ch in value for ch in GLOB_CHARS):
        raise ValueError(f"glob syntax forbidden in v0.1: {value}")
    return value


def safe_path(base: Path, rule: str) -> Path:
    rule = normalize_rule(rule)
    base = base.resolve()
    candidate = (base / rule.rstrip("/")).resolve(strict=False)
    if candidate != base and base not in candidate.parents:
        raise ValueError(f"path escapes allowed root (including symlink escape): {rule}")
    return candidate


def covers(rule: str, candidate: str) -> bool:
    rule = normalize_rule(rule)
    candidate = normalize_rule(candidate)
    if rule.endswith("/"):
        return candidate == rule[:-1] or candidate.startswith(rule)
    return candidate == rule


def overlaps(a: str, b: str) -> bool:
    a = normalize_rule(a)
    b = normalize_rule(b)
    if a == b:
        return True
    if a.endswith("/") and (b == a[:-1] or b.startswith(a)):
        return True
    if b.endswith("/") and (a == b[:-1] or a.startswith(b)):
        return True
    return False


def has_cycle(room_ids: set[str], edges: set[tuple[str, str]]) -> bool:
    outgoing: dict[str, list[str]] = {room: [] for room in room_ids}
    for src, dst in edges:
        outgoing.setdefault(src, []).append(dst)
    visiting: set[str] = set()
    visited: set[str] = set()

    def dfs(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for nxt in outgoing.get(node, []):
            if dfs(nxt):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(dfs(room) for room in room_ids)


def git_resolves(project_root: Path, value: str, is_sha: bool) -> bool:
    target = f"{value}^{{commit}}" if is_sha else f"{value}^{{commit}}"
    proc = subprocess.run(
        ["git", "-C", str(project_root), "rev-parse", "--verify", "--quiet", target],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return proc.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("hotel_dir", help="Path to hotels/<hotel-id>")
    parser.add_argument("--project-root", help="Project repository root; defaults to hotel_dir/../..")
    parser.add_argument(
        "--check-git-refs",
        action="store_true",
        help="Verify hotel_base_sha, non-null Room claim bases, and integration_ref resolve to commits",
    )
    args = parser.parse_args()

    hotel_dir = Path(args.hotel_dir).resolve()
    project_root = Path(args.project_root).resolve() if args.project_root else hotel_dir.parent.parent.resolve()
    errors: list[str] = []

    try:
        hotel = load_json(hotel_dir / "HOTEL_MANIFEST.json")
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    hotel_id = hotel.get("hotel_id")
    lifecycle = hotel.get("lifecycle")
    claims_enabled = hotel.get("claims_enabled")
    hotel_base = hotel.get("hotel_base_sha")
    claim_prefix = hotel.get("claim_prefix")
    integration_ref = hotel.get("integration_ref")

    if not hotel_id:
        errors.append("Hotel manifest missing hotel_id")
    if claims_enabled and lifecycle != "OPEN":
        errors.append("claims_enabled=true requires lifecycle OPEN")
    if lifecycle == "OPEN" and not claims_enabled:
        errors.append("lifecycle OPEN requires claims_enabled=true outside an atomic closing transition")
    if not isinstance(hotel_base, str) or not SHA40.match(hotel_base):
        errors.append("hotel_base_sha must be a 40-hex SHA")
    if hotel_id and claim_prefix != f"hotel/{hotel_id}/claims/":
        errors.append("claim_prefix must exactly match hotel/<hotel-id>/claims/")
    if hotel.get("current_state_path") != "CURRENT_STATE.md":
        errors.append("current_state_path must be CURRENT_STATE.md")

    try:
        current_state = safe_path(project_root, "CURRENT_STATE.md")
        if not current_state.is_file():
            errors.append("Project root CURRENT_STATE.md is missing")
    except ValueError as exc:
        errors.append(str(exc))

    reception_path = hotel.get("reception_path", "RECEPTION.md")
    try:
        reception = safe_path(hotel_dir, reception_path)
    except ValueError as exc:
        errors.append(f"Reception path: {exc}")
        reception = hotel_dir / "__invalid_reception__"
    if not reception.is_file():
        errors.append(f"Reception missing: {reception_path}")
        reception_text = ""
    else:
        reception_text = reception.read_text(encoding="utf-8")

    if args.check_git_refs:
        if not (project_root / ".git").exists() and not git_resolves(project_root, "HEAD", False):
            errors.append("--check-git-refs requires project_root to resolve as a Git worktree/repository")
        if isinstance(hotel_base, str) and SHA40.match(hotel_base) and not git_resolves(project_root, hotel_base, True):
            errors.append(f"hotel_base_sha does not resolve to a commit: {hotel_base}")
        if not isinstance(integration_ref, str) or not integration_ref or not git_resolves(project_root, integration_ref, False):
            errors.append(f"integration_ref does not resolve to a commit: {integration_ref!r}")

    room_refs = hotel.get("rooms")
    if not isinstance(room_refs, list) or not room_refs:
        errors.append("Hotel must declare at least one Room")
        room_refs = []

    rooms: dict[str, dict] = {}
    for ref in room_refs:
        room_id = ref.get("room_id") if isinstance(ref, dict) else None
        manifest_rel = ref.get("manifest_path") if isinstance(ref, dict) else None
        if not room_id or not ROOM_ID.match(str(room_id)):
            errors.append(f"invalid room_id in Hotel manifest: {room_id!r}")
            continue
        if room_id in rooms:
            errors.append(f"duplicate room_id: {room_id}")
            continue
        if not manifest_rel:
            errors.append(f"Room {room_id} missing manifest_path")
            continue
        try:
            manifest_path = safe_path(project_root, manifest_rel)
        except ValueError as exc:
            errors.append(f"Room {room_id} manifest path: {exc}")
            continue
        if not manifest_path.is_file():
            errors.append(f"Room {room_id} manifest missing: {manifest_rel}")
            continue
        try:
            room = load_json(manifest_path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        rooms[room_id] = room
        if room.get("room_id") != room_id:
            errors.append(f"Room {room_id} manifest room_id mismatch")
        if room.get("hotel_id") != hotel_id:
            errors.append(f"Room {room_id} hotel_id mismatch")

    room_ids = set(rooms)
    derived_edges: set[tuple[str, str]] = set()
    for room_id, room in rooms.items():
        deps = room.get("depends_on", [])
        if not isinstance(deps, list):
            errors.append(f"Room {room_id} depends_on must be an array")
            deps = []
        for dep in deps:
            if dep == room_id:
                errors.append(f"Room {room_id} depends on itself")
            if dep not in room_ids:
                errors.append(f"Room {room_id} depends on missing Room {dep}")
            derived_edges.add((dep, room_id))

    declared_edges: set[tuple[str, str]] = set()
    for edge in hotel.get("dependency_edges", []):
        if isinstance(edge, dict):
            declared_edges.add((edge.get("from"), edge.get("to")))
    if declared_edges != derived_edges:
        errors.append("Hotel dependency_edges do not exactly match Room depends_on declarations")
    if has_cycle(room_ids, derived_edges):
        errors.append("Room dependency graph contains a cycle")

    claimable: list[str] = []
    for room_id, room in rooms.items():
        state = room.get("logical_state")
        base_sha = room.get("claim_base_sha")
        if state in BASE_REQUIRED_STATES and (not isinstance(base_sha, str) or not SHA40.match(base_sha)):
            errors.append(f"Room {room_id} is {state} without a resolved claim_base_sha")
        if args.check_git_refs and isinstance(base_sha, str) and SHA40.match(base_sha):
            if not git_resolves(project_root, base_sha, True):
                errors.append(f"Room {room_id} claim_base_sha does not resolve: {base_sha}")

        if state in CLAIMABLE_STATES:
            deps = room.get("depends_on", [])
            unaccepted = [dep for dep in deps if rooms.get(dep, {}).get("logical_state") != "ACCEPTED"]
            if unaccepted:
                errors.append(f"Room {room_id} is {state} but dependencies are not ACCEPTED: {unaccepted}")
            else:
                claimable.append(room_id)

        for section in ("source_read_allowlist", "write_allowlist", "return_allowlist"):
            values = room.get(section, [])
            if not isinstance(values, list):
                errors.append(f"Room {room_id} {section} must be an array")
                continue
            for value in values:
                try:
                    safe_path(project_root, value)
                except ValueError as exc:
                    errors.append(f"Room {room_id} {section}: {exc}")

        if state in CLAIMABLE_STATES:
            for source_rule in room.get("source_read_allowlist", []):
                try:
                    source_path = safe_path(project_root, source_rule)
                except ValueError:
                    continue
                if not source_path.exists():
                    errors.append(f"Room {room_id} source_read_allowlist path missing at claimable state: {source_rule}")

        for item in room.get("inputs", []):
            if not isinstance(item, dict) or "path" not in item:
                errors.append(f"Room {room_id} has invalid input entry")
                continue
            try:
                input_path = safe_path(project_root, item["path"])
            except ValueError as exc:
                errors.append(f"Room {room_id} input: {exc}")
                continue
            if state in CLAIMABLE_STATES and item.get("required") and not input_path.exists():
                errors.append(f"Room {room_id} required input missing at claimable state: {item['path']}")

        for skill in room.get("skills", []):
            if not isinstance(skill, dict) or "path" not in skill:
                errors.append(f"Room {room_id} has invalid skill entry")
                continue
            try:
                skill_path = safe_path(project_root, skill["path"])
            except ValueError as exc:
                errors.append(f"Room {room_id} skill: {exc}")
                continue
            if skill.get("required") and not skill_path.exists():
                errors.append(f"Room {room_id} required Room skill missing: {skill['path']}")

        report_path = room.get("return_contract", {}).get("report_path")
        if report_path:
            try:
                safe_path(project_root, report_path)
                if not any(covers(rule, report_path) for rule in room.get("return_allowlist", [])):
                    errors.append(f"Room {room_id} return report is outside return_allowlist: {report_path}")
            except ValueError as exc:
                errors.append(f"Room {room_id} return path: {exc}")

    for index, a_id in enumerate(claimable):
        for b_id in claimable[index + 1 :]:
            for a_rule in rooms[a_id].get("write_allowlist", []):
                for b_rule in rooms[b_id].get("write_allowlist", []):
                    try:
                        if overlaps(a_rule, b_rule):
                            errors.append(f"simultaneously claimable Rooms {a_id}/{b_id} overlap writes: {a_rule} <> {b_rule}")
                    except ValueError as exc:
                        errors.append(f"write overlap check failed: {exc}")

    for room_id in claimable:
        if room_id not in reception_text:
            errors.append(f"Reception omits dependency-ready Room {room_id}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} error(s)")
        return 1

    mode = "opening" if args.check_git_refs else "structural"
    print(f"OK: Hotel {hotel_id} {mode} validation passed; claimable={','.join(claimable) or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
