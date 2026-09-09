"""Regression tests for the approval-gated Apify Store copy package."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CATALOGUE_PATH = ROOT / "catalogue" / "actors-v1.json"
MANIFEST_PATH = ROOT / "catalogue" / "listing-disposition-v1.json"
GENERATOR_PATH = ROOT / "scripts" / "generate_apify_listing_disposition.py"
DOCS = ROOT / "docs" / "apify-store"

DRAFTS = {
    "linkedin-enrich-translate-normalize-scraper": (
        "KMflYVTHiIAXE6nKN",
        "/actors/linkedin",
        "up to 1,000 LinkedIn jobs per run",
        "Airtable is a destination projection only; no Zapier workflow is claimed.",
    ),
    "euraxess-enrich-translate-normalize-scraper": (
        "Slu3SAWULLRYnCN9Y",
        "/actors/euraxess",
        "up to 200 EURAXESS research jobs per run",
        "Airtable is a post-run destination projection only. No Zapier workflow is claimed.",
    ),
    "ycombinator-enrich-translate-normalize-scraper": (
        "pF4Lk4ifzb9tZXg7K",
        "/actors/ycombinator",
        "up to 1,000 Y Combinator startup jobs per run",
        "API and MCP have documented bounded examples only. No n8n, Make, Zapier, Airtable, or Python client is claimed",
    ),
    "ai-job-fit-scorer": (
        "OZ919PaAyAbifOdcL",
        "/actors/ai-job-fit-scorer",
        "score up to 200 supplied jobs for one candidate",
        "No Airtable asset is claimed.",
    ),
}


def load_generator():
    spec = importlib.util.spec_from_file_location("listing_disposition", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ApifyStoreCopyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalogue = json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.generator = load_generator()

    def test_disposition_is_reproducible_from_catalogue_and_bounded_delta(self) -> None:
        self.assertEqual(self.manifest, self.generator.build_manifest(self.catalogue))
        self.assertEqual(self.manifest["scope"]["accountedLogicalProducts"], 44)
        self.assertEqual(self.manifest["scope"]["accountedDeployments"], 48)

    def test_every_product_and_deployment_has_exactly_one_disposition(self) -> None:
        products = self.manifest["logicalProducts"]
        deployments = self.manifest["deployments"]
        self.assertEqual(len({row["logicalProductId"] for row in products}), 44)
        self.assertEqual(len({row["deploymentId"] for row in deployments}), 48)
        self.assertTrue(all(row["migrationProposed"] is False for row in products + deployments))
        delta = self.manifest["scope"]["knownPostBaselineDelta"]
        known_products = {row["id"] for row in delta if row["kind"] == "logical-product"}
        known_deployments = {row["id"] for row in delta if row["kind"] == "deployment"}
        catalogue_products = {row["id"] for row in self.catalogue["logicalProducts"]}
        catalogue_deployments = {row["id"] for row in self.catalogue["deployments"]}
        self.assertEqual(
            {row["logicalProductId"] for row in products},
            catalogue_products | known_products,
        )
        self.assertEqual(
            {row["deploymentId"] for row in deployments},
            catalogue_deployments | known_deployments,
        )

    def test_only_four_existing_job_atlas_listings_receive_drafts(self) -> None:
        deployments = self.manifest["deployments"]
        promoted = [row for row in deployments if row["owner"] == "job-atlas"]
        legacy = [row for row in deployments if row["owner"] == "nomad-agent"]
        self.assertEqual(len(promoted), 4)
        self.assertEqual(len(legacy), 44)
        self.assertTrue(all(row["action"] == "draft-listing-copy" for row in promoted))
        self.assertTrue(all(row["action"] == "no-listing-change" for row in legacy))
        self.assertTrue(all(row["listingDraft"] is None for row in legacy))
        for row in promoted:
            self.assertTrue((ROOT / row["listingDraft"]).is_file(), row)

    def test_listing_drafts_pin_identity_limits_support_and_reciprocal_links(self) -> None:
        for slug, (actor_id, website_path, limit, support) in DRAFTS.items():
            document = (DOCS / "actors" / f"{slug}.md").read_text(encoding="utf-8")
            with self.subTest(slug=slug):
                self.assertIn(f"Target: `job-atlas/{slug}`", document)
                self.assertIn(f"Actor ID: `{actor_id}`", document)
                self.assertIn(f"https://jobatlas.dev{website_path}", document)
                self.assertIn(limit, document)
                self.assertIn(support, document)
                self.assertIn("https://github.com/Exdenta/jobatlas", document)
                self.assertIn("`latest` selector warning", document)
                self.assertIn("Recheck the live Pricing tab before publication.", document)
                self.assertIn("approval-gated local draft", document)
                if slug in {
                    "euraxess-enrich-translate-normalize-scraper",
                    "ycombinator-enrich-translate-normalize-scraper",
                }:
                    self.assertIn(
                        "https://raw.githubusercontent.com/Exdenta/nomad-agent-job-scrapers",
                        document,
                    )
                    self.assertIn(
                        "https://raw.githubusercontent.com/Exdenta/jobatlas",
                        document,
                    )

    def test_publisher_draft_links_exactly_the_four_promoted_actors(self) -> None:
        document = (DOCS / "publisher-profile.md").read_text(encoding="utf-8")
        self.assertIn("https://jobatlas.dev/", document)
        self.assertIn("https://github.com/Exdenta/jobatlas", document)
        for slug in DRAFTS:
            self.assertIn(f"https://apify.com/job-atlas/{slug}", document)
        self.assertEqual(document.count("https://apify.com/job-atlas/"), 4)
        self.assertNotIn("monthly users", document.lower())
        self.assertNotIn("runs succeeded", document.lower())

    def test_support_matrix_is_copied_without_strengthening(self) -> None:
        expected = {
            (row["logicalProductId"], row["clientClass"], row["support"])
            for row in self.catalogue["clientMatrix"]
        }
        actual = {
            (row["logicalProductId"], row["clientClass"], row["support"])
            for row in self.manifest["clientSupport"]
        }
        self.assertEqual(actual, expected)

    def test_repository_readme_has_all_reciprocal_guides_and_support_boundaries(self) -> None:
        document = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("The LinkedIn, Y Combinator, and EURAXESS Actors", document)
        self.assertIn("[Y Combinator jobs](https://jobatlas.dev/actors/ycombinator)", document)
        self.assertIn("YC API and MCP examples are documented-only", document)
        self.assertIn("standalone assets are maintained", document)
        self.assertIn("Airtable is a destination projection only", document)
        self.assertIn("No Airtable asset is claimed for the scorer", document)
        self.assertNotIn("destination templates untested", document)


if __name__ == "__main__":
    unittest.main()
