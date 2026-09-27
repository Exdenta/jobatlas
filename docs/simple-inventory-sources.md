# UN Careers, Copenhagen and Ikerbasque jobs: simple inventory output

These Actors return stored jobs in `nomad-agent-job-row-v2`. Each posting includes its source identity, title, URL, complete original description, HTML and a `locations` array. Unknown optional source facts remain `null`; an unavailable location is `[]`.

| Source | Actor |
| --- | --- |
| UN Careers | [UN Careers jobs](https://apify.com/nomad-agent/un-careers-scraper) |
| University of Copenhagen mathematics PhDs | [Copenhagen PhD jobs](https://apify.com/nomad-agent/math-ku-phd-scraper) |
| Ikerbasque | [Ikerbasque jobs](https://apify.com/nomad-agent/ikerbasque-scraper) |

Select `latest` and record the immutable build ID returned by the run. Simple Actors are not mirrored to Job Atlas.

## First run

```json
{
  "schemaVersion": "nomad-agent-simple-inventory-search-v1",
  "maxItems": 5,
  "postedWithin": "any",
  "dedupe": {"enabled": true, "key": ""}
}
```

`postedWithin` is the only job filter. It accepts `any` or a positive duration such as `7d`; supported suffixes are hours (`h`), days (`d`), weeks (`w`) and 30-day months (`m`), with a maximum of 36500 days. When a source does not publish a reliable original posting date, the stored date is its first inventory admission; later refreshes do not make the posting new. `maxItems` is bounded to 200, and zero means 200.

Full descriptions are always included. There is no AI enrichment, translation, custom extension or source-site request during a public run. Unproven descriptions are withheld. If inventory is unavailable or stale, the run fails without a website fallback. Coverage may be smaller than the source website.

Repeat suppression is enabled by default for the same user and search. Disable it for a stateless run. Existing startup and result charges remain unchanged; suppressing a repeat result does not charge for that result. Inspect `RUN-SUMMARY` separately from the jobs dataset.

## Migration and verification

Use the versioned inventory input above in place of the old source-search controls. Simple v2 removes `custom`, `warnings` and `docs` from posting rows, retains complete text and HTML, and exposes source salary when available. V1 scoring uses description plus title, employer, location, salary and stable source/ID/URL context.

On 22 September 2026, all three Actors passed bounded owner tests through their promoted default selectors. Each returned a complete proven posting; each repeat suppressed the same posting without a result charge. These tests do not establish normal buyer traffic or downstream scoring and delivery.
