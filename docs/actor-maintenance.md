# Actor maintenance notes

## 27 September 2026: local compatibility cleanup

Local maintenance candidates for the LinkedIn, EURAXESS, Y Combinator and AI Job Search & Fit Scorer Actors share equivalent input, text, retry and summary helpers. Existing input and output contracts, optional enrichment and translation controls, pricing and production selectors are unchanged. Each source retains its current retry and text interpretation rules.

This is a local code cleanup. It has not been deployed to either organization, and it does not establish new live execution or destination integration evidence. Existing integrations continue to select `latest` and inspect the immutable build returned by each run.
