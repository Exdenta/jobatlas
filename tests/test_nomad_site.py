from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import unittest
from urllib.parse import urlsplit, unquote
from xml.etree import ElementTree
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'website-nomad-agent'
spec = importlib.util.spec_from_file_location('nomad_builder', ROOT / 'scripts/build_nomad_site.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class HTML(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.ids = set()
        self.canonical = []
        self.h1 = 0
        self.metas = {}
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'h1': self.h1 += 1
        if 'id' in attrs:
            if attrs['id'] in self.ids: raise AssertionError('Duplicate id: '+attrs['id'])
            self.ids.add(attrs['id'])
        if tag == 'link' and attrs.get('rel') == 'canonical': self.canonical.append(attrs['href'])
        if tag == 'meta': self.metas[attrs.get('name', attrs.get('property'))] = attrs.get('content')
        for key in ('href', 'src'):
            if key in attrs: self.links.append(attrs[key])


class NomadSiteTests(unittest.TestCase):
    def test_reproducible_output(self):
        expected = builder.build()
        actual = {str(p.relative_to(SITE)) for p in SITE.rglob('*') if p.is_file() and p.name != '.DS_Store'}
        self.assertEqual(actual, set(expected) | {'build-manifest.json'})
        for path, content in expected.items():
            with self.subTest(path=path): self.assertEqual((SITE/path).read_bytes(), content)

    def test_catalogue_scope_and_starters(self):
        snapshot = json.loads((ROOT/'nomad-site/actors.json').read_text())
        actors = snapshot['actors']
        self.assertTrue(actors)
        for actor in actors:
            with self.subTest(actor=actor['slug']):
                self.assertTrue(actor['isPublic'])
                self.assertEqual(actor['schemaSelector'], 'latest')
                self.assertFalse(actor['isDeprecated'])
                self.assertEqual(actor['family'], 'Simple and source-specific jobs')
                self.assertTrue(actor['url'].startswith('https://apify.com/nomad-agent/'))
                self.assertTrue((SITE/'actors'/actor['slug']/'index.html').is_file())
                if actor['inputExample'] is not None:
                    jsonschema.validate(actor['inputExample'], actor['inputSchema'])
        self.assertEqual(len(actors), len({a['slug'] for a in actors}))

    def test_all_local_links_and_fragments_resolve(self):
        for path in SITE.rglob('*.html'):
            document=HTML(path.read_text())
            for href in document.links:
                url=urlsplit(href)
                if url.scheme or url.netloc: continue
                target=SITE/unquote(url.path).lstrip('/') if url.path else path
                if target.is_dir(): target=target/'index.html'
                elif not target.is_file() and not target.suffix: target=target/'index.html'
                with self.subTest(page=str(path.relative_to(SITE)), href=href):
                    self.assertTrue(target.is_file(),str(target))
                    if url.fragment and target.suffix=='.html': self.assertIn(url.fragment,HTML(target.read_text()).ids)

    def test_canonicals_sitemap_and_noindex_404(self):
        urls=[]
        for path in SITE.rglob('*.html'):
            doc=HTML(path.read_text())
            self.assertEqual(doc.h1,1)
            if path.name=='404.html':
                self.assertFalse(doc.canonical)
                self.assertEqual(doc.metas['robots'],'noindex,follow')
                continue
            self.assertEqual(len(doc.canonical),1)
            canonical=doc.canonical[0]
            relative=str(path.relative_to(SITE))
            route='/' if relative=='index.html' else '/'+relative.removesuffix('/index.html')
            self.assertEqual(canonical,'https://nomadagent.dev'+route)
            urls.append(canonical)
            self.assertTrue(doc.metas['description'])
        tree=ElementTree.fromstring((SITE/'sitemap.xml').read_text())
        sitemap=[n.text for n in tree.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        self.assertCountEqual(urls,sitemap)
        self.assertIn('Sitemap: https://nomadagent.dev/sitemap.xml',(SITE/'robots.txt').read_text())

    def test_fictional_output_matches_canonical_contract(self):
        schema=json.loads((ROOT/'nomad-site/job-row-v3.schema.json').read_text())
        sample=json.loads((SITE/'samples/job-row.json').read_text())
        jsonschema.validate(sample,schema)
        self.assertEqual(len(sample),15)
        self.assertNotIn('recordType',sample)
        self.assertEqual((SITE/'contracts/nomad-agent-job-row-v3.schema.json').read_bytes(),(ROOT/'nomad-site/job-row-v3.schema.json').read_bytes())
        canonical=ROOT/'integrations/shared/nomad-agent-job-row-v3.schema.json'
        if canonical.exists(): self.assertEqual(canonical.read_bytes(),(ROOT/'nomad-site/job-row-v3.schema.json').read_bytes())
        self.assertIn('fictional',(SITE/'docs/output/index.html').read_text().lower())

    def test_hosting_isolation_and_legacy_routes(self):
        original=json.loads((ROOT/'firebase.json').read_text())
        config=json.loads((ROOT/'firebase.nomad.json').read_text())
        self.assertEqual(original['hosting']['site'],'nomad-agent-job-scrapers')
        self.assertEqual(original['hosting']['public'],'website')
        self.assertEqual(config['hosting']['site'],'nomad-agent-public')
        self.assertEqual(config['hosting']['public'],'website-nomad-agent')
        self.assertNotIn('rewrites',config['hosting'])
        for redirect in config['hosting']['redirects']:
            self.assertNotEqual(redirect['source'],'/')
            self.assertTrue(redirect['destination'].startswith('https://jobatlas.dev/'))
            self.assertEqual(redirect['type'],301)

    def test_build_receipt_matches_files(self):
        import hashlib
        receipt=json.loads((SITE/'build-manifest.json').read_text())
        self.assertEqual(receipt['origin'],'https://nomadagent.dev')
        for name,digest in receipt['files'].items():
            with self.subTest(file=name): self.assertEqual(hashlib.sha256((SITE/name).read_bytes()).hexdigest(),digest)


if __name__=='__main__': unittest.main()
