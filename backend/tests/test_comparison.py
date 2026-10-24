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



def test_finding_explains_conflict_without_picking_a_winner():
    a = make_source({"application_deadline": "November 10, 2026"})
    b = make_source({"application_deadline": "November 15, 2026"})

    finding = finding_for(compare_sources(a, b), "application_deadline")

    assert finding["explanation"] == (
        "Both sources state the application deadline, but the values differ. "
        "The comparison cannot determine which value is current or correct."
    )


def test_finding_explains_missing_information_separately_from_conflict():
    a = make_source({"stipend_or_prize": "INR 10,000"})
    b = make_source()

    finding = finding_for(compare_sources(a, b), "stipend_or_prize")

    assert finding["status"] == "not_found"
    assert "Source A states the stipend or prize" in finding["explanation"]
    assert "not a confirmed contradiction" in finding["explanation"]


def test_finding_explains_matching_values():
    a = make_source({"application_method": "Apply online"})
    b = make_source({"application_method": "APPLY ONLINE"})

    finding = finding_for(compare_sources(a, b), "application_method")

    assert finding["status"] == "match"
    assert "Both sources state the same application method" in finding["explanation"]

def test_missing_source_a_is_identified_and_explained():
    a = make_source()
    b = make_source({"application_deadline": "December 1, 2026"})

    finding = finding_for(compare_sources(a, b), "application_deadline")

    assert finding["status"] == "not_found"
    assert finding["missing_from"] == ["source_a"]
    assert "Source B states the application deadline" in finding["explanation"]
    assert "Source A does not" in finding["explanation"]


def test_missing_from_both_is_explained_as_unknown_not_conflict():
    finding = finding_for(
        compare_sources(make_source(), make_source()),
        "application_deadline",
    )

    assert finding["status"] == "not_found"
    assert finding["missing_from"] == ["both"]
    assert "Neither source states the application deadline" in finding["explanation"]
    assert "conflict" not in finding["status"]


def test_non_eligibility_differences_remain_conflicts_even_if_one_value_is_shorter():
    a = make_source({"stipend_or_prize": "INR 10,000"})
    b = make_source({"stipend_or_prize": "INR 10,000 per month"})

    finding = finding_for(compare_sources(a, b), "stipend_or_prize")

    assert finding["status"] == "conflict"


def test_eligibility_subset_rule_does_not_treat_explicit_negation_as_scope_difference():
    a = make_source({"eligibility_requirements": "undergraduate students"})
    b = make_source({"eligibility_requirements": "undergraduate students not enrolled full time"})

    finding = finding_for(compare_sources(a, b), "eligibility_requirements")

    assert finding["status"] == "conflict"


def test_explanation_and_next_step_exist_for_every_finding_status():
    a = make_source({
        "application_deadline": "November 10, 2026",
        "eligibility_requirements": "undergraduate students",
        "stipend_or_prize": "INR 10,000",
        "location_or_participation_mode": "Remote",
        "application_method": "Apply online",
    })
    b = make_source({
        "application_deadline": "November 15, 2026",
        "eligibility_requirements": "CS undergraduate students",
        "stipend_or_prize": None,
        "location_or_participation_mode": "Remote",
        "application_method": "Submit online",
    })

    result = compare_sources(a, b)

    assert all(item["explanation"].strip() for item in result["findings"])
    assert all(item["next_step"].strip() for item in result["findings"])

