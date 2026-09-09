# EURAXESS listing amendment draft

- Target: `job-atlas/euraxess-enrich-translate-normalize-scraper`
- Actor ID: `Slu3SAWULLRYnCN9Y`
- Website guide: `https://jobatlas.dev/actors/euraxess`
- Observed: 2026-09-09
- Status: approval-gated local draft

## Listing fields

Store and SEO title — keep unchanged:

```text
EURAXESS Jobs Scraper | Full Details & AI Enrichment
```

Regular description — keep unchanged:

```text
From $0.90 per 1,000 research jobs. Search EURAXESS PhD, postdoc and faculty vacancies with deadlines, funding and application links. Export structured data, avoid repeat alerts, and optionally add AI enrichment or English translation.
```

SEO description — replace with:

```text
Collect up to 200 EURAXESS research jobs per run with deadlines, funding, and source links. Base results start at $0.90 per 1,000.
```

## Exact README changes

Apply these edits to the current public README and leave all other wording unchanged.

1. Replace every `https://github.com/Exdenta/nomad-agent-job-scrapers` prefix with `https://github.com/Exdenta/jobatlas`.
2. Replace every `https://nomadagent.dev` prefix with `https://jobatlas.dev`.
3. Replace every `https://raw.githubusercontent.com/Exdenta/nomad-agent-job-scrapers` prefix with `https://raw.githubusercontent.com/Exdenta/jobatlas`.
4. Replace:

```text
It uses the same output format as the normalized Nomad Agent LinkedIn Actor.
```

with:

```text
It uses the same canonical job contract as the normalized Job Atlas LinkedIn and Y Combinator Actors.
```

5. Add this paragraph at the end of “For API users and AI agents”:

```text
Maintained paths are API, MCP, n8n, Make, Python, and the Agent Skill. Airtable is a post-run destination projection only. No Zapier workflow is claimed. Asset availability does not prove a hosted connection or named-destination write.
```

6. Replace the final footer line with:

```text
[Product guide](https://jobatlas.dev/actors/euraxess) | [Source and client examples](https://github.com/Exdenta/jobatlas)
```

The existing five-result first run, maximum of 200 jobs per run, base price of $0.90 per 1,000 returned jobs, optional-feature table, `latest` selector warning, and independent-source disclaimer remain unchanged. Recheck the live Pricing tab before publication.
