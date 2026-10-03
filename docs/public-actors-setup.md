# Public Actor setup and examples

Public Nomad Agent and Job Atlas Actors publish their input schemas and examples on their Apify pages. Choose the Actor for your source and output tier before building an input. This guide provides a small first run; the selected Actor's current schema remains authoritative.

## Install the setup skill

```bash
python scripts/install_skill.py --skill public-apify-actors --client both --target /path/to/your/project
```

The skill checks the current input, keeps credentials outside exports, records the immutable build returned by the run, and inspects actual output. Source-specific LinkedIn, EURAXESS, YC and AI scorer skills remain available through the same installer.

## Simple job readers

Simple readers return source-supplied job facts, including the original description. They do not perform AI enrichment or translation. Readers published on the row-v3 contract return 15 fields, including `employmentTypes` and `hiringContacts`; they omit `recordType`. Some existing paid integrations retain older contracts, so check `schemaVersion` and the Actor schema.

Current simple search-v2 inputs support `queries`, `locations`, `locationTypes`, and `employmentTypes`. Inventory search applies these filters before the result limit. Bundles also support `maxItemsPerSource`. Exact supported values and defaults are declared by each Actor.

First run for `nomad-agent/wttj-scraper`:

```json
{
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "maxItems": 3,
  "postedWithin": "any",
  "queries": [],
  "locations": [],
  "locationTypes": [],
  "employmentTypes": [],
  "dedupe": {"enabled": false, "key": ""}
}
```

For a narrower search, set a query such as `software engineer` and a location such as `France`. Narrower filters can legitimately return zero matches. Disable repeat suppression only when you want a stateless search; keep the normal default when requesting new postings over time.

## Run through the API

Keep `APIFY_TOKEN` in your shell environment. Save the input above as `input.json`, then submit one bounded run:

```bash
curl --fail-with-body --request POST \
  --header "Authorization: Bearer ${APIFY_TOKEN}" \
  --header "Content-Type: application/json" \
  --data-binary @input.json \
  'https://api.apify.com/v2/acts/nomad-agent~wttj-scraper/runs?build=latest&timeout=300&maxTotalChargeUsd=0.20'
```

Record the returned run ID and `buildId`. Poll the run to a terminal state with a finite deadline, then read its dataset and `RUN-SUMMARY` record. Do not repeat an uncertain POST blindly: locate the original run in recent history first. Large bundle defaults may need a larger explicit spending cap than this three-row example; the cap is an upper bound, not a quoted price.

## Normalized readers and the scorer

Normalized readers use a nested job contract with source facts and enrichment provenance. AI enrichment and English translation are separate options; enable them deliberately, using the Actor's current schema and published prices. Do not pass simple-reader input unchanged to a normalized Actor. Owner-funded normalized Actors do not require a customer OpenRouter key.

The AI job-fit scorer ranks jobs against a resume. Follow its dedicated skill and input examples: static exclusions, completed AI evaluations and provider failures are distinct outcomes. A successful run status alone does not prove that useful scores were produced.

## Inspect meaningful results

For a job, verify the source identity, title, source URL and complete original description. Preserve the documented schema and distinguish unknown values from known-empty arrays. Review source limitations and errors in `RUN-SUMMARY`; diagnostic or demo rows do not count as source results.

Native empty input can correctly produce zero rows when persistent dedupe has already delivered every candidate. Check the proven-candidate and suppression counts. Required-input Actors may reject empty input, and legal-source demos may need credentials for real results. Do not clear history, weaken filters or create sample jobs to force a result count.

Dataset views expose readable job columns and pagination. Filtering controls and sorting depend on the current Apify interface; the Actor's input filters are the reliable way to select records before a run.
