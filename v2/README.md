# Golden Hour v2: preview

**Live:** https://bdunmirelowell.github.io/lowell-design-options/v2/

This is a static design preview for team feedback, not the Shopify build. Every page carries `noindex,nofollow` because photo rights are not cleared. Pages:

| Page | File | What it is |
|---|---|---|
| Home | `index.html` | Golden Hour, sharpened |
| Find Lowell | `find.html` | Store locator on live data |
| Farm Store | `shop.html` | Shop landing: three categories and all 21 goods |
| Product | `product.html?p=<slug>` | Placeholder that confirms Farm Store links resolve |

The critique of the July page is in [`CRITIQUE.md`](CRITIQUE.md).

## What changed and why

**Rules the old page broke**
- Four images showed strain or blend names (the tube label, the open pack, the "ritual" pack, the jars). Each is now retouched to a blank label or swapped for another image.
- The farm film had a 3.6-second pack close-up with a blend name on it. It's cut: 45 s became 41 s.
- The open-pack photo had the printed 1909 Bull Lowell "Our Story" card on the flap. It's replaced by a Hero Pack Shots photo with no card.
- The age gate's "Est. 1909" line is removed.
- The "Smoke Accessories" card sold the stone ashtray from the Eunbi shoot, which isn't a Lowell product. The Farm Store now shows the real Signature Metal Ashtray, and the stone ashtray is never captioned as a Lowell product.
- "Bull Roundel Tee" (not in the catalog) is gone. Every product name and price now matches the live Farm Store catalog (lowell-farms.myshopify.com, pulled 23 Sep 2026).
- The footer's "@lowellfarms" handle is removed because it reads as the separate public company. "Instagram" is a placeholder link.
- **All photos from the two unconfirmed shoots are out.** See the rights table below.

**Sharper, same direction**
- Type is on one seven-step scale; the old page had 18 fixed sizes plus 7 clamps.
- Spacing is on one 8-pt scale, and every section uses the same rhythm.
- Colour tokens are unchanged except two text tones darkened to pass WCAG AA: eyebrows went from 2.2:1 to 5.0:1, and secondary text on sand from 4.2:1 to 5.3:1.
- Hero is a split layout: a 100px headline beside an arched photo (the arch motif from the age gate). The paragraph is cut from 43 to 30 words, and the CTAs are real links.
- Merged sections:
  - The two pack sections are one: annotated photo, four features, and the film.
  - The map band and the ZIP band are one "Find Lowell" band: ZIP box, state chips and map.
- The Farm Store moved from seventh section to fourth and uses the store's transparent product cutouts on a single card style.
- The auto-scrolling film strip is now a swipeable strip with no animation.

**Works on a phone**
- A menu button opens a full-screen sheet with the nav and a ZIP box.
- The Farm Store grid is 2-up on phones.
- Touch targets are at least 44px wherever they were under that.

**Accessibility**
- Age gate and menu trap focus, make the page behind them inert, and return focus when closed.
- Skip link, visible focus rings everywhere, and alt text on every image.
- axe-core (WCAG 2.1 AA + best practice) reports **0 violations** on Home, Find Lowell, Farm Store and Product, at 1440px and 390px.

**Load weight**
- Home first view: **0.56 MB, down from 2.1 MB**. Full scroll: **1.2 MB, down from 3.9 MB**, not counting the video.
- Film: **4.7 MB, down from 26.7 MB**. It has a poster and `preload="none"`, so it downloads only when played. The old page requested it on load.
- WebP with `srcset`; only the hero image loads eagerly.
- CSS and JS filenames are versioned per deploy (`site.v1.css`, `find.v1.js`), because GitHub Pages ignores `?v=`.

**Find Lowell**
- Uses the find-lowell app's behaviour as its spec:
  - "Where are you?" landing: ZIP/city search, or one of 8 state buttons
  - radius 25/50/100/Any
  - line and type (lean) filters
  - one pin per store on OSM tiles, with Leaflet 1.9.4 from cdnjs
  - "Store list updated <asof>"
- `doors.json` is fetched live from `brya8385.github.io/find-lowell` on every visit, with no embedded or cached copy. If the fetch fails, the page shows an error and a retry button, not stale data. Test it with `find.html?doors-test=fail`.
- The four tiers look different in both the pins and the cards:
  - **In stock** (solid green)
  - **Listed, out today** (ring)
  - **Carries Lowell · shipped <date>** (dashed)
  - **Partner-reported** (grey diamond)
- Tier B and C never show a price. The page enforces this itself and doesn't rely on the data.
- **No blend names:** product rows are grouped by line × lean (e.g. "Quicks · Indica · 10 pre-rolls, 0.35g each"), and the blend-name field in the data is never read.
  - Leak test: I rendered all 8 states with every tier shown and searched the page text for the 287 distinct product names in the data.
  - 0 blend names appear. The only matches were store and place names, e.g. "State of Mind Dispensary" and "Chicago (Midway)".
- ZIP search resolves any US ZIP using Census 2023 ZCTA centroids. They're split by first digit, so a search loads about 90 KB. The old app only knew ZIPs that already had a store.
- Home's "Find Lowell near you" box goes to `find.html?zip=…`. The state chips on Home go to `find.html?st=…`.

## Photo rights

Brief rule: swap out the Erica Danger 2021 shoot and the 2021 Summer Lifestyle Shoot (UNKOMMON: beach, roof, greenhouse and the Brigitte set) wherever a replacement holds up.

**Remaining images from those two shoots: none.** Every one was replaced. Provenance was checked by perceptual hash against 4,818 Drive images, plus a filename search of the flagged folders.

One near-miss: the "Merchandise Lifestyle Shots" folder holds `20210128-3U9A1693.jpg`, a couple in the green tee. It looks like merch photography, but it's a copy of a frame from the UNKOMMON beach shoot (`Lowell 2021 Summer Lifestyle Shoot/UNKOMMON/BEACH/Copy of 20210128-3U9A1693.jpg`). I used it in a draft, caught it, and replaced it. Anyone reusing images from that folder should check the same way.

Every image v2 uses (sources under `Shared drives/Graphic Design/Photography` unless stated):

| v2 file | Where it's used | Source | Rights status |
|---|---|---|---|
| `hero-pack-*`, `og-v2.jpg` | Hero, share card | `Eunbi Ashtray, Hex Pipe Bundles/Ashtray, Pack/Export186576.jpg`. Strain name retouched off the label. | Eunbi accessory shoot, listed in the brief as a replacement source. The ashtray is stone, not a Lowell product, and isn't captioned as one. |
| `film-pack.webp` | Photo strip | `Eunbi …/Ashtray, Pack/Export186582.jpg`, label retouched | Same shoot |
| `preroll-*` | Pre-roll diagram | `D2C Digital Images/PNGS/HYBRID_Single_…_25.png` (the July asset; the filename carries a strain name). Strain name retouched off the tube. | In-house product render |
| `pack-tray-*` | The Pack | `Hero Pack Shots/ne1jQrmg.jpeg` | Not a flagged shoot. Photographer not recorded in Drive: **confirm**. |
| `journal-box-*` | Journal | `Hero Pack Shots/2S7HO84w.jpeg`, blend name retouched off the label | Same as above: **confirm** |
| `journal-farm-*`, `journal-blend-*`, `film-canopy`, `film-prerolls`, `film-leaf` | Journal, photo strip | `FarmVisit_121421` (iPhone and Canon 5D) | Farm visit, Dec 2021. Listed in the brief as a replacement source. |
| `people-*` | "Bring people together" | `2025/2025 Events/New York/6-5-25 Lowell Bonfire Party/Photos/Kwesi's Raw Photos/132A0081.JPG` | Lowell's own event photography. Attendees are identifiable, and one jacket shows an embroidered first name: **confirm a likeness release**. |
| `film-tee.webp` | Photo strip | `Merchandise Lifestyle Shots/Green Lowell Shirt/132A9928.JPG` | Same in-house camera series (132A) as the 2025 event shoots. Model release not in Drive: **confirm**. |
| `farm-to-pack-v2.mp4`, poster | The Pack | The July `farm-to-pack.mp4` (from a 140 MB Drive original), trimmed | In-house production footage, not a flagged shoot. |
| `p/*.webp` (21 products) | Farm Store | Product cutouts from the live Shopify catalog CDN | Lowell's own product photography |

Images that "confirm" doesn't cover: none. The v1 pages (option1–4) still use the unconfirmed shoots and are unchanged.

## Known gaps

**Store data (session 08 owns the data feed)**
- `doors.json` is dated **11 Sep 2026**, 12 days old when this was built. The page shows that date. Once session 08's daily rebuild lands, the page picks it up with no change here.
- Two Colorado partner stores have coordinates outside Colorado:
  - "Everyday Wellness — 6th Ave, Aurora" is pinned in Aurora, **Illinois**.
  - "Emerald Fields — South Boulder" is pinned in Montana.
  - v2 lists both but doesn't pin them ("Map location unavailable"). The fix belongs in the data feed.
- California shows 14 of the 61 stores we ship. The other 47 have no address in our records yet.
- City search only knows cities that have a Lowell store. ZIP search covers every US ZIP except PO-box-only ZIPs, which have no Census centroid.

**Locator setup**
- The map uses the public OpenStreetMap tile server. That's fine for a preview, but OSM's usage policy rules it out for production traffic, so the live site needs a tile provider.

**Placeholders and unverified copy**
- Farm Store product pages, cart, checkout and email sign-up are placeholders.
- Journal cards don't link anywhere; no articles exist.
- Copy carried over from v1 and not re-verified:
  - the press quote and the four outlet names under it
  - "700+ licensed shops": the live data maps 658 stores plus 47 unplaced CA stores, which is 705
  - the "George Allen" journal byline
- The state licence and marketing disclosure line in the footer is still a placeholder.
- The age gate stores a yes in the browser (`localStorage`). That's a courtesy gate, not a compliance-grade age check.

**Not built**
- Dark mode is off by design; Golden Hour is a light palette.

## How to edit

The pages are generated, so don't hand-edit the four `.html` files. Edit `_src/` and rebuild:

```
python3 v2/_src/build.py
```

- `_src/build.py` holds the page markup.
- `_src/site.css` holds the tokens and styles.
- `_src/site.js` holds the gate, menu and shop filter.
- `_src/find.js` holds the locator.
- `_src/products.json` is the catalog snapshot.

**Bump `VER` in `build.py` on every deploy** that changes CSS or JS. It renames the asset files, which is the only cache-bust GitHub Pages honours.
