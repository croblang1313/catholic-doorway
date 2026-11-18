# CatholicDoorway.com

A free, ad-free guide to the Catholic faith: prayers, daily readings, becoming Catholic (OCIA), a church finder, beliefs, Church structure, dioceses, saints and a glossary.

> "I am the door; if any one enters by me, he will be saved." (John 10:9, RSV-CE)

## How it's built

Plain HTML, CSS and a little JavaScript. No framework, no build tools to install.

```
src/pages/*.html      page content (the middle of each page)
src/data/saints.json  saints list (shown on /saints)
src/data/glossary.json glossary terms (shown on /glossary)
src/build.py          wraps each page in the shared header, menu and footer
site/                 the finished website that Cloudflare Pages serves
site/assets/          styles, scripts, images and the Leaflet map library
```

To change content: edit a file in `src/pages` or `src/data`, then run

```
python3 src/build.py
```

and commit both `src/` and `site/`. (Styles and scripts in `site/assets/` are edited directly.)

## Hosting (Cloudflare Workers)

The `catholic-doorway` Worker is connected to this repo in Cloudflare. Every push to `main` redeploys it. `wrangler.jsonc` tells it to serve the files in `site/` as static assets; no build step is needed.

`site/_headers` sets security headers. `site/404.html` is the not-found page.

### Parish OCIA listings (one-time setup)

The OCIA listing form (`/ocia-listing`) saves submissions in Workers KV. Until this is set up, the form falls back to opening an email to hello@catholicdoorway.com, so nothing breaks.

1. In Cloudflare, go to Storage & Databases > Workers KV and create a namespace (for example `ocia-listings`). Copy its ID.
2. Add it to `wrangler.jsonc` under `kv_namespaces` with the binding `LISTINGS` (done: namespace `ocia_listings`).
3. In the `catholic-doorway` Worker, go to Settings > Variables and Secrets and add a **Secret** named `ADMIN_TOKEN` with a long random password.
4. Review submissions at `/api/ocia-admin` (enter that password). Approve, unpublish or delete there. Only approved listings appear on the site.

### Prayer reminders

`/api/devotions.ics?set=angelus12,angelus6,mercy,stations,novenas&lang=en|es|pt` is a subscribable calendar (see `worker/devotions.js`). Novena dates come from `src/data/novenas.json`; the build writes `worker/novenas-data.js` from it, so rebuild after editing.

## Data and licensing

- Church locations come from OpenStreetMap (ODbL). `scripts/fetch_churches.py`, run weekly by `.github/workflows/churches.yml`, saves them to `site/data/churches/` so the map loads instantly; it falls back to the live Overpass API only if that copy is missing, with geocoding from Nominatim and map tiles from tile.openstreetmap.org. Nothing is scraped from MassTimes.org or other directories. If traffic grows, move tiles to a provider with a free tier (OSM's tile usage policy asks heavy users to do so).
- Scripture quotations: RSV, Second Catholic Edition (used within the NCC's permission for short quotations). Daily readings link to the USCCB rather than copying the NABRE.
- Leaflet is bundled under its BSD-2 license (`site/assets/vendor/leaflet/LICENSE`).
