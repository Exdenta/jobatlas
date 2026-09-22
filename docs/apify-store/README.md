# Apify Store copy package

Status: local draft for review. Nothing in this directory has been published.

This package aligns the existing `jobatlas` publisher profile and four promoted Actor listings with Job Atlas. It leaves all `nomad-agent` listings, Actor code, builds, prices, schedules, billing, and customer integrations unchanged.

## Review surface

| Surface | Draft | Intended action |
| --- | --- | --- |
| Publisher profile | [publisher-profile.md](publisher-profile.md) | Replace the legacy Oink-led profile copy and old links. |
| LinkedIn Actor | [linkedin-enrich-translate-normalize-scraper.md](actors/linkedin-enrich-translate-normalize-scraper.md) | Correct links and state client support precisely. |
| EURAXESS Actor | [euraxess-enrich-translate-normalize-scraper.md](actors/euraxess-enrich-translate-normalize-scraper.md) | Correct links, identity, and client support. |
| Y Combinator Actor | [ycombinator-enrich-translate-normalize-scraper.md](actors/ycombinator-enrich-translate-normalize-scraper.md) | Correct links, add the run limit, and avoid unsupported client claims. |
| AI Job Fit Scorer | [ai-job-fit-scorer.md](actors/ai-job-fit-scorer.md) | Correct links and state the candidate, job, billing, and client boundaries. |

The current catalogue accounts for 58 logical products and 65 deployments: 58 original-publisher deployments and seven Job Atlas copies. Exactly four Job Atlas listings have local copy drafts; the other three copies and all original-publisher listings have no listing change. The generated disposition manifest makes no publication or execution claim.

## Publication gate

Apply nothing until the profile and each listing are separately approved. Before an approved edit, capture the current public field values. Afterward, read back the public profile and all four listing pages and compare their exact URLs, titles, descriptions, README links, prices, and limits. A successful edit is listing readback only; it is not website deployment, discovery, indexing, Actor execution, billing, schedule, or named-destination proof.
