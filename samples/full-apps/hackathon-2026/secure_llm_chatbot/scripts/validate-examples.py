#!/usr/bin/env python3

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = ROOT / "examples"
FEATURES_FILE = ROOT / "catalog" / "features.yml"

REQUIRED_HEADINGS = [
    "## What this example does",
    "## Use case",
    "## What it demonstrates",
    "## Features showcased",
    "## Products/components used",
    "## Architecture",
    "## Getting started",
    "## Try it",
    "## Security & privacy notes",
    "## Troubleshooting",
    "## Next steps / extensions",
    "## License",
]


def parse_canonical_features() -> set[str]:
    text = FEATURES_FILE.read_text(encoding="utf-8")
    slugs = set()
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("- slug:"):
            slugs.add(line.split(":", 1)[1].strip())
    return slugs


def parse_example_metadata(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    data = {}
    features = []
    in_features = False

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        if ":" in line and not line.startswith("-"):
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"')
            if key == "features":
                in_features = True
                data[key] = []
            else:
                in_features = False
                data[key] = value
            continue

        if in_features and line.startswith("-"):
            features.append(line[1:].strip().strip('"'))

    data["features"] = features
    return data


def main() -> int:
    errors = []

    if not EXAMPLES_ROOT.exists():
        print("No examples directory found.")
        return 1

    canonical = parse_canonical_features()
    metadata_files = sorted(EXAMPLES_ROOT.glob("*/*/example.yml"))

    if not metadata_files:
        errors.append("No example.yml files found under examples/<industry>/<example>/")

    for metadata in metadata_files:
        ex_dir = metadata.parent
        slug = ex_dir.name

        readme = ex_dir / "README.md"
        env_example = ex_dir / ".env.example"

        if not readme.exists():
            errors.append(f"Missing README.md: {readme.relative_to(ROOT)}")
        if not env_example.exists():
            errors.append(f"Missing .env.example: {env_example.relative_to(ROOT)}")

        parsed = parse_example_metadata(metadata)

        for key in ["name", "slug", "industry", "difficulty", "runtime", "languages", "features", "summary"]:
            if key not in parsed or parsed[key] == "":
                errors.append(f"Missing required field '{key}' in {metadata.relative_to(ROOT)}")

        if parsed.get("slug") and parsed["slug"] != slug:
            errors.append(
                f"Slug mismatch in {metadata.relative_to(ROOT)}: metadata '{parsed['slug']}' vs folder '{slug}'"
            )

        if readme.exists():
            content = readme.read_text(encoding="utf-8")
            for heading in REQUIRED_HEADINGS:
                if heading not in content:
                    errors.append(f"Missing heading '{heading}' in {readme.relative_to(ROOT)}")

        for tag in parsed.get("features", []):
            if tag not in canonical:
                errors.append(f"Unknown feature tag '{tag}' in {metadata.relative_to(ROOT)}")

    if errors:
        print("Validation failed:\n")
        for item in errors:
            print(f"- {item}")
        return 1

    print(f"Validation passed for {len(metadata_files)} example(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
