from app.schemas import OpportunitySource
from app.comparison import compare_sources


FIELD_NAMES = (
    "application_deadline",
    "eligibility_requirements",
    "stipend_or_prize",
    "location_or_participation_mode",
    "application_method",
)


def make_source(overrides=None, source_text="Fictional opportunity announcement."):
    overrides = overrides or {}
    fields = {}
    for name in FIELD_NAMES:
        value = overrides.get(name)
        fields[name] = (
            {"value": value, "evidence": {"quote": value}}
            if value is not None
            else {"value": None, "evidence": None}
        )
    return OpportunitySource(source_text=source_text, fields=fields)


def finding_for(result, field_name):
    return next(item for item in result["findings"] if item["field"] == field_name)


def test_returns_five_findings_in_fixed_field_order():
    result = compare_sources(make_source(), make_source())

    assert [item["field"] for item in result["findings"]] == list(FIELD_NAMES)
    assert all(item["status"] == "not_found" for item in result["findings"])


def test_matching_claims_ignore_case_and_repeated_whitespace():
    a = make_source({"application_deadline": "November 10, 2026"})
    b = make_source({"application_deadline": "  NOVEMBER   10, 2026 "})

    finding = finding_for(compare_sources(a, b), "application_deadline")

    assert finding["status"] == "match"
    assert finding["source_a"]["value"] == "November 10, 2026"
    assert finding["source_b"]["value"] == "NOVEMBER   10, 2026"


def test_different_deadlines_are_conflict_and_no_source_is_preferred():
    a = make_source({"application_deadline": "November 10, 2026"})
    b = make_source({"application_deadline": "November 15, 2026"})

    finding = finding_for(compare_sources(a, b), "application_deadline")

    assert finding["status"] == "conflict"
    assert finding["source_a"]["value"] == "November 10, 2026"
    assert finding["source_b"]["value"] == "November 15, 2026"
    assert "Verify" in finding["next_step"]


def test_one_unknown_claim_is_reported_as_missing_from_that_source():
    a = make_source({"stipend_or_prize": "INR 10,000"})
    b = make_source()

    finding = finding_for(compare_sources(a, b), "stipend_or_prize")

    assert finding["status"] == "not_found"
    assert finding["missing_from"] == ["source_b"]


def test_unknown_in_both_sources_is_not_a_conflict():
    result = compare_sources(make_source(), make_source())
    finding = finding_for(result, "stipend_or_prize")

    assert finding["status"] == "not_found"
    assert finding["missing_from"] == ["both"]


def test_narrower_eligibility_word_set_is_partial_mismatch():
    a = make_source({"eligibility_requirements": "undergraduate students"})
    b = make_source({"eligibility_requirements": "CS undergraduate students"})

    finding = finding_for(compare_sources(a, b), "eligibility_requirements")

    assert finding["status"] == "partial_mismatch"


def test_explicit_eligibility_negation_is_a_conflict_not_scope_difference():
    a = make_source({"eligibility_requirements": "eligible undergraduate students"})
    b = make_source({"eligibility_requirements": "not eligible undergraduate students"})

    finding = finding_for(compare_sources(a, b), "eligibility_requirements")

    assert finding["status"] == "conflict"


def test_unrelated_eligibility_claims_are_conflicting():
    a = make_source({"eligibility_requirements": "undergraduate students"})
    b = make_source({"eligibility_requirements": "working professionals"})

    finding = finding_for(compare_sources(a, b), "eligibility_requirements")

    assert finding["status"] == "conflict"


def test_finding_preserves_evidence_quotes():
    a = make_source({"application_method": "Submit the online form"})
    b = make_source({"application_method": "Submit the online form"})

    finding = finding_for(compare_sources(a, b), "application_method")

    assert finding["source_a"]["evidence"]["quote"] == "Submit the online form"
    assert finding["source_b"]["evidence"]["quote"] == "Submit the online form"


def test_equivalent_deadline_formats_are_a_match():
    a = make_source({
        "application_deadline": "November 10, 2026"
    })
    b = make_source({
        "application_deadline": "10 November 2026"
    })

    finding = finding_for(
        compare_sources(a, b),
        "application_deadline",
    )

    assert finding["status"] == "match"


def test_iso_and_month_name_deadlines_are_a_match():
    a = make_source({"application_deadline": "2026-11-10"})
    b = make_source({"application_deadline": "November 10, 2026"})

    finding = finding_for(compare_sources(a, b), "application_deadline")

    assert finding["status"] == "match"


def test_abbreviated_month_deadlines_are_a_match():
    a = make_source({"application_deadline": "Nov 10, 2026"})
    b = make_source({"application_deadline": "10 Nov 2026"})

    finding = finding_for(compare_sources(a, b), "application_deadline")

    assert finding["status"] == "match"


def test_different_normalized_deadlines_remain_a_conflict():
    a = make_source({"application_deadline": "November 10, 2026"})
    b = make_source({"application_deadline": "2026-11-15"})

    finding = finding_for(compare_sources(a, b), "application_deadline")

    assert finding["status"] == "conflict"
