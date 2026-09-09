# Apify Store copy package

Status: local draft for review. Nothing in this directory has been published.

This package aligns the existing `job-atlas` publisher profile and four promoted Actor listings with Job Atlas. It leaves all `nomad-agent` listings, Actor code, builds, prices, schedules, billing, and customer integrations unchanged.

## Review surface

| Surface | Draft | Intended action |
| --- | --- | --- |
| Publisher profile | [publisher-profile.md](publisher-profile.md) | Replace the legacy Oink-led profile copy and old links. |
| LinkedIn Actor | [linkedin-enrich-translate-normalize-scraper.md](actors/linkedin-enrich-translate-normalize-scraper.md) | Correct links and state client support precisely. |
| EURAXESS Actor | [euraxess-enrich-translate-normalize-scraper.md](actors/euraxess-enrich-translate-normalize-scraper.md) | Correct links, identity, and client support. |
| Y Combinator Actor | [ycombinator-enrich-translate-normalize-scraper.md](actors/ycombinator-enrich-translate-normalize-scraper.md) | Correct links, add the run limit, and avoid unsupported client claims. |
| AI Job Fit Scorer | [ai-job-fit-scorer.md](actors/ai-job-fit-scorer.md) | Correct links and state the candidate, job, billing, and client boundaries. |

The exhaustive fleet disposition is machine-generated at [`catalogue/listing-disposition-v1.json`](../../catalogue/listing-disposition-v1.json). It accounts for 44 logical products and 48 deployments: only the four existing `job-atlas` listings receive drafts, while all 44 `nomad-agent` deployments are explicit `no-listing-change` records. One product/deployment pair is a known concurrent catalogue addition outside the isolated S03 baseline.

## Publication gate

Apply nothing until the profile and each listing are separately approved. Before an approved edit, capture the current public field values. Afterward, read back the public profile and all four listing pages and compare their exact URLs, titles, descriptions, README links, prices, and limits. A successful edit is listing readback only; it is not website deployment, discovery, indexing, Actor execution, billing, schedule, or named-destination proof.
