# Build a remote data-science and ML hiring shortlist

For a recruiter or candidate who needs original job descriptions. The bounded `input.json` searches data scientist and machine learning roles, filters for explicit remote arrangement, requests at most 50 jobs and at most 10 from each source. Explicit remote filtering withholds rows whose source does not state a remote arrangement. Results can be empty. Remote does not imply worldwide eligibility: the observed Commercial Data Scientist example is restricted to U.S. locations in its original description. Check country and residency requirements before using any result.

Store each record by `(source, id)`, retain `postedAt`, `deadline` and `url`, and read the complete `description` before selecting an opportunity. Source-supplied facts are not an AI assessment of suitability. The sample is an observed existing row whose original run can have different filters; it does not promise that the quickstart returns that posting. Its full description and immutable run/build receipt are in `output.example.json` and the companion build receipt.

The active schema is the 15-field `nomad-agent-job-row-v3`, with no `recordType`, AI fields or API-key inputs. Unknown scalars remain `null`; `locations: []` means no usable location and `hiringContacts: []` means no named contacts. `employmentTypes: null` means unknown. Dedupe uses the account/search and stable `dedupe.key`; unchanged runs can return no new rows. Store downstream history before changing that key.

Coverage comprises eight source groups and ten individual boards: Foorilla, Hacker News, YC, Built In, RemoteOK, Remotive, We Work Remotely, WTTJ, JustJoin.it and LinkedIn. Search filters apply before the result limits. LinkedIn searches have a six-combination limit and can be unavailable. Inspect `RUN-SUMMARY.unavailableSources` and partial status. No AI ranking is performed by this simple bundle.

At the captured Free-tier prices, 50 jobs cost $0.16 in Actor event charges ($0.003/job + $0.01 start); paid-plan discounts apply. This guide creates no schedule and performs no run until you explicitly execute the API quickstart.

Examples and executable script: `../examples/ml-ai-dev-bundle/`.

## API quickstart

Install `apify-client`, set `APIFY_TOKEN` in your environment, and run `python ../examples/ml-ai-dev-bundle/quickstart.py` from the `docs` directory. This starts a chargeable run with a $1 Actor-charge cap, selects `latest` and records the immutable build ID it returns. It writes the dataset and separate RUN-SUMMARY locally. Dataset retrieval is bounded to the requested item cap; inspect partial status and empty output. Your token is never included in URLs or printed.
