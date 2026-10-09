from app.device.simulator import DeviceSimulator


def test_subscribers():
    simulator = DeviceSimulator()

    result = simulator.show_subscribers("UPF-1")

    assert result["success"] is True
    assert result["subscribers"] == 12450