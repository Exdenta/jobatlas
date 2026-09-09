# LinkedIn listing amendment draft

- Target: `job-atlas/linkedin-enrich-translate-normalize-scraper`
- Actor ID: `KMflYVTHiIAXE6nKN`
- Website guide: `https://jobatlas.dev/actors/linkedin`
- Observed: 2026-09-09
- Status: approval-gated local draft

## Listing fields

Store title — keep unchanged:

```text
LinkedIn Jobs Scraper | AI Enrichment
```

SEO title — keep unchanged:

```text
LinkedIn Jobs Scraper | AI Enrichment
```

Regular description — keep unchanged:

```text
Get up to 1,000 LinkedIn jobs per run with full descriptions and original links. Skip repeat jobs for alerts, job boards, and spreadsheets. Add AI enrichment and English translation when needed.
```

SEO description — replace with:

```text
Get up to 1,000 LinkedIn jobs per run for alerts, job boards, and spreadsheets. Keep source links, skip duplicates, and add optional AI enrichment.
```

## Exact README changes

Apply these edits to the current public README and leave all other wording unchanged.

1. Replace every `https://github.com/Exdenta/nomad-agent-job-scrapers` prefix with `https://github.com/Exdenta/jobatlas`.
2. Replace every `https://nomadagent.dev` prefix with `https://jobatlas.dev`.
3. Replace this capability bullet:

```text
- **Ready to connect:** export results or use the API, n8n, Make, Airtable, and MCP.
```

with:

```text
- **Connection paths:** maintained API, MCP, n8n, Make, Python, and Agent Skill assets are available. Airtable is a destination projection only; no Zapier workflow is claimed.
```

4. Replace this paragraph:

```text
[Integration guides and templates](https://github.com/Exdenta/nomad-agent-job-scrapers)
cover MCP, n8n, Make, Airtable, and agent skills.
```

with:

```text
[Integration guides](https://github.com/Exdenta/jobatlas/blob/main/docs/linkedin.md) cover the maintained API, MCP, n8n, Make, Python, and Agent Skill paths. Airtable is a post-run destination projection, not a runnable Actor template. No Zapier workflow is claimed. Asset availability does not prove a hosted connection or named-destination write.
```

5. Replace the final footer line with:

```text
[Product guide](https://jobatlas.dev/actors/linkedin) | [Source and client examples](https://github.com/Exdenta/jobatlas)
```

The existing five-result first run, maximum of 1,000 jobs per run, base price of $0.90 per 1,000 returned jobs, `latest` selector warning, and independent-source disclaimer remain unchanged. Recheck the live Pricing tab before publication.
