from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DialogueRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str = "default"


class DialogueResponse(BaseModel):
    session_id: str
    message: str
    intent: Optional[str] = None
    node: Optional[str] = None
    status: str = "received"


class AgentState(BaseModel):
    session_id: str
    user_request: str
    transcript: Optional[str] = None
    intent: Optional[str] = None
    target: Optional[str] = None

    parameters: Dict[str, Any] = Field(default_factory=dict)

    retrieved_template: Optional[Dict[str, Any]] = None
    risk: Optional[str] = None

    confirmation_required: bool = False
    confirmed: bool = False

    plan: Optional[Dict[str, Any]] = None
    confirmation_message: Optional[str] = None

    dry_run_result: Optional[Dict[str, Any]] = None
    execution_result: Optional[Dict[str, Any]] = None
    verification_result: Optional[Dict[str, Any]] = None
    rollback_result: Optional[Dict[str, Any]] = None

    audit_id: Optional[str] = None

    status: str = "received"

    errors: List[str] = Field(default_factory=list)


class ConfirmRequest(BaseModel):
    session_id: str
    intent: str
    node: str
    risk: str
    confirmation: str    
    
class PlanRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str = "default"    