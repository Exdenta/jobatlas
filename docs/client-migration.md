# Actor catalogue and client migration

The [versioned Actor catalogue](../catalogue/actors-v1.json) separates a logical product from each deployed copy. The 2026-09-08 read-back accounts for 64 Actors owned by `nomad-agent`: 43 public job products, three private support Actors, and 18 unrelated public products. It also records four public `job-atlas` deployments. Those four have different immutable Actor IDs and build histories from their same-slug `nomad-agent` counterparts, so they are copies, not redirects or renamed Actors.

The catalogue is an interoperability record. It does not claim that hosted Actor source is present in this repository, that a mutable `latest` build was executed, or that a destination received data. Validate it with:

```bash
python3 scripts/validate_actor_catalogue.py
```

## Recommended namespace policy

Keep the four verified `job-atlas` deployments as the maintained endpoints for new repository callers. Keep all `nomad-agent` deployments unchanged as compatibility endpoints until each migration is approved and verified.

Do not mass-copy the remaining 39 job products. Apify documents Actor transfer as a Support-assisted operation that retains reviews and usage statistics while changing the Store URL. Before using that path, ask Support to confirm immutable Actor-ID continuity, same-slug collision handling, monetization and existing-user behavior, Task ownership, webhooks, schedules, and rollback for the exact Actors in the batch. If any of those answers is incomplete, retain `nomad-agent` as the technical compatibility namespace and use Job Atlas only as the display brand.

Primary platform references:

- [Actor transfer and access rights](https://docs.apify.com/account/collaboration/access-rights)
- [Actor identifiers in the API](https://docs.apify.com/api/v2/actors)
- [Saved Tasks](https://docs.apify.com/actors/running/tasks)
- [Webhooks](https://docs.apify.com/integrations/webhooks)
- [Schedules](https://docs.apify.com/actors/running/schedules)
- [Organization billing behavior](https://docs.apify.com/account/collaboration/organization/how-to-use)

## Client-by-client treatment

| Client or state | Before a change | Migration action | Proof required before cutover | Rollback |
| --- | --- | --- | --- | --- |
| REST API and SDK | Read the exact route, immutable Actor ID, selector, caps, and retry policy. | Replace the owner/slug and expected immutable ID together. Continue selecting `latest`; record the returned build ID and numeric build number. | One approved bounded run with terminal status, exact-build read-back, contract-valid summary, and reconciled dataset. | Restore the prior route and ID; do not delete the old Actor. |
| MCP | Export the client configuration and note its allowed tools and authentication owner. | Replace the Actor route in the generic `call-actor` input. Keep exact-build and charge-cap checks. | Hosted MCP call, exact run receipt, summary, and dataset. This does not prove a destination write. | Restore the prior MCP input or configuration. |
| n8n | Export the inactive workflow; record schedule state, route, internal IDs, credentials, and destination placeholders. | Import a fresh inactive copy, update the route and expected Actor ID, reselect credentials, and let the editor regenerate internal IDs. | Node-by-node inspection, then one separately approved create and idempotent update in a named disposable destination. | Disable the new workflow and re-enable the saved prior export. |
| Make | Read the referenced Apify Task, build selector, scenario timezone, schedule state, credentials, and destination. | Create or verify the corresponding Task, import a new inactive scenario, and replace the Task placeholder. | Exact Task read-back plus one approved run and one create/update destination canary. | Disable the new scenario and restore the former Task and scenario. |
| Zapier | Export the Zap or editor specification; record schedule, Actor identity, credentials, and destination key. | Build a disabled replacement using the Job Atlas route and immutable ID. | Editor inspection plus one approved create/update canary. | Turn off the replacement and restore the previous Zap. |
| Airtable | Record the upstream runner, base/table, field map, key field, and credential owner. | Change the upstream Actor only; the shared destination projection remains keyed by `jobKey`. | One create and one update in a disposable table, tied to the exact source run. | Restore the previous upstream route and remove only canary rows. |
| Agent Skill | Inspect the installed skill and MCP server entry; local copies do not update themselves. | Reinstall the maintained skill or change its Actor route and identity guard together. | Run the skill validator and one hosted MCP canary if live use is approved. | Restore the previous skill directory or configuration entry. |
| Python or custom parser | Record embedded route and ID constants separately from post-run schema logic. | Change only the runner identity. Keep source-specific validators and projections unchanged. | Offline fixtures plus an approved exact-run fixture from the replacement. | Restore the runner constants; keep the schema layer untouched. |
| Saved Tasks | Read `actId`, input, selector, caps, and integrations without publishing secrets. | Recreate for a copy, or retain and verify after a confirmed in-place transfer. Never assume automatic migration. | Exact Task read-back and a redacted input hash. | Keep the old Task disabled but intact until acceptance. |
| Webhooks | Record Actor/Task conditions, event types, enabled state, payload template, and destination owner. | Clone or rebind only after the target identity is final. | One disposable terminal event and destination receipt. | Disable the new hook and restore the prior binding. |
| Schedules | Record target, cron, timezone, enabled state, selector, and caps. | Move only with the exact Actor or Task it drives. | Before/after schedule read-back and one bounded scheduled canary. | Restore the prior target and enabled state. |
| Billing and subscriptions | Capture pricing configuration and ask Support about the exact transfer or copy behavior. | Make no commercial cutover from metadata alone. | Pricing read-back, bounded charge receipt, and written continuity answer for existing users and payouts. | Leave the prior public deployment available. |
| Credentials | Identify the account and minimum required permissions without exporting the secret. | Reselect credentials in each replacement client. | Bounded authenticated read, followed by separately approved run/write checks. | Disable the replacement and retain the original credential binding. |

## Contract invariants

Namespace changes do not authorize schema changes. The three normalized source Actors keep the six-root `nomad-agent-job-v1` envelope, source-specific custom extensions, `nomad-agent-run-summary-v4`, and legacy v3 compatibility where documented. The flat projection keeps `jobKey`, using `{source}:{externalId}` and the existing `{source}:{url}` fallback; it never falls back to title or company. Unknown scalar values remain `null`, known-empty collections remain `[]`, and `raw: null` remains valid when raw capture is disabled.

The fit scorer keeps `nomad-ai-job-fit-v1` and its current v4 summary. A posting's `jobKey` and a candidate-specific destination `matchKey` are different identities. Do not send fit rows through the flat-job mapper.

## Approval-gated rollout

1. Ask Apify Support for exact transfer and collision semantics; record the answer against immutable Actor IDs.
2. Select one low-risk Actor and one client class. Capture pre-change metadata and define the cost cap, destination, acceptance checks, and rollback.
3. Obtain separate approval for the Actor mutation, the paid run, and any destination write or schedule activation.
4. Run one bounded canary, then verify the same run's immutable build, summary, dataset, charges, and named destination where applicable.
5. Observe before expanding. Keep the old deployment and client configuration available through the rollback window.

The 2026-09-08 S02 work performed metadata reads and local validation only. It started no Actor, changed no external resource, imported no template, and wrote to no destination.
