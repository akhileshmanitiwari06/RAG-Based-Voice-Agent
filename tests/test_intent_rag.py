from app.agent.intent import extract_intent
from app.rag.retriever import search


def test_generate_netact_intent_matches_rag():

    result = extract_intent(
        "Generate NetAct alarms on UPF-1"
    )

    assert result["intent"] == "generate_netact_alarms"

    rag_results = search(
        result["intent"],
        top_k=1,
    )

    assert len(rag_results) == 1
    assert rag_results[0]["template_id"] == "generate_netact_alarms"


def test_clear_netact_intent_matches_rag():

    result = extract_intent(
        "Clear NetAct alarms on UPF-1"
    )

    assert result["intent"] == "clear_netact_alarms"

    rag_results = search(
        result["intent"],
        top_k=1,
    )

    assert len(rag_results) == 1
    assert rag_results[0]["template_id"] == "clear_netact_alarms"


def test_save_config_intent_matches_rag():

    result = extract_intent(
        "Save configuration on UPF-1"
    )

    assert result["intent"] == "save_configuration"

    rag_results = search(
        result["intent"],
        top_k=1,
    )

    assert len(rag_results) == 1
    assert rag_results[0]["template_id"] == "save_configuration"


def test_reboot_intent_matches_rag():

    result = extract_intent(
        "Reboot UPF-1"
    )

    assert result["intent"] == "reboot_node"

    rag_results = search(
        result["intent"],
        top_k=1,
    )

    assert len(rag_results) == 1
    assert rag_results[0]["template_id"] == "reboot_node"