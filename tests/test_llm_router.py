from llm_router import route_prompt


def test_route_prompt_interview_goes_to_gemini() -> None:
    decision = route_prompt("Hello", intent="interview")
    assert decision.provider == "gemini"


def test_route_prompt_bulk_goes_to_self_hosted() -> None:
    decision = route_prompt("Process batch", intent="bulk")
    assert decision.provider == "self_hosted"


def test_route_prompt_other_goes_to_cursor() -> None:
    decision = route_prompt("Refactor code", intent="coding")
    assert decision.provider == "cursor_instructions"
