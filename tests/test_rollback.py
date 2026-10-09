from app.device.simulator import DeviceSimulator


def test_rollback_after_verification_failure():
    simulator = DeviceSimulator()

    # Initial state
    before = simulator.snapshot("UPF-1")
    assert before["netact_alarm_port"] == "UP"

    # Apply configuration
    simulator.apply("UPF-1", "generate_netact_alarms")

    after_apply = simulator.snapshot("UPF-1")
    assert after_apply["netact_alarm_port"] == "DOWN"

    # Force verification failure
    simulator.enable_verification_failure()

    verification = simulator.verify(
        "UPF-1",
        "generate_netact_alarms"
    )

    assert verification["verified"] is False
    assert verification["status"] == "failed"

    # Automatic rollback
    rollback = simulator.rollback(
        "UPF-1",
        "generate_netact_alarms"
    )

    assert rollback["status"] == "rolled_back"

    # Verify state restored
    after_rollback = simulator.snapshot("UPF-1")
    assert after_rollback["netact_alarm_port"] == "UP"