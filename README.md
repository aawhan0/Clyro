# Clyro

> **Know before you apply.**

Clyro helps students verify opportunities by detecting conflicting information across sources and providing evidence-backed insights.

## The Problem

Opportunity details are often scattered across posts, webpages, PDFs, and screenshots. Deadlines, eligibility criteria, and requirements can be missing or contradictory, making it difficult for students to know what to trust.

## The Solution

Clyro is being built to turn opportunity information into a structured, evidence-backed view. The initial MVP focuses on comparing two sources about the same opportunity to:

- Extract key details such as deadlines, eligibility, and requirements.
- Detect conflicting claims and missing information.
- Show the source evidence behind each finding.
- Highlight what students should verify before applying.

**Core principle:** when sources disagree, Clyro should show the disagreement rather than guess which source is correct.

## Example

- **Source A:** Applications close on November 10.
- **Source B:** Applications close on November 15.

Clyro should flag the deadline as **Needs verification** and show both sources, rather than silently choosing one date.

## Planned Workflow

```text
Opportunity Sources
       ↓
AI-Powered Information Extraction
       ↓
Structured Data Validation
       ↓
Source Comparison
       ↓
Evidence-Backed Findings
       ↓
Actionable Next Steps
```

AI extraction is intended to identify relevant details; deterministic comparison logic will check for mismatches and missing fields.

## Planned Technology

| Component | Technology |
|---|---|
| Frontend | React, Vite, Tailwind CSS |
| Backend | Python, FastAPI |
| AI extraction | Hosted Gemma API |
| Data validation | Pydantic |
| Testing | Pytest |

The specific hosted Gemma model and provider will be confirmed during implementation.

## Development Status

**Hackathon MVP in development.** The features and stack above describe the current plan, not necessarily implemented functionality.

- [ ] Set up the frontend and backend
- [ ] Extract and validate opportunity details
- [ ] Compare two sources
- [ ] Display evidence, conflicts, and missing fields
- [ ] Add tests for matching, conflicting, and incomplete information
- [ ] Deploy a working demo

## Security

Keep API credentials on the backend in environment variables or a secret manager. Never expose API keys in frontend code or commit real credentials to Git. Add `.env` to `.gitignore` before storing local secrets.

## License

No license has been added yet.
