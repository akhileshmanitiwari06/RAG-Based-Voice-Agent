# VoiceOps Agent

A simulator-based, human-in-the-loop network operations assistant built with FastAPI and a LangGraph workflow. It interprets an operator request, retrieves an approved operation template, applies safety checks, requests explicit confirmation for higher-risk operations, and records workflow events in an audit log.

> **Safety note:** This project currently uses a local device simulator. A successful response means the simulated workflow completed; it does not mean a real telecom network was accessed or changed.

## Features

- FastAPI API with interactive Swagger documentation.
- Request intent and target-node identification.
- Approved-command/template validation through a command registry.
- Retrieval of approved operation templates (RAG).
- Human confirmation before higher-risk operations.
- Dry-run planning before simulated changes.
- Simulated apply, verification, and rollback operations.
- Session-based pending confirmations.
- Audit records for workflow events.
- Automated tests for core components and workflows.

## Architecture at a glance

```text
Operator request
      |
      v
FastAPI endpoints
  /dialogue  /plan  /confirm
      |
      v
Intent identification + LangGraph workflow
      |
      v
Approved template retrieval / validation
      |
      v
Safety policy and confirmation gate
      |
      +---- confirmation required ----> wait for /confirm
      |
      v
Dry run -> simulated apply -> verification
                         |
                         +---- verification failure -> rollback
      |
      v
Audit events and API response
```

Supporting components include the device simulator, command registry, session manager, and audit logger.

## Requirements

- Python installed on your machine.
- PowerShell or another terminal.
- Project dependencies installed in the active Python environment.

The exact Python version and dependency list should be taken from this repository's environment/configuration files.

## Setup on Windows PowerShell

Open a terminal in the project directory.

```powershell
# Create a virtual environment (skip if .venv already exists)
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Install dependencies if the project has a requirements.txt
pip install -r requirements.txt
```

If this repository uses a different dependency manager or does not have `requirements.txt`, follow the files included in the repository rather than creating an unverified dependency list.

## Run the API

From the project root, with the virtual environment active:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open the interactive API docs:

- Swagger UI: http://127.0.0.1:8000/docs
- Health endpoint: http://127.0.0.1:8000/health

Keep the server terminal open while testing. Press `Ctrl+C` to stop the server.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Application status |
| `GET` | `/health` | Health check |
| `POST` | `/dialogue` | Process a dialogue request and return its status |
| `POST` | `/plan` | Identify the requested operation and return a plan; higher-risk operations may require confirmation |
| `POST` | `/confirm` | Confirm or cancel a pending operation |
| `GET` | `/audit/{session_id}` | Retrieve audit records for a session |

Open `/docs` to see the current request schemas. The examples below reflect the request bodies tested in this project session.

## Example demo: plan and confirm

### 1. Create a plan

In Swagger UI, open `POST /plan`, select **Try it out**, and submit:

```json
{
  "message": "Generate NetAct alarms on UPF-1",
  "session_id": "demo-session-001"
}
```

For the tested simulator workflow, the response returned `awaiting_confirmation` with intent `generate_netact_alarms`, node `UPF-1`, and risk `HIGH`.

### 2. Confirm the pending operation

Use `POST /confirm` with matching session, intent, node, and risk values:

```json
{
  "session_id": "demo-session-001",
  "intent": "generate_netact_alarms",
  "node": "UPF-1",
  "risk": "HIGH",
  "confirmation": "yes"
}
```

A successful simulator response includes the plan, dry-run result, execution result, verification result, and rollback field. Always inspect the actual response; do not assume a request succeeded solely because it was submitted.

### 3. Inspect the audit trail

Open `GET /audit/{session_id}` and enter:

```text
demo-session-001
```

Audit records observed during testing included request/intent identification, template retrieval and validation, safety checks, awaiting confirmation, dry run, apply, verification, and completion. Older requests can remain in the same session's audit history.

## Test suite

With the virtual environment activated, run:

```powershell
pytest -q -p no:cacheprovider
```

The most recent test run reported **58 passed**. Run the suite again after making changes; this README does not guarantee that future runs will pass.

## Safety and limitations

- This is a **simulator-based demonstration**, not a production network operations tool.
- Use only allowlisted operations and approved templates.
- Higher-risk operations should go through the explicit confirmation workflow.
- Review dry-run, execution, verification, rollback, and audit results instead of relying only on the top-level status.
- In-memory session state can be lost when the server process restarts and may not be shared across multiple worker processes.
- Audit retention and persistence depend on the project's logger implementation.
- Before any real network integration, add appropriate authentication/authorization, secret management, durable session storage, robust audit retention, operational approvals, timeout handling, and environment-specific safeguards.

## Suggested demo sequence

1. Start the API server.
2. Open `/docs`.
3. Call `GET /health`.
4. Submit a request to `POST /plan`.
5. Inspect the returned intent, node, risk, template, and confirmation requirement.
6. Submit matching confirmation to `POST /confirm`.
7. Inspect the execution and verification fields.
8. Retrieve the audit records using `GET /audit/{session_id}`.
9. Run the test suite and show the result.

## Project status

At the time this README was drafted, the confirmation flow and audit endpoint had been exercised manually, and the test suite reported 58 passing tests. The project should still be treated as a development/demo implementation until its remaining integration, persistence, security, and deployment requirements are reviewed.
