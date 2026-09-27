# Poslovi Infostud Jobs | Normalized

Search stored Poslovi Infostud jobs with complete original descriptions, optional owner-funded AI enrichment, optional English display text, and advanced filters. This independent Actor is not affiliated with Poslovi Infostud.

## How it works

Background collection reads public source data and stores reliably parsed facts and complete descriptions. This public Actor queries that shared inventory. It never searches or requests the Poslovi Infostud website during your run.

A job is available only when the collector has verified its full description. Snippets, truncated bodies, and unverified historical records are withheld. If the inventory is unavailable or stale, the run fails instead of falling back to website scraping. Coverage can therefore be smaller than the current website listing.

When requested, AI enrichment fills supported unknown fields and records provenance in `llm`. It cannot overwrite known source facts. Jobs whose requested enrichment fails are withheld. Optional translation converts selected human-readable fields into English, while `raw.description` and `raw.descriptionHtml` preserve the original source content. Without enrichment, `llm.status` is `not_requested`. Visible description markup is preserved in `raw.descriptionHtml`; hidden tracking text and reference markers are removed by the collector. Image-only adverts without a complete readable description are withheld.

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

`postedWithin` accepts `any` or a positive duration such as `7d`. When Poslovi Infostud has no reliable original posting date, the stored date is the job's first admission to the inventory. Later refreshes do not make the posting appear new.

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

Place that object under the input's `filters` field. With AI disabled, filters evaluate source facts only; unknown values do not satisfy ordinary comparisons. With AI enabled, known source mismatches are removed before AI calls and unknown enrichable values are checked again after enrichment. Filters operate on normalized values before English display translation. Compare compensation only with the appropriate currency and period filters.

## Output and repeat delivery

Every dataset item follows `nomad-agent-job-v1`, with six roots: `schemaVersion`, `identity`, `data`, `llm`, `raw`, and `custom`. Missing facts remain `null`; a known empty collection is `[]`. Original identity and complete description evidence remain stable across enrichment and translation. The rich format is intended for v3 scoring and advanced filtering.

The default key-value store contains `RUN-SUMMARY`, including inventory freshness, candidates, withheld enrichment failures, delivery counts, and terminal status. `OWNER-USAGE` separates actual provider costs from unpriced token counts when enrichment runs. Diagnostic receipts are not inserted into the jobs dataset.

Repeat suppression is enabled by default. It uses a persistent ledger scoped to the Apify user, Actor, and search. Set `dedupe.enabled` to `false` for a stateless run. A nonempty `dedupe.key` deliberately shares delivery history within that user's scope. Ambiguous delivery or ledger failures fail the run rather than claiming successful delivery.

## Owner-funded processing

AI enrichment and translation are independent opt-ins, both off by default. Enable `aiEnrichment.enabled` for extraction and `translateToEnglish` for English display text. You do not supply API keys. Only when enabled, the owner sends description text to OpenRouter for extraction or selected display text to DeepL for translation. The configured routes deny provider data collection but do not guarantee zero retention or EU-only processing. Sanitized extracted facts and translations may be cached by the owner. V3 callers can explicitly request the processing they need.

The existing Apify pricing configuration is preserved by this migration. This Actor is unmonetized; platform compute or storage charges can still apply. No new per-result, enrichment, or translation price is introduced.

Use `nomad-agent-inventory-search-v1` for this database-only release. The previous source-fetch input required `infostud.startUrls`; those source URLs are not accepted by the inventory search and are never silently discarded. Migrate the request to `keyword` or supported normalized `filters`. Original descriptions are always included.

The top-level `accuracy` field remains a compatibility override for `aiEnrichment.accuracy`; it never enables enrichment by itself.

Relative posting-age windows are limited to 36500 days. Use `any` for an unrestricted search. AI enrichment and translation remain independent opt-ins, both off by default.

Source-specific facts use the [public Infostud schema](https://raw.githubusercontent.com/Exdenta/jobatlas/main/integrations/shared/infostud-v1.schema.json).

## Actor endpoints and verification

Use [Job Atlas](https://apify.com/jobatlas/normalized-infostud-jobs-scraper) or the [original publisher](https://apify.com/nomad-agent/normalized-infostud-jobs-scraper), selecting `latest`. Record the immutable build returned by each run.

On 22 September 2026, bounded owner tests passed on both accounts with processing enabled and with both options omitted. A Serbian posting retained its original title, description and HTML when processing was off; translation-only and AI-only tests also passed on the original publisher. Its repeat test suppressed a proven duplicate without a result charge. These observations do not establish normal buyer traffic or delivery to a destination application.
