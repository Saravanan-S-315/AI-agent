from app.idea_generator import IdeaGenerator


def test_idea_generator_avoids_duplicates() -> None:
    generator = IdeaGenerator(seed=1)
    idea = generator.generate(existing_names={"task-status-api"}, min_complexity=1, max_complexity=3)
    assert idea.name != "task-status-api"
    assert 1 <= idea.complexity <= 3
