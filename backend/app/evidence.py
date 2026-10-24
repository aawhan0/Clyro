"""Literal evidence checks for extracted opportunity claims."""

import re

from app.schemas import OpportunitySource


class EvidenceValidationError(ValueError):
    """One or more evidence quotes do not occur in the supplied source."""


def _normalize_whitespace(text: str) -> str:
    """Collapse whitespace only; keep case and punctuation significant."""
    return re.sub(r"\s+", " ", text).strip()


def validate_source_evidence(source: OpportunitySource) -> OpportunitySource:
    """Reject stated claims whose evidence quote is absent from source_text.

    Whitespace differences are tolerated. Case, punctuation, and wording remain
    significant. This proves literal presence only, not semantic support.
    The validated source is returned unchanged.
    """
    normalized_source = _normalize_whitespace(source.source_text)
    invalid_fields = []

    for field_name in source.fields.model_fields:
        claim = getattr(source.fields, field_name)
        if claim.value is None:
            continue
        if claim.evidence is None:
            # Defensive guard: the schema should already reject this state.
            invalid_fields.append(field_name)
            continue
        quote = _normalize_whitespace(claim.evidence.quote)
        if not quote or quote not in normalized_source:
            invalid_fields.append(field_name)

    if invalid_fields:
        fields = ", ".join(invalid_fields)
        raise EvidenceValidationError(
            f"Evidence quote was not found in source text for: {fields}."
        )

    return source
