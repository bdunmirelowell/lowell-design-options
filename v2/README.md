# Golden Hour v2: lowellherbco.com (no store)

**Preview:** https://bdunmirelowell.github.io/lowell-design-options/v2/
**Production (after the DNS cutover):** https://www.lowellherbco.com/, on Netlify (team "Lowell Herb Co"), publishing this `v2/` folder as the site root (`../netlify.toml`).

The static site that replaces the compromised WordPress site on lowellherbco.com, without the store. Until the cutover every page carries `noindex,nofollow` and a preview ribbon; one line in `_src/build.py` (`LIVE = False` → `True`) turns both off and adds canonical URLs on www.lowellherbco.com. Pages:

| Page | File | What it is |
|---|---|---|
| Home | `index.html` | Golden Hour, sharpened; the Farm Store section is now a merch photo band (no prices, links or cart) |
| Notes from the Farm | `notes-<slug>.html` (3) | One article page per blog card |
| Find Lowell | `find.html` | Store locator on live data |
| Contact | `contact.html` | Email link only (no form), per Bryan |
| Policies | `privacy.html`, `terms.html`, `disclaimer.html` | The live WordPress pages' text, verbatim (WordPress ids 3, 362, 924, last modified 3 Jan 2025) |
| Not found / Gone | `404.html`, `410.html` | Netlify serves 404.html for unknown URLs; `_redirects` serves 410.html for the old WordPress URLs that are gone for good |

`robots.txt` and `sitemap.xml` are generated with the pages. `_redirects` maps every old WordPress URL (301 or 410). The critique of the July page is in [`CRITIQUE.md`](CRITIQUE.md).

## Go-live without the store (1 Oct 2026, branch `golive-no-store-2026-09-30`)

Bryan's decisions of 30 Sep: the home page is locked except for removing store references; the merch photos stay as plain imagery; the policies are the current WordPress text, verbatim; hosting is Netlify.

- **Store removed:** `shop.html`, `product.html` and `shipping-returns.html` are gone, and so are the cart icon, the "Farm Store" nav link, the hero's "Shop the Farm Store" button, "Shop all 21", the footer's Shop column and its "Shipping & returns" link, and "Nothing sold in the Farm Store contains cannabis." Restore from git at `7d32447` when e-commerce returns.
- **Home, Farm Store section → merch photo band:** the same ten photos in the same bento (two lifestyle photos, eight merch cutouts). No links, prices, name plates or hover effects. The eyebrow "The Farm Store" became "Lowell goods"; the heading "Timeless goods. No gimmicks." stays; the lede about shipping direct and the "Shop all 21" link are gone. Each merch photo keeps its product name as alt text.
- **Footer:** the email sign-up is gone (it never stored anything; its note said sign-ups open with the new store). In its place, the home page's own Notes line and a "Read the notes" link. Columns are Lowell, Help (Contact, @lowellfarms) and Legal (Privacy, Terms, Disclaimer). The bracketed licensee-number placeholder is removed; the WordPress footer carries no licence line either.
- **Contact:** "Farm Store orders, returns, press, or anything else." became "Questions, press, or anything else."
- **Policies:** `_src/policies/source-wp-2026-09-30/page-<id>.json` are the raw `/wp-json/wp/v2/pages/<id>` responses (fetched 1 Oct 2026 01:34 UTC). `build.py` renders their `content.rendered` with the site's styles: classes dropped, the top heading level becomes h2 and the next h3, `<hr>` dropped, every word kept. A normalised word diff against WordPress shows 0 words changed. The drafts with 15 `{{To confirm}}` markers and the "Draft: needs legal review" banners are gone.
- **Self-contained folder:** the brand fonts are copied into `assets/fonts/` at build time (they live at the repo root for the v1 pages), so `v2/` works as a site root. CSS and JS are `.v16`.
- **Images:** the 31 store-only image files (shop header, two category photos, 13 unused product cutouts) are removed from `img/`; every remaining image is used by a page.
- Checks and screenshots: `~/work-prompts/2026-09-30/reports/03-website-build-report.md`.

## Store finder on phones (28 Sep)

- **The page scrolls past the map.**
  - On touch screens, one finger now scrolls the page and two fingers move or zoom the map.
  - A one-finger drag over the map shows "Use two fingers to move the map." for about 1.5 s.
  - With a mouse or pen, the map works as before: drag to pan, and the wheel zooms after a click.
  - About 30 lines in `_src/find.js` (`touchGestures()`), not a library. leaflet-gesture-handling 1.2.2 (its latest) is on jsdelivr only, not cdnjs. It would also change desktop, where zooming would need ctrl + scroll.
  - Phone map height: 52% of the screen, and never more than 62% of the visible screen (`62svh`, which counts the browser's toolbars). It was at least 320px, which filled a phone held sideways. At 375×812 the map is 422px; at 812×375 it's 232px.
  - A phone on its side (landscape, under 500px tall, touch) hides the map legend. The key under the list explains the pins.
- **Your location:**
  - A "Use my location" button sits under the ZIP/city search on every screen size.
  - Phones also ask as the page opens, unless the link names a ZIP, city or state (`?zip=`, `?q=`, `?st=`). On a first visit they ask right after "Yes, I'm 21+", so the prompt doesn't cover the age gate.
  - When location is granted, the list shows the stores within 50 miles of your location, nearest first, with the ring and dot a ZIP search shows.
  - If location is refused, unavailable or takes over 10 s, the page stays as it is and says nothing. Only a tapped button shows a line: "We couldn't get your location. Search a ZIP code or city instead."
  - The position never goes into the URL or share link, is never stored, and isn't sent anywhere by this page.
- **"Get directions" on every store card** (and in the map pin's popup), a quiet link beside the phone number.
  - Where it opens: Apple Maps (`maps.apple.com/?daddr=`) on iPhone, iPad and Mac, including Chrome on a Mac. Google Maps (`google.com/maps/dir/?api=1&destination=`) everywhere else.
  - The destination is the store's name and street address whenever the address has a street, including stores whose pin was placed by town (`approx`). A store with no street gets name + city + state. An approximate pin's coordinates are never used.
  - The visitor's position is never in the link: Maps works out the route itself.
  - It's a plain link, so long-press and copy work.
- **One label for store links:** "See Lowell at this store" in the solid style for both link kinds.
  - A brand page (`uk` "verified") and a Lowell product page listed in stock (`uk` "menu") are both checked in a browser to open to Lowell products.
  - "View their menu" and its faded style are gone.
- **Privacy draft:** under "Finding a store near you", the review's wording (28 Sep), still a draft for counsel: "If you allow it, the store finder uses your device's location to show the stores nearest you. We don't receive or save your location, and it never appears in the page's web address. To draw the map around you, your browser loads map images for that area from our map provider, which can tell roughly which area is on screen, as it can after a ZIP code search. You can say no and search by ZIP code or city instead." The open items on the map provider stay.
- CSS and JS are now `.v15`.

## Round 4, phase 2 fix (26 Sep, 09r review B-1 and B-2)

- **Empty-state button:**
  - With "Hide out of stock" on and no store left, "Show stores that are out of stock" now appears only when an out-of-stock store matches the state, line and type filters. Otherwise the page shows "No stores match those filters." alone.
  - Before, the button appeared in every empty scope. On the 25 Sep data it revealed nothing in all 231 of them (e.g. Missouri + Littles).
  - The radius branch ("Show any distance") is unchanged.
- **Privacy draft:**
  - "The store list is loaded from our own servers." wasn't true. The preview loads the list from brya8385.github.io (GitHub Pages), and Leaflet from cdnjs.cloudflare.com.
  - The sentence is now a `{{To confirm: …}}` open item that names both hosts. The three drafts now carry 16 open items (privacy 6, shipping 6, terms 4).
- CSS and JS are now `.v11`.

## Round 4, phase 2 (25 Sep, after Bryan said the home page is done)

- **Farm Store filters fixed.** The All / Apparel / Luggage / Accessories chips (and the category tiles) marked cards hidden, but the cards' `display: grid` overrode the browser's `[hidden]` rule. All 21 stayed on screen while the count said 9 or 6. A base `[hidden] { display: none !important }` rule fixes it everywhere. Each chip now shows exactly its count. There's no price sort: Bryan chose to fix the filters only.
- **Locator labels follow `doors.json`'s `st` field** (08r review, F1; Bryan's rule of 25 Sep):
  - `in_stock`: "In stock · N products" plus the shelf price
  - `out_of_stock`: "Currently out of stock"
  - `carries` (no live menu we can read): no badge, no price and no stock claim, with a plain grey "Lowell store" pin

  "Carries Lowell · shipped" and "Partner-reported" are gone, and so is the "without a live menu feed… Show them" bar. "In stock only" becomes "Hide out of stock", which hides only out-of-stock stores. Files without `st` are labelled the same way find-lowell's `app.v5.js` does it. `accept_09_v2_labels.py`: 4/4 PASS on the live site.
- **Contact page:** admin@lowellherbco.com as an email link, plus Find Lowell and @lowellfarms. There's no form, address or phone (Bryan's choice).
- **Policy drafts:** Privacy, Shipping & Returns, and Terms for a merch-only store.
  - Built from the old Shopify store's policies (lowell-farms.myshopify.com/policies/…), with all hemp and THCa content removed. The old store had no shipping policy.
  - Written in our own words, after a read of Old Pal's (oldpalprovisions.com) and Miss Grass's policies for what a brand like ours covers. No text was copied.
  - Open facts and decisions are highlighted on the page, from `{{To confirm: …}}` / `{{To decide: …}}` markers in `_src/policies/*.md`.
  - Merch shipping and returns stay in, because Bryan confirmed that merch ships direct.
- **Footer:** the Help column is back, with real pages: Contact, Shipping & returns, Privacy, Terms, @lowellfarms.
- **Site-wide link test:** 11 pages, 408 static links, 58 unique targets, all working. The locator's 472 store-menu links were swept separately; see Known gaps.
- CSS and JS are now `.v10`.

## Round 4 (25 Sep, Bryan's third review): home page first

Phase 1 is the home page only. Phase 2 (Farm Store sort, contact page, policy drafts, site-wide link test, locator labels) waits for Bryan's OK on the home page.

- **Hero:** back to round 2's full-bleed dusk bonfire photo (`hero-dusk-*`, from `Lowell x Revelry-15.jpg`), replacing round 3's rooftop shot. Git history holds only one bonfire hero (round 1's hero was the Eunbi pack photo, not a bonfire).
  - Desktop: the headline, paragraph and buttons sit on the **left**, over the empty sky and clear of every face; the fire is out of frame. (First built on the right per the round-4 prompt; Bryan corrected it to the left on 25 Sep and approved it in the build session.) Checked at 1280×720, 1440×900 and 1920×1080: the buttons end 95–215px above the nearest head.
  - Phone: the tall crop, with the text on the sky and the buttons over the grass. The text runs full width there, so it isn't "right" or "left".
  - The rooftop files are deleted, so no image from the two unconfirmed 2021 shoots is left on v2.
- **The Pack:** the single-Smoke section ("What sets us apart") is gone. The Pack now has six features, all pinned on the open-pack photo:
  - two from the Smoke section, tightened: Quality first and Always blended
  - the pack's four: magnetic flap, slide-out tray, emergency matches, wax liner

  The header is Bryan's pick of three options: "Pre-rolls made with intention. A box built to match."
- **Blog name:** "Notes from the Farm" everywhere: nav, home section, footer sign-up. It was Journal / Notes from Lowell / Letters from Lowell. This is Bryan's exception to the no-from-the-farm-copy rule, for the name only.
- **Articles:** each blog card links to its own page, built from a real Lowell post on lowellsupply.com/blogs/news (George Allen). The text is verbatim except for the edits listed in `_src/articles.json`.
  - Farming Cannabis (13 Oct 2025)
  - Salad Science (4 Aug 2025)
  - Freshness You Can Trust (22 Jul 2025)

  Card titles are the posts' real titles, and each teaser is a sentence from the post. The pages reuse the cards' photos; the posts' own featured images weren't used (farm-imagery rule).
- **Press:** Forbes, Robb Report, Page Six and Newsweek each link, in a new tab, to their article about Lowell. The quote is verbatim from the Forbes piece, with the cut marked by an ellipsis. Sources and dates are listed under Known gaps → Press.
- **Instagram:** the five bottom photos and an "@lowellfarms" pill link to instagram.com/lowellfarms in a new tab. The word "Instagram" is replaced by the Instagram logo (inline SVG, `aria-label="Instagram"`).
  - The band's dusk tile was the same frame as the hero, so it's replaced by `Bonfire + Lowell.jpg` from the same party.
- **Footer:** the four dead `#top` help links are removed until Phase 2 builds real pages: Contact, Shipping & returns, Privacy, Terms.
- On phones the band is 2×2, so the per-photo Instagram glyphs are hidden and the pill carries the cue.
- Bryan's edits after the first look (25 Sep):
  - The Pack moves above the Farm Store.
  - Larger hero type: headline about 74px at 1440 wide (was 61), paragraph 22px (was 19).
  - The hero line "Every detail, from the flower to the pack, is considered." becomes "From the flower to the pack, nothing is an afterthought." It was Bryan's pick of three.
- CSS and JS are now `site.v7.css`, `site.v7.js` and `find.v7.js`. axe-core (WCAG 2.1 AA + best practice) reports 0 violations on Home and on an article page.

## Round 3 (23 Sep, Bryan's second review)

- **Hero photo:** back to the July page's rooftop shot (two friends laughing in golden light), per Bryan. The layout is still round 2's. On desktop the text sits on the right over a warm gradient; on phones the photo sits above a dark text panel so the headline stays off her face.
- **"What sets us apart":** the 1g tube Single (a CA product) is replaced by a single **Lowell Smoke**. It's cut from the 2025 Originals tray render (see the rights table). The four points now describe the Smoke:
  - Quality first
  - Always blended
  - Engineered draw
  - Even burn

  "Ready and able" (tube and matches) is gone. The copy for points 3 and 4 is new and needs checking (see Known gaps).
- **Purpose band:** just the quote. The "Why we exist" label and the four brand-pillar names are gone.
- **No growing:**
  - The farm film is removed.
  - The greenhouse and tractor photos are removed.
  - The "Farming cannabis" Journal card is now "Where our flower comes from": we don't grow our own; we buy from the best farms.
  - "Letters from the farm" is now "Notes from Lowell" in the Journal and "Letters from Lowell" in the footer.
  - The hero line now reads "from the flower to the pack".
- **The Pack:** two columns (photo and features) now that the video is gone.
- CSS and JS are at `site.v3.css` and `find.v3.js`. Find Lowell is unchanged.

## Round 2 (23 Sep, after Bryan's review: "too much white space, need more/better images; locator looks nice")

- **Less white space.** Section padding went from 72–128px to 48–88px, and heading-to-content gaps from 64px to 32px. The purpose line, press quote and footer are compact bands. The home page is about 12% shorter (8,050px vs 9,120px at 1440px wide) while carrying 25 photos instead of 18.
- **Full-bleed photo hero**, as in the July page the CEO picked: a dusk bonfire at a 2025 Lowell farm party, with the headline over the sky.
- **Farm Store bento:** eight products plus two lifestyle tiles (the Wax Canvas Duffel in use; the Lowell Denim Jacket at the farm party).
- **"Bring people together" mosaic:** four photos and the mission line on a dark band.
- **The Pack:** photo, features and film side by side instead of stacked.
- **Edge-to-edge photo band** above the footer: farm, people, product.
- **Farm Store page:** a photo header and photo category tiles, replacing cream cards with cutouts.
- **Find Lowell:** unchanged.
- **@lowellfarms** is linked in the footer. Bryan confirmed it's the brand's Instagram handle.

## What changed and why

**Rules the old page broke**
- Four images showed strain or blend names (the tube label, the open pack, the "ritual" pack, the jars). Each is now retouched to a blank label or swapped for another image.
- The farm film had a 3.6-second pack close-up with a blend name on it; round 1 cut it (45 s to 41 s) and round 3 removed the film.
- The open-pack photo had the printed 1909 Bull Lowell "Our Story" card on the flap. It's replaced by a Hero Pack Shots photo with no card.
- The age gate's "Est. 1909" line is removed.
- The "Smoke Accessories" card sold the stone ashtray from the Eunbi shoot, which isn't a Lowell product. The Farm Store now shows the real Signature Metal Ashtray, and the stone ashtray is never captioned as a Lowell product.
- "Bull Roundel Tee" (not in the catalog) is gone. Every product name and price now matches the live Farm Store catalog (lowell-farms.myshopify.com, pulled 23 Sep 2026).
- **All photos from the two unconfirmed shoots are out.** See the rights table below.

**Sharper, same direction**
- Type is on one seven-step scale; the old page had 18 fixed sizes plus 7 clamps.
- Spacing is on one 8-pt scale, and every section uses the same rhythm.
- Colour tokens are unchanged except two text tones darkened to pass WCAG AA: eyebrows went from 2.2:1 to 5.0:1, and secondary text on sand from 4.2:1 to 5.3:1.
- Hero paragraph is cut from 43 to 20 words, and the CTAs are real links (round 2 restored the full-bleed photo hero; see above).
- Merged sections:
  - The two pack sections are one: annotated photo, four features, and the film.
  - The map band and the ZIP band are one "Find Lowell" band: ZIP box, state chips and map.
- The Farm Store moved from seventh section to fourth and uses the store's transparent product cutouts on a single card style.
- The auto-scrolling film strip is gone; round 2 replaced it with a static edge-to-edge photo band.

**Works on a phone**
- A menu button opens a full-screen sheet with the nav and a ZIP box.
- The Farm Store grid is 2-up on phones.
- Touch targets are at least 44px wherever they were under that.

**Accessibility**
- Age gate and menu trap focus, make the page behind them inert, and return focus when closed.
- Skip link, visible focus rings everywhere, and alt text on every image.
- axe-core (WCAG 2.1 AA + best practice) reports **0 violations** on Home, Find Lowell, Farm Store and Product, at 1440px and 390px.

**Load weight**
- Home first view: **0.65 MB, down from 2.1 MB**. Full scroll: **1.2 MB, down from 3.9 MB**, not counting the video (round 2, with 25 photos).
- The 26.7 MB farm film is gone (removed in round 3). The old page requested it on page load.
- WebP with `srcset`; only the hero image loads eagerly.
- CSS and JS filenames are versioned per deploy (`site.v3.css`, `find.v3.js` as of round 3), because GitHub Pages ignores `?v=`.

**Find Lowell**
- Uses the find-lowell app's behaviour as its spec:
  - "Where are you?" landing: ZIP/city search, or one of 8 state buttons
  - radius 25/50/100/Any
  - line and type (lean) filters
  - one pin per store on OSM tiles, with Leaflet 1.9.4 from cdnjs
  - "Store list updated <asof>"
- `doors.json` is fetched live from `brya8385.github.io/find-lowell` on every visit, with no embedded or cached copy. If the fetch fails, the page shows an error and a retry button, not stale data. Test it with `find.html?doors-test=fail`.
- Since round 4, phase 2, labels come from each store's `st` field. The three states look different in both the pins and the cards:
  - **In stock now** (solid green)
  - **Currently out of stock** (amber ring)
  - **Lowell store** (plain grey: no live menu we can read, so no stock claim)
- Only in-stock stores show a price. The page enforces this itself and doesn't rely on the data.
- **No blend names:** product rows are grouped by line × lean (e.g. "Quicks · Indica · 10 pre-rolls, 0.35g each"), and the blend-name field in the data is never read.
  - Leak test: I rendered all 8 states with every tier shown and searched the page text for the 287 distinct product names in the data.
  - 0 blend names appear. The only matches were store and place names, e.g. "State of Mind Dispensary" and "Chicago (Midway)".
- ZIP search resolves any US ZIP using Census 2023 ZCTA centroids. They're split by first digit, so a search loads about 90 KB. The old app only knew ZIPs that already had a store.
- Home's "Find Lowell near you" box goes to `find.html?zip=…`. The state chips on Home go to `find.html?st=…`.

## Photo rights

Brief rule: swap out the Erica Danger 2021 shoot and the 2021 Summer Lifestyle Shoot (UNKOMMON: beach, roof, greenhouse and the Brigitte set) wherever a replacement holds up.

**No image from those two shoots remains on v2** (round 4). The round-3 rooftop hero (`Lowell Farms Photoshoot/Selects/ROOF/20210709-1Q0A3170.jpg`, UNKOMMON) was the last one; it was replaced by the dusk bonfire photo and its files are deleted.

How this was checked:
- Each July image was traced to its Drive original by perceptual hash across 4,818 Drive images.
- Each v2 source file was searched by filename across all five flagged-shoot folders: 0 hits. In round 2, the prefix `LHC_35s_` matched 5 files there, but those are 2022 holiday frames filed inside a copy of the 2021 folder, not files v2 uses.
- The two Hero Pack Shots were hash-compared against the flagged shoot's own product frames (`Lowell Farms Photoshoot/Selects/GREENHOUSE/Product Additions`): no match. Distances were 111–134 of 256 bits; a copy scores under about 30.
- **Not done:** a full perceptual sweep of v2's sources against all 1,589 flagged-shoot images. Drive streaming made it take hours, so I stopped it. A renamed copy of a flagged frame would get past the filename search.

One near-miss: the "Merchandise Lifestyle Shots" folder holds `20210128-3U9A1693.jpg`, a couple in the green tee. It looks like merch photography, but it's a copy of a frame from the UNKOMMON beach shoot (`Lowell 2021 Summer Lifestyle Shoot/UNKOMMON/BEACH/Copy of 20210128-3U9A1693.jpg`). I used it in a draft, caught it, and replaced it. Anyone reusing images from that folder should check the same way.

Every image v2 uses (sources under `Shared drives/Graphic Design/Photography` unless stated):

| v2 file | Where it's used | Source | Rights status |
|---|---|---|---|
| `hero-dusk-*`, `og-v2.jpg` | Home hero, share card | `2025/2025 Events/New York/6-5-25 Lowell Bonfire Party/Thank You Carousel Assets/Lowell x Revelry-15.jpg` | Lowell's own event photography. **Verified 25 Sep:** its EXIF matches the `132A` frames (Canon EOS R6, body serial 122024000392), shot 5 Jun 2025 20:54. Guests are identifiable: **confirm likeness releases**. The right edge of the frame shows a John Deere loader. |
| `band-bonfire-*` | Photo band (links to Instagram) | Same folder, `Bonfire + Lowell.jpg` (two guests from behind watching the bonfire, the Lowell bull on a jacket) | Lowell's own event collateral: a Photoshop export made 9 Jun 2025 with the other carousel files. It has no EXIF, and a perceptual-hash search of the party's 114 `132A` raws and Daniel's iPhone photos found no match (best 97 of 256 bits). At 1080×1920 it's likely a still from one of Daniel's iPhone videos: **source frame not traced**. No faces shown. |
| `mo-sunset-*` | People mosaic | Same folder, `Lowell x Revelry-14.jpg` (a hand holding a pre-roll against the sun) | Same as above; no face shown. |
| `ls-denim-*` | Home merch band | Same party, `Photos/Kwesi's Raw Photos/132A0091.JPG` | Same as above: **confirm likeness releases**. |
| `mo-pass-*`, `mo-smoke-*`, `band-greens-*` | People mosaic, photo band | `35s/House Shoot/Finals/…` (files named `Lowell Farms3421_F.jpg`, `Lowell Farms3934_F.jpg`, `Lowell Farms2803 _F.jpg`) | 2022 commissioned 35's lifestyle shoot with professional models. The filenames say it was shot under Lowell Farms Inc.: **confirm the licence carried over to the brand**. In `mo-pass` the blend name on the pack spine is blurred. |
| `mo-pool-*`, `band-light-*` | People mosaic, photo band | `35s/2023 Lifestyle Sanitized/LHC_35s_…_Sanitized_010623.jpg` | Same shoot, "sanitized" versions: no blend name is legible. Same licence question. |
| `ls-luggage-*` | Home merch band | `2025/Merch/Luggae Photoshoot - Lifestyle and Product Photography/BackPackShootB10.jpg` | In-house 2025 merch shoot. Model release not in Drive: **confirm**. |
| `band-jacket-*` | Photo band | Same folder, the green-jacket frame | Same as above. |
| `journal-flower-*` | Journal | `Flower/` (a loose-bud product shot on white) | In-house flower photography. No text in the image. |
| `hero-pack-*` | Photo band | `Eunbi Ashtray, Hex Pipe Bundles/Ashtray, Pack/Export186576.jpg`. Strain name retouched off the label. | Eunbi accessory shoot, listed in the brief as a replacement source. The ashtray is stone, not a Lowell product, and isn't captioned as one. |
| `pack-tray-*` | The Pack | `Hero Pack Shots/ne1jQrmg.jpeg` | Not a flagged shoot. Photographer not recorded in Drive: **confirm**. |
| `journal-box-*` | Journal | `Hero Pack Shots/2S7HO84w.jpeg`, blend name retouched off the label | Same as above: **confirm** |
| `journal-blend-*` | Journal | `FarmVisit_121421` (iPhone, pre-roll packing) | Dec 2021 visit. Listed in the brief as a replacement source. |
| `p/*.webp` (8 products) | Home merch band | Product cutouts from the live Shopify catalog CDN | Lowell's own product photography |

Images that "confirm" doesn't cover: none. The v1 pages (option1–4) still use the unconfirmed shoots and are unchanged.

## Known gaps

**Store data (session 08 owns the data feed)**
- `doors.json` is rebuilt daily by session 08. On 25 Sep it was dated 2026-09-25: 598 stores, all with `st` (428 in stock, 77 out of stock, 93 carries). Stores whose coordinates fall outside their state are listed but not pinned ("Map location unavailable").
- **Store-menu links** (from the data feed, 25 Sep sweep of the 472 unique URLs):
  - 190 answer 200.
  - 278 answer 403 to scripts. All are Dutchie, iHeartJane or Verilife; spot checks of one of each load normally in a browser.
  - Four fail. They belong in session 08's feed:
    - `organicblooms.dispensary.shop/…afternoon-delight-10pk-lowell…`: 404
    - `www.carngiehillcannabis.com`: no response; the domain is misspelled
    - `emeraldfields.com/shop/`: no response
    - `shop.root22dispensary.com/menu?brand=Lowell%20Herb%20Co`: 307
- City search only knows cities that have a Lowell store. ZIP search covers every US ZIP except PO-box-only ZIPs, which have no Census centroid.

**Locator setup**
- The map uses the public OpenStreetMap tile server. That's fine for a preview, but OSM's usage policy rules it out for production traffic, so the live site needs a tile provider.

**Copy to confirm (round 4)**
- Tightened pack features:
  - Quality first: "Flower from the best farms. Only the best gets in." (was "Craft flower sourced from the best farms. Only the best gets in.")
  - Always blended: "A purposeful blend in every smoke: terpene diversity, flavor, balance." (was "A purposeful blend inside: …")
- Two new labels: the blog section's eyebrow "The blog" and the article pages' "Keep reading." / "All notes".
- Article edits, all listed in `_src/articles.json`:
  - **Freshness You Can Trust:** four cuts remove the growing claims ("grow and", "harvest, trim, and") and the online-store / ship-to-your-door wording. The last paragraph (a link to the retired THC vs THCa post) is dropped. **Confirm every retail Lowell pack carries a packaging date**, because the title and body claim it. The source post was written about packs shipped from the online store.
  - **Salad Science:** two capitalisation typos fixed. The post makes effect claims ("therapeutic", "mood-enhancing", receptor "blockage"): check them against each state's marketing rules.
  - **Farming Cannabis:** verbatim. It names Hudson Cannabis as a grower: confirm it's still a supplier.
- The hero headline still reads "Grown with intention." It's the existing brand line, but it may read as growing.

**Press (verified 25 Sep; each article opened and read)**
- Forbes: Javier Hasse, "America's $3.1 Billion Cannabis Pre-Roll Habit…", 26 Jun 2025. Lowell is No. 9, with its own section; the quote is from it. Opened in the built-in browser.
- Robb Report: Nick Williams, "How Lowell Herb Co. Became America's First Great Weed Brand", 11 Feb 2019. The built-in browser refused robbreport.com, so I read the Wayback copy (23 Jul 2025 capture). The live URL returns 200.
- Page Six: Ian Mohr, "Bella Thorne marijuana ad rejected ahead of Oscars", 24 Feb 2019, about Lowell's Oscars ad. The built-in browser blocks pagesix.com, so I read the Wayback copy (23 Oct 2019 capture). The live URL returns 200.
- Newsweek: Mary Kaye Schilling, "Pot Offenders Wanted: California's Lowell Herb Co. Seeks to Hire Parolees", 15 Jun 2018. Opened in the built-in browser.
- The Robb Report piece retells the Bull Lowell story and names Coachella-era strains. It's an outside article, not site copy, but it is one click away.

**Imagery and state rules**
- Several photos show people smoking: the mosaic, the photo band, and the July page's hero did too. Check each launch state's cannabis marketing rules on depicting consumption before the real site goes live.

**Placeholders and unverified copy**
- The store (product pages, cart, checkout) and the email sign-up are removed until payment processing is sorted (1 Oct).
- Copy carried over from v1 and not re-verified:
  - "700+ licensed shops": the live data maps 658 stores plus 47 unplaced CA stores, which is 705
- The footer has no state licence or marketing disclosure line (the placeholder was removed on 1 Oct; WordPress had none). Check each state's rules.
- The age gate stores a yes in the browser (`localStorage`). That's a courtesy gate, not a compliance-grade age check.

**Not built**
- Dark mode is off by design; Golden Hour is a light palette.

## How to edit

The pages are generated, so don't hand-edit the `.html` files. Edit `_src/` and rebuild:

```
python3 v2/_src/build.py
```

- `_src/build.py` holds the page markup.
- `_src/site.css` holds the tokens and styles.
- `_src/site.js` holds the gate, menu and ZIP forms.
- `_src/find.js` holds the locator.
- `_src/products.json` is the catalog snapshot (the home merch band shows eight of its photos).
- `_src/articles.json` holds the Notes from the Farm articles: source URL, byline, date, body, and every edit made to the source text.
- `_src/policies/source-wp-2026-09-30/` holds the WordPress policy pages (raw REST JSON). To change a policy, change the text there (or replace the file with a new export) and rebuild; `DISCLAIMER = False` in `build.py` drops the Disclaimer page and its footer link.
- `_redirects` (published root) maps the old WordPress URLs; `../netlify.toml` sets the publish folder and headers.

**Go-live switch:** `LIVE = True` in `build.py`, rebuild, commit, push, at the DNS cutover and not before. It removes `noindex` and the preview ribbon, drops "(v2 preview)" from titles, and adds `<link rel="canonical">` on www.lowellherbco.com (which also keeps the GitHub Pages copy out of search results). 404 and 410 stay `noindex`.

**Bump `VER` in `build.py` on every deploy** that changes CSS or JS. It renames the asset files, which is the only cache-bust GitHub Pages honours.
