#!/usr/bin/env python3
"""Validate and build deterministic Job Atlas measurement artifacts."""

from __future__ import annotations

import argparse
import copy
from collections import Counter
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence
from uuid import UUID


STATUS_VALUES = (
    "observed",
    "unknown",
    "unavailable",
    "not_mature",
    "not_collected",
)

BASELINE_LAYERS = (
    "deployment",
    "discovery",
    "googleIndexing",
    "bingIndexing",
    "searchDemand",
    "onsiteIntent",
    "actorExecution",
    "usefulActivation",
    "destinationDelivery",
    "retention",
    "commercial",
    "support",
)

CAMPAIGN_SOURCES = (
    "jobatlas",
    "devto",
    "linkedin",
    "youtube",
    "github",
    "apify",
    "n8n",
    "make",
)
CAMPAIGN_MEDIA = (
    "owned-site",
    "tutorial",
    "social",
    "video",
    "documentation",
    "template",
    "referral",
)
CAMPAIGNS = (
    "actor-discovery",
    "linkedin-alerts",
    "euraxess-tracker",
    "yc-tracker",
    "fit-scoring",
)
CAMPAIGN_ALIASES = {"nomad-agent-job-scrapers": "jobatlas"}
CONTENT_PATTERN = r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$"

EVENT_VOCABULARY = (
    "actor_cta_click",
    "asset_cta_click",
    "choose_actor_click",
    "contract_cta_click",
    "cta_click",
    "first_run_selected",
    "guide_cta_click",
    "history_cta_click",
    "install_command_copied",
    "integration_click",
    "integration_page_click",
    "methodology_cta_click",
    "navigation_click",
    "outbound_click",
    "page_view",
    "path_selected",
    "product_page_click",
    "product_selected",
    "sample_copied",
    "sample_download",
    "sample_source_selected",
    "sample_view",
    "skill_source_selected",
    "source_cta_click",
    "support_cta_click",
)
ACTIVITY_CLASSES = ("unclassified", "owner_test", "customer_activity")
CANONICAL_PAGES = (
    "/",
    "/404",
    "/about",
    "/actors",
    "/actors/ai-job-fit-scorer",
    "/actors/euraxess",
    "/actors/linkedin",
    "/actors/ycombinator",
    "/changelog",
    "/contracts",
    "/guides",
    "/guides/ai-job-fit-scoring-api",
    "/guides/euraxess-jobs-api-export",
    "/guides/linkedin-job-alerts-n8n",
    "/guides/linkedin-jobs-api-alternatives",
    "/integrations",
    "/integrations/airtable",
    "/integrations/api",
    "/integrations/make",
    "/integrations/mcp",
    "/integrations/n8n",
    "/integrations/python",
    "/integrations/zapier",
    "/methodology",
    "/privacy",
)
EVENT_DIMENSIONS = (
    "category",
    "label",
    "placement",
    "product",
    "actor",
    "destination",
    "format",
)
CAMPAIGN_DIMENSIONS = ("source", "medium", "campaign", "content")
EVENT_KEYS = {
    "schemaVersion",
    "eventId",
    "occurredAt",
    "event",
    "page",
    "activityClass",
    *EVENT_DIMENSIONS,
    *CAMPAIGN_DIMENSIONS,
}
EVENT_REQUIRED_KEYS = {
    "schemaVersion",
    "eventId",
    "occurredAt",
    "event",
    "page",
    "activityClass",
    "placement",
}
EVENT_REQUIRED_DIMENSIONS = {
    "actor_cta_click": {"actor"},
    "asset_cta_click": {"actor"},
    "choose_actor_click": {"actor"},
    "contract_cta_click": {"actor"},
    "cta_click": {"category", "label"},
    "first_run_selected": {"product"},
    "guide_cta_click": {"actor"},
    "history_cta_click": {"actor"},
    "install_command_copied": {"category", "product", "format"},
    "integration_click": {"label"},
    "integration_page_click": {"actor"},
    "methodology_cta_click": {"actor"},
    "navigation_click": {"category", "label"},
    "outbound_click": {"category", "label", "destination"},
    "page_view": {"category", "label"},
    "path_selected": {"label"},
    "product_page_click": {"actor"},
    "product_selected": {"product"},
    "sample_copied": {"product", "format"},
    "sample_download": {"product", "format"},
    "sample_source_selected": {"product", "format"},
    "sample_view": {"product", "format"},
    "skill_source_selected": {"category", "product"},
    "source_cta_click": {"actor"},
    "support_cta_click": {"actor"},
}
EVENT_BATCH_KEYS = {
    "$schema",
    "schemaVersion",
    "batchId",
    "observedAt",
    "source",
    "events",
}
EVENT_BATCH_SOURCES = ("synthetic_fixture", "local_owner_test", "collector_export")
EVENT_DIMENSION_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
METRIC_NAME_PATTERN = re.compile(r"^[a-z][A-Za-z0-9]{0,79}$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")
TOKEN_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,99}$")
UTC_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$")

METRIC_UNITS = ("count", "ratio", "percent", "usd", "seconds", "position")
METRIC_SEGMENTS = ("aggregate", *ACTIVITY_CLASSES)
ACTIVITY_LAYERS = {
    "onsiteIntent",
    "actorExecution",
    "usefulActivation",
    "destinationDelivery",
    "retention",
    "commercial",
    "support",
}
EVIDENCE_KINDS = (
    "repository_fixture",
    "deployment_receipt",
    "discovery_receipt",
    "google_search_console",
    "google_url_inspection",
    "bing_url_inspection",
    "site_event_batch",
    "actor_analytics",
    "activation_receipt",
    "destination_receipt",
    "retention_report",
    "commercial_report",
    "support_ledger",
    "operator_statement",
)
LAYER_QUALIFYING_EVIDENCE_KINDS = {
    "deployment": ("deployment_receipt",),
    "discovery": ("discovery_receipt",),
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
LAYER_ALLOWED_EVIDENCE_KINDS = {
    layer_name: ("repository_fixture", "operator_statement", *qualifying_kinds)
    for layer_name, qualifying_kinds in LAYER_QUALIFYING_EVIDENCE_KINDS.items()
}
LAYER_SEGMENT_QUALIFYING_EVIDENCE_KINDS = {
    layer_name: {
        segment: qualifying_kinds
        for segment in (
            ACTIVITY_CLASSES if layer_name in ACTIVITY_LAYERS else METRIC_SEGMENTS
        )
    }
    for layer_name, qualifying_kinds in LAYER_QUALIFYING_EVIDENCE_KINDS.items()
}
LAYER_SEGMENT_QUALIFYING_EVIDENCE_KINDS["actorExecution"] = {
    "unclassified": ("actor_analytics",),
    "owner_test": ("actor_analytics", "deployment_receipt"),
    "customer_activity": ("actor_analytics",),
}


class ValidationError(ValueError):
    """Raised when an input does not satisfy the public measurement contract."""


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationError(f"{path} must be an object")
    return value


def _exact_keys(value: Mapping[str, Any], required: set[str], path: str) -> None:
    missing = required - set(value)
    extra = set(value) - required
    if missing:
        raise ValidationError(f"{path} is missing fields: {', '.join(sorted(missing))}")
    if extra:
        raise ValidationError(f"{path} has unknown fields: {', '.join(sorted(extra))}")


def _nonempty_string(value: Any, path: str, *, max_length: int = 500) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValidationError(f"{path} must be a non-empty trimmed string")
    if len(value) > max_length:
        raise ValidationError(f"{path} exceeds {max_length} characters")
    return value


def _utc(value: Any, path: str) -> str:
    if not isinstance(value, str) or UTC_PATTERN.fullmatch(value) is None:
        raise ValidationError(f"{path} must be a UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as error:
        raise ValidationError(f"{path} must be a valid UTC timestamp") from error
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValidationError(f"{path} must be a UTC timestamp")
    return value


def _parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value[:-1] + "+00:00")


def _uuid(value: Any, path: str) -> str:
    if not isinstance(value, str):
        raise ValidationError(f"{path} must be a UUID")
    try:
        parsed = UUID(value)
    except (ValueError, AttributeError) as error:
        raise ValidationError(f"{path} must be a UUID") from error
    if str(parsed) != value:
        raise ValidationError(f"{path} must be a canonical lowercase UUID")
    return value


def _date(value: Any, path: str) -> date:
    if not isinstance(value, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
        raise ValidationError(f"{path} must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValidationError(f"{path} must be a valid ISO date") from error


def _count(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValidationError(f"{path} must be a non-negative integer")
    return value


def _number(value: Any, path: str) -> float | int:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValidationError(f"{path} must be a non-negative number")
    if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
        raise ValidationError(f"{path} must be finite")
    return value


def _validate_window(value: Any, path: str) -> None:
    window = _mapping(value, path)
    _exact_keys(window, {"start", "end", "days", "complete"}, path)
    start = _date(window["start"], f"{path} start")
    end = _date(window["end"], f"{path} end")
    days = window["days"]
    if isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= 90:
        raise ValidationError(f"{path} days must be an integer from 1 through 90")
    if end < start or (end - start).days + 1 != days:
        raise ValidationError(f"{path} dates must reconcile with days")
    if not isinstance(window["complete"], bool):
        raise ValidationError(f"{path} complete must be boolean")


def validate_campaign_registry(registry: Any) -> None:
    value = _mapping(registry, "campaign registry")
    keys = {
        "$schema",
        "schemaVersion",
        "registryVersion",
        "sources",
        "sourceAliases",
        "media",
        "campaigns",
        "contentPattern",
    }
    _exact_keys(value, keys, "campaign registry")
    if value["$schema"] != "campaign-registry-v1.schema.json":
        raise ValidationError("campaign registry $schema is unsupported")
    if value["schemaVersion"] != "jobatlas-campaign-registry-v1":
        raise ValidationError("campaign registry schemaVersion is unsupported")
    _date(value["registryVersion"], "campaign registry registryVersion")
    if value["sources"] != list(CAMPAIGN_SOURCES):
        raise ValidationError("campaign registry sources do not match the v1 allowlist")
    if value["sourceAliases"] != CAMPAIGN_ALIASES:
        raise ValidationError("campaign registry sourceAliases do not match the v1 aliases")
    if value["media"] != list(CAMPAIGN_MEDIA):
        raise ValidationError("campaign registry media do not match the v1 allowlist")
    if value["campaigns"] != list(CAMPAIGNS):
        raise ValidationError("campaign registry campaigns do not match the v1 allowlist")
    if value["contentPattern"] != CONTENT_PATTERN:
        raise ValidationError("campaign registry contentPattern is unsupported")


def validate_event_definitions(definitions: Any) -> None:
    value = _mapping(definitions, "event definitions")
    keys = {"$schema", "schemaVersion", "canonicalPages", "definitions"}
    _exact_keys(value, keys, "event definitions")
    if value["$schema"] != "event-definitions-v1.schema.json":
        raise ValidationError("event definitions $schema is unsupported")
    if value["schemaVersion"] != "jobatlas-site-event-definitions-v1":
        raise ValidationError("event definitions schemaVersion is unsupported")
    if value["canonicalPages"] != list(CANONICAL_PAGES):
        raise ValidationError("event definitions canonicalPages do not match the v1 allowlist")
    rows = value["definitions"]
    if not isinstance(rows, list) or len(rows) != len(EVENT_VOCABULARY):
        raise ValidationError("event definitions must cover all v1 events exactly once")
    if [row.get("event") if isinstance(row, Mapping) else None for row in rows] != list(
        EVENT_VOCABULARY
    ):
        raise ValidationError("event definitions must follow the exact v1 event vocabulary")
    denominator = {
        "event": "page_view",
        "matchDimensions": ["page", "window", "activityClass"],
    }
    for index, row in enumerate(rows):
        path = f"event definitions definitions[{index}]"
        item = _mapping(row, path)
        _exact_keys(
            item,
            {"event", "requiredDimensions", "allowedActivityClasses", "reportingDenominator"},
            path,
        )
        additional = EVENT_REQUIRED_DIMENSIONS.get(item["event"], set())
        required = ["placement"] + [
            dimension
            for dimension in EVENT_DIMENSIONS
            if dimension != "placement" and dimension in additional
        ]
        if item["requiredDimensions"] != required:
            raise ValidationError(f"{path} requiredDimensions do not match the v1 contract")
        if item["allowedActivityClasses"] != list(ACTIVITY_CLASSES):
            raise ValidationError(f"{path} allowedActivityClasses do not match the v1 contract")
        expected_denominator = None if item["event"] == "page_view" else denominator
        if item["reportingDenominator"] != expected_denominator:
            raise ValidationError(f"{path} reportingDenominator does not match the v1 contract")


def canonicalize_campaign(
    registry: Any,
    *,
    source: Any = None,
    medium: Any = None,
    campaign: Any = None,
    content: Any = None,
) -> dict[str, str]:
    """Return one complete allowlisted campaign tuple, or no campaign fields."""

    validate_campaign_registry(registry)
    core = (source, medium, campaign)
    if all(item is None for item in core) and content is None:
        return {}
    if any(item is None for item in core):
        return {}
    if not all(isinstance(item, str) for item in core):
        return {}
    canonical_source = registry["sourceAliases"].get(source, source)
    if (
        canonical_source not in registry["sources"]
        or medium not in registry["media"]
        or campaign not in registry["campaigns"]
    ):
        return {}
    if content is not None:
        if not isinstance(content, str) or re.fullmatch(registry["contentPattern"], content) is None:
            return {}
    result = {
        "source": canonical_source,
        "medium": medium,
        "campaign": campaign,
    }
    if content is not None:
        result["content"] = content
    return result


def validate_site_event(event: Any, registry: Any) -> dict[str, Any]:
    """Validate and normalize one privacy-minimized, flat site event."""

    validate_campaign_registry(registry)
    value = _mapping(event, "site event")
    unknown = set(value) - EVENT_KEYS
    if unknown:
        raise ValidationError(
            f"site event has unknown or forbidden event fields: {', '.join(sorted(unknown))}"
        )
    missing = EVENT_REQUIRED_KEYS - set(value)
    if missing:
        raise ValidationError(f"site event is missing fields: {', '.join(sorted(missing))}")
    if value["schemaVersion"] != "jobatlas-site-event-v1":
        raise ValidationError("site event schemaVersion is unsupported")
    _uuid(value["eventId"], "site event eventId UUID")
    _utc(value["occurredAt"], "site event occurredAt UTC")
    event_name = value["event"]
    if event_name not in EVENT_VOCABULARY:
        raise ValidationError("site event event is outside the event vocabulary")
    page = value["page"]
    if page not in CANONICAL_PAGES:
        raise ValidationError("site event page is outside the canonical page allowlist")
    if value["activityClass"] not in ACTIVITY_CLASSES:
        raise ValidationError("site event activityClass is unsupported")

    for dimension in EVENT_DIMENSIONS:
        if dimension in value:
            candidate = value[dimension]
            if not isinstance(candidate, str) or EVENT_DIMENSION_PATTERN.fullmatch(candidate) is None:
                raise ValidationError(
                    f"site event {dimension} must be a lowercase controlled token"
                )
    required_dimensions = EVENT_REQUIRED_DIMENSIONS.get(event_name, set())
    absent_dimensions = required_dimensions - set(value)
    if absent_dimensions:
        raise ValidationError(
            f"site event {event_name} requires: {', '.join(sorted(absent_dimensions))}"
        )

    normalized: dict[str, Any] = {
        "schemaVersion": value["schemaVersion"],
        "eventId": value["eventId"],
        "occurredAt": value["occurredAt"],
        "event": event_name,
        "page": page,
        "activityClass": value["activityClass"],
    }
    for dimension in EVENT_DIMENSIONS:
        if dimension in value:
            normalized[dimension] = value[dimension]
    campaign_fields = set(value) & set(CAMPAIGN_DIMENSIONS)
    campaign = canonicalize_campaign(
        registry,
        source=value.get("source"),
        medium=value.get("medium"),
        campaign=value.get("campaign"),
        content=value.get("content"),
    )
    if campaign_fields and (
        not campaign
        or not {"source", "medium", "campaign"} <= campaign_fields
        or ("content" in value and "content" not in campaign)
    ):
        raise ValidationError("site event campaign fields must form one valid atomic tuple")
    normalized.update(campaign)
    return normalized


def validate_event_batch(batch: Any, registry: Any) -> dict[str, Any]:
    validate_campaign_registry(registry)
    value = _mapping(batch, "event batch")
    _exact_keys(value, EVENT_BATCH_KEYS, "event batch")
    if value["$schema"] != "site-events-v1.schema.json":
        raise ValidationError("event batch $schema is unsupported")
    if value["schemaVersion"] != "jobatlas-site-event-batch-v1":
        raise ValidationError("event batch schemaVersion is unsupported")
    _uuid(value["batchId"], "event batch batchId UUID")
    _utc(value["observedAt"], "event batch observedAt UTC")
    if value["source"] not in EVENT_BATCH_SOURCES:
        raise ValidationError("event batch source is unsupported")
    if not isinstance(value["events"], list):
        raise ValidationError("event batch events must be an array")
    normalized = copy.deepcopy(dict(value))
    normalized["events"] = [validate_site_event(event, registry) for event in value["events"]]
    observed_at = _parse_utc(normalized["observedAt"])
    for index, event in enumerate(normalized["events"]):
        if _parse_utc(event["occurredAt"]) > observed_at:
            raise ValidationError(
                f"event batch events[{index}] occurredAt cannot be after batch observedAt"
            )
    return normalized


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _count_rows(counter: Counter[str]) -> list[dict[str, Any]]:
    return [{"key": key, "count": counter[key]} for key in sorted(counter)]


def summarize_events(batch: Any, registry: Any) -> dict[str, Any]:
    """Deduplicate normalized event IDs and return deterministic aggregate counts."""

    normalized = validate_event_batch(batch, registry)
    unique: dict[str, dict[str, Any]] = {}
    duplicate_count = 0
    for event in normalized["events"]:
        event_id = event["eventId"]
        prior = unique.get(event_id)
        if prior is None:
            unique[event_id] = event
        elif _canonical_json(prior) == _canonical_json(event):
            duplicate_count += 1
        else:
            raise ValidationError(f"conflicting duplicate eventId {event_id}")

    events = sorted(
        unique.values(),
        key=lambda item: (_parse_utc(item["occurredAt"]), item["eventId"]),
    )
    by_event = Counter(item["event"] for item in events)
    by_activity = Counter(item["activityClass"] for item in events)
    by_page = Counter(item["page"] for item in events)
    campaign_keys = []
    for item in events:
        if all(field in item for field in ("source", "medium", "campaign")):
            parts = [item["source"], item["medium"], item["campaign"]]
            if "content" in item:
                parts.append(item["content"])
            campaign_keys.append("/".join(parts))
    by_campaign = Counter(campaign_keys)
    digest = hashlib.sha256(_canonical_json(events)).hexdigest()
    return {
        "schemaVersion": "jobatlas-site-event-summary-v1",
        "batchId": normalized["batchId"],
        "batchSource": normalized["source"],
        "observedAt": normalized["observedAt"],
        "firstOccurredAt": events[0]["occurredAt"] if events else None,
        "lastOccurredAt": events[-1]["occurredAt"] if events else None,
        "inputCount": len(normalized["events"]),
        "uniqueCount": len(events),
        "exactDuplicateCount": duplicate_count,
        "attributedCount": len(campaign_keys),
        "unattributedCount": len(events) - len(campaign_keys),
        "byEvent": _count_rows(by_event),
        "byActivityClass": _count_rows(by_activity),
        "byPage": _count_rows(by_page),
        "byCampaign": _count_rows(by_campaign),
        "eventDigestSha256": digest,
    }


def _validate_metric(metric: Any, path: str, layer_name: str) -> tuple[str, str]:
    value = _mapping(metric, path)
    keys = {"name", "status", "unit", "value", "denominator", "reason", "segment"}
    _exact_keys(value, keys, path)
    name = value["name"]
    if not isinstance(name, str) or METRIC_NAME_PATTERN.fullmatch(name) is None:
        raise ValidationError(f"{path} name is invalid")
    unit = value["unit"]
    if unit not in METRIC_UNITS:
        raise ValidationError(f"{path} unit is unsupported")
    segment = value["segment"]
    if segment not in METRIC_SEGMENTS:
        raise ValidationError(f"{path} segment is unsupported")
    if layer_name in ACTIVITY_LAYERS and segment == "aggregate":
        raise ValidationError(f"{path} segment cannot pool activity classes")

    status = value["status"]
    if status not in STATUS_VALUES:
        raise ValidationError(f"{path} status is unsupported")
    metric_value = value["value"]
    reason = value["reason"]
    if status == "observed":
        if metric_value is None:
            raise ValidationError(f"{path} observed metric requires a value")
        if unit == "count":
            _count(metric_value, f"{path} value")
        else:
            numeric_value = _number(metric_value, f"{path} value")
            if unit == "ratio" and numeric_value > 1:
                raise ValidationError(f"{path} ratio value cannot exceed 1")
            if unit == "percent" and numeric_value > 100:
                raise ValidationError(f"{path} percent value cannot exceed 100")
        if reason is not None:
            raise ValidationError(f"{path} observed metric reason must be null")
    else:
        if metric_value is not None:
            raise ValidationError(f"{path} nonobserved metric value must be null")
        _nonempty_string(reason, f"{path} metric reason")

    denominator = value["denominator"]
    if unit in ("ratio", "percent") and metric_value is not None:
        denominator_value = _mapping(denominator, f"{path} denominator")
        _exact_keys(denominator_value, {"metric", "value"}, f"{path} denominator")
        denominator_name = denominator_value["metric"]
        if not isinstance(denominator_name, str) or METRIC_NAME_PATTERN.fullmatch(denominator_name) is None:
            raise ValidationError(f"{path} denominator metric is invalid")
        numeric_denominator = _count(
            denominator_value["value"], f"{path} denominator value"
        )
        if numeric_denominator <= 0:
            raise ValidationError(f"{path} requires a positive denominator")
    elif denominator is not None:
        raise ValidationError(f"{path} denominator is only allowed for observed ratio or percent metrics")
    return name, segment


def _validate_evidence(evidence: Any, path: str) -> None:
    value = _mapping(evidence, path)
    _exact_keys(value, {"kind", "observedAt", "reference"}, path)
    if value["kind"] not in EVIDENCE_KINDS:
        raise ValidationError(f"{path} kind is unsupported")
    _utc(value["observedAt"], f"{path} observedAt UTC")
    _nonempty_string(value["reference"], f"{path} reference", max_length=240)


def _validate_count_rows(rows: Any, path: str) -> int:
    if not isinstance(rows, list):
        raise ValidationError(f"{path} must be an array")
    last_key: str | None = None
    total = 0
    for index, row in enumerate(rows):
        item_path = f"{path}[{index}]"
        value = _mapping(row, item_path)
        _exact_keys(value, {"key", "count"}, item_path)
        key = _nonempty_string(value["key"], f"{item_path} key", max_length=240)
        if last_key is not None and key <= last_key:
            raise ValidationError(f"{path} keys must be unique and sorted")
        last_key = key
        count = _count(value["count"], f"{item_path} count")
        if count == 0:
            raise ValidationError(f"{item_path} count must be positive")
        total += count
    return total


def _validate_event_summary(summary: Any, path: str = "eventSummary") -> str:
    value = _mapping(summary, path)
    keys = {
        "schemaVersion",
        "batchId",
        "batchSource",
        "observedAt",
        "firstOccurredAt",
        "lastOccurredAt",
        "inputCount",
        "uniqueCount",
        "exactDuplicateCount",
        "attributedCount",
        "unattributedCount",
        "byEvent",
        "byActivityClass",
        "byPage",
        "byCampaign",
        "eventDigestSha256",
    }
    _exact_keys(value, keys, path)
    if value["schemaVersion"] != "jobatlas-site-event-summary-v1":
        raise ValidationError(f"{path} schemaVersion is unsupported")
    _uuid(value["batchId"], f"{path} batchId UUID")
    if value["batchSource"] not in EVENT_BATCH_SOURCES:
        raise ValidationError(f"{path} batchSource is unsupported")
    observed_at = _utc(value["observedAt"], f"{path} observedAt UTC")
    input_count = _count(value["inputCount"], f"{path} inputCount")
    unique_count = _count(value["uniqueCount"], f"{path} uniqueCount")
    duplicates = _count(value["exactDuplicateCount"], f"{path} exactDuplicateCount")
    attributed = _count(value["attributedCount"], f"{path} attributedCount")
    unattributed = _count(value["unattributedCount"], f"{path} unattributedCount")
    if input_count != unique_count + duplicates:
        raise ValidationError(f"{path} input count does not reconcile")
    if unique_count != attributed + unattributed:
        raise ValidationError(f"{path} attribution counts do not reconcile")
    first_occurred_at = value["firstOccurredAt"]
    last_occurred_at = value["lastOccurredAt"]
    if unique_count == 0:
        if first_occurred_at is not None or last_occurred_at is not None:
            raise ValidationError(f"{path} empty summary requires a null event-time range")
    else:
        first = _utc(first_occurred_at, f"{path} firstOccurredAt UTC")
        last = _utc(last_occurred_at, f"{path} lastOccurredAt UTC")
        if _parse_utc(first) > _parse_utc(last):
            raise ValidationError(f"{path} event-time range is reversed")
        if _parse_utc(last) > _parse_utc(observed_at):
            raise ValidationError(f"{path} lastOccurredAt cannot be after observedAt")
    event_total = _validate_count_rows(value["byEvent"], f"{path} byEvent")
    activity_total = _validate_count_rows(value["byActivityClass"], f"{path} byActivityClass")
    page_total = _validate_count_rows(value["byPage"], f"{path} byPage")
    campaign_total = _validate_count_rows(value["byCampaign"], f"{path} byCampaign")
    if (event_total, activity_total, page_total) != (unique_count, unique_count, unique_count):
        raise ValidationError(f"{path} event counts do not reconcile")
    if campaign_total != attributed:
        raise ValidationError(f"{path} campaign counts do not reconcile")
    activity_keys = {row["key"] for row in value["byActivityClass"]}
    if not activity_keys <= set(ACTIVITY_CLASSES):
        raise ValidationError(f"{path} activity classes are unsupported")
    event_keys = {row["key"] for row in value["byEvent"]}
    if not event_keys <= set(EVENT_VOCABULARY):
        raise ValidationError(f"{path} event names are unsupported")
    page_keys = {row["key"] for row in value["byPage"]}
    if not page_keys <= set(CANONICAL_PAGES):
        raise ValidationError(f"{path} page keys are unsupported")
    for row in value["byCampaign"]:
        parts = row["key"].split("/")
        if (
            len(parts) not in (3, 4)
            or parts[0] not in CAMPAIGN_SOURCES
            or parts[1] not in CAMPAIGN_MEDIA
            or parts[2] not in CAMPAIGNS
            or (len(parts) == 4 and re.fullmatch(CONTENT_PATTERN, parts[3]) is None)
        ):
            raise ValidationError(f"{path} campaign keys are unsupported")
    digest = value["eventDigestSha256"]
    if not isinstance(digest, str) or DIGEST_PATTERN.fullmatch(digest) is None:
        raise ValidationError(f"{path} eventDigestSha256 is invalid")
    return observed_at


def validate_baseline(baseline: Any) -> None:
    value = _mapping(baseline, "baseline")
    keys = {
        "$schema",
        "schemaVersion",
        "baselineId",
        "generatedAt",
        "siteUrl",
        "sourceRevision",
        "window",
        "campaignRegistryVersion",
        "changePoints",
        "layers",
        "eventSummary",
    }
    _exact_keys(value, keys, "baseline")
    if value["$schema"] != "baseline-v1.schema.json":
        raise ValidationError("baseline $schema is unsupported")
    if value["schemaVersion"] != "jobatlas-measurement-baseline-v1":
        raise ValidationError("baseline schemaVersion is unsupported")
    if not isinstance(value["baselineId"], str) or TOKEN_PATTERN.fullmatch(value["baselineId"]) is None:
        raise ValidationError("baseline baselineId is invalid")
    generated_at = _utc(value["generatedAt"], "baseline generatedAt UTC")
    if value["siteUrl"] != "https://jobatlas.dev/":
        raise ValidationError("baseline siteUrl must be https://jobatlas.dev/")
    if not isinstance(value["sourceRevision"], str) or SHA_PATTERN.fullmatch(value["sourceRevision"]) is None:
        raise ValidationError("baseline sourceRevision must be a lowercase 40-character revision")
    _date(value["campaignRegistryVersion"], "baseline campaignRegistryVersion")

    _validate_window(value["window"], "baseline window")

    change_points = value["changePoints"]
    if not isinstance(change_points, list) or not change_points:
        raise ValidationError("baseline changePoints must be a non-empty array")
    seen_change_points: set[str] = set()
    prior_change_point: tuple[str, str] | None = None
    for index, change_point in enumerate(change_points):
        path = f"baseline changePoints[{index}]"
        item = _mapping(change_point, path)
        _exact_keys(item, {"id", "occurredAt", "description", "reference"}, path)
        change_id = item["id"]
        if not isinstance(change_id, str) or TOKEN_PATTERN.fullmatch(change_id) is None:
            raise ValidationError(f"{path} id is invalid")
        if change_id in seen_change_points:
            raise ValidationError(f"{path} id is duplicated")
        seen_change_points.add(change_id)
        occurred_at = _utc(item["occurredAt"], f"{path} occurredAt UTC")
        if _parse_utc(occurred_at) > _parse_utc(generated_at):
            raise ValidationError(f"{path} cannot occur after baseline generatedAt")
        _nonempty_string(item["description"], f"{path} description")
        _nonempty_string(item["reference"], f"{path} reference", max_length=240)
        sort_key = (occurred_at, change_id)
        if prior_change_point is not None and sort_key <= prior_change_point:
            raise ValidationError("baseline changePoints must be unique and sorted")
        prior_change_point = sort_key

    layers = _mapping(value["layers"], "baseline layers")
    if set(layers) != set(BASELINE_LAYERS):
        raise ValidationError("baseline layers must contain the exact v1 layer set")
    for layer_name in BASELINE_LAYERS:
        path = f"baseline layers {layer_name}"
        layer = _mapping(layers[layer_name], path)
        _exact_keys(
            layer,
            {
                "status",
                "reason",
                "asOf",
                "window",
                "ownerTestsExcluded",
                "metrics",
                "evidence",
                "limitations",
            },
            path,
        )
        status = layer["status"]
        if status not in STATUS_VALUES:
            raise ValidationError(f"{path} status is unsupported")
        as_of = _utc(layer["asOf"], f"{path} asOf UTC")
        if _parse_utc(as_of) > _parse_utc(generated_at):
            raise ValidationError(f"{path} asOf cannot be after baseline generatedAt")
        if layer["window"] is not None:
            _validate_window(layer["window"], f"{path} window")
            if _date(layer["window"]["end"], f"{path} window end") > _parse_utc(as_of).date():
                raise ValidationError(f"{path} window cannot end after asOf")
        if layer_name in ACTIVITY_LAYERS:
            if not isinstance(layer["ownerTestsExcluded"], bool):
                raise ValidationError(f"{path} ownerTestsExcluded must be explicit")
        elif layer["ownerTestsExcluded"] is not None:
            raise ValidationError(f"{path} ownerTestsExcluded must be null")
        if not isinstance(layer["metrics"], list):
            raise ValidationError(f"{path} metrics must be an array")
        metrics_by_identity: dict[tuple[str, str], Mapping[str, Any]] = {}
        for index, metric in enumerate(layer["metrics"]):
            identity = _validate_metric(metric, f"{path} metrics[{index}]", layer_name)
            if identity in metrics_by_identity:
                raise ValidationError(f"{path} has duplicate metric {identity[0]} for {identity[1]}")
            metrics_by_identity[identity] = metric
        for index, metric in enumerate(layer["metrics"]):
            denominator = metric["denominator"]
            if denominator is None:
                continue
            denominator_identity = (denominator["metric"], metric["segment"])
            referenced_metric = metrics_by_identity.get(denominator_identity)
            if (
                referenced_metric is None
                or referenced_metric is metric
                or referenced_metric["status"] != "observed"
                or referenced_metric["unit"] != "count"
            ):
                raise ValidationError(
                    f"{path} metrics[{index}] denominator metric must name an observed "
                    "count metric in the same layer and segment"
                )
            if denominator["value"] != referenced_metric["value"]:
                raise ValidationError(
                    f"{path} metrics[{index}] denominator value must match observed metric "
                    f"{denominator['metric']} value"
                )
        if not isinstance(layer["evidence"], list):
            raise ValidationError(f"{path} evidence must be an array")
        for index, evidence in enumerate(layer["evidence"]):
            _validate_evidence(evidence, f"{path} evidence[{index}]")
            if evidence["kind"] not in LAYER_ALLOWED_EVIDENCE_KINDS[layer_name]:
                raise ValidationError(
                    f"{path} evidence kind {evidence['kind']} is not allowed for {layer_name}"
                )
            if _parse_utc(evidence["observedAt"]) > _parse_utc(as_of):
                raise ValidationError(f"{path} evidence cannot be after asOf")
        if not isinstance(layer["limitations"], list):
            raise ValidationError(f"{path} limitations must be an array")
        for index, limitation in enumerate(layer["limitations"]):
            _nonempty_string(limitation, f"{path} limitations[{index}]")

        observed_metrics = [
            metric for metric in layer["metrics"] if metric["status"] == "observed"
        ]
        for metric in observed_metrics:
            qualifying_kinds = LAYER_SEGMENT_QUALIFYING_EVIDENCE_KINDS[
                layer_name
            ][metric["segment"]]
            if not any(
                evidence["kind"] in qualifying_kinds for evidence in layer["evidence"]
            ):
                raise ValidationError(
                    f"qualifying evidence is required for {layer_name} observed metric "
                    f"{metric['name']} segment {metric['segment']}"
                )
        if status == "observed":
            if layer["reason"] is not None:
                raise ValidationError(f"{path} observed layer reason must be null")
            if not observed_metrics:
                raise ValidationError(f"{path} observed layer needs a measured metric")
        else:
            _nonempty_string(layer["reason"], f"{path} layer reason")
        if not any(metric["status"] == status for metric in layer["metrics"]):
            raise ValidationError(f"{path} needs a metric matching the layer status")

    if value["eventSummary"] is not None:
        event_summary_observed_at = _validate_event_summary(value["eventSummary"])
        if _parse_utc(event_summary_observed_at) > _parse_utc(generated_at):
            raise ValidationError(
                "eventSummary observedAt cannot be after baseline generatedAt"
            )


def build_baseline(
    baseline: Any,
    registry: Any,
    event_batch: Any | None = None,
) -> dict[str, Any]:
    """Validate inputs and return a stable, canonically ordered baseline."""

    validate_campaign_registry(registry)
    validate_baseline(baseline)
    if baseline["campaignRegistryVersion"] != registry["registryVersion"]:
        raise ValidationError("baseline campaignRegistryVersion does not match campaign registry")
    result = copy.deepcopy(dict(baseline))
    result["changePoints"] = sorted(
        copy.deepcopy(baseline["changePoints"]),
        key=lambda item: (item["occurredAt"], item["id"]),
    )
    result["layers"] = {name: copy.deepcopy(baseline["layers"][name]) for name in BASELINE_LAYERS}
    for layer in result["layers"].values():
        layer["metrics"] = sorted(layer["metrics"], key=lambda item: (item["name"], item["segment"]))
        layer["evidence"] = sorted(
            layer["evidence"],
            key=lambda item: (item["kind"], item["observedAt"], item["reference"]),
        )
        layer["limitations"] = sorted(layer["limitations"])
    if event_batch is not None:
        result["eventSummary"] = summarize_events(event_batch, registry)
    validate_baseline(result)
    return result


def _load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str, value: Any) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    registry = commands.add_parser("validate-registry", help="validate a campaign registry")
    registry.add_argument("--campaigns", required=True)

    definitions = commands.add_parser("validate-definitions", help="validate event definitions")
    definitions.add_argument("--definitions", required=True)

    events = commands.add_parser("summarize-events", help="validate and summarize site events")
    events.add_argument("--events", required=True)
    events.add_argument("--campaigns", required=True)
    events.add_argument("--output", required=True)

    baseline = commands.add_parser("validate-baseline", help="validate a baseline")
    baseline.add_argument("--baseline", required=True)

    build = commands.add_parser("build", help="validate and build a deterministic baseline")
    build.add_argument("--baseline", required=True)
    build.add_argument("--campaigns", required=True)
    build.add_argument("--events")
    build.add_argument("--output", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "validate-registry":
            validate_campaign_registry(_load_json(args.campaigns))
        elif args.command == "validate-definitions":
            validate_event_definitions(_load_json(args.definitions))
        elif args.command == "summarize-events":
            summary = summarize_events(_load_json(args.events), _load_json(args.campaigns))
            _write_json(args.output, summary)
        elif args.command == "validate-baseline":
            validate_baseline(_load_json(args.baseline))
        elif args.command == "build":
            event_batch = _load_json(args.events) if args.events else None
            result = build_baseline(
                _load_json(args.baseline),
                _load_json(args.campaigns),
                event_batch,
            )
            _write_json(args.output, result)
        else:  # pragma: no cover - argparse enforces the command.
            raise ValidationError(f"unsupported command {args.command}")
    except (OSError, json.JSONDecodeError, ValidationError) as error:
        print(f"measurement validation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
