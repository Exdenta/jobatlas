# Job Atlas website style guide

Approved direction: 9 September 2026. This guide records the original visual system and the homepage refinements selected during local review. The production implementation lives in `website/` and is served at [jobatlas.dev](https://jobatlas.dev/). The approved local review was Original Plus.

## Design character

Use the existing Italian transit-ticket character: bottle green, warm paper, restrained vermilion accents, clear typography and simple rectangular surfaces. Keep the original header, hero identity and page layouts. The selected homepage content is an extension of that design.

Field Guide and Data Studio are earlier explorations. Their new visual systems were rejected; do not use them as design references. Other pages retain their original layouts until separately reviewed. Correcting links and naming does not authorize redesigning those pages.

## Color palette

Use the existing CSS variables rather than introducing close substitutes.

| Token | Value | Role |
| --- | --- | --- |
| `--green` | `#0B4B38` | Hero, workflow section, main text and primary buttons |
| `--green-dark` | `#063829` | Footer and the workflow tool-logo row |
| `--background` | `#F6EFDF` | Light cream section background |
| `--paper` | `#EEE3CA` | Alternating paper section background |
| `--paper-light` | `#FBF5E8` | Output panels, workflow cards and form controls |
| `--cream` | `#F4E8CF` | Main text on green backgrounds |
| `--muted` | `#566153` | Secondary text on light surfaces |
| Dark-section secondary text | `#C2CDB3` | Descriptions and notes on green |
| `--border` | `#C9CCB7` | Fine dividers on light surfaces |
| Dark-section border | `#F4E8CF40` | Fine dividers on green surfaces |
| `--accent` | `#E83A20` | Small accents and visible keyboard focus |
| `--accent-ink` | `#B22D19` | Small labels and accent links on light surfaces |

The closing section has **no red top border**. Workflow cards stay `--paper-light` during hover and focus; do not turn them yellow. Vermilion is a restrained detail, not a large section divider.

## Homepage order and background sequence

| Order | Section | Background |
| --- | --- | --- |
| 1 | Job scrapers and résumé matching / original hero | Green |
| 2 | Four tools. Clear starting points. | Light cream |
| 3 | For your coding agent | Paper |
| 4 | Built around your work / What are you building? | Green |
| 5 | Small trial. Clear cost. | Light cream |
| 6 | Before your first run / A few useful answers | Paper |
| 7 | Look inside the output | Light cream |
| 8 | Your first useful workflow / Start with one tool. | Paper |

The header stays light cream and the footer stays dark green. Preserve the alternating light sections and the green break around workflows. Do not reintroduce the three-collectors/one-scorer proof strip.

## Typography and spacing

Use the existing system fonts. No external font dependency is needed.

| Element | Treatment |
| --- | --- |
| Body | Helvetica Neue, Helvetica, Arial, sans-serif; 16 px base |
| Main hero heading | Strong sans-serif, tight tracking; Georgia italic for “career tools.” |
| Hero scale | `clamp(48px, 5.15vw, 74px)` on desktop; existing tablet/mobile rules apply |
| Section headings | `clamp(32px, 4vw, 49px)`, approximately 1.06 line height |
| Labels, numbers and code | SFMono-Regular, Consolas, Liberation Mono, monospace |
| Section labels | Small uppercase text with modest tracking |
| Supporting prose | Comfortable 1.65–1.75 line height; bounded line length |

Keep the homepage content width at 1,184 px, with the existing responsive outer gutters. Standard sections use 94 px vertical padding on desktop and 64 px on small screens. Hero and closing sections retain their own spacing. Keep thin borders, nearly square controls and generous space between groups; avoid gradients, glass effects and decorative blobs.

## Component rules

### Hero and output explorers

Keep the original headline: “Build job alerts, trackers, and career tools.” Explain the use case first, then what an Actor and Apify are. Retain the original facts: source links, a five-result start, and use in an app or automation.

The secondary action is **Explore the data**, linking to the lower output section. Both explorers offer an Actor selector, card/table/JSON views, JSON copying and downloads. Collector samples also offer CSV. Controls must remain clearly labelled and usable by keyboard.

Keep the recorded EURAXESS sample intact, including its collection date and source link. Label fictional examples clearly. The scorer demonstration is not the canonical fit schema. Full JSON preserves nesting; collector CSV uses `nomad-agent-flat-job-v1` and explains its information loss.

### Product cards

Use the original product-card system: two columns on desktop, one on mobile, existing Actor logos, concise purpose, returned fields, price and clear starting actions. Keep verified product limits and optional charges visible near the relevant choice.

### Workflow cards

The green workflow section contains four **separate cream cards**, not a continuous green table. Use a 22 px gutter between cards on desktop and 18 px on mobile. Cards use `--paper-light`, green text, a thin border, a small numbered marker, the existing Actor logo, an audience label, a heading and a short description.

Use two columns above the small-screen breakpoint and one below it. Desktop card padding is 28 px vertically and 30 px horizontally; mobile padding is 24 px vertically and 22 px horizontally. Separate the final link area with a fine internal rule.

The tool-logo row is a distinct darker green group beneath the cards, with light logos and readable secondary text. Use the existing API, n8n, Make, MCP, Airtable, Python and Zapier assets. Do not regenerate or casually substitute brand marks.

### Selected hover behavior

All four workflow cards use the **gentle lift** selected from the first animation example: move up 6 px over 260 ms, using `cubic-bezier(.2,.7,.2,1)`. Keep the cream fill, darken the border and underline the final link. The arrow stays still.

```css
@media (prefers-reduced-motion: no-preference) and (hover: hover) and (pointer: fine) {
  .original-plus-home #use-cases .outcome-card {
    transition: translate 260ms var(--ease-out);
  }
  .original-plus-home #use-cases .outcome-card:is(:hover, :focus-visible) {
    translate: 0 -6px;
  }
}
```

Use the individual `translate` property so the hover effect can coexist with the original entrance animation. Respect reduced-motion settings and keep static focus feedback available. The tilt, expanding shadow and moving-arrow alternatives were comparison experiments and are not the selected style.

### FAQ and closing section

Keep the original FAQ layout, native disclosure controls and useful answers. The final section is full width, paper colored and free of the red divider. Its copy is:

> Your first useful workflow
>
> Start with one tool.
>
> Try a few results and see how the data fits what you're building.

## Content and naming

Use short, human-readable, outcome-led copy. Explain platform terms when they first appear. Keep evidence, limits and implementation detail close to the relevant decision or deeper in the documentation. Avoid unsupported accuracy claims, testimonials and promises of automatic delivery.

| Identity | Current value | Handling |
| --- | --- | --- |
| Public brand | Job Atlas | Use in customer-facing prose |
| Website | `https://jobatlas.dev/` | Canonical public origin |
| GitHub repository | `https://github.com/Exdenta/jobatlas` | Use for source links, documentation and install commands |
| Apify publisher | `job-atlas` | Keep the hyphen; verified public listings use this owner |
| Technical contracts | `nomad-agent-job-v1`, `nomad-agent-flat-job-v1`, `nomad-ai-job-fit-v1` | Preserve stable identifiers |
| Historical sample provenance | Original recorded values | Preserve rather than rewriting evidence |

GitHub's public API confirmed the repository rename on 9 September 2026: both repository routes resolve to repository ID `1328909865`. The four promoted public Apify tools were separately checked under `job-atlas`; the equivalent `jobatlas` routes returned 404. Repository naming and publisher naming are different identifiers.

Keep prices and sample observations dated. Refresh dates only when the relevant fact has actually been rechecked. A link cleanup is not a new Actor run, pricing audit or production release. Preserve `null` versus empty-array semantics, original source identity and the `latest` release selector.

## Implementation and upkeep

- Base styles: [website/styles.css](../website/styles.css) and [website/first-visit.css](../website/first-visit.css).
- Approved homepage refinements: [website/homepage.css](../website/homepage.css).
- Homepage content: [website/index.html](../website/index.html).
- Interactive explorers and calculator: [website/homepage.js](../website/homepage.js).
- Sample payload and downloads: `website/homepage-samples.js` and `website/samples/explorer/`.

Edit the production files in `website/` and preview that directory before release. Keep the approved stylesheet when refreshing content. Check the section order, preserved hero/FAQ, current repository links, downloads, keyboard behavior and mobile overflow. A content refresh may update names and links on the original secondary pages; their layouts remain unchanged.

Run the repository's public-text cleaner on new or edited public prose. Keep build evidence separate from customer copy. Record any future user-approved change in this guide; production deployment remains a separate action.
