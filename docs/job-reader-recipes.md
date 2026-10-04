# Simple job reader input recipes

Use these recipes to start a small search across 21 stored-job readers. They complement the [other job Actor examples](job-actor-input-examples.md) and the [simple inventory guide](simple-inventory-sources.md).

[Public repository](https://github.com/Exdenta/jobatlas) | [General agent setup skill](https://github.com/Exdenta/jobatlas/blob/main/.agents/skills/public-apify-actors/SKILL.md)

Copy the JSON beneath your Actor into the Apify input form or save it as `input.json` for the API. These examples were checked offline against the input schema of each `latest` build observed on 4 October 2026. They have not been executed as part of this documentation update.

Each example requests at most one job, accepts any posting age, and turns repeat-delivery suppression off for that search. This can return a posting delivered by a previous run; it does not clear your delivery history. The company careers bundle also limits each source to one candidate. Empty search filters keep the search broad. Result counts depend on usable stored postings, source availability and the run budget; zero results are possible. Diagnostics are not jobs.

## Run a recipe

1. Choose the Actor below and paste its JSON into the input form. Keep the build selector at `latest`.
2. For a small API check, set a 300-second timeout and a $0.10 maximum charge. A budget cap can stop processing before a result is available; the Actor's Pricing tab gives the current charges.
3. Wait for a terminal run status, then inspect its dataset. Record the immutable `buildId` and build number returned by the run alongside its run ID.
4. If the Actor publishes `RUN-SUMMARY`, inspect it with the dataset for failed sources, suppression and partial coverage. A successful exit alone does not establish complete source coverage.

For example, after saving one of the inputs below:

```bash
curl --request POST \
  --url 'https://api.apify.com/v2/acts/nomad-agent~wellfound-scraper/runs?build=latest&timeout=300&maxTotalChargeUsd=0.10' \
  --header "Authorization: Bearer $APIFY_TOKEN" \
  --header 'Content-Type: application/json' \
  --data-binary @input.json
```

Replace `wellfound-scraper` with the chosen slug. The response starts a run; it is not the final dataset. Poll `GET /v2/actor-runs/<runId>` until terminal, then read `GET /v2/datasets/<defaultDatasetId>/items?clean=true` using the dataset ID from that run. Keep the token in the authorization header.

## Filters and repeated searches

These readers expose `queries`, `locations`, `locationTypes` and `employmentTypes`. Leave these arrays empty to avoid narrowing the recipe; add values from the Actor's current form or schema when you need them. Queries match any query whose words all occur in the posting title or description. Filters apply before the result limit. A restrictive query may match no usable stored postings.

For ongoing incremental delivery, change `dedupe.enabled` to `true`. Leave `dedupe.key` empty for automatic search scoping. If you supply a nonempty key, use a different key for each distinct search: a manual key controls the delivery scope, and changing your search filters with the same key can suppress previously delivered results.

## Actor recipes

The build numbers below identify the schemas inspected for this guide. Select `latest` when running; do not pin these historical numbers in production integrations.

### wellfound-scraper

[Open Actor](https://apify.com/nomad-agent/wellfound-scraper)

Input schema observed on build 0.1.37 (`djcPb2HhKvmQznq3B`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### linkedin-full-info-scraper

[Open Actor](https://apify.com/nomad-agent/linkedin-full-info-scraper)

Input schema observed on build 0.1.12 (`qzys8WLfZUBmHJFi5`). This legacy Actor is deprecated; its public status is unchanged.

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### company-careers-bundle

[Open Actor](https://apify.com/nomad-agent/company-careers-bundle)

Input schema observed on build 0.1.35 (`TuMvyZGWK9PTnrR7L`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "maxItemsPerSource": 1,
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### workable-jobs-scraper

[Open Actor](https://apify.com/nomad-agent/workable-jobs-scraper)

Input schema observed on build 0.1.30 (`NFywiOINtDydiOQuz`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### ashby-jobs-scraper

[Open Actor](https://apify.com/nomad-agent/ashby-jobs-scraper)

Input schema observed on build 0.1.29 (`COFaCN7xJDA6yXe3c`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### lever-jobs-scraper

[Open Actor](https://apify.com/nomad-agent/lever-jobs-scraper)

Input schema observed on build 0.1.30 (`HqrAtqwbfMgN9Jgvm`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### greenhouse-jobs-scraper

[Open Actor](https://apify.com/nomad-agent/greenhouse-jobs-scraper)

Input schema observed on build 0.1.29 (`3HUWLVcHOviUqU7N2`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### wttj-scraper

[Open Actor](https://apify.com/nomad-agent/wttj-scraper)

Input schema observed on build 0.1.34 (`MPr0peBsDLFht6faI`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### ub-doctoral-scraper

[Open Actor](https://apify.com/nomad-agent/ub-doctoral-scraper)

Input schema observed on build 0.1.48 (`utjDqeLssLK3zq2ga`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### nofluffjobs-scraper

[Open Actor](https://apify.com/nomad-agent/nofluffjobs-scraper)

Input schema observed on build 0.1.39 (`u4F8NeYNVzxEsRRFf`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### justjoinit-scraper

[Open Actor](https://apify.com/nomad-agent/justjoinit-scraper)

Input schema observed on build 0.1.38 (`Mya2oy9krAdZyUAvp`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### jobs-ac-uk-scraper

[Open Actor](https://apify.com/nomad-agent/jobs-ac-uk-scraper)

Input schema observed on build 0.1.42 (`Hsl2arv9l4O1C5lxI`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### infojobs-scraper

[Open Actor](https://apify.com/nomad-agent/infojobs-scraper)

Input schema observed on build 0.1.43 (`r4P8EsKbm1yuZ4dLe`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### hackernews-scraper

[Open Actor](https://apify.com/nomad-agent/hackernews-scraper)

Input schema observed on build 0.1.43 (`g7qQKDBuEdNfCVGMo`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### eures-scraper

[Open Actor](https://apify.com/nomad-agent/eures-scraper)

Input schema observed on build 0.1.43 (`n2AeQYl1tY9eyGxk4`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### builtin-scraper

[Open Actor](https://apify.com/nomad-agent/builtin-scraper)

Input schema observed on build 0.1.44 (`fJ1a0vk4FnMoLHVmk`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### ai-jobs-net-scraper

[Open Actor](https://apify.com/nomad-agent/ai-jobs-net-scraper)

Input schema observed on build 0.1.42 (`d6nVZnTuTvULjSjvp`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### ycombinator-was-scraper

[Open Actor](https://apify.com/nomad-agent/ycombinator-was-scraper)

Input schema observed on build 0.1.41 (`SoREk9WVQbdqsxZ1K`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### linkedin-scraper

[Open Actor](https://apify.com/nomad-agent/linkedin-scraper)

Input schema observed on build 0.1.36 (`a4m7ec7WMn5WAYQfr`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### euraxess-scraper

[Open Actor](https://apify.com/nomad-agent/euraxess-scraper)

Input schema observed on build 0.1.37 (`ToHKHwLdHqVqf9iqW`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

### foorilla-ai-jobs-scraper

[Open Actor](https://apify.com/nomad-agent/foorilla-ai-jobs-scraper)

Input schema observed on build 0.1.10 (`cE0nUfrUiBoxiGnYH`).

```json
{
  "maxItems": 1,
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "dedupe": {
    "enabled": false,
    "key": ""
  },
  "postedWithin": "any"
}
```

