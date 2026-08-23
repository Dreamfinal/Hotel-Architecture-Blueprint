# Room Path / Allowlist Semantics

Hotel vNext v0.1 uses simple repository-relative path rules so every runtime can enforce the same contract without provider-specific glob engines.

## Allowed forms

An allowlist entry is either:

- an exact repository-relative file/path, e.g. `src/features/map/Compass.tsx`;
- a repository-relative directory prefix ending in `/`, e.g. `src/features/compass/`.

Paths use `/` separators and must not be absolute.

## Forbidden forms in v0.1

Do not use:

- `..` traversal;
- drive letters or absolute `/` paths;
- `*`, `?`, `[]`, brace, regex, or shell glob syntax;
- symlink-based escapes outside the repository;
- environment-variable expansion.

If a Room needs a complex generated set, compile the exact paths/prefixes into the Room manifest during Hotel design.

## Coverage

An exact file entry covers only that exact path.

A directory entry ending `/` covers descendants under that directory but not sibling prefixes.

Example:

```text
src/features/map/
```

covers:

```text
src/features/map/index.ts
src/features/map/Compass.tsx
```

but not:

```text
src/features/map2/index.ts
```

## Overlap

Two production write entries overlap when either:

- they are the same exact path;
- one is a directory prefix that contains the other;
- both directory prefixes contain a common subtree because one is an ancestor of the other.

Simultaneously claimable Rooms must not overlap unless the Hotel explicitly serializes them before they become READY.

## Return paths

Room `return_allowlist` should normally stay under that Room packet, e.g.:

```text
hotels/<hotel-id>/rooms/R001/return/
```

Return-only paths do not create production write conflict with another Room's return directory.

## Read paths

`source_read_allowlist` follows the same syntax but multiple Rooms may read the same path. Read access never implies write authority.