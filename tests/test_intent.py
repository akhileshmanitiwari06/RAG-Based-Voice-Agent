from app.agent.intent import extract_intent


def test_check_subscribers():

    result = extract_intent(
        "Check subscribers on UPF-1"
    )

    assert result["intent"] == "check_subscribers"
    assert result["node"] == "UPF-1"
    assert result["risk"] == "READ"


def test_check_bgp():

    result = extract_intent(
        "Check BGP on UPF-1"
    )

    assert result["intent"] == "check_bgp"
    assert result["node"] == "UPF-1"
    assert result["risk"] == "READ"


def test_check_alarms():

    result = extract_intent(
        "Check alarms on UPF-1"
    )

    assert result["intent"] == "check_alarms"
    assert result["node"] == "UPF-1"
    assert result["risk"] == "READ"


def test_generate_netact_alarms():

    result = extract_intent(
        "Generate NetAct alarms on UPF-1"
    )

    assert result["intent"] == "generate_netact_alarms"
    assert result["node"] == "UPF-1"
    assert result["risk"] == "HIGH"


def test_clear_netact_alarms():

    result = extract_intent(
        "Clear NetAct alarms on UPF-1"
    )

    assert result["intent"] == "clear_netact_alarms"
    assert result["node"] == "UPF-1"
    assert result["risk"] == "HIGH"


def test_save_configuration():

    result = extract_intent(
        "Save configuration on UPF-1"
    )

    assert result["intent"] == "save_configuration"
    assert result["risk"] == "ACTION"


def test_reboot():

    result = extract_intent(
        "Reboot UPF-1"
    )

    assert result["intent"] == "reboot_node"
    assert result["node"] == "UPF-1"
    assert result["risk"] == "CRITICAL"