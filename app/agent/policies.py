RISK_LEVELS = {
    "READ": 1,
    "ACTION": 2,
    "CONFIG": 3,
    "HIGH": 4,
    "CRITICAL": 5,
}


def requires_confirmation(risk: str) -> bool:
    return RISK_LEVELS.get(risk.upper(), 5) >= 3


def is_allowed_intent(intent: str) -> bool:
    allowed = {
        "check_subscribers",
        "check_bgp",
        "check_alarms",
        "check_interface",
        "check_system_health",
        "generate_netact_alarms",
        "clear_netact_alarms",
        "save_configuration",
        "reboot_node",
    }

    return intent in allowed


def validate_execution(
    intent: str,
    risk: str,
    confirmed: bool,
):
    if not is_allowed_intent(intent):
        return {
            "allowed": False,
            "reason": "Intent is not allowlisted",
        }

    if requires_confirmation(risk) and not confirmed:
        return {
            "allowed": False,
            "reason": "Explicit confirmation required",
        }

    return {
        "allowed": True,
        "reason": "Execution policy passed",
    }