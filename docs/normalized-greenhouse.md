# Greenhouse Jobs | Normalized

Search stored Greenhouse jobs from supported employer boards and return complete original descriptions with normalized fields. This independent Actor is not affiliated with Greenhouse.

This inventory migration is prepared locally; deployment and board activation are pending. Existing hosted behavior is not changed by this README.

## Choose a board

Select `stripe`, `figma`, or both. The Actor reads a shared job inventory; it does not visit Greenhouse, discover employers, enroll boards or fall back to scraping. Every selected board must have ready inventory. An unavailable or stale board makes the request fail instead of silently returning partial board coverage.

```json
{
  "schemaVersion": "nomad-agent-board-inventory-search-v1",
  "boards": ["stripe"],
  "maxItems": 5,
  "postedWithin": "any",
  "dedupe": {"enabled": false, "key": ""},
  "aiEnrichment": {"enabled": false, "accuracy": "silver"},
  "translateToEnglish": false
}
```

The Store example is stateless. For ongoing alerts, enable `dedupe` and optionally supply a stable profile key. Both automatic scopes and explicit keys include the selected board set. Changing board order preserves the scope; selecting a different board set creates a different scope. Identity includes board and native job ID, so identical native IDs on different boards remain distinct.

The previous nested selection remains accepted with `schemaVersion: "nomad-agent-job-search-input-v1"` and `greenhouse: {"schemaVersion": "nomad-greenhouse-search-v1", "boards": ["stripe"]}`. Supply exactly one selection form. Arbitrary board IDs and source URLs are not supported.

## Descriptions, filters and optional processing

Every returned job carries the full original text and HTML. Records without valid complete-description evidence are withheld. `includeRaw` can only be true. Missing source facts remain unknown unless you request enrichment.

Use `keyword` to match the stored title, company or original description. `workArrangements` selects remote, hybrid or onsite jobs. `postedWithin` accepts `any` or a positive duration in hours, days, weeks or 30-day months, up to 36500 days. A missing source date uses the first inventory admission date; later refreshes do not make a posting new.

Advanced `filters` use `nomad-agent-job-filter-v1`. For example:

```json
{
  "schemaVersion": "nomad-agent-job-filter-v1",
  "expression": {
    "field": "data.employment.workArrangements",
    "operator": "overlaps",
    "value": ["remote"]
  }
}
```

AI enrichment and English display translation are independent, owner-funded options, both off by default. Enrichment fills allowed unknown fields and records provenance. Translation changes selected display fields while preserving original descriptions. No buyer API key is required or accepted. `aiEnrichment.accuracy` selects `silver` or `gold`; an explicitly supplied top-level `accuracy` overrides it for compatibility and never enables enrichment by itself.

Without enrichment, filters use source facts. With enrichment, eligible unknown fields can be filled before the final filter. A failed requested enrichment withholds the affected job. Unknown values do not satisfy ordinary filter comparisons.

## Output and limits

The default dataset contains `nomad-agent-job-v1` records with `identity`, `data`, `llm`, `raw` and source-specific `custom` fields. `identity.externalId` has the form `greenhouse:<board>:<nativeId>`. `RUN-SUMMARY` in the default key-value store records the selected board set, inventory counts, delivery counts, filtering and failures; diagnostic rows are not mixed into the dataset.

`maxItems` is at most 200; zero also means 200. Filters, delivery history and incomplete records can reduce the returned count. A valid empty result is distinct from unavailable inventory. Pricing follows the Actor's current Store configuration; these controls do not change published prices.

## Prepared client schemas

The [input schema](../integrations/shared/greenhouse-inventory-input-v1.schema.json), [source extension](../integrations/shared/greenhouse-v1.schema.json), [board run summary](../integrations/shared/inventory-board-run-summary-v1.schema.json) and [bounded input example](../integrations/shared/input-greenhouse-inventory.json) describe this prepared migration. They do not establish that the hosted Actor accepts it yet. After release, callers select `latest` and inspect the immutable build ID and build number returned by the run.
