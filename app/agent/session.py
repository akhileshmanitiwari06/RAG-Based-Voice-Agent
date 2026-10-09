
from typing import Dict, Any, Optional


class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def create_pending(
        self,
        session_id: str,
        intent: str,
        node: str,
        risk: str,
        template: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        self.sessions[session_id] = {
            "intent": intent,
            "node": node,
            "risk": risk,
            "template": template,
            "parameters": parameters or {},
            "status": "awaiting_confirmation",
        }

    def get_pending(self, session_id: str):
        return self.sessions.get(session_id)

    def clear(self, session_id: str):
        self.sessions.pop(session_id, None)
