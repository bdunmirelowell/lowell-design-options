#!/usr/bin/env python3
"""Build Golden Hour v2 static pages.

Run from anywhere:  python3 v2/_src/build.py
Writes v2/index.html, v2/find.html, v2/shop.html, v2/product.html and the
versioned assets v2/assets/site.<VER>.css|js and find.<VER>.js.

Bump VER on every deploy that changes CSS/JS: GitHub Pages caches by filename
and ignores ?v= query strings.
"""
import html, json, pathlib, re, shutil

VER = "v1"
SRC = pathlib.Path(__file__).resolve().parent
OUT = SRC.parent
BASE = "https://bdunmirelowell.github.io/lowell-design-options/v2/"
DOORS_URL = "https://brya8385.github.io/find-lowell/data/doors.json"
PRODUCTS = json.loads((SRC / "products.json").read_text())
BY_SLUG = {p["slug"]: p for p in PRODUCTS}
esc = html.escape


def money(p):
    v = p["price"]
    return f"${v:,.0f}" if v == int(v) else f"${v:,.2f}"


# ---------------------------------------------------------------- partials
ICON_CART = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 7h14l-1.2 11.1a2 2 0 0 1-2 1.9H8.2a2 2 0 0 1-2-1.9L5 7Z"/><path d="M9 10V6a3 3 0 0 1 6 0v4"/></svg>'
ICON_MENU = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 8h16M4 16h16"/></svg>'
ICON_X = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>'
ICON_PIN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21Z"/><circle cx="12" cy="9.5" r="2.5"/></svg>'

NAV = [("index.html", "Home", "home"), ("shop.html", "Farm Store", "shop"), ("find.html", "Find Lowell", "find"),
       ("index.html#pack", "The Pack", "pack"), ("index.html#journal", "Journal", "journal")]

STATES = [("CA", "California"), ("CO", "Colorado"), ("NM", "New Mexico"), ("MO", "Missouri"),
          ("IL", "Illinois"), ("OH", "Ohio"), ("NY", "New York"), ("NJ", "New Jersey")]


def head(title, desc, path, extra=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
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
<link rel="preload" href="../assets/fonts/El-Hidrant-Regular.otf" as="font" type="font/otf" crossorigin>
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
    return f"""<aside class="ribbon" aria-label="Preview notice"><span class="long">Design preview for team feedback &middot; not the live site &middot; </span><span class="short">Preview &middot; not the live site &middot; </span><a href="../index.html">All directions</a></aside>
<header class="site-head" id="top">
  <div class="container">
    <a class="wordmark" href="index.html" aria-label="Lowell Herb Co. home">Lowell</a>
    <nav class="nav" aria-label="Main">{links}</nav>
    <div class="head-actions">
      <a class="btn sm" href="find.html"{cur("find")}>{ICON_PIN}Find Lowell</a>
      <a class="icon-btn" href="shop.html" aria-label="Cart, 0 items (checkout arrives with the Shopify build)">{ICON_CART}<span class="cart-count" aria-hidden="true">0</span></a>
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
        <h2 class="h2">Letters from the farm</h2>
        <p>New goods, restock news and first word on drops. One email a month, at most.</p>
        <form class="field js-signup" action="#" aria-label="Email sign-up">
          <label class="sr-only" for="signup-email">Email address</label>
          <input id="signup-email" type="email" autocomplete="email" placeholder="Your email" required>
          <button type="submit">Sign up</button>
        </form>
        <p class="field-note" aria-live="polite"></p>
      </div>
      <div class="foot-cols">
        <div><h3>Shop</h3><a href="shop.html">Farm Store</a><a href="shop.html?c=apparel">Apparel</a><a href="shop.html?c=luggage">Luggage</a><a href="shop.html?c=accessories">Accessories</a></div>
        <div><h3>Lowell</h3><a href="find.html">Find Lowell</a><a href="index.html#apart">What sets us apart</a><a href="index.html#pack">The Pack</a><a href="index.html#journal">Journal</a></div>
        <div><h3>Help</h3><a href="#top">Contact</a><a href="#top">Shipping &amp; returns</a><a href="#top">Privacy</a><a href="#top">Terms</a><a href="#top">Instagram</a></div>
      </div>
    </div>
    <ul class="values" aria-label="What we value"><li>Freedom</li><li>Confidence</li><li>No Bullshit</li><li>Generosity</li><li>Originality</li><li>Family</li><li>Good Vibes</li></ul>
    <div class="foot-legal">
      <p>For adults 21 and over. Nothing sold in the Farm Store contains cannabis. Lowell pre-rolls and flower are sold only through licensed dispensaries, and availability varies by state. [Licensee name and license number shown here per state marketing rules.] &copy; 2026 Lowell Herb Co.</p>
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


def pcard(p, sizes="(max-width: 760px) 46vw, 30vw"):
    sold = not p["avail"]
    tag = '<span class="tag">Sold out</span>' if sold else f'<span class="price">{money(p)}</span>'
    return (f'<a class="pcard{" soldout" if sold else ""}" href="product.html?p={p["slug"]}">'
            f'<div class="im"><img src="img/p/{p["slug"]}-640.webp" srcset="img/p/{p["slug"]}-360.webp 360w, img/p/{p["slug"]}-640.webp 640w" '
            f'sizes="{sizes}" alt="{esc(p["title"])}" loading="lazy" decoding="async" width="640" height="640"></div>'
            f'<div class="meta"><h3>{esc(p["title"])}</h3>{tag}</div></a>')


# ---------------------------------------------------------------- home
def page_home():
    usmap = (SRC / "partials" / "usmap.svg").read_text()
    names = dict(STATES)
    for st, name in STATES:
        s = st.lower()
        usmap = re.sub(rf'(<path class="{s}" d="[^"]*">\s*</path>)',
                       rf'<a href="find.html?st={st}" tabindex="-1" aria-label="Find Lowell in {name}" data-st="{st}">\1</a>', usmap, count=1)
    usmap = usmap.replace('viewBox="0 0 959 593"', 'viewBox="20 18 910 500"')
    # the state chips are the accessible control; the map is decoration for sighted mouse users
    usmap = usmap.replace('role="img" aria-labelledby="map-title"', 'aria-hidden="true" focusable="false"')
    usmap = re.sub(r'<title id="map-title">.*?</title>', '', usmap)
    home6 = ["lowell-denim-jacket", "wax-canvas-duffel-bag", "green-bulls-head-tee",
             "bulls-head-metal-ashtray", "lowell-leather-rolling-tray", "great-american-cannabis-hoodie"]
    chips = "".join(f'<a class="chip" href="find.html?st={st}" data-st="{st}">{name}</a>' for st, name in STATES)
    body = f"""<main id="main">
<section class="hero" aria-labelledby="hero-h">
  <div class="container">
    <div class="hero-copy">
      <span class="eyebrow red">Great American Cannabis</span>
      <h1 class="display" id="hero-h">Grown with intention. <em>Blended</em> to perfection.</h1>
      <p class="lede">We don&rsquo;t want to reinvent how you smoke, just make it better. From how we grow our cannabis to how we roll, pack and ship it, every detail is considered.</p>
      <div class="hero-ctas">
        <a class="btn" href="shop.html">Shop the Farm Store</a>
        <a class="btn line" href="find.html">{ICON_PIN}Find Lowell near you</a>
      </div>
    </div>
    <figure class="hero-media" style="margin:0">
      <div class="arch">{pic("hero-pack", [720, 1200], "A Lowell Smokes pack and a stone ashtray with a pre-roll on a walnut table, matches beside them, in warm afternoon light", "(max-width: 860px) 90vw, 540px", eager=True, jpg=1200)}</div>
      <div class="hero-stamp" aria-hidden="true">Natura<br>Arte<br>Aucta</div>
    </figure>
  </div>
</section>

<section class="section sand purpose" aria-labelledby="purpose-h">
  <div class="container">
    <span class="eyebrow" id="purpose-h">Why we exist</span>
    <blockquote>&ldquo;To bring great American cannabis to <em>everyone</em>.&rdquo;</blockquote>
    <ul class="pillars" aria-label="Brand pillars"><li>Effortless Edge</li><li>Quality Ingenuity</li><li>Crafted Natural</li><li>Explorer Social</li></ul>
  </div>
</section>

<section class="section" id="apart" aria-labelledby="apart-h">
  <div class="container">
    <div class="sect-head">
      <span class="eyebrow red">What sets us apart</span>
      <h2 class="h2" id="apart-h">Every product, crafted with respect for the plant, our planet, and you.</h2>
      <p class="lede">We sweat the details so you don&rsquo;t need to.</p>
    </div>
    <div class="diagram">
      <ol class="points left" aria-label="Details, part one">
        <li class="point"><span class="num" aria-hidden="true">1</span><h3>Quality first</h3><p>Sun-grown craft flower from hundreds of farms. Only the best gets in.</p></li>
        <li class="point"><span class="num" aria-hidden="true">2</span><h3>Always blended</h3><p>A purposeful blend inside: terpene diversity, flavor, balance.</p></li>
      </ol>
      <figure class="diagram-figure">
        <picture><source type="image/webp" srcset="img/preroll-560.webp 560w, img/preroll-900.webp 900w" sizes="(max-width: 900px) 340px, 420px">
          <img src="img/preroll-700.png" alt="A Lowell pre-roll beside its glass travel tube and a Lowell matchbook" loading="lazy" decoding="async" width="700" height="700"></picture>
        <span class="pin-mark" style="left:52%;top:30%" aria-hidden="true">1</span>
        <span class="pin-mark" style="left:52%;top:55%" aria-hidden="true">2</span>
        <span class="pin-mark" style="left:56%;top:79%" aria-hidden="true">3</span>
        <span class="pin-mark" style="left:23%;top:40%" aria-hidden="true">4</span>
      </figure>
      <ol class="points" start="3" aria-label="Details, part two">
        <li class="point"><span class="num" aria-hidden="true">3</span><h3>A better smoke</h3><p>Engineered draw, even burn. You will never lose a cherry.</p></li>
        <li class="point"><span class="num" aria-hidden="true">4</span><h3>Ready and able</h3><p>Travel-ready tube, matches included. Prepared beats lucky.</p></li>
      </ol>
    </div>
  </div>
</section>

<section class="section sand" id="shop" aria-labelledby="shop-h">
  <div class="container">
    <div class="sect-head row">
      <span class="eyebrow red">The Farm Store</span>
      <h2 class="h2" id="shop-h">Timeless goods. No gimmicks.</h2>
      <p class="lede">Our own shop: Lowell-designed goods, made to our spec and shipped by us, direct to your door, nationwide. It&rsquo;s the only place we sell direct.</p>
      <a class="link-arrow" href="shop.html">Shop all {len(PRODUCTS)}</a>
    </div>
    <div class="products">{"".join(pcard(BY_SLUG[s]) for s in home6)}</div>
  </div>
</section>

<section class="section" id="pack" aria-labelledby="pack-h">
  <div class="container">
    <div class="pack">
      <figure class="pack-figure">
        <div class="arch">{pic("pack-tray", [640, 1000], "An open Lowell Smokes pack: the tray of six pre-rolls slid out, emergency matches in the top slot, the magnetic flap behind", "(max-width: 900px) 90vw, 460px", jpg=1000)}</div>
        <span class="pin-mark" style="left:24%;top:9%" aria-hidden="true">1</span>
        <span class="pin-mark" style="left:40%;top:60%" aria-hidden="true">2</span>
        <span class="pin-mark" style="left:74%;top:21%" aria-hidden="true">3</span>
        <span class="pin-mark" style="left:9%;top:31%" aria-hidden="true">4</span>
      </figure>
      <div>
        <span class="eyebrow red">The Pack</span>
        <h2 class="h2" id="pack-h" style="margin-top:var(--s4)">Lighting up is a ritual. We built the box for it.</h2>
        <p class="lede" style="margin-top:var(--s4)">Flip open the flap, slide out the tray and there&rsquo;s your stash, with emergency matches alongside. Every box is wax-lined to hold the right moisture for our pre-rolls.</p>
        <ol class="feats">
          <li class="feat"><span class="pin-mark" aria-hidden="true">1</span><h3>The magnetic flap</h3><p>The signature closure: sturdy, organic packaging that&rsquo;s ready for any outdoor adventure.</p></li>
          <li class="feat"><span class="pin-mark" aria-hidden="true">2</span><h3>The slide-out tray</h3><p>Pull the tray and your pre-rolls sit in a row, like the good silverware.</p></li>
          <li class="feat"><span class="pin-mark" aria-hidden="true">3</span><h3>Emergency matches</h3><p>Every pack ships with them. Prepared beats lucky.</p></li>
          <li class="feat"><span class="pin-mark" aria-hidden="true">4</span><h3>The wax liner</h3><p>Holds the moisture, so the last smoke in the pack is as fresh as the first.</p></li>
        </ol>
      </div>
    </div>
    <div class="film">
      <video controls muted playsinline preload="none" poster="img/farm-to-pack-poster.webp" aria-describedby="film-d">
        <source src="img/farm-to-pack-v2.mp4" type="video/mp4">
      </video>
      <div class="copy">
        <span class="eyebrow red">From the farm</span>
        <h3 class="h3">Greenhouse to sealed tray.</h3>
        <p class="small" id="film-d">Clones potted, plants grown and hung to dry, flower trimmed and weighed, cones filled, and every pre-roll set into its tray by hand. Silent film, 41 seconds.</p>
      </div>
    </div>
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
      <div class="map-stats"><div><b>8</b><span>states</span></div><div><b>700+</b><span>licensed shops</span></div><div><b>1</b><span>standard</span></div></div>
    </div>
    <div class="usmap-wrap">{usmap}</div>
  </div>
</section>

<section class="people on-ink" aria-labelledby="people-h">
  <div class="people-img">
    <picture><source type="image/webp" srcset="img/people-720.webp 720w, img/people-1000.webp 1000w, img/people-1400.webp 1400w" sizes="(max-width: 760px) 100vw, 50vw">
      <img src="img/people-1000.jpg" alt="Three friends laughing on hay bales at a Lowell farm party, one in a Lowell denim jacket" loading="lazy" decoding="async" width="1000" height="1250"></picture>
  </div>
  <div class="people-copy">
    <div class="copy">
      <span class="eyebrow">The whole point</span>
      <h2 class="h2" id="people-h">Bring people together.</h2>
      <p>That&rsquo;s the whole mission: the best and most distinctive American-grown products, made to be shared.</p>
      <a class="btn line" href="shop.html">Shop the Farm Store</a>
    </div>
  </div>
</section>

<section class="section" id="journal" aria-labelledby="journal-h">
  <div class="container">
    <div class="sect-head">
      <span class="eyebrow red">The Journal</span>
      <h2 class="h2" id="journal-h">Letters from the farm.</h2>
    </div>
    <div class="jcards">
      <article class="jcard"><div class="im">{pic("journal-farm", [480, 960], "A greenhouse aisle between rows of cannabis plants in warm light", "(max-width: 900px) 92vw, 30vw")}</div>
        <span class="eyebrow red">Field notes</span><h3 class="h3">Farming cannabis</h3><p>George Allen on sun-grown flower, local farmers, and doing it the slow way.</p></article>
      <article class="jcard"><div class="im">{pic("journal-blend", [480, 960], "Freshly rolled Lowell pre-rolls spread across a sorting tray", "(max-width: 900px) 92vw, 30vw")}</div>
        <span class="eyebrow red">Craft</span><h3 class="h3">Why we blend</h3><p>Single strains are a gamble. Blends are a recipe. The case for terpene diversity.</p></article>
      <article class="jcard"><div class="im">{pic("journal-box", [480, 960], "A Lowell Smokes pack, its open tray of pre-rolls and the Signature Metal Ashtray on a wooden valet tray", "(max-width: 900px) 92vw, 30vw")}</div>
        <span class="eyebrow red">Design</span><h3 class="h3">The craft of the box</h3><p>Magnetic flap, wax liner, emergency matches: why the pack is engineered like the smoke.</p></article>
    </div>
  </div>
</section>

<section class="strip-wrap" aria-label="Photographs from the farm and the Farm Store" style="padding-bottom:var(--section)">
  <div class="strip" tabindex="0">
    <ul>
      <li><img src="img/film-canopy.webp" alt="Cannabis canopy under warm greenhouse lights" loading="lazy" decoding="async" width="540" height="720"></li>
      <li><img src="img/film-tee.webp" alt="A woman in a Lowell Smokes tee and waxed jacket among redwoods" loading="lazy" decoding="async" width="480" height="720"></li>
      <li><img src="img/film-leaf.webp" alt="A hand holding a single fan leaf up to the greenhouse roof" loading="lazy" decoding="async" width="1080" height="720"></li>
      <li><img src="img/film-pack.webp" alt="A Lowell Smokes pack, stone ashtray and three matches from above" loading="lazy" decoding="async" width="480" height="720"></li>
      <li><img src="img/film-prerolls.webp" alt="Pre-rolls being sorted by hand on the packing line" loading="lazy" decoding="async" width="540" height="720"></li>
    </ul>
  </div>
</section>

<section class="section sand press" aria-label="Press">
  <div class="container">
    <blockquote>&ldquo;Lowell is one of the most widely recognized names in American cannabis, with a trailblazing legacy.&rdquo;</blockquote>
    <ul class="press-names" aria-label="As featured in"><li>Forbes</li><li>Robb Report</li><li>Page Six</li><li>Newsweek</li></ul>
  </div>
</section>
</main>
"""
    out = head("Lowell Herb Co. · Great American Cannabis (v2 preview)",
               "Golden Hour v2: the new lowellherbco.com homepage, with the Farm Store and a store locator for all eight Lowell states.",
               "") + gate() + header("home") + body + footer() + tail()
    (OUT / "index.html").write_text(out)


# ---------------------------------------------------------------- shop
def page_shop():
    cats = [("apparel", "Apparel", "lowell-denim-jacket"), ("luggage", "Luggage", "wax-canvas-duffel-bag"),
            ("accessories", "Accessories", "bulls-head-metal-ashtray")]
    counts = {c: sum(1 for p in PRODUCTS if p["cat"].lower() == c) for c, _, _ in cats}
    tiles = "".join(
        f'<a class="cat" href="shop.html?c={c}#all" data-cat="{c}"><div class="im"><img src="img/p/{img}-640.webp" alt="" loading="lazy" width="640" height="640"></div>'
        f'<div class="label"><h2 class="h3">{label}</h2><span>{counts[c]} items</span></div></a>' for c, label, img in cats)
    order = {"Apparel": 0, "Luggage": 1, "Accessories": 2}
    prods = sorted(PRODUCTS, key=lambda p: (not p["avail"], order[p["cat"]], -p["price"]))
    grid = "".join(pcard(p, "(max-width: 760px) 46vw, (max-width: 1000px) 30vw, 22vw").replace('<a class="pcard', f'<a data-cat="{p["cat"].lower()}" class="pcard', 1) for p in prods)
    chips = f'<button class="chip" type="button" data-filter="all" aria-pressed="true">All <span class="mono">{len(PRODUCTS)}</span></button>' + "".join(
        f'<button class="chip" type="button" data-filter="{c}" aria-pressed="false">{label} <span class="mono">{counts[c]}</span></button>' for c, label, _ in cats)
    body = f"""<main id="main">
<section class="page-head" aria-labelledby="shop-h">
  <div class="container">
    <p class="crumbs"><a href="index.html">Home</a> / Farm Store</p>
    <span class="eyebrow red">The Farm Store</span>
    <h1 class="display" id="shop-h">Timeless goods. No&nbsp;gimmicks.</h1>
    <p class="lede">Lowell-designed goods, made to our spec and shipped by us, direct to your door, nationwide. Nothing here contains cannabis.</p>
  </div>
</section>
<section class="section shop-cats" aria-label="Shop by category">
  <div class="container"><div class="cats">{tiles}</div></div>
</section>
<section class="section sand" id="all" aria-labelledby="all-h">
  <div class="container">
    <h2 class="sr-only" id="all-h">All goods</h2>
    <div class="shop-bar" role="group" aria-label="Filter by category">{chips}<span class="count" id="shop-count" aria-live="polite">{len(PRODUCTS)} goods</span></div>
    <div class="products four" id="shop-grid">{grid}</div>
    <div class="notice" style="margin-top:var(--s7)"><span aria-hidden="true">&#9432;</span><p><strong>Preview.</strong> Products and prices are the live Farm Store catalog (lowell-farms.myshopify.com, 23 Sep 2026). Product pages, sizes and checkout come with the Shopify theme build.</p></div>
  </div>
</section>
</main>
"""
    out = head("Farm Store · Lowell Herb Co. (v2 preview)", "Lowell-designed apparel, waxed-canvas luggage and smoke accessories, shipped direct.",
               "shop.html") + gate() + header("shop") + body + footer() + tail()
    (OUT / "shop.html").write_text(out)


# ---------------------------------------------------------------- product placeholder
def page_product():
    data = json.dumps({p["slug"]: {"t": p["title"], "p": money(p), "c": p["cat"], "a": p["avail"]} for p in PRODUCTS}, separators=(",", ":"))
    body = f"""<main id="main">
<section class="section">
  <div class="container">
    <p class="crumbs" style="margin-bottom:var(--s6)"><a href="index.html">Home</a> / <a href="shop.html">Farm Store</a> / <span id="pd-crumb">Product</span></p>
    <div class="pdp">
      <div class="im"><img id="pd-img" src="img/p/lowell-denim-jacket-640.webp" alt="" width="640" height="640"></div>
      <div class="info">
        <span class="eyebrow red" id="pd-cat">Farm Store</span>
        <h1 class="h2" id="pd-title">Product</h1>
        <p class="price" id="pd-price"></p>
        <div><button class="btn" type="button" disabled aria-disabled="true" style="opacity:.55;cursor:not-allowed">Add to cart</button></div>
        <div class="notice"><span aria-hidden="true">&#9432;</span><p><strong>Placeholder page.</strong> Product detail, sizes, photos and checkout come with the Shopify theme build. This page only confirms the Farm Store links resolve.</p></div>
        <a class="link-arrow" href="shop.html">Back to the Farm Store</a>
      </div>
    </div>
  </div>
</section>
</main>
<script type="application/json" id="catalog">{data}</script>
"""
    out = head("Product · Farm Store · Lowell Herb Co. (v2 preview)", "Farm Store product placeholder.", "product.html") + gate() + header("shop") + body + footer() + tail()
    (OUT / "product.html").write_text(out)


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
      <label class="fl-toggle"><input type="checkbox" id="fl-stock" checked> In stock only</label></div>
    <div class="fl-reveal" id="fl-reveal" hidden></div>
    <div class="fl-list" id="fl-list"><div class="fl-loading">Loading stores&hellip;</div></div>
  </div>
  <div class="fl-mapwrap"><div id="fl-map" role="region" aria-label="Map of stores"></div></div>
</section>
<section class="section sand fl-key" aria-labelledby="key-h">
  <div class="container">
    <h2 class="h3" id="key-h">How to read the list</h2>
    <ul class="fl-keylist">
      <li><span class="kdot k-stock" aria-hidden="true"></span><div><b>In stock</b><p class="small">Listed on the shop&rsquo;s own online menu today, at the shelf price that menu quotes.</p></div></li>
      <li><span class="kdot k-out" aria-hidden="true"></span><div><b>Listed, out today</b><p class="small">The shop carries Lowell but its menu shows none in stock right now.</p></div></li>
      <li><span class="kdot k-ship" aria-hidden="true"></span><div><b>Carries Lowell &middot; shipped &lt;date&gt;</b><p class="small">We delivered to this shop on that date. No live menu feed, so no stock or price: call ahead.</p></div></li>
      <li><span class="kdot k-partner" aria-hidden="true"></span><div><b>Partner-reported</b><p class="small">From our retail partner&rsquo;s monthly report. Placed by city, not street address. No price shown.</p></div></li>
    </ul>
  </div>
</section>
</main>
"""
    scripts = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>\n'
               f'<script src="assets/find.{VER}.js"></script>\n')
    out = head("Find Lowell · Store locator · Lowell Herb Co. (v2 preview)",
               "Find licensed dispensaries carrying Lowell pre-rolls near you, in California, Colorado, New Mexico, Missouri, Illinois, Ohio, New York and New Jersey.",
               "find.html", extra) + gate() + header("find") + body + footer() + tail(scripts)
    (OUT / "find.html").write_text(out)


def assets():
    a = OUT / "assets"
    a.mkdir(exist_ok=True)
    for old in list(a.glob("site.*.css")) + list(a.glob("site.*.js")) + list(a.glob("find.*.js")):
        old.unlink()
    shutil.copy(SRC / "site.css", a / f"site.{VER}.css")
    shutil.copy(SRC / "site.js", a / f"site.{VER}.js")
    shutil.copy(SRC / "find.js", a / f"find.{VER}.js")


if __name__ == "__main__":
    assets()
    page_home(); page_shop(); page_product(); page_find()
    print("built", VER, sorted(p.name for p in OUT.glob("*.html")))
