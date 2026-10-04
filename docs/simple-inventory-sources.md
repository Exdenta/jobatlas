# Simple job Actors: source facts and complete descriptions

Simple job Actors return source-linked postings with original descriptions, HTML and locations. Current readers use the 15-field `nomad-agent-job-row-v3`; older row-v2 output includes `recordType`. Check the exact endpoint's current schema. Unknown optional values are `null`; `locations: []` means no usable location was parsed.

| Actor |
| --- |
| [AcademicPositions academic jobs](https://apify.com/nomad-agent/academicpositions-scraper) |
| [American jobs bundle](https://apify.com/nomad-agent/american-jobs-bundle) |
| [Ashby jobs](https://apify.com/nomad-agent/ashby-jobs-scraper) |
| [Built In jobs](https://apify.com/nomad-agent/builtin-scraper) |
| [Company careers bundle](https://apify.com/nomad-agent/company-careers-bundle) |
| [EURAXESS legacy jobs](https://apify.com/nomad-agent/euraxess-scraper) |
| [EURES jobs](https://apify.com/nomad-agent/eures-scraper) |
| [Foorilla Data, AI, and Machine Learning jobs](https://apify.com/nomad-agent/foorilla-ai-jobs-scraper) |
| [Greenhouse jobs](https://apify.com/nomad-agent/greenhouse-jobs-scraper) |
| [Hacker News jobs and search](https://apify.com/nomad-agent/hackernews-scraper) |
| [Ikerbasque jobs](https://apify.com/nomad-agent/ikerbasque-scraper) |
| [Impactpool jobs](https://apify.com/nomad-agent/impactpool-scraper) |
| [InfoJobs Spain jobs](https://apify.com/nomad-agent/infojobs-scraper) |
| [JustJoin.it jobs](https://apify.com/nomad-agent/justjoinit-scraper) |
| [Lever jobs](https://apify.com/nomad-agent/lever-jobs-scraper) |
| [LinkedIn full-information jobs](https://apify.com/nomad-agent/linkedin-full-info-scraper) |
| [LinkedIn short-output jobs](https://apify.com/nomad-agent/linkedin-scraper) |
| [NoFluffJobs](https://apify.com/nomad-agent/nofluffjobs-scraper) |
| [Remote job boards: RemoteOK, Remotive, We Work Remotely and Himalayas](https://apify.com/nomad-agent/remote-boards-scraper) |
| [UN Careers jobs](https://apify.com/nomad-agent/un-careers-scraper) |
| [Universitat de Barcelona doctoral jobs](https://apify.com/nomad-agent/ub-doctoral-scraper) |
| [University of Copenhagen mathematics PhD jobs](https://apify.com/nomad-agent/math-ku-phd-scraper) |
| [Web developer jobs bundle](https://apify.com/nomad-agent/web-dev-bundle) |
| [Welcome to the Jungle jobs](https://apify.com/nomad-agent/wttj-scraper) |
| [Wellfound startup jobs](https://apify.com/nomad-agent/wellfound-scraper) |
| [Workable jobs](https://apify.com/nomad-agent/workable-jobs-scraper) |
| [Y Combinator Work at a Startup legacy jobs](https://apify.com/nomad-agent/ycombinator-was-scraper) |
| [aijobs.net jobs](https://apify.com/nomad-agent/ai-jobs-net-scraper) |
| [jobs.ac.uk jobs](https://apify.com/nomad-agent/jobs-ac-uk-scraper) |

Select `latest` and record the immutable build returned by the run. Simple Actors are available in the Nomad Agent namespace; Job Atlas publishes separate normalized products.

## First run

Most current simple Actors accept the input below. Confirm it against the exact Actor's Input tab; Tecnoempleo and Devex have their own inputs. See the [schema-checked examples](job-actor-input-examples.md).

```json
{
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "maxItems": 5,
  "postedWithin": "any",
  "dedupe": {"enabled": true, "key": ""}
}
```

The [filter guide](simple-filters-v2.md) documents queries, locations, work arrangement and employment type. `postedWithin` accepts `any` or a positive duration such as `7d`. Where a reliable source date is unavailable, the date is the first observation; later observations do not make the posting new. Filtering and source availability can produce fewer results or an empty dataset.

Repeat suppression is enabled by default where supported. Disable it for a stateless inspection. Inspect `RUN-SUMMARY` separately from job rows for partial status, unavailable sources and notes about older inputs. Check the current Pricing tab and set a cost cap before running.

## Compatibility

Row v3 uses `employmentTypes` and `hiringContacts`, and omits `recordType`. Earlier fields such as `snippet`, singular `location`, split salary fields and `hiringContact*` are not part of the current closed row. Use `locations`, `workType`, `salary`, `employmentTypes` and `hiringContacts`. Preserve `(source, id)` as the posting key; Foorilla-backed postings use `source: "foorilla"`, and remote-board IDs include their board identity.

`linkedin-full-info-scraper` is deprecated in favour of `linkedin-scraper`; check the listing notice before changing an existing integration. Company Careers supports its documented coverage; older `companies`, `presetLists` and `atsProviders` controls are ignored with a summary note and do not add an employer to the search.

ML/AI searches AI and machine-learning phrases by default. Your `queries` replace the defaults; `[]` removes the query filter. Results from its supported boards are ordered by date and capped by `maxItemsPerSource` and `maxItems`. Source limits can make the summary partial. This simple bundle does not rank suitability with AI.

The [ML hiring workflow](ml-ai-dev-bundle-workflow.md) includes bounded inputs, a dated observed row and an API quickstart. Remote eligibility requires reading the original description; the example has U.S. restrictions. Offline example validation does not establish a destination integration or normal buyer traffic.

See the [public directory](public-actors.md) for all sources, bundles and separate normalized products.
