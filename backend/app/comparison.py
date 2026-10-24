"""Deterministic, evidence-preserving comparison for two opportunity sources."""

import re
from typing import Any

from app.schemas import FieldClaim, OpportunitySource


FIELD_NAMES = (
    "application_deadline",
    "eligibility_requirements",
    "stipend_or_prize",
    "location_or_participation_mode",
    "application_method",
)


def _normalize(value: str) -> str:
    """Normalize casing and whitespace only; do not infer semantic equivalence."""
    return " ".join(value.casefold().split())


def _tokens(value: str) -> set[str]:
    """Return word tokens for the narrow eligibility-scope comparison."""
    return set(re.findall(r"\w+", _normalize(value)))


def _claim_payload(claim: FieldClaim) -> dict[str, Any]:
    return {
        "value": claim.value,
        "evidence": claim.evidence.model_dump() if claim.evidence is not None else None,
    }


def _next_step(field_name: str, status: str, missing_from: list[str]) -> str:
    label = field_name.replace("_", " ")
    if status == "match":
        return "No follow-up needed for this field based on the supplied text."
    if status == "not_found":
        if missing_from == ["both"]:
            return f"Check the organizer's current page for the {label}; neither source states it."
        source = "Source A" if missing_from == ["source_a"] else "Source B"
        return f"Check the organizer's current page for the {label}; it is not stated in {source}."
    if status == "partial_mismatch":
        return f"Verify the exact {label} with the organizer; the sources state differently scoped requirements."
    return f"Verify the conflicting {label} against the organizer's current application page."


def _explanation(field_name: str, status: str, missing_from: list[str]) -> str:
    """Explain the comparison outcome without implying either source is authoritative."""
    label = field_name.replace("_", " ")
    if status == "match":
        return f"Both sources state the same {label}, after case and whitespace normalization."
    if status == "not_found":
        if missing_from == ["both"]:
            return f"Neither source states the {label}; there is nothing to compare yet."
        missing_source = "Source A" if missing_from == ["source_a"] else "Source B"
        present_source = "Source B" if missing_source == "Source A" else "Source A"
        return f"{present_source} states the {label}, but {missing_source} does not. This is missing information, not a confirmed contradiction."
    if status == "partial_mismatch":
        return f"Both sources describe the {label}, but their wording differs in scope. Check the exact conditions before relying on either description."
    return f"Both sources state the {label}, but the values differ. The comparison cannot determine which value is current or correct."


def _compare_claims(field_name: str, a: FieldClaim, b: FieldClaim) -> dict[str, Any]:
    missing_from: list[str] = []
    if a.value is None:
        missing_from.append("source_a")
    if b.value is None:
        missing_from.append("source_b")

    if missing_from:
        status = "not_found"
        if len(missing_from) == 2:
            missing_from = ["both"]
    elif _normalize(a.value) == _normalize(b.value):
        status = "match"
    elif field_name == "eligibility_requirements":
        tokens_a, tokens_b = _tokens(a.value), _tokens(b.value)
        # Never treat an explicit negation as merely a scope difference.
        # A token-set subset is only a weak lexical signal, not semantic reasoning.
        negation_tokens = {"not", "no", "never", "neither", "nor", "ineligible"}
        has_negation_a = bool(tokens_a & negation_tokens)
        has_negation_b = bool(tokens_b & negation_tokens)
        strict_subset = tokens_a != tokens_b and (
            tokens_a < tokens_b or tokens_b < tokens_a
        )
        status = (
            "partial_mismatch"
            if strict_subset and has_negation_a == has_negation_b
            else "conflict"
        )
    else:
        status = "conflict"

    return {
        "field": field_name,
        "status": status,
        "source_a": _claim_payload(a),
        "source_b": _claim_payload(b),
        "missing_from": missing_from,
        "explanation": _explanation(field_name, status, missing_from),
        "next_step": _next_step(field_name, status, missing_from),
    }


def compare_sources(source_a: OpportunitySource, source_b: OpportunitySource) -> dict[str, Any]:
    """Compare the five MVP fields without selecting a winning source.

    Matching is case/whitespace-insensitive. Eligibility can be marked as a
    partial mismatch only when one claim's word-token set is a strict subset
    of the other's. All other differing stated values are conflicts.
    """
    findings = [
        _compare_claims(
            field_name,
            getattr(source_a.fields, field_name),
            getattr(source_b.fields, field_name),
        )
        for field_name in FIELD_NAMES
    ]
    return {"findings": findings}
