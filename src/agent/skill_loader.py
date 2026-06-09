from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_skill(skill_name):
    path = ROOT / "skills" / skill_name / "SKILL.md"
    content = path.read_text(encoding="utf-8")
    metadata, body = _parse_skill_markdown(content)
    return {
        "name": metadata.get("name", skill_name),
        "description": metadata.get("description", ""),
        "version": metadata.get("metadata.version", "0.1.0"),
        "path": str(path.relative_to(ROOT)),
        "body": body.strip(),
    }


def _parse_skill_markdown(content):
    if not content.startswith("---\n"):
        return {}, content

    _, frontmatter, body = content.split("---", 2)
    metadata = {}
    current_parent = None
    for raw_line in frontmatter.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if not raw_line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"')
            if value:
                metadata[key] = value
                current_parent = None
            else:
                current_parent = key
        elif current_parent and ":" in line:
            key, value = line.strip().split(":", 1)
            metadata[f"{current_parent}.{key.strip()}"] = value.strip().strip('"')
    return metadata, body
