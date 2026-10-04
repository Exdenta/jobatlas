# Search filters for simple job Actors

The Actors below accept `nomad-agent-simple-inventory-search-v2` and return `nomad-agent-job-row-v3`. They return source-linked postings with complete original descriptions. They do not use AI or require an AI API key.

## Search inputs

```json
{
  "schemaVersion": "nomad-agent-simple-inventory-search-v2",
  "queries": ["software engineer", "python developer"],
  "locations": ["Germany"],
  "locationTypes": ["remote"],
  "employmentTypes": ["Full-time"],
  "postedWithin": "7d",
  "maxItems": 5,
  "dedupe": {"enabled": true, "key": ""}
}
```

Each filter is optional. Empty lists leave that filter off. Queries match whole words in the title and description: all words in one query must appear, and any query can match. Locations match source city, region, country names or ISO country codes. `EU` and `Europe` expand to their countries; Europe excludes Russia, Belarus and Turkey.

`locationTypes` accepts `remote`, `hybrid` and `onsite`. `employmentTypes` accepts `Full-time`, `Part-time`, `Contract` and `Internship`. A posting with unknown arrangement or employment type is excluded when the corresponding filter is active. Some boards do not supply these facts, so filtered coverage can be smaller than the unfiltered search.

Bundles accept `maxItemsPerSource`, default 50. It caps each source before `maxItems` selects the newest postings across sources. `maxItems` is limited to 200; zero means 200. Larger legacy limits are clamped with a note.

Earlier fields remain accepted: `keyword`, `keywords`, `query` and `searchQuery` map to queries; `location`, `searchLocation` and `city` map to locations. `remote: true`, `remoteOnly: true`, and the old web search's `remote: "remote-only"` map to the remote filter. Its `maxAgeHours` maps to posting age. Other unsupported fields are ignored and listed in `RUN-SUMMARY.inputNotes`.

## Job rows and repeats

Row v3 adds `employmentTypes` (null when unknown) and `hiringContacts` (named people only, `[]` when none). The existing source, ID, URL, title, company, locations, dates, complete description, HTML, work type and salary remain. Unknown optional facts are null; missing usable location labels are `[]`. Multiple source arrangements can produce a null `workType` while still matching an arrangement filter.

With an empty `dedupe.key`, filters have separate repeat histories. A non-empty key intentionally shares one history across those searches. An unfiltered search retains its earlier history. A capped bundle can deliver the next unsent posting on a repeat; it never delivers the same posting twice in that history. A repeat that finds no unsent matches has no result charge. Existing pricing remains unchanged.

Select `latest` or the default selector and record the immutable build ID the run returns. Inspect `RUN-SUMMARY` for filters, legacy-field notes and unavailable sources. These simple Actors are separate from the normalized Actors' `nomad-agent-job-v1` output.

## Actors using these contracts

- [academicpositions-scraper](https://apify.com/nomad-agent/academicpositions-scraper)
- [ai-jobs-net-scraper](https://apify.com/nomad-agent/ai-jobs-net-scraper)
- [ashby-jobs-scraper](https://apify.com/nomad-agent/ashby-jobs-scraper)
- [builtin-scraper](https://apify.com/nomad-agent/builtin-scraper)
- [company-careers-bundle](https://apify.com/nomad-agent/company-careers-bundle)
- [euraxess-scraper](https://apify.com/nomad-agent/euraxess-scraper)
- [eures-scraper](https://apify.com/nomad-agent/eures-scraper)
- [foorilla-ai-jobs-scraper](https://apify.com/nomad-agent/foorilla-ai-jobs-scraper)
- [greenhouse-jobs-scraper](https://apify.com/nomad-agent/greenhouse-jobs-scraper)
- [hackernews-scraper](https://apify.com/nomad-agent/hackernews-scraper)
- [infojobs-scraper](https://apify.com/nomad-agent/infojobs-scraper)
- [jobs-ac-uk-scraper](https://apify.com/nomad-agent/jobs-ac-uk-scraper)
- [justjoinit-scraper](https://apify.com/nomad-agent/justjoinit-scraper)
- [lever-jobs-scraper](https://apify.com/nomad-agent/lever-jobs-scraper)
- [linkedin-full-info-scraper](https://apify.com/nomad-agent/linkedin-full-info-scraper)
- [linkedin-scraper](https://apify.com/nomad-agent/linkedin-scraper)
- [nofluffjobs-scraper](https://apify.com/nomad-agent/nofluffjobs-scraper)
- [ub-doctoral-scraper](https://apify.com/nomad-agent/ub-doctoral-scraper)
- [wellfound-scraper](https://apify.com/nomad-agent/wellfound-scraper)
- [workable-jobs-scraper](https://apify.com/nomad-agent/workable-jobs-scraper)
- [wttj-scraper](https://apify.com/nomad-agent/wttj-scraper)
- [ycombinator-was-scraper](https://apify.com/nomad-agent/ycombinator-was-scraper)
- [remote-boards-scraper](https://apify.com/nomad-agent/remote-boards-scraper)
- [american-jobs-bundle](https://apify.com/nomad-agent/american-jobs-bundle)
- [web-dev-bundle](https://apify.com/nomad-agent/web-dev-bundle)
- [web-search-scraper](https://apify.com/nomad-agent/web-search-scraper)

- [reliefweb-scraper](https://apify.com/nomad-agent/reliefweb-scraper)
- [unjobs-scraper](https://apify.com/nomad-agent/unjobs-scraper)
- [ikerbasque-scraper](https://apify.com/nomad-agent/ikerbasque-scraper)
- [impactpool-scraper](https://apify.com/nomad-agent/impactpool-scraper)

`web-search-scraper` searches its supported public sources with the same filters and rows. Its earlier AI provider and key fields are accepted and ignored. The separate `ai-job-search-agent` has not changed.

Web search includes MLOps Community, EURACTIV and DynamiteJobs alongside the other supported boards. Coverage depends on the facts each source publishes; missing employment and arrangement facts remain unknown.
