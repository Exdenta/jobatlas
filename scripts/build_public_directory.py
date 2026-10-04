#!/usr/bin/env python3
"""Generate the public product directory from its canonical public catalogue."""
from __future__ import annotations
import argparse
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://jobatlas.dev'
GROUPS = {
    'Simple and source-specific jobs': 'source-jobs',
    'Normalized jobs': 'normalized-jobs',
    'Job fit scoring': 'job-fit-scoring',
    'AI job search': 'ai-job-search',
    'Restaurant menus and photos': 'menus-and-photos',
    'Property': 'property',
    'Public records': 'public-records',
    'Search, marketing and data tools': 'data-tools',
}
REPO = 'https://github.com/Exdenta/jobatlas'


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def render_pages(root: Path = ROOT) -> dict[str, str]:
    records = json.loads((root / 'docs/public-actors.json').read_text())['actors']
    template = (root / 'website/actors/index.html').read_text()
    header = template.split('<main ', 1)[0]
    footer = template.split('</main>', 1)[1]
    old_title = 'Compare Job Scrapers &amp; Résumé Matching | Job Atlas'
    old_description = re.search(r'<meta name="description" content="([^"]+)"', header)[1]
    pages = {}

    def page(route: str, title: str, description: str, content: str) -> str:
        head = header.replace(old_title, escape(title + ' | Job Atlas'))
        head = head.replace(old_description, escape(description))
        head = head.replace('https://jobatlas.dev/actors', ORIGIN + route)
        placement = route.rsplit('/', 1)[-1]
        head = head.replace('href="/actors">Tools</a>',
            'href="/actors" data-event="navigation_click" data-category="navigation" data-label="tools" data-placement="directory-' + placement + '-tools">Tools</a>', 1)
        head = head.replace('href="https://github.com/Exdenta/jobatlas">View source</a>',
            'href="https://github.com/Exdenta/jobatlas" data-event="navigation_click" data-category="documentation" data-label="github" data-placement="directory-' + placement + '-source">View source</a>', 1)
        middle_route = '/actors' if route == '/actors/directory' else '/actors/directory'
        middle_label = 'Tools' if route == '/actors/directory' else 'Public tools'
        graph = {
            '@context': 'https://schema.org',
            '@graph': [
                {'@type': 'CollectionPage', 'name': title,
                 'url': ORIGIN + route, 'description': description},
                {'@type': 'BreadcrumbList', 'itemListElement': [
                    {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': ORIGIN + '/'},
                    {'@type': 'ListItem', 'position': 2, 'name': middle_label, 'item': ORIGIN + middle_route},
                    {'@type': 'ListItem', 'position': 3, 'name': title, 'item': ORIGIN + route},
                ]},
            ],
        }
        head = re.sub(r'(<script type="application/ld\+json">).*?(</script>)',
                      lambda match: match[1] + json.dumps(graph, separators=(',', ':')) + match[2],
                      head, count=1, flags=re.S)
        breadcrumbs = '<nav class="detail-breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><a href="' + middle_route + '">' + middle_label + '</a><span>/</span><span>' + escape(title) + '</span></nav>'
        hero = '<section class="detail-hero"><p class="detail-eyebrow">Public APIs and documentation</p><h1>' + escape(title) + '</h1><p class="detail-lede">' + escape(description) + '</p></section>'
        return head + '<main class="detail-main" id="main-content">' + breadcrumbs + hero + content + '</main>' + footer

    hubs = []
    for family, slug in GROUPS.items():
        group = sorted((row for row in records if row['family'] == family), key=lambda row: (row['title'], row['owner']))
        assert group, family
        route = '/actors/directory/' + slug
        hubs.append('<li><a href="' + route + '">' + escape(family) + '</a> (' + str(len(group)) + ' listings)</li>')
        cards = []
        for actor in group:
            anchor = actor['owner'] + '-' + actor['slug']
            extra = ''
            if family == 'Restaurant menus and photos':
                extra = '<p>Use the <a href="https://traveleat.app/blog/ai-menu-parser-api">Travel Eat menu API guide</a> or <a href="https://github.com/Exdenta/traveleat-support">public menu documentation</a>.</p>'
            elif family in {'Simple and source-specific jobs', 'Normalized jobs', 'Job fit scoring', 'AI job search'}:
                extra = '<p>For personal job alerts, <a href="https://oinkjobsearch.com/">try Oink</a>. For developers, <a href="https://github.com/Exdenta/OinkAIJobSearch">read its public documentation</a>.</p>'
            cards.append('<article class="detail-panel" id="' + escape(anchor) + '"><h2>' + escape(actor['title']) + '</h2><p>' + escape(actor['description']) + '</p><p><a href="' + escape(actor['url']) + '">Open on Apify (' + escape(actor['owner']) + ')</a> · <a href="' + REPO + '/blob/main/docs/public-actors.md">Public documentation</a></p>' + extra + '</article>')
        intro = 'Find public ' + family.lower() + ' APIs, understand their outputs, and follow their Store listings and documentation before choosing a tool.'
        content = '<p>Each listing links to its own current input and pricing. Optional modes and output formats differ between products.</p>' + ''.join(cards) + '<p><a href="/actors/directory">Browse other public tools</a></p>'
        pages[route.lstrip('/') + '/index.html'] = page(route, family, intro, content)
    intro = 'Browse our public job, menu, property, legal, search and data APIs. Find the exact Apify listing, product guide and relevant application for each tool.'
    content = '<section class="detail-panel"><h2>Choose a product family</h2><ul>' + ''.join(hubs) + '</ul><p><a href="' + REPO + '/blob/main/docs/public-actors.md">Full directory on GitHub</a> · <a href="https://apify.com/nomad-agent">Nomad Agent on Apify</a> · <a href="https://apify.com/jobatlas">Job Atlas on Apify</a></p><p>Job Atlas listings provide normalized job data and candidate scoring. Simple and source-specific job Actors have their own formats. Menu and photo APIs have <a href="https://traveleat.app/blog/ai-menu-parser-api">Travel Eat documentation</a>. Read the exact product\'s current input, output and pricing before running.</p></section>'
    pages['actors/directory/index.html'] = page('/actors/directory', 'Public data tools', intro, content)
    return pages


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify generated pages without writing')
    args = parser.parse_args()
    for relative, content in render_pages().items():
        target = ROOT / 'website' / relative
        if args.check:
            assert target.read_text() == content, 'Directory page drift: ' + relative
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
    print('Public directory pages verified' if args.check else 'Public directory pages generated')


if __name__ == '__main__':
    main()
