
from app.device.command_registry import CommandRegistry


class SSHAdapter:
    """Controlled adapter supporting mock and approved-template modes."""

    def __init__(self, command_runner=None):
        self.command_runner = command_runner
        self.registry = CommandRegistry()

    def execute(
        self,
        node: str,
        command: str | None = None,
        template_id: str | None = None,
        confirmed: bool = False,
    ):
        # Legacy command mode: intended only for mock/testing use.
        if command is not None:
            if not command.strip():
                return {
                    "node": node,
                    "status": "failed",
                    "error": "Empty command rejected",
                }

            if self.command_runner is None:
                return {
                    "node": node,
                    "status": "not_configured",
                    "message": "SSH runner is not configured",
                }

            try:
                output = self.command_runner(node=node, command=command)
                return {
                    "node": node,
                    "status": "success",
                    "output": output,
                }
            except Exception as exc:
                return {
                    "node": node,
                    "status": "failed",
                    "error": str(exc),
                }

        # Approved-template mode
        if not template_id or not self.registry.is_approved(template_id):
            return {
                "node": node,
                "status": "rejected",
                "reason": "Template is not allowlisted",
            }

        operation = self.registry.get_operation(template_id)

        if operation != "READ" and not confirmed:
            return {
                "node": node,
                "template_id": template_id,
                "status": "awaiting_confirmation",
                "reason": "Explicit confirmation required",
            }

        if self.command_runner is None:
            return {
                "node": node,
                "template_id": template_id,
                "status": "not_configured",
                "message": "SSH runner is not configured",
            }

        try:
            output = self.command_runner(
                node=node,
                template_id=template_id,
            )
            return {
                "node": node,
                "template_id": template_id,
                "status": "success",
                "output": output,
            }
        except Exception as exc:
            return {
                "node": node,
                "template_id": template_id,
                "status": "failed",
                "error": str(exc),
            }
