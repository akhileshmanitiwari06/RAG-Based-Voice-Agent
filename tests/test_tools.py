
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
    assert result["before"] == 2
    assert result["after"] == 3
    assert "alarm" in result["change"].lower()


def test_apply_and_verify():
    tools = ToolExecutor()

    result = tools.apply(
        "generate_netact_alarms",
        "UPF-1",
    )

    assert result["status"] == "applied"

    verification = tools.verify(
        "generate_netact_alarms",
        "UPF-1",
    )

    assert verification["verified"] is True
    assert verification["status"] == "success"



def test_rollback():
    from app.device.simulator import DeviceSimulator

    simulator = DeviceSimulator()

    before = simulator.snapshot("UPF-1")

    simulator.apply(
        "UPF-1",
        "generate_netact_alarms",
    )

    rollback = simulator.rollback(
        "UPF-1",
        "generate_netact_alarms",
    )

    assert rollback["status"] == "rolled_back"
    assert simulator.snapshot("UPF-1") == before

    # After rollback, generation should no longer verify as applied.
    result = simulator.verify(
        "UPF-1",
        "generate_netact_alarms",
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
        "verification": (
            "configuration state is verified after execution"
        ),
    }

    result = tools.validate_template(template)

    assert result["valid"] is True
    assert result["template_id"] == "clear_netact_alarms"
    assert result["source"] == "approved_command_library"



def test_tool_executor_apply_verify_and_rollback_same_device():
    tools = ToolExecutor()

    before = tools.device.snapshot("UPF-1")

    apply_result = tools.apply(
        "generate_netact_alarms",
        "UPF-1",
    )
    assert apply_result["status"] == "applied"

    after_apply = tools.device.snapshot("UPF-1")
    assert after_apply["alarms"] == before["alarms"] + 1

    verify_result = tools.verify(
        "generate_netact_alarms",
        "UPF-1",
    )
    assert verify_result["verified"] is True

    rollback_result = tools.rollback(
        "generate_netact_alarms",
        "UPF-1",
    )
    assert rollback_result["status"] == "rolled_back"

    after_rollback = tools.device.snapshot("UPF-1")
    assert after_rollback == before
