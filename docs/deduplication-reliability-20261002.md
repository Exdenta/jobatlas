# Cross-run deduplication reliability update

Release date: 2 October 2026.

A retained job could be selected even when it was absent from the current inventory response, causing a run to fail while mapping its identifier. The updated runtimes select delivery candidates from the current response. Retained jobs stay available for a later response, and jobs already delivered remain suppressed.

The public deployments below use the repaired build through `latest` and the default selector. Existing input/output contracts, prices and visibility were preserved. Release checks used bounded API runs with at most two results. Normalized Job Atlas checks also enabled optional AI enrichment and translation. These checks establish Actor execution; customer workflows and destination integrations were not exercised.

| Account | Actor | Verified build | Immutable build ID |
| --- | --- | --- | --- |
| jobatlas | normalized-ashby-jobs-scraper | 1.0.2 | `kgqD7fC6JpmyfOApp` |
| jobatlas | normalized-euractiv-jobs-scraper | 1.0.3 | `PIdcLGPrJyzZAgaLT` |
| jobatlas | normalized-eurobrussels-jobs-scraper | 1.0.2 | `zpsf6yv0qNRwZJaXV` |
| jobatlas | normalized-fashionjobs-jobs-scraper | 1.0.2 | `FNJ9lQTP17s5V8dSY` |
| jobatlas | normalized-helloworld-jobs-scraper | 1.0.2 | `lGP02SuFPKB5WUuNf` |
| jobatlas | normalized-himalayas-jobs-scraper | 1.0.2 | `PxVcOCoasOBeN5J5L` |
| jobatlas | normalized-infostud-jobs-scraper | 1.0.2 | `0qcVq7ohJDumNmwdn` |
| jobatlas | normalized-manfred-jobs-scraper | 1.0.3 | `JIdHJ5wqHrB3nz3gS` |
| nomad-agent | [academicpositions-scraper](https://apify.com/nomad-agent/academicpositions-scraper) | 0.1.48 | `2qM2QMuTBjwZvfMxf` |
| nomad-agent | [ai-jobs-net-scraper](https://apify.com/nomad-agent/ai-jobs-net-scraper) | 0.1.40 | `jrAfLfjdmVd33UhQm` |
| nomad-agent | [ashby-jobs-scraper](https://apify.com/nomad-agent/ashby-jobs-scraper) | 0.1.27 | `O2U93al9LxbSfEAKN` |
| nomad-agent | [builtin-scraper](https://apify.com/nomad-agent/builtin-scraper) | 0.1.42 | `m6RYtjM4Eymi90z32` |
| nomad-agent | [company-careers-bundle](https://apify.com/nomad-agent/company-careers-bundle) | 0.1.33 | `psecgjh951q9CWsKl` |
| nomad-agent | [euraxess-scraper](https://apify.com/nomad-agent/euraxess-scraper) | 0.1.35 | `1D4xYOR60bdVbWLdz` |
| nomad-agent | [eures-scraper](https://apify.com/nomad-agent/eures-scraper) | 0.1.41 | `8KXKWVFNBnEu5E1wk` |
| nomad-agent | [foorilla-ai-jobs-scraper](https://apify.com/nomad-agent/foorilla-ai-jobs-scraper) | 0.1.8 | `J8hYA3Ce1XTgb0MzT` |
| nomad-agent | [greenhouse-jobs-scraper](https://apify.com/nomad-agent/greenhouse-jobs-scraper) | 0.1.27 | `lOHs8n0l8pAfuFxlJ` |
| nomad-agent | [hackernews-scraper](https://apify.com/nomad-agent/hackernews-scraper) | 0.1.41 | `vB1Eyt8OPNGkmP1fB` |
| nomad-agent | [ikerbasque-scraper](https://apify.com/nomad-agent/ikerbasque-scraper) | 0.1.37 | `bF0sx0HKmdVCtqhNy` |
| nomad-agent | [impactpool-scraper](https://apify.com/nomad-agent/impactpool-scraper) | 0.1.40 | `FyDGxoOvnhmgdqx1S` |
| nomad-agent | [infojobs-scraper](https://apify.com/nomad-agent/infojobs-scraper) | 0.1.41 | `ORVwhaUvwxJlxVGbG` |
| nomad-agent | [jobs-ac-uk-scraper](https://apify.com/nomad-agent/jobs-ac-uk-scraper) | 0.1.40 | `9SWr1KecB37RzS4aH` |
| nomad-agent | [justjoinit-scraper](https://apify.com/nomad-agent/justjoinit-scraper) | 0.1.36 | `bTZKHXEVhzebAmRa3` |
| nomad-agent | [lever-jobs-scraper](https://apify.com/nomad-agent/lever-jobs-scraper) | 0.1.28 | `7vQQV26KQDN0ANCek` |
| nomad-agent | [linkedin-full-info-scraper](https://apify.com/nomad-agent/linkedin-full-info-scraper) | 0.1.10 | `sKRQXECbZ5kk4HpxN` |
| nomad-agent | [math-ku-phd-scraper](https://apify.com/nomad-agent/math-ku-phd-scraper) | 0.2.1 | `Ose5kZnF3TWxJWImn` |
| nomad-agent | [nofluffjobs-scraper](https://apify.com/nomad-agent/nofluffjobs-scraper) | 0.1.37 | `fIhlwc7aX4rCMdGJk` |
| nomad-agent | [normalized-ashby-jobs-scraper](https://apify.com/nomad-agent/normalized-ashby-jobs-scraper) | 1.0.5 | `QZ5GScm2Oo8Mi1X2Z` |
| nomad-agent | [normalized-dynamitejobs-jobs-scraper](https://apify.com/nomad-agent/normalized-dynamitejobs-jobs-scraper) | 1.0.5 | `mBe17R2X98kqVg31z` |
| nomad-agent | [normalized-euractiv-jobs-scraper](https://apify.com/nomad-agent/normalized-euractiv-jobs-scraper) | 1.0.5 | `s898vUb7F8uzCGsq3` |
| nomad-agent | [normalized-eurobrussels-jobs-scraper](https://apify.com/nomad-agent/normalized-eurobrussels-jobs-scraper) | 1.0.4 | `DK9m8Uud7Pge22JC2` |
| nomad-agent | [normalized-fashionjobs-jobs-scraper](https://apify.com/nomad-agent/normalized-fashionjobs-jobs-scraper) | 1.0.5 | `xfciyKAcWMdh1sTT0` |
| nomad-agent | [normalized-greenhouse-jobs-scraper](https://apify.com/nomad-agent/normalized-greenhouse-jobs-scraper) | 1.0.6 | `bsdQqhqB4rxRuIzIr` |
| nomad-agent | [normalized-helloworld-jobs-scraper](https://apify.com/nomad-agent/normalized-helloworld-jobs-scraper) | 1.0.4 | `zmzQSUCmOlhPRfeYU` |
| nomad-agent | [normalized-himalayas-jobs-scraper](https://apify.com/nomad-agent/normalized-himalayas-jobs-scraper) | 1.0.5 | `7PajeyxeTd6xAA3qS` |
| nomad-agent | [normalized-infostud-jobs-scraper](https://apify.com/nomad-agent/normalized-infostud-jobs-scraper) | 1.0.3 | `j9vuM50Ag56UTjpWP` |
| nomad-agent | [normalized-jobgether-jobs-scraper](https://apify.com/nomad-agent/normalized-jobgether-jobs-scraper) | 1.0.10 | `vgGqRrGrYVee6sjk3` |
| nomad-agent | [normalized-lever-jobs-scraper](https://apify.com/nomad-agent/normalized-lever-jobs-scraper) | 1.0.5 | `p0Ah47WqUxHRySSUI` |
| nomad-agent | [normalized-manfred-jobs-scraper](https://apify.com/nomad-agent/normalized-manfred-jobs-scraper) | 1.0.6 | `4XQ7hasM6z7wNr0EV` |
| nomad-agent | [normalized-mlops-community-jobs-scraper](https://apify.com/nomad-agent/normalized-mlops-community-jobs-scraper) | 1.0.4 | `4OvF5Cn1OtwdUK9LP` |
| nomad-agent | [normalized-smartrecruiters-jobs-scraper](https://apify.com/nomad-agent/normalized-smartrecruiters-jobs-scraper) | 1.0.5 | `NwF0nKCPbBo5EmztN` |
| nomad-agent | [reliefweb-scraper](https://apify.com/nomad-agent/reliefweb-scraper) | 0.1.36 | `qxQXsPxxoV875brDe` |
| nomad-agent | [remote-boards-scraper](https://apify.com/nomad-agent/remote-boards-scraper) | 0.1.39 | `5WYlij8jntzRlhw4t` |
| nomad-agent | [ub-doctoral-scraper](https://apify.com/nomad-agent/ub-doctoral-scraper) | 0.1.46 | `sZTOrfiqzkxTcjCoC` |
| nomad-agent | [un-careers-scraper](https://apify.com/nomad-agent/un-careers-scraper) | 0.1.39 | `jcOGGwiDPa3XOzPEJ` |
| nomad-agent | [unjobs-scraper](https://apify.com/nomad-agent/unjobs-scraper) | 0.1.18 | `isaQe24Euaqa1SH8m` |
| nomad-agent | [wellfound-scraper](https://apify.com/nomad-agent/wellfound-scraper) | 0.1.35 | `qcWYoUcOvTwUNkk8I` |
| nomad-agent | [workable-jobs-scraper](https://apify.com/nomad-agent/workable-jobs-scraper) | 0.1.28 | `xhQ4JbUqdeKJnZc83` |
| nomad-agent | [wttj-scraper](https://apify.com/nomad-agent/wttj-scraper) | 0.1.32 | `ngDoIndT6nk1vkpQa` |
| nomad-agent | [ycombinator-was-scraper](https://apify.com/nomad-agent/ycombinator-was-scraper) | 0.1.38 | `puJLrbpWI9u6iTBY0` |

Use `latest` in maintained callers and record the immutable build ID returned by each run. Historical build numbers in this table are evidence from the release checks, rather than selectors to pin in new callers.
