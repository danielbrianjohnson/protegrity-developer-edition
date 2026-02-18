#!/usr/bin/env python3

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = ROOT / "examples"
OUTPUT = ROOT / "catalog" / "examples.json"


def parse_example_yml(path: Path) -> dict:
    data = {}
    features = []
    in_features = False

    for raw in path.read_text(encoding="utf-8").splitlines():
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


def main() -> None:
    entries = []
    for metadata in sorted(EXAMPLES_ROOT.glob("*/*/example.yml")):
        parsed = parse_example_yml(metadata)
        rel = metadata.parent.relative_to(ROOT).as_posix()
        entries.append(
            {
                "name": parsed.get("name", metadata.parent.name),
                "slug": parsed.get("slug", metadata.parent.name),
                "industry": parsed.get("industry", metadata.parent.parent.name),
                "path": rel,
                "features": parsed.get("features", []),
            }
        )

    OUTPUT.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(entries)} example(s) to {OUTPUT}")


if __name__ == "__main__":
    main()
