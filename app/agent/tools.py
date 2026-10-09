
from app.device.simulator import DeviceSimulator
from app.device.command_registry import CommandRegistry


class ToolExecutor:
    def __init__(self):
        self.device = DeviceSimulator()
        self.registry = CommandRegistry()

    # -------------------------
    # TEMPLATE VALIDATION
    # -------------------------

    def validate_template(self, template: dict):
        if not template:
            return {
                "valid": False,
                "reason": "No approved template provided",
            }

        required_fields = [
            "template_id",
            "intent",
            "operation",
            "risk",
            "source",
            "verification",
        ]

        missing = [
            field
            for field in required_fields
            if not template.get(field)
        ]

        if missing:
            return {
                "valid": False,
                "reason": f"Template missing fields: {missing}",
            }

        if template.get("source") != "approved_command_library":
            return {
                "valid": False,
                "reason": "Template source is not approved",
            }

        template_id = template["template_id"]

        if not self.registry.is_approved(template_id):
            return {
                "valid": False,
                "reason": "Template is not allowlisted",
            }

        if template["intent"] != template_id:
            return {
                "valid": False,
                "reason": "Template ID and intent do not match",
            }

        expected_operation = self.registry.get_operation(
            template_id
        )

        # Registry values describe execution risk categories.
        expected_template_operation = (
            "READ" if expected_operation == "READ"
            else "CONFIG" if expected_operation == "CONFIG"
            else "ACTION" if expected_operation == "ACTION"
            else "CRITICAL"
        )

        if template["operation"] != expected_template_operation:
            return {
                "valid": False,
                "reason": "Template operation does not match registry",
            }

        return {
            "valid": True,
            "template_id": template_id,
            "intent": template["intent"],
            "operation": template["operation"],
            "risk": template["risk"],
            "source": template["source"],
        }

    # -------------------------
    # READ OPERATIONS
    # -------------------------

    def execute_read(
        self,
        intent: str,
        node: str,
        parameters: dict | None = None,
    ):
        if not self.registry.is_approved(intent):
            return {
                "node": node,
                "status": "rejected",
                "reason": "Operation is not allowlisted",
            }

        parameters = parameters or {}

        if intent == "check_subscribers":
            return self.device.show_subscribers(node)

        if intent == "check_bgp":
            return self.device.show_bgp(node)

        if intent == "check_alarms":
            return self.device.show_alarms(node)

        if intent == "check_interface":
            interface = parameters.get("interface", "eth0")
            return self.device.show_interface(node, interface)

        raise ValueError(f"Unsupported read intent: {intent}")

    # -------------------------
    # DRY RUN
    # -------------------------

    def dry_run(self, intent: str, node: str):
        if not self.registry.is_approved(intent):
            return {
                "node": node,
                "operation": intent,
                "status": "rejected",
                "reason": "Operation is not allowlisted",
            }

        return self.device.dry_run(node, intent)

    # -------------------------
    # APPLY
    # -------------------------

    def apply(self, intent: str, node: str):
        if not self.registry.is_approved(intent):
            return {
                "node": node,
                "operation": intent,
                "status": "rejected",
                "reason": "Operation is not allowlisted",
            }

        return self.device.apply(node, intent)

    # -------------------------
    # VERIFY
    # -------------------------

    def verify(self, intent: str, node: str):
        if not self.registry.is_approved(intent):
            return {
                "node": node,
                "operation": intent,
                "verified": False,
                "status": "rejected",
                "reason": "Operation is not allowlisted",
            }

        return self.device.verify(node, intent)

    # -------------------------
    # ROLLBACK
    # -------------------------

    def rollback(self, intent: str, node: str):
        if not self.registry.is_approved(intent):
            return {
                "node": node,
                "operation": intent,
                "status": "rejected",
                "reason": "Operation is not allowlisted",
            }

        return self.device.rollback(node, intent)
