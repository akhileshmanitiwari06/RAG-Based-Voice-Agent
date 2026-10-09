from app.device.command_registry import CommandRegistry


def test_approved_template_is_allowlisted():
    registry = CommandRegistry()

    assert registry.is_approved(
        "generate_netact_alarms"
    ) is True


def test_registry_returns_operation():
    registry = CommandRegistry()

    assert registry.get_operation(
        "clear_netact_alarms"
    ) == "CONFIG"


def test_unknown_template_is_rejected():
    registry = CommandRegistry()

    assert registry.is_approved(
        "invented_command"
    ) is False


def test_unknown_template_cannot_execute():
    registry = CommandRegistry()

    try:
        registry.get_operation("invented_command")
        assert False, "Unknown template should be rejected"
    except ValueError:
        assert True