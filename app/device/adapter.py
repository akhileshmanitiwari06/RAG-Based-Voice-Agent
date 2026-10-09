from typing import Any, Dict


class DeviceAdapter:
    """
    Execution abstraction for VoiceOps.

    The agent talks to this interface instead of directly
    executing shell/SSH commands.
    """

    def execute(
        self,
        node: str,
        command: str,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    def dry_run(
        self,
        node: str,
        command: str,
    ) -> Dict[str, Any]:
        return {
            "node": node,
            "dry_run": True,
            "command": command,
            "status": "validated",
        }