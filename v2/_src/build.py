#!/usr/bin/env python3
"""Build Golden Hour v2 static pages.

Run from anywhere:  python3 v2/_src/build.py
Writes the pages in v2/ (home, Find Lowell, Notes, contact, privacy, terms,
disclaimer, 404, 410), robots.txt, sitemap.xml and the versioned assets
v2/assets/site.<VER>.css|js and find.<VER>.js. v2/ is self-contained: Netlify
publishes it as the site root (netlify.toml), GitHub Pages serves it at /v2/.

Bump VER on every deploy that changes CSS/JS: GitHub Pages caches by filename
and ignores ?v= query strings.

The store (shop.html, product.html, shipping-returns.html, cart, Farm Store
section) was removed for the lowellherbco.com go-live (30 Sep 2026). It is in
git at 7d32447 (`git show 7d32447:v2/_src/build.py`) for when e-commerce returns.
"""
import html, json, pathlib, re, shutil
from html.parser import HTMLParser

VER = "v16"
# The one go-live switch. False = preview: noindex on every page, the preview ribbon, "(v2 preview)" titles.
# Set True at the DNS cutover (cutover sheet, step 6), rebuild, commit, push: indexable pages with canonical URLs on www.lowellherbco.com.
LIVE = False
SRC = pathlib.Path(__file__).resolve().parent
OUT = SRC.parent
SITE = "https://www.lowellherbco.com/"
BASE = SITE if LIVE else "https://bdunmirelowell.github.io/lowell-design-options/v2/"
TAG = "" if LIVE else " (v2 preview)"
DOORS_URL = "https://brya8385.github.io/find-lowell/data/doors.json"
PRODUCTS = json.loads((SRC / "products.json").read_text())   # catalog snapshot; the home merch band shows eight of its photos, no prices
BY_SLUG = {p["slug"]: p for p in PRODUCTS}
# Disclaimer page: the live WordPress /disclaimer/ text, verbatim (Bryan, 30 Sep). Its text is about hemp products.
# False drops the page and its footer link, and _redirects then needs /disclaimer/ pointed elsewhere (see the build report).
DISCLAIMER = True
# Notes from the Farm: real Lowell posts (lowellsupply.com/blogs/news, read 25 Sep 2026); every edit is listed in each entry's "edits"
ARTICLES = json.loads((SRC / "articles.json").read_text())
esc = html.escape


# ---------------------------------------------------------------- partials
ICON_MENU = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 8h16M4 16h16"/></svg>'
ICON_X = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>'
ICON_PIN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21Z"/><circle cx="12" cy="9.5" r="2.5"/></svg>'

IG_URL = "https://www.instagram.com/lowellfarms/"
IG_PATH = '<rect x="3" y="3" width="18" height="18" rx="5.2"/><circle cx="12" cy="12" r="4.1"/><circle cx="17.35" cy="6.65" r="1.15" fill="currentColor" stroke="none"/>'


def ig_icon(labelled=True):
    a11y = 'role="img" aria-label="Instagram"' if labelled else 'aria-hidden="true" focusable="false"'
    return f'<svg class="ig" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" {a11y}>{IG_PATH}</svg>'


# Press: each outlet's article about Lowell, opened and read 25 Sep 2026 (Robb Report and Page Six via their Wayback copies)
PRESS = [
    ("Forbes", "https://www.forbes.com/sites/javierhasse/2025/06/26/americas-31-billion-cannabis-pre-roll-habit-316-million-joints-smoked-last-year-heres-who-cashed-in/",
     "America’s $3.1 Billion Cannabis Pre-Roll Habit, June 2025"),
    ("Robb Report", "https://robbreport.com/lifestyle/news/lowell-herb-cannabis-brand-2840799/",
     "How Lowell Herb Co. Became America’s First Great Weed Brand, February 2019"),
    ("Page Six", "https://pagesix.com/2019/02/24/bella-thorne-marijuana-ad-rejected-ahead-of-oscars/",
     "Bella Thorne marijuana ad rejected ahead of Oscars, February 2019"),
    ("Newsweek", "https://www.newsweek.com/pot-marijuana-weed-lowell-herb-co-980030",
     "Pot Offenders Wanted: California’s Lowell Herb Co. Seeks to Hire Parolees, June 2018"),
]

NAV = [("index.html", "Home", "home"), ("find.html", "Find Lowell", "find"),
       ("index.html#pack", "The Pack", "pack"), ("index.html#notes", "Notes from the Farm", "notes")]

STATES = [("CA", "California"), ("CO", "Colorado"), ("NM", "New Mexico"), ("MO", "Missouri"),
          ("IL", "Illinois"), ("OH", "Ohio"), ("NY", "New York"), ("NJ", "New Jersey")]


def head(title, desc, path, extra=""):
    # preview: noindex. live: indexable, with a canonical URL on www.lowellherbco.com (also de-duplicates the GitHub Pages copy)
    robots = (f'<link rel="canonical" href="{SITE}{path}">' if path is not None else '<meta name="robots" content="noindex">') if LIVE \
        else '<meta name="robots" content="noindex,nofollow">'
    path = path or ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{robots}
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{BASE}{path}">
<meta property="og:image" content="{BASE}img/og-v2.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE}img/og-v2.jpg">
<meta name="theme-color" content="#F6EFDF">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='30' fill='%23F6EFDF' stroke='%2335291A' stroke-width='3'/%3E%3Ctext x='32' y='44' text-anchor='middle' font-family='Georgia,serif' font-style='italic' font-size='36' fill='%23A5301F'%3EL%3C/text%3E%3C/svg%3E">
<link rel="preload" href="assets/fonts/El-Hidrant-Regular.otf" as="font" type="font/otf" crossorigin>
<link rel="stylesheet" href="assets/site.{VER}.css">
{extra}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""


def gate():
    return """<div class="gate" id="gate" role="dialog" aria-modal="true" aria-labelledby="gate-h" aria-describedby="gate-d" hidden>
  <div class="gate-card">
    <span class="eyebrow red">Lowell Herb Co.</span>
    <h2 class="h2" id="gate-h">Let&rsquo;s keep this legal.</h2>
    <p class="small" id="gate-d">You must be 21 or older to enter. By entering you confirm you&rsquo;re of legal age and agree to our Terms and Privacy Policy.</p>
    <div class="gate-actions">
      <button class="btn" type="button" id="gate-yes">Yes, I&rsquo;m 21+</button>
      <button class="btn line" type="button" id="gate-no">Not yet</button>
    </div>
    <p class="small gate-no-msg" id="gate-msg" aria-live="polite"></p>
  </div>
</div>
"""


def header(active):
    cur = lambda key: ' aria-current="page"' if key == active else ""
    links = "".join(f'<a href="{h}"{cur(key)}>{label}</a>' for h, label, key in NAV if key not in ("home", "find"))
    sheet_links = "".join(f'<a href="{h}"{cur(key)}>{label}</a>' for h, label, key in NAV)
    ribbon = "" if LIVE else """<aside class="ribbon" aria-label="Preview notice"><span class="long">Design preview for team feedback &middot; not the live site &middot; </span><span class="short">Preview &middot; not the live site &middot; </span><a href="../index.html">All directions</a></aside>
"""
    return f"""{ribbon}<header class="site-head" id="top">
  <div class="container">
    <a class="wordmark" href="index.html" aria-label="Lowell Herb Co. home">Lowell</a>
    <nav class="nav" aria-label="Main">{links}</nav>
    <div class="head-actions">
      <a class="btn sm" href="find.html"{cur("find")}>{ICON_PIN}Find Lowell</a>
      <button class="icon-btn menu-btn" type="button" id="menu-open" aria-expanded="false" aria-controls="sheet" aria-label="Open menu">{ICON_MENU}</button>
    </div>
  </div>
</header>
<div class="sheet" id="sheet" role="dialog" aria-modal="true" aria-label="Menu" hidden>
  <div class="sheet-top"><a class="wordmark" href="index.html">Lowell</a>
    <button class="icon-btn" type="button" id="menu-close" aria-label="Close menu">{ICON_X}</button></div>
  <nav aria-label="Main">{sheet_links}</nav>
  <div class="sheet-zip">
    <span class="eyebrow">Find Lowell near you</span>
    {zip_form("sheet")}
  </div>
</div>
"""


def zip_form(uid, dark=False):
    return f"""<form class="field js-zip" action="find.html" method="get" role="search" aria-label="Find Lowell by ZIP code">
      <label class="sr-only" for="zip-{uid}">ZIP code</label>
      <input id="zip-{uid}" name="zip" inputmode="numeric" autocomplete="postal-code" pattern="[0-9]{{5}}" maxlength="5" placeholder="Your ZIP code" required>
      <button type="submit">Find</button>
    </form>
    <p class="field-note" aria-live="polite"></p>"""


def footer():
    return f"""<footer class="site-foot on-ink">
  <div class="container">
    <div class="foot-top">
      <div>
        <h2 class="h2">Notes from the Farm</h2>
        <p>Sourcing, craft and design, from the people who make Lowell.</p>
        <a class="link-arrow" href="index.html#notes">Read the notes</a>
      </div>
      <div class="foot-cols">
        <div><h3>Lowell</h3><a href="find.html">Find Lowell</a><a href="index.html#pack">The Pack</a><a href="index.html#notes">Notes from the Farm</a></div>
        <div><h3>Help</h3><a href="contact.html">Contact</a><a class="ig-link" href="{IG_URL}" target="_blank" rel="noopener">{ig_icon()}<span>@lowellfarms</span></a></div>
        <div><h3>Legal</h3>{"".join(f'<a href="{s}.html">{esc(short)}</a>' for s, _, short in policies())}</div>
      </div>
    </div>
    <ul class="values" aria-label="What we value"><li>Freedom</li><li>Confidence</li><li>No Bullshit</li><li>Generosity</li><li>Originality</li><li>Family</li><li>Good Vibes</li></ul>
    <div class="foot-legal">
      <p>For adults 21 and over. Lowell pre-rolls and flower are sold only through licensed dispensaries, and availability varies by state. &copy; 2026 Lowell Herb Co.</p>
      <a class="wordmark" href="#top" aria-label="Back to top">Lowell</a>
    </div>
  </div>
</footer>
"""


def tail(scripts=""):
    return f"""{scripts}<script src="assets/site.{VER}.js"></script>
</body>
</html>
"""


def pic(name, widths, alt, sizes, cls="", eager=False, jpg=None, style=""):
    srcset = ", ".join(f"img/{name}-{w}.webp {w}w" for w in widths)
    fallback = f"img/{name}-{jpg}.jpg" if jpg else f"img/{name}-{widths[-1]}.webp"
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    st = f' style="{style}"' if style else ""
    c = f' class="{cls}"' if cls else ""
    return (f'<picture><source type="image/webp" srcset="{srcset}" sizes="{sizes}">'
            f'<img src="{fallback}" alt="{esc(alt)}" {load}{c}{st}></picture>')


def mcard(p, sizes="(max-width: 760px) 46vw, 30vw"):
    """A merch photo, as plain imagery: no link, no name plate, no price (go-live without the store, Bryan 30 Sep)."""
    return (f'<figure class="mcard">'
            f'<img src="img/p/{p["slug"]}-640.webp" srcset="img/p/{p["slug"]}-360.webp 360w, img/p/{p["slug"]}-640.webp 640w" '
            f'sizes="{sizes}" alt="{esc(p["title"])}" loading="lazy" decoding="async" width="640" height="640"></figure>')


# ---------------------------------------------------------------- home
def lsphoto(name, widths, alt, sizes, cls=""):
    return f'<figure class="ls-tile {cls}">{pic(name, widths, alt, sizes)}</figure>'


MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def long_date(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{MONTHS[m - 1]} {d}, {y}"


def article_href(a):
    return f"notes-{a['slug']}.html"


def jcard(a, sizes="(max-width: 900px) 92vw, 30vw"):
    return (f'<a class="jcard" href="{article_href(a)}"><div class="im">{pic(a["img"], [480, 960], a["alt"], sizes)}</div>'
            f'<span class="eyebrow red">{esc(a["cat"])}</span><h3 class="h3">{esc(a["title"])}</h3><p>{esc(a["teaser"])}</p>'
            f'<span class="link-arrow" aria-hidden="true">Read</span></a>')


def band_tile(name, widths, alt, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<li{c}><a href="{IG_URL}" target="_blank" rel="noopener" aria-label="{esc(alt)}. Lowell on Instagram (opens in a new tab)">'
            f'{pic(name, widths, "", "(max-width: 760px) 50vw, 20vw")}{ig_icon(False)}</a></li>')


def page_home():
    usmap = (SRC / "partials" / "usmap.svg").read_text()
    for st, name in STATES:
        s = st.lower()
        usmap = re.sub(rf'(<path class="{s}" d="[^"]*">\s*</path>)',
                       rf'<a href="find.html?st={st}" tabindex="-1" aria-label="Find Lowell in {name}" data-st="{st}">\1</a>', usmap, count=1)
    usmap = usmap.replace('viewBox="0 0 959 593"', 'viewBox="20 18 910 500"')
    # the state chips are the accessible control; the map is decoration for sighted mouse users
    usmap = usmap.replace('role="img" aria-labelledby="map-title"', 'aria-hidden="true" focusable="false"')
    usmap = re.sub(r'<title id="map-title">.*?</title>', '', usmap)
    first4 = ["lowell-denim-jacket", "wax-canvas-duffel-bag", "green-bulls-head-tee", "bulls-head-metal-ashtray"]
    next4 = ["lowell-leather-rolling-tray", "great-american-cannabis-hoodie", "wax-canvas-backpack", "lowell-hockey-jersey"]
    psz = "(max-width: 760px) 46vw, 22vw"
    chips = "".join(f'<a class="chip" href="find.html?st={st}" data-st="{st}">{name}</a>' for st, name in STATES)
    body = f"""<main id="main">
<section class="hero-full hero-dusk on-photo" aria-labelledby="hero-h">
  <picture>
    <source media="(max-width: 760px)" type="image/webp" srcset="img/hero-dusk-tall-640.webp 640w, img/hero-dusk-tall-960.webp 960w" sizes="100vw">
    <source type="image/webp" srcset="img/hero-dusk-1440.webp 1440w, img/hero-dusk-2200.webp 2200w" sizes="100vw">
    <img src="img/hero-dusk-1600.jpg" alt="Friends talking in the firelight at a Lowell party at dusk" fetchpriority="high">
  </picture>
  <div class="container hero-inner">
    <div class="hero-top">
      <span class="eyebrow">Great American Cannabis</span>
      <h1 class="display" id="hero-h">Grown with intention.<br><em>Blended</em> to perfection.</h1>
      <p class="lede">We don&rsquo;t want to reinvent how you smoke, just make it better. From the flower to the pack, nothing is an afterthought.</p>
    </div>
    <div class="hero-ctas">
      <a class="btn line" href="find.html">{ICON_PIN}Find Lowell near you</a>
    </div>
  </div>
</section>

<section class="purpose-band" aria-label="Our purpose">
  <div class="container">
    <blockquote>&ldquo;To bring great American cannabis to <em>everyone</em>.&rdquo;</blockquote>
  </div>
</section>

<section class="section" id="pack" aria-labelledby="pack-h">
  <div class="container">
    <div class="pack">
      <figure class="pack-figure">
        <div class="arch">{pic("pack-tray", [640, 1000], "An open Lowell Smokes pack: the tray of six pre-rolls slid out, emergency matches in the top slot, the magnetic flap behind", "(max-width: 900px) 90vw, 440px", jpg=1000)}</div>
        <span class="pin-mark" style="left:33%;top:37%" aria-hidden="true">1</span>
        <span class="pin-mark" style="left:58%;top:57%" aria-hidden="true">2</span>
        <span class="pin-mark" style="left:24%;top:9%" aria-hidden="true">3</span>
        <span class="pin-mark" style="left:44%;top:86%" aria-hidden="true">4</span>
        <span class="pin-mark" style="left:74%;top:21%" aria-hidden="true">5</span>
        <span class="pin-mark" style="left:9%;top:31%" aria-hidden="true">6</span>
      </figure>
      <div class="pack-copy">
        <span class="eyebrow red">The Pack</span>
        <h2 class="h2" id="pack-h">Pre-rolls made with intention. A box built to match.</h2>
        <ol class="feats">
          <li class="feat"><span class="pin-mark" aria-hidden="true">1</span><h3>Quality first</h3><p>Flower from the best farms. Only the best gets in.</p></li>
          <li class="feat"><span class="pin-mark" aria-hidden="true">2</span><h3>Always blended</h3><p>A purposeful blend in every smoke: terpene diversity, flavor, balance.</p></li>
          <li class="feat"><span class="pin-mark" aria-hidden="true">3</span><h3>The magnetic flap</h3><p>The signature closure: sturdy, organic packaging that&rsquo;s ready for any outdoor adventure.</p></li>
          <li class="feat"><span class="pin-mark" aria-hidden="true">4</span><h3>The slide-out tray</h3><p>Pull the tray and your pre-rolls sit in a row, like the good silverware.</p></li>
          <li class="feat"><span class="pin-mark" aria-hidden="true">5</span><h3>Emergency matches</h3><p>Every pack ships with them. Prepared beats lucky.</p></li>
          <li class="feat"><span class="pin-mark" aria-hidden="true">6</span><h3>The wax liner</h3><p>Holds the moisture, so the last smoke in the pack is as fresh as the first.</p></li>
        </ol>
      </div>
    </div>
  </div>
</section>

<section class="section" id="goods" aria-labelledby="goods-h">
  <div class="container">
    <div class="sect-head">
      <span class="eyebrow red">Lowell goods</span>
      <h2 class="h2" id="goods-h">Timeless goods. No gimmicks.</h2>
    </div>
    <div class="bento">
      {lsphoto("ls-luggage", [640, 1000], "A woman in a green jacket carrying the Wax Canvas Duffel Bag", "(max-width: 760px) 92vw, 46vw", "a")}
      {"".join(mcard(BY_SLUG[s], psz) for s in first4)}
      {"".join(mcard(BY_SLUG[s], psz) for s in next4)}
      {lsphoto("ls-denim", [640, 1000], "Friends at a Lowell party, one wearing the Lowell Denim Jacket with its bull's-head back print", "(max-width: 760px) 92vw, 46vw", "b")}
    </div>
  </div>
</section>

<section class="mosaic-sec on-ink" aria-labelledby="people-h">
  <div class="mosaic">
    <figure class="mo mo-a">{pic("mo-pass", [800, 1400], "Friends on a leather couch passing a pack of Lowell 35's across a table of snacks", "(max-width: 760px) 100vw, 50vw")}</figure>
    <div class="mo mo-t">
      <span class="eyebrow">The whole point</span>
      <h2 class="h2" id="people-h">Bring people together.</h2>
      <p>That&rsquo;s the whole mission: the best and most distinctive American-grown products, made to be shared.</p>
      <a class="btn line" href="find.html">{ICON_PIN}Find Lowell near you</a>
    </div>
    <figure class="mo mo-b">{pic("mo-sunset", [480, 800], "A hand holding up a lit pre-roll against a low sun", "(max-width: 760px) 50vw, 25vw")}</figure>
    <figure class="mo mo-c">{pic("mo-pool", [480, 800], "A pack of Lowell 35's and an amber ashtray on the edge of a pool", "(max-width: 760px) 50vw, 25vw")}</figure>
    <figure class="mo mo-d">{pic("mo-smoke", [800, 1400], "A woman exhaling smoke against a warm wood wall, pre-roll in hand", "(max-width: 760px) 100vw, 50vw")}</figure>
  </div>
</section>

<section class="section sand find-band" id="find" aria-labelledby="find-h">
  <div class="container">
    <div class="find-copy">
      <span class="eyebrow red">Where to find us</span>
      <h2 class="h2" id="find-h">Eight states and counting.</h2>
      <p class="lede">Our pre-rolls are sold only through licensed dispensaries. Give us your ZIP and we&rsquo;ll show the shops near you, nearest first, with what&rsquo;s on their shelf today.</p>
      <div style="width:100%;max-width:440px">{zip_form("home")}</div>
      <nav class="state-links" aria-label="Find Lowell by state">{chips}</nav>
    </div>
    <div class="usmap-wrap">{usmap}
      <div class="map-stats"><div><b>8</b><span>states</span></div><div><b>700+</b><span>licensed shops</span></div><div><b>1</b><span>standard</span></div></div>
    </div>
  </div>
</section>

<section class="section" id="notes" aria-labelledby="notes-h">
  <div class="container">
    <div class="sect-head row">
      <span class="eyebrow red">The blog</span>
      <h2 class="h2" id="notes-h">Notes from the Farm.</h2>
      <p class="lede">Sourcing, craft and design, from the people who make Lowell.</p>
      <span></span>
    </div>
    <div class="jcards">{"".join(jcard(x) for x in ARTICLES)}</div>
  </div>
</section>

<section class="press-band on-ink" aria-labelledby="press-h">
  <div class="container">
    <h2 class="sr-only" id="press-h">Press</h2>
    <figure class="press-quote">
      <blockquote cite="{PRESS[0][1]}">&ldquo;Lowell is one of the most widely recognized names in American cannabis, with a trailblazing legacy&hellip;&rdquo;</blockquote>
      <figcaption>Forbes &middot; June 2025</figcaption>
    </figure>
    <ul class="press-names" aria-label="As featured in">{"".join(f'<li><a href="{u}" target="_blank" rel="noopener" aria-label="{n}: {esc(t)} (opens in a new tab)">{n}</a></li>' for n, u, t in PRESS)}</ul>
  </div>
</section>

<section class="band" aria-labelledby="band-h">
  <h2 class="sr-only" id="band-h">Lowell on Instagram</h2>
  <ul>
    {band_tile("band-bonfire", [480, 720], "Two guests watching a bonfire at a Lowell party, one in a jacket with the Lowell bull on the back")}
    {band_tile("band-light", [480, 720], "A man lighting a pre-roll over an amber ashtray")}
    {band_tile("hero-pack", [720, 1200], "A Lowell Smokes pack, three matches and a pre-roll resting in a stone ashtray on a walnut table")}
    {band_tile("band-greens", [480, 720], "A man in a mustard tee smoking a pre-roll among tropical leaves")}
    {band_tile("band-jacket", [480, 720], "A woman in the green quilted Lowell Herb Co. jacket, seen from behind", "band-5")}
  </ul>
  <a class="band-handle" href="{IG_URL}" target="_blank" rel="noopener">{ig_icon()}<span>@lowellfarms</span></a>
</section>
</main>
"""
    out = head(f"Lowell Herb Co. · Great American Cannabis{TAG}",
               "Golden Hour v2: the new lowellherbco.com homepage, with a store locator for all eight Lowell states." if not LIVE else
               "We don’t want to reinvent how you smoke, just make it better. From the flower to the pack, nothing is an afterthought.",   # the hero line, verbatim
               "") + gate() + header("home") + body + footer() + tail()
    (OUT / "index.html").write_text(out)


# ---------------------------------------------------------------- Notes from the Farm articles
def page_article(a):
    blocks = "".join(f'<h2 class="h3">{esc(b["h"])}</h2>' if "h" in b else f'<p>{esc(b["p"])}</p>' for b in a["body"])
    more = "".join(jcard(x, "(max-width: 900px) 92vw, 44vw") for x in ARTICLES if x["slug"] != a["slug"])
    body = f"""<main id="main">
<article class="post" aria-labelledby="post-h">
  <header class="container post-head">
    <p class="crumbs"><a href="index.html">Home</a> / <a href="index.html#notes">Notes from the Farm</a></p>
    <span class="eyebrow red">{esc(a["cat"])}</span>
    <h1 class="h2" id="post-h">{esc(a["title"])}</h1>
    <p class="post-meta">By {esc(a["by"])} &middot; <time datetime="{a["date"]}">{long_date(a["date"])}</time></p>
  </header>
  <figure class="container post-hero">{pic(a["img"], [480, 960], a["alt"], "(max-width: 1000px) 92vw, 960px", eager=True)}</figure>
  <div class="container post-body">{blocks}</div>
</article>
<section class="section sand" aria-labelledby="more-h">
  <div class="container">
    <div class="sect-head row">
      <span class="eyebrow red">Notes from the Farm</span>
      <h2 class="h2" id="more-h">Keep reading.</h2>
      <span></span>
      <a class="link-arrow" href="index.html#notes">All notes</a>
    </div>
    <div class="jcards two">{more}</div>
  </div>
</section>
</main>
"""
    out = head(f"{a['title']} · Notes from the Farm · Lowell Herb Co.{TAG}", a["teaser"], article_href(a)) + gate() + header("notes") + body + footer() + tail()
    (OUT / article_href(a)).write_text(out)


# ---------------------------------------------------------------- contact + policies
CONTACT_EMAIL = "admin@lowellherbco.com"   # Bryan, 25 Sep 2026: email only, no form, no address or phone
# The policies are the live WordPress pages, verbatim (Bryan, 30 Sep 2026): the raw /wp-json/wp/v2/pages/<id> responses,
# fetched 1 Oct 2026 01:34 UTC, are in policies/source-wp-2026-09-30/. Only the markup is changed (classes dropped,
# headings re-levelled, <hr> dropped); every word is WordPress's. The old {{To confirm}} drafts are in git at 7d32447.
WP_SRC = SRC / "policies" / "source-wp-2026-09-30"
POLICY_PAGES = [("privacy", 3, "Privacy"), ("terms", 362, "Terms"), ("disclaimer", 924, "Disclaimer")]   # slug, WordPress page id, footer label
WP_LINKS = {"/privacy-policy/": "privacy.html", "/terms-of-service/": "terms.html", "/disclaimer/": "disclaimer.html"}


def policies():
    """[(slug, WordPress JSON, footer label)] for the policy pages this build publishes."""
    return [(slug, json.loads((WP_SRC / f"page-{pid}.json").read_text()), short)
            for slug, pid, short in POLICY_PAGES if slug != "disclaimer" or DISCLAIMER]


class WPClean(HTMLParser):
    """WordPress block HTML -> the site's .doc markup. Keeps p, lists, headings, strong/em, br and links; drops classes,
    styles, <hr> and any other tag (its text is kept). The top heading level in the page becomes h2, the next h3."""
    KEEP = {"p", "ul", "ol", "li", "strong", "b", "em", "i", "br"}

    def __init__(self, levels):
        super().__init__(convert_charrefs=True)
        self.map = {f"h{n}": f"h{i + 2}" for i, n in enumerate(levels)}
        self.out, self.stack = [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.map:
            self.out.append(f"<{self.map[tag]}>"); self.stack.append(self.map[tag])
        elif tag == "a":
            href = a.get("href")
            if href:
                for old, new in WP_LINKS.items():
                    if re.fullmatch(rf"https?://(www\.)?lowellherbco\.com{re.escape(old)}?", href):
                        href = new
                self.out.append(f'<a class="link" href="{esc(href)}">'); self.stack.append("a")
            else:
                self.stack.append(None)   # an <a> with no href is plain text on the WordPress page; keep it plain
        elif tag == "br":
            self.out.append("<br>")
        elif tag in self.KEEP:
            self.out.append(f"<{tag}>"); self.stack.append(tag)
        else:
            self.stack.append(None)

    def handle_endtag(self, tag):
        if tag == "br" or not self.stack:
            return
        t = self.stack.pop()
        if t:
            self.out.append(f"</{t}>")

    def handle_startendtag(self, tag, attrs):
        if tag == "br":
            self.out.append("<br>")

    def handle_data(self, data):
        self.out.append(esc(data, quote=False))


def wp_html(rendered):
    levels = sorted({int(n) for n in re.findall(r"<h([1-6])[\s>]", rendered)})
    w = WPClean(levels); w.feed(rendered); w.close()
    h = re.sub(r"\s*\n\s*", "\n", "".join(w.out)).strip()
    h = re.sub(r"<p>\s*</p>", "", h)
    def hid(m):   # heading anchors, e.g. #section-4-cookies
        slug = re.sub(r"[^a-z0-9]+", "-", html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).lower()).strip("-")[:60]
        return f'<{m.group(1)} id="{slug}">{m.group(2)}</{m.group(1)}>'
    return re.sub(r"<(h[23])>(.*?)</\1>", hid, h, flags=re.S)


def page_contact():
    body = f"""<main id="main">
<section class="page-head" aria-labelledby="contact-h">
  <div class="container">
    <p class="crumbs"><a href="index.html">Home</a> / Contact</p>
    <span class="eyebrow red">Contact</span>
    <h1 class="display" id="contact-h">Get in touch.</h1>
  </div>
</section>
<section class="section">
  <div class="container contact-grid">
    <div class="contact-card">
      <h2 class="h3">Email us</h2>
      <p class="small">Questions, press, or anything else.</p>
      <a class="contact-mail" href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>
    </div>
    <div class="contact-card">
      <h2 class="h3">Looking for Lowell pre-rolls?</h2>
      <p class="small">Our pre-rolls are sold only through licensed dispensaries.</p>
      <a class="link-arrow" href="find.html">Find Lowell near you</a>
    </div>
    <div class="contact-card">
      <h2 class="h3">Follow along</h2>
      <p class="small">New goods, events and the people behind Lowell.</p>
      <a class="ig-link contact-ig" href="{IG_URL}" target="_blank" rel="noopener">{ig_icon()}<span>@lowellfarms</span></a>
    </div>
  </div>
</section>
</main>
"""
    out = head(f"Contact · Lowell Herb Co.{TAG}", "How to reach Lowell Herb Co.", "contact.html") + gate() + header("contact") + body + footer() + tail()
    (OUT / "contact.html").write_text(out)


def page_policy(slug, wp, all_pages):
    title = html.unescape(wp["title"]["rendered"])
    others = " &middot; ".join(f'<a class="link" href="{s}.html">{esc(html.unescape(w["title"]["rendered"]))}</a>' for s, w, _ in all_pages if s != slug)
    body = f"""<main id="main">
<section class="page-head" aria-labelledby="doc-h">
  <div class="container">
    <p class="crumbs"><a href="index.html">Home</a> / {esc(title)}</p>
    <h1 class="display" id="doc-h">{esc(title)}</h1>
  </div>
</section>
<section class="section">
  <div class="container doc wp" data-wp-id="{wp["id"]}" data-wp-modified="{wp["modified"]}">
<div class="wp-text">
{wp_html(wp["content"]["rendered"])}
</div>
    <p class="doc-more small">Also see: {others}</p>
  </div>
</section>
</main>
"""
    out = head(f"{title} · Lowell Herb Co.{TAG}", f"Lowell Herb Co. {title}.", f"{slug}.html") + gate() + header("legal") + body + footer() + tail()
    (OUT / f"{slug}.html").write_text(out)


# ---------------------------------------------------------------- 404 and 410 (Netlify serves them at any path, so links are root-absolute)
def absolutize(page):
    """Relative href/src/srcset -> root-absolute ("/assets/...", "/find.html"), for pages Netlify serves at any URL."""
    rel = lambda u: u if re.match(r"(?:[a-z]+:|/|#)", u) else "/" + u
    page = re.sub(r'\b(href|src)="([^"]*)"', lambda m: f'{m.group(1)}="{rel(m.group(2))}"', page)
    return re.sub(r'\bsrcset="([^"]*)"', lambda m: 'srcset="' + ", ".join(rel(x.strip()) for x in m.group(1).split(",")) + '"', page)


def page_gone(code, h1, text):
    body = f"""<main id="main">
<section class="page-head err-head" aria-labelledby="err-h">
  <div class="container">
    <span class="eyebrow red">{code}</span>
    <h1 class="display" id="err-h">{h1}</h1>
    <p class="lede">{text}</p>
    <div class="err-ctas"><a class="btn" href="index.html">Go to the home page</a><a class="btn line" href="find.html">{ICON_PIN}Find Lowell near you</a></div>
  </div>
</section>
</main>
"""
    out = head(f"{h1} · Lowell Herb Co.{TAG}", text, None) + gate() + header("") + body + footer() + tail()
    (OUT / f"{code}.html").write_text(absolutize(out))


# ---------------------------------------------------------------- robots.txt + sitemap.xml (served from the Netlify root)
def seo_files(pages):
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n")
    urls = "".join(f"  <url><loc>{SITE}{'' if p == 'index.html' else p}</loc></url>\n" for p in pages)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')


# ---------------------------------------------------------------- find lowell
def page_find():
    extra = ('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" crossorigin="anonymous" referrerpolicy="no-referrer">\n'
             f'<link rel="preconnect" href="https://brya8385.github.io" crossorigin>\n')
    body = f"""<main id="main" class="fl" data-doors="{DOORS_URL}">
<section class="page-head fl-head" aria-labelledby="fl-h">
  <div class="container fl-headgrid">
    <div class="fl-intro">
      <p class="crumbs"><a href="index.html">Home</a> / Find Lowell</p>
      <h1 class="fl-title" id="fl-h">Find Lowell</h1>
      <p class="small">Every licensed shop carrying Lowell, with what&rsquo;s on its shelf today wherever the shop&rsquo;s own menu tells us.</p>
    </div>
    <form class="fl-search" id="fl-form" role="search" aria-label="Search stores">
      <span class="fl-asof mono" id="fl-asof">Loading store list&hellip;</span>
      <div class="field">
        <label class="sr-only" for="fl-q">ZIP code or city</label>
        <input id="fl-q" name="q" autocomplete="postal-code" placeholder="ZIP code or city" enterkeyhint="search">
        <button type="submit">Search</button>
      </div>
      <button type="button" class="fl-locate" id="fl-locate" hidden><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="7" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="2.6" fill="currentColor"/><path d="M12 1.5v4M12 18.5v4M1.5 12h4M18.5 12h4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>Use my location</button>
      <p class="field-note" id="fl-note" aria-live="polite"></p>
    </form>
  </div>
  <div class="container">
    <details class="fl-filters" id="fl-filters" hidden>
      <summary class="chip" id="fl-fsum">Filters<span class="mono" id="fl-fcount"></span></summary>
      <div class="fl-fbody">
      <div class="fl-group" role="group" aria-labelledby="g-rad"><span class="fl-lbl" id="g-rad">Within</span><div id="fl-rad"></div></div>
      <div class="fl-group" role="group" aria-labelledby="g-line"><span class="fl-lbl" id="g-line">Line</span><div id="fl-line"></div></div>
      <div class="fl-group" role="group" aria-labelledby="g-lean"><span class="fl-lbl" id="g-lean">Type</span><div id="fl-lean"></div></div>
      <div class="fl-group" role="group" aria-labelledby="g-st"><span class="fl-lbl" id="g-st">State</span><div id="fl-st"></div></div>
      </div>
    </details>
  </div>
</section>
<section class="fl-body" aria-labelledby="fl-results-h">
  <div class="fl-panel">
    <h2 class="sr-only" id="fl-results-h">Stores</h2>
    <div class="fl-resulthead"><p class="fl-count" id="fl-count" aria-live="polite"></p>
      <label class="fl-toggle"><input type="checkbox" id="fl-stock" checked> Hide out of stock</label></div>
    <div class="fl-list" id="fl-list"><div class="fl-loading">Loading stores&hellip;</div></div>
  </div>
  <div class="fl-mapwrap"><div id="fl-map" role="region" aria-label="Map of stores"></div></div>
</section>
<section class="section sand fl-key" aria-labelledby="key-h">
  <div class="container">
    <h2 class="h3" id="key-h">How to read the list</h2>
    <ul class="fl-keylist">
      <li><span class="kdot k-stock" aria-hidden="true"></span><div><b>In stock now</b><p class="small">On the shop&rsquo;s own online menu today, at the shelf price that menu quotes.</p></div></li>
      <li><span class="kdot k-out" aria-hidden="true"></span><div><b>Currently out of stock</b><p class="small">The shop&rsquo;s live menu shows no Lowell right now.</p></div></li>
      <li><span class="kdot k-carries" aria-hidden="true"></span><div><b>Lowell store</b><p class="small">A shop that carries Lowell. We can&rsquo;t read its menu, so we don&rsquo;t show stock or prices.</p></div></li>
    </ul>
  </div>
</section>
</main>
"""
    scripts = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>\n'
               f'<script src="assets/find.{VER}.js"></script>\n')
    out = head(f"Find Lowell · Store locator · Lowell Herb Co.{TAG}",
               "Find licensed dispensaries carrying Lowell pre-rolls near you, in California, Colorado, New Mexico, Missouri, Illinois, Ohio, New York and New Jersey.",
               "find.html", extra) + gate() + header("find") + body + footer() + tail(scripts)
    (OUT / "find.html").write_text(out)


FONTS = ["El-Hidrant-Regular.otf", "GothamCondensed-Book.otf", "GothamCondensed-Medium.otf", "GothamCondensed-Bold.otf", "Nitti-Normal.ttf"]


def assets():
    a = OUT / "assets"
    a.mkdir(exist_ok=True)
    for old in list(a.glob("site.*.css")) + list(a.glob("site.*.js")) + list(a.glob("find.*.js")):
        old.unlink()
    shutil.copy(SRC / "site.css", a / f"site.{VER}.css")
    shutil.copy(SRC / "site.js", a / f"site.{VER}.js")
    shutil.copy(SRC / "find.js", a / f"find.{VER}.js")
    # the brand fonts live at the repo root (assets/fonts, shared with the v1 pages); v2 carries its own copy so it can be
    # published as a site root on Netlify, where ../ above v2 doesn't exist
    (a / "fonts").mkdir(exist_ok=True)
    for f in FONTS:
        shutil.copy(OUT.parent / "assets" / "fonts" / f, a / "fonts" / f)


if __name__ == "__main__":
    for gone in ("shop.html", "product.html", "shipping-returns.html"):   # the store pages, removed for the go-live
        (OUT / gone).unlink(missing_ok=True)
    if not DISCLAIMER:
        (OUT / "disclaimer.html").unlink(missing_ok=True)
    assets()
    page_home(); page_find()
    for a in ARTICLES:
        page_article(a)
    page_contact()
    pol = policies()
    for slug, wp, _ in pol:
        page_policy(slug, wp, pol)
    page_gone(404, "This page isn’t here.", "The page you’re looking for has moved or no longer exists.")
    page_gone(410, "This page is gone.", "It was removed from lowellherbco.com and isn’t coming back.")
    seo_files(["index.html", "find.html"] + [article_href(a) for a in ARTICLES] + ["contact.html"] + [f"{s}.html" for s, _, _ in pol])
    print("built", VER, "LIVE" if LIVE else "preview", sorted(p.name for p in OUT.glob("*.html")))
