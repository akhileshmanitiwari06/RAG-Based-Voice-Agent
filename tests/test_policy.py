from app.agent.policies import validate_execution


def test_read_operation_does_not_need_confirmation():

    result = validate_execution(
        "check_subscribers",
        "READ",
        False,
    )

    assert result["allowed"] is True


def test_config_requires_confirmation():

    result = validate_execution(
        "generate_netact_alarms",
        "HIGH",
        False,
    )

    assert result["allowed"] is False


def test_confirmed_config_is_allowed():

    result = validate_execution(
        "generate_netact_alarms",
        "HIGH",
        True,
    )

    assert result["allowed"] is True


def test_unknown_intent_is_blocked():

    result = validate_execution(
        "run_random_command",
        "CRITICAL",
        True,
    )

    assert result["allowed"] is False