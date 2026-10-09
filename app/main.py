from fastapi import FastAPI

from app.agent.intent import extract_intent
from app.agent.workflow import VoiceOpsAgent
from app.audit.logger import AuditLogger
from app.agent.session import SessionManager
from app.models.schemas import AgentState
from app.agent.graph import voiceops_graph
from app.models.schemas import (
    DialogueRequest,
    DialogueResponse,
    ConfirmRequest,
    PlanRequest,
)

app = FastAPI(
    title="VoiceOps Agent",
    description="Human-in-the-loop Voice-Based Configuration Agent",
    version="1.0.0",
)


agent = VoiceOpsAgent()
session_manager = SessionManager()
audit = AuditLogger()


@app.get("/")
def root():
    return {
        "application": "VoiceOps Agent",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.post("/dialogue", response_model=DialogueResponse)
def dialogue(request: DialogueRequest):

    intent_result = extract_intent(request.message)

    intent = intent_result.get("intent")
    node = intent_result.get("node")
    risk = intent_result.get("risk", "READ")
    parameters = intent_result.get("parameters", {})

    if not intent:
        return DialogueResponse(
            session_id=request.session_id,
            message="I could not identify the requested operation.",
            intent=None,
            node=node,
            status="needs_clarification",
        )

    if not node:
        return DialogueResponse(
            session_id=request.session_id,
            message="Which target node should I use?",
            intent=intent,
            node=None,
            status="needs_clarification",
        )

    result = agent.handle(
        intent=intent,
        node=node,
        risk=risk,
        confirmed=False,
        parameters=parameters,
        session_id=request.session_id,
    )

    if result["status"] == "awaiting_confirmation":

        session_manager.create_pending(
            session_id=request.session_id,
            intent=intent,
            node=node,
            risk=risk,
            template=result.get("template"),
            parameters=parameters,
        )

        return DialogueResponse(
            session_id=request.session_id,
            message=(
                f"This is a {risk} operation. "
                "Explicit confirmation is required."
            ),
            intent=intent,
            node=node,
            status="awaiting_confirmation",
        )

    return DialogueResponse(
        session_id=request.session_id,
        message="Request processed successfully.",
        intent=intent,
        node=node,
        status=result["status"],
    )


@app.post("/plan")
def plan(request: PlanRequest):

    state = AgentState(
        session_id=request.session_id,
        user_request=request.message,
        confirmed=False,
    )

    result = voiceops_graph.invoke(state)

    if result.get("errors"):
        return {
            "session_id": request.session_id,
            "status": "blocked",
            "errors": result["errors"],
        }

    intent = result.get("intent")
    node = result.get("target")
    risk = result.get("risk")
    template = result.get("retrieved_template")

    if not intent:
        return {
            "session_id": request.session_id,
            "status": "needs_clarification",
            "message": "I could not identify the requested operation.",
        }

    if not node:
        return {
            "session_id": request.session_id,
            "status": "needs_clarification",
            "message": "Which target node should I use?",
            "intent": intent,
        }

    if result.get("confirmation_required"):
        session_manager.create_pending(
            session_id=request.session_id,
            intent=intent,
            node=node,
            risk=risk,
            template=template,
            parameters=result.get("parameters", {}),
        )
        print("DEBUG PENDING AFTER PLAN:", session_manager.get_pending(request.session_id))

        return {
            "session_id": request.session_id,
            "status": "awaiting_confirmation",
            "intent": intent,
            "node": node,
            "risk": risk,
            "template": template,
            "confirmation_message": (
                f"This is a {risk} operation on {node}. "
                "Explicit confirmation is required."
            ),
        }

    return {
        "session_id": request.session_id,
        "status": result.get("status", "completed"),
        "intent": intent,
        "node": node,
        "risk": risk,
        "result": result,
    }









@app.get("/audit/{session_id}")
def get_audit(session_id: str):

    return {
        "session_id": session_id,
        "records": audit.read(session_id),
    }
    


@app.post("/confirm")
def confirm(request: ConfirmRequest):

    confirmation = request.confirmation.strip().lower()

    if confirmation not in {
        "yes",
        "confirm",
        "confirmed",
        "i confirm",
    }:
        session_manager.clear(request.session_id)

        return {
            "status": "cancelled",
            "message": "Operation cancelled by user.",
            "session_id": request.session_id,
        }

    pending = session_manager.get_pending(request.session_id)
    print("DEBUG PENDING DURING CONFIRM:", pending)

    if not pending:
        return {
            "status": "blocked",
            "message": "No pending operation requires confirmation.",
            "session_id": request.session_id,
        }

    if pending["intent"] != request.intent:
        return {
            "status": "blocked",
            "message": "Confirmation does not match the pending intent.",
            "session_id": request.session_id,
        }

    if pending["node"] != request.node:
        return {
            "status": "blocked",
            "message": "Confirmation does not match the pending target.",
            "session_id": request.session_id,
        }

    if pending["risk"] != request.risk:
        return {
            "status": "blocked",
            "message": "Confirmation does not match the pending risk level.",
            "session_id": request.session_id,
        }

    # Build confirmed LangGraph state
    state = AgentState(
        session_id=request.session_id,
        user_request=pending["intent"],
        confirmed=True,
        intent=pending["intent"],
        target=pending["node"],
        risk=pending["risk"],
        parameters=pending.get("parameters", {}),
        retrieved_template=pending.get("template"),
    )

    # Execute confirmed operation through LangGraph
    result = voiceops_graph.invoke(state)

    # Clear pending confirmation after execution
    session_manager.clear(request.session_id)

    return {
        "session_id": request.session_id,
        "status": result.get("status"),
        "intent": result.get("intent"),
        "node": result.get("target"),
        "risk": result.get("risk"),
        "plan": result.get("plan"),
        "dry_run": result.get("dry_run_result"),
        "execution": result.get("execution_result"),
        "verification": result.get("verification_result"),
        "rollback": result.get("rollback_result"),
    }