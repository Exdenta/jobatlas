# Job Actors: simple and normalized

The job-producing catalogue has two target tiers. Migration is in progress;
a tier label describes the intended contract, not a claim that every hosted
Actor already implements it. Existing paid contracts stay unchanged.

Both tiers are moving to stored jobs collected privately from public sources.
Private collection keeps reliable source facts and complete descriptions;
it performs no AI enrichment or translation. Public Actors will query that
inventory and will not search or parse source websites during a buyer's run.

## Simple Actors — v1 scoring

The target is the closed `nomad-agent-job-row-v2` contract: source, ID, URL,
title, company, locations, posting date, deadline, full description, HTML,
work arrangement, and source salary text, plus schema and record type.
There is no custom extension, AI enrichment, or translation. Posting age is
the only job filter; result limits are execution controls. V1 uses title,
company, location, source, URL, ID, and salary when available alongside the
full description. HTML and locations are always present; text-only source
descriptions receive a lossless escaped HTML representation.

Release status is shown per Actor below. Existing v1 and paid output
contracts keep their current meaning until their own migration.

| Actor | Migration status |
| --- | --- |
| [academicpositions-scraper](https://apify.com/nomad-agent/academicpositions-scraper) | Paid contract retained; migration skipped |
| [ai-job-search-agent](https://apify.com/nomad-agent/ai-job-search-agent) | Paid contract retained; migration skipped |
| [ai-jobs-net-scraper](https://apify.com/nomad-agent/ai-jobs-net-scraper) | Inventory and simple-contract migration pending |
| [american-jobs-bundle](https://apify.com/nomad-agent/american-jobs-bundle) | Inventory and simple-contract migration pending |
| [ashby-jobs-scraper](https://apify.com/nomad-agent/ashby-jobs-scraper) | Inventory and simple-contract migration pending |
| [builtin-scraper](https://apify.com/nomad-agent/builtin-scraper) | Inventory and simple-contract migration pending |
| [company-careers-bundle](https://apify.com/nomad-agent/company-careers-bundle) | Inventory and simple-contract migration pending |
| [devex-jobs-scraper](https://apify.com/nomad-agent/devex-jobs-scraper) | Inventory and simple-contract migration pending |
| [devex-scraper](https://apify.com/nomad-agent/devex-scraper) | Inventory and simple-contract migration pending |
| [euraxess-scraper](https://apify.com/nomad-agent/euraxess-scraper) | Paid contract retained; migration skipped |
| [eures-scraper](https://apify.com/nomad-agent/eures-scraper) | Paid contract retained; migration skipped |
| [foorilla-ai-jobs-scraper](https://apify.com/nomad-agent/foorilla-ai-jobs-scraper) | Inventory and simple-contract migration pending |
| [greenhouse-jobs-scraper](https://apify.com/nomad-agent/greenhouse-jobs-scraper) | Inventory and simple-contract migration pending |
| [hackernews-scraper](https://apify.com/nomad-agent/hackernews-scraper) | Paid contract retained; migration skipped |
| [ikerbasque-scraper](https://apify.com/nomad-agent/ikerbasque-scraper) | Inventory and simple-contract migration pending |
| [impactpool-scraper](https://apify.com/nomad-agent/impactpool-scraper) | Database-only simple v2 and complete descriptions verified |
| [infojobs-scraper](https://apify.com/nomad-agent/infojobs-scraper) | Inventory and simple-contract migration pending |
| [jobs-ac-uk-scraper](https://apify.com/nomad-agent/jobs-ac-uk-scraper) | Paid contract retained; migration skipped |
| [justjoinit-scraper](https://apify.com/nomad-agent/justjoinit-scraper) | Paid contract retained; migration skipped |
| [lever-jobs-scraper](https://apify.com/nomad-agent/lever-jobs-scraper) | Inventory and simple-contract migration pending |
| [linkedin-full-info-scraper](https://apify.com/nomad-agent/linkedin-full-info-scraper) | Inventory and simple-contract migration pending |
| [linkedin-scraper](https://apify.com/nomad-agent/linkedin-scraper) | Paid contract retained; migration skipped |
| [math-ku-phd-scraper](https://apify.com/nomad-agent/math-ku-phd-scraper) | Inventory and simple-contract migration pending |
| [ml-ai-dev-bundle](https://apify.com/nomad-agent/ml-ai-dev-bundle) | Paid contract retained; migration skipped |
| [nofluffjobs-scraper](https://apify.com/nomad-agent/nofluffjobs-scraper) | Inventory and simple-contract migration pending |
| [reliefweb-scraper](https://apify.com/nomad-agent/reliefweb-scraper) | Simple v2 inventory package prepared locally; hosted migration pending |
| [remote-boards-scraper](https://apify.com/nomad-agent/remote-boards-scraper) | Paid contract retained; migration skipped |
| [tecnoempleo-scraper](https://apify.com/nomad-agent/tecnoempleo-scraper) | Paid contract retained; migration skipped |
| [ub-doctoral-scraper](https://apify.com/nomad-agent/ub-doctoral-scraper) | Inventory and simple-contract migration pending |
| [un-careers-scraper](https://apify.com/nomad-agent/un-careers-scraper) | Inventory and simple-contract migration pending |
| [unjobs-scraper](https://apify.com/nomad-agent/unjobs-scraper) | Inventory and simple-contract migration pending |
| [web-dev-bundle](https://apify.com/nomad-agent/web-dev-bundle) | Paid contract retained; migration skipped |
| [web-search-scraper](https://apify.com/nomad-agent/web-search-scraper) | Retired in local code; hosted retirement not verified |
| [wellfound-scraper](https://apify.com/nomad-agent/wellfound-scraper) | Inventory and simple-contract migration pending |
| [workable-jobs-scraper](https://apify.com/nomad-agent/workable-jobs-scraper) | Inventory and simple-contract migration pending |
| [wttj-scraper](https://apify.com/nomad-agent/wttj-scraper) | Inventory and simple-contract migration pending |
| [ycombinator-was-scraper](https://apify.com/nomad-agent/ycombinator-was-scraper) | Paid contract retained; migration skipped |

## Normalized Actors — v3 scoring and advanced filtering

The target is the rich six-root `nomad-agent-job-v1` contract, full original
description and HTML, optional owner-funded AI enrichment, optional English
display translation, and advanced filters. New processing options default off;
existing Actor defaults are preserved. Raw source text remains unchanged.
No customer model key is required. Every normalized source and bundle is
intended to have a Job Atlas mirror; links below appear only for existing
metadata-verified mirrors. A mirror link does not prove a specific live run.

The status below separates verified inventory releases from pending work.
A six-root output alone does not establish working enrichment, translation,
or complete descriptions. Verification uses bounded functional tests and
does not imply an observed customer run.

| Primary Actor | Job Atlas | Migration status |
| --- | --- | --- |
| [all-jobs-scraper](https://apify.com/nomad-agent/all-jobs-scraper) | Planned; not published | Inventory, enrichment, and translation migration pending |
| [euraxess-enrich-translate-normalize-scraper](https://apify.com/nomad-agent/euraxess-enrich-translate-normalize-scraper) | [Job Atlas](https://apify.com/jobatlas/euraxess-enrich-translate-normalize-scraper) | Full-description proof migration pending |
| [europe-jobs-bundle](https://apify.com/nomad-agent/europe-jobs-bundle) | Planned; not published | Inventory, enrichment, and translation migration pending |
| [linkedin-enrich-translate-normalize-scraper](https://apify.com/nomad-agent/linkedin-enrich-translate-normalize-scraper) | [Job Atlas](https://apify.com/jobatlas/linkedin-enrich-translate-normalize-scraper) | Inventory migration pending |
| [normalized-ashby-jobs-scraper](https://apify.com/nomad-agent/normalized-ashby-jobs-scraper) | Planned; not published | Inventory, enrichment, and translation migration pending |
| [normalized-dynamitejobs-jobs-scraper](https://apify.com/nomad-agent/normalized-dynamitejobs-jobs-scraper) | Planned; not published | Inventory, enrichment, and translation migration pending |
| [normalized-euractiv-jobs-scraper](https://apify.com/nomad-agent/normalized-euractiv-jobs-scraper) | Planned; not published | Inventory, enrichment, and translation migration pending |
| [normalized-eurobrussels-jobs-scraper](https://apify.com/nomad-agent/normalized-eurobrussels-jobs-scraper) | [Job Atlas](https://apify.com/jobatlas/normalized-eurobrussels-jobs-scraper) | Inventory and complete descriptions verified; optional processing tested |
| [normalized-fashionjobs-jobs-scraper](https://apify.com/nomad-agent/normalized-fashionjobs-jobs-scraper) | Planned; not published | Inventory, enrichment, and translation migration pending |
| [normalized-greenhouse-jobs-scraper](https://apify.com/nomad-agent/normalized-greenhouse-jobs-scraper) | Planned; not published | Inventory, enrichment, and translation migration pending |
| [normalized-helloworld-jobs-scraper](https://apify.com/nomad-agent/normalized-helloworld-jobs-scraper) | Planned; not published | Inventory, enrichment, and translation migration pending |
| [normalized-himalayas-jobs-scraper](https://apify.com/nomad-agent/normalized-himalayas-jobs-scraper) | Planned; not published | Inventory, enrichment, and translation migration pending |
| [normalized-infostud-jobs-scraper](https://apify.com/nomad-agent/normalized-infostud-jobs-scraper) | Planned; not published | Inventory, enrichment, and translation migration pending |
| [normalized-jobgether-jobs-scraper](https://apify.com/nomad-agent/normalized-jobgether-jobs-scraper) | Planned; not published | Inventory, enrichment, and translation migration pending |
| [normalized-lever-jobs-scraper](https://apify.com/nomad-agent/normalized-lever-jobs-scraper) | Planned; not published | Inventory, enrichment, and translation migration pending |
| [normalized-manfred-jobs-scraper](https://apify.com/nomad-agent/normalized-manfred-jobs-scraper) | [Job Atlas](https://apify.com/jobatlas/normalized-manfred-jobs-scraper) | Inventory and complete descriptions verified; optional processing tested |
| [normalized-mlops-community-jobs-scraper](https://apify.com/nomad-agent/normalized-mlops-community-jobs-scraper) | Planned; not published | Inventory, enrichment, and translation migration pending |
| [normalized-smartrecruiters-jobs-scraper](https://apify.com/nomad-agent/normalized-smartrecruiters-jobs-scraper) | Planned; not published | Inventory, enrichment, and translation migration pending |
| [researcher-bundle](https://apify.com/nomad-agent/researcher-bundle) | Planned; not published | Inventory, enrichment, and translation migration pending |
| [ycombinator-enrich-translate-normalize-scraper](https://apify.com/nomad-agent/ycombinator-enrich-translate-normalize-scraper) | [Job Atlas](https://apify.com/jobatlas/ycombinator-enrich-translate-normalize-scraper) | Full-description proof migration pending |

The [AI job-fit scorer](https://apify.com/jobatlas/ai-job-fit-scorer) is a
downstream matching product with its own result contract, not a third job
Actor tier. Table exports and integration projections are also consumer
formats rather than additional public job tiers.
