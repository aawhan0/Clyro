import pytest
from fastapi.testclient import TestClient

from app import main
from app.extraction import ExtractionProviderError, ExtractionResponseError
from app.schemas import OpportunitySource


client = TestClient(main.app)


def make_source(text, deadline=None):
    fields = {
        "application_deadline": (
            {"value": deadline, "evidence": {"quote": deadline}}
            if deadline
            else {"value": None, "evidence": None}
        ),
        "eligibility_requirements": {"value": None, "evidence": None},
        "stipend_or_prize": {"value": None, "evidence": None},
        "location_or_participation_mode": {"value": None, "evidence": None},
        "application_method": {"value": None, "evidence": None},
    }
    return OpportunitySource(source_text=text, fields=fields)


def test_health_check_does_not_call_provider():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_compare_endpoint_extracts_both_sources_and_returns_findings(monkeypatch):
    extracted = iter(
        [
            make_source("Deadline: November 10, 2026.", "November 10, 2026"),
            make_source("Deadline: November 15, 2026.", "November 15, 2026"),
        ]
    )
    calls = []

    def fake_extract(source_text):
        calls.append(source_text)
        return next(extracted)

    monkeypatch.setattr(main, "extract_source", fake_extract)
    response = client.post(
        "/api/compare",
        json={
            "source_a": "Deadline: November 10, 2026.",
            "source_b": "Deadline: November 15, 2026.",
        },
    )

    assert response.status_code == 200
    assert calls == [
        "Deadline: November 10, 2026.",
        "Deadline: November 15, 2026.",
    ]
    deadline = next(
        item for item in response.json()["findings"]
        if item["field"] == "application_deadline"
    )
    assert deadline["status"] == "conflict"
    assert deadline["source_a"]["evidence"]["quote"] == "November 10, 2026"
    assert deadline["source_b"]["evidence"]["quote"] == "November 15, 2026"
    assert len(response.json()["findings"]) == 5


def test_compare_endpoint_returns_gateway_error_for_provider_failure(monkeypatch):
    monkeypatch.setattr(
        main,
        "extract_source",
        lambda _text: (_ for _ in ()).throw(ExtractionProviderError("private detail")),
    )

    response = client.post(
        "/api/compare",
        json={"source_a": "Source A", "source_b": "Source B"},
    )

    assert response.status_code == 502
    assert response.json()["error"] == "extraction_provider_error"
    assert "private detail" not in response.text


def test_compare_endpoint_rejects_extraction_validation_failure(monkeypatch):
    monkeypatch.setattr(
        main,
        "extract_source",
        lambda _text: (_ for _ in ()).throw(
            ExtractionResponseError("Evidence quote was not found.")
        ),
    )

    response = client.post(
        "/api/compare",
        json={"source_a": "Source A", "source_b": "Source B"},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "extraction_validation_error"


@pytest.mark.parametrize(
    "payload",
    [
        {"source_a": "", "source_b": "valid"},
        {"source_a": "valid"},
        {"source_a": "x" * 30_001, "source_b": "valid"},
    ],
)
def test_compare_endpoint_rejects_invalid_request_payload(payload, monkeypatch):
    monkeypatch.setattr(
        main,
        "extract_source",
        lambda *_args: pytest.fail("Invalid request must not call extraction"),
    )

    response = client.post("/api/compare", json=payload)

    assert response.status_code == 422
