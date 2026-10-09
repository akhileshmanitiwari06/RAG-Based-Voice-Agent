from app.rag.metadata import load_templates


def test_templates_loaded():

    templates = load_templates()

    template_ids = {
        item["template_id"]
        for item in templates
    }

    assert "check_subscribers" in template_ids
    assert "check_bgp" in template_ids
    assert "check_alarms" in template_ids