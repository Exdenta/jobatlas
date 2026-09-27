# Impactpool Jobs - Simple

Read jobs from the stored Impactpool inventory with complete original descriptions. Each job includes title, employer, source URL, locations, posting date, application deadline when available, original text and HTML, and source-published work arrangement and salary. Unknown optional facts are null; unavailable locations are an empty array.

This Actor returns the flat `nomad-agent-job-row-v2` contract. It has no AI enrichment, translation, custom fields, or source-site requests. Jobs without collector evidence of a complete description are withheld. Diagnostics are in `RUN-SUMMARY`, outside the job dataset.

## Input

```json
{"schemaVersion":"nomad-agent-simple-inventory-search-v1","maxItems":40,"postedWithin":"any","dedupe":{"enabled":true,"key":""}}
```

`postedWithin` is the only job filter: use a positive number of hours (`h`), days (`d`), weeks (`w`), or 30-day months (`m`), up to 36500 days. `any` disables it. Impactpool publishes no posting date on the supported pages, so the stored date is the first inventory admission date; refreshes do not reset it. `maxItems` is bounded to 200 and zero means 200. Dedupe suppresses confirmed previous deliveries for the same user and search.

The existing startup charge and per-result prices are unchanged. Full descriptions are included in each result. An unavailable or stale inventory fails the run; there is no website fallback.

## Migration

The versioned simple input replaces source search controls and `includeDetails`. Full descriptions are always required. The v2 row removes `custom`, `warnings`, and `docs` from posting output and adds the optional source salary field. Existing v1 scoring can use description, title, company, locations, salary, and stable source/ID/URL fields.

## Endpoint and verification

Use [Impactpool Jobs - Simple](https://apify.com/nomad-agent/impactpool-scraper) with `latest`. Simple Actors are not mirrored to Job Atlas. On 21 September 2026, an owner test through the default selector returned a complete simple-v2 record with the existing startup and result charges. A repeat suppressed the duplicate and charged no result fee. This does not claim normal buyer or scheduled consumer execution.
