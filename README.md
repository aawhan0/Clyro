# Clyro

> **Know before you apply.**

Clyro is an evidence-backed opportunity verification tool for students. It helps students cross-check internships, hackathons, and events before applying by comparing details across sources and clearly showing what matches, conflicts, or is missing.

## Why Clyro?

Students discover opportunities across student platforms, social posts, and organizer websites. But deadlines, eligibility rules, stipends, locations, and application links can differ between listings. A polished listing alone does not guarantee that every detail is current or consistent.

Clyro makes those differences visible, so students know what to verify before acting.

## The MVP

The first version focuses on one clear workflow: **compare two sources describing the same opportunity.**

- Extract key fields: deadline, eligibility, stipend or prize, location, and application link.
- Compare the extracted details field by field.
- Flag conflicts and missing information.
- Show the evidence and source for each finding.
- Give students a clear next step when a detail needs verification.

**Clyro does not guess which conflicting claim is correct. It shows the evidence and makes uncertainty explicit.**

## Example

A student finds an internship listing on a student platform and opens the organizer's application page.

| Field | Source A | Source B | Clyro result |
|---|---|---|---|
| Deadline | November 10 | November 15 | Conflict detected |
| Eligibility | Final-year students | Not stated | Missing information |
| Application link | Listed | Listed | Compare links |

Clyro should display both claims with their source evidence and mark the deadline for verification instead of silently choosing a date.

## Planned Workflow

```text
Two Opportunity Sources
        ↓
AI-Assisted Field Extraction
        ↓
Structured Validation
        ↓
Deterministic Field Comparison
        ↓
Evidence-Linked Findings
        ↓
Suggested Verification Steps
```

AI helps extract structured details. Validation and comparison logic handle missing fields and mismatches, keeping the final findings inspectable and testable.

## Planned Technology

| Component | Technology |
|---|---|
| Frontend | React, Vite, Tailwind CSS |
| Backend | Python, FastAPI |
| AI extraction | Hosted Gemma API |
| Data validation | Pydantic |
| Testing | Pytest |

The specific hosted Gemma model and provider will be selected during implementation.

## Development Roadmap

- [ ] Build a simple interface to submit two opportunity sources
- [ ] Extract and validate the key opportunity fields
- [ ] Compare deadlines, eligibility, stipends/prizes, location, and application links
- [ ] Display field-level matches, conflicts, and missing information with source evidence
- [ ] Add clear loading, error, and verification-needed states
- [ ] Test matching sources, conflicting fields, missing fields, and extraction failures
- [ ] Deploy a working demo

## Scope

The MVP prioritizes **internships, hackathons, and student events**. Features such as personalized recommendations, saved opportunities, room listings, marketplace functionality, and continuous monitoring are outside the initial scope.

## Security

Keep API credentials on the backend in environment variables or a secret manager. Never expose API keys in frontend code or commit real credentials to Git. Add `.env` to `.gitignore` before storing local secrets.

## Project Status

**Hackathon MVP in development.** The features and technology listed here are planned and should not be considered implemented until they are available in the working application.

## License

No license has been added yet.
