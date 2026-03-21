#!/usr/bin/env python3
from __future__ import annotations

from app.build import BuildError, build_target
from app.config import REPO_ROOT
from app.validator import load_representative_targets


def main() -> int:
    for target in load_representative_targets(REPO_ROOT):
        try:
            artifact = build_target(
                target.id,
                audience=target.audience,
                language=target.language,
                output_format=target.format,
                root=REPO_ROOT,
            )
        except BuildError as exc:
            target_descriptor = (
                f"{target.label} ({target.id}, {target.audience}, "
                f"{target.language}, {target.format})"
            )
            print(f"Representative build failed: {target_descriptor}")
            print(str(exc))
            return 1

        print(
            "Built representative target: "
            f"{target.label} -> {artifact.output_path.relative_to(REPO_ROOT)}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
