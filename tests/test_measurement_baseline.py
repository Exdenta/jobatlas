from __future__ import annotations

import copy
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import unittest

from scripts import measurement_baseline


ROOT = Path(__file__).resolve().parents[1]
MEASUREMENT = ROOT / "measurement"
REGISTRY_PATH = MEASUREMENT / "campaign-registry-v1.json"
EVENTS_PATH = MEASUREMENT / "site-events.sample.json"
DEFINITIONS_PATH = MEASUREMENT / "event-definitions-v1.json"
BASELINE_PATH = MEASUREMENT / "baseline.sample.json"


class MeasurementBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.event_batch = json.loads(EVENTS_PATH.read_text(encoding="utf-8"))
        cls.definitions = json.loads(DEFINITIONS_PATH.read_text(encoding="utf-8"))
        cls.baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))

    def test_public_assets_validate_and_schemas_close_every_object(self) -> None:
        measurement_baseline.validate_campaign_registry(self.registry)
        measurement_baseline.validate_event_batch(self.event_batch, self.registry)
        measurement_baseline.validate_event_definitions(self.definitions)
        measurement_baseline.validate_baseline(self.baseline)

        for name in (
            "campaign-registry-v1.schema.json",
            "event-definitions-v1.schema.json",
            "site-events-v1.schema.json",
            "baseline-v1.schema.json",
        ):
            schema = json.loads((MEASUREMENT / name).read_text(encoding="utf-8"))
            pending = [schema]
            while pending:
                node = pending.pop()
                if isinstance(node, dict):
                    if node.get("type") == "object":
                        self.assertIs(node.get("additionalProperties"), False, (name, node))
                    pending.extend(node.values())
                elif isinstance(node, list):
                    pending.extend(node)

        event_schema = json.loads(
            (MEASUREMENT / "site-events-v1.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            len(event_schema["$defs"]["event"]["allOf"]),
            len(measurement_baseline.EVENT_VOCABULARY),
        )
        definitions_schema = json.loads(
            (MEASUREMENT / "event-definitions-v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            definitions_schema["properties"]["canonicalPages"]["const"],
            list(measurement_baseline.CANONICAL_PAGES),
        )
        self.assertEqual(
            len(definitions_schema["$defs"]["eventDefinition"]["allOf"]),
            len(measurement_baseline.EVENT_VOCABULARY),
        )
        baseline_schema = json.loads(
            (MEASUREMENT / "baseline-v1.schema.json").read_text(encoding="utf-8")
        )
        self.assertTrue(
            {"batchSource", "observedAt", "firstOccurredAt", "lastOccurredAt"}
            <= set(baseline_schema["$defs"]["eventSummary"]["required"])
        )

    def test_event_definitions_cover_vocabulary_denominators_and_paths(self) -> None:
        definitions = self.definitions["definitions"]
        self.assertEqual(
            {definition["event"] for definition in definitions},
            set(measurement_baseline.EVENT_VOCABULARY),
        )
        self.assertEqual(
            self.definitions["canonicalPages"], list(measurement_baseline.CANONICAL_PAGES)
        )
        self.assertEqual(len(self.definitions["canonicalPages"]), 25)
        for definition in definitions:
            self.assertIn("placement", definition["requiredDimensions"])
            self.assertEqual(
                definition["allowedActivityClasses"],
                ["unclassified", "owner_test", "customer_activity"],
            )
            if definition["event"] == "page_view":
                self.assertIsNone(definition["reportingDenominator"])
            else:
                self.assertEqual(
                    definition["reportingDenominator"],
                    {
                        "event": "page_view",
                        "matchDimensions": ["page", "window", "activityClass"],
                    },
                )

    def test_browser_runtime_matches_public_measurement_vocabularies(self) -> None:
        script = (ROOT / "website" / "script.js").read_text(encoding="utf-8")

        rules_match = re.search(
            r'const eventRules = new Map\("([^"]+)"\.split\(" "\)', script
        )
        self.assertIsNotNone(rules_match)
        runtime_rules = {
            event: set(fields.split(","))
            for event, fields in (
                rule.split(":") for rule in rules_match.group(1).split()
            )
        }
        contract_rules = {
            definition["event"]: set(definition["requiredDimensions"]) - {"placement"}
            for definition in self.definitions["definitions"]
        }
        self.assertEqual(runtime_rules, contract_rules)

        def runtime_set(name: str) -> set[str]:
            match = re.search(
                rf'const {name} = new Set\("([^"]+)"\.split\(" "\)\);', script
            )
            self.assertIsNotNone(match, name)
            return set(match.group(1).split())

        self.assertEqual(
            runtime_set("canonicalPages"),
            set(self.definitions["canonicalPages"]) - {"/404"},
        )
        self.assertEqual(runtime_set("campaignSources"), set(self.registry["sources"]))
        self.assertEqual(runtime_set("campaignMedia"), set(self.registry["media"]))
        self.assertEqual(runtime_set("campaignNames"), set(self.registry["campaigns"]))
        self.assertIn(f'/{self.registry["contentPattern"]}/.test(content)', script)
        self.assertIn(
            's[0] === "nomad-agent-job-scrapers" ? "jobatlas" : s[0]', script
        )

    def test_campaign_registry_has_exact_vocabulary_and_legacy_alias(self) -> None:
        self.assertEqual(
            self.registry["sources"],
            ["jobatlas", "devto", "linkedin", "youtube", "github", "apify", "n8n", "make"],
        )
        self.assertEqual(
            self.registry["media"],
            ["owned-site", "tutorial", "social", "video", "documentation", "template", "referral"],
        )
        self.assertEqual(
            self.registry["campaigns"],
            ["actor-discovery", "linkedin-alerts", "euraxess-tracker", "yc-tracker", "fit-scoring"],
        )
        self.assertEqual(self.registry["sourceAliases"], {"nomad-agent-job-scrapers": "jobatlas"})

    def test_campaign_canonicalization_is_atomic_and_allowlisted(self) -> None:
        self.assertEqual(
            measurement_baseline.canonicalize_campaign(
                self.registry,
                source="nomad-agent-job-scrapers",
                medium="owned-site",
                campaign="actor-discovery",
                content="w04-guide",
            ),
            {
                "source": "jobatlas",
                "medium": "owned-site",
                "campaign": "actor-discovery",
                "content": "w04-guide",
            },
        )
        self.assertEqual(
            measurement_baseline.canonicalize_campaign(
                self.registry,
                source="jobatlas",
                medium="owned-site",
                campaign=None,
                content="w04-guide",
            ),
            {},
        )
        self.assertEqual(
            measurement_baseline.canonicalize_campaign(
                self.registry,
                source="newsletter",
                medium="email",
                campaign="launch",
                content="Person@Example.com",
            ),
            {},
        )

    def test_event_normalization_enforces_uuid_utc_page_and_required_properties(self) -> None:
        event = copy.deepcopy(self.event_batch["events"][0])
        normalized = measurement_baseline.validate_site_event(event, self.registry)
        self.assertEqual(normalized["eventId"], event["eventId"])

        cases = (
            ("eventId", "not-a-uuid", "UUID"),
            ("occurredAt", "2026-09-10T01:00:00+02:00", "UTC"),
            ("page", "/actors/linkedin?from=home", "page"),
            ("page", "/private/john-doe", "page"),
            ("event", "form_submitted", "event vocabulary"),
        )
        for field, value, expected in cases:
            with self.subTest(field=field):
                invalid = copy.deepcopy(event)
                invalid[field] = value
                with self.assertRaisesRegex(measurement_baseline.ValidationError, expected):
                    measurement_baseline.validate_site_event(invalid, self.registry)

        missing = copy.deepcopy(event)
        del missing["placement"]
        with self.assertRaisesRegex(measurement_baseline.ValidationError, "placement"):
            measurement_baseline.validate_site_event(missing, self.registry)

    def test_event_contract_rejects_identifiers_and_unknown_fields(self) -> None:
        event = copy.deepcopy(self.event_batch["events"][0])
        for key in ("userId", "sessionId", "visitorId", "email", "ipAddress", "cookie"):
            with self.subTest(key=key):
                invalid = copy.deepcopy(event)
                invalid[key] = "stable-or-personal-value"
                with self.assertRaisesRegex(measurement_baseline.ValidationError, "forbidden|unknown"):
                    measurement_baseline.validate_site_event(invalid, self.registry)

        invalid = copy.deepcopy(event)
        invalid["destinationUrl"] = "https://example.com/?token=secret"
        with self.assertRaisesRegex(measurement_baseline.ValidationError, "unknown"):
            measurement_baseline.validate_site_event(invalid, self.registry)

        invalid = copy.deepcopy(event)
        invalid["label"] = "person@example_com"
        with self.assertRaisesRegex(measurement_baseline.ValidationError, "controlled token"):
            measurement_baseline.validate_site_event(invalid, self.registry)

    def test_partial_and_invalid_event_campaigns_are_rejected(self) -> None:
        partial = copy.deepcopy(self.event_batch["events"][1])
        partial.pop("campaign")
        with self.assertRaisesRegex(measurement_baseline.ValidationError, "campaign"):
            measurement_baseline.validate_site_event(partial, self.registry)

        invalid = copy.deepcopy(self.event_batch["events"][1])
        invalid["source"] = "unknown-source"
        with self.assertRaisesRegex(measurement_baseline.ValidationError, "campaign"):
            measurement_baseline.validate_site_event(invalid, self.registry)

    def test_event_batch_rejects_events_after_observation_time(self) -> None:
        invalid = copy.deepcopy(self.event_batch)
        invalid["events"][0]["occurredAt"] = "2026-09-10T01:02:04Z"
        with self.assertRaisesRegex(measurement_baseline.ValidationError, "after.*observedAt"):
            measurement_baseline.validate_event_batch(invalid, self.registry)

    def test_event_summary_deduplicates_exact_ids_and_rejects_conflicts(self) -> None:
        summary = measurement_baseline.summarize_events(self.event_batch, self.registry)
        self.assertEqual(summary["inputCount"], 3)
        self.assertEqual(summary["uniqueCount"], 2)
        self.assertEqual(summary["exactDuplicateCount"], 1)
        self.assertEqual(
            summary["byActivityClass"],
            [{"key": "customer_activity", "count": 1}, {"key": "owner_test", "count": 1}],
        )
        self.assertEqual(
            summary["byEvent"],
            [{"key": "actor_cta_click", "count": 1}, {"key": "page_view", "count": 1}],
        )
        self.assertEqual(
            summary["byCampaign"],
            [{"key": "jobatlas/owned-site/actor-discovery/w04-guide", "count": 1}],
        )
        self.assertEqual(summary["batchSource"], "synthetic_fixture")
        self.assertEqual(summary["observedAt"], self.event_batch["observedAt"])
        self.assertEqual(summary["firstOccurredAt"], "2026-09-10T01:00:00Z")
        self.assertEqual(summary["lastOccurredAt"], "2026-09-10T01:01:00Z")

        conflict = copy.deepcopy(self.event_batch)
        conflict["events"][2]["page"] = "/actors/euraxess"
        with self.assertRaisesRegex(measurement_baseline.ValidationError, "conflicting duplicate eventId"):
            measurement_baseline.summarize_events(conflict, self.registry)

    def test_event_summary_is_deterministic_across_input_order(self) -> None:
        forward = measurement_baseline.summarize_events(self.event_batch, self.registry)
        reversed_batch = copy.deepcopy(self.event_batch)
        reversed_batch["events"].reverse()
        reverse = measurement_baseline.summarize_events(reversed_batch, self.registry)
        self.assertEqual(forward, reverse)
        self.assertRegex(forward["eventDigestSha256"], r"^[0-9a-f]{64}$")

    def test_event_summary_rejects_uncontrolled_aggregate_keys(self) -> None:
        summary = measurement_baseline.summarize_events(self.event_batch, self.registry)
        cases = (
            ("byEvent", "private_event"),
            ("byPage", "/private/person-name"),
            ("byCampaign", "jobatlas/owned-site/private/person-name"),
        )
        for collection, key in cases:
            with self.subTest(collection=collection):
                invalid = copy.deepcopy(summary)
                invalid[collection][0]["key"] = key
                invalid[collection].sort(key=lambda row: row["key"])
                with self.assertRaisesRegex(
                    measurement_baseline.ValidationError, "unsupported"
                ):
                    measurement_baseline._validate_event_summary(invalid)

    def test_baseline_has_exact_layers_and_all_status_values(self) -> None:
        measurement_baseline.validate_baseline(self.baseline)
        self.assertEqual(tuple(self.baseline["layers"]), measurement_baseline.BASELINE_LAYERS)
        self.assertEqual(
            {layer["status"] for layer in self.baseline["layers"].values()},
            set(measurement_baseline.STATUS_VALUES),
        )
        for layer in self.baseline["layers"].values():
            self.assertIn("asOf", layer)
            self.assertIn("window", layer)
            self.assertIn("ownerTestsExcluded", layer)
            self.assertIn("limitations", layer)
            self.assertNotIn("notes", layer)

    def test_baseline_has_change_points_and_heterogeneous_evidence_dates(self) -> None:
        self.assertTrue(self.baseline["changePoints"])
        self.assertEqual(
            self.baseline["changePoints"][0]["id"], "s03-release-2026-09-09"
        )
        as_of_dates = {
            layer["asOf"][:10] for layer in self.baseline["layers"].values()
        }
        self.assertTrue({"2026-09-07", "2026-09-08", "2026-09-09", "2026-09-10"} <= as_of_dates)

    def test_layers_reject_cross_layer_evidence_substitution(self) -> None:
        qualifying = {
            "deployment": ("deployment_receipt",),
            "discovery": ("discovery_receipt", "deployment_receipt"),
            "googleIndexing": ("google_url_inspection",),
            "bingIndexing": ("bing_url_inspection",),
            "searchDemand": ("google_search_console",),
            "onsiteIntent": ("site_event_batch",),
            "actorExecution": ("actor_analytics", "deployment_receipt"),
            "usefulActivation": ("activation_receipt",),
            "destinationDelivery": ("destination_receipt",),
            "retention": ("retention_report",),
            "commercial": ("commercial_report",),
            "support": ("support_ledger",),
        }
        allowed = {
            layer_name: ("repository_fixture", "operator_statement", *kinds)
            for layer_name, kinds in qualifying.items()
        }
        self.assertEqual(measurement_baseline.LAYER_ALLOWED_EVIDENCE_KINDS, allowed)
        self.assertEqual(
            measurement_baseline.LAYER_QUALIFYING_EVIDENCE_KINDS, qualifying
        )

        schema = json.loads(
            (MEASUREMENT / "baseline-v1.schema.json").read_text(encoding="utf-8")
        )
        for layer_name, kinds in allowed.items():
            rule = schema["$defs"]["layers"]["properties"][layer_name]
            self.assertEqual(
                rule["allOf"][1]["$ref"],
                f"#/$defs/{layer_name}EvidencePolicy",
            )
            policy = schema["$defs"][f"{layer_name}EvidencePolicy"]
            schema_kinds = policy["allOf"][0]["properties"]["evidence"]["items"][
                "properties"
            ]["kind"]["enum"]
            self.assertEqual(schema_kinds, list(kinds), layer_name)
            qualifying_kinds = policy["allOf"][1]["then"]["properties"][
                "evidence"
            ]["contains"]["properties"]["kind"]["enum"]
            self.assertEqual(qualifying_kinds, list(qualifying[layer_name]), layer_name)

        wrong_indexing = copy.deepcopy(self.baseline)
        wrong_indexing["layers"]["googleIndexing"]["evidence"][0][
            "kind"
        ] = "discovery_receipt"
        with self.assertRaisesRegex(
            measurement_baseline.ValidationError,
            "discovery_receipt.*googleIndexing",
        ):
            measurement_baseline.validate_baseline(wrong_indexing)

        wrong_activation = copy.deepcopy(self.baseline)
        wrong_activation["layers"]["usefulActivation"]["evidence"].append(
            {
                "kind": "site_event_batch",
                "observedAt": "2026-09-09T22:00:00Z",
                "reference": "synthetic-site-event-batch",
            }
        )
        with self.assertRaisesRegex(
            measurement_baseline.ValidationError,
            "site_event_batch.*usefulActivation",
        ):
            measurement_baseline.validate_baseline(wrong_activation)

        nonqualifying = copy.deepcopy(self.baseline)
        nonqualifying["layers"]["deployment"]["evidence"][0][
            "kind"
        ] = "repository_fixture"
        with self.assertRaisesRegex(
            measurement_baseline.ValidationError,
            "qualifying evidence.*deployment",
        ):
            measurement_baseline.validate_baseline(nonqualifying)

    def test_event_summary_cannot_be_observed_after_baseline_generation(self) -> None:
        invalid = copy.deepcopy(self.baseline)
        invalid["eventSummary"] = measurement_baseline.summarize_events(
            self.event_batch, self.registry
        )
        invalid["eventSummary"]["observedAt"] = "2026-09-10T01:05:01Z"
        with self.assertRaisesRegex(
            measurement_baseline.ValidationError,
            "eventSummary observedAt.*generatedAt",
        ):
            measurement_baseline.validate_baseline(invalid)

    def test_activity_segment_evidence_is_checked_for_each_observed_metric(self) -> None:
        expected = {
            "onsiteIntent": {
                segment: ("site_event_batch",)
                for segment in measurement_baseline.ACTIVITY_CLASSES
            },
            "actorExecution": {
                "unclassified": ("actor_analytics",),
                "owner_test": ("actor_analytics", "deployment_receipt"),
                "customer_activity": ("actor_analytics",),
            },
            "usefulActivation": {
                segment: ("activation_receipt",)
                for segment in measurement_baseline.ACTIVITY_CLASSES
            },
            "destinationDelivery": {
                segment: ("destination_receipt",)
                for segment in measurement_baseline.ACTIVITY_CLASSES
            },
            "retention": {
                segment: ("retention_report",)
                for segment in measurement_baseline.ACTIVITY_CLASSES
            },
            "commercial": {
                segment: ("commercial_report",)
                for segment in measurement_baseline.ACTIVITY_CLASSES
            },
            "support": {
                segment: ("support_ledger",)
                for segment in measurement_baseline.ACTIVITY_CLASSES
            },
        }
        for layer_name, segments in expected.items():
            self.assertEqual(
                measurement_baseline.LAYER_SEGMENT_QUALIFYING_EVIDENCE_KINDS[
                    layer_name
                ],
                segments,
            )

        owner_only = copy.deepcopy(self.baseline)
        owner_only["layers"]["actorExecution"]["evidence"][0][
            "kind"
        ] = "deployment_receipt"
        measurement_baseline.validate_baseline(owner_only)

        for segment in ("customer_activity", "unclassified"):
            with self.subTest(segment=segment):
                invalid = copy.deepcopy(owner_only)
                actor = invalid["layers"]["actorExecution"]
                customer = next(
                    metric
                    for metric in actor["metrics"]
                    if metric["name"] == "customerRuns"
                )
                customer.update(
                    {
                        "status": "observed",
                        "value": 1,
                        "reason": None,
                        "segment": segment,
                    }
                )
                actor["status"] = "observed"
                actor["reason"] = None
                with self.assertRaisesRegex(
                    measurement_baseline.ValidationError,
                    f"qualifying evidence.*actorExecution.*{segment}",
                ):
                    measurement_baseline.validate_baseline(invalid)

        schema = json.loads(
            (MEASUREMENT / "baseline-v1.schema.json").read_text(encoding="utf-8")
        )
        schema_segments = {
            "#/$defs/hasObservedUnclassifiedMetric": "unclassified",
            "#/$defs/hasObservedOwnerTestMetric": "owner_test",
            "#/$defs/hasObservedCustomerActivityMetric": "customer_activity",
        }
        for layer_name, expected_segments in expected.items():
            policy = schema["$defs"][f"{layer_name}EvidencePolicy"]
            segment_rules = {
                schema_segments[rule["if"]["$ref"]]: tuple(
                    rule["then"]["properties"]["evidence"]["contains"][
                        "properties"
                    ]["kind"]["enum"]
                )
                for rule in policy["allOf"][2:]
            }
            self.assertEqual(segment_rules, expected_segments, layer_name)

    def test_actor_execution_keeps_owner_test_evidence_separate(self) -> None:
        actor = self.baseline["layers"]["actorExecution"]
        self.assertEqual(actor["status"], "unknown")
        metrics = {(metric["name"], metric["segment"]): metric for metric in actor["metrics"]}
        self.assertEqual(metrics[("actorRuns", "owner_test")]["status"], "observed")
        self.assertEqual(metrics[("actorRuns", "owner_test")]["value"], 3)
        self.assertEqual(metrics[("customerRuns", "customer_activity")]["status"], "unknown")
        self.assertIsNone(metrics[("customerRuns", "customer_activity")]["value"])

    def test_observed_zero_is_not_unknown(self) -> None:
        demand = self.baseline["layers"]["searchDemand"]
        clicks = next(metric for metric in demand["metrics"] if metric["name"] == "clicks")
        self.assertEqual(demand["status"], "observed")
        self.assertEqual(clicks["value"], 0)
        self.assertIsNone(clicks["reason"])

        activation = self.baseline["layers"]["usefulActivation"]
        activations = activation["metrics"][0]
        self.assertEqual(activation["status"], "unknown")
        self.assertEqual(activations["status"], "unknown")
        self.assertIsNone(activations["value"])
        self.assertTrue(activations["reason"])

    def test_nullable_metrics_and_nonobserved_layers_require_reasons(self) -> None:
        missing_metric_reason = copy.deepcopy(self.baseline)
        missing_metric_reason["layers"]["usefulActivation"]["metrics"][0]["reason"] = None
        with self.assertRaisesRegex(measurement_baseline.ValidationError, "metric reason"):
            measurement_baseline.validate_baseline(missing_metric_reason)

        missing_layer_reason = copy.deepcopy(self.baseline)
        missing_layer_reason["layers"]["retention"]["reason"] = None
        with self.assertRaisesRegex(measurement_baseline.ValidationError, "layer reason"):
            measurement_baseline.validate_baseline(missing_layer_reason)

        observed_with_reason = copy.deepcopy(self.baseline)
        observed_with_reason["layers"]["searchDemand"]["metrics"][0]["reason"] = "zero"
        with self.assertRaisesRegex(measurement_baseline.ValidationError, "observed metric"):
            measurement_baseline.validate_baseline(observed_with_reason)

    def test_ratios_require_a_positive_denominator(self) -> None:
        invalid = copy.deepcopy(self.baseline)
        metric = invalid["layers"]["searchDemand"]["metrics"][2]
        self.assertEqual(metric["unit"], "ratio")
        metric["denominator"]["value"] = 0
        with self.assertRaisesRegex(measurement_baseline.ValidationError, "positive denominator"):
            measurement_baseline.validate_baseline(invalid)

    def test_ratio_denominator_is_an_observed_same_segment_metric(self) -> None:
        missing = copy.deepcopy(self.baseline)
        ratio = next(
            metric
            for metric in missing["layers"]["searchDemand"]["metrics"]
            if metric["unit"] == "ratio"
        )
        ratio["denominator"]["metric"] = "pageViews"
        with self.assertRaisesRegex(
            measurement_baseline.ValidationError,
            "denominator metric.*observed.*same layer and segment",
        ):
            measurement_baseline.validate_baseline(missing)

        wrong_segment = copy.deepcopy(self.baseline)
        ratio = next(
            metric
            for metric in wrong_segment["layers"]["searchDemand"]["metrics"]
            if metric["unit"] == "ratio"
        )
        ratio["segment"] = "unclassified"
        with self.assertRaisesRegex(
            measurement_baseline.ValidationError,
            "denominator metric.*observed.*same layer and segment",
        ):
            measurement_baseline.validate_baseline(wrong_segment)

        self_reference = copy.deepcopy(self.baseline)
        ratio = next(
            metric
            for metric in self_reference["layers"]["searchDemand"]["metrics"]
            if metric["unit"] == "ratio"
        )
        ratio["denominator"]["metric"] = ratio["name"]
        with self.assertRaisesRegex(
            measurement_baseline.ValidationError,
            "denominator metric.*observed count.*same layer and segment",
        ):
            measurement_baseline.validate_baseline(self_reference)

    def test_ratio_denominator_value_matches_referenced_metric(self) -> None:
        invalid = copy.deepcopy(self.baseline)
        ratio = next(
            metric
            for metric in invalid["layers"]["searchDemand"]["metrics"]
            if metric["unit"] == "ratio"
        )
        ratio["denominator"]["value"] = 99
        with self.assertRaisesRegex(
            measurement_baseline.ValidationError,
            "denominator value.*match.*impressions",
        ):
            measurement_baseline.validate_baseline(invalid)

    def test_count_metrics_reject_fractional_values(self) -> None:
        invalid = copy.deepcopy(self.baseline)
        metric = invalid["layers"]["deployment"]["metrics"][0]
        self.assertEqual(metric["unit"], "count")
        metric["value"] = 1.5
        with self.assertRaisesRegex(measurement_baseline.ValidationError, "integer"):
            measurement_baseline.validate_baseline(invalid)

    def test_missing_layer_and_owner_customer_pooling_fail(self) -> None:
        missing = copy.deepcopy(self.baseline)
        del missing["layers"]["support"]
        with self.assertRaisesRegex(measurement_baseline.ValidationError, "baseline layers"):
            measurement_baseline.validate_baseline(missing)

        pooled = copy.deepcopy(self.baseline)
        pooled["layers"]["actorExecution"]["metrics"][0]["segment"] = "mixed"
        with self.assertRaisesRegex(measurement_baseline.ValidationError, "segment"):
            measurement_baseline.validate_baseline(pooled)

    def test_build_and_cli_output_are_deterministic(self) -> None:
        first = measurement_baseline.build_baseline(
            self.baseline, self.registry, self.event_batch
        )
        second = measurement_baseline.build_baseline(
            copy.deepcopy(self.baseline), copy.deepcopy(self.registry), copy.deepcopy(self.event_batch)
        )
        self.assertEqual(first, second)
        self.assertEqual(first["eventSummary"]["uniqueCount"], 2)

        with TemporaryDirectory() as directory:
            first_path = Path(directory) / "first.json"
            second_path = Path(directory) / "second.json"
            for output in (first_path, second_path):
                result = measurement_baseline.main(
                    [
                        "build",
                        "--baseline",
                        str(BASELINE_PATH),
                        "--campaigns",
                        str(REGISTRY_PATH),
                        "--events",
                        str(EVENTS_PATH),
                        "--output",
                        str(output),
                    ]
                )
                self.assertEqual(result, 0)
            self.assertEqual(first_path.read_bytes(), second_path.read_bytes())
            self.assertEqual(json.loads(first_path.read_text(encoding="utf-8")), first)

    def test_readme_documents_boundaries_and_commands(self) -> None:
        readme = (MEASUREMENT / "README.md").read_text(encoding="utf-8")
        for phrase in (
            "observed zero",
            "not the same as unknown",
            "owner tests",
            "customer activity",
            "conflicting duplicate",
            "python3 scripts/measurement_baseline.py build",
            "does not prove activation",
            "qualifying evidence kinds",
            "same layer and segment",
        ):
            self.assertIn(phrase, readme)


if __name__ == "__main__":
    unittest.main()
