"""Regression tests for the checked Job Atlas Actor catalogue."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest
import tempfile


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
        self.assertEqual(self.catalogue["scope"]["inventoryCounts"]["ownedActors"], 92)
        self.assertEqual(self.catalogue["scope"]["inventoryCounts"]["inScopeDeployments"], len(self.catalogue["deployments"]))

    def test_all_source_and_live_candidates_have_one_disposition(self) -> None:
        deployments = self.catalogue["deployments"]
        exclusions = self.catalogue["excludedCandidates"]
        self.assertEqual(len(deployments), self.catalogue["scope"]["inventoryCounts"]["inScopeDeployments"])
        self.assertEqual(len(exclusions), 18)
        identities = {
            (record["owner"], record["slug"], record["actorId"])
            for record in deployments + exclusions
        }
        self.assertEqual(len(identities), len(deployments) + len(exclusions))
        self.assertEqual(
            sum(record["owner"] == "nomad-agent" for record in deployments + exclusions),
            76,
        )
        self.assertEqual(self.catalogue["scope"]["inventoryCounts"]["ownedPrivateSupportExcluded"], 16)
        for record in exclusions:
            self.assertEqual(record["category"], "unrelated-public")
            self.assertRegex(record["actorId"], r"^[A-Za-z0-9]{17}$")

    def test_logical_products_are_not_deployments(self) -> None:
        products = self.catalogue["logicalProducts"]
        deployments = self.catalogue["deployments"]
        self.assertEqual(len(products), 58)
        self.assertEqual({record["id"] for record in products}, {
            record["logicalProductId"] for record in deployments
        })
        for product in products:
            self.assertNotIn("actorId", product)
            self.assertNotIn("owner", product)
            self.assertNotIn("slug", product)
        copied = [record for record in deployments if record["relationship"] == "promoted-copy"]
        self.assertEqual(len(copied), self.catalogue["scope"]["inventoryCounts"]["promotedJobAtlasDeployments"])
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
            "https://apify.com/jobatlas/linkedin-enrich-translate-normalize-scraper "
            "jobatlas~ai-job-fit-scorer "
            "jobatlas%2Feuraxess-enrich-translate-normalize-scraper "
            "https://github.com/Exdenta/jobatlas/blob/main/docs/linkedin.md"
        )
        self.assertEqual(
            extract(sample),
            {
                "jobatlas/linkedin-enrich-translate-normalize-scraper",
                "jobatlas/ai-job-fit-scorer",
                "jobatlas/euraxess-enrich-translate-normalize-scraper",
            },
        )

    def test_verified_primary_routes_do_not_require_an_integration_template(self) -> None:
        primary = next(d for d in self.catalogue["deployments"] if d["owner"] == "nomad-agent")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "README.md"
            path.write_text(f'https://apify.com/{primary["owner"]}/{primary["slug"]}')
            data = copy.deepcopy(self.catalogue)
            data["clientMatrix"] = []
            self.assertEqual(self.validator.validate_repository_routes(data, root), [])
            data["deployments"] = [d for d in data["deployments"] if d["id"] != primary["id"]]
            self.assertTrue(self.validator.validate_repository_routes(data, root))
            path.write_text("https://apify.com/job-atlas/ai-job-fit-scorer")
            self.assertTrue(any("retired Apify owner" in e for e in self.validator.validate_repository_routes(self.catalogue, root)))

    def test_public_directory_covers_only_catalogued_public_endpoints(self) -> None:
        directory = json.loads((ROOT / "docs/public-actors.json").read_text())
        self.assertEqual(directory["schemaVersion"], "public-actor-directory-v1")
        expected = {
            (row["owner"], row["slug"], row["actorId"])
            for row in self.catalogue["deployments"] + self.catalogue["excludedCandidates"]
        }
        actual = {(row["owner"], row["slug"], row["actorId"]) for row in directory["actors"]}
        self.assertEqual(actual, expected)
        self.assertEqual(len(directory["actors"]), len(expected))
        prose = (ROOT / "docs/public-actors.md").read_text()
        for row in directory["actors"]:
            self.assertIn(row["url"], prose)
            self.assertGreater(len(row["description"]), 40)
            self.assertNotIn("private-collector", row["slug"])
            self.assertNotIn("private" + " collector", row["description"].lower())

    def test_non_job_directory_does_not_authorize_integration_routes(self) -> None:
        excluded = self.catalogue["excludedCandidates"][0]
        route = f'https://apify.com/{excluded["owner"]}/{excluded["slug"]}'
        text = route + ' "actorId": "' + excluded["actorId"] + '"'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "docs/public-actors.md").write_text(text)
            self.assertEqual(self.validator.validate_repository_routes(self.catalogue, root), [])
            (root / "README.md").write_text(text)
            (root / "docs/actors").mkdir()
            (root / f'docs/actors/{excluded["slug"]}.md').write_text(text)
            self.assertEqual(self.validator.validate_repository_routes(self.catalogue, root), [])
            (root / "integrations").mkdir()
            (root / "integrations/caller.py").write_text(text)
            errors = self.validator.validate_repository_routes(self.catalogue, root)
            self.assertTrue(any("uncatalogued maintained Actor route" in error for error in errors))
            self.assertTrue(any("uncatalogued maintained Actor ID" in error for error in errors))

    def test_public_guides_require_catalogued_identity_and_exact_path(self) -> None:
        excluded = self.catalogue["excludedCandidates"][0]
        route = f'https://apify.com/{excluded["owner"]}/{excluded["slug"]}'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs/actors").mkdir(parents=True)
            (root / "docs/actors/uncatalogued.md").write_text(route)
            (root / "README.md").write_text("https://apify.com/nomad-agent/unknown-actor")
            errors = self.validator.validate_repository_routes(self.catalogue, root)
            self.assertEqual(len(errors), 2)
            self.assertTrue(all("uncatalogued maintained Actor route" in error for error in errors))

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

    def test_observed_counts_reject_each_inconsistent_total(self) -> None:
        for field in self.catalogue["scope"]["inventoryCounts"]:
            with self.subTest(field=field):
                self.assert_invalid(
                    lambda data, field=field: data["scope"]["inventoryCounts"].update(
                        {field: data["scope"]["inventoryCounts"][field] + 1}
                    ),
                    "inventoryCounts mismatch",
                )

    def test_another_observed_mirror_does_not_require_a_hardcoded_count(self) -> None:
        candidate = copy.deepcopy(self.catalogue)
        mirror = copy.deepcopy(next(d for d in candidate["deployments"] if d["owner"] == "jobatlas"))
        mirror["slug"] += "-test"
        mirror["id"] = "jobatlas--" + mirror["slug"]
        mirror["actorId"] = "ZZZZZZZZZZZZZZZZZ"
        candidate["deployments"].append(mirror)
        counts = candidate["scope"]["inventoryCounts"]
        counts["promotedJobAtlasDeployments"] += 1
        counts["inScopeDeployments"] += 1
        self.assertEqual(self.validator.validate_catalogue(candidate, ROOT), [])

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
