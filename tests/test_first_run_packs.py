from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.validate_first_run_packs import (
    ValidationError,
    validate_all,
    validate_pack,
)


ROOT = Path(__file__).resolve().parents[1]
PACKS_DIR = ROOT / "first-run" / "packs"
VALIDATOR = ROOT / "scripts" / "validate_first_run_packs.py"

EXPECTED = {
    "linkedin": {
        "slug": "linkedin-enrich-translate-normalize-scraper",
        "actor_id": "KMflYVTHiIAXE6nKN",
        "sample_source": "linkedin",
        "evidence_class": "illustrative_fixture",
        "max_charge": 0.10,
        "statuses": {"succeeded", "empty", "empty-limited", "partial"},
    },
    "euraxess": {
        "slug": "euraxess-enrich-translate-normalize-scraper",
        "actor_id": "Slu3SAWULLRYnCN9Y",
        "sample_source": "euraxess",
        "evidence_class": "recorded_source_result",
        "max_charge": 0.05,
        "statuses": {"succeeded", "empty", "empty-limited", "partial"},
    },
    "ycombinator": {
        "slug": "ycombinator-enrich-translate-normalize-scraper",
        "actor_id": "pF4Lk4ifzb9tZXg7K",
        "sample_source": "ycombinator_was",
        "evidence_class": "illustrative_fixture",
        "max_charge": 0.05,
        "statuses": {"succeeded", "empty", "empty-limited", "partial"},
    },
    "ai-job-fit-scorer": {
        "slug": "ai-job-fit-scorer",
        "actor_id": "OZ919PaAyAbifOdcL",
        "sample_source": "linkedin",
        "evidence_class": "historical_predecessor_run",
        "max_charge": 0.10,
        "statuses": {"complete", "partial", "empty"},
    },
}

SCRAPER_PACKS = {"linkedin", "euraxess", "ycombinator"}
REQUIRED_CHECKS = {
    "terminal_succeeded",
    "resolved_build_identity",
    "same_run_storages",
    "summary_schema",
    "dataset_count",
    "row_schema",
    "row_source",
    "settled_cost",
}


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def feature_is_off(actor_input: dict[str, object], name: str) -> bool:
    value = actor_input.get(name, False)
    if isinstance(value, dict):
        return value.get("enabled") is False
    return value is False


class FirstRunPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pack_paths = {
            path.stem: path for path in sorted(PACKS_DIR.glob("*.json"))
        }
        cls.packs = {
            pack_id: load_json(path) for pack_id, path in cls.pack_paths.items()
        }

    def assert_rejected(self, value: dict[str, object]) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pack.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaises(ValidationError):
                validate_pack(path)

    def test_inventory_identities_and_routes_are_exact(self) -> None:
        self.assertEqual(set(self.packs), set(EXPECTED))
        for pack_id, expected in EXPECTED.items():
            with self.subTest(pack=pack_id):
                pack = self.packs[pack_id]
                slug = expected["slug"]
                actor = pack["actor"]
                proposal = pack["approvalProposal"]

                self.assertEqual(pack["packId"], pack_id)
                self.assertEqual(actor["slug"], slug)
                self.assertEqual(actor["immutableActorId"], expected["actor_id"])
                self.assertEqual(actor["apiActorId"], f"job-atlas~{slug}")
                self.assertEqual(actor["storeUrl"], f"https://apify.com/job-atlas/{slug}")
                self.assertEqual(
                    pack["product"]["websiteUrl"],
                    f"https://jobatlas.dev/actors/{pack_id}",
                )
                self.assertEqual(actor["buildSelector"], "latest")
                self.assertEqual(proposal["buildSelector"], "latest")
                endpoint_segment = "actors" if pack_id == "ai-job-fit-scorer" else "acts"
                self.assertEqual(
                    proposal["endpoint"],
                    f"https://api.apify.com/v2/{endpoint_segment}/"
                    f"job-atlas~{slug}/runs",
                )

    def test_inputs_are_bounded_and_declared_features_are_off(self) -> None:
        for pack_id, pack in self.packs.items():
            with self.subTest(pack=pack_id):
                starter = pack["starter"]
                proposal = pack["approvalProposal"]
                actor_input = load_json(ROOT / starter["inputPath"])

                self.assertEqual(actor_input["maxItems"], starter["maxItems"])
                self.assertEqual(starter["maxItems"], 5)
                self.assertEqual(proposal["maxItems"], starter["maxItems"])
                self.assertEqual(
                    proposal["maxTotalChargeUsd"], starter["maxTotalChargeUsd"]
                )
                self.assertEqual(
                    starter["maxTotalChargeUsd"], EXPECTED[pack_id]["max_charge"]
                )
                self.assertLessEqual(starter["maxTotalChargeUsd"], 0.10)

                for feature in starter["optionalPaidFeaturesDisabled"]:
                    self.assertTrue(feature_is_off(actor_input, feature), feature)
                for feature in starter["statefulFeaturesDisabled"]:
                    self.assertTrue(feature_is_off(actor_input, feature), feature)

                if pack_id in SCRAPER_PACKS:
                    self.assertEqual(
                        actor_input["schemaVersion"],
                        "nomad-agent-job-search-input-v1",
                    )
                    self.assertFalse(actor_input["translateToEnglish"])
                    self.assertFalse(actor_input["aiEnrichment"]["enabled"])
                    self.assertFalse(actor_input["dedupe"]["enabled"])
                    self.assertFalse(actor_input["analyticsEnabled"])
                else:
                    self.assertEqual(actor_input["mode"], "search")
                    self.assertEqual(actor_input["resultMode"], "shortlist")
                    self.assertFalse(actor_input["recoverHolds"])
                    self.assertLessEqual(actor_input["search"]["maxItemsPerSource"], 3)

    def test_referenced_hashes_and_approval_input_match(self) -> None:
        for pack_id, pack in self.packs.items():
            with self.subTest(pack=pack_id):
                starter = pack["starter"]
                sample = pack["sample"]
                completion = pack["completion"]
                proposal = pack["approvalProposal"]

                self.assertEqual(
                    sha256(ROOT / starter["inputPath"]), starter["inputSha256"]
                )
                self.assertEqual(
                    sha256(ROOT / sample["recordPath"]), sample["recordSha256"]
                )
                self.assertEqual(
                    sha256(ROOT / sample["rowSchemaPath"]),
                    sample["rowSchemaSha256"],
                )
                self.assertEqual(
                    sha256(ROOT / completion["runSummarySchemaPath"]),
                    completion["runSummarySchemaSha256"],
                )
                if sample["sourceExtensionSchemaPath"] is None:
                    self.assertIsNone(sample["sourceExtensionSchemaSha256"])
                    self.assertIsNone(sample["sourceExtensionSchemaVersion"])
                else:
                    self.assertEqual(
                        sha256(ROOT / sample["sourceExtensionSchemaPath"]),
                        sample["sourceExtensionSchemaSha256"],
                    )

                self.assertEqual(proposal["inputPath"], starter["inputPath"])
                self.assertEqual(proposal["inputSha256"], starter["inputSha256"])

    def test_samples_keep_source_and_evidence_provenance(self) -> None:
        for pack_id, pack in self.packs.items():
            with self.subTest(pack=pack_id):
                sample_meta = pack["sample"]
                sample = load_json(ROOT / sample_meta["recordPath"])
                expected = EXPECTED[pack_id]

                self.assertEqual(sample_meta["sampleSource"], expected["sample_source"])
                self.assertEqual(
                    sample_meta["evidenceClass"], expected["evidence_class"]
                )
                self.assertTrue(sample_meta["notProofOf"])
                if sample_meta["evidenceClass"] == "illustrative_fixture":
                    self.assertIsNone(sample_meta["observedAt"])
                else:
                    self.assertIsNotNone(sample_meta["observedAt"])

                if pack_id == "ai-job-fit-scorer":
                    self.assertEqual(sample["source"], expected["sample_source"])
                    self.assertEqual(
                        sample["job"]["identity"]["source"],
                        expected["sample_source"],
                    )
                else:
                    self.assertEqual(
                        sample["identity"]["source"], expected["sample_source"]
                    )

    def test_ycombinator_sample_exercises_the_v2_extension(self) -> None:
        pack = self.packs["ycombinator"]
        sample = load_json(ROOT / pack["sample"]["recordPath"])
        required_custom_fields = {
            "companyBatch",
            "companySlug",
            "locationRaw",
            "jobTypeRaw",
            "equityRaw",
            "visaPolicyRaw",
            "skills",
            "interviewProcessHtml",
            "customQuestions",
            "company",
        }

        self.assertEqual(pack["sample"]["sourceExtensionSchemaVersion"], "ycombinator-v2")
        self.assertEqual(set(sample["custom"]["data"]), required_custom_fields)

        invalid = copy.deepcopy(sample)
        invalid["custom"]["data"].pop("company")
        with self.assertRaises(ValidationError):
            validate_pack(self.pack_paths["ycombinator"], sample_override=invalid)

    def test_public_api_accepts_valid_object_overrides(self) -> None:
        for pack_id, pack in self.packs.items():
            with self.subTest(pack=pack_id):
                validate_pack(
                    self.pack_paths[pack_id],
                    input_override=load_json(ROOT / pack["starter"]["inputPath"]),
                    sample_override=load_json(ROOT / pack["sample"]["recordPath"]),
                )

    def test_wrong_input_and_sample_sources_are_rejected(self) -> None:
        linkedin = self.packs["linkedin"]
        invalid_input = load_json(ROOT / linkedin["starter"]["inputPath"])
        invalid_input["maxItems"] = 6
        with self.assertRaises(ValidationError):
            validate_pack(
                self.pack_paths["linkedin"], input_override=invalid_input
            )

        paid_input = load_json(ROOT / linkedin["starter"]["inputPath"])
        paid_input["aiEnrichment"]["enabled"] = True
        with self.assertRaises(ValidationError):
            validate_pack(
                self.pack_paths["linkedin"], input_override=paid_input
            )

        invalid_sample = load_json(ROOT / linkedin["sample"]["recordPath"])
        invalid_sample["identity"]["source"] = "euraxess"
        with self.assertRaises(ValidationError):
            validate_pack(
                self.pack_paths["linkedin"], sample_override=invalid_sample
            )

    def test_source_specific_input_contracts_fail_closed(self) -> None:
        euraxess = self.packs["euraxess"]
        invalid_euraxess = load_json(ROOT / euraxess["starter"]["inputPath"])
        invalid_euraxess["postedWithin"] = "1h"
        with self.assertRaises(ValidationError):
            validate_pack(
                self.pack_paths["euraxess"],
                input_override=invalid_euraxess,
            )

        ycombinator = self.packs["ycombinator"]
        invalid_yc = load_json(ROOT / ycombinator["starter"]["inputPath"])
        invalid_yc["ycSearch"]["queries"] = [123]
        with self.assertRaises(ValidationError):
            validate_pack(
                self.pack_paths["ycombinator"],
                input_override=invalid_yc,
            )
        conflicting_yc = load_json(ROOT / ycombinator["starter"]["inputPath"])
        conflicting_yc["keyword"] = "founding engineer"
        with self.assertRaises(ValidationError):
            validate_pack(
                self.pack_paths["ycombinator"],
                input_override=conflicting_yc,
            )

        scorer = self.packs["ai-job-fit-scorer"]
        invalid_scorer = load_json(ROOT / scorer["starter"]["inputPath"])
        invalid_scorer["search"].pop("keywords")
        invalid_scorer["search"]["sources"] = ["not_a_source"]
        with self.assertRaises(ValidationError):
            validate_pack(
                self.pack_paths["ai-job-fit-scorer"],
                input_override=invalid_scorer,
            )

    def test_wrong_route_build_hash_cost_retry_and_checks_are_rejected(self) -> None:
        mutations = {
            "route": lambda value: value["actor"].update(
                apiActorId="job-atlas~euraxess-enrich-translate-normalize-scraper"
            ),
            "build": lambda value: value["actor"]["datedPublicReadback"].update(
                buildId="x0bGueGFnm6eEGY3K"
            ),
            "hash": lambda value: value["starter"].update(inputSha256="0" * 64),
            "cost": lambda value: value["approvalProposal"].update(
                maxTotalChargeUsd=0.09
            ),
            "reviewed-cap": lambda value: (
                value["starter"].update(maxTotalChargeUsd=0.09),
                value["approvalProposal"].update(maxTotalChargeUsd=0.09),
            ),
            "disabled-feature-list": lambda value: value["starter"][
                "optionalPaidFeaturesDisabled"
            ].remove("aiEnrichment"),
            "related-count": lambda value: value["relatedExecutionEvidence"].update(
                datasetRows=3
            ),
            "retry": lambda value: value["approvalProposal"].update(
                maxFollowUpRuns=1
            ),
            "checks": lambda value: value["approvalProposal"]["checks"].remove(
                "dataset_count"
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(case=label):
                invalid = copy.deepcopy(self.packs["linkedin"])
                mutate(invalid)
                self.assert_rejected(invalid)

    def test_completion_checks_cover_receipt_count_retry_and_cost(self) -> None:
        receipt_fields = {
            "id",
            "buildId",
            "buildNumber",
            "defaultDatasetId",
            "defaultKeyValueStoreId",
            "status",
            "exitCode",
        }
        for pack_id, pack in self.packs.items():
            with self.subTest(pack=pack_id):
                completion = pack["completion"]
                checks = set(pack["approvalProposal"]["checks"])
                self.assertEqual(
                    set(completion["requiredRunReceiptFields"]), receipt_fields
                )
                self.assertTrue(REQUIRED_CHECKS <= checks)
                self.assertEqual(pack["approvalProposal"]["maxFollowUpRuns"], 0)
                self.assertIn("Do not", completion["retryRule"])
                self.assertIn("settled", completion["costRule"].lower())
                self.assertIn(
                    completion["datasetCountField"],
                    {"delivered", "counts.outputRows"},
                )
                self.assertEqual(
                    set(completion["usableSummaryStatuses"]),
                    EXPECTED[pack_id]["statuses"],
                )

    def test_root_and_product_pages_link_the_versioned_packs(self) -> None:
        pack_index = ROOT / "first-run" / "README.md"
        self.assertTrue(pack_index.is_file())
        root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("(first-run/README.md)", root_readme)

        index_text = pack_index.read_text(encoding="utf-8")
        common_url = "https://github.com/Exdenta/jobatlas/blob/main/first-run/README.md"
        for pack_id in EXPECTED:
            with self.subTest(pack=pack_id):
                self.assertIn(f"packs/{pack_id}.json", index_text)
                page = (
                    ROOT / "website" / "actors" / pack_id / "index.html"
                ).read_text(encoding="utf-8")
                self.assertIn(
                    "https://github.com/Exdenta/jobatlas/blob/main/"
                    f"first-run/packs/{pack_id}.json",
                    page,
                )
                self.assertIn(common_url, page)

    def test_validate_all_and_cli_emit_deterministic_json(self) -> None:
        validate_all()
        commands = []
        for _ in range(2):
            commands.append(
                subprocess.run(
                    [sys.executable, str(VALIDATOR)],
                    cwd=ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
            )
        for result in commands:
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(commands[0].stdout, commands[1].stdout)
        payload = json.loads(commands[0].stdout)
        serialized = json.dumps(payload, sort_keys=True)
        for pack_id in EXPECTED:
            self.assertIn(pack_id, serialized)


if __name__ == "__main__":
    unittest.main(verbosity=2)
