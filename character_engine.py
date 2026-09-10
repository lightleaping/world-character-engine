"""Small state and action engine for a world-based AI character.

Module order
1. Allowed actions
2. Initial state
3. Action preconditions
4. State-changing actions
5. Proposal validation
6. Validated action dispatch
7. Result-to-dialogue conversion

Design rules
- A proposed action is not an executed action.
- Program code validates every proposal before dispatch.
- State changes only after successful execution.
- Failed, unsupported, and duplicate actions preserve state.
"""


# 1. Allowed actions

ALLOWED_ACTIONS = [
    "organize_documents",
    "move_to_audience_room",
]


# 2. Initial state

def create_initial_state():
    """Return a new state object for an independent session or test."""
    return {
        "location": "집무실",
        "activity": "대기",
        "report_reviewed": True,
        "outfit_arranged": True,
        "documents_organized": False,
    }


# 3. Action preconditions

def can_move_to_audience_room(state):
    """Check whether movement is allowed without changing state."""
    return (
        state["location"] == "집무실"
        and state["activity"] == "대기"
        and state["report_reviewed"]
        and state["outfit_arranged"]
        and state["documents_organized"]
    )


# 4. State-changing actions

def move_to_audience_room(state):
    """Move to the audience room only when every precondition passes."""
    if not can_move_to_audience_room(state):
        return False

    state["location"] = "접견실"
    return True


def organize_documents(state, tool_succeeded):
    """Organize documents and update state only after tool success."""
    if state["documents_organized"]:
        return {"success": False, "reason": "already_completed"}

    if state["location"] != "집무실":
        return {"success": False, "reason": "wrong_location"}

    if state["activity"] != "대기":
        return {"success": False, "reason": "busy"}

    if not tool_succeeded:
        return {"success": False, "reason": "tool_failed"}

    state["documents_organized"] = True
    return {"success": True, "reason": "completed"}


# 5. Proposal validation

def validate_action_proposal(proposal):
    """Validate an untrusted action proposal without executing it."""
    if "action" not in proposal:
        return {"valid": False, "reason": "missing_action"}

    if proposal["action"] is None:
        return {"valid": True, "reason": "no_action"}

    if proposal["action"] not in ALLOWED_ACTIONS:
        return {"valid": False, "reason": "unknown_action"}

    return {"valid": True, "reason": "allowed"}


# 6. Validated action dispatch

def execute_action(proposal, state, tool_succeeded=True):
    """Validate a proposal, dispatch it once, and return one result schema."""
    validation = validate_action_proposal(proposal)

    if not validation["valid"]:
        return {"success": False, "reason": validation["reason"]}

    action = proposal["action"]

    if action is None:
        return {"success": True, "reason": "no_action"}

    if action == "organize_documents":
        return organize_documents(state, tool_succeeded=tool_succeeded)

    if action == "move_to_audience_room":
        if move_to_audience_room(state):
            return {"success": True, "reason": "moved"}
        return {"success": False, "reason": "move_not_allowed"}

    # Defensive fallback if the allowlist and dispatcher diverge later.
    return {"success": False, "reason": "unknown_action"}


# 7. Result-to-dialogue conversion

def describe_action_result(result):
    """Convert a verified execution result into a truthful response."""
    replies = {
        "completed": "서류 정리를 마쳤어요.",
        "already_completed": "서류는 이미 정리되어 있어요.",
        "wrong_location": "이곳에서는 서류를 정리할 수 없어요.",
        "busy": "지금 진행 중인 일을 먼저 마치겠어요.",
        "tool_failed": "서류를 정리하지 못했어요.",
        "moved": "접견실로 이동했어요.",
        "move_not_allowed": "아직 접견실로 이동할 수 없어요.",
        "unknown_action": "그 행동은 지금 수행할 수 없어요.",
        "missing_action": "무엇을 해야 할지 확인할 수 없어요.",
        "no_action": "무슨 일인지 말씀해 주세요.",
    }
    return replies.get(result["reason"], "행동 결과를 확인할 수 없어요.")


# Complete one deterministic character turn from proposal to verified response.

def process_action_turn(proposal, state, tool_succeeded=True):
    """Execute a proposal once and reuse its result to build the response."""
    action_result = execute_action(
        proposal,
        state,
        tool_succeeded=tool_succeeded,
    )
    reply = describe_action_result(action_result)

    return {
        "reply": reply,
        "action_result": action_result,
    }
