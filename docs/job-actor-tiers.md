# Job Actors: simple and normalized

Choose by the data you need. Simple Actors return source facts and descriptions in flat rows. Normalized Actors return the nested `nomad-agent-job-v1` format, with source-specific facts and optional processing where supported. AI job search and fit scoring are separate products.

The current simple row is `nomad-agent-job-row-v3`: 15 fields, including `employmentTypes` and `hiringContacts`, without `recordType`. Older v2 rows include `recordType`; some source-specific Actors keep separate inputs and outputs. Read the exact Actor's published schema instead of assuming every endpoint is interchangeable.

Simple rows perform no AI enrichment or translation. Query, location, work arrangement, employment type, posting-age and repeat controls depend on the Actor. See the [simple filter guide](simple-filters-v2.md) and [bounded input examples](job-actor-input-examples.md). `tecnoempleo-scraper` and both Devex products have their own input controls.

All Jobs, Europe, American, Researcher, Web Developer, Company Careers and ML/AI bundles currently return simple rows. The separate `ai-job-search-agent` ranks jobs against a resume, and `ai-job-fit-scorer` returns candidate evaluations; neither is a simple source feed.

## Public normalized endpoints

Public endpoint identities were checked on 4 October 2026. Links establish public availability; this documentation check did not execute any endpoint or test optional AI, translation or destination delivery. Each copy has its own input defaults, pricing, builds and execution evidence.

| Source | Nomad Agent | Job Atlas |
| --- | --- | --- |
| EURAXESS Jobs Scraper \| Full Details & AI Enrichment | [Actor](https://apify.com/nomad-agent/euraxess-enrich-translate-normalize-scraper) | [Actor](https://apify.com/jobatlas/euraxess-enrich-translate-normalize-scraper) |
| LinkedIn Jobs Scraper \| AI Enrichment | [Actor](https://apify.com/nomad-agent/linkedin-enrich-translate-normalize-scraper) | [Actor](https://apify.com/jobatlas/linkedin-enrich-translate-normalize-scraper) |
| Ashby Jobs \| Normalized | [Actor](https://apify.com/nomad-agent/normalized-ashby-jobs-scraper) | [Actor](https://apify.com/jobatlas/normalized-ashby-jobs-scraper) |
| Dynamite Jobs \| Normalized | [Actor](https://apify.com/nomad-agent/normalized-dynamitejobs-jobs-scraper) | [Actor](https://apify.com/jobatlas/normalized-dynamitejobs-jobs-scraper) |
| EURACTIV Jobs \| Normalized | [Actor](https://apify.com/nomad-agent/normalized-euractiv-jobs-scraper) | [Actor](https://apify.com/jobatlas/normalized-euractiv-jobs-scraper) |
| EuroBrussels Jobs \| Normalized | [Actor](https://apify.com/nomad-agent/normalized-eurobrussels-jobs-scraper) | [Actor](https://apify.com/jobatlas/normalized-eurobrussels-jobs-scraper) |
| FashionJobs \| Normalized | [Actor](https://apify.com/nomad-agent/normalized-fashionjobs-jobs-scraper) | [Actor](https://apify.com/jobatlas/normalized-fashionjobs-jobs-scraper) |
| Greenhouse Jobs \| Normalized | [Actor](https://apify.com/nomad-agent/normalized-greenhouse-jobs-scraper) | No public endpoint verified |
| HelloWorld.rs Jobs \| Normalized | [Actor](https://apify.com/nomad-agent/normalized-helloworld-jobs-scraper) | [Actor](https://apify.com/jobatlas/normalized-helloworld-jobs-scraper) |
| Himalayas Jobs \| Normalized | [Actor](https://apify.com/nomad-agent/normalized-himalayas-jobs-scraper) | [Actor](https://apify.com/jobatlas/normalized-himalayas-jobs-scraper) |
| Poslovi Infostud Jobs \| Normalized | [Actor](https://apify.com/nomad-agent/normalized-infostud-jobs-scraper) | [Actor](https://apify.com/jobatlas/normalized-infostud-jobs-scraper) |
| Jobgether Jobs \| Normalized | [Actor](https://apify.com/nomad-agent/normalized-jobgether-jobs-scraper) | [Actor](https://apify.com/jobatlas/normalized-jobgether-jobs-scraper) |
| Lever Jobs \| Normalized | [Actor](https://apify.com/nomad-agent/normalized-lever-jobs-scraper) | [Actor](https://apify.com/jobatlas/normalized-lever-jobs-scraper) |
| Manfred Jobs \| Normalized | [Actor](https://apify.com/nomad-agent/normalized-manfred-jobs-scraper) | [Actor](https://apify.com/jobatlas/normalized-manfred-jobs-scraper) |
| MLOps Community Jobs \| Normalized | [Actor](https://apify.com/nomad-agent/normalized-mlops-community-jobs-scraper) | [Actor](https://apify.com/jobatlas/normalized-mlops-community-jobs-scraper) |
| SmartRecruiters Jobs \| Normalized | [Actor](https://apify.com/nomad-agent/normalized-smartrecruiters-jobs-scraper) | [Actor](https://apify.com/jobatlas/normalized-smartrecruiters-jobs-scraper) |
| Y Combinator Jobs Scraper \| Pipelines & Alerts | [Actor](https://apify.com/nomad-agent/ycombinator-enrich-translate-normalize-scraper) | [Actor](https://apify.com/jobatlas/ycombinator-enrich-translate-normalize-scraper) |

Normalized records preserve original source evidence. Unknown facts are `null`; empty arrays follow the documented field semantics. Enrichment may fill supported missing facts, and translation changes selected display fields while preserving original descriptions. Check each Actor's defaults and pricing before enabling either option.

Filters and repeat suppression can reduce output or produce a valid empty result. Complete source coverage and current availability are separate from the format of a row. Inspect `RUN-SUMMARY` and the dataset, and check original application requirements before acting on a job.

See the [complete public Actor directory](public-actors.md) for every simple source, bundle, normalized endpoint, scorer and non-job product.
