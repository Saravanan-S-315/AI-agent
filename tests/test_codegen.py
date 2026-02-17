from app.codegen import ProjectScaffolder
from app.config import AgentConfig
from app.models import PlanArtifact, ProjectCategory, ProjectIdea


def test_scaffolder_generates_modular_project(tmp_path) -> None:
    idea = ProjectIdea(name="demo-project", category=ProjectCategory.CLI, complexity=2, summary="demo")
    plan = PlanArtifact(structure=[], dependencies=[], interfaces=[], test_outline=[])
    config = AgentConfig(workspace_root=tmp_path)

    generated = ProjectScaffolder().generate(
        workspace_root=tmp_path,
        idea=idea,
        plan=plan,
        readme_text="# Demo",
        config=config,
    )

    assert (generated.root / "app" / "main.py").exists()
    assert (generated.root / "app" / "services.py").exists()
    assert (generated.root / "tests" / "test_core.py").exists()
