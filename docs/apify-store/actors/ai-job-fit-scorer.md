# AI Job Fit Scorer listing amendment draft

- Target: `job-atlas/ai-job-fit-scorer`
- Actor ID: `OZ919PaAyAbifOdcL`
- Website guide: `https://jobatlas.dev/actors/ai-job-fit-scorer`
- Observed: 2026-09-09
- Status: approval-gated local draft

## Listing fields

Store title — keep unchanged:

```text
AI Job Search & Fit Scorer — 10 Sources + AI Matching
```

SEO title — keep unchanged:

```text
AI Job Search & Resume Fit Scorer – 10 Sources
```

Regular description — replace with:

```text
Search 10 public developer-job sources or score up to 200 supplied jobs for one candidate. Get a ranked shortlist with fit scores, hard-requirement checks, evidence, gaps, and posting links. Returned shortlist results cost $0.02 each; no model key is needed.
```

SEO description — replace with:

```text
Search 10 developer-job sources or score up to 200 jobs for one candidate. Return evidence-gated fit results at $0.02 per billed retained row.
```

## Exact README changes

Apply these edits to the current public README and leave all other wording unchanged.

1. Replace every `https://github.com/Exdenta/nomad-agent-job-scrapers` prefix with `https://github.com/Exdenta/jobatlas`.
2. Replace every `https://nomadagent.dev` prefix with `https://jobatlas.dev`.
3. After the “Integrations” link list, add:

```text
Maintained paths are API, MCP, n8n, Make, Zapier, Python, and the Agent Skill. No Airtable asset is claimed. An Actor run proves neither hosted client exposure nor a named-destination write; verify those layers separately.
```

4. Replace the final footer line with:

```text
[Product guide](https://jobatlas.dev/actors/ai-job-fit-scorer) | [Source and client examples](https://github.com/Exdenta/jobatlas)
```

The existing one-candidate rule, maximum of 200 unique jobs per run, $0.02 shortlist/audit billing distinction, five-result first run, ten-source capability wording, `latest` selector warning, privacy boundary, and independent-source disclaimer remain unchanged. Ten-source capability is not a claim that every source succeeded in the current run. Recheck the live Pricing tab before publication.
