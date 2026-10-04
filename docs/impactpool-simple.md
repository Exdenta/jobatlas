# Impactpool jobs: simple source facts

[Impactpool](https://apify.com/nomad-agent/impactpool-scraper) returns UN, NGO and international-development jobs with original descriptions, HTML, source links and locations. The current row is `nomad-agent-job-row-v3`, with 15 fields and no `recordType`. It performs no AI enrichment or translation.

## First run

Select `latest`, check the current Input and Pricing tabs, and record the immutable build returned by the run.

```json
{
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "maxItems": 5,
  "postedWithin": "any",
  "dedupe": {"enabled": true, "key": ""}
}
```

Optional query, location, work-arrangement and employment-type filters follow the [simple filter guide](simple-filters-v2.md). A source fact that is unknown does not satisfy a corresponding active filter. `maxItems` is at most 200; zero means 200. Filters, source limitations and repeat suppression can produce fewer results or a valid empty dataset.

`postedWithin` accepts `any` or a positive duration such as `7d`, up to 36500 days. A date recorded without a reliable source publication date means first observation; later observations do not reset it. It is not proof of the employer's publication date.

Unknown optional facts remain `null`; `locations: []` means no usable location was parsed and `hiringContacts: []` means no named contacts. Keep `(source, id)` as the posting key. Read the original description for eligibility and application requirements.

Inspect `RUN-SUMMARY` separately from dataset rows for delivery counts, limits and source availability. Dated earlier owner tests are not proof that your search or destination works today. See the [complete public directory](public-actors.md) for other products.
