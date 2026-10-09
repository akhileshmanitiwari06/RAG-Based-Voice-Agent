from app.agent.graph import voiceops_graph
from app.models.schemas import AgentState


def test_read_only_graph():
    state = AgentState(
        session_id="graph-read-001",
        user_request="Check subscribers on UPF-1",
    )

    result = voiceops_graph.invoke(state)

    assert result["intent"] == "check_subscribers"
    assert result["target"] == "UPF-1"
    assert result["risk"] == "READ"
    assert result["execution_result"] is not None


def test_change_graph_requires_confirmation():
    state = AgentState(
        session_id="graph-change-001",
        user_request="Generate NetAct alarms on UPF-1",
    )

    result = voiceops_graph.invoke(state)

    assert result["intent"] == "generate_netact_alarms"
    assert result["target"] == "UPF-1"
    assert result["risk"] == "HIGH"
    assert result["confirmation_required"] is True
    
    
def test_change_graph_stops_before_execution_without_confirmation():
    state = AgentState(
        session_id="graph-pending-001",
        user_request="Generate NetAct alarms on UPF-1",
        confirmed=False,
    )

    result = voiceops_graph.invoke(state)

    assert result["intent"] == "generate_netact_alarms"
    assert result["target"] == "UPF-1"
    assert result["risk"] == "HIGH"

    assert result["confirmation_required"] is True

    # It must NOT execute the operation yet.
    assert result.get("dry_run_result") is None
    assert result.get("execution_result") is None
    assert result.get("verification_result") is None
    
    
def test_change_graph_executes_after_confirmation():
    state = AgentState(
        session_id="graph-confirmed-001",
        user_request="Generate NetAct alarms on UPF-1",
        confirmed=True,
    )

    result = voiceops_graph.invoke(state)

    assert result["intent"] == "generate_netact_alarms"
    assert result["target"] == "UPF-1"
    assert result["risk"] == "HIGH"

    assert result["plan"] is not None
    assert result["dry_run_result"] is not None
    assert result["execution_result"] is not None
    assert result["verification_result"] is not None

    assert result["status"] == "completed"    


def test_graph_rolls_back_when_verification_fails():
    from app.agent.graph import tools

    # Force verification failure in the simulator
    tools.device.enable_verification_failure()

    try:
        state = AgentState(
            session_id="graph-rollback-001",
            user_request="Generate NetAct alarms on UPF-1",
            confirmed=True,
        )

        result = voiceops_graph.invoke(state)

        # Verification must fail
        assert result["verification_result"]["verified"] is False

        # Rollback must execute
        assert result["rollback_result"] is not None
        assert result["rollback_result"]["status"] == "rolled_back"

        # Graph must finish after rollback
        assert result["status"] == "completed"

    finally:
        # VERY IMPORTANT: don't affect other tests
        tools.device.disable_verification_failure()        