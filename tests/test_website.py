from __future__ import annotations

from collections import deque
from html.parser import HTMLParser
import json
from html import unescape
from pathlib import Path
import re
import subprocess
import struct
import unittest
from urllib.parse import parse_qs, unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website"
ORIGIN = "https://jobatlas.dev"
SOCIAL_IMAGE = f"{ORIGIN}/assets/job-atlas-social-card.png"

# Intent owners come from docs/seo-program.md; its first milestone adds these
# hubs and trust pages to the public surface.
EXPECTED_CANONICALS = {
    "/", "/actors", "/actors/ycombinator", "/actors/linkedin", "/actors/euraxess", "/actors/ai-job-fit-scorer",
    "/integrations", "/integrations/n8n", "/integrations/make", "/integrations/mcp",
    "/integrations/api", "/integrations/airtable", "/integrations/python", "/integrations/zapier",
    "/guides", "/guides/linkedin-jobs-api-alternatives", "/guides/linkedin-job-alerts-n8n",
    "/guides/euraxess-jobs-api-export", "/guides/ai-job-fit-scoring-api", "/contracts",
    "/about", "/methodology", "/privacy", "/changelog",
}
HUBS = {"/", "/actors", "/integrations", "/guides"}
ACTOR_PATHS = {
    "ycombinator": "/job-atlas/ycombinator-enrich-translate-normalize-scraper",
    "linkedin": "/job-atlas/linkedin-enrich-translate-normalize-scraper",
    "euraxess": "/job-atlas/euraxess-enrich-translate-normalize-scraper",
    "ai-job-fit-scorer": "/job-atlas/ai-job-fit-scorer",
}
PUBLIC_SCHEMAS = (
    "nomad-ai-job-fit-destination-v1.schema.json",
    "nomad-ai-job-fit-run-summary-v3.schema.json",
    "nomad-ai-job-fit-run-summary-v4.schema.json",
    "nomad-ai-job-fit-v1.schema.json",
)
PROGRAM_INTENT_ROUTES = {
    "/actors/ycombinator",
    "/", "/actors/linkedin", "/actors/euraxess", "/actors/ai-job-fit-scorer",
    "/integrations/n8n", "/integrations/make", "/integrations/mcp", "/integrations/api",
    "/integrations/airtable", "/integrations/python", "/integrations/zapier", "/contracts",
    "/guides/linkedin-jobs-api-alternatives", "/guides/linkedin-job-alerts-n8n",
    "/guides/euraxess-jobs-api-export", "/guides/ai-job-fit-scoring-api",
}
SITE_EVENT_SCHEMA = "jobatlas-site-event-v1"
SITE_EVENT_CACHE_VERSION = "site-event-v1-20260910"
SITE_EVENT_NAMES = {
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
}
SITE_EVENT_REQUIRED = {
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
CAMPAIGN_SOURCES = {
    "jobatlas", "devto", "linkedin", "youtube", "github", "apify", "n8n", "make"
}
CAMPAIGN_MEDIA = {
    "owned-site", "tutorial", "social", "video", "documentation", "template", "referral"
}
CAMPAIGNS = {
    "actor-discovery", "linkedin-alerts", "euraxess-tracker", "yc-tracker", "fit-scoring"
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[tuple[str, dict[str, str]]] = []
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.visible_text: list[str] = []
        self.json_ld: list[str] = []
        self._ignored_depth = 0
        self._json_depth = 0
        self._json_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()
        self.elements.append((tag, attributes))
        element_id = attributes.get("id")
        if element_id:
            if element_id in self.ids:
                self.duplicate_ids.add(element_id)
            self.ids.add(element_id)
        if tag in {"script", "style"}:
            self._ignored_depth += 1
        if tag == "script" and attributes.get("type") == "application/ld+json":
            self._json_depth += 1
            self._json_parts = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "script" and self._json_depth:
            self.json_ld.append("".join(self._json_parts).strip())
            self._json_depth -= 1
        if tag in {"script", "style"}:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._json_depth:
            self._json_parts.append(data)
        if self._ignored_depth == 0 and data.strip():
            self.visible_text.append(data.strip())


class BreadcrumbParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.items: list[tuple[str, str]] = []
        self._href: str | None = None
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() not in {"a", "span"}:
            return
        attributes = {key.lower(): value or "" for key, value in attrs}
        self._href = attributes.get("href", "") if tag.lower() == "a" else ""
        self._parts = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() not in {"a", "span"} or self._href is None:
            return
        label = re.sub(r"\s+", " ", "".join(self._parts)).strip()
        if label and label != "/":
            self.items.append((label, self._href))
        self._href = None
        self._parts = []


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


def clean_path(path: str) -> str:
    path = unquote(path).rstrip("/") or "/"
    return path if path.startswith("/") else f"/{path}"


def javascript_string_set(source: str, name: str) -> set[str]:
    match = re.search(
        rf'const {name} = new Set\("([^"]+)"\.split\(" "\)\);', source
    )
    if match is None:
        raise AssertionError(f"missing JavaScript set: {name}")
    return set(match.group(1).split())


def javascript_event_rules(source: str) -> dict[str, set[str]]:
    match = re.search(
        r'const eventRules = new Map\("([^"]+)"\.split\(" "\)', source
    )
    if match is None:
        raise AssertionError("missing JavaScript event rules")
    return {
        event: set(fields.split(","))
        for event, fields in (rule.split(":") for rule in match.group(1).split())
    }


def local_document_for_route(route: str) -> Path | None:
    route = clean_path(route)
    if route == "/":
        return WEBSITE / "index.html"
    candidate = WEBSITE / route.lstrip("/")
    if candidate.suffix:
        return candidate if candidate.is_file() else None
    index = candidate / "index.html"
    return index if index.is_file() else None


def metadata(parser: PageParser) -> dict[str, str]:
    return {
        attrs.get("name") or attrs.get("property", ""): attrs.get("content", "")
        for tag, attrs in parser.elements
        if tag == "meta" and (attrs.get("name") or attrs.get("property"))
    }


def canonical(parser: PageParser) -> list[str]:
    return [
        attrs.get("href", "")
        for tag, attrs in parser.elements
        if tag == "link" and "canonical" in attrs.get("rel", "").split()
    ]


def structured_data(parser: PageParser) -> list[object]:
    return [json.loads(blob) for blob in parser.json_ld]


class WebsiteContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pages = {route: local_document_for_route(route) for route in EXPECTED_CANONICALS}
        assert all(cls.pages.values())
        cls.parsers = {route: parse_page(document) for route, document in cls.pages.items()}
        cls.home = cls.parsers["/"]
        cls.css = (WEBSITE / "styles.css").read_text(encoding="utf-8")
        cls.detail_css = (WEBSITE / "detail.css").read_text(encoding="utf-8")
        cls.script = (WEBSITE / "script.js").read_text(encoding="utf-8")
        cls.homepage_script = (WEBSITE / "homepage.js").read_text(encoding="utf-8")

    def run_event_harness(self, config: dict[str, object]) -> dict[str, object]:
        harness = r"""
const fs = require("node:fs");
const vm = require("node:vm");
const { randomUUID } = require("node:crypto");
const source = fs.readFileSync(process.argv[1], "utf8");
const config = JSON.parse(process.argv[2]);
const emitted = [];
const dataLayer = [];
const plausible = [];
const classList = { add() {}, remove() {}, toggle() {} };
const location = {};
Object.defineProperty(location, "pathname", {
  get() {
    if (config.throwOnLocationRead) throw new Error("pathname read while privacy signal enabled");
    return config.pathname || "/";
  },
});
Object.defineProperty(location, "search", {
  get() {
    if (config.throwOnLocationRead) throw new Error("search read while privacy signal enabled");
    return config.search || "";
  },
});
class Element {}
class CustomEvent {
  constructor(type, options) { this.type = type; this.detail = options.detail; }
}
const document = {
  body: { classList, append() {} },
  addEventListener() {},
  createElement() { return { classList, setAttribute() {}, select() {}, remove() {} }; },
  execCommand() { return true; },
  querySelector(selector) {
    if (selector === 'meta[name="robots"]') {
      return config.noindex ? { content: "noindex,follow" } : null;
    }
    return null;
  },
  querySelectorAll() { return []; },
};
const window = {
  clearTimeout,
  crypto: { randomUUID },
  dataLayer,
  dispatchEvent(event) { emitted.push(event.detail); },
  doNotTrack: config.windowDnt || "0",
  innerWidth: 1280,
  location,
  matchMedia() { return { matches: false, addEventListener() {} }; },
  plausible(event, options) { plausible.push({ event, props: options.props }); },
  setTimeout,
  addEventListener() {},
};
const navigator = {
  doNotTrack: config.dnt || "0",
  globalPrivacyControl: config.gpc === true,
};
vm.runInNewContext(source, {
  CustomEvent,
  Element,
  URLSearchParams,
  console,
  document,
  navigator,
  window,
});
const callResults = (config.calls || []).map(call =>
  window.nomadAgentAnalytics.track(call.event, call.properties || {})
);
process.stdout.write(JSON.stringify({ emitted, dataLayer, plausible, callResults }));
"""
        result = subprocess.run(
            ["node", "-e", harness, str(WEBSITE / "script.js"), json.dumps(config)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_seo_program_declares_the_complete_intent_surface(self) -> None:
        program = (ROOT / "docs" / "seo-program.md").read_text(encoding="utf-8")
        for route in PROGRAM_INTENT_ROUTES:
            self.assertIn(f"`{route}`", program, route)

    def test_indexable_documents_match_expected_canonicals_and_exclude_404(self) -> None:
        discovered: dict[str, Path] = {}
        for document in WEBSITE.rglob("*.html"):
            parser = parse_page(document)
            if "noindex" in metadata(parser).get("robots", "").lower():
                self.assertEqual(canonical(parser), [], document)
                continue
            links = canonical(parser)
            self.assertEqual(len(links), 1, document)
            discovered[clean_path(urlsplit(links[0]).path)] = document
        self.assertEqual(set(discovered), EXPECTED_CANONICALS)
        self.assertEqual(discovered["/"], WEBSITE / "index.html")
        not_found = parse_page(WEBSITE / "404.html")
        self.assertIn("noindex", metadata(not_found).get("robots", "").lower())
        self.assertEqual(canonical(not_found), [])

    def test_metadata_social_cards_and_document_basics(self) -> None:
        titles: set[str] = set()
        descriptions: set[str] = set()
        for route, parser in self.parsers.items():
            with self.subTest(route=route):
                document = self.pages[route].read_text(encoding="utf-8")
                title_match = re.search(r"<title>\s*(.*?)\s*</title>", document, re.S)
                self.assertIsNotNone(title_match)
                title = unescape(re.sub(r"\s+", " ", title_match.group(1)).strip())
                self.assertGreaterEqual(len(title), 20)
                self.assertNotIn(title, titles)
                titles.add(title)
                self.assertIn('<html lang="en">', document)
                self.assertEqual(len(re.findall(r"<h1(?:\s|>)", document, re.I)), 1)
                data = metadata(parser)
                description = data.get("description", "")
                self.assertGreaterEqual(len(description), 70)
                self.assertNotIn(description, descriptions)
                descriptions.add(description)
                self.assertIn("width=device-width", data.get("viewport", ""))
                self.assertNotIn("noindex", data.get("robots", "").lower())
                self.assertEqual(canonical(parser), [ORIGIN + route])
                self.assertIn(data.get("og:type"), {"website", "article"})
                self.assertEqual(data.get("og:url"), ORIGIN + route)
                self.assertEqual(data.get("og:site_name"), "Job Atlas")
                self.assertEqual(data.get("og:image"), SOCIAL_IMAGE)
                self.assertEqual(data.get("og:image:width"), "1200")
                self.assertEqual(data.get("og:image:height"), "630")
                self.assertTrue(data.get("og:image:alt"))
                self.assertEqual(data.get("twitter:card"), "summary_large_image")
                self.assertEqual(data.get("twitter:image"), SOCIAL_IMAGE)
                self.assertEqual(
                    data.get("twitter:image:alt"), data.get("og:image:alt")
                )
                self.assertEqual(data.get("og:title"), title)
                self.assertEqual(data.get("twitter:title"), title)
                self.assertTrue(data.get("og:description"))
                self.assertTrue(data.get("twitter:description"))
                self.assertFalse(parser.duplicate_ids, parser.duplicate_ids)

    def test_valid_structured_data_and_home_catalog(self) -> None:
        for route, parser in self.parsers.items():
            with self.subTest(route=route):
                payloads = structured_data(parser)
                self.assertTrue(payloads)
                self.assertTrue(all(item.get("@context") == "https://schema.org" for item in payloads if isinstance(item, dict)))
                raw = " ".join(parser.json_ld).lower()
                self.assertNotIn("aggregaterating", raw)
                if route == "/actors/euraxess":
                    graph = payloads[0]["@graph"]
                    app = next(x for x in graph if x["@type"] == "SoftwareApplication")
                    self.assertEqual(app["offers"]["price"], "0.0009")
                    self.assertEqual(app["offers"]["priceCurrency"], "USD")
                    self.assertIn("per delivered job", app["offers"]["description"])
                else:
                    self.assertNotIn('"offers"', raw)
        graph = structured_data(self.home)[0]["@graph"]
        by_type = {entry["@type"]: entry for entry in graph}
        self.assertEqual({"Organization", "WebSite", "ItemList"}, set(by_type))
        self.assertEqual(by_type["WebSite"].get("alternateName"), "Job Atlas Job Data")
        items = by_type["ItemList"]["itemListElement"]
        self.assertEqual(len(items), len(ACTOR_PATHS))
        self.assertEqual({urlsplit(item["item"]["sameAs"]).path for item in items}, set(ACTOR_PATHS.values()))

    def test_non_hub_pages_have_valid_breadcrumbs(self) -> None:
        for route, parser in self.parsers.items():
            if route in HUBS:
                continue
            with self.subTest(route=route):
                nodes = []
                for payload in structured_data(parser):
                    nodes.extend(payload.get("@graph", [payload]))
                crumbs = [node for node in nodes if node.get("@type") == "BreadcrumbList"]
                self.assertEqual(len(crumbs), 1)
                items = crumbs[0]["itemListElement"]
                self.assertEqual(items[0]["item"], f"{ORIGIN}/")
                self.assertEqual(items[-1]["item"], ORIGIN + route)

    def test_visible_and_structured_breadcrumbs_match_exactly(self) -> None:
        for route, document in self.pages.items():
            raw = document.read_text(encoding="utf-8")
            match = re.search(
                r'<nav class="detail-breadcrumbs"[^>]*>(.*?)</nav>', raw, re.S
            )
            if match is None:
                continue
            visible = BreadcrumbParser()
            visible.feed(match.group(1))
            visible.close()
            expected = []
            for position, (name, href) in enumerate(visible.items, start=1):
                item_route = clean_path(urlsplit(href).path) if href else route
                item_url = f"{ORIGIN}/" if item_route == "/" else ORIGIN + item_route
                expected.append(
                    {"@type": "ListItem", "position": position, "name": name, "item": item_url}
                )

            nodes = []
            for payload in structured_data(self.parsers[route]):
                nodes.extend(payload.get("@graph", [payload]))
            crumbs = [node for node in nodes if node.get("@type") == "BreadcrumbList"]
            with self.subTest(route=route):
                self.assertEqual(len(crumbs), 1)
                self.assertEqual(crumbs[0]["itemListElement"], expected)

    def test_local_links_assets_and_fragments_resolve(self) -> None:
        for route, parser in self.parsers.items():
            for tag, attrs in parser.elements:
                reference = attrs.get("href") if tag in {"a", "link"} else attrs.get("src")
                if not reference or reference.startswith(("data:", "mailto:", "tel:", "javascript:")):
                    continue
                parsed = urlsplit(reference)
                if parsed.netloc and parsed.netloc != "jobatlas.dev":
                    continue
                if parsed.scheme and parsed.scheme != "https":
                    continue
                if parsed.path.startswith("/") or parsed.netloc == "jobatlas.dev":
                    target = local_document_for_route(clean_path(parsed.path))
                else:
                    candidate = (self.pages[route].parent / unquote(parsed.path or ".")).resolve()
                    target = candidate if candidate.is_file() else candidate / "index.html"
                self.assertIsNotNone(target, (route, tag, reference))
                self.assertTrue(target.is_file(), (route, tag, reference, target))
                if parsed.fragment:
                    self.assertIn(parsed.fragment, parse_page(target).ids, (route, reference))

    def test_every_intended_page_is_reachable_from_home(self) -> None:
        graph: dict[str, set[str]] = {route: set() for route in EXPECTED_CANONICALS}
        for route, parser in self.parsers.items():
            for tag, attrs in parser.elements:
                if tag != "a":
                    continue
                parsed = urlsplit(attrs.get("href", ""))
                if parsed.netloc not in {"", "jobatlas.dev"} or parsed.scheme not in {"", "https"}:
                    continue
                target = clean_path(parsed.path)
                if target in graph:
                    graph[route].add(target)
        reached, queue = {"/"}, deque(["/"])
        while queue:
            for target in graph[queue.popleft()] - reached:
                reached.add(target)
                queue.append(target)
        self.assertEqual(reached, EXPECTED_CANONICALS)

    def test_semantic_events_are_local_and_no_default_network_collector_exists(self) -> None:
        for token in (
            'CustomEvent("nomad-agent:analytics"',
            "window.nomadAgentAnalytics",
            SITE_EVENT_SCHEMA,
            "skill_source_selected",
            "install_command_copied",
        ):
            self.assertIn(token, self.script)
        self.assertNotIn("fetch(", self.script)
        self.assertNotIn("XMLHttpRequest", self.script)
        self.assertNotIn("sendBeacon", self.script)
        self.assertNotIn("localStorage", self.script)
        self.assertNotIn("sessionStorage", self.script)
        self.assertNotIn("document.cookie", self.script)

        self.assertEqual(javascript_event_rules(self.script), SITE_EVENT_REQUIRED)
        self.assertEqual(set(SITE_EVENT_REQUIRED), SITE_EVENT_NAMES)
        self.assertEqual(javascript_string_set(self.script, "canonicalPages"), EXPECTED_CANONICALS)

        annotated_names: set[str] = set()
        for route, parser in self.parsers.items():
            events = [attrs for _, attrs in parser.elements if attrs.get("data-event")]
            self.assertGreaterEqual(len(events), 2, route)
            for attrs in events:
                event = attrs["data-event"]
                annotated_names.add(event)
                with self.subTest(route=route, event=event, placement=attrs.get("data-placement")):
                    self.assertIn(event, SITE_EVENT_NAMES)
                    self.assertTrue(attrs.get("data-placement"))
                    for required in SITE_EVENT_REQUIRED[event]:
                        self.assertTrue(attrs.get(f"data-{required}"), required)

        called_names = set(
            re.findall(r"\btrack\(\s*['\"]([a-z0-9_]+)['\"]", self.script + self.homepage_script)
        )
        self.assertEqual(annotated_names | called_names, SITE_EVENT_NAMES)

        for document in WEBSITE.rglob("*.html"):
            versions = re.findall(r'/script\.js\?v=([^"\']+)', document.read_text(encoding="utf-8"))
            self.assertEqual(versions, [SITE_EVENT_CACHE_VERSION], document)

    def test_event_envelope_campaign_privacy_and_404_runtime(self) -> None:
        self.assertEqual(javascript_string_set(self.script, "campaignSources"), CAMPAIGN_SOURCES)
        self.assertEqual(javascript_string_set(self.script, "campaignMedia"), CAMPAIGN_MEDIA)
        self.assertEqual(javascript_string_set(self.script, "campaignNames"), CAMPAIGNS)

        valid = self.run_event_harness({
            "pathname": "/actors/linkedin/",
            "search": (
                "?utm_source=nomad-agent-job-scrapers&utm_medium=owned-site"
                "&utm_campaign=actor-discovery&utm_content=w04-guide"
            ),
            "calls": [
                {"event": "not_an_event", "properties": {"placement": "test"}},
                {"event": "cta_click", "properties": {}},
                {"event": "cta_click", "properties": {"placement": "free text"}},
                {"event": "cta_click", "properties": {"placement": "test"}},
                {
                    "event": "cta_click",
                    "properties": {
                        "placement": "test",
                        "label": "person@example.com",
                        "category": "navigation",
                    },
                },
                {"event": "actor_cta_click", "properties": {"placement": "test"}},
                {
                    "event": "sample_view",
                    "properties": {"placement": "test", "product": "euraxess"},
                },
                {
                    "event": "cta_click",
                    "properties": {
                        "placement": "test",
                        "category": "navigation",
                        "label": "start",
                    },
                },
                {
                    "event": "actor_cta_click",
                    "properties": {
                        "placement": "test",
                        "actor": "linkedin",
                        "label": "person@example.com",
                        "destination": "free text",
                    },
                },
            ],
        })
        self.assertEqual(
            valid["callResults"],
            [False, False, False, False, False, False, False, True, True],
        )
        self.assertEqual(valid["emitted"], valid["dataLayer"])
        self.assertEqual(len(valid["emitted"]), 3)
        self.assertEqual(len({event["eventId"] for event in valid["emitted"]}), 3)
        for detail, plausible in zip(valid["emitted"], valid["plausible"], strict=True):
            self.assertEqual(detail["schemaVersion"], SITE_EVENT_SCHEMA)
            self.assertEqual(detail["activityClass"], "unclassified")
            self.assertRegex(
                detail["eventId"],
                r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
            )
            self.assertRegex(detail["occurredAt"], r"^\d{4}-\d{2}-\d{2}T.*Z$")
            self.assertEqual(detail["page"], "/actors/linkedin")
            self.assertEqual(detail["source"], "jobatlas")
            self.assertEqual(detail["medium"], "owned-site")
            self.assertEqual(detail["campaign"], "actor-discovery")
            self.assertEqual(detail["content"], "w04-guide")
            self.assertEqual(plausible["event"], detail["event"])
            for private_key in ("schemaVersion", "eventId", "occurredAt", "activityClass", "event"):
                self.assertNotIn(private_key, plausible["props"])
            self.assertEqual(plausible["props"]["source"], "jobatlas")
        self.assertNotIn("person@example.com", json.dumps(valid["emitted"]))
        self.assertNotIn("free text", json.dumps(valid["emitted"]))

        privacy = self.run_event_harness({"gpc": True, "throwOnLocationRead": True})
        self.assertEqual(privacy["emitted"], [])
        self.assertEqual(privacy["dataLayer"], [])
        self.assertEqual(privacy["plausible"], [])

        noindex = self.run_event_harness({
            "pathname": "/private/person@example.com",
            "search": "?token=secret",
            "noindex": True,
        })
        self.assertEqual(noindex["emitted"][0]["page"], "/404")
        self.assertEqual(noindex["emitted"][0]["label"], "404")
        self.assertNotIn("private", json.dumps(noindex["emitted"]))
        self.assertNotIn("secret", json.dumps(noindex["emitted"]))

        unknown_path = self.run_event_harness({"pathname": "/private/john-doe"})
        self.assertEqual(unknown_path["emitted"][0]["page"], "/404")
        self.assertNotIn("john-doe", json.dumps(unknown_path["emitted"]))

        invalid_queries = (
            "?utm_source=jobatlas&utm_medium=owned-site",
            "?utm_source=unknown&utm_medium=owned-site&utm_campaign=actor-discovery",
            "?utm_source=devto&utm_medium=email&utm_campaign=linkedin-alerts",
            "?utm_source=devto&utm_medium=tutorial&utm_campaign=unknown",
            "?utm_source=devto&utm_medium=tutorial&utm_campaign=linkedin-alerts&utm_content=Person%40example.com",
            "?utm_source=devto&utm_source=github&utm_medium=tutorial&utm_campaign=linkedin-alerts",
        )
        for query in invalid_queries:
            with self.subTest(query=query):
                detail = self.run_event_harness({"pathname": "/", "search": query})["emitted"][0]
                for key in ("source", "medium", "campaign", "content"):
                    self.assertNotIn(key, detail)

    def test_apify_ctas_are_direct_attributed_and_cover_all_products(self) -> None:
        counts = {actor: 0 for actor in ACTOR_PATHS}
        placements: set[str] = set()
        for parser in self.parsers.values():
            for tag, attrs in parser.elements:
                if tag != "a":
                    continue
                parsed = urlsplit(attrs.get("href", ""))
                actor = attrs.get("data-actor")
                if parsed.netloc != "apify.com" or actor not in ACTOR_PATHS:
                    continue
                with self.subTest(actor=actor, href=attrs["href"]):
                    self.assertEqual(parsed.path, ACTOR_PATHS[actor])
                    self.assertEqual(attrs.get("data-event"), "actor_cta_click")
                    self.assertTrue(attrs.get("data-placement"))
                    self.assertNotIn(attrs["data-placement"], placements)
                    query = parse_qs(parsed.query)
                    self.assertEqual(query.get("utm_source"), ["nomad-agent-job-scrapers"])
                    self.assertEqual(query.get("utm_medium"), ["owned-site"])
                    self.assertEqual(query.get("utm_campaign"), ["actor-discovery"])
                    self.assertEqual(query.get("utm_content"), [attrs["data-placement"]])
                    self.assertEqual(attrs.get("target"), "_blank")
                    self.assertIn("noopener", attrs.get("rel", "").split())
                    self.assertIn("noreferrer", attrs.get("rel", "").split())
                placements.add(attrs["data-placement"])
                counts[actor] += 1
        self.assertTrue(all(counts.values()), counts)

    def test_truth_boundaries_and_price_language(self) -> None:
        visible = " ".join(text for parser in self.parsers.values() for text in parser.visible_text)
        for phrase in ("nomad-agent-job-v1", "named destination", "not affiliated with or endorsed by", "not a live release"):
            self.assertIn(phrase, visible)
        self.assertIn("$0.02 per returned shortlist result", visible)
        self.assertNotIn("$0.02 per job", visible)
        self.assertNotIn("$0.02 per run", visible)
        self.assertNotRegex(visible, r"\b(?:100|[1-9]\d(?:\.\d+)?)\s*%")

    def test_flagship_pages_disclose_per_run_limits(self) -> None:
        expected_limits = {
            "/actors/linkedin": "up to 1,000 jobs per run",
            "/actors/ycombinator": "up to 1,000 jobs per run",
            "/actors/euraxess": "up to 200 jobs per run",
            "/actors/ai-job-fit-scorer": "up to 200 unique jobs per run",
        }
        for route, disclosure in expected_limits.items():
            visible = " ".join(self.parsers[route].visible_text).lower()
            with self.subTest(route=route):
                self.assertIn(disclosure.lower(), visible)

    def test_high_volume_estimates_disclose_multiple_runs(self) -> None:
        home = " ".join(self.home.visible_text).lower()
        self.assertIn("volumes above a tool's per-run limit require multiple runs", home)

    def test_contract_overview_links_every_canonical_collector(self) -> None:
        parser = self.parsers["/contracts"]
        actor_links = {
            clean_path(urlsplit(attrs.get("href", "")).path)
            for tag, attrs in parser.elements
            if tag == "a" and attrs.get("href", "").startswith("/actors/")
        }
        self.assertTrue(
            {"/actors/linkedin", "/actors/ycombinator", "/actors/euraxess"}.issubset(actor_links)
        )

    def test_public_contracts_are_byte_identical_and_resolvable(self) -> None:
        for filename in PUBLIC_SCHEMAS:
            source = ROOT / "integrations" / "shared" / filename
            published = WEBSITE / "contracts" / filename
            with self.subTest(filename=filename):
                self.assertEqual(published.read_bytes(), source.read_bytes())
                self.assertEqual(json.loads(published.read_text(encoding="utf-8")).get("$id"), f"{ORIGIN}/contracts/{filename}")

    def test_social_card_is_exact_standard_dimensions(self) -> None:
        raw = (WEBSITE / "assets" / "job-atlas-social-card.png").read_bytes()
        self.assertEqual(raw[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(raw[12:16], b"IHDR")
        self.assertEqual(struct.unpack(">II", raw[16:24]), (1200, 630))

    def test_accessibility_responsiveness_csp_and_runtime_budget(self) -> None:
        homepage = self.pages["/"].read_text(encoding="utf-8")
        for token in ('class="skip-link"', 'aria-controls="mobile-menu"', 'aria-expanded="false"', 'aria-label="Primary navigation"'):
            self.assertIn(token, homepage)
        css = self.css + self.detail_css
        for token in (":focus-visible", "@media (max-width: 960px)", "@media (prefers-reduced-motion: reduce)"):
            self.assertIn(token, css)
        hosting = json.loads((ROOT / "firebase.json").read_text(encoding="utf-8"))["hosting"]
        self.assertEqual(hosting["site"], "nomad-agent-job-scrapers")
        self.assertEqual(hosting["public"], "website")
        security = {item["key"]: item["value"] for item in next(item["headers"] for item in hosting["headers"] if item["source"] == "**")}
        for header in ("Content-Security-Policy", "X-Frame-Options", "X-Content-Type-Options", "Referrer-Policy", "Permissions-Policy"):
            self.assertIn(header, security)
        self.assertIn("default-src 'self'", security["Content-Security-Policy"])
        self.assertIn("connect-src 'self'", security["Content-Security-Policy"])
        self.assertNotIn("'unsafe-inline'", security["Content-Security-Policy"])
        self.assertIn("clipboard-fallback", self.script)
        self.assertIn(".clipboard-fallback", self.css)
        shared = sum(path.stat().st_size for path in (WEBSITE / "styles.css", WEBSITE / "detail.css", WEBSITE / "first-visit.css", WEBSITE / "script.js", WEBSITE / "assets" / "job-atlas-mark.svg"))
        for route, document in self.pages.items():
            self.assertLess(document.stat().st_size + shared, 100 * 1024, route)


if __name__ == "__main__":
    unittest.main()
