"""Regression tests for the checked Job Atlas Actor catalogue."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CATALOGUE_PATH = ROOT / "catalogue" / "actors-v1.json"
VALIDATOR_PATH = ROOT / "scripts" / "validate_actor_catalogue.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("actor_catalogue_validator", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ActorCatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = load_validator()
        cls.catalogue = json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))

    def assert_invalid(self, mutate, expected: str) -> None:
        candidate = copy.deepcopy(self.catalogue)
        mutate(candidate)
        errors = self.validator.validate_catalogue(candidate, ROOT)
        self.assertTrue(any(expected in error for error in errors), errors)

    def test_catalogue_is_closed_and_referentially_valid(self) -> None:
        self.assertEqual(self.validator.validate_catalogue(self.catalogue, ROOT), [])
        self.assertEqual(self.catalogue["schemaVersion"], "job-atlas-actor-catalogue-v1")
        self.assertEqual(self.catalogue["scope"]["inventoryCounts"]["ownedActors"], 64)
        self.assertEqual(self.catalogue["scope"]["inventoryCounts"]["inScopeDeployments"], 47)

    def test_all_source_and_live_candidates_have_one_disposition(self) -> None:
        deployments = self.catalogue["deployments"]
        exclusions = self.catalogue["excludedCandidates"]
        self.assertEqual(len(deployments), 47)
        self.assertEqual(len(exclusions), 18)
        identities = {
            (record["owner"], record["slug"], record["actorId"])
            for record in deployments + exclusions
        }
        self.assertEqual(len(identities), 65)
        self.assertEqual(
            sum(record["owner"] == "nomad-agent" for record in deployments + exclusions),
            61,
        )
        self.assertEqual(self.catalogue["scope"]["inventoryCounts"]["ownedPrivateSupportExcluded"], 3)
        for record in exclusions:
            self.assertEqual(record["category"], "unrelated-public")
            self.assertRegex(record["actorId"], r"^[A-Za-z0-9]{17}$")

    def test_logical_products_are_not_deployments(self) -> None:
        products = self.catalogue["logicalProducts"]
        deployments = self.catalogue["deployments"]
        self.assertEqual(len(products), 43)
        self.assertEqual({record["id"] for record in products}, {
            record["logicalProductId"] for record in deployments
        })
        for product in products:
            self.assertNotIn("actorId", product)
            self.assertNotIn("owner", product)
            self.assertNotIn("slug", product)
        copied = [record for record in deployments if record["relationship"] == "promoted-copy"]
        self.assertEqual(len(copied), 4)
        for record in copied:
            predecessor = next(
                item for item in deployments if item["id"] == record["relationshipTargetId"]
            )
            self.assertNotEqual(record["actorId"], predecessor["actorId"])

    def test_endpoint_states_require_live_observations(self) -> None:
        for deployment in self.catalogue["deployments"]:
            self.assertEqual(deployment["endpointState"], "live-metadata-verified")
            self.assertEqual(deployment["releaseSelector"], "latest")
            self.assertRegex(deployment["latestObservation"]["buildNumber"], r"^\d+\.\d+\.\d+$")
            self.assertRegex(deployment["latestObservation"]["buildId"], r"^[A-Za-z0-9]{17}$")

        self.assert_invalid(
            lambda data: data["deployments"][0].update(endpointState="proposed"),
            "endpointState",
        )

    def test_every_maintained_route_and_actor_id_is_catalogued(self) -> None:
        errors = self.validator.validate_repository_routes(self.catalogue, ROOT)
        self.assertEqual(errors, [])
        extract = self.validator.extract_actor_routes
        sample = (
            "https://apify.com/job-atlas/linkedin-enrich-translate-normalize-scraper "
            "job-atlas~ai-job-fit-scorer "
            "job-atlas%2Feuraxess-enrich-translate-normalize-scraper"
        )
        self.assertEqual(
            extract(sample),
            {
                "job-atlas/linkedin-enrich-translate-normalize-scraper",
                "job-atlas/ai-job-fit-scorer",
                "job-atlas/euraxess-enrich-translate-normalize-scraper",
            },
        )

    def test_client_matrix_is_complete_and_assets_exist(self) -> None:
        expected_classes = {
            "api-sdk", "mcp", "n8n", "make", "zapier", "airtable",
            "agent-skill", "python",
        }
        promoted = {
            record["logicalProductId"]
            for record in self.catalogue["deployments"]
            if record["relationship"] == "promoted-copy"
        }
        rows = self.catalogue["clientMatrix"]
        self.assertEqual(
            {(row["logicalProductId"], row["clientClass"]) for row in rows},
            {(product, client) for product in promoted for client in expected_classes},
        )
        for row in rows:
            if row["support"] in {"maintained", "documented-only", "destination-only"}:
                self.assertTrue(row["assets"], row)
                for asset in row["assets"]:
                    self.assertTrue((ROOT / asset).is_file(), asset)
            else:
                self.assertTrue(row["gap"], row)

    def test_external_state_matrix_names_all_gaps_and_rollback(self) -> None:
        expected = {
            "saved-tasks", "webhooks", "imports", "schedules",
            "billing-subscriptions", "credentials", "named-destinations",
        }
        rows = self.catalogue["externalStateMatrix"]
        self.assertEqual({row["class"] for row in rows}, expected)
        for row in rows:
            self.assertTrue(row["action"])
            self.assertTrue(row["verification"])
            self.assertTrue(row["rollback"])
            self.assertTrue(row["gaps"])

    def test_contract_profiles_preserve_identity_and_empty_value_semantics(self) -> None:
        profiles = {record["id"]: record for record in self.catalogue["contractProfiles"]}
        jobs = profiles["normalized-job-v1"]
        self.assertEqual(jobs["canonicalRoots"], ["schemaVersion", "identity", "data", "custom", "llm", "raw"])
        self.assertEqual(jobs["postingKey"]["primary"], "{source}:{externalId}")
        self.assertEqual(jobs["postingKey"]["fallback"], "{source}:{url}")
        self.assertIn("null", jobs["emptyValueSemantics"])
        self.assertIn("[]", jobs["emptyValueSemantics"])
        self.assertIn("raw: null", jobs["emptyValueSemantics"])
        scorer = profiles["job-fit-v1"]
        self.assertEqual(scorer["postingKey"], "jobKey")
        self.assertEqual(scorer["destinationKey"], "matchKey")

    def test_latest_is_a_selector_not_immutable_identity(self) -> None:
        for deployment in self.catalogue["deployments"]:
            self.assertEqual(deployment["releaseSelector"], "latest")
            self.assertNotEqual(deployment["latestObservation"]["buildId"], "latest")
            self.assertNotEqual(deployment["latestObservation"]["buildNumber"], "latest")

    def test_schema_invalid_enums_and_ids_fail_closed(self) -> None:
        self.assert_invalid(
            lambda data: data["logicalProducts"][0].update(kind="unknown-kind"),
            "kind",
        )
        self.assert_invalid(
            lambda data: data["deployments"][0]["latestObservation"].update(sourceType="ZIP"),
            "sourceType",
        )
        self.assert_invalid(
            lambda data: data["deployments"][0].update(actorId="too-short"),
            "actorId",
        )
        self.assert_invalid(
            lambda data: data["excludedCandidates"][0].update(category="private-support"),
            "category",
        )

    def test_every_schema_object_is_closed(self) -> None:
        schema = json.loads(
            (ROOT / "catalogue" / "actors-v1.schema.json").read_text(encoding="utf-8")
        )
        pending = [schema]
        while pending:
            node = pending.pop()
            if isinstance(node, dict):
                if node.get("type") == "object":
                    self.assertIs(node.get("additionalProperties"), False, node)
                pending.extend(node.values())
            elif isinstance(node, list):
                pending.extend(node)


if __name__ == "__main__":
    unittest.main()
