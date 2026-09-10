"""Dependency-free regression tests for the character action engine.

Test order
1. Document organization
2. Proposal validation
3. Movement and duplicate prevention
4. Result-driven dialogue
5. End-to-end turn processing

Each test creates a fresh state so mutations cannot leak across tests.
"""

from character_engine import (
    create_initial_state,
    describe_action_result,
    execute_action,
    process_action_turn,
)


# 1. Document organization

def test_organization_success():
    state = create_initial_state()
    result = execute_action(
        {"action": "organize_documents"},
        state,
        tool_succeeded=True,
    )

    assert result == {"success": True, "reason": "completed"}
    assert state["documents_organized"] is True


def test_organization_tool_failed():
    state = create_initial_state()
    state_before_execution = state.copy()
    result = execute_action(
        {"action": "organize_documents"},
        state,
        tool_succeeded=False,
    )

    assert result == {"success": False, "reason": "tool_failed"}
    assert state == state_before_execution


def test_organization_already_completed():
    state = create_initial_state()
    state["documents_organized"] = True
    result = execute_action(
        {"action": "organize_documents"},
        state,
        tool_succeeded=True,
    )

    assert result == {"success": False, "reason": "already_completed"}
    assert state["documents_organized"] is True


def test_organization_wrong_location():
    state = create_initial_state()
    state["location"] = "접견실"
    result = execute_action(
        {"action": "organize_documents"},
        state,
        tool_succeeded=True,
    )

    assert result == {"success": False, "reason": "wrong_location"}
    assert state["documents_organized"] is False


def test_organization_while_busy():
    state = create_initial_state()
    state["activity"] = "이동 중"
    result = execute_action(
        {"action": "organize_documents"},
        state,
        tool_succeeded=True,
    )

    assert result == {"success": False, "reason": "busy"}
    assert state["documents_organized"] is False


# 2. Proposal validation

def test_unknown_action():
    state = create_initial_state()
    state_before_execution = state.copy()
    result = execute_action({"action": "leave_palace"}, state)

    assert result == {"success": False, "reason": "unknown_action"}
    # A rejected proposal must not mutate any part of the character state.
    assert state == state_before_execution


def test_missing_action():
    state = create_initial_state()
    state_before_execution = state.copy()
    result = execute_action({}, state)

    assert result == {"success": False, "reason": "missing_action"}
    assert state == state_before_execution


def test_no_action():
    state = create_initial_state()
    state_before_execution = state.copy()
    result = execute_action({"action": None}, state)

    assert result == {"success": True, "reason": "no_action"}
    assert state == state_before_execution


# 3. Movement and duplicate prevention

def test_move_success():
    state = create_initial_state()
    state["documents_organized"] = True
    result = execute_action({"action": "move_to_audience_room"}, state)

    assert result == {"success": True, "reason": "moved"}
    assert state["location"] == "접견실"


def test_move_before_preparation():
    state = create_initial_state()
    result = execute_action({"action": "move_to_audience_room"}, state)

    assert result == {"success": False, "reason": "move_not_allowed"}
    assert state["location"] == "집무실"


def test_duplicate_move():
    state = create_initial_state()
    state["documents_organized"] = True

    first_result = execute_action({"action": "move_to_audience_room"}, state)
    second_result = execute_action({"action": "move_to_audience_room"}, state)

    assert first_result == {"success": True, "reason": "moved"}
    assert second_result == {"success": False, "reason": "move_not_allowed"}
    assert state["location"] == "접견실"


# 4. Result-driven dialogue

def test_result_dialogue():
    assert describe_action_result(
        {"success": True, "reason": "moved"}
    ) == "접견실로 이동했어요."
    assert describe_action_result(
        {"success": False, "reason": "tool_failed"}
    ) == "서류를 정리하지 못했어요."
    assert describe_action_result(
        {"success": False, "reason": "unknown_action"}
    ) == "그 행동은 지금 수행할 수 없어요."


# 5. End-to-end turn processing

def test_process_two_turns():
    state = create_initial_state()

    first_turn = process_action_turn(
        {"action": "organize_documents"},
        state,
        tool_succeeded=True,
    )

    assert first_turn["action_result"] == {
        "success": True,
        "reason": "completed",
    }
    assert first_turn["reply"] == "서류 정리를 마쳤어요."
    assert state["documents_organized"] is True

    second_turn = process_action_turn(
        {"action": "move_to_audience_room"},
        state,
    )

    assert second_turn["action_result"] == {
        "success": True,
        "reason": "moved",
    }
    assert second_turn["reply"] == "접견실로 이동했어요."
    assert state["location"] == "접견실"


# Test runner

def run_all_tests():
    tests = [
        test_organization_success,
        test_organization_tool_failed,
        test_organization_already_completed,
        test_organization_wrong_location,
        test_organization_while_busy,
        test_unknown_action,
        test_missing_action,
        test_no_action,
        test_move_success,
        test_move_before_preparation,
        test_duplicate_move,
        test_result_dialogue,
        test_process_two_turns,
    ]

    for test in tests:
        test()

    print(f"모든 테스트 통과: {len(tests)}개")


if __name__ == "__main__":
    run_all_tests()
