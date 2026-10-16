# marginmail.ai

The public site for Margin: the homepage with the beta signup, comparison pages, guides, and the Privacy Policy and Terms. Static HTML served free by GitHub Pages. No frameworks, no npm, no analytics, no cookies, no third-party requests.

## Build

```sh
python3 _build/build.py     # writes the pages, images, sitemap.xml, robots.txt, llms.txt, llms-full.txt
python3 _build/check.py     # offline checks: HTML structure, links and anchors, headings, alt text, meta, JSON-LD, sitemap
python3 -m http.server 8000 # preview at http://localhost:8000 (the signup endpoint allows localhost)
```
Python standard library plus macOS `sips` (images). Commit the built files; Pages serves the repo root as is.

| Source | Becomes |
|---|---|
| `content/homepage.md` (copy lives in `_build/copy_home.py`) | `index.html` |
| `content/comparisons/*.md` | `compare/` and `compare/<slug>/` |
| `content/seo/pages/*.md` | `best/…/`, `guides/…/` (from each file's `url`) |
| `_build/legal/privacy.html`, `terms.html` (legal text, edit by hand) | `privacy/`, `terms/` |
| `assets/shots/` | `img/*.jpg` (resized; hero ≤ 250 KB) |
| `assets/motion/{stack,live-words,write-it}.*`, `brand/final/lockup/` | `motion/`, `img/brand/` |

Hand-written, not generated: `css/site.css`, `js/site.js` (forms, marks drawing on view, sticky Join bar, star easter egg, scroll-sky fallback), `fonts/` (Newsreader and Caveat, latin subset, OFL), favicons, `og/margin-og.png`.

Links to pages that don't exist yet (for example `/answers/`) are rendered as plain text and listed as warnings by the build. Add the page and rebuild, and the links appear.

`_config.yml` keeps `content/`, `docs/`, `waitlist/`, `tools/`, `brand/` and `assets/` from being published.

## Signup
Forms post to the waitlist endpoint (`waitlist/README.md`). `?r=` (or `?ref=`) is sent as the referral code; `?utm_source=`, `?src=` or `?s=` as the source. Search pages tag their own form with a source (for example `compare-spark`, `seo-follow-ups`). Referral links are `https://marginmail.ai/?r=<code>`. Without JavaScript the endpoint answers a form post with a 303 back to `/?joined=1&p=…&r=…#joined` (or `#already`, `#join-error`), and the page shows that state with `:target`.

Social cards: `python3 _build/og.py` renders `og/compare-*.png`, `og/guides-*.png` and `og/best-*.png` with headless Chrome; run it before `build.py` when titles change.

## Hosting
- GitHub Pages on repo `nmetric/marginmail-site`, branch `main`, root `/`. The custom domain is set by the `CNAME` file and in repo Settings → Pages.
- HTTPS: Let's Encrypt via GitHub. Turn on "Enforce HTTPS" in Settings → Pages once DNS resolves: `gh api -X PUT repos/nmetric/marginmail-site/pages -F https_enforced=true`.

## Domain and DNS
- Registrar and DNS: **GoDaddy** (account of bnowacky). Nameservers: `ns45/ns46.domaincontrol.com`. Registered 2026-10-12.

| Type | Name | Value | Purpose |
|---|---|---|---|
| A | @ | 185.199.108.153, .109.153, .110.153, .111.153 | GitHub Pages |
| CNAME | www | marginmail.ai. | www → apex |
| MX 10 | @ | mx1.forwardemail.net, mx2.forwardemail.net | Email forwarding |
| TXT | @ | `forward-email=<encrypted>` | Forwarding rule (encrypted) |
| TXT | @ | `v=spf1 include:spf.forwardemail.net -all` | SPF for forwarding |
| TXT | _dmarc | GoDaddy default (p=quarantine) | DMARC |

## Email: hello@marginmail.ai
- **Service:** Forward Email (forwardemail.net), free plan, no account. The whole setup is the DNS records above.
- **Current rule:** `hello@marginmail.ai` forwards to Ben's personal Gmail. The rule is encrypted in the TXT record so the destination isn't public.
- **To change or add an address:**
  1. Encrypt the new rule:
     ```
     curl -X POST https://api.forwardemail.net/v1/encrypt -d "input=hello:you@example.com"
     ```
     Several rules can go in one record, comma-separated (e.g. `hello:a@x.com,support:b@y.com`), or as separate `forward-email=` TXT records. A catch-all is just an address: `input=you@example.com`.
  2. Replace the `forward-email=…` TXT value in GoDaddy with the output.
- **Replies:** sending *as* hello@ from Gmail needs outbound SMTP, which is Forward Email's paid plan (about $3/month). It isn't set up; reply from your own address for now.
- **Upgrade path:** when Margin has a company and Google Workspace or Cloud Identity, replace the MX and SPF records with the provider's and remove the `forward-email` TXT.

## Google OAuth (margin-app-511419)
The consent screen's Branding page references `https://marginmail.ai`, `/privacy`, `/terms` and the authorized domain `marginmail.ai`. Keep these URLs working, or update Branding if they change.
