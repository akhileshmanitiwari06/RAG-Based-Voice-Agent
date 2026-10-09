from app.agent.tools import ToolExecutor


def test_read_subscribers():

    tools = ToolExecutor()

    result = tools.execute_read(
        "check_subscribers",
        "UPF-1",
    )

    assert result["success"] is True
    assert result["subscribers"] == 12450


def test_read_bgp():

    tools = ToolExecutor()

    result = tools.execute_read(
        "check_bgp",
        "UPF-1",
    )

    assert result["status"] == "success"
    assert result["bgp_status"] == "ESTABLISHED"


def test_dry_run():

    tools = ToolExecutor()

    result = tools.dry_run(
        "generate_netact_alarms",
        "UPF-1",
    )

    assert result["dry_run"] is True
    assert result["after"] == "DOWN"


def test_apply_and_verify():

    tools = ToolExecutor()

    tools.apply(
        "generate_netact_alarms",
        "UPF-1",
    )

    result = tools.verify(
        "generate_netact_alarms",
        "UPF-1",
    )

    assert result["verified"] is True


def test_rollback():

    tools = ToolExecutor()

    tools.apply(
        "generate_netact_alarms",
        "UPF-1",
    )

    tools.rollback(
        "generate_netact_alarms",
        "UPF-1",
    )

    result = tools.verify(
        "generate_netact_alarms",
        "UPF-1",
    )

    assert result["verified"] is False
    

def test_validate_approved_template():

    tools = ToolExecutor()

    template = {
        "template_id": "clear_netact_alarms",
        "intent": "clear_netact_alarms",
        "operation": "CONFIG",
        "risk": "HIGH",
        "description": "Clear NetAct alarms.",
        "source": "approved_command_library",
        "verification": "configuration state is verified after execution",
    }

    result = tools.validate_template(template)

    assert result["valid"] is True
    assert result["template_id"] == "clear_netact_alarms"
    assert result["source"] == "approved_command_library"    