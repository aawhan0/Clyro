import pytest
from pydantic import ValidationError

from app.schemas import OpportunitySource


def _unknown_fields():
    return {
        name: {"value": None, "evidence": None}
        for name in (
            "application_deadline",
            "eligibility_requirements",
            "stipend_or_prize",
            "location_or_participation_mode",
            "application_method",
        )
    }


def test_accepts_all_five_fields_with_explicit_unknowns():
    source = OpportunitySource(
        source_text="A fictional student opportunity announcement.",
        fields=_unknown_fields(),
    )

    assert source.fields.application_deadline.value is None
    assert source.fields.eligibility_requirements.value is None
    assert source.fields.stipend_or_prize.value is None
    assert source.fields.location_or_participation_mode.value is None
    assert source.fields.application_method.value is None


def test_accepts_claim_with_candidate_evidence():
    fields = _unknown_fields()
    fields["application_deadline"] = {
        "value": "November 10, 2026",
        "evidence": {"quote": "Applications close November 10, 2026."},
    }

    source = OpportunitySource(
        source_text="Applications close November 10, 2026.",
        fields=fields,
    )

    assert source.fields.application_deadline.value == "November 10, 2026"
    assert source.fields.application_deadline.evidence.quote.startswith("Applications close")


def test_rejects_stated_claim_without_evidence():
    fields = _unknown_fields()
    fields["application_deadline"] = {"value": "November 10, 2026"}

    with pytest.raises(ValidationError, match="must include supporting evidence"):
        OpportunitySource(source_text="Deadline: November 10, 2026.", fields=fields)


def test_rejects_evidence_for_unknown_claim():
    fields = _unknown_fields()
    fields["stipend_or_prize"] = {
        "value": None,
        "evidence": {"quote": "Prize: INR 10,000"},
    }

    with pytest.raises(ValidationError, match="must not include evidence"):
        OpportunitySource(source_text="Prize: INR 10,000", fields=fields)


def test_rejects_missing_required_field():
    fields = _unknown_fields()
    del fields["application_method"]

    with pytest.raises(ValidationError):
        OpportunitySource(source_text="Fictional announcement.", fields=fields)


def test_rejects_unexpected_field():
    fields = _unknown_fields()
    fields["application_deadline"]["extra_guess"] = "November 10"

    with pytest.raises(ValidationError):
        OpportunitySource(source_text="Fictional announcement.", fields=fields)


@pytest.mark.parametrize("source_text", ["", "   "])
def test_rejects_empty_source_text(source_text):
    with pytest.raises(ValidationError):
        OpportunitySource(source_text=source_text, fields=_unknown_fields())


def test_rejects_empty_evidence_quote():
    fields = _unknown_fields()
    fields["application_deadline"] = {
        "value": "November 10, 2026",
        "evidence": {"quote": "   "},
    }

    with pytest.raises(ValidationError):
        OpportunitySource(source_text="Deadline November 10, 2026", fields=fields)
