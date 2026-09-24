from pathlib import Path

import yaml

SKILL_DIRS = [
    Path.cwd() / ".agents" / "skills",
    Path.home() / ".agents" / "skills"
]

def find_skills():
    """Discover available skills and their metadata."""
    skills = {}

    for directory in SKILL_DIRS:
        for path in sorted(directory.glob("*/SKILL.md")):
            try:
                content = path.read_text(
                    encoding="utf-8"
                )

                parts = content.split("---", 2)

                if len(parts) != 3:
                    continue

                _, frontmatter, _ = parts

                metadata = yaml.safe_load(frontmatter)

                if not isinstance(metadata, dict):
                    continue

                name = metadata.get("name")
                description = metadata.get("description")

                if not name or not description:
                    continue

                skills[name] = {
                    "description": " ".join(
                        str(description).split()
                    ),
                    "path": path,
                }

            except (OSError, yaml.YAMLError):
                continue

    return skills

SKILLS = find_skills()

def skills_prompt():
    """Return skill names and descriptions for the agent prompt."""
    return "\n".join(
        f"- {name}: {skill["description"]}"
        for name, skill in SKILLS.items()
    )

def read_skill(name: str):
    """Load the full instractions for a skill. """
    if name not in SKILLS:
        return f"No skill named {name}"
    return SKILLS[name]["path"].read_text(
        encoding="utf-8"
    )