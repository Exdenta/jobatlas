# Four Job Atlas first-run packs

These packs turn a first Actor trial into a reviewable, bounded proposal. Each one binds a small starter input to the promoted `job-atlas` Actor, a dated public build readback, an evidence-labelled sample, the output and run-summary contracts, expected cost mechanics, and the checks required before calling a result usable.

No exact pack input was run while preparing this package. The included September 9 run IDs are related current-organization evidence, not proof of these inputs or any destination delivery. Each proposed run remains separately approval-gated.

## Choose the outcome

| Pack | First useful outcome | Sample evidence | Public `latest` readback on 11 September 2026 | Proposed ceiling |
| --- | --- | --- | --- | ---: |
| [LinkedIn](packs/linkedin.json) | Up to five recent TypeScript roles for a Spain search | Fictional illustrative row | `1.0.5` / `4wE4rKPq5aq7jeIY1`; base result `$0.0009` | `$0.10` |
| [EURAXESS](packs/euraxess.json) | Up to five recent postdoctoral machine-learning opportunities | Recorded source row from 4 September 2026 | `1.0.4` / `x0bGueGFnm6eEGY3K`; base result `$0.0009` | `$0.05` |
| [Y Combinator](packs/ycombinator.json) | Up to five founding-engineer roles from refreshed inventory | Fictional row validated against `ycombinator-v2` | `1.0.4` / `9D13ViqHgk6hFtWVi`; base result `$0.0009` | `$0.05` |
| [AI Job Fit Scorer](packs/ai-job-fit-scorer.json) | Up to five explained evaluations for a fictional candidate | Historical predecessor row, not current Job Atlas output | `0.1.5` / `gxzLgzyS6vc1djG9S`; fit result `$0.02` | `$0.10` |

The ceiling is an authorization limit, not a quote or a promise of that many rows. The three scraper inputs disable optional enrichment, translation, raw output, deduplication, and analytics; the scorer uses a fictional profile and a three-source shortlist. Runtime varies with source state, options, cache state, and source health.

## Review before any run

1. Open the pack manifest and its hashed starter input. Confirm the exact Actor ID, literal `latest` selector, maximum items, optional features, and maximum total charge.
2. Re-read the deployed input schema and pricing. If either differs from the dated manifest, stop and revise the proposal.
3. Obtain approval for that one run. A pack authorizes zero follow-up runs, destinations, schedules, webhooks, repository publication, or Actor metadata changes.
4. Retain the terminal run ID, resolved immutable build ID and number, dataset ID, key-value-store ID, exit code, and settled charge receipt from the same run.
5. Validate the one run summary, every returned row, source identity, count arithmetic, partial and retry guidance, and product-specific result policy. A successful Actor status alone is insufficient.

Use synthetic or consented candidate information. Do not place credentials in input JSON; authenticate outside the file with Apify's bearer-token mechanism.

## Interpret the result

- `null` means a fact was unknown or unavailable. For scraper rows, `[]` means the source established an empty collection.
- Zero rows describe only the bounded input and observed source state. They do not show that no matching job exists.
- `partial` may still contain useful rows. A deliberate cap can set `resultsLimited=true` without recommending another run.
- Reject missing immutable build or storage identities, invalid schemas, source drift, non-`SUCCEEDED` terminal runs, count mismatches, or unsettled cost evidence.
- An Actor result does not prove an imported workflow, active schedule, notification, named destination write, application, customer use, or retention.

The manifests contain the source-specific support route and the narrowest documented next step. In particular, Y Combinator points only to the documented REST recipe and maintained Agent Skill; the pack does not upgrade its other integration surfaces.

## Validate locally

Run the standard-library-only check from the repository root:

```bash
python3 scripts/validate_first_run_packs.py
```

The validator checks all four manifests against [the closed pack schema](first-run-pack-v1.schema.json), recomputes referenced hashes, reconciles the catalogue identities and dated build labels, rejects unsafe input settings, validates product-specific row contracts, and checks exact single-run approval rules. It performs no network request and starts no Actor run.
