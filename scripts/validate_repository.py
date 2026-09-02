#!/usr/bin/env python3
"""Validate the standards repository without third-party dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FRONTMATTER_FIELD = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")


def markdown_files() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*.md") if ".git" not in path.parts)


def strip_fenced_blocks(text: str) -> str:
    visible: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        marker = line.lstrip()[:3]
        if marker in {"```", "~~~"}:
            if fence is None:
                fence = marker
            elif marker == fence:
                fence = None
            continue
        if fence is None:
            visible.append(line)
    return "\n".join(visible)


def local_link_target(source: Path, raw_target: str) -> Path | None:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    target = target.split(maxsplit=1)[0]
    parsed = urlparse(target)
    if parsed.scheme or target.startswith("#"):
        return None
    path_part = unquote(target.split("#", 1)[0].split("?", 1)[0])
    if not path_part:
        return None
    return (source.parent / path_part).resolve()


def validate_markdown() -> list[str]:
    errors: list[str] = []
    for path in markdown_files():
        relative = path.relative_to(ROOT)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            errors.append(f"{relative}: not valid UTF-8: {error}")
            continue

        lines = text.splitlines()
        for number, line in enumerate(lines, start=1):
            if line.endswith((" ", "\t")):
                errors.append(f"{relative}:{number}: trailing whitespace")

        for marker in ("```", "~~~"):
            count = sum(1 for line in lines if line.lstrip().startswith(marker))
            if count % 2:
                errors.append(f"{relative}: unbalanced {marker} fences ({count})")

        visible_text = strip_fenced_blocks(text)
        for match in MARKDOWN_LINK.finditer(visible_text):
            target = local_link_target(path, match.group(1))
            if target is not None and not target.exists():
                errors.append(
                    f"{relative}: broken local link {match.group(1)!r} -> "
                    f"{target.relative_to(ROOT) if target.is_relative_to(ROOT) else target}"
                )
    return errors


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return {}, [f"{path.relative_to(ROOT)}: missing YAML frontmatter"]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, [f"{path.relative_to(ROOT)}: unclosed YAML frontmatter"]

    fields: dict[str, str] = {}
    for number, line in enumerate(lines[1:end], start=2):
        match = FRONTMATTER_FIELD.match(line)
        if not match:
            errors.append(f"{path.relative_to(ROOT)}:{number}: unsupported frontmatter line")
            continue
        fields[match.group(1)] = match.group(2).strip().strip('"\'')
    return fields, errors


def validate_skills() -> list[str]:
    errors: list[str] = []
    skill_files = sorted((ROOT / "skills").glob("*/SKILL.md"))
    if not skill_files:
        return ["skills: no */SKILL.md packages found"]

    for path in skill_files:
        relative = path.relative_to(ROOT)
        fields, parse_errors = parse_frontmatter(path)
        errors.extend(parse_errors)
        unexpected = set(fields) - {"name", "description"}
        if unexpected:
            errors.append(f"{relative}: unsupported frontmatter fields {sorted(unexpected)}")
        if fields.get("name") != path.parent.name:
            errors.append(
                f"{relative}: name {fields.get('name')!r} must match folder {path.parent.name!r}"
            )
        if not fields.get("description"):
            errors.append(f"{relative}: description is required")
    return errors


def validate_version() -> list[str]:
    errors: list[str] = []
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(version):
        errors.append(f"VERSION: {version!r} is not SemVer core format")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if f"--branch v{version}" not in readme:
        errors.append(f"README.md: install command does not pin v{version}")

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## [{version}]" not in changelog:
        errors.append(f"CHANGELOG.md: missing [{version}] release section")

    required = [
        ROOT / "LICENSE",
        ROOT / "VERSIONING.md",
        ROOT / "MIGRATION-v1-to-v2.md",
        ROOT / "conventions/backend-conventions.md",
        ROOT / "conventions/backend/core.md",
        ROOT / "conventions/backend/project-profile.template.md",
    ]
    for path in required:
        if not path.exists():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")
    return errors


def main() -> int:
    errors = validate_markdown() + validate_skills() + validate_version()
    if errors:
        print("Repository validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Repository validation passed: {len(markdown_files())} Markdown files, "
        f"{len(list((ROOT / 'skills').glob('*/SKILL.md')))} skill package(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
