#!/usr/bin/env python3
"""Validate plugin files with the Python standard library only."""

import argparse
import json
from pathlib import Path
import re
import sys

SKILLS = {
    "factory-foreman", "factory-relay", "factory-watchdog", "factory-triage",
    "factory-spec", "factory-build", "factory-review", "factory-linear-state",
    "factory-repo-gates",
}
SCHEMAS = {"triage", "spec", "build", "review", "state"}
AUTOMATIONS = {
    "A1-intake", "A2-signal", "A3-merged-pr", "A4-watchdog",
}
DRAFT_07 = "http://json-schema.org/draft-07/schema#"


def read_text(path, errors):
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"{path}: cannot read: {exc}")
        return None


def read_json(path, errors):
    content = read_text(path, errors)
    if content is None:
        return None
    try:
        value = json.loads(content)
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path}: expected a JSON object")
        return None
    return value


def frontmatter(content):
    lines = content.splitlines()
    if not lines or lines[0] != "---":
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}
    fields = {}
    for line in lines[1:end]:
        match = re.fullmatch(r"([a-zA-Z_][\w-]*):\s*(.*)", line)
        if match:
            value = match.group(2).strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            fields[match.group(1)] = value
    return fields


def string_values(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from string_values(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from string_values(item)


def validate(root):
    root = Path(root)
    errors = []
    read_json(root / ".claude-plugin" / "plugin.json", errors)
    readme = read_text(root / "README.md", errors)
    skills_dir = root / "skills"
    skill_dirs = sorted(p for p in skills_dir.glob("*") if p.is_dir())
    skill_names = {p.name for p in skill_dirs}
    for name in sorted(SKILLS - skill_names):
        errors.append(f"skills: missing required skill {name}")
    for folder in skill_dirs:
        path = folder / "SKILL.md"
        content = read_text(path, errors)
        fields = frontmatter(content) if content is not None else {}
        if fields.get("name") != folder.name:
            errors.append(f"{path}: frontmatter name must match directory {folder.name}")
        if not fields.get("description") or fields.get("description") in {"|", ">"}:
            errors.append(f"{path}: frontmatter description must be nonempty inline text")
        if readme is not None and not re.search(
            rf"(?<![\w-]){re.escape(folder.name)}(?![\w-])", readme
        ):
            errors.append(f"README.md: missing skill {folder.name}")

    schema_paths = sorted((root / "schemas").glob("*.json"))
    for name in sorted(SCHEMAS - {p.stem for p in schema_paths}):
        errors.append(f"schemas: missing required schema {name}.json")
    for path in schema_paths:
        schema = read_json(path, errors)
        if schema is not None and schema.get("$schema") != DRAFT_07:
            errors.append(f"{path}: $schema must be {DRAFT_07}")

    automation_paths = sorted((root / "automations").glob("*.json"))
    for name in sorted(AUTOMATIONS - {p.stem for p in automation_paths}):
        errors.append(f"automations: missing required automation {name}.json")
    for path in automation_paths:
        automation = read_json(path, errors)
        if automation is None:
            continue
        references = {
            name
            for value in string_values(automation)
            for name in re.findall(r"@skills:([\w-]+)", value)
        }
        if not references:
            errors.append(f"{path}: no @skills: reference")
        for name in sorted(references):
            if name not in skill_names or not (skills_dir / name / "SKILL.md").is_file():
                errors.append(f"{path}: unknown skill {name}")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    errors = validate(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Validation failed: {len(errors)} error(s).", file=sys.stderr)
        return 1
    print("Validation passed: plugin, skills, schemas, automations, README.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
