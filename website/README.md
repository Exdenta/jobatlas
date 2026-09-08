# Job Atlas website

Static, dependency-free site for the Job Atlas job-data catalog. The public
origin is `https://jobatlas.dev/`; Firebase Hosting serves the files in this
directory from the isolated `nomad-agent-job-scrapers` site in project
`hryu-jobs`.

## Visual system

Follow the [approved website style guide](../docs/website-style-guide.md) for
visual and public-copy changes. It records the selected Original Plus homepage,
section backgrounds, cream workflow cards and gentle lift interaction. Secondary
page layouts remain the original design until reviewed.

Job Atlas uses bottle green (`#0B4B38`), warm cream (`#F4E8CF`), and vermilion
(`#E83A20`) with system typography, printed route tickets, and flat color. The
shared `styles.css` and `detail.css` cover the homepage and reference pages;
`assets/job-atlas-mark.svg` preserves the existing live brand mark. The social
card is editable SVG with a matching 1200 x 630 PNG export. No hosted fonts or
new runtime dependencies are required. Entry animations and the route drawing run
once; hover effects are limited to pointer devices. Reduced-motion preferences
disable them. Content remains visible without JavaScript.

## Information architecture

The site has four product pages, seven integration pages, four task-led guides,
and About, methodology, privacy, changelog, and contract pages. Every indexable
HTML file declares one absolute canonical. `404.html` is intentionally
`noindex,follow` and has no canonical.

The JSON schemas in `contracts/` must remain byte-for-byte copies of the
canonical sources in `integrations/shared/`. `scripts/search_publish.py prepare`
syncs the copies and regenerates `sitemap.xml` and `robots.txt`.

## Local preview and verification

From the repository root:

```bash
python3 scripts/search_publish.py prepare
python3 -m unittest tests.test_website tests.test_search_publish -v
python3 -m http.server 4173 --directory website
```

Open `http://127.0.0.1:4173/`. The complete acceptance contract and current
proof state are in `SUCCESS_CRITERIA.md`.

## First-visit content

The homepage explains the outcome before the platform terminology, shows a dated
EURAXESS record from `samples/euraxess-job.json`, and connects four audience use
cases to a tool or workflow. The sample is a checked-in illustration, not a live
vacancy feed; retain its observation date and source link. The four-tool catalog
and product `#first-run` sections provide bounded starter inputs. Price examples
are dated Actor-event estimates and separate optional services and Apify costs.

`first-visit.css` extends the original visual design. `homepage.css` adds the
approved section colors, cream workflow cards and gentle lift interaction.
`homepage.js` powers two independent output explorers and the trial calculator.
Collector downloads include canonical nested JSON and the existing flat CSV
projection; the scorer preview is explicitly fictional. `homepage-samples.js`
must contain the same records as `samples/explorer/*.json`.

Keep the version query on the homepage assets current when those assets change. Keep meaningful content in
reading order on mobile, and retain the lower-page technical contracts and
source limitations when editing the introductory copy.

## Privacy-minimized interaction events

`script.js` dispatches a local `nomad-agent:analytics` `CustomEvent` for page
views and annotated actions. Its allowlist accepts only short semantic values
such as event, product, placement, destination, and format; it does not collect
cookies, user IDs, query strings, form content, or resume data. Global Privacy
Control or Do Not Track suppresses the events.

No event leaves the browser by default. A site owner may deliberately attach a
subscriber, an existing `dataLayer`, or Plausible. Such a collector is a
separate deployment and consent decision; the current static site does not
prove that any event was received or tied to a product outcome.

## Production deployment and search discovery

`.github/workflows/deploy-website.yml` runs on relevant changes to `main`. It:

1. validates the IndexNow secret and prepares generated artifacts;
2. rejects uncommitted sitemap, robots, or contract drift;
3. runs the full repository test suite;
4. uses GitHub OIDC for Google authentication and checks exact Search Console
   property access;
5. deploys the isolated Firebase Hosting target;
6. verifies every live HTML and schema response against the checked-out bytes;
7. only then submits the sitemap to Google and canonical URLs to IndexNow.

A deployment receipt proves deployment. Search Console or IndexNow acceptance
proves notification, not crawling, indexing, ranking, or traffic.

The workflow requires the repository-scoped Workload Identity provider and
service account already documented in `.github/workflows/deploy-website.yml`,
plus an `INDEXNOW_KEY` secret containing 8–128 letters, digits, or dashes. The
provider keeps its stable `nomad-agent-job-scrapers` resource ID, but after
the repository cutover its trust condition and service-account principal must
both restrict access to `Exdenta/jobatlas` on `refs/heads/main`. The service
account must also be a full user of the exact URL-prefix Search Console
property `https://jobatlas.dev/`.

## Search measurement

`.github/workflows/seo-observatory.yml` captures a weekly 28-day Search Console
snapshot with raw query strings omitted, plus a read-only URL Inspection state
for every current canonical. The artifact is retained for 90 days. Search
Console reports top rows rather than a guaranteed exhaustive dataset, so the
report records that limitation. The operating cadence and evidence gates are in
`../docs/seo-program.md`.
