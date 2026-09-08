#!/usr/bin/env python3
"""Validate the approved homepage and downloadable record integrity."""
import csv
import importlib.util
import io
import json
from pathlib import Path
import re
import unittest
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'website'
PREVIEW = SOURCE
spec = importlib.util.spec_from_file_location('schema_check', ROOT / '.agents/skills/ai-job-fit-scorer/scripts/schema_check.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.elements = []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    @property
    def ids(self):
        return [attrs['id'] for _, attrs in self.elements if 'id' in attrs]


def section(text, name):
    return next(s for s in re.findall(r'<section\b.*?</section>', text, re.S) if f'aria-labelledby="{name}"' in s)


class OriginalPlusChecks(unittest.TestCase):
    def test_current_repository_links_and_install_commands(self):
        retired = ('https://github.com/Exdenta/nomad-agent-job-scrapers',
                   'https://raw.githubusercontent.com/Exdenta/nomad-agent-job-scrapers')
        # Recorded JSON provenance is intentionally outside this public-copy check.
        stale = []
        for directory in (SOURCE,):
            for path in [*directory.rglob('*.html'), directory / 'llms.txt']:
                if any(url in path.read_text() for url in retired):
                    stale.append(str(path.relative_to(ROOT)))
        self.assertEqual(stale, [], 'Public links still use the retired repository name')
        self.assertIn('npx skills add https://github.com/Exdenta/jobatlas --skill',
                      (PREVIEW / 'index.html').read_text())

    def test_approved_content_and_section_order(self):
        page = Page(SOURCE / 'index.html')
        headings = [attrs.get('aria-labelledby') for tag, attrs in page.elements if tag == 'section']
        self.assertEqual(headings, ['page-title', 'products-heading', 'skill-heading', 'paths-heading', 'pricing-heading', 'faq-heading', 'output-section-heading', 'start-heading'])
        text = (SOURCE / 'index.html').read_text()
        for copy in ['Job scrapers and résumé matching', 'Explore the data', 'For your coding agent', 'Before your first run', 'Your first useful workflow']:
            self.assertIn(copy, text)
        self.assertNotIn('noindex', text)
        explorers = [attrs['data-output-explorer'] for tag, attrs in page.elements if 'data-output-explorer' in attrs]
        self.assertEqual(explorers, ['hero', 'detail'])

    def test_homepage_links_downloads_and_anchors_resolve(self):
        page = Page(PREVIEW / 'index.html')
        self.assertEqual(len(page.ids), len(set(page.ids)), 'Duplicate HTML ids')
        for tag, attrs in page.elements:
            for attr in (['href'] if tag in ('a', 'link') else ['src'] if tag in ('script', 'img') else []):
                url = urlsplit(attrs.get(attr, ''))
                if url.scheme or url.netloc:
                    continue
                path = PREVIEW / unquote(url.path.lstrip('/')) if url.path else PREVIEW / 'index.html'
                if path.is_dir():
                    path /= 'index.html'
                with self.subTest(url=attrs.get(attr)):
                    self.assertTrue(path.is_file(), str(path))
                    if url.fragment and path.suffix == '.html':
                        self.assertIn(unquote(url.fragment), Page(path).ids)

    def test_collector_downloads_match_schema_and_csv_projection(self):
        nested_schema = json.loads((ROOT / 'integrations/shared/nomad-agent-job-v1.schema.json').read_text())
        flat_schema = json.loads((ROOT / 'integrations/shared/flat-job-v1.schema.json').read_text())
        for actor in ['euraxess', 'linkedin', 'ycombinator']:
            with self.subTest(actor=actor):
                record = json.loads((PREVIEW / f'samples/explorer/{actor}.json').read_text())
                flat = json.loads((PREVIEW / f'samples/explorer/{actor}-flat.json').read_text())
                validator.check(record, nested_schema)
                validator.check(flat, flat_schema)
                self.assertEqual(flat['identityExternalId'], record['identity']['externalId'])
                self.assertEqual(flat['jobUrl'], record['identity']['url'])
                rows = list(csv.DictReader(io.StringIO((PREVIEW / f'samples/explorer/{actor}.csv').read_text())))
                self.assertEqual(len(rows), 1)
                self.assertEqual(set(rows[0]), set(flat))
                for key, value in flat.items():
                    expected = '' if value is None else 'true' if value is True else 'false' if value is False else str(value)
                    self.assertEqual(rows[0][key], expected, key)
                for key in ['workArrangements', 'workSchedules', 'contractTypes']:
                    nested = record['data']['employment'][key]
                    self.assertEqual(None if flat[key] is None else json.loads(flat[key]), nested)

    def test_recorded_sample_and_browser_payload_preserved(self):
        recorded = json.loads((SOURCE / 'samples/euraxess-job.json').read_text())
        self.assertEqual(recorded, json.loads((PREVIEW / 'samples/explorer/euraxess.json').read_text()))
        script = (PREVIEW / 'homepage-samples.js').read_text()
        samples = json.loads(script.removeprefix('window.HomepageSamples = ').strip().removesuffix(';'))
        for actor, sample in samples.items():
            self.assertEqual(sample['record'], json.loads((PREVIEW / f'samples/explorer/{actor}.json').read_text()))
            if actor != 'euraxess':
                self.assertIn('illustrative', sample['kind'].lower())


if __name__ == '__main__':
    unittest.main(verbosity=2)
