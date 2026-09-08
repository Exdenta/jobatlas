"""Customer entry points must route to the public Job Atlas catalog."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = json.loads((ROOT / 'catalogue/actors-v1.json').read_text(encoding='utf-8'))
SLUGS = tuple(sorted(
    deployment['slug']
    for deployment in CATALOGUE['deployments']
    if deployment['owner'] == 'job-atlas'
    and deployment['relationship'] == 'promoted-copy'
    and deployment['endpointState'] == 'live-metadata-verified'
))
TARGET_REPOSITORY = 'https://github.com/Exdenta/jobatlas'
LEGACY_REPOSITORY = 'https://github.com/Exdenta/nomad-agent-job-scrapers'
LEGACY_RAW_REPOSITORY = (
    'https://raw.githubusercontent.com/Exdenta/nomad-agent-job-scrapers'
)

class JobAtlasRoutingTests(unittest.TestCase):
    def test_website_routes_to_current_store_and_keeps_current_brand(self):
        for path in (ROOT / 'website').rglob('*.html'):
            text = path.read_text()
            self.assertNotIn('apify.com/nomad-agent', text, path)
            for identity in re.findall(r'<title[^>]*>.*?</title>|<header[^>]*>.*?</header>', text, re.S):
                if identity.startswith('<header'):
                    self.assertIn('Job Atlas', identity, path)
                self.assertNotIn('Nomad Agent', identity, path)
            # The homepage FAQ and About may explain the retained legacy domain.
            if path.relative_to(ROOT).as_posix() not in {'website/index.html', 'website/about/index.html'}:
                self.assertNotIn('Nomad Agent', text, path)
            self.assertIn('/assets/job-atlas-mark.svg', text, path)
        home = (ROOT / 'website/index.html').read_text()
        for slug in SLUGS:
            self.assertIn('https://apify.com/job-atlas/' + slug, home)

    def test_runnable_examples_and_skills_use_job_atlas(self):
        for folder in ('integrations', '.agents/skills', 'scripts'):
            for path in (ROOT / folder).rglob('*'):
                if not path.is_file() or 'evidence' in path.parts or path.suffix not in {'.md','.json','.py','.mjs','.yaml'}:
                    continue
                text = path.read_text()
                for slug in SLUGS:
                    self.assertNotRegex(text, r'nomad-agent(?:/|~|%2[Ff])' + re.escape(slug), path)
        self.assertIn('nomad-agent-job-v1', (ROOT / 'README.md').read_text())

    def test_promoted_routes_are_derived_from_the_checked_catalogue(self):
        self.assertEqual(len(SLUGS), 4)
        self.assertEqual(
            set(SLUGS),
            {
                'linkedin-enrich-translate-normalize-scraper',
                'euraxess-enrich-translate-normalize-scraper',
                'ycombinator-enrich-translate-normalize-scraper',
                'ai-job-fit-scorer',
            },
        )
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertIn('catalogue/actors-v1.json', readme)
        self.assertIn('docs/client-migration.md', readme)

    def test_current_brand_assets_are_present(self):
        assets = ROOT / 'website/assets'
        for name in ('job-atlas-mark.svg','job-atlas-mark-512.png','job-atlas-social-card.svg',
                     'job-atlas-social-card.png','linkedin-mark.svg','euraxess-mark.svg',
                     'ycombinator-mark.svg','ai-job-fit-scorer-mark.svg'):
            self.assertGreater((assets / name).stat().st_size, 0)

    def test_repository_cutover_updates_navigation_but_retains_stable_ids(self):
        legacy_web_identifier_paths = {
            'benchmarks/enrichment-quality-v1/benchmark.schema.json',
            'benchmarks/enrichment-quality-v1/prediction.schema.json',
            'integrations/shared/flat-job-v1.schema.json',
        }
        legacy_raw_identifier_paths = {
            '.agents/skills/euraxess-enrich-translate-normalize-scraper/'
            'references/output-contract.md',
            '.agents/skills/euraxess-enrich-translate-normalize-scraper/'
            'scripts/validate_contract.py',
            '.agents/skills/ycombinator-enrich-translate-normalize-scraper/SKILL.md',
            'examples/euraxess-job.json',
            'integrations/shared/euraxess-v1.schema.json',
            'integrations/shared/nomad-agent-job-v1.schema.json',
            'integrations/shared/run-summary-v3.schema.json',
            'integrations/shared/run-summary-v4.schema.json',
            'integrations/shared/ycombinator-v2.schema.json',
            'website/samples/euraxess-job.json',
            # Exact downloadable copy of the recorded source result.
            'website/samples/explorer/euraxess.json',
        }
        text_suffixes = {
            '.csv', '.html', '.json', '.md', '.mjs', '.py', '.svg', '.toml',
            '.txt', '.xml', '.yaml', '.yml',
        }
        old_web_paths = set()
        old_raw_paths = set()
        for path in ROOT.rglob('*'):
            if not path.is_file() or path.suffix not in text_suffixes:
                continue
            relative = path.relative_to(ROOT).as_posix()
            if (
                relative.startswith(('.git/', 'seo-evidence/', 'tests/'))
                or relative.startswith('website-variations/')
                or relative == 'docs/CEO_REPORT_2026-08-27.md'
                or relative.startswith('docs/seo-baselines/')
                or relative.startswith('integrations/evidence/')
            ):
                continue
            text = path.read_text(encoding='utf-8')
            if LEGACY_REPOSITORY in text:
                old_web_paths.add(relative)
            if LEGACY_RAW_REPOSITORY in text:
                old_raw_paths.add(relative)

        self.assertEqual(old_web_paths, legacy_web_identifier_paths)
        self.assertEqual(old_raw_paths, legacy_raw_identifier_paths)

        for relative in (
            'README.md',
            '.github/ISSUE_TEMPLATE/config.yml',
            'docs/job-atlas.md',
            'integrations/n8n/README.md',
            'website/index.html',
            'website/about/index.html',
        ):
            self.assertIn(
                TARGET_REPOSITORY,
                (ROOT / relative).read_text(encoding='utf-8'),
                relative,
            )

        hosting = json.loads((ROOT / 'firebase.json').read_text(encoding='utf-8'))
        self.assertEqual(hosting['hosting']['site'], 'nomad-agent-job-scrapers')
        for relative in (
            '.github/workflows/deploy-website.yml',
            '.github/workflows/seo-observatory.yml',
        ):
            self.assertIn(
                'providers/nomad-agent-job-scrapers',
                (ROOT / relative).read_text(encoding='utf-8'),
                relative,
            )

    def test_current_pages_use_the_canonical_jobatlas_social_card(self):
        social_image = 'https://jobatlas.dev/assets/job-atlas-social-card.png'
        for path in (ROOT / 'website').rglob('*.html'):
            text = path.read_text(encoding='utf-8')
            self.assertNotIn('/assets/nomad-agent-social-card.png', text, path)
            if 'property="og:image"' in text:
                self.assertIn(social_image, text, path)

    def test_synthetic_benchmark_uses_current_actor_labels(self):
        sample = json.loads(
            (
                ROOT / 'benchmarks/enrichment-quality-v1/predictions.sample.json'
            ).read_text(encoding='utf-8')
        )
        for system in sample['systems'].values():
            self.assertTrue(system['actorId'].startswith('job-atlas/'))
