from pathlib import Path

import yaml

SKILL_DIRS = [
    Path.cwd() / ".agents" / "skills",
    Path.home() / ".agents" / "skills"
]

def find_skills():
    """Discover available skills and their matadata"""
    skills =  {}

    for directory in SKILL_DIRS:
        for path in sorted(directory.glob("*/SKILL.md")):
            _, frontmatter, _ = path.read_text(
                encoding="utf-8"
            ).split("---", 2)

            metadata = yaml.safe_load(frontmatter)

            name = metadata["name"]
            descriptions = " ".join(
                metadata["description"].split()
            )

            skills[name] = {
                "descriptions": descriptions,
                "path": path
            }
    return skills

SKILLS = find_skills()

def skills_prompt():
    """Return skill names and descriptions for the agent prompt."""
    return "\n".join(
        f"- {name}: {skill["descriptions"]}"
        for name, skill in SKILLS.items()
    )

def read_skill(name: str):
    """Load the full instractions for a skill. """
    if name not in SKILLS:
        return f"No skill named {name}"
    return SKILLS[name]["path"].read_text(
        encoding="utf-8"
    )