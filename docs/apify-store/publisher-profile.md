# Job Atlas publisher profile draft

- Target: `https://apify.com/job-atlas`
- Observed: 2026-09-09
- Status: approval-gated local draft

## Dated public observation

The display name is already `Job Atlas` and the stable publisher identifier is already `job-atlas`. The current bio leads with Lex and Oink. The current profile README links to `https://nomadagent.dev/` and `https://github.com/Exdenta/nomad-agent-job-scrapers`. The existing GitHub username `Exdenta` and LinkedIn URL remain valid.

## Copy-ready fields

Display name — keep unchanged:

```text
Job Atlas
```

Publisher identifier — keep unchanged:

```text
job-atlas
```

Bio — replace with:

```text
Job Atlas publishes source-linked job-data and candidate-fit Actors for alerts, trackers, career products, and AI agents.
```

Website — replace with:

```text
https://jobatlas.dev/
```

GitHub username — keep unchanged:

```text
Exdenta
```

LinkedIn — keep unchanged:

```text
https://www.linkedin.com/in/lexsherman/
```

Profile README — replace with:

```markdown
#### Job data for the things you're building

Job Atlas publishes focused job-data Actors for LinkedIn, Y Combinator, and EURAXESS, plus an AI job-fit scorer. Start with five results, inspect the source-linked output, and connect only the workflow your product needs.

- [LinkedIn Jobs Scraper](https://apify.com/job-atlas/linkedin-enrich-translate-normalize-scraper)
- [Y Combinator Jobs Scraper](https://apify.com/job-atlas/ycombinator-enrich-translate-normalize-scraper)
- [EURAXESS Jobs Scraper](https://apify.com/job-atlas/euraxess-enrich-translate-normalize-scraper)
- [AI Job Search & Fit Scorer](https://apify.com/job-atlas/ai-job-fit-scorer)

[Website](https://jobatlas.dev/) | [Source and integration guides](https://github.com/Exdenta/jobatlas) | [LinkedIn](https://www.linkedin.com/in/lexsherman/)
```

Do not add mutable user counts, run-success percentages, or unsupported integration claims to the authored profile copy.

## Readback gate

After separate approval and publication, require a public 200 response, the unchanged `job-atlas` identifier, the exact bio and website above, the canonical repository, and links to exactly the four promoted Actors. Record any Apify normalization separately instead of silently altering this draft.
