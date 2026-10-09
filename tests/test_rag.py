from app.rag.retriever import search


# -----------------------------------------
# Existing semantic retrieval tests
# -----------------------------------------

def test_bgp_retrieval():

    results = search(
        "check BGP status",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["template_id"] == "check_bgp"


def test_subscriber_retrieval():

    results = search(
        "show subscribers",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["template_id"] == "check_subscribers"


def test_alarm_retrieval():

    results = search(
        "check active alarms",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["template_id"] == "check_alarms"


# -----------------------------------------
# Exact approved-template retrieval tests
# -----------------------------------------

def test_generate_netact_retrieval():

    results = search(
        "generate_netact_alarms",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["template_id"] == "generate_netact_alarms"


def test_clear_netact_retrieval():

    results = search(
        "clear_netact_alarms",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["template_id"] == "clear_netact_alarms"


def test_save_configuration_retrieval():

    results = search(
        "save_configuration",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["template_id"] == "save_configuration"


def test_reboot_retrieval():

    results = search(
        "reboot_node",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["template_id"] == "reboot_node"


def test_interface_retrieval():

    results = search(
        "check_interface",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["template_id"] == "check_interface"


def test_system_health_retrieval():

    results = search(
        "check_system_health",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["template_id"] == "check_system_health"