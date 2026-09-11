#!/usr/bin/env python3
"""Validate the four evidence-labelled Job Atlas first-run packs offline."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
PACK_SCHEMA_PATH = ROOT / "first-run" / "first-run-pack-v1.schema.json"
PUBLIC_READBACK_AT = "2026-09-11T01:13:07+02:00"
RELATED_EXECUTION_AT = "2026-09-09"
PACK_IDS = (
    "linkedin",
    "euraxess",
    "ycombinator",
    "ai-job-fit-scorer",
)

COMMON_RECEIPT_FIELDS = {
    "id",
    "buildId",
    "buildNumber",
    "defaultDatasetId",
    "defaultKeyValueStoreId",
    "status",
    "exitCode",
}
SCRAPER_CHECKS = {
    "terminal_succeeded",
    "resolved_build_identity",
    "same_run_storages",
    "summary_schema",
    "summary_status",
    "dataset_count",
    "row_schema",
    "row_source",
    "retry_policy",
    "settled_cost",
}
SCORER_CHECKS = {
    "terminal_succeeded",
    "resolved_build_identity",
    "same_run_storages",
    "summary_schema",
    "summary_result_policy",
    "dataset_count",
    "row_schema",
    "row_source",
    "match_key",
    "settled_cost",
}

PACK_SPECS: dict[str, dict[str, Any]] = {
    "linkedin": {
        "slug": "linkedin-enrich-translate-normalize-scraper",
        "actor_id": "KMflYVTHiIAXE6nKN",
        "build_id": "4wE4rKPq5aq7jeIY1",
        "build_number": "1.0.5",
        "endpoint_segment": "acts",
        "sample_source": "linkedin",
        "sample_class": "illustrative_fixture",
        "row_schema_version": "nomad-agent-job-v1",
        "summary_schema_version": "nomad-agent-run-summary-v4",
        "dataset_count_field": "delivered",
        "statuses": {"succeeded", "empty", "empty-limited", "partial"},
        "checks": SCRAPER_CHECKS,
        "related_run_id": "N8yk4dVkRSr1avM93",
        "primary_event": "result",
        "primary_price": 0.0009,
        "optional_prices": {
            "position-enrichment": 0.004,
            "position-enrichment-gold": 0.01,
            "translation": 0.006,
        },
        "input_path": "integrations/api/linkedin-search.json",
        "sample_path": "website/samples/explorer/linkedin.json",
        "row_schema_path": "integrations/shared/nomad-agent-job-v1.schema.json",
        "extension_path": None,
        "extension_version": None,
        "summary_schema_path": "integrations/shared/run-summary-v4.schema.json",
        "optional_disabled": {
            "firstRunMode",
            "aiEnrichment",
            "translateToEnglish",
            "companyProfileEnrichment",
        },
        "stateful_disabled": {"dedupe", "analyticsEnabled"},
        "max_items": 5,
        "cap": 0.10,
        "sample_observed_at": None,
        "related_rows": 2,
        "related_status": "partial",
    },
    "euraxess": {
        "slug": "euraxess-enrich-translate-normalize-scraper",
        "actor_id": "Slu3SAWULLRYnCN9Y",
        "build_id": "x0bGueGFnm6eEGY3K",
        "build_number": "1.0.4",
        "endpoint_segment": "acts",
        "sample_source": "euraxess",
        "sample_class": "recorded_source_result",
        "row_schema_version": "nomad-agent-job-v1",
        "summary_schema_version": "nomad-agent-run-summary-v4",
        "dataset_count_field": "delivered",
        "statuses": {"succeeded", "empty", "empty-limited", "partial"},
        "checks": SCRAPER_CHECKS,
        "related_run_id": "0s3ZypkpzoncXvlyE",
        "primary_event": "result",
        "primary_price": 0.0009,
        "optional_prices": {
            "position-enrichment": 0.006,
            "position-enrichment-gold": 0.01,
            "translation": 0.006,
        },
        "input_path": "integrations/api/euraxess-search.json",
        "sample_path": "website/samples/explorer/euraxess.json",
        "row_schema_path": "integrations/shared/nomad-agent-job-v1.schema.json",
        "extension_path": "integrations/shared/euraxess-v1.schema.json",
        "extension_version": "euraxess-v1",
        "summary_schema_path": "integrations/shared/run-summary-v4.schema.json",
        "optional_disabled": {"aiEnrichment", "translateToEnglish"},
        "stateful_disabled": {"dedupe", "analyticsEnabled"},
        "max_items": 5,
        "cap": 0.05,
        "sample_observed_at": "2026-09-04T12:23:46.255387Z",
        "related_rows": 2,
        "related_status": "partial",
    },
    "ycombinator": {
        "slug": "ycombinator-enrich-translate-normalize-scraper",
        "actor_id": "pF4Lk4ifzb9tZXg7K",
        "build_id": "9D13ViqHgk6hFtWVi",
        "build_number": "1.0.4",
        "endpoint_segment": "acts",
        "sample_source": "ycombinator_was",
        "sample_class": "illustrative_fixture",
        "row_schema_version": "nomad-agent-job-v1",
        "summary_schema_version": "nomad-agent-run-summary-v4",
        "dataset_count_field": "delivered",
        "statuses": {"succeeded", "empty", "empty-limited", "partial"},
        "checks": SCRAPER_CHECKS,
        "related_run_id": "GLrBSf94Z2x87EH7X",
        "primary_event": "result",
        "primary_price": 0.0009,
        "optional_prices": {
            "position-enrichment": 0.006,
            "position-enrichment-gold": 0.01,
            "translation": 0.006,
        },
        "input_path": "first-run/inputs/ycombinator.json",
        "sample_path": "first-run/samples/ycombinator-v2.illustrative.json",
        "row_schema_path": "integrations/shared/nomad-agent-job-v1.schema.json",
        "extension_path": "integrations/shared/ycombinator-v2.schema.json",
        "extension_version": "ycombinator-v2",
        "summary_schema_path": "integrations/shared/run-summary-v4.schema.json",
        "optional_disabled": {
            "firstRunMode",
            "aiEnrichment",
            "translateToEnglish",
        },
        "stateful_disabled": {"dedupe", "analyticsEnabled"},
        "max_items": 5,
        "cap": 0.05,
        "sample_observed_at": None,
        "related_rows": 2,
        "related_status": "partial",
    },
    "ai-job-fit-scorer": {
        "slug": "ai-job-fit-scorer",
        "actor_id": "OZ919PaAyAbifOdcL",
        "build_id": "gxzLgzyS6vc1djG9S",
        "build_number": "0.1.5",
        "endpoint_segment": "actors",
        "sample_source": "linkedin",
        "sample_class": "historical_predecessor_run",
        "row_schema_version": "nomad-ai-job-fit-v1",
        "summary_schema_version": "nomad-ai-job-fit-run-summary-v4",
        "dataset_count_field": "counts.outputRows",
        "statuses": {"complete", "partial", "empty"},
        "checks": SCORER_CHECKS,
        "related_run_id": "he2KWlCNQ7c53lHK8",
        "primary_event": "job-fit-result",
        "primary_price": 0.02,
        "optional_prices": {},
        "input_path": "integrations/api/ai-job-fit-scorer-input.json",
        "sample_path": "docs/examples/ai-job-fit-scorer/fit-row.example.json",
        "row_schema_path": "integrations/shared/nomad-ai-job-fit-v1.schema.json",
        "extension_path": None,
        "extension_version": None,
        "summary_schema_path": (
            "integrations/shared/nomad-ai-job-fit-run-summary-v4.schema.json"
        ),
        "optional_disabled": set(),
        "stateful_disabled": set(),
        "max_items": 5,
        "cap": 0.10,
        "sample_observed_at": "2026-09-05",
        "related_rows": 1,
        "related_status": "complete",
    },
}


class ValidationError(ValueError):
    """Raised when a first-run pack fails a closed validation rule."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValidationError(f"non-finite JSON number: {value}")


def _load_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_constant,
        )
    except (OSError, json.JSONDecodeError) as error:
        raise ValidationError(f"cannot read valid JSON from {path}: {error}") from error


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_relative(value: Any, field: str, root: Path = ROOT) -> Path:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{field} must be a non-empty relative path")
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValidationError(f"{field} must not escape the repository")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as error:
        raise ValidationError(f"{field} escapes the repository") from error
    if not resolved.is_file():
        raise ValidationError(f"{field} does not exist: {value}")
    return resolved


def _load_schema_checker(root: Path) -> Any:
    path = (
        root
        / ".agents"
        / "skills"
        / "ai-job-fit-scorer"
        / "scripts"
        / "schema_check.py"
    )
    spec = importlib.util.spec_from_file_location("jobatlas_first_run_schema_check", path)
    if spec is None or spec.loader is None:
        raise ValidationError("cannot load the offline schema checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _check_schema(
    value: Any,
    schema: Mapping[str, Any],
    path: str,
    root: Path,
) -> None:
    try:
        _load_schema_checker(root).check(value, dict(schema), path)
    except (KeyError, TypeError, ValueError) as error:
        raise ValidationError(str(error)) from error


def _without_unique_items(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _without_unique_items(child)
            for key, child in value.items()
            if key != "uniqueItems"
        }
    if isinstance(value, list):
        return [_without_unique_items(child) for child in value]
    return value


def _enforce_unique_items(value: Any, schema: Mapping[str, Any], path: str) -> None:
    if isinstance(value, list):
        if schema.get("uniqueItems"):
            serialized = [
                json.dumps(item, sort_keys=True, separators=(",", ":"))
                for item in value
            ]
            if len(serialized) != len(set(serialized)):
                raise ValidationError(f"{path}: items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                _enforce_unique_items(item, item_schema, f"{path}[{index}]")
    elif isinstance(value, dict):
        properties = schema.get("properties", {})
        for key, item in value.items():
            child_schema = properties.get(key)
            if isinstance(child_schema, dict):
                _enforce_unique_items(item, child_schema, f"{path}.{key}")


def _require_unique_set(value: Any, expected: set[str], field: str) -> None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValidationError(f"{field} must be a string array")
    if len(value) != len(set(value)):
        raise ValidationError(f"{field} must not contain duplicates")
    if set(value) != expected:
        raise ValidationError(f"{field} must equal {sorted(expected)}")


def _require_hash(path: Path, expected: Any, field: str) -> None:
    actual = _sha256(path)
    if expected != actual:
        raise ValidationError(f"{field} mismatch: expected {expected!r}, got {actual}")


def _require_exact_keys(
    value: Mapping[str, Any],
    expected: set[str],
    field: str,
) -> None:
    actual = set(value)
    if actual != expected:
        raise ValidationError(
            f"{field} keys must equal {sorted(expected)}; got {sorted(actual)}"
        )


def _require_integer(
    value: Any,
    field: str,
    minimum: int,
    maximum: int,
) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValidationError(
            f"{field} must be an integer from {minimum} through {maximum}"
        )
    return value


def _require_string_array(
    value: Any,
    field: str,
    minimum: int,
    maximum: int,
    *,
    item_maximum: int | None = None,
    allowed: set[str] | None = None,
) -> list[str]:
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        raise ValidationError(
            f"{field} must contain {minimum} through {maximum} strings"
        )
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValidationError(f"{field} must contain only non-empty strings")
    if item_maximum is not None and any(len(item) > item_maximum for item in value):
        raise ValidationError(f"{field} contains a string longer than {item_maximum}")
    if len(value) != len(set(value)):
        raise ValidationError(f"{field} must contain unique strings")
    if allowed is not None and not set(value) <= allowed:
        raise ValidationError(f"{field} contains an unsupported value")
    return value


def _validate_catalogue_identity(pack: Mapping[str, Any], root: Path) -> None:
    actor = pack["actor"]
    catalogue = _load_json(root / "catalogue" / "actors-v1.json")
    matches = [
        item
        for item in catalogue.get("deployments", [])
        if item.get("owner") == "job-atlas" and item.get("slug") == actor["slug"]
    ]
    if len(matches) != 1 or matches[0].get("actorId") != actor["immutableActorId"]:
        raise ValidationError("actor owner/slug/immutable ID does not match the catalogue")


def _validate_scraper_input(pack_id: str, value: Mapping[str, Any], max_items: int) -> None:
    common_keys = {
        "schemaVersion",
        "postedWithin",
        "maxItems",
        "translateToEnglish",
        "aiEnrichment",
        "includeRaw",
        "dedupe",
        "analyticsEnabled",
    }
    expected_keys = {
        "linkedin": common_keys | {"keyword", "location", "workArrangements"},
        "euraxess": common_keys
        | {"keyword", "location", "workArrangements", "euraxessSearch"},
        "ycombinator": common_keys | {"firstRunMode", "ycSearch"},
    }[pack_id]
    _require_exact_keys(value, expected_keys, "starter input")
    if value.get("schemaVersion") != "nomad-agent-job-search-input-v1":
        raise ValidationError("starter input must use nomad-agent-job-search-input-v1")
    _require_integer(value.get("maxItems"), "starter.maxItems", 1, 5)
    if value.get("maxItems") != max_items:
        raise ValidationError("starter maxItems must match the pack and be at most five")
    if value.get("firstRunMode", False) is not False:
        raise ValidationError("firstRunMode must be absent or false")
    if value.get("translateToEnglish") is not False:
        raise ValidationError("translateToEnglish must be false")
    enrichment = value.get("aiEnrichment")
    if not isinstance(enrichment, dict):
        raise ValidationError("aiEnrichment must be an object")
    _require_exact_keys(enrichment, {"enabled", "accuracy"}, "aiEnrichment")
    if enrichment.get("enabled") is not False:
        raise ValidationError("aiEnrichment.enabled must be false")
    if enrichment.get("accuracy") != "silver":
        raise ValidationError("disabled starter enrichment must retain the silver tier")
    if value.get("includeRaw") is not False:
        raise ValidationError("includeRaw must be false")
    dedupe = value.get("dedupe")
    if not isinstance(dedupe, dict):
        raise ValidationError("dedupe must be an object")
    _require_exact_keys(dedupe, {"enabled", "key"}, "dedupe")
    if dedupe.get("enabled") is not False or dedupe.get("key") != "":
        raise ValidationError("dedupe.enabled must be false")
    if value.get("analyticsEnabled") is not False:
        raise ValidationError("analyticsEnabled must be false")
    if value.get("companyProfileEnrichment", False) is not False:
        raise ValidationError("companyProfileEnrichment must be absent or false")
    if pack_id == "euraxess":
        for field in ("keyword", "location"):
            if not isinstance(value.get(field), str) or not value[field].strip():
                raise ValidationError(f"EURAXESS {field} must be a non-empty string")
        _require_string_array(
            value.get("workArrangements"),
            "workArrangements",
            0,
            3,
            allowed={"remote", "hybrid", "onsite"},
        )
        if value.get("postedWithin") not in {"24h", "7d", "30d", "any"}:
            raise ValidationError("EURAXESS postedWithin rejects 1h and unknown values")
        search = value.get("euraxessSearch")
        if (
            not isinstance(search, dict)
            or search.get("schemaVersion") != "nomad-agent-euraxess-search-v1"
        ):
            raise ValidationError("EURAXESS input must carry euraxessSearch v1")
        _require_exact_keys(
            search,
            {"schemaVersion", "translateKeywords"},
            "euraxessSearch",
        )
        if search.get("translateKeywords") is not False:
            raise ValidationError("EURAXESS keyword translation must be false")
    elif pack_id == "ycombinator":
        if value.get("postedWithin") not in {"1h", "24h", "7d", "30d", "any"}:
            raise ValidationError("YC postedWithin has an unsupported value")
        search = value.get("ycSearch")
        if (
            not isinstance(search, dict)
            or search.get("schemaVersion") != "nomad-agent-ycombinator-search-v1"
        ):
            raise ValidationError("YC input must carry ycSearch v1")
        _require_exact_keys(search, {"schemaVersion", "queries"}, "ycSearch")
        _require_string_array(
            search.get("queries"),
            "ycSearch.queries",
            1,
            3,
            item_maximum=100,
        )
    else:
        for field in ("keyword", "location"):
            if not isinstance(value.get(field), str) or not value[field].strip():
                raise ValidationError(f"LinkedIn {field} must be a non-empty string")
        if value.get("postedWithin") not in {"1h", "24h", "7d", "30d", "any"}:
            raise ValidationError("LinkedIn postedWithin has an unsupported value")
        _require_string_array(
            value.get("workArrangements"),
            "workArrangements",
            0,
            3,
            allowed={"remote", "hybrid", "onsite"},
        )


def _walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        keys.update(str(key).lower() for key in value)
        for child in value.values():
            keys.update(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_walk_keys(child))
    return keys


def _validate_scorer_input(value: Mapping[str, Any], max_items: int) -> None:
    _require_exact_keys(
        value,
        {
            "mode",
            "search",
            "candidateProfile",
            "maxItems",
            "resultMode",
            "minDeliveryScore",
            "minRankToForward",
            "recoverHolds",
            "aiConcurrency",
        },
        "scorer starter",
    )
    if value.get("mode") != "search" or value.get("resultMode") != "shortlist":
        raise ValidationError("scorer starter must use search/shortlist mode")
    _require_integer(value.get("maxItems"), "scorer.maxItems", 1, 5)
    if value.get("maxItems") != max_items:
        raise ValidationError("scorer maxItems must match the pack and be at most five")
    search = value.get("search")
    if not isinstance(search, dict):
        raise ValidationError("scorer starter requires a search object")
    _require_exact_keys(
        search,
        {
            "sources",
            "keywords",
            "postedWithinDays",
            "maxItemsPerSource",
            "cacheTtlSeconds",
            "concurrency",
            "sourceTimeoutSecs",
        },
        "scorer.search",
    )
    _require_string_array(
        search.get("sources"),
        "scorer.search.sources",
        1,
        3,
        allowed={
            "linkedin",
            "remote_boards",
            "builtin",
            "justjoinit",
            "nofluffjobs",
            "hackernews",
            "ycombinator_was",
            "wttj",
            "infojobs",
            "tecnoempleo",
        },
    )
    _require_string_array(
        search.get("keywords"),
        "scorer.search.keywords",
        1,
        10,
        item_maximum=100,
    )
    _require_integer(
        search.get("postedWithinDays"),
        "scorer.search.postedWithinDays",
        0,
        365,
    )
    _require_integer(
        search.get("maxItemsPerSource"),
        "scorer.search.maxItemsPerSource",
        1,
        3,
    )
    _require_integer(
        search.get("cacheTtlSeconds"),
        "scorer.search.cacheTtlSeconds",
        0,
        86400,
    )
    _require_integer(
        search.get("concurrency"),
        "scorer.search.concurrency",
        1,
        10,
    )
    _require_integer(
        search.get("sourceTimeoutSecs"),
        "scorer.search.sourceTimeoutSecs",
        30,
        300,
    )
    profile = value.get("candidateProfile")
    if not isinstance(profile, dict) or not profile.get("primaryRole"):
        raise ValidationError("scorer starter requires a bounded fictional candidate profile")
    _require_exact_keys(
        profile,
        {
            "primaryRole",
            "targetTerms",
            "skills",
            "seniorityLevels",
            "remoteLocations",
            "hybridLocations",
            "onsiteLocations",
            "workArrangementPreferencesComplete",
        },
        "candidateProfile",
    )
    if (
        not isinstance(profile["primaryRole"], str)
        or not profile["primaryRole"].strip()
        or len(profile["primaryRole"]) > 200
    ):
        raise ValidationError("candidateProfile.primaryRole must be a short string")
    _require_string_array(
        profile["targetTerms"],
        "candidateProfile.targetTerms",
        1,
        30,
        item_maximum=200,
    )
    _require_string_array(
        profile["skills"],
        "candidateProfile.skills",
        1,
        100,
        item_maximum=200,
    )
    _require_string_array(
        profile["seniorityLevels"],
        "candidateProfile.seniorityLevels",
        1,
        12,
        item_maximum=40,
        allowed={
            "intern",
            "entry",
            "junior",
            "associate",
            "mid",
            "senior",
            "lead",
            "staff",
            "principal",
        },
    )
    location_counts = {
        "remoteLocations": (1, 30),
        "hybridLocations": (0, 30),
        "onsiteLocations": (0, 30),
    }
    for field, (minimum, maximum) in location_counts.items():
        _require_string_array(
            profile[field],
            f"candidateProfile.{field}",
            minimum,
            maximum,
            item_maximum=200,
        )
    if profile["workArrangementPreferencesComplete"] is not True:
        raise ValidationError("fictional starter must explicitly close its work preferences")
    _require_integer(value.get("minDeliveryScore"), "minDeliveryScore", 0, 5)
    _require_integer(value.get("minRankToForward"), "minRankToForward", 0, 100)
    if value.get("recoverHolds") is not False:
        raise ValidationError("recoverHolds must be false in the starter")
    _require_integer(value.get("aiConcurrency"), "aiConcurrency", 1, 8)
    secret_keys = {
        "name",
        "email",
        "phone",
        "address",
        "token",
        "password",
        "secret",
        "api_key",
        "apikey",
    }
    exposed = _walk_keys(profile) & secret_keys
    if exposed:
        raise ValidationError(
            "scorer starter contains disallowed personal or secret fields: "
            f"{sorted(exposed)}"
        )


def _validate_sample(
    pack_id: str,
    pack: Mapping[str, Any],
    sample: Mapping[str, Any],
    root: Path,
) -> None:
    spec = PACK_SPECS[pack_id]
    sample_meta = pack["sample"]
    row_schema_path = _resolve_relative(sample_meta["rowSchemaPath"], "sample.rowSchemaPath", root)
    _require_hash(row_schema_path, sample_meta["rowSchemaSha256"], "sample.rowSchemaSha256")
    row_schema = _load_json(row_schema_path)
    _check_schema(sample, row_schema, "sample", root)
    if sample.get("schemaVersion") != spec["row_schema_version"]:
        raise ValidationError("sample schemaVersion does not match its pack")

    if pack_id == "ai-job-fit-scorer":
        if sample.get("source") != spec["sample_source"]:
            raise ValidationError("scorer sample source does not match its pack")
        job = sample.get("job")
        if not isinstance(job, dict) or not isinstance(job.get("identity"), dict):
            raise ValidationError("scorer sample must retain nested job identity")
        if job["identity"].get("source") != sample.get("source"):
            raise ValidationError("scorer row.source and row.job.identity.source must agree")
        if not isinstance(sample.get("matchKey"), str) or not sample["matchKey"]:
            raise ValidationError("scorer sample requires candidate-specific matchKey")
        if (
            sample_meta["sourceExtensionSchemaPath"] is not None
            or sample_meta["sourceExtensionSchemaSha256"] is not None
        ):
            raise ValidationError("scorer sample must not declare a scraper source extension")
        return

    identity = sample.get("identity")
    if not isinstance(identity, dict) or identity.get("source") != spec["sample_source"]:
        raise ValidationError("sample identity.source does not match its pack")

    extension_path_value = sample_meta["sourceExtensionSchemaPath"]
    if pack_id == "linkedin":
        if (
            extension_path_value is not None
            or sample_meta["sourceExtensionSchemaSha256"] is not None
        ):
            raise ValidationError("LinkedIn sample must not declare a source extension")
        return
    extension_path = _resolve_relative(
        extension_path_value,
        "sample.sourceExtensionSchemaPath",
        root,
    )
    _require_hash(
        extension_path,
        sample_meta["sourceExtensionSchemaSha256"],
        "sample.sourceExtensionSchemaSha256",
    )
    custom = sample.get("custom")
    if not isinstance(custom, dict) or not isinstance(custom.get("data"), dict):
        raise ValidationError(f"{pack_id} sample must include custom.data")
    extension_schema = _load_json(extension_path)
    if custom.get("schemaId") != extension_schema.get("$id"):
        raise ValidationError(f"{pack_id} custom.schemaId does not match the source schema")
    if pack_id == "euraxess":
        validator_path = (
            root
            / ".agents"
            / "skills"
            / "euraxess-enrich-translate-normalize-scraper"
            / "scripts"
            / "validate_contract.py"
        )
        module_spec = importlib.util.spec_from_file_location(
            "jobatlas_euraxess_contract",
            validator_path,
        )
        if module_spec is None or module_spec.loader is None:
            raise ValidationError("cannot load the EURAXESS source validator")
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        try:
            module.validate_euraxess_job(sample)
        except (KeyError, TypeError, ValueError) as error:
            raise ValidationError(str(error)) from error
    else:
        _check_schema(
            custom["data"],
            _without_unique_items(extension_schema),
            "sample.custom.data",
            root,
        )
        _enforce_unique_items(custom["data"], extension_schema, "sample.custom.data")


def _validate_guidance(pack_id: str, pack: Mapping[str, Any]) -> None:
    guidance = pack["guidance"]
    completion = pack["completion"]
    if "null" not in guidance["unknownFields"]:
        raise ValidationError("unknown-field guidance must explain null values")
    if pack_id != "ai-job-fit-scorer" and "[]" not in guidance["unknownFields"]:
        raise ValidationError("scraper unknown-field guidance must distinguish null from []")
    empty = guidance["empty"].lower()
    empty_state = (
        "empty" in empty
        if pack_id == "ai-job-fit-scorer"
        else ("no rows" in empty or "zero rows" in empty)
    )
    if "not" not in empty or not empty_state:
        raise ValidationError("empty guidance must bound the no-row interpretation")
    partial = guidance["partial"].lower()
    if "partial" not in partial or "limit" not in partial:
        raise ValidationError("partial guidance must explain bounded limits")
    if "non-succeeded" not in guidance["failure"].lower():
        raise ValidationError("failure guidance must reject non-SUCCEEDED runs")
    retry_rule = completion["retryRule"].lower()
    if not (
        "do not retry automatically" in retry_rule
        or "do not start another run automatically" in retry_rule
    ):
        raise ValidationError("retry rule must forbid automatic paid retries")
    cost_rule = completion["costRule"].lower()
    if "settled" not in cost_rule or "ceiling" not in cost_rule:
        raise ValidationError("cost rule must require settlement and explain the ceiling")
    source_rule = completion["sourceRule"].lower()
    spec = PACK_SPECS[pack_id]
    source_token = "row.source" if pack_id == "ai-job-fit-scorer" else spec["sample_source"]
    if (
        source_token not in source_rule
        or spec["row_schema_version"] not in source_rule
    ):
        raise ValidationError("source rule must bind the row contract and source")
    proof = guidance["nextStepProof"].lower()
    if "proof" not in proof and "proved" not in proof and "remain" not in proof:
        raise ValidationError("next-step guidance must preserve the downstream proof boundary")


def validate_pack(
    pack_path: str | Path,
    *,
    input_override: Mapping[str, Any] | None = None,
    sample_override: Mapping[str, Any] | None = None,
    root: Path = ROOT,
) -> dict[str, Any]:
    """Validate one pack and return a compact deterministic result."""
    path = Path(pack_path)
    if not path.is_absolute():
        path = root / path
    pack = _load_json(path)
    if not isinstance(pack, dict):
        raise ValidationError("pack must be a JSON object")
    schema = _load_json(root / PACK_SCHEMA_PATH.relative_to(ROOT))
    _check_schema(pack, schema, "pack", root)
    pack_id = pack.get("packId")
    if pack_id not in PACK_SPECS:
        raise ValidationError(f"unsupported packId: {pack_id!r}")
    spec = PACK_SPECS[pack_id]
    if pack["product"]["websiteUrl"] != f"https://jobatlas.dev/actors/{pack_id}":
        raise ValidationError("product.websiteUrl must use the canonical Job Atlas route")

    actor = pack["actor"]
    expected_actor = {
        "slug": spec["slug"],
        "immutableActorId": spec["actor_id"],
        "apiActorId": f"job-atlas~{spec['slug']}",
        "storeUrl": f"https://apify.com/job-atlas/{spec['slug']}",
        "buildSelector": "latest",
    }
    for field, expected in expected_actor.items():
        if actor.get(field) != expected:
            raise ValidationError(f"actor.{field} must equal {expected!r}")
    readback = actor["datedPublicReadback"]
    if readback["observedAt"] != PUBLIC_READBACK_AT:
        raise ValidationError("public build and pricing readback timestamp has drifted")
    for field, expected in (
        ("buildId", spec["build_id"]),
        ("buildNumber", spec["build_number"]),
        ("primaryEventName", spec["primary_event"]),
        ("primaryUnitPriceUsd", spec["primary_price"]),
    ):
        if readback.get(field) != expected:
            raise ValidationError(
                f"actor.datedPublicReadback.{field} must equal {expected!r}"
            )
    observed_optional = readback["optionalEventPricesUsd"]
    event_names = [item["eventName"] for item in observed_optional]
    if len(event_names) != len(set(event_names)):
        raise ValidationError("dated optional-event prices must have unique names")
    optional_prices = {
        item["eventName"]: item["unitPriceUsd"] for item in observed_optional
    }
    if optional_prices != spec["optional_prices"]:
        raise ValidationError("dated optional-event prices do not match the readback")
    if "did not execute" not in readback["proofBoundary"].lower():
        raise ValidationError("dated public readback must disclaim Actor execution")
    _validate_catalogue_identity(pack, root)

    starter = pack["starter"]
    if starter["inputPath"] != spec["input_path"]:
        raise ValidationError("starter input path does not match the reviewed pack")
    if starter["maxItems"] != spec["max_items"]:
        raise ValidationError("starter maxItems does not match the reviewed pack")
    if starter["maxTotalChargeUsd"] != spec["cap"]:
        raise ValidationError("starter charge ceiling does not match the reviewed pack")
    _require_unique_set(
        starter["optionalPaidFeaturesDisabled"],
        spec["optional_disabled"],
        "starter.optionalPaidFeaturesDisabled",
    )
    _require_unique_set(
        starter["statefulFeaturesDisabled"],
        spec["stateful_disabled"],
        "starter.statefulFeaturesDisabled",
    )
    input_path = _resolve_relative(starter["inputPath"], "starter.inputPath", root)
    _require_hash(input_path, starter["inputSha256"], "starter.inputSha256")
    starter_input = (
        copy.deepcopy(input_override)
        if input_override is not None
        else _load_json(input_path)
    )
    if not isinstance(starter_input, dict):
        raise ValidationError("starter input must be a JSON object")
    if pack_id == "ai-job-fit-scorer":
        _validate_scorer_input(starter_input, starter["maxItems"])
    else:
        _validate_scraper_input(pack_id, starter_input, starter["maxItems"])

    expected_cost = readback["primaryUnitPriceUsd"] * starter["maxItems"]
    cap = starter["maxTotalChargeUsd"]
    if not isinstance(cap, (int, float)) or isinstance(cap, bool) or not math.isfinite(cap):
        raise ValidationError("starter.maxTotalChargeUsd must be a finite number")
    if cap < expected_cost - 1e-12 or cap > 0.10:
        raise ValidationError("starter charge ceiling must cover base rows and be at most $0.10")

    sample_meta = pack["sample"]
    for field, expected in (
        ("recordPath", spec["sample_path"]),
        ("rowSchemaPath", spec["row_schema_path"]),
        ("sourceExtensionSchemaPath", spec["extension_path"]),
        ("sourceExtensionSchemaVersion", spec["extension_version"]),
        ("observedAt", spec["sample_observed_at"]),
    ):
        if sample_meta[field] != expected:
            raise ValidationError(f"sample.{field} does not match the reviewed evidence")
    if sample_meta["evidenceClass"] != spec["sample_class"]:
        raise ValidationError("sample evidence class does not match the reviewed fixture")
    if sample_meta["sampleSource"] != spec["sample_source"]:
        raise ValidationError("sample source label does not match the reviewed fixture")
    if sample_meta["rowSchemaVersion"] != spec["row_schema_version"]:
        raise ValidationError("sample row schema version does not match the product")
    not_proof = " ".join(sample_meta["notProofOf"]).lower()
    execution_disclaimed = "run" in not_proof or "actor output" in not_proof
    if not execution_disclaimed or "destination" not in not_proof:
        raise ValidationError("sample provenance must disclaim run and destination proof")
    sample_path = _resolve_relative(sample_meta["recordPath"], "sample.recordPath", root)
    _require_hash(sample_path, sample_meta["recordSha256"], "sample.recordSha256")
    sample = (
        copy.deepcopy(sample_override)
        if sample_override is not None
        else _load_json(sample_path)
    )
    if not isinstance(sample, dict):
        raise ValidationError("sample must be a JSON object")
    _validate_sample(pack_id, pack, sample, root)

    completion = pack["completion"]
    if completion["runSummarySchemaPath"] != spec["summary_schema_path"]:
        raise ValidationError("run-summary schema path does not match the product")
    summary_schema_path = _resolve_relative(
        completion["runSummarySchemaPath"], "completion.runSummarySchemaPath", root
    )
    _require_hash(
        summary_schema_path,
        completion["runSummarySchemaSha256"],
        "completion.runSummarySchemaSha256",
    )
    if completion["runSummarySchemaVersion"] != spec["summary_schema_version"]:
        raise ValidationError("run-summary schema version does not match the product")
    if completion["datasetCountField"] != spec["dataset_count_field"]:
        raise ValidationError("dataset count field does not match the product")
    _require_unique_set(
        completion["usableSummaryStatuses"],
        spec["statuses"],
        "usableSummaryStatuses",
    )
    _require_unique_set(
        completion["requiredRunReceiptFields"],
        COMMON_RECEIPT_FIELDS,
        "requiredRunReceiptFields",
    )

    related = pack["relatedExecutionEvidence"]
    if related["observedAt"] != RELATED_EXECUTION_AT:
        raise ValidationError("related execution evidence date has drifted")
    if related["runId"] != spec["related_run_id"]:
        raise ValidationError("related run ID does not match the retained S03 evidence")
    if related["datasetRows"] != spec["related_rows"]:
        raise ValidationError("related dataset count does not match the retained S03 evidence")
    if related["summaryStatus"] != spec["related_status"]:
        raise ValidationError("related summary status does not match the retained S03 evidence")
    if (
        related["resolvedBuildId"] != readback["buildId"]
        or related["resolvedBuildNumber"] != readback["buildNumber"]
    ):
        raise ValidationError("related run and dated build readback do not reconcile")
    if related["exactStarterInput"] is not False or related["destinationWrite"] is not False:
        raise ValidationError(
            "related execution must not be promoted into exact trial or delivery proof"
        )

    proposal = pack["approvalProposal"]
    expected_endpoint = (
        f"https://api.apify.com/v2/{spec['endpoint_segment']}/"
        f"job-atlas~{spec['slug']}/runs"
    )
    if proposal["endpoint"] != expected_endpoint:
        raise ValidationError(f"approval endpoint must equal {expected_endpoint}")
    for field in ("buildSelector", "inputPath", "inputSha256", "maxItems", "maxTotalChargeUsd"):
        expected = actor["buildSelector"] if field == "buildSelector" else starter[field]
        if proposal[field] != expected:
            raise ValidationError(f"approvalProposal.{field} must match the reviewed starter")
    if proposal["maxFollowUpRuns"] != 0:
        raise ValidationError("approval proposal must authorize no follow-up runs")
    _require_unique_set(proposal["checks"], spec["checks"], "approvalProposal.checks")
    side_effects = " ".join(proposal["sideEffects"]).lower()
    if "paid actor run" not in side_effects or "no destination" not in side_effects:
        raise ValidationError("approval side effects must name the paid run and no destination")
    if "do not retry" not in proposal["rollback"].lower():
        raise ValidationError("approval rollback must forbid an unapproved retry")
    _validate_guidance(pack_id, pack)

    return {
        "packId": pack_id,
        "actorId": actor["immutableActorId"],
        "buildSelector": actor["buildSelector"],
        "datedBuildId": readback["buildId"],
        "inputSha256": starter["inputSha256"],
        "maxItems": starter["maxItems"],
        "maxTotalChargeUsd": starter["maxTotalChargeUsd"],
        "sampleEvidenceClass": sample_meta["evidenceClass"],
        "exactTrialState": proposal["state"],
    }


def validate_all(root: Path = ROOT) -> list[dict[str, Any]]:
    """Validate the complete four-pack set in stable order."""
    results = [
        validate_pack(
            root / "first-run" / "packs" / f"{pack_id}.json",
            root=root,
        )
        for pack_id in PACK_IDS
    ]
    if [result["packId"] for result in results] != list(PACK_IDS):
        raise ValidationError("the pack set must contain each flagship exactly once")
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packs", nargs="*", help="Optional repository-relative pack JSON paths")
    args = parser.parse_args(argv)
    try:
        results = (
            [validate_pack(path) for path in args.packs]
            if args.packs
            else validate_all()
        )
    except ValidationError as error:
        print(
            json.dumps(
                {
                    "schemaVersion": "jobatlas-first-run-validation-v1",
                    "status": "invalid",
                    "error": str(error),
                },
                sort_keys=True,
            )
        )
        return 1
    print(
        json.dumps(
            {
                "schemaVersion": "jobatlas-first-run-validation-v1",
                "status": "valid",
                "packCount": len(results),
                "packs": results,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
