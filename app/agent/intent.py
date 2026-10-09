import re
from typing import Dict, Any


def extract_intent(message: str) -> Dict[str, Any]:
    """
    Deterministic intent and parameter extraction.

    Specific/action phrases are checked before generic keywords
    to avoid conflicts such as:
        "Generate NetAct alarms"
        vs
        "Check alarms"
    """

    text = message.lower().strip()

    # ---------------------------------
    # Extract node
    # ---------------------------------

    node_match = re.search(
        r"\b(upf-\d+|cmg-\d+)\b",
        text
    )

    node = (
        node_match.group(1).upper()
        if node_match
        else None
    )

    # ---------------------------------
    # Extract interface
    # ---------------------------------

    interface_match = re.search(
        r"\b(?:interface|port)\s*"
        r"(eth\d+|[\w/-]+)\b",
        text
    )

    interface = (
        interface_match.group(1)
        if interface_match
        else None
    )

    parameters = {}

    if interface:
        parameters["interface"] = interface

    # ---------------------------------
    # Intent detection
    # IMPORTANT:
    # Specific operations FIRST
    # ---------------------------------

    # HIGH-RISK / CONFIG OPERATIONS
    if (
        "generate netact alarms" in text
        or "generate netact alarm" in text
    ):
        intent = "generate_netact_alarms"
        risk = "HIGH"

    elif (
        "clear netact alarms" in text
        or "clear netact alarm" in text
    ):
        intent = "clear_netact_alarms"
        risk = "HIGH"

    elif (
        "save configuration" in text
        or "save config" in text
    ):
        intent = "save_configuration"
        risk = "ACTION"

    elif "reboot" in text:
        intent = "reboot_node"
        risk = "CRITICAL"

    # ---------------------------------
    # READ OPERATIONS
    # ---------------------------------

    elif "subscriber" in text:
        intent = "check_subscribers"
        risk = "READ"

    elif (
        "bgp" in text
        or "neighbor" in text
        or "neighbour" in text
    ):
        intent = "check_bgp"
        risk = "READ"

    elif "alarm" in text:
        intent = "check_alarms"
        risk = "READ"

    elif "interface" in text:
        intent = "check_interface"
        risk = "READ"

    elif (
        "system health" in text
        or "health check" in text
    ):
        intent = "check_system_health"
        risk = "READ"

    else:
        intent = None
        risk = "UNKNOWN"

    return {
        "intent": intent,
        "node": node,
        "risk": risk,
        "parameters": parameters,
    }