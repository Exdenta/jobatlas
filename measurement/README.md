# Job Atlas measurement contract

This directory defines the public, dependency-free measurement contract for Job Atlas. The files describe what can be reported; they do not assert that collection, indexing, activation, delivery, retention, or revenue has happened.

## Files

- `campaign-registry-v1.json` is the exact campaign allowlist. Its schema is `campaign-registry-v1.schema.json`.
- `event-definitions-v1.json` fixes the 25 event names, canonical page paths, required dimensions, activity classes, and reporting denominators. Its schema is `event-definitions-v1.schema.json`.
- `site-events-v1.schema.json` defines a privacy-minimized event batch. `site-events.sample.json` is synthetic and includes one exact duplicate after campaign alias normalization.
- `baseline-v1.schema.json` defines the measurement ledger. `baseline.sample.json` is synthetic and demonstrates every status, per-layer dates, a change point, owner-test exclusion, and nullable metrics.

All schemas are closed: unknown fields fail validation. The JSON Schemas enforce the portable shape constraints; the dependency-free CLI is the normative semantic validator for exact v1 vocabularies, date reconciliation, event chronology, sorted identities, and aggregate totals. Producers must run both layers before publishing an artifact. A version change is required before adding campaign values, event names, dimensions, routes, or baseline fields.

## Evidence statuses

`observed` means the named source was checked for the stated layer window or point in time and yielded a value. An observed zero is a real measurement and is not the same as unknown. Observed metrics require a numeric value, a null reason, and layer evidence.

`unknown` means the truth was not established. `unavailable` means the named evidence source could not be used. `not_mature` means the required cohort or time window has not matured. `not_collected` means no qualifying collection was configured or received. Every non-observed layer and metric has a reason; null is never silently converted to zero.

Each layer records its own `asOf`, optional `window`, `ownerTestsExcluded`, and `limitations`. The top-level window describes the overall program view, not a claim that every source used the same dates. `changePoints` records releases or migrations that can split comparison windows. Equal-length windows should not be compared across a change point without an explicit limitation.

The fixed layer order is deployment, discovery, Google indexing, Bing indexing, search demand, onsite intent, Actor execution, useful activation, destination delivery, retention, commercial, and support. A discovery receipt is not indexing evidence. A click or successful Actor run does not prove activation, and activation does not prove destination delivery.

Each layer has separate allowed evidence and qualifying evidence kinds. `repository_fixture` and `operator_statement` may add context to any layer, but neither can qualify an observed metric. The qualifying evidence kinds are:

- deployment: `deployment_receipt`
- discovery: `discovery_receipt` or `deployment_receipt`
- Google indexing: `google_url_inspection`
- Bing indexing: `bing_url_inspection`
- search demand: `google_search_console`
- onsite intent: `site_event_batch`
- Actor execution: `actor_analytics` or `deployment_receipt`
- useful activation: `activation_receipt`
- destination delivery: `destination_receipt`
- retention: `retention_report`
- commercial: `commercial_report`
- support: `support_ledger`

Evidence that belongs to another layer fails validation. In particular, a discovery receipt cannot prove Google indexing, and a site-event batch cannot prove useful activation. Qualification is checked for every observed metric and its activity segment, rather than once for the layer.

For Actor execution, `deployment_receipt` may qualify only an `owner_test` metric. Observed `unclassified` and `customer_activity` Actor-execution metrics require `actor_analytics`. The other activity layers use their named qualifying kind for every permitted activity segment: `site_event_batch` for onsite intent, `activation_receipt` for useful activation, `destination_receipt` for destination delivery, `retention_report` for retention, `commercial_report` for commercial, and `support_ledger` for support. One qualifying receipt may support multiple observed metrics in the same layer and segment when its referenced artifact contains those measurements.

Metric status is independent from layer status. This allows an `actorExecution` layer to preserve observed owner-test canaries while its customer-run metric remains unknown. Activity metrics use `unclassified`, `owner_test`, or `customer_activity`; activity layers cannot use an aggregate segment. The `ownerTestsExcluded` flag makes the exclusion decision explicit. Recorded owner tests and customer activity must never be pooled.

## Site events and privacy

Events use a flat envelope. Campaign fields are `source`, `medium`, `campaign`, and optional `content`. Other allowed dimensions are `category`, `label`, `placement`, `product`, `actor`, `destination`, and `format`. These dimensions are controlled lowercase tokens, not free text. Dedicated user, session, email, IP, cookie, and arbitrary-URL fields are rejected. The controlled-token syntax also blocks ordinary email addresses, URLs, and free text, but syntax alone cannot prove that an opaque token was not reused as an identifier. Producers must use reviewed semantic values and must not place names, handles, receipt IDs, hashes, or other person/device identifiers inside a dimension.

The page field accepts only the 24 canonical site paths plus `/404`. Event IDs are canonical lowercase UUIDs and timestamps are UTC values ending in `Z`. Browser events start as `unclassified`; the browser must not infer customer activity. A trusted downstream process may classify records as `owner_test` or `customer_activity` when it has separate evidence.

Campaign attribution is atomic. The legacy source `nomad-agent-job-scrapers` canonicalizes to the reporting source `jobatlas`. The browser omits all campaign fields if any required value is missing or outside the registry. A serialized event that nevertheless contains an invalid or partial tuple is rejected by the batch validator. The optional content value is a lowercase, hyphen-only token of at most 64 characters.

Event summaries deduplicate only after normalization. Repeated event IDs with identical normalized payloads count as exact duplicates. A conflicting duplicate event ID fails the batch instead of choosing one payload. Counts remain separated by activity class. Every summary retains its batch source, observation time, and event-time range so synthetic activity cannot be mistaken for received production evidence. The digest covers sorted, unique normalized events so input order cannot change the result.

`page_view` is a count and has no denominator. Every other event rate uses received `page_view` events for the same page, reporting window, and activity class. A ratio or percent denominator must name a distinct observed count metric in the same layer and segment, and its recorded value must equal that metric. The contract never infers users or sessions.

An event summary retains the batch `observedAt` timestamp, which must not be later than the baseline `generatedAt` timestamp. The semantic validator enforces this cross-field rule; the JSON Schema documents it but cannot compare timestamps stored in separate object locations.

## Commands

Run these commands from the repository root:

```sh
python3 scripts/measurement_baseline.py validate-registry \
  --campaigns measurement/campaign-registry-v1.json

python3 scripts/measurement_baseline.py validate-definitions \
  --definitions measurement/event-definitions-v1.json

python3 scripts/measurement_baseline.py summarize-events \
  --events measurement/site-events.sample.json \
  --campaigns measurement/campaign-registry-v1.json \
  --output /tmp/jobatlas-event-summary.json

python3 scripts/measurement_baseline.py validate-baseline \
  --baseline measurement/baseline.sample.json

python3 scripts/measurement_baseline.py build \
  --baseline measurement/baseline.sample.json \
  --campaigns measurement/campaign-registry-v1.json \
  --events measurement/site-events.sample.json \
  --output /tmp/jobatlas-baseline.json
```

The builder validates the registry and baseline, canonicalizes campaigns, rejects conflicting IDs, sorts report structures, and writes deterministic JSON. Supplying an event batch attaches only its aggregate summary. That summary does not turn a synthetic fixture, local owner test, or unclassified browser event into evidence of customer activation.
