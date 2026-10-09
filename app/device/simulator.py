from copy import deepcopy


class DeviceSimulator:
    def __init__(self):
        self.devices = {
            "UPF-1": {
                "subscribers": 12450,
                "bgp": "ESTABLISHED",
                "alarms": 2,
                "interfaces": {
                    "eth0": "UP",
                    "eth1": "UP",
                    "eth2": "DOWN",
                },
                "netact_alarm_port": "UP",
                "config_saved": False,
                "reboot_count": 0,
            },
            "UPF-2": {
                "subscribers": 980,
                "bgp": "ESTABLISHED",
                "alarms": 0,
                "interfaces": {
                    "eth0": "UP",
                    "eth1": "UP",
                    "eth2": "UP",
                },
                "netact_alarm_port": "UP",
                "config_saved": False,
                "reboot_count": 0,
            },
        }

        # Used only for controlled rollback/failure testing.
        self.force_verification_failure = False

    def _get_device(self, node: str):
        if node not in self.devices:
            raise ValueError(f"Unknown node: {node}")
        return self.devices[node]

    # -------------------------
    # READ OPERATIONS
    # -------------------------

    def show_subscribers(self, node: str):
        device = self._get_device(node)

        return {
            "success": True,
            "node": node,
            "subscribers": device["subscribers"],
            "status": "success",
        }

    def show_bgp(self, node: str):
        device = self._get_device(node)

        return {
            "node": node,
            "bgp_status": device["bgp"],
            "status": "success",
        }

    def show_alarms(self, node: str):
        device = self._get_device(node)

        return {
            "node": node,
            "active_alarms": device["alarms"],
            "status": "success",
        }

    def show_interface(self, node: str, interface: str):
        device = self._get_device(node)

        state = device["interfaces"].get(interface)

        if state is None:
            return {
                "node": node,
                "interface": interface,
                "status": "not_found",
            }

        return {
            "node": node,
            "interface": interface,
            "state": state,
            "status": "success",
        }

    # -------------------------
    # CONFIGURATION OPERATIONS
    # -------------------------

    def dry_run(self, node: str, operation: str):
        device = self._get_device(node)

        if operation == "generate_netact_alarms":
            return {
                "node": node,
                "operation": operation,
                "dry_run": True,
                "before": device["netact_alarm_port"],
                "after": "DOWN",
                "change": "Simulated NetAct alarm port would be disabled",
            }

        if operation == "clear_netact_alarms":
            return {
                "node": node,
                "operation": operation,
                "dry_run": True,
                "before": device["netact_alarm_port"],
                "after": "UP",
                "change": "Port would be enabled",
            }

        if operation == "save_configuration":
            return {
                "node": node,
                "operation": operation,
                "dry_run": True,
                "change": "Current configuration would be saved",
            }

        if operation == "reboot_node":
            return {
                "node": node,
                "operation": operation,
                "dry_run": True,
                "change": "Node would be rebooted",
            }

        raise ValueError(f"Unsupported operation: {operation}")

    def apply(self, node: str, operation: str):
        device = self._get_device(node)

        if operation == "generate_netact_alarms":
            device["netact_alarm_port"] = "DOWN"

        elif operation == "clear_netact_alarms":
            device["netact_alarm_port"] = "UP"

        elif operation == "save_configuration":
            device["config_saved"] = True

        elif operation == "reboot_node":
            device["reboot_count"] += 1

        else:
            raise ValueError(f"Unsupported operation: {operation}")

        return {
            "node": node,
            "operation": operation,
            "status": "applied",
        }

    # -------------------------
    # VERIFICATION
    # -------------------------

    def verify(self, node: str, operation: str):
        device = self._get_device(node)

        # Controlled failure injection for rollback testing.
        if self.force_verification_failure:
            return {
                "node": node,
                "operation": operation,
                "verified": False,
                "status": "failed",
                "reason": "Simulated verification failure",
            }

        if operation == "generate_netact_alarms":
            passed = device["netact_alarm_port"] == "DOWN"

        elif operation == "clear_netact_alarms":
            passed = device["netact_alarm_port"] == "UP"

        elif operation == "save_configuration":
            passed = device["config_saved"] is True

        elif operation == "reboot_node":
            passed = device["reboot_count"] > 0

        else:
            raise ValueError(f"Unsupported operation: {operation}")

        return {
            "node": node,
            "operation": operation,
            "verified": passed,
            "status": "success" if passed else "failed",
        }

    # -------------------------
    # ROLLBACK
    # -------------------------

    def rollback(self, node: str, operation: str):
        device = self._get_device(node)

        if operation == "generate_netact_alarms":
            device["netact_alarm_port"] = "UP"

        elif operation == "clear_netact_alarms":
            device["netact_alarm_port"] = "DOWN"

        elif operation == "save_configuration":
            device["config_saved"] = False

        elif operation == "reboot_node":
            # Simulator cannot truly undo a reboot.
            # We only record rollback handling.
            device["reboot_count"] = max(
                0,
                device["reboot_count"] - 1
            )

        else:
            raise ValueError(f"Unsupported operation: {operation}")

        return {
            "node": node,
            "operation": operation,
            "status": "rolled_back",
        }

    # -------------------------
    # TEST / FAILURE INJECTION
    # -------------------------

    def enable_verification_failure(self):
        self.force_verification_failure = True

    def disable_verification_failure(self):
        self.force_verification_failure = False

    # -------------------------
    # SNAPSHOT
    # -------------------------

    def snapshot(self, node: str):
        return deepcopy(self._get_device(node))