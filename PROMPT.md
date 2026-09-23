# One-shot prompt for a personal identity website

Paste everything below the line into a fresh chat. Attach your photo if the model
accepts images, and paste your facts file where marked.

---

Build a personal identity website for one person. One shot — do not ask me
questions first. If something is genuinely ambiguous, make a reasonable choice
and list it at the end under "Judgement calls".

## Input

FACTS FILE — this is the *only* source of information about me:

<facts>
[PASTE THE FULL CONTENTS OF YOUR FACTS FILE HERE]
</facts>

PHOTO: a portrait photo named `photo.jpg`, sitting in the same folder as
`index.html`. Reference it as `photo.jpg`. (I have attached it so you can see it
— use its actual colours and mood to inform the palette.)

## Deliverable

A single self-contained `index.html` — all CSS in one `<style>` block, any JS in
one `<script>` block, no build step, no frameworks, no external files except
Google Fonts and `photo.jpg`. Output the complete file, nothing omitted.

## Rule 1 — Content fidelity. This matters more than anything else.

Every factual claim on the page must be traceable to a sentence in the facts
file. Specifically:

- **Do not invent dates.** If the file says "several years" with no start or end
  date, write "several years" or leave the date blank. Never compute, estimate,
  or infer a year, a duration, or an age — not from an email address, not from a
  graduation date, not from anything.
- **Do not add general knowledge.** If the file says someone worked as a
  navigation officer, do not describe what navigation officers do. If it names a
  degree, do not list what that degree covers. If it names a city, do not add its
  coordinates, population, or history.
- **Do not invent preferences, motivations or opinions.** Not what I want from an
  employer, not what I value in a team, not what I think my past taught me —
  unless the file says so.
- **Do not merge two facts into a claim neither one makes.**
- Prefer my own sentences from the file, lightly tidied for grammar, over your
  paraphrase. Where the file already reads well, quote it.

## Rule 2 — Voice. Plain and humble.

This is the failure mode I care most about after Rule 1. Write like a competent
person describing themselves without selling. Short declarative sentences.

Banned, with real examples of what I mean:

- Aphorisms and closing zingers — "a procedure is the thing that holds when
  attention doesn't", "the method was sound, the object of it wasn't".
- The "not X, but Y" and "X isn't a Y, it's a Z" constructions.
- Dramatised summaries of ordinary work — "the discipline of being responsible
  for a position estimate you cannot verify until much later".
- Grand section subtitles — "the route actually taken, not the one plotted",
  "open them, don't take my word for it", "because it is the same discipline".
- Marketing verbs: crafted, forged, leveraged, passionate, journey, mission,
  relentless, obsessed, transforming, empowering, cutting-edge.
- Em-dash-heavy rhetorical build-ups and rule-of-three lists added for rhythm.

Section headings are plain nouns: About, Work history, Projects, Skills,
Education, Contact. No clever titles. No numbered section markers (01 / 02 / 03)
unless the content is genuinely a sequence.

## Rule 3 — This is an identity site, not a LinkedIn profile

It should read like a person's own page, not a CV export. Include the personal
material from the facts file — habits, interests, what they like, where they're
from — as a real section with equal weight, not a throwaway line at the bottom.
Still plain-worded; don't turn it into a personality essay.

## Rule 4 — Structure

- Hero with name, one plain line on what I do, and the photo.
- A section for each block in the facts file, in an order that makes sense.
- **Navigation:** a sticky top bar linking to each section, with the current
  section highlighted as you scroll. It must work on a phone — a horizontally
  scrollable row is fine; do not build a hamburger menu.
- Contact section with every link from the facts file, each opening correctly
  (`mailto:` for email, `target="_blank" rel="noopener"` for external links).
- No footer credits, no "built with" line, no font credits, no fake copyright.
- The photo appears once. Do not repeat it in the footer.

## Rule 5 — Design

Make a deliberate, specific visual choice — a real palette of 4–6 colours, two
or three typefaces used with intent, a clear type scale, considered spacing.
Take the palette from the photo if that works.

Avoid the current generic-AI-website look: cream `#F4F1EA` with a serif display
and terracotta accent; near-black with one acid-green accent; purple-to-blue
gradient hero; Inter or Space Grotesk by default; emoji as section markers;
everything centred; identical rounded cards with a coloured left bar; giant
full-viewport hero. Not everything needs to be a card — hairline rules between
rows often read better.

## Rule 6 — Technical

- **Mobile first-class.** Test your layout mentally at 390px wide: no horizontal
  scrolling on the page body, at least 16px side gutters, nothing overflowing —
  watch long names and long email addresses in large display type especially.
  Multi-column rows stack to one column.
- Light and dark: define all colours as CSS custom properties on `:root` for
  light, then override only those properties inside
  `@media (prefers-color-scheme: dark)`. Set an explicit `background` on `body`.
  Never define a colour only inside the dark block.
- Everything readable is visible on load — no scroll-triggered fade-ins parked at
  `opacity: 0`.
- Respect `prefers-reduced-motion`. Visible keyboard focus states. Real `alt`
  text on the photo.
- Google Fonts via `<link>`, with a real fallback stack in every `font-family`.

## Before you output — run this check

1. Go through your finished page line by line. For every sentence, point to the
   line in the facts file it came from. Anything you cannot trace: delete it.
2. Re-read for Rule 2 tells. Any sentence that sounds like it's building to a
   point — cut it down to the plain statement.
3. Confirm no date appears that isn't in the facts file.

Then output the full `index.html`, followed by two short lists:

- **Not from the file** — anything you wrote that isn't literally in the facts
  file, so I can review it. Write "none" if there is none.
- **Judgement calls** — grouping labels you invented, ordering decisions, and any
  ambiguity you resolved yourself.

---

## Notes for you (not part of the prompt)

- **Comparing models:** Rule 5 is deliberately open so each model picks its own
  direction and you get real variety. If you'd rather compare *execution* on a
  fixed brief, replace Rule 5 with a specific palette and font pairing and every
  model will build roughly the same page.
- **The photo:** most chat UIs let you attach an image the model can actually
  look at, which improves the palette a lot. Resize it first — a 26 MB camera
  file is slow to upload and unusable on a web page. Roughly 1000px on the long
  edge is plenty:
  `ffmpeg -i DSC05785.jpg -vf "scale=1000:-1" -q:v 3 photo.jpg`
- **The "Not from the file" list is the point.** It is the thing that turns three
  rounds of correction into one. Read it before you read the page.
- **If a model asks questions instead of building,** reply "make the calls
  yourself and list them at the end" rather than answering — you'll find out more
  about how it behaves unsupervised.
