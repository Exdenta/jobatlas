#!/usr/bin/env python3
"""Generate the approval-gated Apify Store listing disposition manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOGUE_PATH = ROOT / "catalogue" / "actors-v1.json"
OUTPUT_PATH = ROOT / "catalogue" / "listing-disposition-v1.json"
OBSERVED_AT = "2026-09-09T01:19:34+02:00"
SOURCE_REVISION = "348f2f32f9c23f52afecaefcfd9f0db43c5cb4fb"

DRAFTS = {
    "linkedin-enrich-translate-normalize-scraper": "docs/apify-store/actors/linkedin-enrich-translate-normalize-scraper.md",
    "euraxess-enrich-translate-normalize-scraper": "docs/apify-store/actors/euraxess-enrich-translate-normalize-scraper.md",
    "ycombinator-enrich-translate-normalize-scraper": "docs/apify-store/actors/ycombinator-enrich-translate-normalize-scraper.md",
    "ai-job-fit-scorer": "docs/apify-store/actors/ai-job-fit-scorer.md",
}

# This product was added by a concurrent, uncommitted catalogue refresh while
# S03 was isolated at SOURCE_REVISION. Keeping the bounded delta here accounts
# for the current fleet without copying or overwriting that checkout's changes.
KNOWN_POST_BASELINE = {
    "product": {
        "id": "foorilla-ai-jobs-scraper",
        "name": "Foorilla Data, AI, and Machine Learning jobs",
        "promotion": "not-planned",
    },
    "deployment": {
        "id": "nomad-agent--foorilla-ai-jobs-scraper",
        "logicalProductId": "foorilla-ai-jobs-scraper",
        "owner": "nomad-agent",
        "relationship": "legacy-primary",
    },
}


def _product_disposition(product: dict[str, Any], catalogue_state: str) -> dict[str, Any]:
    promoted = product["promotion"] == "job-atlas"
    return {
        "logicalProductId": product["id"],
        "name": product["name"],
        "catalogueState": catalogue_state,
        "promotion": product["promotion"],
        "action": "draft-listing-copy" if promoted else "no-listing-change",
        "migrationProposed": False,
        "supportClaim": "catalogue-client-matrix" if promoted else "none",
        "listingDraft": DRAFTS.get(product["id"]),
    }


def _deployment_disposition(deployment: dict[str, Any], catalogue_state: str) -> dict[str, Any]:
    promoted_copy = deployment["owner"] == "job-atlas"
    return {
        "deploymentId": deployment["id"],
        "logicalProductId": deployment["logicalProductId"],
        "catalogueState": catalogue_state,
        "owner": deployment["owner"],
        "relationship": deployment["relationship"],
        "action": "draft-listing-copy" if promoted_copy else "no-listing-change",
        "migrationProposed": False,
        "listingDraft": DRAFTS.get(deployment["logicalProductId"]) if promoted_copy else None,
    }


def build_manifest(catalogue: dict[str, Any]) -> dict[str, Any]:
    products = [
        _product_disposition(product, "catalogued")
        for product in catalogue["logicalProducts"]
    ]
    deployments = [
        _deployment_disposition(deployment, "catalogued")
        for deployment in catalogue["deployments"]
    ]
    product_ids = {record["logicalProductId"] for record in products}
    deployment_ids = {record["deploymentId"] for record in deployments}
    known_delta: list[dict[str, str]] = []

    known_product = KNOWN_POST_BASELINE["product"]
    if known_product["id"] not in product_ids:
        products.append(_product_disposition(known_product, "known-concurrent"))
        known_delta.append({"kind": "logical-product", "id": known_product["id"]})

    known_deployment = KNOWN_POST_BASELINE["deployment"]
    if known_deployment["id"] not in deployment_ids:
        deployments.append(
            _deployment_disposition(known_deployment, "known-concurrent")
        )
        known_delta.append({"kind": "deployment", "id": known_deployment["id"]})

    support = [
        {
            "logicalProductId": row["logicalProductId"],
            "clientClass": row["clientClass"],
            "support": row["support"],
        }
        for row in catalogue["clientMatrix"]
    ]
    counts = catalogue["scope"]["inventoryCounts"]
    return {
        "schemaVersion": "job-atlas-listing-disposition-v1",
        "scope": {
            "observedAt": OBSERVED_AT,
            "sourceRevision": SOURCE_REVISION,
            "sourceCatalogue": "catalogue/actors-v1.json",
            "baselineLogicalProducts": len(catalogue["logicalProducts"]),
            "baselineDeployments": len(catalogue["deployments"]),
            "accountedLogicalProducts": len(products),
            "accountedDeployments": len(deployments),
            "ownedActorsAccounted": counts["ownedActors"] + len(known_delta) // 2,
            "privateSupportExcluded": counts["ownedPrivateSupportExcluded"],
            "unrelatedPublicExcluded": counts["ownedUnrelatedPublicExcluded"],
            "knownPostBaselineDelta": known_delta,
            "evidenceBoundary": "Four existing job-atlas Store listings receive local copy drafts. Every nomad-agent deployment remains unchanged. Private support identities stay aggregate-only. This manifest authorizes no publication, migration, Actor run, billing change, schedule change, or destination write.",
        },
        "logicalProducts": products,
        "deployments": deployments,
        "clientSupport": support,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()
    catalogue = json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))
    rendered = json.dumps(build_manifest(catalogue), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"stale listing disposition: run {Path(__file__).relative_to(ROOT)}")
        return 0
    args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
