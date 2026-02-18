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

    def __init__(self, seed: int | None = None) -> None:
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

        # Fallback: recycle the least-used base template with a numeric suffix.
        template_usage: list[tuple[int, ProjectCategory, str]] = []
        for category, names in self._TEMPLATES.items():
            for base_name in names:
                count = self._usage_count(existing_names, base_name)
                template_usage.append((count, category, base_name))

        min_count = min(item[0] for item in template_usage)
        least_used = [item for item in template_usage if item[0] == min_count]
        _, category, base_name = self._rng.choice(least_used)
        suffix = 2
        candidate = f"{base_name}-v{suffix}"
        while candidate in existing_names:
            suffix += 1
            candidate = f"{base_name}-v{suffix}"
        complexity = self._rng.randint(min_complexity, max_complexity)
        summary = f"Build {candidate} as a {category.value} project."
        return ProjectIdea(candidate, category, complexity, summary)

    @staticmethod
    def _usage_count(existing_names: set[str], base_name: str) -> int:
        count = 0
        version_prefix = f"{base_name}-v"
        for name in existing_names:
            if name == base_name:
                count += 1
                continue
            if name.startswith(version_prefix):
                suffix = name[len(version_prefix) :]
                if suffix.isdigit():
                    count += 1
        return count
