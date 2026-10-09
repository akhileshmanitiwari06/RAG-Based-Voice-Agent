
from app.device.simulator import DeviceSimulator


def test_rollback_after_verification_failure():
    simulator = DeviceSimulator()

    # Capture the complete initial state.
    before = simulator.snapshot("UPF-1")
    assert before["netact_alarm_port"] == "UP"
    assert before["alarms"] == 2

    # Apply simulated alarm generation.
    simulator.apply("UPF-1", "generate_netact_alarms")

    after_apply = simulator.snapshot("UPF-1")
    assert after_apply["alarms"] == before["alarms"] + 1
    assert after_apply["netact_alarm_port"] == "UP"

    # Force verification failure.
    simulator.enable_verification_failure()

    verification = simulator.verify(
        "UPF-1",
        "generate_netact_alarms",
    )

    assert verification["verified"] is False
    assert verification["status"] == "failed"

    # Roll back the simulated operation.
    rollback = simulator.rollback(
        "UPF-1",
        "generate_netact_alarms",
    )

    assert rollback["status"] == "rolled_back"

    # Verify the complete state has been restored.
    after_rollback = simulator.snapshot("UPF-1")
    assert after_rollback == before
