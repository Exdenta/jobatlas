# Job Actor input examples

Small, copyable inputs for 26 public job Actors, checked against their published input schemas on October 4, 2026. Each example limits requested output to five jobs. Schema validation confirms the input shape; it does not establish a successful run or guarantee matching jobs.

[Public repository](https://github.com/Exdenta/jobatlas) · [Agent setup skill](https://github.com/Exdenta/jobatlas/blob/main/.agents/skills/public-apify-actors/SKILL.md) · [Complete setup guide](https://github.com/Exdenta/jobatlas/blob/main/docs/public-actors-setup.md)

## Start in Apify Console

Open an Actor below, choose its input Form or JSON tab, and paste the matching example. Form controls describe the filters supported by that Actor. The JSON examples work in the API too. Keep the production build selector at `latest`; record the immutable `buildId` returned by each run.

Set Maximum cost per run before starting a paid run. A $0.20 cap and a 300-second timeout are suggested limits for an initial check, not promises that every source scan or enrichment will finish within them. Read the Actor Pricing tab first. `maxItems` limits returned jobs; it does not necessarily limit source scanning, AI work, or total cost.

The examples keep repeat-delivery suppression enabled where supported, with an empty key so the Actor derives the scope from the search. If you supply a nonempty key, choose one unique stable key per alert or search; do not share it across different searches. Repeated searches can correctly return zero already-delivered jobs. Empty inventory, restrictive filters, deadlines, and unavailable sources can also yield no jobs; do not treat a diagnostic row as a posting.

## Inputs by Actor

Simple readers return original source facts and descriptions. Normalized readers return structured job facts; the examples explicitly leave optional AI enrichment and translation off. Fields differ across Actors, so use the example under the exact Actor name.

### nomad-agent/devex-scraper

[Open Actor](https://apify.com/nomad-agent/devex-scraper)

```json
{
  "maxItems": 5
}
```

### nomad-agent/ai-job-search-agent

[Open Actor](https://apify.com/nomad-agent/ai-job-search-agent)

This live Actor ranks jobs against a resume. Replace the fictional resume with your own only when you are ready to submit it to this Actor. AI ranking can incur charges; source-confirmed jobs explicitly dated today may be limited.

```json
{
  "maxItems": 5,
  "resumeText": "Fictional setup example: Python backend developer with three years of experience in APIs, SQL, and automated testing. Seeking backend developer roles."
}
```

### nomad-agent/all-jobs-scraper

[Open Actor](https://apify.com/nomad-agent/all-jobs-scraper)

```json
{
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "maxItems": 5,
  "maxItemsPerSource": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  }
}
```

### nomad-agent/europe-jobs-bundle

[Open Actor](https://apify.com/nomad-agent/europe-jobs-bundle)

```json
{
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "maxItems": 5,
  "maxItemsPerSource": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  }
}
```

### nomad-agent/academicpositions-scraper

[Open Actor](https://apify.com/nomad-agent/academicpositions-scraper)

```json
{
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "maxItems": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  }
}
```

### nomad-agent/researcher-bundle

[Open Actor](https://apify.com/nomad-agent/researcher-bundle)

```json
{
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "maxItems": 5,
  "maxItemsPerSource": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  }
}
```

### nomad-agent/web-dev-bundle

[Open Actor](https://apify.com/nomad-agent/web-dev-bundle)

```json
{
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "maxItems": 5,
  "maxItemsPerSource": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  }
}
```

### nomad-agent/web-search-scraper

[Open Actor](https://apify.com/nomad-agent/web-search-scraper)

```json
{
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "maxItems": 5,
  "maxItemsPerSource": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  }
}
```

### nomad-agent/tecnoempleo-scraper

[Open Actor](https://apify.com/nomad-agent/tecnoempleo-scraper)

```json
{
  "maxItems": 5
}
```

### nomad-agent/remote-boards-scraper

[Open Actor](https://apify.com/nomad-agent/remote-boards-scraper)

```json
{
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "maxItems": 5,
  "maxItemsPerSource": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  }
}
```

### nomad-agent/reliefweb-scraper

[Open Actor](https://apify.com/nomad-agent/reliefweb-scraper)

```json
{
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "maxItems": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  }
}
```

### nomad-agent/ml-ai-dev-bundle

[Open Actor](https://apify.com/nomad-agent/ml-ai-dev-bundle)

```json
{
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "maxItems": 5,
  "maxItemsPerSource": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  }
}
```

### nomad-agent/american-jobs-bundle

[Open Actor](https://apify.com/nomad-agent/american-jobs-bundle)

```json
{
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "maxItems": 5,
  "maxItemsPerSource": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  }
}
```

### nomad-agent/unjobs-scraper

[Open Actor](https://apify.com/nomad-agent/unjobs-scraper)

```json
{
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "maxItems": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  }
}
```

### nomad-agent/devex-jobs-scraper

[Open Actor](https://apify.com/nomad-agent/devex-jobs-scraper)

Use this Actor's current `maxItems` input. The separate Devex Actor has a different input shape; do not add fields from another reader.

```json
{
  "maxItems": 5
}
```

### nomad-agent/normalized-ashby-jobs-scraper

[Open Actor](https://apify.com/nomad-agent/normalized-ashby-jobs-scraper)

```json
{
  "schemaVersion": "nomad-agent-inventory-search-v1",
  "maxItems": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  },
  "aiEnrichment": {
    "enabled": false
  },
  "translateToEnglish": false
}
```

### nomad-agent/normalized-dynamitejobs-jobs-scraper

[Open Actor](https://apify.com/nomad-agent/normalized-dynamitejobs-jobs-scraper)

```json
{
  "schemaVersion": "nomad-agent-inventory-search-v1",
  "maxItems": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  },
  "aiEnrichment": {
    "enabled": false
  },
  "translateToEnglish": false
}
```

### nomad-agent/normalized-euractiv-jobs-scraper

[Open Actor](https://apify.com/nomad-agent/normalized-euractiv-jobs-scraper)

```json
{
  "schemaVersion": "nomad-agent-inventory-search-v1",
  "maxItems": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  },
  "aiEnrichment": {
    "enabled": false
  },
  "translateToEnglish": false
}
```

### nomad-agent/normalized-fashionjobs-jobs-scraper

[Open Actor](https://apify.com/nomad-agent/normalized-fashionjobs-jobs-scraper)

```json
{
  "schemaVersion": "nomad-agent-inventory-search-v1",
  "maxItems": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  },
  "aiEnrichment": {
    "enabled": false
  },
  "translateToEnglish": false
}
```

### nomad-agent/normalized-greenhouse-jobs-scraper

[Open Actor](https://apify.com/nomad-agent/normalized-greenhouse-jobs-scraper)

```json
{
  "schemaVersion": "nomad-agent-inventory-search-v1",
  "maxItems": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  },
  "aiEnrichment": {
    "enabled": false
  },
  "translateToEnglish": false
}
```

### nomad-agent/normalized-helloworld-jobs-scraper

[Open Actor](https://apify.com/nomad-agent/normalized-helloworld-jobs-scraper)

```json
{
  "schemaVersion": "nomad-agent-inventory-search-v1",
  "maxItems": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  },
  "aiEnrichment": {
    "enabled": false
  },
  "translateToEnglish": false
}
```

### nomad-agent/normalized-himalayas-jobs-scraper

[Open Actor](https://apify.com/nomad-agent/normalized-himalayas-jobs-scraper)

```json
{
  "schemaVersion": "nomad-agent-inventory-search-v1",
  "maxItems": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  },
  "aiEnrichment": {
    "enabled": false
  },
  "translateToEnglish": false
}
```

### nomad-agent/normalized-jobgether-jobs-scraper

[Open Actor](https://apify.com/nomad-agent/normalized-jobgether-jobs-scraper)

```json
{
  "schemaVersion": "nomad-agent-inventory-search-v1",
  "maxItems": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  },
  "aiEnrichment": {
    "enabled": false
  },
  "translateToEnglish": false
}
```

### nomad-agent/normalized-lever-jobs-scraper

[Open Actor](https://apify.com/nomad-agent/normalized-lever-jobs-scraper)

```json
{
  "schemaVersion": "nomad-agent-inventory-search-v1",
  "maxItems": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  },
  "aiEnrichment": {
    "enabled": false
  },
  "translateToEnglish": false
}
```

### nomad-agent/normalized-mlops-community-jobs-scraper

[Open Actor](https://apify.com/nomad-agent/normalized-mlops-community-jobs-scraper)

```json
{
  "schemaVersion": "nomad-agent-inventory-search-v1",
  "maxItems": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  },
  "aiEnrichment": {
    "enabled": false
  },
  "translateToEnglish": false
}
```

### nomad-agent/normalized-smartrecruiters-jobs-scraper

[Open Actor](https://apify.com/nomad-agent/normalized-smartrecruiters-jobs-scraper)

```json
{
  "schemaVersion": "nomad-agent-inventory-search-v1",
  "maxItems": 5,
  "dedupe": {
    "enabled": true,
    "key": ""
  },
  "aiEnrichment": {
    "enabled": false
  },
  "translateToEnglish": false
}
```

## Run through the API

Save the matching JSON block as `input.json`. Set `APIFY_TOKEN` privately in your environment, then replace the Actor route below with the exact route you chose. This command starts a potentially billable run; it uses explicit limits and selects `latest`.

```bash
curl --fail-with-body --request POST \
  --header "Authorization: Bearer $APIFY_TOKEN" \
  --header "Content-Type: application/json" \
  --data-binary @input.json \
  "https://api.apify.com/v2/acts/nomad-agent~reliefweb-scraper/runs?build=latest&timeout=300&maxTotalChargeUsd=0.20"
```

Inspect the returned run ID, immutable build ID, status, dataset, and log. When available, read `RUN-SUMMARY` from the run's key-value store for delivered, withheld, duplicate, and source-failure counts. Some legacy Actors do not publish this summary. A successful exit with only demo, error, or diagnostic rows does not demonstrate usable source results.

For a simple job row, inspect its source, ID, original URL, title, and complete description. For a normalized row, inspect `identity`, `data`, and the original description in `raw` when raw capture is enabled. Unknown fields can be null; empty arrays are not proof of a missing source scrape.

## Job Atlas normalized routes

These public Job Atlas routes were read back on October 4, 2026. Choose the exact Actor you need and read its own current input schema and Pricing tab. Primary and Job Atlas deployments have separate build identities, runs, and delivery history; a primary run does not verify the corresponding Job Atlas run.

| Actor | Open listing |
|---|---|
| jobatlas/ai-job-fit-scorer | [Open](https://apify.com/jobatlas/ai-job-fit-scorer) |
| jobatlas/euraxess-enrich-translate-normalize-scraper | [Open](https://apify.com/jobatlas/euraxess-enrich-translate-normalize-scraper) |
| jobatlas/linkedin-enrich-translate-normalize-scraper | [Open](https://apify.com/jobatlas/linkedin-enrich-translate-normalize-scraper) |
| jobatlas/normalized-ashby-jobs-scraper | [Open](https://apify.com/jobatlas/normalized-ashby-jobs-scraper) |
| jobatlas/normalized-dynamitejobs-jobs-scraper | [Open](https://apify.com/jobatlas/normalized-dynamitejobs-jobs-scraper) |
| jobatlas/normalized-euractiv-jobs-scraper | [Open](https://apify.com/jobatlas/normalized-euractiv-jobs-scraper) |
| jobatlas/normalized-eurobrussels-jobs-scraper | [Open](https://apify.com/jobatlas/normalized-eurobrussels-jobs-scraper) |
| jobatlas/normalized-fashionjobs-jobs-scraper | [Open](https://apify.com/jobatlas/normalized-fashionjobs-jobs-scraper) |
| jobatlas/normalized-helloworld-jobs-scraper | [Open](https://apify.com/jobatlas/normalized-helloworld-jobs-scraper) |
| jobatlas/normalized-himalayas-jobs-scraper | [Open](https://apify.com/jobatlas/normalized-himalayas-jobs-scraper) |
| jobatlas/normalized-infostud-jobs-scraper | [Open](https://apify.com/jobatlas/normalized-infostud-jobs-scraper) |
| jobatlas/normalized-jobgether-jobs-scraper | [Open](https://apify.com/jobatlas/normalized-jobgether-jobs-scraper) |
| jobatlas/normalized-lever-jobs-scraper | [Open](https://apify.com/jobatlas/normalized-lever-jobs-scraper) |
| jobatlas/normalized-manfred-jobs-scraper | [Open](https://apify.com/jobatlas/normalized-manfred-jobs-scraper) |
| jobatlas/normalized-mlops-community-jobs-scraper | [Open](https://apify.com/jobatlas/normalized-mlops-community-jobs-scraper) |
| jobatlas/normalized-smartrecruiters-jobs-scraper | [Open](https://apify.com/jobatlas/normalized-smartrecruiters-jobs-scraper) |
| jobatlas/ycombinator-enrich-translate-normalize-scraper | [Open](https://apify.com/jobatlas/ycombinator-enrich-translate-normalize-scraper) |

## Filtering and exports

Set source filters in the input Form before starting the run. Normalized advanced filters may use a JSON editor. Output views format the result columns; views and pagination do not imply interactive row search, filtering, or sorting. Export JSON or CSV when you need to filter returned rows in your own application or spreadsheet.

For setup automation, install the [public Actor skill](https://github.com/Exdenta/jobatlas/blob/main/.agents/skills/public-apify-actors/SKILL.md). It reads current Actor metadata and schemas before choosing inputs. Keep credentials in environment variables and authorization headers; never put tokens into committed examples or public links.

## Example maintenance

These examples describe the published input shapes observed on October 4, 2026. Recheck the current schema when an Actor changes. They intentionally avoid numeric production build pins, customer data, required customer API keys, and fabricated result rows.
