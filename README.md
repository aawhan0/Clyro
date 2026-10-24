# Clyro

> **Know before you apply.**

Clyro helps students compare information about an internship, hackathon, or event across two sources. It highlights conflicting and missing details, shows the evidence behind each finding, and suggests what to verify next.

## The problem

Opportunity details are often spread across announcement posts, organizer pages, and other sources. Deadlines, eligibility rules, prizes, and application instructions may be incomplete or inconsistent. A summary can hide those differences instead of helping students spot them.

Clyro focuses on one practical task: **compare two sources about the same opportunity without guessing which source is correct.**

## The MVP

The first version is limited to a single end-to-end workflow:

1. Provide two pieces of source text describing the same opportunity.
2. Extract the same set of structured fields from each source.
3. Validate the extracted data.
4. Compare fields and classify them as matching, conflicting, or missing.
5. Show the evidence supporting each result.
6. Suggest a clear next step for details that need verification.

Fields in scope:

- Application deadline
- Eligibility and requirements
- Stipend or prize
- Location or participation mode
- Application link or method

**Clyro reports what the sources say; it does not automatically decide which conflicting claim is true.** Missing information must remain missing rather than being filled in by the model.

## Example

The following is an illustrative example, not a result from a running application.

| Field | Source A | Source B | Expected finding |
|---|---|---|---|
| Deadline | November 10, 2026 | November 15, 2026 | Conflict |
| Eligibility | Undergraduate students | CS/data-related undergraduate students | Needs review |
| Application method | Online form | Online form | Match |
| Stipend | Not mentioned | Not mentioned | Missing from both sources |

A useful result should show the relevant source text beside each finding and recommend checking the organizer's current application page for the conflicting deadline and eligibility details.

## How it works

```text
Source A + Source B
        ↓
Structured field extraction
        ↓
Schema validation
        ↓
Field-by-field comparison
        ↓
Evidence-backed findings
        ↓
Suggested verification steps
```

AI assists with extracting information from source text. Structured validation and deterministic comparison logic handle the actual field checks. The result should preserve the original claims so a student can inspect why a finding was produced.

## Planned technology

| Component | Planned choice |
|---|---|
| Frontend | React, Vite, Tailwind CSS |
| Backend | Python, FastAPI |
| AI-assisted extraction | Hosted Gemma API |
| Structured validation | Pydantic |
| Tests | Pytest |

These are planned choices, not a claim that the stack or features are already implemented.

## Build order

- [ ] Accept two source-text inputs.
- [ ] Add a clearly labelled fictional demo case.
- [ ] Extract the same fields from both sources.
- [ ] Validate extracted values and represent unknown fields explicitly.
- [ ] Compare fields as match, conflict, partial mismatch, or not found.
- [ ] Display source evidence for every finding.
- [ ] Handle invalid input and extraction/API failures clearly.
- [ ] Test matching, conflicting, missing, and malformed-input cases.
- [ ] Deploy a working end-to-end demo.

URL extraction can be added with graceful failure handling, but pasted text is the fallback so website access problems do not block the core workflow.

## Scope boundaries

The MVP is **not** a job board, recommendation engine, application autofiller, chatbot, browser extension, or opportunity-monitoring service. Accounts, saved listings, marketplace features, and third-party platform integrations are outside the initial build.

Clyro is designed to complement student opportunity platforms, not replace them. No integration or partnership with any external platform is implied.

## Reliability and safety

- A disagreement is a reason to verify, not proof of fraud.
- Missing information is not the same as a conflict.
- Findings should include traceable source evidence.
- Do not invent values when extraction fails.
- Do not expose API keys in frontend code or commit secrets.
- Label fictional demo data clearly.

## Project status

**Early-stage hackathon MVP.** The workflow above describes the intended behavior. Features should be treated as planned until implemented and tested.

## License

No license has been added yet.
