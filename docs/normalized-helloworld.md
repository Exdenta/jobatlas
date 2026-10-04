# HelloWorld.rs Jobs | Normalized

Search HelloWorld.rs jobs with complete original descriptions and advanced filters. Optional owner-funded AI enrichment and English display translation are independent options, both off by default. This independent Actor is not affiliated with HelloWorld.rs.

Results include complete original descriptions. Incomplete records are withheld, and unavailable or stale source data is reported as a failure. Coverage can be smaller than the website listing.

## Actor endpoints

- [Original publisher](https://apify.com/nomad-agent/normalized-helloworld-jobs-scraper)
- [Job Atlas Actor](https://apify.com/jobatlas/normalized-helloworld-jobs-scraper)

Use the original publisher for the example below. Independently released copies can be found in the Job Atlas directory. Select `latest` and record each run's returned immutable `buildId` and build number; each copy has its own builds and execution evidence. The release evidence below applies to the original publisher.

## First run

```json
{
  "schemaVersion": "nomad-agent-inventory-search-v1",
  "maxItems": 3,
  "postedWithin": "any",
  "keyword": "",
  "aiEnrichment": {"enabled": false, "accuracy": "silver"},
  "translateToEnglish": false,
  "dedupe": {"enabled": false, "key": ""}
}
```

Platform charges can apply. `maxItems` caps output at 200; zero means 200. Filtering and repeat suppression can produce fewer or no results. A keyword matches the title, employer, and original description as a case-insensitive phrase. `postedWithin` accepts `any` or a positive duration such as `7d`, up to 36500 days. Where the source supplies no reliable date, the posting date is the first observation; refreshes do not reset it.

`workArrangements` accepts `remote`, `hybrid`, and `onsite`. For other normalized fields, pass a versioned expression under `filters`, for example:

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

Use compatible currency and compensation-period filters when comparing pay. With AI off, unknown source values do not satisfy ordinary comparisons. With AI on, known mismatches are filtered before enrichment and unknown enrichable values are checked afterwards. Filtering happens before English display translation.

## Output and repeat delivery

Rows use `nomad-agent-job-v1`: `schemaVersion`, `identity`, `data`, `llm`, `raw`, and `custom`. Missing facts are `null`; known empty collections are `[]`. `raw.description` and `raw.descriptionHtml` preserve source content. The stable posting key is `(identity.source, identity.externalId)`; HelloWorld IDs are numeric strings. Older prefixed IDs such as `helloworld:738769` may require comparison-key migration and permit a one-time repeat.

Inspect the dataset alongside the default key-value store's `RUN-SUMMARY`. It reports candidates, emitted rows, repeat suppression, freshness and terminal status. A partial summary may mean the bounded scan reached its limit. Diagnostics do not count as jobs.

Repeat suppression is enabled by default and scoped to the Apify user, Actor and search. The example disables it for a stateless inspection. Leave `dedupe.key` empty to derive scope from the search; set a stable key deliberately for recurring alerts. A successful run with zero rows can be valid when every candidate has already been delivered.

## Optional processing and setup

AI fills supported unknown facts without overwriting known source facts; failed requested enrichment is withheld. Translation changes selected display text while preserving original descriptions. No customer API key is required. `accuracy` accepts `silver` or `gold`; top-level `accuracy` remains a compatibility override and does not enable AI by itself. With enrichment off, `llm.status` is `not_requested`.

Legacy source-fetch inputs using `helloworld.startUrls` need migration to `keyword` or normalized filters. Original descriptions remain included.

Use the [generic setup skill](../.agents/skills/public-apify-actors/SKILL.md) and [complete setup guide](public-actors-setup.md) to configure a client from the current published input schema. Source-specific facts follow the [HelloWorld custom facts schema](../integrations/shared/helloworld-v1.schema.json). Dataset views provide readable columns; input filters determine which jobs are retrieved.

## Verification scope

On 3 October 2026, the original publisher's promoted `latest` and default selector resolved to build `1.0.7` (`Ws7hvUNffXDWDDzxn`). A controlled stateless default-selector run (`GRFbXo3jcdeQ78GK0`) returned three source jobs with original descriptions; its summary was partial because the three-item scan limit was reached. An untouched default-input test (`MPcJhwFz48tggf8sU`) returned zero rows with 100 candidates suppressed as already delivered and no reported error. These checks establish bounded functional output and repeat suppression. They do not establish complete source coverage, normal customer execution, enabled AI or translation, destination integration, or the Job Atlas endpoint's release status.
