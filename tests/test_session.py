from app.agent.session import SessionManager


def test_create_pending_session():

    manager = SessionManager()

    manager.create_pending(
        session_id="test-001",
        intent="generate_netact_alarms",
        node="UPF-1",
        risk="HIGH",
    )

    pending = manager.get_pending("test-001")

    assert pending is not None
    assert pending["intent"] == "generate_netact_alarms"
    assert pending["node"] == "UPF-1"
    assert pending["risk"] == "HIGH"
    assert pending["status"] == "awaiting_confirmation"


def test_clear_session():

    manager = SessionManager()

    manager.create_pending(
        session_id="test-002",
        intent="reboot_node",
        node="UPF-1",
        risk="CRITICAL",
    )

    manager.clear("test-002")

    assert manager.get_pending("test-002") is None