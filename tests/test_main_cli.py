"""Tests for CLI planning and safety helpers."""

from main import is_command_blocked, prompt_to_plan


def test_prompt_to_plan_run_tests() -> None:
    plan = prompt_to_plan("run tests", use_llm=False)
    assert plan is not None
    assert plan.commands == ["py -3 -m pytest -q"]


def test_prompt_to_plan_search() -> None:
    plan = prompt_to_plan("search for orchestrator", use_llm=False)
    assert plan is not None
    assert plan.commands == ['rg -n "orchestrator" .']


def test_prompt_to_plan_unknown() -> None:
    plan = prompt_to_plan("do magic unknown thing", use_llm=False)
    assert plan is None


def test_blocked_command() -> None:
    assert is_command_blocked("rm -rf /")
    assert not is_command_blocked("git status")


def test_prompt_to_plan_generate_project() -> None:
    plan = prompt_to_plan("generate project", use_llm=False)
    assert plan is not None
    assert "main.py run" in plan.commands[0]


def test_prompt_to_plan_desktop_file() -> None:
    plan = prompt_to_plan("create text document in desktop", use_llm=False)
    assert plan is not None
    assert "Desktop" in plan.commands[0]
