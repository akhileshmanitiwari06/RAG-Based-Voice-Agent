from app.agent.tools import ToolExecutor
from app.agent.policies import validate_execution
from app.rag.retriever import search
from app.audit.logger import AuditLogger


class VoiceOpsAgent:

    def __init__(self):

        self.tools = ToolExecutor()
        self.audit = AuditLogger()

    def handle(
        self,
        intent: str,
        node: str,
        risk: str = "READ",
        confirmed: bool = False,
        parameters: dict | None = None,
        session_id: str = "default-session",
    ):

        parameters = parameters or {}

        # =====================================
        # 1. REQUEST
        # =====================================

        self.audit.log(
            session_id,
            "REQUEST_RECEIVED",
            {
                "intent": intent,
                "node": node,
                "risk": risk,
            },
        )

        # =====================================
        # 2. RAG
        # =====================================

        results = search(
            intent,
            top_k=1,
        )

        if not results:

            self.audit.log(
                session_id,
                "RAG_FAILED",
                {
                    "intent": intent,
                },
            )

            return {
                "status": "blocked",
                "reason": "No approved template found",
            }

        template = results[0]

        self.audit.log(
            session_id,
            "RAG_RETRIEVED",
            {
                "template_id":
                    template["template_id"],
                "score":
                    template.get("score"),
                "source":
                    template.get("source"),
            },
        )

        # =====================================
        # 3. READ
        # =====================================

        if risk.upper() == "READ":

            result = self.tools.execute_read(
                intent=intent,
                node=node,
                parameters=parameters,
            )

            self.audit.log(
                session_id,
                "READ_EXECUTED",
                {
                    "intent": intent,
                    "node": node,
                },
            )

            return {
                "status": "completed",
                "mode": "read",
                "intent": intent,
                "node": node,
                "template": template,
                "result": result,
            }

        # =====================================
        # 4. SAFETY
        # =====================================

        policy = validate_execution(
            intent=intent,
            risk=risk,
            confirmed=confirmed,
        )

        self.audit.log(
            session_id,
            "SAFETY_CHECK",
            policy,
        )

        if not policy["allowed"]:

            self.audit.log(
                session_id,
                "AWAITING_CONFIRMATION",
                {
                    "reason":
                        policy["reason"],
                },
            )

            return {
                "status":
                    "awaiting_confirmation",
                "intent": intent,
                "node": node,
                "risk": risk,
                "template": template,
                "reason": policy["reason"],
            }

        # =====================================
        # 5. DRY RUN
        # =====================================

        dry_run = self.tools.dry_run(
            intent=intent,
            node=node,
        )

        self.audit.log(
            session_id,
            "DRY_RUN",
            dry_run,
        )

        # =====================================
        # 6. APPLY
        # =====================================

        applied = self.tools.apply(
            intent=intent,
            node=node,
        )

        self.audit.log(
            session_id,
            "APPLIED",
            applied,
        )

        # =====================================
        # 7. VERIFY
        # =====================================

        verification = self.tools.verify(
            intent=intent,
            node=node,
        )

        self.audit.log(
            session_id,
            "VERIFICATION",
            verification,
        )

        # =====================================
        # 8. ROLLBACK
        # =====================================

        if not verification["verified"]:

            rollback = self.tools.rollback(
                intent=intent,
                node=node,
            )

            self.audit.log(
                session_id,
                "ROLLBACK",
                rollback,
            )

            return {
                "status": "rolled_back",
                "intent": intent,
                "node": node,
                "dry_run": dry_run,
                "applied": applied,
                "verification": verification,
                "rollback": rollback,
            }

        # =====================================
        # 9. COMPLETE
        # =====================================

        self.audit.log(
            session_id,
            "COMPLETED",
            {
                "intent": intent,
                "node": node,
            },
        )

        return {
            "status": "completed",
            "mode": "change",
            "intent": intent,
            "node": node,
            "risk": risk,
            "template": template,
            "dry_run": dry_run,
            "applied": applied,
            "verification": verification,
        }