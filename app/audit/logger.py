import json
from datetime import datetime, timezone
from pathlib import Path


AUDIT_DIR = Path("audit_logs")
AUDIT_DIR.mkdir(exist_ok=True)


class AuditLogger:

    def __init__(self):
        self.audit_dir = AUDIT_DIR

    def log(
        self,
        session_id: str,
        event: str,
        details: dict | None = None,
    ):

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "event": event,
            "details": details or {},
        }

        file_path = self.audit_dir / f"{session_id}.jsonl"

        with open(
            file_path,
            "a",
            encoding="utf-8",
        ) as f:

            f.write(
                json.dumps(record)
                + "\n"
            )

        return record

    def read(self, session_id: str):

        file_path = self.audit_dir / f"{session_id}.jsonl"

        if not file_path.exists():
            return []

        records = []

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as f:

            for line in f:
                if line.strip():
                    records.append(
                        json.loads(line)
                    )

        return records