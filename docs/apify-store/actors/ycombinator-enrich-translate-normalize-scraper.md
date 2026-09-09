# Y Combinator listing amendment draft

- Target: `job-atlas/ycombinator-enrich-translate-normalize-scraper`
- Actor ID: `pF4Lk4ifzb9tZXg7K`
- Website guide: `https://jobatlas.dev/actors/ycombinator`
- Observed: 2026-09-09
- Status: approval-gated local draft

## Listing fields

Store title — keep unchanged:

```text
Y Combinator Jobs Scraper | Pipelines & Alerts
```

SEO title — keep unchanged:

```text
Y Combinator Jobs Scraper for Startup Job Alerts
```

Regular description — replace with:

```text
Get up to 1,000 Y Combinator startup jobs per run for recruiting pipelines, job boards, and recurring alerts. Export complete descriptions, salary ranges, company details, and source links, with optional AI enrichment and cross-run deduplication.
```

SEO description — replace with:

```text
Collect up to 1,000 YC startup jobs per run with descriptions, salary ranges, company details, and source links for pipelines and alerts.
```

## Exact README changes

Apply these edits to the current public README and leave all other wording unchanged.

1. Replace every `https://github.com/Exdenta/nomad-agent-job-scrapers` prefix with `https://github.com/Exdenta/jobatlas`.
2. Replace every `https://nomadagent.dev` prefix with `https://jobatlas.dev`.
3. Replace every `https://raw.githubusercontent.com/Exdenta/nomad-agent-job-scrapers` prefix with `https://raw.githubusercontent.com/Exdenta/jobatlas`.
4. After the paragraph ending “The Actor never starts another paid run automatically,” add:

```text
The maintained Agent Skill is the supported client asset. API and MCP have documented bounded examples only. No n8n, Make, Zapier, Airtable, or Python client is claimed for this Actor. Documentation presence does not prove hosted MCP exposure or a named-destination write.
```

5. Replace the final footer line with:

```text
[Product guide](https://jobatlas.dev/actors/ycombinator) | [Source and client examples](https://github.com/Exdenta/jobatlas)
```

The existing five-result first run, maximum of 1,000 jobs per run, base price of $0.90 per 1,000 returned jobs, optional-feature table, `latest` selector warning, legacy-product distinction, and independent-source disclaimer remain unchanged. Recheck the live Pricing tab before publication.
