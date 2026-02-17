"""Documentation generation utilities."""

from __future__ import annotations

from .models import PlanArtifact, ProjectIdea


def generate_readme(idea: ProjectIdea, plan: PlanArtifact) -> str:
    """Generate beginner-friendly README content."""
    return f"""# {idea.name}

## Overview
{idea.summary}

## Features
- Modular architecture
- Automated tests
- Input validation and error handling

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python -m app.main
```

## Example Output
```text
Execution completed successfully.
```

## Project Structure
{chr(10).join(f'- `{item}`' for item in plan.structure)}

## Future Enhancements
- Add CI deployment hooks
- Add advanced observability and telemetry
"""
