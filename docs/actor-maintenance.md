# Actor maintenance notes

## 27 September 2026: local compatibility cleanup

Local maintenance candidates for the LinkedIn, EURAXESS, Y Combinator and AI Job Search & Fit Scorer Actors share equivalent input, text, retry and summary helpers. Existing input and output contracts, optional enrichment and translation controls, pricing and production selectors are unchanged. Each source retains its current retry and text interpretation rules.

This is a local code cleanup. It has not been deployed to either organization, and it does not establish new live execution or destination integration evidence. Existing integrations continue to select `latest` and inspect the immutable build returned by each run.


## 2 October 2026: simple job deduplication repair

A repair has been released for All Jobs, Job Search, Web Developer, Researcher, Europe Jobs, American Jobs and LinkedIn Jobs in the `nomad-agent` namespace. A job missing from the current search response stays eligible for a later response instead of failing the run. Repeated runs continue to suppress jobs already delivered. Dedupe remains enabled in the default and prefilled inputs; prefilled searches now use smaller limits.

Job Search uses the current 15-field `nomad-agent-job-row-v3` output, without `recordType`. Its documented source coverage is retained. Prices and visibility are unchanged. Each Actor was checked through its promoted `latest` and default selector. Each exact prefilled-input run returned 20 valid rows, and repeated runs did not redeliver earlier jobs. These bounded checks leave additional postings outside the bounded check. The next automatic platform QA, normal buyer traffic and destination integrations are unverified.
