# Greenhouse Jobs | Normalized

Search Greenhouse jobs with complete original descriptions, normalized fields and advanced filters. The current supported employers are Stripe and Figma. This independent Actor is not affiliated with Greenhouse.

The Nomad Agent endpoint is public; its default build and published input were checked on 4 October 2026. No public Job Atlas endpoint was verified. This documentation check did not execute the Actor.

## First run

Use [nomad-agent/normalized-greenhouse-jobs-scraper](https://apify.com/nomad-agent/normalized-greenhouse-jobs-scraper), select `latest`, and check the current Input and Pricing tabs.

```json
{
  "schemaVersion": "nomad-agent-inventory-search-v1",
  "maxItems": 5,
  "postedWithin": "any",
  "keyword": "",
  "dedupe": {"enabled": false, "key": ""},
  "aiEnrichment": {"enabled": false, "accuracy": "silver"},
  "translateToEnglish": false
}
```

The current input does not accept `boards`, `greenhouse.boards`, arbitrary employer IDs or source URLs. Use `keyword` or the supported normalized `filters`; naming an employer does not expand the supported coverage. The earlier board-selection example is not the current hosted input.

`maxItems` is capped at 200; zero also means 200. Filters, incomplete records and repeat suppression can reduce output or return no jobs. `postedWithin` accepts `any` or a positive duration, up to 36500 days. When the source supplies no reliable posting date, first observation is used and later observations do not reset it.

## Filters and processing

`keyword` matches title, employer and description. `workArrangements` accepts `remote`, `hybrid` and `onsite`. Advanced filters use `nomad-agent-job-filter-v1` under the input's `filters` field. Unknown values do not satisfy ordinary comparisons; a city alone does not establish onsite work.

AI enrichment and English translation are independent, owner-funded options, both off by default. Enrichment fills supported missing facts and records provenance. Translation changes selected display fields while preserving original descriptions. No customer model key is required. `accuracy` is a compatibility override for `aiEnrichment.accuracy` and never enables AI by itself.

## Output and repeats

Rows use `nomad-agent-job-v1` with the six roots `schemaVersion`, `identity`, `data`, `llm`, `raw` and `custom`. Original descriptions remain in `raw`. Unknown facts are `null`; empty collections follow the documented field semantics. Preserve source identity when exporting to a table.

Inspect the dataset and `RUN-SUMMARY` for delivered counts, repeat suppression, source limitations and terminal status. Record the immutable build ID and build number returned by each run. Source availability, optional processing and destination delivery need their own validation.

The [board-selection schema](../integrations/shared/greenhouse-inventory-input-v1.schema.json) and [its example](../integrations/shared/input-greenhouse-inventory.json) are local proposal artifacts, not the current published input. The [source extension](../integrations/shared/greenhouse-v1.schema.json) is a separate output contract. See the [public directory](public-actors.md) and [setup guide](public-actors-setup.md) for current endpoints and bounded run checks.
