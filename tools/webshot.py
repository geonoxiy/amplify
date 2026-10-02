#!/usr/bin/env python3
"""Real, sharp screenshots of a live website at a device's exact screen size, for mockup.py.

The page is laid out at the device's default scaled resolution and captured at its pixel density (MacBook Air 13:
1470x956 CSS px at 2x = 2940x1912 px; iPhone 15: 393 px wide at 3x = 1179 px, as a phone, so the site serves its
mobile layout), so the site wraps, crops and sizes its text exactly as it would on that device. It is the real site,
never a redrawn version. mockup.py later maps this rectangle onto the display with the same aspect ratio, so nothing
is stretched or squeezed.

Usage:
  webshot.py <url> --out <file.png> [--device air13] [--fullscreen] [--scroll <css px> | --at "<css selector>"]
             [--full <full-page.png>] [--hide "<css selector>" …] [--keep-popups] [--scale 4] [--wait 1.5] [--dark]

  --fullscreen  macOS full-screen on a notch MacBook: the page sits under a black menu-bar strip (mockup.py adds the strip)
  --scroll/--at show a section further down the page instead of the top
  --full        also save the whole page, top to bottom, at the same width (to pick other sections from later)
  --hide        hide extra elements by CSS selector. Common cookie banners are always hidden (never accepted), and small
                floating boxes below the header (chat bubbles, promo cards) are hidden unless --keep-popups
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mockup import DEVICES  # noqa: E402

IOS_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
          "Version/18.5 Mobile/15E148 Safari/604.1")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/151.0.0.0 Safari/537.36")
# hidden with CSS, never clicked: a banner is a consent prompt, and accepting it is the visitor's call, not ours
CONSENT = ["#onetrust-banner-sdk", "#onetrust-consent-sdk", "#CybotCookiebotDialog", "#usercentrics-root", ".osano-cm-window",
           "#truste-consent-track", "#didomi-host", ".qc-cmp2-container", "#cookie-law-info-bar", ".cky-consent-container",
           "#termly-code-snippet-support", "#shopify-pc__banner", ".cc-window", "#cookiescript_injected", "#cmpbox",
           "[aria-label='cookieconsent']", "#hs-eu-cookie-confirmation", "#iubenda-cs-banner", ".fc-consent-root"]
SETTLE_JS = """async (stepPause) => {
  const h = () => Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
  for (let y = 0, i = 0; y < h() && i < 40; y += window.innerHeight * 0.8, i++) {
    window.scrollTo(0, y); await new Promise(r => setTimeout(r, stepPause));
  }
  window.scrollTo(0, 0);
  await document.fonts.ready;
}"""
# floating extras that are not the page itself: chat bubbles, promo cards, bottom bars, consent banners (also inside
# shadow DOM, where some consent tools live). Fixed/sticky boxes that sit below the top 12% of the window and cover
# under 35% of it (60% if they mention cookies). A fixed header at the top is part of the site and stays.
POPUPS_JS = """() => {
  const out = [], vw = innerWidth, vh = innerHeight, all = [];
  const collect = root => { for (const el of root.querySelectorAll('*')) { all.push(el); if (el.shadowRoot) collect(el.shadowRoot); } };
  collect(document.body);
  for (const el of all) {
    const cs = getComputedStyle(el);
    if (cs.position !== 'fixed' && cs.position !== 'sticky') continue;
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2 || r.top < vh * 0.12) continue;
    const cookie = /cookie|consent/i.test(el.innerText || '');
    if ((r.width * r.height) / (vw * vh) > (cookie ? 0.6 : 0.35)) continue;
    if (cs.position === 'sticky' && r.bottom < vh - 2) continue;
    el.style.setProperty('display', 'none', 'important');
    out.push((el.id ? '#' + el.id : el.tagName.toLowerCase() + (typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\\s+/)[0] : ''))
             + ` ${Math.round(r.width)}x${Math.round(r.height)} at ${Math.round(r.left)},${Math.round(r.top)}` + (cookie ? ' (cookie notice)' : ''));
  }
  return out;
}"""
IMAGES_JS = """async () => {
  const vis = [...document.images].filter(i => { const r = i.getBoundingClientRect();
    return r.bottom > 0 && r.top < innerHeight && r.width > 0; });
  await Promise.race([Promise.all(vis.map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; }))),
                      new Promise(r => setTimeout(r, 8000))]);
  await Promise.all(vis.map(i => i.decode ? i.decode().catch(() => 0) : 0));
}"""


def shoot(url, out, device="air13", fullscreen=False, scroll=0, at=None, full=None, hide=(), wait=1.5, dark=False,
          keep_popups=False, scale=None):
    """scale: pixel density override. The layout (CSS size) never changes; a higher density only renders the same
    page sharper, for a template whose screen has more pixels than the device itself."""
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    dev = DEVICES[device]
    cw, ch = dev["css"]
    phone = dev["kind"] == "phone"
    if phone:  # the page sits below the iOS status bar; mockup.py draws the bar and Safari's bottom bar around it
        ch -= dev["status_bar"]
        fullscreen = False
    elif fullscreen:
        ch -= dev["menubar"]
    css = ("html{scrollbar-width:none!important} ::-webkit-scrollbar{display:none!important} "
           + ",".join(CONSENT + list(hide)) + "{display:none!important;visibility:hidden!important}")
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": cw, "height": ch}, device_scale_factor=scale or dev["dpr"],
                                  user_agent=IOS_UA if phone else UA, is_mobile=phone, has_touch=phone,
                                  locale="en-US", color_scheme="dark" if dark else "light")
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except PWTimeout:
            pass  # sites with analytics beacons or live chat never go idle; the scroll pass below still loads images
        page.add_style_tag(content=css)
        page.evaluate(SETTLE_JS, 250)  # one pass down the page: lazy images load, scroll-reveal sections play
        if at:
            page.locator(at).first.scroll_into_view_if_needed()
            page.evaluate("sel => { const r = document.querySelector(sel).getBoundingClientRect(); window.scrollBy(0, r.top); }", at)
        elif scroll:
            page.evaluate("y => window.scrollTo(0, y)", scroll)
        page.evaluate(IMAGES_JS)
        page.wait_for_timeout(int(wait * 1000))
        hidden = [] if keep_popups else page.evaluate(POPUPS_JS)
        for h in hidden:
            print(f"  hid floating element {h}  (--keep-popups to keep)")
        page.screenshot(path=str(out), animations="disabled", caret="hide", scale="device")
        title = page.title()
        y = page.evaluate("window.scrollY")
        if full:
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(300)
            page.screenshot(path=str(full), full_page=True, animations="disabled", caret="hide", scale="device")
        browser.close()
    from PIL import Image, ImageStat
    im = Image.open(out)
    side = {"url": url, "title": title, "device": device, "fullscreen": fullscreen, "css_viewport": [cw, ch], "dpr": scale or dev["dpr"],
            "scroll_y": y, "size": list(im.size), "hidden_popups": hidden, "taken": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    out.with_suffix(".json").write_text(json.dumps(side, indent=1))
    if max(ImageStat.Stat(im.convert("L")).stddev) < 6:
        print(f"warning: {out.name} is almost one flat colour; the site may have blocked the capture or not rendered")
    if any(s in title.lower() for s in ("just a moment", "access denied", "attention required", "verify you are human")):
        print(f"warning: page title {title!r} looks like a bot check, not the site itself")
    print(f"{out}  {im.size[0]}x{im.size[1]}  ({device}{', fullscreen' if fullscreen else ''}, scrollY {y}, {title!r})")
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("url")
    p.add_argument("--out", required=True)
    p.add_argument("--device", default="air13", choices=DEVICES)
    p.add_argument("--fullscreen", action="store_true")
    p.add_argument("--scroll", type=int, default=0)
    p.add_argument("--at")
    p.add_argument("--full")
    p.add_argument("--hide", nargs="*", default=[])
    p.add_argument("--wait", type=float, default=1.5)
    p.add_argument("--dark", action="store_true")
    p.add_argument("--keep-popups", action="store_true")
    p.add_argument("--scale", type=float, help="pixel density override (same layout, sharper), e.g. 4")
    a = p.parse_args()
    shoot(a.url, a.out, a.device, a.fullscreen, a.scroll, a.at, a.full, a.hide, a.wait, a.dark, a.keep_popups, a.scale)


if __name__ == "__main__":
    main()
