# marginmail.ai

The public "coming soon" site for Margin, with its Privacy Policy and Terms. It's static HTML served free by GitHub Pages.

## Pages
- `/` (`index.html`): logo, one-line blurb, "Coming soon", and links.
- `/privacy` (`privacy/index.html`): Privacy Policy. Google's OAuth consent screen links here.
- `/terms` (`terms/index.html`): Terms of Service. Also linked from the consent screen.
- `logo.png` and `favicon.png` are rendered from the app icon (`margin/Apps/Shared/Assets.xcassets/AppIcon.appiconset`).

To edit, change the HTML, commit and push to `main`. Pages redeploys within a minute or two.

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
