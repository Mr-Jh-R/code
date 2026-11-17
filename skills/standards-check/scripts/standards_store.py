"""Versioned local standards. Offline by default; only 'updates' uses the network."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile


SOURCE = "https://github.com/Mr-Jh-R/code.git"
RELEASE = re.compile(r"v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)\Z")
SNAPSHOT = re.compile(r"snapshot-[0-9a-f]{40}\Z")
ESSENTIAL = {"VERSION", "LICENSE", "conventions/backend/core.md",
             "conventions/frontend-conventions.md", "conventions/backend-conventions.md"}


def default_store():
    base = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    return base / "standards" / "code"


def git(repo, *args):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, timeout=60)
    if result.returncode:
        raise ValueError("Git command failed: " + result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def is_link(path):
    return path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction())


def safe_path(root, relative):
    parts = PurePosixPath(relative)
    if (not relative or parts.is_absolute() or "\\" in relative or ":" in relative
            or any(p in {"..", "."} for p in relative.split("/"))):
        raise ValueError("Unsafe file path: " + relative)
    target = root.joinpath(*parts.parts)
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError("Path escapes snapshot: " + relative)
    current = root
    for part in parts.parts:
        current = current / part
        if is_link(current):
            raise ValueError("Linked files are not allowed: " + relative)
    return target


def check_version(version):
    if not (RELEASE.fullmatch(version) or SNAPSHOT.fullmatch(version)):
        raise ValueError("Use an installed vX.Y.Z or snapshot-<full commit SHA> ID")


def verify(store, version):
    check_version(version)
    root = store / "versions" / version
    if is_link(root) or is_link(root.parent):
        raise ValueError("Snapshot directories cannot be links")
    manifest_path = safe_path(root, "manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != 1 or manifest.get("id") != version or manifest.get("source") != SOURCE:
        raise ValueError("Snapshot manifest identity mismatch")
    sha = manifest.get("commit", "")
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("Missing fixed commit SHA")
    kind = "release" if RELEASE.fullmatch(version) else "snapshot"
    if manifest.get("kind") != kind or (kind == "snapshot" and version != "snapshot-" + sha):
        raise ValueError("Snapshot kind/commit mismatch")
    files = manifest.get("files", {})
    if not isinstance(files, dict) or not ESSENTIAL.issubset(files):
        raise ValueError("Incomplete standards package")
    for relative, digest in files.items():
        path = safe_path(root, relative)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("Changed snapshot file: " + relative)
    actual = set()
    for path in root.rglob("*"):
        if is_link(path):
            raise ValueError("Linked content in snapshot")
        if path.is_file():
            actual.add(path.relative_to(root).as_posix())
    if actual != set(files) | {"manifest.json"}:
        raise ValueError("Unexpected or missing snapshot files")
    declared = (root / "VERSION").read_text(encoding="utf-8").strip()
    if manifest.get("package_version") != declared or (kind == "release" and version != "v" + declared):
        raise ValueError("VERSION does not match snapshot identity")
    return {**manifest, "root": str(root.resolve()), "status": "verified"}


def install(store, repo, ref):
    """Export committed blobs only, never copy working-tree modifications."""
    source = git(repo, "remote", "get-url", "origin").decode().strip()
    if source.rstrip("/").removesuffix(".git") != SOURCE.removesuffix(".git"):
        raise ValueError("Repository origin is not the configured standards source")
    if RELEASE.fullmatch(ref):
        revision = "refs/tags/" + ref
        kind = "release"
    elif re.fullmatch(r"[0-9a-fA-F]{40}", ref):
        revision = ref
        kind = "snapshot"
    else:
        raise ValueError("Install requires an exact stable tag or full commit SHA; branches are not accepted")
    sha = git(repo, "rev-parse", "--verify", revision + "^{commit}").decode().strip()
    version = ref if kind == "release" else "snapshot-" + sha
    blobs = {}
    listing = git(repo, "ls-tree", "-rz", "--full-tree", sha)
    for entry in listing.split(b"\0"):
        if not entry:
            continue
        meta, name = entry.split(b"\t", 1)
        relative = name.decode("utf-8")
        if relative not in {"VERSION", "LICENSE", "CHANGELOG.md"} and not relative.startswith("conventions/"):
            continue
        mode, obj_type, oid = meta.split()
        if mode not in {b"100644", b"100755"} or obj_type != b"blob":
            raise ValueError("Snapshot contains a link/submodule: " + relative)
        blobs[relative] = git(repo, "cat-file", "blob", oid.decode())
    if not ESSENTIAL.issubset(blobs):
        raise ValueError("Selected commit lacks required standards files")
    package_version = blobs["VERSION"].decode().strip()
    if kind == "release" and ref != "v" + package_version:
        raise ValueError("Tag and VERSION disagree")
    manifest = {"schema": 1, "id": version, "kind": kind, "source": SOURCE,
                "commit": sha, "package_version": package_version,
                "files": {name: hashlib.sha256(data).hexdigest() for name, data in blobs.items()}}
    versions = store / "versions"
    if is_link(versions):
        raise ValueError("Versions directory cannot be a link")
    destination = versions / version
    if destination.exists() or is_link(destination):
        existing = verify(store, version)
        if any(existing[key] != manifest[key] for key in manifest):
            raise ValueError("Immutable version already exists with different content")
        return existing
    versions.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".install-", dir=versions) as staging:
        root = Path(staging) / version
        root.mkdir()
        for name, data in blobs.items():
            path = safe_path(root, name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        root.rename(destination)
    return verify(store, version)


def inventory(store):
    valid, invalid = [], []
    versions = store / "versions"
    if is_link(versions):
        raise ValueError("Versions directory cannot be a link")
    if versions.exists():
        for folder in sorted(versions.iterdir()):
            if folder.name.startswith(".install-"):
                continue
            try:
                item = verify(store, folder.name)
                valid.append({k: item[k] for k in ("id", "kind", "source", "commit", "package_version", "root", "status")})
            except (ValueError, OSError, KeyError, TypeError) as error:
                invalid.append({"id": folder.name, "error": str(error)})
    valid.sort(key=lambda item: (item["kind"] == "release",
                                tuple(map(int, item["id"][1:].split("."))) if item["kind"] == "release" else (),
                                item["id"]), reverse=True)
    settings = store / "selection.json"
    if is_link(settings):
        raise ValueError("Default settings cannot be a link")
    default = json.loads(settings.read_text(encoding="utf-8")).get("default") if settings.exists() else None
    return {"store": str(store.resolve()), "versions": valid, "invalid": invalid,
            "default": default, "upstream_checked": False}


def resolve(store, explicit=None, session=None, project=None):
    items = inventory(store)
    for origin, version in (("explicit", explicit), ("session", session), ("project", project), ("default", items["default"])):
        if version:
            item = verify(store, version)  # Fail rather than silently downgrade.
            return {"selection": origin, **item}
    return {"status": "selection_required", **items}


def reading_plan(item, backend=False, frontend=None, language=None, databases=(), llm=False):
    root = Path(item["root"])
    files, missing = [], []
    def add(name, required=True):
        path = safe_path(root, "conventions/" + name)
        if path.is_file():
            files.append({"path": str(path), "read": "full"})
        elif required:
            missing.append(name)
    add("quality-gates.md", False)
    if backend:
        add("backend-conventions.md")
        add("backend/core.md")
        if language:
            if not re.fullmatch(r"[a-z][a-z0-9-]*", language):
                raise ValueError("Invalid language ID")
            add("backend/languages/" + language + ".md")
    if frontend:
        add("frontend-conventions.md")
        add("frontend-conventions-" + frontend + ".md")
    for database in databases:
        add("backend/databases/" + database + ".md")
    if llm:
        add("backend/extensions/ai-llm.md")
    if not files:
        raise ValueError("Select a target technology or use the reading guide for task-specific rules")
    return {"id": item["id"], "source": item["source"], "commit": item["commit"],
            "root": str(root), "files": files, "missing_appendices": missing,
            "note": "Read selected files before reviewing code. Missing language appendix does not invalidate common rules; use project ecosystem configuration. Select framework/risk-specific chapters using references/reading-guide.md."}


def updates():
    result = subprocess.run(["git", "ls-remote", "--tags", SOURCE], capture_output=True, timeout=60)
    if result.returncode:
        raise ValueError("Upstream lookup failed; local snapshots remain available")
    refs = dict(line.split()[::-1] for line in result.stdout.decode().splitlines())
    releases = []
    for ref, oid in refs.items():
        tag = ref.removeprefix("refs/tags/")
        if RELEASE.fullmatch(tag):
            releases.append({"id": tag, "commit": refs.get(ref + "^{}", oid)})
    releases.sort(key=lambda v: tuple(map(int, v["id"][1:].split("."))), reverse=True)
    return {"source": SOURCE, "upstream_checked": True, "releases": releases,
            "note": "Remote tags are candidates, not installed local versions; inspect release notes before installation."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, default=default_store())
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    sub.add_parser("updates")
    install_cmd = sub.add_parser("install")
    install_cmd.add_argument("--repo", type=Path, required=True)
    install_cmd.add_argument("--ref", required=True)
    for name in ("verify", "default", "read-plan", "resolve"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--version", required=name != "resolve")
        if name == "resolve":
            cmd.add_argument("--session-version")
            cmd.add_argument("--project-version")
        if name == "read-plan":
            cmd.add_argument("--backend", action="store_true")
            cmd.add_argument("--frontend", choices=["react", "vue"])
            cmd.add_argument("--language")
            cmd.add_argument("--database", action="append", choices=["mysql", "postgresql"], default=[])
            cmd.add_argument("--llm", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "list":
            result = inventory(args.store)
        elif args.command == "updates":
            result = updates()
        elif args.command == "install":
            result = install(args.store, args.repo, args.ref)
        elif args.command == "resolve":
            result = resolve(args.store, args.version, args.session_version, args.project_version)
        else:
            result = verify(args.store, args.version)
            if args.command == "read-plan":
                result = reading_plan(result, args.backend, args.frontend, args.language, args.database, args.llm)
            elif args.command == "default":
                payload = json.dumps({"default": args.version}, indent=2) + "\n"
                target = args.store / "selection.json"
                if is_link(target):
                    raise ValueError("Default settings cannot be a link")
                with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=args.store, delete=False) as f:
                    f.write(payload)
                    temp = Path(f.name)
                temp.replace(target)
                result = {"default": args.version, "store": str(args.store)}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result.get("status") == "selection_required" else 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"status": "error", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
