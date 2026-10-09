from typing import Literal

from langgraph.graph import StateGraph, START, END

from app.models.schemas import AgentState
from app.agent.intent import extract_intent
from app.agent.policies import validate_execution
from app.rag.retriever import search
from app.agent.tools import ToolExecutor
from app.audit.logger import AuditLogger


tools = ToolExecutor()
audit = AuditLogger()


# --------------------------------------------------
# 1. Intent Node
# --------------------------------------------------

def intent_node(state: AgentState):

    # If intent/target/risk are already supplied
    # by a confirmed session, preserve them.
    if state.intent:
        audit.log(
            state.session_id,
            "INTENT_REUSED",
            {
                "intent": state.intent,
                "node": state.target,
                "risk": state.risk,
            },
        )
        return state

    # First-time request: extract intent from user text.
    result = extract_intent(state.user_request)

    state.intent = result.get("intent")
    state.target = result.get("node")
    state.risk = result.get("risk")
    state.parameters = result.get("parameters", {})

    audit.log(
        state.session_id,
        "INTENT_IDENTIFIED",
        {
            "intent": state.intent,
            "node": state.target,
            "risk": state.risk,
        },
    )

    return state


# --------------------------------------------------
# 2. RAG Node
# --------------------------------------------------


def rag_node(state: AgentState):
    if not state.intent:
        state.errors.append("Intent could not be identified")
        return state

    results = search(state.intent, top_k=1)

    if not results:
        state.errors.append("No approved template found")
        return state

    template = results[0]

    validation = tools.validate_template(template)

    audit.log(
        state.session_id,
        "TEMPLATE_VALIDATION",
        validation,
    )

    if not validation.get("valid"):
        state.errors.append(
            validation.get(
                "reason",
                "Template validation failed",
            )
        )
        state.status = "blocked"
        return state

    state.retrieved_template = template

    audit.log(
        state.session_id,
        "RAG_RETRIEVED",
        {
            "template_id": template.get("template_id"),
            "score": template.get("score"),
            "source": template.get("source"),
        },
    )

    return state


# --------------------------------------------------
# 3. Safety Node
# --------------------------------------------------

def safety_node(state: AgentState):

    if not state.intent:
        state.errors.append("Missing intent")
        return state

    if not state.target:
        state.errors.append("Missing target node")
        return state

    risk = state.risk or "CRITICAL"

    state.confirmation_required = (
        risk.upper() in {
            "CONFIG",
            "HIGH",
            "CRITICAL",
            "ACTION",
        }
    )

    policy = validate_execution(
        intent=state.intent,
        risk=risk,
        confirmed=state.confirmed,
    )

    audit.log(
        state.session_id,
        "SAFETY_CHECK",
        policy,
    )

    if not policy["allowed"]:
        state.confirmation_required = True

    return state


# --------------------------------------------------
# 4. Routing
# --------------------------------------------------

def route_after_safety(
    state: AgentState,
) -> Literal["read", "confirmation", "plan", "blocked"]:

    if state.errors:
        return "blocked"

    if not state.intent or not state.target:
        return "blocked"

    if state.risk == "READ":
        return "read"

    if state.confirmed:
        return "plan"

    return "confirmation"


# --------------------------------------------------
# 5. Read Execution
# --------------------------------------------------

def read_node(state: AgentState):

    result = tools.execute_read(
        intent=state.intent,
        node=state.target,
        parameters=state.parameters,
    )

    state.execution_result = result

    audit.log(
        state.session_id,
        "READ_EXECUTED",
        {
            "intent": state.intent,
            "node": state.target,
        },
    )

    return state


# --------------------------------------------------
# 6. Confirmation
# --------------------------------------------------

def confirmation_node(state: AgentState):

    state.confirmation_required = True

    audit.log(
        state.session_id,
        "AWAITING_CONFIRMATION",
        {
            "intent": state.intent,
            "node": state.target,
            "risk": state.risk,
        },
    )

    return state


# --------------------------------------------------
# 7. Plan Node
# --------------------------------------------------

def plan_node(state: AgentState):

    template = state.retrieved_template or {}

    state.plan = {
        "intent": state.intent,
        "target": state.target,
        "risk": state.risk,
        "template_id": template.get("template_id"),
        "source": template.get("source"),
        "operation": template.get("operation"),
        "verification": template.get("verification"),
    }

    state.confirmation_message = (
        f"Operation: {state.intent}\n"
        f"Target: {state.target}\n"
        f"Risk: {state.risk}\n"
        f"Approved template: {template.get('template_id')}\n"
        f"Source: {template.get('source')}"
    )

    state.status = "plan_ready"

    audit.log(
        state.session_id,
        "PLAN_READY",
        state.plan,
    )

    return state


# --------------------------------------------------
# 8. Dry Run Node
# --------------------------------------------------

def dry_run_node(state: AgentState):

    result = tools.dry_run(
        intent=state.intent,
        node=state.target,
    )

    state.dry_run_result = result
    state.status = "dry_run_completed"

    audit.log(
        state.session_id,
        "DRY_RUN",
        result,
    )

    return state


# --------------------------------------------------
# 9. Apply Node
# --------------------------------------------------

def apply_node(state: AgentState):

    result = tools.apply(
        intent=state.intent,
        node=state.target,
    )

    state.execution_result = result
    state.status = "applied"

    audit.log(
        state.session_id,
        "APPLIED",
        result,
    )

    return state


# --------------------------------------------------
# 10. Verify Node
# --------------------------------------------------

def verify_node(state: AgentState):

    result = tools.verify(
        intent=state.intent,
        node=state.target,
    )

    state.verification_result = result

    if result.get("verified"):
        state.status = "verified"
    else:
        state.status = "verification_failed"

    audit.log(
        state.session_id,
        "VERIFICATION",
        result,
    )

    return state


# --------------------------------------------------
# 11. Rollback Node
# --------------------------------------------------

def rollback_node(state: AgentState):

    result = tools.rollback(
        intent=state.intent,
        node=state.target,
    )

    state.rollback_result = result
    state.status = "rolled_back"

    audit.log(
        state.session_id,
        "ROLLBACK",
        result,
    )

    return state


# --------------------------------------------------
# 12. Verification Routing
# --------------------------------------------------

def route_after_verification(
    state: AgentState,
) -> Literal["complete", "rollback"]:

    if (
        state.verification_result
        and state.verification_result.get("verified")
    ):
        return "complete"

    return "rollback"


# --------------------------------------------------
# 13. Complete Node
# --------------------------------------------------

def complete_node(state: AgentState):

    state.status = "completed"

    audit.log(
        state.session_id,
        "COMPLETED",
        {
            "intent": state.intent,
            "node": state.target,
        },
    )

    return state





# --------------------------------------------------
# 7. Build Graph
# --------------------------------------------------

def build_graph():
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("intent", intent_node)
    graph.add_node("rag", rag_node)
    graph.add_node("safety", safety_node)
    graph.add_node("read", read_node)
    graph.add_node("confirmation", confirmation_node)
    graph.add_node("plan", plan_node)
    graph.add_node("dry_run", dry_run_node)
    graph.add_node("apply", apply_node)
    graph.add_node("verify", verify_node)
    graph.add_node("rollback", rollback_node)
    graph.add_node("complete", complete_node)

    # Initial flow
    graph.add_edge(START, "intent")
    graph.add_edge("intent", "rag")
    graph.add_edge("rag", "safety")

    # Safety routing
    graph.add_conditional_edges(
    "safety",
    route_after_safety,
    {
        "read": "read",
        "confirmation": "confirmation",
        "plan": "plan",
        "blocked": END,
    },
)

    # Read-only path
    graph.add_edge("read", END)

    # Change path
    graph.add_edge("confirmation", END)

    # Execution lifecycle
    graph.add_edge("plan", "dry_run")
    graph.add_edge("dry_run", "apply")
    graph.add_edge("apply", "verify")

    # Verification
    graph.add_conditional_edges(
        "verify",
        route_after_verification,
        {
            "complete": "complete",
            "rollback": "rollback",
        },
    )

    # Rollback
    graph.add_edge("rollback", "complete")

    # End
    graph.add_edge("complete", END)

    return graph.compile()


# Compiled graph used by tests/API
voiceops_graph = build_graph()