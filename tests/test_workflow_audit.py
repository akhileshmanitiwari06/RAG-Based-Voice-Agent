from app.agent.workflow import VoiceOpsAgent


def test_workflow_creates_audit():

    agent = VoiceOpsAgent()

    session_id = "demo-audit"

    result = agent.handle(
        intent="check_subscribers",
        node="UPF-1",
        risk="READ",
        session_id=session_id,
    )

    assert result["status"] == "completed"

    records = agent.audit.read(
        session_id
    )

    events = [
        record["event"]
        for record in records
    ]

    assert "REQUEST_RECEIVED" in events
    assert "RAG_RETRIEVED" in events
    assert "READ_EXECUTED" in events