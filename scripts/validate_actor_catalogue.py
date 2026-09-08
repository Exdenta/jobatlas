#!/usr/bin/env python3
"""Validate the versioned Job Atlas Actor catalogue and maintained callers."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlparse


CATALOGUE_KEYS = {
    "$schema",
    "schemaVersion",
    "scope",
    "contractProfiles",
    "logicalProducts",
    "deployments",
    "excludedCandidates",
    "clientMatrix",
    "externalStateMatrix",
}
CLIENT_CLASSES = {
    "api-sdk",
    "mcp",
    "n8n",
    "make",
    "zapier",
    "airtable",
    "agent-skill",
    "python",
}
EXTERNAL_STATE_CLASSES = {
    "saved-tasks",
    "webhooks",
    "imports",
    "schedules",
    "billing-subscriptions",
    "credentials",
    "named-destinations",
}
SUPPORT_STATES = {"maintained", "documented-only", "destination-only", "not-claimed"}
TEXT_SUFFIXES = {
    ".html", ".json", ".md", ".mjs", ".py", ".toml", ".txt", ".yaml", ".yml",
}
IGNORED_ROUTE_PREFIXES = (
    ".git/",
    "catalogue/",
    "seo-evidence/",
    "tests/",
    "integrations/evidence/",
    "docs/seo-baselines/",
)
IGNORED_ROUTE_FILES = {
    "docs/CEO_REPORT_2026-08-27.md",
    "docs/client-migration.md",
}
ROUTE_PATTERN = re.compile(
    r"(?i)(?:job-atlas|nomad-agent)(?:/|~|%2f)[a-z0-9][a-z0-9-]*"
)
ACTOR_ID_PATTERN = re.compile(
    r"(?i)(?:expected[_-]?actor[_-]?id|actor[_-]?id|actId)"
    r"[^A-Za-z0-9]{0,20}([A-Za-z0-9]{17})(?![A-Za-z0-9])"
)


def extract_actor_routes(text: str) -> set[str]:
    """Return normalized owner/slug routes from slash, tilde, or encoded forms."""
    routes: set[str] = set()
    for raw in ROUTE_PATTERN.findall(text):
        normalized = re.sub(r"(?i)(?:~|%2f)", "/", raw).lower()
        routes.add(normalized)
    return routes


def _duplicates(values: list[str]) -> set[str]:
    return {value for value in values if values.count(value) > 1}


def _safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _timestamp(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})",
        value,
    ) is not None


def _schema_type_matches(value: Any, expected: str) -> bool:
    """Match the JSON types used by actors-v1.schema.json."""
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(expected, False)


def _schema_errors(
    value: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any],
    path: str = "$",
) -> list[str]:
    """Validate the catalogue against the schema subset it uses.

    Keeping this standard-library-only makes the checked validator runnable in
    release and contributor environments without turning JSON Schema into an
    optional check.
    """
    errors: list[str] = []
    if "$ref" in schema:
        reference = schema["$ref"]
        if not isinstance(reference, str) or not reference.startswith("#/"):
            return [f"{path}: unsupported schema reference {reference!r}"]
        target: Any = root_schema
        try:
            for token in reference[2:].split("/"):
                token = token.replace("~1", "/").replace("~0", "~")
                target = target[token]
        except (KeyError, TypeError):
            return [f"{path}: unresolved schema reference {reference}"]
        if not isinstance(target, dict):
            return [f"{path}: schema reference {reference} is not an object"]
        return _schema_errors(value, target, root_schema, path)

    if "oneOf" in schema:
        matches = [
            not _schema_errors(value, branch, root_schema, path)
            for branch in schema["oneOf"]
        ]
        if sum(matches) != 1:
            errors.append(f"{path}: must match exactly one schema alternative")
            return errors

    if "not" in schema and not _schema_errors(value, schema["not"], root_schema, path):
        errors.append(f"{path}: matches a forbidden schema")

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value {value!r} is outside the allowed enum")

    expected_types = schema.get("type")
    if expected_types is not None:
        if isinstance(expected_types, str):
            expected_types = [expected_types]
        if not any(_schema_type_matches(value, item) for item in expected_types):
            errors.append(f"{path}: expected type {' or '.join(expected_types)}")
            return errors

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required property {key}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value.keys() - properties.keys():
                errors.append(f"{path}: unknown property {key}")
        for key, child_schema in properties.items():
            if key in value:
                errors.extend(_schema_errors(value[key], child_schema, root_schema, f"{path}.{key}"))

    if isinstance(value, list):
        minimum = schema.get("minItems")
        if isinstance(minimum, int) and len(value) < minimum:
            errors.append(f"{path}: needs at least {minimum} items")
        if schema.get("uniqueItems"):
            serialized = [json.dumps(item, sort_keys=True, separators=(",", ":")) for item in value]
            if len(serialized) != len(set(serialized)):
                errors.append(f"{path}: items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(_schema_errors(item, item_schema, root_schema, f"{path}[{index}]"))

    if isinstance(value, str):
        minimum = schema.get("minLength")
        if isinstance(minimum, int) and len(value) < minimum:
            errors.append(f"{path}: string is shorter than {minimum}")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, value) is None:
            errors.append(f"{path}: does not match {pattern}")
        if schema.get("format") == "date-time":
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    raise ValueError("timezone missing")
            except ValueError:
                errors.append(f"{path}: is not an ISO-8601 date-time with timezone")
        if schema.get("format") == "uri":
            parsed_uri = urlparse(value)
            if not parsed_uri.scheme:
                errors.append(f"{path}: is not an absolute URI")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if isinstance(minimum, (int, float)) and value < minimum:
            errors.append(f"{path}: is below minimum {minimum}")

    return errors


def validate_catalogue(data: dict[str, Any], root: Path) -> list[str]:
    """Return deterministic validation errors; an empty list means valid."""
    errors: list[str] = []
    schema_path = root / "catalogue" / "actors-v1.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"catalogue schema cannot be loaded: {error}"]
    schema_errors = _schema_errors(data, schema, schema)
    if schema_errors:
        return [f"schema {error}" for error in schema_errors]

    extra_keys = set(data) - CATALOGUE_KEYS
    missing_keys = CATALOGUE_KEYS - set(data)
    if extra_keys or missing_keys:
        errors.append(f"catalogue keys mismatch: missing={sorted(missing_keys)} extra={sorted(extra_keys)}")
        return errors
    if data.get("schemaVersion") != "job-atlas-actor-catalogue-v1":
        errors.append("schemaVersion must be job-atlas-actor-catalogue-v1")

    schema_ref = data.get("$schema")
    if not _safe_relative_path(schema_ref) or not (root / "catalogue" / schema_ref).is_file():
        errors.append("$schema must name an existing local catalogue schema")

    scope = data.get("scope", {})
    if set(scope) != {
        "observedAt", "sourceRevision", "sourceRepository", "inventoryCounts",
        "inclusionRule", "evidenceBoundary",
    }:
        errors.append("scope has missing or unknown keys")
    if not re.fullmatch(r"[0-9a-f]{40}", str(scope.get("sourceRevision", ""))):
        errors.append("scope.sourceRevision must be a full Git commit")
    if not _timestamp(scope.get("observedAt")):
        errors.append("scope.observedAt must be an ISO-8601 timestamp with timezone")
    if not _nonempty_string(scope.get("sourceRepository")) or not scope["sourceRepository"].startswith("https://"):
        errors.append("scope.sourceRepository must be an HTTPS URL")
    for field in ("inclusionRule", "evidenceBoundary"):
        if not _nonempty_string(scope.get(field)):
            errors.append(f"scope.{field} must be non-empty")

    profiles = data.get("contractProfiles", [])
    products = data.get("logicalProducts", [])
    deployments = data.get("deployments", [])
    exclusions = data.get("excludedCandidates", [])
    clients = data.get("clientMatrix", [])
    external = data.get("externalStateMatrix", [])

    profile_ids = [str(item.get("id")) for item in profiles]
    product_ids = [str(item.get("id")) for item in products]
    deployment_ids = [str(item.get("id")) for item in deployments]
    actor_ids = [str(item.get("actorId")) for item in deployments + exclusions if item.get("actorId") is not None]
    candidate_routes = [f'{item.get("owner")}/{item.get("slug")}' for item in deployments + exclusions]
    for label, values in (
        ("contract profile", profile_ids),
        ("logical product", product_ids),
        ("deployment", deployment_ids),
        ("Actor ID", actor_ids),
        ("candidate route", candidate_routes),
    ):
        duplicates = _duplicates(values)
        if duplicates:
            errors.append(f"duplicate {label}: {sorted(duplicates)}")

    profile_id_set = set(profile_ids)
    product_id_set = set(product_ids)
    deployment_by_id = {item.get("id"): item for item in deployments}
    contract_profile_keys = {
        "id", "name", "canonicalRoots", "schemaPaths", "currentRunSummary",
        "legacyRunSummaries", "postingKey", "destinationKey", "emptyValueSemantics",
    }
    for profile in profiles:
        if set(profile) != contract_profile_keys:
            errors.append(f"contract profile {profile.get('id')} has missing or unknown keys")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(profile.get("id", ""))):
            errors.append(f"contract profile {profile.get('id')} has invalid id")
        if not _nonempty_string(profile.get("name")):
            errors.append(f"contract profile {profile.get('id')} has invalid name")
        roots = profile.get("canonicalRoots")
        if not isinstance(roots, list) or not roots or not all(_nonempty_string(item) for item in roots) or len(roots) != len(set(roots)):
            errors.append(f"contract profile {profile.get('id')} has invalid canonicalRoots")
        schema_paths = profile.get("schemaPaths")
        if not isinstance(schema_paths, list) or not schema_paths or len(schema_paths) != len(set(schema_paths)):
            errors.append(f"contract profile {profile.get('id')} has invalid schemaPaths")
        for profile_schema_path in schema_paths:
            if not _safe_relative_path(profile_schema_path) or not (root / profile_schema_path).is_file():
                errors.append(f"contract profile {profile.get('id')} has missing schema {profile_schema_path}")
        if not _nonempty_string(profile.get("currentRunSummary")):
            errors.append(f"contract profile {profile.get('id')} has invalid currentRunSummary")
        legacy_summaries = profile.get("legacyRunSummaries")
        if not isinstance(legacy_summaries, list) or not all(_nonempty_string(item) for item in legacy_summaries):
            errors.append(f"contract profile {profile.get('id')} has invalid legacyRunSummaries")
        posting_key = profile.get("postingKey")
        if not (
            _nonempty_string(posting_key)
            or isinstance(posting_key, dict)
            and set(posting_key) == {"primary", "fallback"}
            and all(_nonempty_string(value) for value in posting_key.values())
        ):
            errors.append(f"contract profile {profile.get('id')} has invalid postingKey")
        for field in ("destinationKey", "emptyValueSemantics"):
            if not _nonempty_string(profile.get(field)):
                errors.append(f"contract profile {profile.get('id')} has invalid {field}")

    for product in products:
        if set(product) != {
            "id", "name", "kind", "lifecycle", "promotion", "implementationSource",
            "contractProfileId", "maintainedExamples",
        }:
            errors.append(f"logical product {product.get('id')} has missing or unknown keys")
        if any(key in product for key in ("owner", "slug", "actorId")):
            errors.append(f"logical product {product.get('id')} mixes deployment identity")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(product.get("id", ""))):
            errors.append(f"logical product {product.get('id')} has invalid id")
        if not _nonempty_string(product.get("name")):
            errors.append(f"logical product {product.get('id')} has invalid name")
        if product.get("kind") not in {"source-scraper", "bundle", "search-agent", "fit-scorer"}:
            errors.append(f"logical product {product.get('id')} has invalid kind")
        if product.get("lifecycle") not in {"promoted", "legacy-live"}:
            errors.append(f"logical product {product.get('id')} has invalid lifecycle")
        if product.get("promotion") not in {"job-atlas", "not-planned"}:
            errors.append(f"logical product {product.get('id')} has invalid promotion")
        if (product.get("lifecycle"), product.get("promotion")) not in {
            ("promoted", "job-atlas"), ("legacy-live", "not-planned"),
        }:
            errors.append(f"logical product {product.get('id')} has inconsistent lifecycle and promotion")
        profile_id = product.get("contractProfileId")
        if profile_id is not None and profile_id not in profile_id_set:
            errors.append(f"logical product {product.get('id')} has unknown contractProfileId")
        source = product.get("implementationSource", {})
        if set(source) != {"state", "location", "evidence"}:
            errors.append(f"logical product {product.get('id')} has incomplete implementationSource")
        if source.get("state") not in {"in-repository", "not-in-repository", "unresolved"}:
            errors.append(f"logical product {product.get('id')} has invalid implementation source state")
        if source.get("location") is not None and not _safe_relative_path(source.get("location")):
            errors.append(f"logical product {product.get('id')} has invalid implementation source location")
        if source.get("state") == "not-in-repository" and source.get("location") is not None:
            errors.append(f"logical product {product.get('id')} cannot name a repository source location")
        if not _nonempty_string(source.get("evidence")):
            errors.append(f"logical product {product.get('id')} has empty implementation source evidence")
        examples = product.get("maintainedExamples")
        if not isinstance(examples, list) or len(examples) != len(set(examples)):
            errors.append(f"logical product {product.get('id')} has invalid maintainedExamples")
            examples = []
        for asset in examples:
            if not _safe_relative_path(asset) or not (root / asset).is_file():
                errors.append(f"logical product {product.get('id')} has missing asset {asset}")

    allowed_relationships = {"legacy-primary", "promoted-copy"}
    for deployment in deployments:
        if set(deployment) != {
            "id", "logicalProductId", "owner", "slug", "actorId", "endpointState",
            "releaseSelector", "relationship", "relationshipTargetId", "latestObservation",
        }:
            errors.append(f"deployment {deployment.get('id')} has missing or unknown keys")
        if deployment.get("logicalProductId") not in product_id_set:
            errors.append(f"deployment {deployment.get('id')} has unknown logicalProductId")
        if deployment.get("id") != f"{deployment.get('owner')}--{deployment.get('slug')}":
            errors.append(f"deployment {deployment.get('id')} id must match owner and slug")
        if not re.fullmatch(r"[A-Za-z0-9]{17}", deployment.get("actorId", "")):
            errors.append(f"deployment {deployment.get('id')} has invalid actorId")
        if deployment.get("endpointState") != "live-metadata-verified":
            errors.append(f"deployment {deployment.get('id')} endpointState is not live-metadata-verified")
        if deployment.get("releaseSelector") != "latest":
            errors.append(f"deployment {deployment.get('id')} releaseSelector is not latest")
        if deployment.get("relationship") not in allowed_relationships:
            errors.append(f"deployment {deployment.get('id')} has unknown relationship")
        observation = deployment.get("latestObservation", {})
        if set(observation) != {"observedAt", "buildId", "buildNumber", "sourceType", "evidence"}:
            errors.append(f"deployment {deployment.get('id')} has incomplete latestObservation")
        if not re.fullmatch(r"[A-Za-z0-9]{17}", str(observation.get("buildId", ""))):
            errors.append(f"deployment {deployment.get('id')} has invalid observed buildId")
        if not re.fullmatch(r"\d+\.\d+\.\d+", str(observation.get("buildNumber", ""))):
            errors.append(f"deployment {deployment.get('id')} has invalid observed buildNumber")
        if not _timestamp(observation.get("observedAt")):
            errors.append(f"deployment {deployment.get('id')} has invalid observation timestamp")
        if observation.get("sourceType") not in {"SOURCE_FILES", "TARBALL", "GIT_REPO", "unresolved"}:
            errors.append(f"deployment {deployment.get('id')} has invalid observation sourceType")
        if not _nonempty_string(observation.get("evidence")):
            errors.append(f"deployment {deployment.get('id')} has empty observation evidence")
        target_id = deployment.get("relationshipTargetId")
        if deployment.get("relationship") == "legacy-primary" and target_id is not None:
            errors.append(f"deployment {deployment.get('id')} legacy-primary cannot target another deployment")
        if deployment.get("relationship") == "legacy-primary" and deployment.get("owner") != "nomad-agent":
            errors.append(f"deployment {deployment.get('id')} legacy-primary must use nomad-agent owner")
        if deployment.get("relationship") == "promoted-copy":
            if deployment.get("owner") != "job-atlas":
                errors.append(f"deployment {deployment.get('id')} promoted-copy must use job-atlas owner")
            target = deployment_by_id.get(target_id)
            if target is None:
                errors.append(f"deployment {deployment.get('id')} promoted-copy target is unknown")
            elif target.get("actorId") == deployment.get("actorId"):
                errors.append(f"deployment {deployment.get('id')} promoted-copy must use a different Actor ID")
            elif target.get("logicalProductId") != deployment.get("logicalProductId"):
                errors.append(f"deployment {deployment.get('id')} promoted-copy crosses logical products")

    for exclusion in exclusions:
        if set(exclusion) != {"owner", "slug", "actorId", "category", "reason"}:
            errors.append(f"excluded candidate {exclusion.get('slug')} has missing or unknown keys")
        if exclusion.get("owner") != "nomad-agent":
            errors.append(f"excluded candidate {exclusion.get('slug')} must use nomad-agent owner")
        if exclusion.get("category") != "unrelated-public":
            errors.append(f"excluded candidate {exclusion.get('slug')} has invalid category")
        if not _nonempty_string(exclusion.get("reason")):
            errors.append(f"excluded candidate {exclusion.get('slug')} has no reason")
        if not re.fullmatch(r"[A-Za-z0-9]{17}", str(exclusion.get("actorId", ""))):
            errors.append(f"excluded public candidate {exclusion.get('slug')} has invalid actorId")

    counts = scope.get("inventoryCounts", {})
    expected_counts = {
        "ownedActors": 64,
        "ownedInScopePublic": 43,
        "ownedPrivateSupportExcluded": 3,
        "ownedUnrelatedPublicExcluded": 18,
        "promotedJobAtlasDeployments": 4,
        "inScopeDeployments": 47,
    }
    if counts != expected_counts:
        errors.append(f"inventoryCounts mismatch: expected {expected_counts}")
    if len(products) != 43 or len(deployments) != 47 or len(exclusions) != 18:
        errors.append("catalogue cardinality must be 43 products, 47 deployments, and 18 public exclusions")
    public_nomad_candidates = sum(
        item.get("owner") == "nomad-agent" for item in deployments + exclusions
    )
    if public_nomad_candidates != 61 or public_nomad_candidates + counts.get("ownedPrivateSupportExcluded", 0) != 64:
        errors.append("catalogue and aggregate private count do not account for all 64 owned candidates")

    promoted_products = {
        item.get("logicalProductId")
        for item in deployments
        if item.get("relationship") == "promoted-copy"
    }
    expected_client_keys = {
        (product_id, client_class)
        for product_id in promoted_products
        for client_class in CLIENT_CLASSES
    }
    actual_client_keys = [(item.get("logicalProductId"), item.get("clientClass")) for item in clients]
    if set(actual_client_keys) != expected_client_keys or len(actual_client_keys) != len(expected_client_keys):
        errors.append("clientMatrix must contain each promoted product and client class exactly once")
    for row in clients:
        if set(row) != {
            "logicalProductId", "clientClass", "support", "deploymentId", "routeMode",
            "releaseSelector", "assets", "externalStateClasses", "gap",
        }:
            errors.append(f"clientMatrix row {row.get('logicalProductId')}/{row.get('clientClass')} has missing or unknown keys")
        if row.get("support") not in SUPPORT_STATES:
            errors.append(f"clientMatrix row {row.get('logicalProductId')}/{row.get('clientClass')} has invalid support")
        if row.get("deploymentId") not in deployment_by_id:
            errors.append(f"clientMatrix row {row.get('logicalProductId')}/{row.get('clientClass')} has unknown deployment")
        else:
            deployment = deployment_by_id[row.get("deploymentId")]
            if deployment.get("logicalProductId") != row.get("logicalProductId"):
                errors.append(f"clientMatrix row {row.get('logicalProductId')}/{row.get('clientClass')} crosses deployments")
            if deployment.get("owner") != "job-atlas":
                errors.append(f"clientMatrix row {row.get('logicalProductId')}/{row.get('clientClass')} must target Job Atlas")
        if row.get("clientClass") not in CLIENT_CLASSES:
            errors.append(f"clientMatrix row {row.get('logicalProductId')}/{row.get('clientClass')} has invalid client class")
        if row.get("routeMode") not in {"direct", "task-owned", "destination-only", "post-run", "not-applicable"}:
            errors.append(f"clientMatrix row {row.get('logicalProductId')}/{row.get('clientClass')} has invalid route mode")
        assets = row.get("assets", [])
        for asset in assets:
            if not _safe_relative_path(asset) or not (root / asset).is_file():
                errors.append(f"clientMatrix row {row.get('logicalProductId')}/{row.get('clientClass')} has missing asset {asset}")
        if row.get("support") == "not-claimed" and not row.get("gap"):
            errors.append(f"clientMatrix row {row.get('logicalProductId')}/{row.get('clientClass')} needs a gap")
        if row.get("support") != "not-claimed" and not row.get("assets"):
            errors.append(f"supported client row {row.get('logicalProductId')}/{row.get('clientClass')} needs an asset")
        if row.get("support") == "maintained" and row.get("releaseSelector") not in {"latest", "task-latest"}:
            errors.append(f"maintained client row {row.get('logicalProductId')}/{row.get('clientClass')} lacks latest selector")
        state_classes = row.get("externalStateClasses", [])
        unknown_state_classes = set(state_classes) - EXTERNAL_STATE_CLASSES
        if unknown_state_classes:
            errors.append(f"clientMatrix row {row.get('logicalProductId')}/{row.get('clientClass')} has unknown external state")

    if {item.get("class") for item in external} != EXTERNAL_STATE_CLASSES or len(external) != len(EXTERNAL_STATE_CLASSES):
        errors.append("externalStateMatrix must cover every required state class exactly once")
    for row in external:
        if set(row) != {"class", "evidenceState", "action", "verification", "rollback", "gaps"}:
            errors.append(f"external state {row.get('class')} has missing or unknown keys")
        if not _nonempty_string(row.get("evidenceState")):
            errors.append(f"external state {row.get('class')} has empty evidenceState")
        for field in ("action", "verification", "rollback"):
            if not _nonempty_string(row.get(field)):
                errors.append(f"external state {row.get('class')} has empty {field}")
        if not row.get("gaps") or not all(_nonempty_string(gap) for gap in row.get("gaps", [])):
            errors.append(f"external state {row.get('class')} has invalid gaps")

    profile_by_id = {item.get("id"): item for item in profiles}
    jobs = profile_by_id.get("normalized-job-v1", {})
    if jobs.get("canonicalRoots") != ["schemaVersion", "identity", "data", "custom", "llm", "raw"]:
        errors.append("normalized-job-v1 must preserve the six canonical roots")
    if jobs.get("postingKey") != {"primary": "{source}:{externalId}", "fallback": "{source}:{url}"}:
        errors.append("normalized-job-v1 postingKey semantics changed")
    semantics = jobs.get("emptyValueSemantics", "")
    if not all(token in semantics for token in ("null", "[]", "raw: null")):
        errors.append("normalized-job-v1 empty-value semantics are incomplete")
    scorer = profile_by_id.get("job-fit-v1", {})
    if scorer.get("postingKey") != "jobKey" or scorer.get("destinationKey") != "matchKey":
        errors.append("job-fit-v1 must keep posting jobKey separate from destination matchKey")

    return errors


def validate_repository_routes(data: dict[str, Any], root: Path) -> list[str]:
    """Reconcile maintained route and contextual immutable-ID references."""
    current_deployment_ids = {
        row["deploymentId"] for row in data.get("clientMatrix", [])
    }
    current_deployments = [
        item for item in data.get("deployments", [])
        if item.get("id") in current_deployment_ids
        and item.get("endpointState") == "live-metadata-verified"
    ]
    current_routes = {
        f'{item["owner"]}/{item["slug"]}'.lower()
        for item in current_deployments
    }
    current_ids = {
        item["actorId"]
        for item in current_deployments
    }
    errors: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(root).as_posix()
        if relative in IGNORED_ROUTE_FILES or relative.startswith(IGNORED_ROUTE_PREFIXES):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for route in sorted(extract_actor_routes(text) - current_routes):
            errors.append(f"uncatalogued maintained Actor route {route} in {relative}")
        for actor_id in sorted(set(ACTOR_ID_PATTERN.findall(text)) - current_ids):
            errors.append(f"uncatalogued maintained Actor ID {actor_id} in {relative}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--catalogue", type=Path)
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()
    root = args.root.resolve()
    catalogue_path = args.catalogue or root / "catalogue" / "actors-v1.json"
    data = json.loads(catalogue_path.read_text(encoding="utf-8"))
    errors = validate_catalogue(data, root)
    if not errors:
        errors.extend(validate_repository_routes(data, root))
    if args.json_output:
        print(json.dumps({"ok": not errors, "errors": errors}, indent=2))
    elif errors:
        print("Actor catalogue validation failed:")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"Actor catalogue is valid: {catalogue_path}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
