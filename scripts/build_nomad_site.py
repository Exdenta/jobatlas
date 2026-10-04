"""Build the independent Nomad Agent public site from an observed Actor catalogue."""
from __future__ import annotations

import argparse
import hashlib
from html import escape
import json
from pathlib import Path
import subprocess
from typing import TypedDict
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'nomad-site'
OUTPUT = ROOT / 'website-nomad-agent'
ORIGIN = 'https://nomadagent.dev'
GITHUB = 'https://github.com/Exdenta/jobatlas'
VERSION = 'nomad-20261004'


class Actor(TypedDict):
    """Public listing and schema observations, never execution or delivery proof."""
    slug: str
    actorId: str
    title: str
    description: str
    url: str
    isPublic: bool
    isDeprecated: bool
    family: str
    schemaSelector: str  # The schema was observed through the latest selector.
    buildId: str
    buildNumber: str
    inputExample: dict | None  # None means no schema-validated starter is available.
    inputSchema: dict | None  # Raw external JSON Schema; None means unavailable.


class ActorIcon(TypedDict):
    """Observed public Apify image; sha256 identifies the original PNG bytes."""
    actorId: str
    sourceUrl: str
    file: str
    sha256: str
    bytes: int


class IconSnapshot(TypedDict):
    schemaVersion: str
    observedAt: str
    icons: dict[str, ActorIcon]


FEATURED = ['all-jobs-scraper', 'europe-jobs-bundle', 'remote-boards-scraper',
            'researcher-bundle', 'web-dev-bundle', 'ml-ai-dev-bundle']
SHORT_NAMES = {
    'all-jobs-scraper': 'All Jobs', 'europe-jobs-bundle': 'Europe Jobs',
    'american-jobs-bundle': 'American Jobs', 'remote-boards-scraper': 'Remote Jobs',
    'researcher-bundle': 'Research Jobs', 'web-dev-bundle': 'Web Developer Jobs',
    'ml-ai-dev-bundle': 'AI & ML Jobs', 'company-careers-bundle': 'Company Careers',
    'web-search-scraper': 'Job Search',
}
GROUPS = {
    'Bundles': ['all-jobs-scraper', 'europe-jobs-bundle', 'american-jobs-bundle',
                'remote-boards-scraper', 'researcher-bundle', 'web-dev-bundle',
                'ml-ai-dev-bundle', 'company-careers-bundle', 'web-search-scraper'],
    'Research & academia': ['academicpositions-scraper', 'euraxess-scraper',
                'jobs-ac-uk-scraper', 'ikerbasque-scraper', 'math-ku-phd-scraper', 'ub-doctoral-scraper'],
    'Tech & startups': ['ai-jobs-net-scraper', 'builtin-scraper', 'foorilla-ai-jobs-scraper',
                'hackernews-scraper', 'justjoinit-scraper', 'nofluffjobs-scraper',
                'tecnoempleo-scraper', 'wellfound-scraper', 'ycombinator-was-scraper'],
    'UN & NGOs': ['devex-jobs-scraper', 'devex-scraper', 'impactpool-scraper',
                'reliefweb-scraper', 'un-careers-scraper', 'unjobs-scraper'],
    'Company boards': ['ashby-jobs-scraper', 'greenhouse-jobs-scraper',
                'lever-jobs-scraper', 'workable-jobs-scraper'],
}


def group(actor: Actor) -> str:
    return next((name for name, slugs in GROUPS.items() if actor['slug'] in slugs), 'General job boards')


def short_name(actor: Actor) -> str:
    return SHORT_NAMES.get(actor['slug'], actor['title'].split(' — ')[0].split(' | ')[0])


def link(url: str, text: str, cls: str = '') -> str:
    download = ' download' if url.startswith('/samples/') else ''
    return f'<a href="{escape(url, quote=True)}" class="{escape(cls)}"{download}>{escape(text)}</a>'


def heading(kicker: str, title: str, text: str = '') -> str:
    return f'<div class="section-heading"><p class="section-kicker">{escape(kicker)}</p><h2>{escape(title)}</h2>' + (f'<p>{text}</p>' if text else '') + '</div>'


def section(body: str, cls: str = '', ident: str = '') -> str:
    return f'<section class="home-section {cls}"' + (f' id="{ident}"' if ident else '') + f'><div class="home-container">{body}</div></section>'


def page(title: str, description: str, route: str, body: str, *, noindex: bool = False, structured: dict | None = None) -> str:
    if route != '/':
        body = body.replace('<h2>', '<h1>', 1).replace('</h2>', '</h1>', 1)
    style_version = hashlib.sha256((SOURCE/'site.css').read_bytes()).hexdigest()[:12]
    canonical = '' if noindex else f'<link rel="canonical" href="{ORIGIN}{route}" />'
    seo = json.dumps(structured or {'@context': 'https://schema.org', '@type': 'WebPage', 'name': title, 'url': ORIGIN + route, 'description': description}, ensure_ascii=False).replace('<', '\\u003c')
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{escape(title)} | Nomad Agent</title><meta name="description" content="{escape(description, quote=True)}" />{canonical}
<meta name="robots" content="{'noindex,follow' if noindex else 'index,follow'}" />
<meta property="og:title" content="{escape(title, quote=True)} | Nomad Agent" /><meta property="og:description" content="{escape(description, quote=True)}" />
<meta property="og:type" content="website" /><meta property="og:url" content="{ORIGIN}{route}" />
<meta property="og:image" content="{ORIGIN}/assets/social-card.jpg" /><meta name="twitter:card" content="summary_large_image" />
<link rel="icon" href="/assets/nomad-agent-mark.png" />
<link rel="stylesheet" href="/styles.css?v={VERSION}" /><link rel="stylesheet" href="/first-visit.css?v={VERSION}" />
<link rel="stylesheet" href="/site.css?v={style_version}" /><script src="/site.js?v={VERSION}" defer></script>
<script type="application/ld+json">{seo}</script></head>
<body class="nomad-home"><a class="skip-link" href="#main-content">Skip to content</a>
<header class="topbar"><nav class="nav-container" aria-label="Primary navigation">
<a class="brand" href="/" aria-label="Nomad Agent home"><img src="/assets/nomad-agent-mark.png" alt="" width="42" height="42" /><span>Nomad Agent</span></a>
<div class="desktop-nav">{link('/actors', 'Actors')}{link('/guides', 'Workflows')}{link('/docs', 'Docs')}{link('/about', 'About')}</div>
<div class="nav-actions">{link('https://jobatlas.dev/', 'Job Atlas ↗', 'nav-link')}{link('/actors', 'Choose an Actor', 'nav-primary')}</div>
<div class="mobile-tools"><button class="menu-button" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Open navigation"><span></span><span></span><span></span></button></div>
</nav><nav class="mobile-menu" id="mobile-menu" aria-label="Mobile navigation" hidden>{link('/actors','Actors')}{link('/guides','Workflows')}{link('/docs','Docs')}{link('/about','About')}{link('https://jobatlas.dev/','Job Atlas ↗')}</nav></header>
<main id="main-content">{body}</main>
<footer class="site-footer site-footer-expanded"><div class="footer-container footer-grid">
<div class="footer-brand"><a class="brand" href="/">Nomad Agent</a><p>Source facts for your next job feed, tracker, or alert.</p><small>Independent tools. Original source links.</small></div>
<div class="footer-links"><strong>Explore</strong>{link('/actors','All Actors')}{link('/guides','Workflows')}{link('/docs','Getting started')}</div>
<div class="footer-links"><strong>Reference</strong>{link('/docs/output','Data format')}{link('/about','About')}{link('/privacy','Privacy')}</div>
<div class="footer-links"><strong>Elsewhere</strong>{link('https://apify.com/nomad-agent','Nomad Agent on Apify ↗')}{link('https://jobatlas.dev/','Normalized data at Job Atlas ↗')}{link(GITHUB,'GitHub ↗')}</div></div>
<div class="footer-bottom"><span>Nomad Agent · {VERSION[-8:-4]}</span><span>Unofficial, independent tools. No affiliation with source operators. Availability and fields depend on the selected Actor.</span></div></footer>
</body></html>'''


def card(actor: Actor, number: int, *, filtering: bool = False) -> str:
    attrs = f' data-actor-card data-group="{escape(group(actor))}" data-search="{escape((short_name(actor)+" "+actor["title"]+" "+actor["description"]).lower(), quote=True)}"' if filtering else ''
    return f'''<article class="product-card nomad-card"{attrs}>
<div class="actor-ticket"><span>NA / {number:02d}</span><span>{escape(group(actor))}</span></div>
<div class="nomad-card-heading"><img class="nomad-actor-icon" src="/assets/actors/{escape(actor['slug'])}.png" alt="" width="48" height="48" loading="lazy" decoding="async" /><h3>{escape(short_name(actor))}</h3></div><p>{escape(actor['description'])}</p>
<div class="product-actions">{link('/actors/'+actor['slug'], 'Details & first run →')}{link(actor['url'], 'Open on Apify ↗')}</div></article>'''


def steps() -> str:
    return '''<ol class="onboarding-steps"><li><span>01 / Choose</span><h3>Pick your sources.</h3><p>Use one board for a focused feed, or a bundle for a broader search.</p></li><li><span>02 / Try</span><h3>Start with a few jobs.</h3><p>Open the Actor on Apify, check its input and pricing, and set a small result limit and a cost cap.</p></li><li><span>03 / Connect</span><h3>Make the data useful.</h3><p>Export the results, map them into your app, or connect a spreadsheet. Test the destination before scheduling.</p></li></ol>'''


def workflows() -> str:
    cards = [
        ('01', 'For your spreadsheet', 'Keep a useful job tracker.', 'Keep source IDs, descriptions, and application links together. Update by job identity instead of adding duplicates.', 'job-tracker'),
        ('02', 'For your alerts', 'Send the jobs you want.', 'Apply the Actor’s supported filters, then connect a destination you control. Keep a stable scope for recurring searches.', 'job-alerts'),
        ('03', 'For research careers', 'Bring opportunities together.', 'Start with a research bundle or an academic board. Read the original requirements, funding, and deadlines.', 'research-jobs'),
        ('04', 'For your coding agent', 'Give your agent source data.', 'Inspect the exact Actor schema, request a bounded run, and keep its original job records available.', 'coding-agent'),
    ]
    return '<div class="nomad-workflows">' + ''.join(f'<a class="nomad-workflow" href="/guides/{slug}"><span class="workflow-number">{num}</span><p class="section-kicker">{audience}</p><h3>{title}</h3><p>{text}</p><strong>See the workflow <span>→</span></strong></a>' for num,audience,title,text,slug in cards) + '</div>'


def sample_panel(sample: dict) -> str:
    return f'''<div class="sample-card"><div class="sample-label"><span>One simple job row</span><span>Illustration</span></div>
<h2>{escape(sample['title'])}</h2><p class="sample-company">{escape(sample['company'])}</p>
<dl><div><dt>Location</dt><dd>{escape(sample['locations'][0])}</dd></div><div><dt>Work arrangement</dt><dd>{escape(sample['workType'])}</dd></div><div><dt>Original description</dt><dd>Text + HTML</dd></div><div><dt>Application link</dt><dd>Original source URL</dd></div></dl>
<p class="sample-note">A fictional example of the current simple row format. Each Actor’s actual output can differ.</p><div class="sample-actions">{link('/samples/job-row.json','Download JSON')}{link('/docs/output','Explore the data →')}</div></div>'''


def homepage(actors: list[Actor], sample: dict) -> str:
    summaries = {
        'all-jobs-scraper': 'Search across job boards in one feed. Keep original descriptions and source links ready for an alert, tracker, or application.',
        'europe-jobs-bundle': 'Bring European job sources together. Keep source-supplied locations and original descriptions available for your search.',
        'remote-boards-scraper': 'Bring remote-job boards into one feed. Read original location and eligibility requirements before treating a role as worldwide.',
        'researcher-bundle': 'Bring PhD, postdoc, and research opportunities together. Keep original requirements and deadlines when the source provides them.',
        'web-dev-bundle': 'Find web and software development roles across several boards. Keep original job details and application links together.',
        'ml-ai-dev-bundle': 'Find AI, machine-learning, and data roles across several boards. Returns source job data without AI ranking.',
    }
    by_slug = {a['slug']: dict(a, description=summaries.get(a['slug'], a['description'])) for a in actors}
    intro = f'''<section class="home-hero"><div class="home-container hero-grid"><div class="hero-copy"><p class="eyebrow">Nomad Agent / Simple job data</p>
<h1>Build job feeds,<br />alerts, and <em>trackers.</em></h1><p class="hero-lede">Find job postings from the boards you care about. Keep source facts, original descriptions, and application links ready for your next workflow.</p>
<p class="hero-setup">Choose a single source or a bundle. Each <strong>Actor</strong> is a ready-to-run tool on Apify that returns data you can export or use in your app.</p>
<div class="hero-actions">{link('/actors','Choose an Actor →','button button-large nomad-cream-button')}{link('/docs/output','Explore the data','button button-large button-light')}</div>
<ul class="hero-facts"><li>Source-linked records</li><li>Single boards & bundles</li><li>Start with a small run</li></ul></div>{sample_panel(sample)}</div></section>'''
    featured = section(heading('Choose your starting point','One board. Or a broader view.','Pick a focused feed or collect across several sources. Open each Actor for its supported filters and current pricing.') + '<div class="product-grid nomad-featured">' + ''.join(card(by_slug[s],i+1) for i,s in enumerate(FEATURED) if s in by_slug) + '</div>' + f'<div class="section-tail">{link("/actors",f"Browse all {len(actors)} Actors →","text-link")}</div>')
    start = section(heading('Your first useful run','Choose. Try. Connect.') + steps(), 'section-paper')
    work = section(heading('Built around your work','What are you building?','A job feed is a starting point. Connect it to the workflow that matters to you.') + workflows(), 'nomad-green')
    faq = section(heading('Before your first run','A few useful answers.') + '''<div class="home-faq nomad-faq"><details><summary>What does “simple” mean?</summary><p>Simple readers return source-supplied facts in flat job rows, with original descriptions and links. They do not enrich or translate those rows with AI. Some source-specific products keep their own schemas; check the selected Actor’s Output tab.</p></details><details><summary>How much does a run cost?</summary><p>Pricing varies by Actor. Check its current Pricing tab, set Maximum cost per run, and start with a small result limit. The number of returned jobs does not necessarily limit scanning or total processing cost.</p></details><details><summary>Can a search return no jobs?</summary><p>Yes. Filters, source availability, deadlines, and repeat suppression can leave no matching jobs. Read the run summary where available. A successful run does not promise a fixed number of results.</p></details><details><summary>What if I need normalized fields or AI processing?</summary><p>Visit <a href="https://jobatlas.dev/">Job Atlas</a> for separate normalized job Actors and fit scoring. Their inputs, outputs, defaults, and pricing differ from these simple feeds.</p></details></div>''', 'section-paper')
    close = section(heading('Your next workflow','Start with one source.','Try a few results and see how the data fits what you’re building.') + '<div class="hero-actions">' + link('/actors','Choose an Actor →','button button-dark') + link('/docs','Read the quickstart','button button-outline') + '</div>', 'nomad-close')
    return intro + featured + start + work + faq + close


def actor_page(actor: Actor, observed: str) -> str:
    starter = actor['inputExample']
    start = '<p>Read this Actor’s current Input tab and construct a small request using its documented fields.</p>'
    if starter is not None:
        start = f'''<p>This starter was schema-checked on {observed}. Recheck the current Input tab before running.</p><div class="nomad-code"><div class="code-title"><span>Starter input</span><button type="button" data-copy="starter-json">Copy JSON</button></div><pre id="starter-json">{escape(json.dumps(starter,indent=2,ensure_ascii=False))}</pre></div>'''
    links = link(actor['url']+'/input-schema','View current input ↗','button button-dark') + link(actor['url']+'/pricing','Check pricing ↗','button button-outline')
    return section(f'<div class="breadcrumbs">{link("/actors","All Actors")} / {escape(group(actor))}</div>' + heading('Nomad Agent / '+group(actor),short_name(actor),escape(actor['description'])) + '<div class="hero-actions">'+link(actor['url'],'Open Actor on Apify ↗','button button-dark')+link('/guides','Explore workflows','button button-outline')+'</div>') + section('<div class="nomad-detail-grid"><div>'+heading('First run','Try a few results.','Use the exact Actor’s fields. Keep the result limit and spending budget small, then inspect what the run returned.')+ '<ol class="nomad-list"><li>Open Input and Pricing on Apify.</li><li>Set Maximum cost per run before starting.</li><li>Select the production build <code>latest</code>.</li><li>Check the terminal run status, immutable build, dataset, and run summary where available.</li><li>Test your destination before enabling a schedule.</li></ol><div class="hero-actions">'+links+'</div></div><div>'+start+'</div></div>', 'section-paper') + section(heading('Keep the original evidence','Read the source before acting.','Preserve source IDs, original descriptions, and application links. Unknown facts stay unknown. Remote work does not imply worldwide eligibility; read the posting’s location and residency requirements.') + '<p class="nomad-note">This page documents the public listing and input schema. It does not establish live source coverage, a successful run, or delivery to your destination.</p><div class="hero-actions">'+link('/docs/output','Understand the formats →','text-link')+'</div>')


def quickstart() -> str:
    return section(heading('Getting started','From an Actor to useful data.','Start in Apify Console, inspect a small result, and then connect the feed to your application.')+steps()+link('/actors','Choose an Actor →','button button-dark')) + section(heading('For your application','Use the API with a bounded run.','Read the selected Actor’s current input schema. Replace the example Actor and input.json with your selected Actor’s identity and validated input.')+r'''<div class="nomad-code"><div class="code-title"><span>REST / start a run</span><button type="button" data-copy="api-example">Copy command</button></div><pre id="api-example">curl --request POST \
  'https://api.apify.com/v2/acts/nomad-agent~all-jobs-scraper/runs?build=latest&amp;timeout=300&amp;maxTotalChargeUsd=0.20' \
  --header "Authorization: Bearer $APIFY_TOKEN" \
  --header 'Content-Type: application/json' \
  --data-binary @input.json</pre></div><p class="nomad-note">The $0.20 cap and 300-second timeout are example guardrails, not a guarantee that every source scan completes. Read current pricing before choosing your budget. Keep credentials in your environment, never in URLs or shared files.</p><ol class="nomad-list"><li>Retain the returned run ID and poll it to a terminal status with a finite deadline.</li><li>Record the immutable <code>buildId</code> returned by the run. Read the default dataset and <code>RUN-SUMMARY</code> where provided.</li><li>Distinguish actual job rows from diagnostics, partial results, and a valid empty search.</li><li>Fetch dataset items through the documented Apify API and validate the exact Actor’s output before mapping fields.</li></ol>''', 'section-paper') + section(heading('For your agent','Connect only the tools you need.','Use the generic Apify MCP tools to inspect the Actor and run it with explicit input, build, timeout, and cost limits.')+'''<div class="nomad-code"><pre>https://mcp.apify.com?tools=fetch-actor-details,call-actor,get-actor-run,get-dataset-items,get-key-value-store-record</pre></div>'''+ '<p class="nomad-note">Ask your agent to inspect the exact Actor schema, use <code>latest</code>, and request a small run only within your authorized budget. Read the run and dataset before claiming results.</p>'+link(GITHUB+'/blob/main/.agents/skills/public-apify-actors/SKILL.md','Read the public Actor skill ↗','text-link'))


def output_page(sample: dict) -> str:
    code = escape(json.dumps(sample,indent=2,ensure_ascii=False))
    return section(heading('The data','Source facts. Flat rows.','Most current simple job readers use the 15-field nomad-agent-job-row-v3 contract. Older and source-specific products can have different formats. Always check the exact Actor’s Output tab.') + '<div class="hero-actions">'+link('/samples/job-row.json','Download illustrative JSON','button button-dark')+link('/contracts/nomad-agent-job-row-v3.schema.json','Read the row-v3 schema','button button-outline')+'</div>')+section('<div class="nomad-detail-grid"><div>'+heading('A fictional example','Keep the useful details.','The example illustrates the current shared simple format; it is not a live vacancy or evidence that a particular Actor ran.')+'''<dl class="nomad-definitions"><div><dt>Identity</dt><dd>The pair <code>(source, id)</code> identifies a posting. Do not deduplicate by title.</dd></div><div><dt>Original content</dt><dd>Keep <code>description</code>, <code>descriptionHtml</code>, and the original <code>url</code>.</dd></div><div><dt>Unknown values</dt><dd><code>null</code> means unknown. <code>locations: []</code> means no usable location was parsed; <code>hiringContacts: []</code> means no named contacts.</dd></div><div><dt>Dates & work arrangement</dt><dd>Retain posting dates and deadlines. Use source-stated arrangement and read the original eligibility requirements.</dd></div></dl></div><div class="nomad-code"><div class="code-title"><span>Illustration / row-v3</span><button type="button" data-copy="output-json">Copy JSON</button></div><pre id="output-json">'''+code+'</pre></div></div>', 'section-paper')+section(heading('Need a different layer?','Explore normalized data at Job Atlas.','Normalized job Actors use a separate nested format with richer fields and optional processing where supported. Fit scoring returns a separate candidate-evaluation contract.')+link('https://jobatlas.dev/','Explore Job Atlas ↗','button button-dark'))


GUIDES = {
 'job-tracker': ('Build a job tracker', 'Keep one record per posting.', [('Choose a source','Use a single board for a focused tracker or a bundle for a broader search.'),('Inspect your first rows','Check the exact output schema. Preserve source IDs, descriptions and original application links.'),('Map your destination','For the shared simple format, key records by the pair (source, id). Upsert existing records rather than appending duplicate titles.'),('Test before scheduling','Write a small batch to your Sheet or database and read it back. Actor success and destination delivery are separate checks.')]),
 'job-alerts': ('Build recurring job alerts', 'Make each alert a useful one.', [('Define one search','Choose an Actor and only the query, location and arrangement filters its input schema supports.'),('Keep a stable scope','Where repeat suppression is supported, preserve one stable dedupe key for each search. Do not reuse a key across unrelated alerts.'),('Check the run','Inspect terminal status, the returned build, actual rows and the run summary where provided. An empty result can be correct.'),('Connect your alert','Format the original title, source and application link for your destination. Verify a delivery before enabling a recurring workflow.')]),
 'research-jobs': ('Track research opportunities', 'Bring your research search together.', [('Start with the right sources','Choose Research Jobs for a bundle, or focus on EURAXESS, jobs.ac.uk or AcademicPositions.'),('Keep the original description','Check qualifications, research area, funding and deadlines in the source text. Missing facts are not inferred by a simple reader.'),('Preserve dates and links','Store the posting’s identity and original application URL. Recheck deadlines and requirements at the source before applying.'),('Inspect coverage','Read the run summary where available. Unavailable sources or an empty search do not prove there are no opportunities elsewhere.')]),
 'coding-agent': ('Connect your coding agent', 'Let your agent work with source data.', [('Inspect the Actor','Use fetch-actor-details to read the exact public Actor’s input and capabilities. Simple and normalized contracts differ.'),('Bound the request','Use generic call-actor with latest and explicit input, timeout and cost limits. Authorize paid execution before starting.'),('Inspect the real result','Get terminal run status, record the immutable build ID, read dataset items and inspect RUN-SUMMARY where provided.'),('Keep the evidence','Preserve original records and links. Validate the output before your agent writes to an application or destination.')]),
}


def build() -> dict[str, bytes]:
    catalog = json.loads((SOURCE/'actors.json').read_text())
    if catalog['schemaVersion'] != 'nomad-simple-site-catalog-v1':
        raise ValueError('Unsupported catalogue contract')
    actors: list[Actor] = catalog['actors']
    for actor in actors:
        actor['description'] = actor['description'].replace('Only verified postings; repeats are suppressed. No login or API key.', '').strip()
    if not actors or any(not a['isPublic'] or a['isDeprecated'] or a['family'] != 'Simple and source-specific jobs' or not a['url'].startswith('https://apify.com/nomad-agent/') for a in actors):
        raise ValueError('Only observed public active simple job Actors belong on this site')
    if len({a['slug'] for a in actors}) != len(actors):
        raise ValueError('Duplicate Actor slug')
    icon_snapshot: IconSnapshot = json.loads((SOURCE/'actor-icons.json').read_text())
    if icon_snapshot['schemaVersion'] != 'nomad-actor-icons-v1':
        raise ValueError('Unsupported Actor icon snapshot')
    icons = icon_snapshot['icons']
    if set(icons) != {actor['slug'] for actor in actors}:
        raise ValueError('Actor icon snapshot must match the website cohort')
    for actor in actors:
        icon = icons[actor['slug']]
        if icon['actorId'] != actor['actorId'] or icon['file'] != actor['slug'] + '.png':
            raise ValueError('Actor icon identity mismatch: ' + actor['slug'])
        data = (SOURCE/'actor-icons'/icon['file']).read_bytes()
        if not data.startswith(b'\x89PNG\r\n\x1a\n') or hashlib.sha256(data).hexdigest() != icon['sha256']:
            raise ValueError('Actor icon bytes differ from the observed Apify image: ' + actor['slug'])
    sample = json.loads((SOURCE/'job-row.json').read_text())
    observed = catalog['observedAt'][:10]
    files: dict[str, bytes] = {}
    routes = []
    def add(route: str, title: str, description: str, body: str, noindex: bool = False):
        path = 'index.html' if route == '/' else ('404.html' if noindex else route.strip('/')+'/index.html')
        files[path] = page(title,description,route,body,noindex=noindex).encode()
        if not noindex:
            routes.append(route)
    add('/','Simple job data for feeds, alerts, and trackers','Explore public Nomad Agent job Actors: single boards and bundles with source facts, original descriptions, and links.',homepage(actors,sample))
    filters = '<div class="catalog-controls" data-catalog-controls hidden><label>Search Actors<input type="search" id="actor-search" placeholder="Try remote, research, or LinkedIn" /></label><label>Browse by use<select id="actor-group"><option value="">All Actors</option>' + ''.join(f'<option>{escape(g)}</option>' for g in sorted({group(a) for a in actors}))+'</select></label><button type="button" id="clear-filters" class="button button-outline">Clear filters</button></div>'
    catalog_body = heading('The public catalogue','Find your next job feed.','Choose a single source or a bundle. Each page links to the exact Actor, current input, and pricing.')+filters+f'<p id="catalog-count" class="catalog-count" role="status" aria-live="polite">{len(actors)} Actors</p><div class="product-grid nomad-catalog">'+''.join(card(a,i+1,filtering=True) for i,a in enumerate(actors))+'</div><p id="catalog-empty" class="catalog-empty" hidden>No Actors match your search. Try another source or clear the filters.</p><p class="nomad-note">Public listings and input schemas checked '+observed+'. Availability and output depend on the selected Actor and its source.</p>'
    add('/actors','Public simple job Actors','Browse simple job feeds and bundles from Nomad Agent by source and use.',section(catalog_body))
    for actor in actors:
        add('/actors/'+actor['slug'],short_name(actor),actor['description'],actor_page(actor,observed))
    add('/docs','Getting started','Start a small Apify Actor run, inspect source-linked job data, and connect a destination.',quickstart())
    add('/docs/output','The simple job data format','Understand flat simple job rows, original descriptions, stable identity, and unknown values.',output_page(sample))
    add('/guides','Useful job-data workflows','Build a job tracker, alert, research feed, or coding-agent workflow from simple source data.',section(heading('Workflows','Make the feed useful.','Start with a small run and test the destination you want to connect.')+workflows()))
    for slug,(title,subtitle,items) in GUIDES.items():
        body = section(heading('A practical workflow',title,subtitle) + '<ol class="nomad-guide-steps">'+''.join(f'<li><span>0{i+1}</span><div><h2>{escape(t)}</h2><p>{escape(p)}</p></div></li>' for i,(t,p) in enumerate(items))+'</ol><div class="hero-actions">'+link('/actors','Choose an Actor →','button button-dark')+link('/docs','Read the API quickstart','button button-outline')+'</div>')
        add('/guides/'+slug,title,subtitle,body)
    add('/about','About Nomad Agent','Independent source-linked job data tools for feeds, alerts, and trackers.',section(heading('Nomad Agent','Useful source data. A clear starting point.','Nomad Agent publishes independent tools on Apify for collecting job postings into feeds, trackers, and applications.')+'''<div class="nomad-prose"><h2>Choose the layer you need.</h2><p>This website focuses on simple job Actors and source-specific feeds in the Nomad Agent namespace. Simple readers preserve source facts and original descriptions. Job Atlas publishes separate normalized products and candidate fit scoring.</p><h2>Understand the limits.</h2><p>Sources can be unavailable, a search can return no new jobs, and fields differ between Actors. A public listing or a schema-checked input does not prove live coverage or delivery. Inspect the run, dataset and destination for your use.</p><h2>Independent tools.</h2><p>Nomad Agent is not affiliated with or endorsed by the job boards, employers, or institutions whose public postings it collects. Review the source’s terms and your intended use before republishing data.</p></div>'''+link('https://apify.com/nomad-agent','Explore Nomad Agent on Apify ↗','button button-dark')))
    add('/privacy','Privacy','How this static website handles browsing, local controls, and links to external services.',section(heading('Privacy','A simple website. Local controls.')+'''<div class="nomad-prose"><p>This website does not ask for your resume, account credentials, or contact details. Its search, filters and copy controls run locally in your browser. It uses no analytics scripts, advertising trackers, cookies or persistent browser storage.</p><p>The hosting provider processes requests to serve the pages and can log technical request information such as your IP address. This website does not claim the hosting provider collects no data.</p><p>Links to Apify, GitHub, source websites and Job Atlas take you to separate services with their own privacy policies. Actor inputs and results are handled by Apify and the selected Actor; read their policies before submitting personal information.</p></div>'''))
    add('/404','Page not found','The requested page could not be found.',section(heading('404','This route has no stop.','Try the Actor catalogue or return to the homepage.')+link('/actors','Browse Actors →','button button-dark')),True)
    for source,target in [('site.css','site.css'),('site.js','site.js'),('job-row.json','samples/job-row.json'),('social-card.jpg','assets/social-card.jpg')]:
        files[target]=(SOURCE/source).read_bytes()
    for source,target in [('styles.css','styles.css'),('first-visit.css','first-visit.css'),('assets/nomad-agent-mark-512.png','assets/nomad-agent-mark.png')]:
        files[target]=(ROOT/'website'/source).read_bytes()
    for actor in actors:
        icon = icons[actor['slug']]
        files['assets/actors/' + icon['file']] = (SOURCE/'actor-icons'/icon['file']).read_bytes()
    schema_copy = (SOURCE/'job-row-v3.schema.json').read_bytes()
    canonical_schema = ROOT/'integrations/shared/nomad-agent-job-row-v3.schema.json'
    if canonical_schema.exists() and canonical_schema.read_bytes() != schema_copy:
        raise ValueError('Observed row-v3 schema copy differs from the canonical shared contract; review and refresh the copy')
    files['contracts/nomad-agent-job-row-v3.schema.json'] = schema_copy
    files['robots.txt']=f'User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n'.encode()
    files['sitemap.xml']=('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{xml_escape(ORIGIN+r)}</loc></url>\n' for r in routes)+'</urlset>\n').encode()
    files['assets/social-card.svg']=b'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630"><rect width="1200" height="630" fill="#0b4b38"/><rect x="64" y="58" width="1072" height="514" fill="none" stroke="#f4e8cf"/><text x="104" y="140" fill="#f4e8cf" font-family="Arial,sans-serif" font-size="28">NOMAD AGENT / SIMPLE JOB DATA</text><text x="100" y="275" fill="#f4e8cf" font-family="Arial,sans-serif" font-size="78" font-weight="bold">Build job feeds,</text><text x="100" y="365" fill="#f4e8cf" font-family="Arial,sans-serif" font-size="78" font-weight="bold">alerts, and trackers.</text><circle cx="104" cy="467" r="8" fill="#e83a20"/><path d="M104 467H1096" stroke="#f4e8cf" stroke-width="2"/><text x="104" y="529" fill="#f4e8cf" font-family="Arial,sans-serif" font-size="24">Source facts. Original descriptions. Useful workflows.</text></svg>'''
    return files


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Check committed output against source without writing')
    args=parser.parse_args()
    files=build()
    manifest={'schemaVersion':'nomad-site-build-v1','origin':ORIGIN,'files':{p:hashlib.sha256(b).hexdigest() for p,b in sorted(files.items())}}
    files['build-manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    if args.check:
        actual={str(p.relative_to(OUTPUT)) for p in OUTPUT.rglob('*') if p.is_file() and p.name != '.DS_Store'}
        different=[p for p,b in files.items() if not (OUTPUT/p).exists() or (OUTPUT/p).read_bytes()!=b]
        extra=sorted(actual-set(files))
        if different or extra:
            raise SystemExit(f'Generated site differs: changed={different}, unexpected={extra}')
        print(f'Generated site matches {len(files)} files')
        return
    if subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()!='main':
        raise SystemExit('STOP: expected the shared main branch')
    # Never remove an unexpected file; review catalogue retirements explicitly.
    unexpected=[str(p.relative_to(OUTPUT)) for p in OUTPUT.rglob('*') if p.is_file() and p.name != '.DS_Store' and str(p.relative_to(OUTPUT)) not in files]
    if unexpected:
        raise SystemExit(f'Review unexpected existing site files before building: {unexpected}')
    for path,data in files.items():
        destination=OUTPUT/path
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(data)
    print(f'Built {len(files)} files for {ORIGIN}')


if __name__=='__main__':
    main()
