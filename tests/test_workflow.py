from app.agent.workflow import VoiceOpsAgent


def test_read_workflow():

    agent = VoiceOpsAgent()

    result = agent.handle(
        intent="check_subscribers",
        node="UPF-1",
        risk="READ",
    )

    assert result["status"] == "completed"
    assert result["mode"] == "read"
    assert result["result"]["subscribers"] == 12450


def test_change_requires_confirmation():

    agent = VoiceOpsAgent()

    result = agent.handle(
        intent="generate_netact_alarms",
        node="UPF-1",
        risk="HIGH",
        confirmed=False,
    )

    assert result["status"] == "awaiting_confirmation"


def test_confirmed_change():

    agent = VoiceOpsAgent()

    result = agent.handle(
        intent="generate_netact_alarms",
        node="UPF-1",
        risk="HIGH",
        confirmed=True,
    )

    assert result["status"] == "completed"
    assert result["dry_run"]["dry_run"] is True
    assert result["applied"]["status"] == "applied"
    assert result["verification"]["verified"] is True