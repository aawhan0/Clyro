import pytest

from app.evidence import EvidenceValidationError, validate_source_evidence
from app.schemas import OpportunitySource


FIELD_NAMES = (
    "application_deadline",
    "eligibility_requirements",
    "stipend_or_prize",
    "location_or_participation_mode",
    "application_method",
)


def make_source(source_text, overrides=None):
    overrides = overrides or {}
    fields = {}
    for name in FIELD_NAMES:
        quote = overrides.get(name)
        fields[name] = (
            {"value": quote, "evidence": {"quote": quote}}
            if quote is not None
            else {"value": None, "evidence": None}
        )
    return OpportunitySource(source_text=source_text, fields=fields)


def test_accepts_quote_found_verbatim_in_source():
    source = make_source(
        "Applications close November 10, 2026.",
        {"application_deadline": "November 10, 2026"},
    )

    assert validate_source_evidence(source) is source


def test_accepts_whitespace_variation_without_rewriting_quote():
    source = make_source(
        "Eligibility: Open to final-year students.",
        {"eligibility_requirements": "Open to\n  final-year\tstudents."},
    )

    result = validate_source_evidence(source)

    assert result.fields.eligibility_requirements.evidence.quote == (
        "Open to\n  final-year\tstudents."
    )


def test_rejects_fabricated_quote():
    source = make_source(
        "Applications close November 10, 2026.",
        {"application_deadline": "Applications close December 1, 2026"},
    )

    with pytest.raises(EvidenceValidationError, match="application_deadline"):
        validate_source_evidence(source)


def test_rejects_case_or_punctuation_changes():
    source = make_source(
        "Applications close November 10, 2026.",
        {"application_deadline": "applications close November 10 2026"},
    )

    with pytest.raises(EvidenceValidationError, match="application_deadline"):
        validate_source_evidence(source)


def test_reports_each_field_with_invalid_evidence():
    source = make_source(
        "Only the deadline is stated: November 10, 2026.",
        {
            "application_deadline": "November 10, 2026",
            "stipend_or_prize": "₹50,000 prize",
            "application_method": "Apply through the official portal",
        },
    )

    with pytest.raises(EvidenceValidationError) as exc_info:
        validate_source_evidence(source)

    message = str(exc_info.value)
    assert "stipend_or_prize" in message
    assert "application_method" in message


def test_unknown_fields_do_not_require_quotes():
    source = make_source("Announcement with no deadline, stipend, or location.")

    assert validate_source_evidence(source) is source
