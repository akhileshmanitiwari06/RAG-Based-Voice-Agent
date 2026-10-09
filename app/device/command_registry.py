
from typing import Dict


class CommandRegistry:
    """Allowlist of approved VoiceOps template operations."""

    APPROVED_OPERATIONS: Dict[str, str] = {
        # Read-only operations
        "check_subscribers": "READ",
        "check_bgp": "READ",
        "check_alarms": "READ",
        "check_interface": "READ",
        "check_system_health": "READ",

        # Configuration operations
        "generate_netact_alarms": "CONFIG",
        "clear_netact_alarms": "CONFIG",

        # Actions
        "save_configuration": "ACTION",
        "reboot_node": "ACTION",
    }

    def get_operation(self, template_id: str) -> str:
        """Return the operation for an approved template."""
        operation = self.APPROVED_OPERATIONS.get(template_id)

        if operation is None:
            raise ValueError(
                f"Template is not allowlisted: {template_id}"
            )

        return operation

    def is_approved(self, template_id: str) -> bool:
        """Return whether the template is approved."""
        return template_id in self.APPROVED_OPERATIONS

    def get_approved_templates(self) -> list[str]:
        """Return all approved template IDs."""
        return list(self.APPROVED_OPERATIONS.keys())
