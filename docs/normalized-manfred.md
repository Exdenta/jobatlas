# Manfred Jobs | Normalized

Search stored Manfred jobs with complete original descriptions, optional owner-funded AI enrichment, optional English display text, and advanced filters. Both processing options default to off. This independent Actor is not affiliated with Manfred.

## How it works

Background collection reads public source data and stores reliably parsed facts and complete descriptions. This public Actor queries that shared inventory. It never searches or requests the Manfred website during your run.

A job is available only when the collector has verified its full description. Snippets, truncated bodies, and unverified historical records are withheld. If the inventory is unavailable or stale, the run fails instead of falling back to website scraping. Coverage can therefore be smaller than the current website listing.

When enabled, AI enrichment fills supported unknown fields and records provenance in `llm`. It cannot overwrite known source facts. Jobs whose requested enrichment fails are withheld. When translation is enabled, selected human-readable fields are translated into English, while `raw.description` and `raw.descriptionHtml` preserve the original source content. Manfred's complete text can be available without source HTML; in that case `raw.descriptionHtml` is `null`.

## Actor endpoints

- [Job Atlas](https://apify.com/jobatlas/normalized-manfred-jobs-scraper)
- [Original publisher](https://apify.com/nomad-agent/normalized-manfred-jobs-scraper)

Use the Apify API or SDK with `jobatlas/normalized-manfred-jobs-scraper` and the `latest` build selector. Record the immutable `buildId` returned by each run. The example below limits output to five jobs; platform charges can still apply.

## First run

```json
{
  "schemaVersion": "nomad-agent-inventory-search-v1",
  "maxItems": 5,
  "postedWithin": "any",
  "keyword": "",
  "aiEnrichment": {"enabled": false, "accuracy": "silver"},
  "translateToEnglish": false,
  "dedupe": {"enabled": false, "key": ""}
}
```

`maxItems` is an upper bound of 200; zero also means 200. Filtering, repeat suppression, and failed enrichment can produce fewer results. A keyword is a case-insensitive phrase matched against the stored title, employer, and complete original description. It is never sent to the source website.

`postedWithin` accepts `any` or a positive duration such as `7d`. When Manfred has no reliable original posting date, the stored date is the job's first admission to the inventory. Later refreshes do not make the posting appear new.

## Advanced filters

`workArrangements` accepts `remote`, `hybrid`, and `onsite`. For other normalized fields, use the shared `nomad-agent-job-filter-v1` expression contract:

```json
{
  "schemaVersion": "nomad-agent-job-filter-v1",
  "expression": {
    "field": "data.compensation.minimum",
    "operator": "gte",
    "value": 50000
  }
}
```

Place that object under the input's `filters` field. With AI off, filters match stored source facts and unknown values do not satisfy ordinary comparisons. With AI on, known source mismatches are removed before AI calls; unknown enrichable values are checked again after enrichment. Filters operate on normalized values before English display translation. Compare compensation only with the appropriate currency and period filters.

## Output and repeat delivery

Every dataset item follows `nomad-agent-job-v1`, with six roots: `schemaVersion`, `identity`, `data`, `llm`, `raw`, and `custom`. Missing facts remain `null`; a known empty collection is `[]`. Original identity and complete description evidence remain stable across enrichment and translation. The rich format is intended for v3 scoring and advanced filtering.

The default key-value store contains `RUN-SUMMARY`, including inventory freshness, candidates, withheld enrichment failures, delivery counts, and terminal status. `OWNER-USAGE` separates actual provider costs from unpriced token counts when enrichment runs. Diagnostic receipts are not inserted into the jobs dataset.

Repeat suppression is enabled by default. It uses a persistent ledger scoped to the Apify user, Actor, and search. Set `dedupe.enabled` to `false` for a stateless run. A nonempty `dedupe.key` deliberately shares delivery history within that user's scope. Ambiguous delivery or ledger failures fail the run rather than claiming successful delivery.

## Owner-funded processing

AI enrichment and translation are independent options, both off by default. Set `aiEnrichment.enabled` to `true` for extraction and `translateToEnglish` to `true` for translation. AI accuracy accepts `silver` or `gold`. With AI off, `llm.status` is `not_requested`; enabling translation alone does not change that status. You do not supply API keys. Only enabled stages send text to the relevant provider: OpenRouter for extraction and DeepL for selected English display fields. The configured routes deny provider data collection but do not guarantee zero retention or EU-only processing. Sanitized extracted facts and translations may be cached by the owner.

The existing Apify pricing configuration is preserved by this migration. This Actor is currently unmonetized; platform compute or storage charges can still apply. No new per-result, enrichment, or translation price is introduced.

The previous `nomad-agent-job-search-input-v1` keyword block remains accepted for compatibility. The old top-level `accuracy` field overrides nested accuracy when explicitly supplied, but does not enable AI. `includeRaw` must be true, and source-native country or sort requests must move to inventory filters.

## Verification scope

On 21 September 2026, the primary and Job Atlas default selectors completed bounded owner functional tests. Tests on each account covered explicit opt-in and omitted options. Complete original descriptions, rich schema, completed enrichment and English display fields with opt-in, and `llm.not_requested` with no owner usage record by default were inspected. Both default-off tests also exercised persistent deduplication. This does not claim a normal customer run or an integration test against an external destination.
