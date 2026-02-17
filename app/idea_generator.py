"""Idea generation engine."""

from __future__ import annotations

from random import Random

from .models import ProjectCategory, ProjectIdea


class IdeaGenerator:
    """Generate non-duplicate project ideas from category pools."""

    _TEMPLATES: dict[ProjectCategory, list[str]] = {
        ProjectCategory.CLI: ["log-summarizer", "csv-inspector", "backup-checker"],
        ProjectCategory.API: ["task-status-api", "inventory-api", "habit-api"],
        ProjectCategory.DATA: ["dataset-profiler", "etl-sanitizer", "schema-diff-tool"],
        ProjectCategory.AUTOMATION: ["release-note-bot", "folder-hygiene-agent", "ci-log-parser"],
        ProjectCategory.AI: ["prompt-regression-checker", "doc-qna-indexer", "smart-refactor-helper"],
    }

    def __init__(self, seed: int = 7) -> None:
        self._rng = Random(seed)

    def generate(
        self,
        existing_names: set[str],
        min_complexity: int,
        max_complexity: int,
    ) -> ProjectIdea:
        """Create a unique project idea honoring complexity constraints."""
        categories = list(ProjectCategory)
        self._rng.shuffle(categories)

        for category in categories:
            names = self._TEMPLATES[category][:]
            self._rng.shuffle(names)
            for candidate in names:
                if candidate in existing_names:
                    continue
                complexity = self._rng.randint(min_complexity, max_complexity)
                summary = f"Build {candidate} as a {category.value} project."
                return ProjectIdea(candidate, category, complexity, summary)

        raise RuntimeError("No unique ideas left in the current template pool.")
