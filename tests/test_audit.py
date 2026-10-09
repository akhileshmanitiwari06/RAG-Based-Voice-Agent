from app.audit.logger import AuditLogger


def test_audit_logger(tmp_path, monkeypatch):

    monkeypatch.setattr(
        "app.audit.logger.AUDIT_DIR",
        tmp_path,
    )

    logger = AuditLogger()

    logger.log(
        "test-session",
        "REQUEST_RECEIVED",
        {
            "intent": "check_subscribers"
        },
    )

    records = logger.read("test-session")

    assert len(records) == 1
    assert records[0]["event"] == "REQUEST_RECEIVED"
    assert (
        records[0]["details"]["intent"]
        == "check_subscribers"
    )