from app.device.ssh_adapter import SSHAdapter


def test_ssh_adapter_uses_injected_runner():

    def fake_runner(node, command):
        return f"executed on {node}: {command}"

    adapter = SSHAdapter(
        command_runner=fake_runner
    )

    result = adapter.execute(
        node="UPF-1",
        command="SAFE_TEST_COMMAND",
    )

    assert result["status"] == "success"
    assert "UPF-1" in result["output"]


def test_ssh_adapter_rejects_empty_command():

    adapter = SSHAdapter(
        command_runner=lambda node, command: "should not execute"
    )

    result = adapter.execute(
        node="UPF-1",
        command="",
    )

    assert result["status"] == "failed"
    


from app.device.ssh_adapter import SSHAdapter


def test_ssh_adapter_passes_target_and_command_to_runner():
    calls = []

    def fake_runner(node, command):
        calls.append((node, command))
        return "mock execution successful"

    adapter = SSHAdapter(command_runner=fake_runner)

    result = adapter.execute(
        node="UPF-1",
        command="SAFE_TEST_COMMAND",
    )

    assert result["status"] == "success"
    assert calls == [("UPF-1", "SAFE_TEST_COMMAND")]


def test_ssh_adapter_handles_runner_failure():
    def failing_runner(node, command):
        raise RuntimeError("simulated connection failure")

    adapter = SSHAdapter(command_runner=failing_runner)

    result = adapter.execute(
        node="UPF-1",
        command="SAFE_TEST_COMMAND",
    )

    assert result["status"] == "failed"
    assert "simulated connection failure" in result["error"]


def test_ssh_adapter_does_not_execute_without_runner():
    adapter = SSHAdapter()

    result = adapter.execute(
        node="UPF-1",
        command="SAFE_TEST_COMMAND",
    )

    assert result["status"] == "not_configured"



def test_ssh_adapter_rejects_unknown_template():
    adapter = SSHAdapter(
        command_runner=lambda **kwargs: "should not run"
    )

    result = adapter.execute(
        node="UPF-1",
        template_id="invented_command",
        confirmed=True,
    )

    assert result["status"] == "rejected"


def test_ssh_adapter_requires_confirmation_for_config():
    adapter = SSHAdapter(
        command_runner=lambda **kwargs: "should not run"
    )

    result = adapter.execute(
        node="UPF-1",
        template_id="generate_netact_alarms",
        confirmed=False,
    )

    assert result["status"] == "awaiting_confirmation"


def test_ssh_adapter_passes_approved_template_to_runner():
    calls = []

    def fake_runner(**kwargs):
        calls.append(kwargs)
        return "mock execution successful"

    adapter = SSHAdapter(command_runner=fake_runner)

    result = adapter.execute(
        node="UPF-1",
        template_id="generate_netact_alarms",
        confirmed=True,
    )

    assert result["status"] == "success"
    assert calls == [{
        "node": "UPF-1",
        "template_id": "generate_netact_alarms",
    }]
    