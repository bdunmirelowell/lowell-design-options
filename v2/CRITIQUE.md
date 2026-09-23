# Golden Hour (option2.html): critique before v2

Reviewed 23 Sep 2026 against the live page at 1440px and 390px (headless Chrome and the in-app browser). Screenshots are in the session report.

## Overall

The direction holds up: warm paper, oxblood red, El Hidrant headlines, sunlit photography, the arch motif. Execution is what holds it back. Several images break the site's own rules, the eyebrow labels can't be read, three sections repeat each other, and the phone layout has no navigation.

## Rule breaches (fix before anything else)

| Asset | Where it shows | Problem |
|---|---|---|
| `preroll-single.png` | "What sets us apart" diagram | Tube label carries a strain name |
| `pack-open.jpg` | Farm-to-pack section | Label carries a blend name. The flap card is the printed **"Our Story"** 1909 Bull Lowell narrative, legible at full size |
| `ritual.jpg` | Pack parallax band + "Smoke Accessories" card | Label carries a strain name. On the shop card it sells the stone ashtray, which is not a Lowell product (the real one is the zinc Signature Metal Ashtray) |
| `jars.jpg` | Journal card "Why We Blend" | Jar labels carry three strain names |
| `roof-laugh.jpg` (hero, og.jpg), `beanies.jpg`, `chey.jpg`, `beach-drift.jpg`, `greenhouse.jpg` | Hero, community band, film strip, Journal | Unconfirmed-rights shoots (see v2 README for the full list) |
| "Bull Roundel Tee $30" | Farm Store grid | Not in the store catalog (lowell-farms.myshopify.com lists 21 merch items; this is not one of them) |
| Footer "@lowellfarms" | Follow column | Reads as the Lowell Farms Inc. name, a separate company |

## Usability

| Finding | Severity | Recommendation |
|---|---|---|
| Below 760px the nav links are hidden and nothing replaces them. On a phone the only way to reach Find Lowell is to scroll 10 screens | 🔴 | Menu button with a full-height sheet; Find Lowell as a persistent button |
| The ZIP box does nothing (`onsubmit="return false"`); both hero CTAs are `<button>`s with no destination | 🔴 | Real links: ZIP → locator with the ZIP prefilled; CTAs → Shop and Find Lowell pages |
| Farm-to-pack video: 26.7 MB, no poster, so it renders as an empty 300×530 box with a play bar. Chrome makes three range requests for it on page load | 🔴 | Poster frame, `preload="none"`, and a re-encode of the 540×960 file (it runs at 4.7 Mbit/s; target under 5 MB) |
| Locator lives in two separate places: the state map (section 4) and the ZIP band (section 9) | 🟡 | One "Find Lowell" band: map, ZIP box and state links together |
| The two pack sections run back to back and say the same thing ("Lighting up is a ritual…" then "Open the box…") | 🟡 | Merge into one pack section: annotated photo, four features, the film |
| Age gate has no focus management; keyboard focus starts behind the modal | 🟡 | Focus the first button on open, trap Tab inside, return focus on close |
| Film strip auto-scrolls for as long as the page is open, with no pause control (WCAG 2.2.2) | 🟢 | Static, swipeable strip |

## Visual hierarchy

- **What draws the eye first:** the hero headline at 104px, correct. But it is four lines of 104px italic over a face, followed by a 43-word paragraph. Four elements compete in the lower left.
- **Eyebrows are illegible.** "GREAT AMERICAN CANNABIS" is #EAD9AE on a pale sky: **1.07:1**. Gold eyebrows on paper (#C89B4B on #F6EFDF) are **2.22:1**. Both fail WCAG AA (4.5:1).
- **Reading flow:** hero → purpose → diagram works. After that the page alternates between full-bleed photo bands and paper sections with no rhythm: three full-bleed bands (ritual, community, hero), then the commerce grid sits seventh.
- **Emphasis:** the purpose line gets the most whitespace on the page and earns it. The values pills and the press logos (plain text set as logos) are orphaned.

## Consistency

| Element | Issue | Recommendation |
|---|---|---|
| Type scale | 18 fixed font sizes (10, 10.5, 11, 12, 12.5, 13, 14, 14.5, 15, 16, 17, 17.5, 18, 19, 21, 30, 34, 40px) plus seven clamp() sizes. Caps labels range 10–12.5px at 0.14–0.34em tracking | Seven-step scale; caps labels 12–13px at 0.14–0.18em |
| Spacing | Section padding 84/90/96/110px, gaps 22/24/26/30/40/44/54/60px | 8-pt spacing tokens; one section rhythm |
| Cards | Farm Store product stills sit on white inside cream cards; one card is a burlap lifestyle shot | Transparent product cutouts on one card colour; lifestyle images kept out of the product grid |
| Buttons | Primary style changes by section (cream on hero, ink on gate, outline on ritual) and hover states differ | Two button styles (solid, outline) × two surfaces (light, dark) |
| Body type | Paragraphs set in El Hidrant, a display serif, down to 14.5px italic | Keep El Hidrant for display and ledes; short body copy at ≥17px, 60–65ch measure |
| Map | Alaska/Hawaii inset separator paths render as filled beige wedges under the map | Unfilled strokes, or hide them (AK/HI are hidden anyway) |

## Accessibility

- **Colour contrast:** body ink 12:1 passes. `--ink-soft` passes on paper (4.58) and fails on the sand band (4.18). Footer legal text 3.38:1 fails. Hero and gold eyebrows fail (above).
- **Touch targets:** state chips 32px tall, footer links 24px. Target 44px.
- **Focus:** only `.btn` has a focus style. Nav links, cards, chips and the ZIP input have none visible.
- **Alt text:** mostly present. The pre-roll diagram's red markers are bare digits with no programmatic link to their labels. The video has no audio track, so it needs a text description rather than captions.
- **Motion:** the hero parallax, reveals and film strip respect `prefers-reduced-motion`; the ritual band's parallax does not. The film strip has no pause control for everyone else.

## Load weight

- First view transfers **2.1 MB** of images and fonts before any scrolling (measured in Chrome via DevTools protocol). The largest items are the 483 KB pre-roll PNG and the 441 KB ritual photo, and neither is visible at first paint.
- The 26.7 MB video has no poster and is requested on load (three HTTP 206 range requests observed). Its actual transfer size wasn't measurable in headless Chrome.
- JPEG only; no WebP/AVIF and no `srcset`, so phones download 1400–1700px images for a 390px screen.

## What works

- The palette and the arch motif (age gate, pack photo). They are distinctive and they fit the brand bible's "Crafted Natural".
- The purpose line as a standalone moment.
- The annotated diagrams (pre-roll, pack). They explain the product without a paragraph.
- The real US map with the eight states filled.

## Priority for v2

1. **Clear the rule breaches.** Swap or retouch every image with a strain or blend name, the Bull story card and the non-Lowell ashtray, and replace unconfirmed-rights photos wherever a Drive replacement holds up.
2. **Make it work on a phone.** Menu sheet, real links, a ZIP box that goes somewhere, 2-up product grid.
3. **One type and spacing system.** Seven type sizes, 8-pt spacing, legible eyebrows, visible focus rings.
4. **Pacing.** Merge the two pack sections and the two locator sections, and move the Farm Store up.
5. **Weight.** Poster and lazy-load the film, serve WebP with `srcset`, eager-load only the hero.
