import json

import pytest

from app import extraction
from app.schemas import OpportunitySource


FIELD_NAMES = (
    "application_deadline",
    "eligibility_requirements",
    "stipend_or_prize",
    "location_or_participation_mode",
    "application_method",
)


def response_payload(overrides=None):
    overrides = overrides or {}
    fields = {}
    for name in FIELD_NAMES:
        value = overrides.get(name)
        fields[name] = (
            {"value": value, "evidence": {"quote": value}}
            if value is not None
            else {"value": None, "evidence": None}
        )
    return {"fields": fields}


def test_parse_accepts_explicit_unknowns_and_preserves_source_text():
    source_text = "  Fictional announcement.\nDeadline: not stated.  "
    result = extraction.parse_extraction_response(
        source_text, json.dumps(response_payload())
    )

    assert isinstance(result, OpportunitySource)
    assert result.source_text == source_text.strip()
    assert result.fields.application_deadline.value is None


def test_parse_accepts_stated_claim_with_candidate_evidence():
    payload = response_payload({"application_deadline": "November 10, 2026"})
    result = extraction.parse_extraction_response(
        "Applications close November 10, 2026.", json.dumps(payload)
    )

    assert result.fields.application_deadline.value == "November 10, 2026"
    assert result.fields.application_deadline.evidence.quote == "November 10, 2026"


def test_parse_rejects_invalid_json():
    with pytest.raises(extraction.ExtractionResponseError, match="valid JSON"):
        extraction.parse_extraction_response("Source text", "{nope")


def test_parse_rejects_extra_top_level_key():
    payload = response_payload()
    payload["guess"] = "invented"

    with pytest.raises(extraction.ExtractionResponseError, match="exactly one"):
        extraction.parse_extraction_response("Source text", json.dumps(payload))


def test_parse_rejects_missing_required_field():
    payload = response_payload()
    del payload["fields"]["application_method"]

    with pytest.raises(extraction.ExtractionResponseError, match="required field schema"):
        extraction.parse_extraction_response("Source text", json.dumps(payload))


def test_parse_rejects_claim_without_evidence():
    payload = response_payload()
    payload["fields"]["application_deadline"] = {
        "value": "November 10, 2026",
        "evidence": None,
    }

    with pytest.raises(extraction.ExtractionResponseError, match="required field schema"):
        extraction.parse_extraction_response("Source text", json.dumps(payload))


def test_extract_fails_clearly_when_api_key_is_missing(monkeypatch):
    monkeypatch.delenv("GEMMA_API_KEY", raising=False)

    with pytest.raises(extraction.ExtractionProviderError, match="GEMMA_API_KEY"):
        extraction.extract_source("A fictional announcement.", api_key=None)


def test_extract_rejects_empty_source_before_calling_provider(monkeypatch):
    monkeypatch.setattr(
        extraction,
        "_request_gemma",
        lambda *_args: pytest.fail("Provider must not be called for empty input"),
    )

    with pytest.raises(extraction.ExtractionResponseError, match="must not be empty"):
        extraction.extract_source("   ", api_key="test-key")


def test_extract_uses_provider_response_and_selected_model(monkeypatch):
    payload = response_payload({"application_deadline": "November 10, 2026"})
    captured = {}

    def fake_request(prompt, api_key, model):
        captured.update(prompt=prompt, api_key=api_key, model=model)
        return json.dumps(payload)

    monkeypatch.setattr(extraction, "_request_gemma", fake_request)
    result = extraction.extract_source(
        "Deadline: November 10, 2026.", api_key="test-key", model="test-model"
    )

    assert result.fields.application_deadline.value == "November 10, 2026"
    assert captured["api_key"] == "test-key"
    assert captured["model"] == "test-model"
    assert "Never infer" in captured["prompt"]


def test_extract_rejects_overlong_input_before_provider_call(monkeypatch):
    monkeypatch.setattr(
        extraction,
        "_request_gemma",
        lambda *_args: pytest.fail("Provider must not be called for oversized input"),
    )

    source_text = "x" * (extraction.MAX_SOURCE_CHARACTERS + 1)
    with pytest.raises(extraction.ExtractionResponseError, match="character MVP limit"):
        extraction.extract_source(source_text, api_key="test-key")

def test_extract_rejects_fabricated_evidence_before_returning_source(monkeypatch):
    payload = response_payload(
        {"application_deadline": "December 1, 2026"}
    )
    payload["fields"]["application_deadline"]["evidence"]["quote"] = (
        "Applications close December 1, 2026"
    )
    monkeypatch.setattr(
        extraction, "_request_gemma", lambda *_args: json.dumps(payload)
    )

    with pytest.raises(
        extraction.ExtractionResponseError, match="application_deadline"
    ):
        extraction.extract_source(
            "Applications close November 10, 2026.", api_key="test-key"
        )


def test_extract_accepts_evidence_with_whitespace_variation(monkeypatch):
    payload = response_payload(
        {"eligibility_requirements": "Open to final-year students"}
    )
    payload["fields"]["eligibility_requirements"]["evidence"]["quote"] = (
        "Open to final-year\nstudents"
    )
    monkeypatch.setattr(
        extraction, "_request_gemma", lambda *_args: json.dumps(payload)
    )

    result = extraction.extract_source(
        "Eligibility: Open to final-year students.", api_key="test-key"
    )

    assert result.fields.eligibility_requirements.value == (
        "Open to final-year students"
    )


def test_parse_extraction_response_preserves_original_source_text():
    from app.extraction import parse_extraction_response

    original = (
        "Applications close on 30 November 2026. "
        "Remote participation. Apply through the official form."
    )
    response = """{
        "fields": {
            "application_deadline": {
                "value": "30 November 2026",
                "evidence": {
                    "quote": "Applications close on 30 November 2026."
                }
            },
            "eligibility_requirements": {
                "value": null,
                "evidence": null
            },
            "stipend_or_prize": {
                "value": null,
                "evidence": null
            },
            "location_or_participation_mode": {
                "value": "Remote participation",
                "evidence": {
                    "quote": "Remote participation."
                }
            },
            "application_method": {
                "value": "official form",
                "evidence": {
                    "quote": "Apply through the official form."
                }
            }
        }
    }"""

    result = parse_extraction_response(original, response)

    assert result.source_text == original
    assert "Remote participation." in result.source_text
