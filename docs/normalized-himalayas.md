# Himalayas Jobs | Normalized

Search verified stored Himalayas jobs in the normalized job format, with complete original descriptions and source links. This independent Actor is not affiliated with the source.

[Open the Job Atlas Actor](https://apify.com/jobatlas/normalized-himalayas-jobs-scraper) · [Source Actor](https://apify.com/nomad-agent/normalized-himalayas-jobs-scraper) · [Setup skill](https://github.com/Exdenta/jobatlas/blob/main/.agents/skills/public-apify-actors/SKILL.md)

## Coverage

Search stored jobs with complete original descriptions and advanced filters. Owner-funded AI enrichment and English display translation are independent opt-ins, off by default. No source website is requested.

Coverage reflects verified stored postings. An unavailable source, narrow filters or repeat suppression can reduce the result count. Consult the Actor's current description and input form before reusing saved inputs.

## First search

This explicitly stateless example requests up to three jobs. It is a setup example, not the Actor's default input. Repeat suppression is enabled by default; AI enrichment and English translation are optional and disabled by default.

```json
{
  "schemaVersion": "nomad-agent-inventory-search-v1",
  "maxItems": 3,
  "postedWithin": "any",
  "keyword": "",
  "aiEnrichment": {
    "enabled": false,
    "accuracy": "silver"
  },
  "translateToEnglish": false,
  "dedupe": {
    "enabled": false,
    "key": ""
  }
}
```

Read the current input schema in the linked Actor's Input tab. API clients can fetch `GET /v2/acts/jobatlas~normalized-himalayas-jobs-scraper`, then `GET /v2/actor-builds/<buildId>` using `taggedBuilds.latest.buildId`. Inspect the build's input schema or decoded `.actor/input_schema.json` source file before running. Run with the `latest` selector, then save the immutable build ID returned by the run. Use the Console form for keyword, posting age, work arrangement and supported normalized filters. Advanced expressions use the input's `filters` field; [shared input examples](https://github.com/Exdenta/jobatlas/blob/main/docs/job-actor-input-examples.md) explain the format.

## Read the results

Each job follows `nomad-agent-job-v1`, with `schemaVersion`, `identity`, `data`, `llm`, `raw` and `custom`. `raw.description` and `raw.descriptionHtml` preserve the source text. Unknown facts remain `null`; a known empty collection is `[]`.

Read `RUN-SUMMARY` in the run's default key-value store alongside the dataset. Its counts distinguish returned jobs, withheld records and repeat suppression. Zero rows can be a valid result; do not clear delivery history or substitute diagnostic records for jobs. When optional processing runs, inspect its provenance and `OWNER-USAGE` where available.

For recurring alerts, enable `dedupe` and leave its `key` empty to derive history from the search. A nonempty key deliberately shares an alert history, so use a separate key when searches should remain independent. Platform charges still apply; check the Actor's current Pricing tab before running it.
