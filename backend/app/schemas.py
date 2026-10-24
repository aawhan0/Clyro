"""Validated data contracts for Clyro's source-text comparison MVP.

This module validates structure only. It does not determine whether a claim
is true or whether its evidence quote semantically supports the claim.
"""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator


NonEmptyText = Annotated[str, Field(min_length=1)]


class StrictModel(BaseModel):
    """Reject unexpected fields instead of silently accepting bad payloads."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ClaimEvidence(StrictModel):
    """A verbatim excerpt that can later be checked against source_text."""

    quote: NonEmptyText


class FieldClaim(StrictModel):
    """One source's claim for a single opportunity field.

    A null value explicitly means the source does not state this field.
    Non-null claims must include a candidate evidence excerpt.
    """

    value: NonEmptyText | None = None
    evidence: ClaimEvidence | None = None

    @model_validator(mode="after")
    def require_evidence_for_claim(self) -> "FieldClaim":
        if self.value is not None and self.evidence is None:
            raise ValueError("A stated claim must include supporting evidence")
        if self.value is None and self.evidence is not None:
            raise ValueError("An unknown claim must not include evidence")
        return self


class OpportunityFields(StrictModel):
    """The fixed set of fields Clyro compares between two sources."""

    application_deadline: FieldClaim
    eligibility_requirements: FieldClaim
    stipend_or_prize: FieldClaim
    location_or_participation_mode: FieldClaim
    application_method: FieldClaim


class OpportunitySource(StrictModel):
    """A single source description and its structured, evidence-linked claims."""

    source_text: NonEmptyText
    fields: OpportunityFields
