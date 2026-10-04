# Nomad Agent simple job website

An independent companion to Job Atlas, in the same approved visual style. The intended origin is `https://nomadagent.dev/`. Its public files live in `website-nomad-agent/`; the existing Job Atlas website remains in `website/`.

The catalogue includes active public Nomad Agent simple and source-specific job Actors and bundles. Normalized job Actors and fit scoring belong on Job Atlas. The site links to each exact Actor and its input and pricing pages. It includes a searchable catalogue, individual Actor pages, workflow guides, a quickstart, an illustrative output row and its schema, and privacy information. Starter examples are checked against an observed public input schema, not execution-tested.

## Source and build

- `actors.json`: versioned public listing and input-schema observations, with observation time and evidence boundary. This snapshot defines the explicit website cohort; a refresh rechecks those slugs, not the entire publisher portfolio.
- `actor-icons.json` and `actor-icons/`: dated public Apify `pictureUrl` observations and exact downloaded PNGs for every Actor in the site cohort. Icons are served locally. The build verifies Actor identity, cohort coverage and image hashes; adding an Actor or changing its icon requires a new observed image and matching receipt. The catalogue refresh does not refresh these images.
- `job-row.json`: explicitly fictional 15-field row-v3 illustration.
- `job-row-v3.schema.json`: byte-identical observed copy of the canonical shared contract, not an independently maintained schema. The build rejects drift from `integrations/shared/nomad-agent-job-row-v3.schema.json` when that canonical file exists.
- `social-card.jpg`: 1200 × 630 sharing image exported from the generated editable SVG.
- `site.css` and `site.js`: the simple-site extension and local-only controls.
- `../scripts/build_nomad_site.py`: deterministic HTML, sitemap, robots and build manifest generator. It copies the approved base styles and existing Nomad Agent mark without editing the Job Atlas site. The published schema comes from the observed canonical-contract copy, with parity checks when the repository’s shared schema is available.
- `../scripts/refresh_nomad_catalog.py`: explicit read-only Apify metadata refresh. It revalidates the explicit site cohort’s publisher, visibility, deprecation and `latest` build identity, then validates bounded starter inputs against the observed immutable build resolved through `latest`. It never starts Actors.

Run from the repository root:

```bash
uv run --with jsonschema==4.25.1 python scripts/refresh_nomad_catalog.py
python3 scripts/build_nomad_site.py
python3 scripts/build_nomad_site.py --check
uv run --with jsonschema==4.25.1 python -m unittest tests.test_nomad_site -v
node --check nomad-site/site.js
python3 -m http.server 4187 --bind 127.0.0.1 --directory website-nomad-agent
```

Catalogue refresh is optional during an ordinary build; it changes the observed source snapshot and requires review. Open the local preview at `http://127.0.0.1:4187/`. With the standard Python server, directory routes acquire a trailing slash. Firebase uses clean URLs in production. macOS `.DS_Store` files are excluded from build checks and Hosting uploads.

## Independent hosting

`firebase.nomad.json` selects site `nomad-agent-public`, and public directory `website-nomad-agent` in the existing `hryu-jobs` project. This is a separate configuration: the existing default configuration and Job Atlas deployment workflow continue targeting `nomad-agent-job-scrapers`.

Before first production publication, inspect the current domain mapping, create the separate Hosting site, deploy and verify its default hostname, then move only `nomadagent.dev` to the new site. Follow Firebase’s required domain verification and DNS records. Preserve `jobatlas.dev` and any unrelated domain mappings. Do not delete a current mapping until its replacement and rollback are prepared. Site creation, domain attachment and DNS confirmation are separate from deployment.

After the site exists and publication is authorized:

```bash
python3 scripts/build_nomad_site.py --check
firebase deploy --config firebase.nomad.json --only hosting --project hryu-jobs
```

Never omit `--config firebase.nomad.json`: the default configuration serves Job Atlas. Four historical normalized Actor routes redirect to the corresponding Job Atlas pages; the root serves the simple site. No root redirect is configured.

Before reporting a live release, record the source commit and Firebase release/version identity, compare every live file to `build-manifest.json`, inspect the home, catalogue, Actor and guide pages, verify the old normalized redirects, and confirm that `jobatlas.dev` still serves its existing site. HTTPS 200 alone does not establish the deployed bytes or a successful Actor run.

## Boundaries

The site makes no fixed-price, uptime, complete-coverage or delivery claims. Price links go to the current Actor listing. Source availability and actual rows need a bounded authorized run; a working website does not prove Actor execution. Search and filter controls work locally and send no analytics. External services have their own policies.
