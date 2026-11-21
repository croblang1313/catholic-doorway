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

Approved listings also appear on the church map (`site/assets/js/map.js` matches them to churches by parish name and city), including any **Mass and Confession times** the parish sends in the `masses` field.

### Prayer Wall

`/prayer-wall` (es `/es/muro-de-oracion`, pt `/pt/mural-de-oracao`, tl `/tl/mga-kahilingang-panalangin`) lets visitors ask for prayer with a first name or anonymously, and tap **I prayed** on others' requests. The page comes from `src/prayerwall.py` and `site/assets/js/prayerwall.js`; the API is `worker/prayers.js`, stored in the same `LISTINGS` KV namespace.

- Nothing is shown until it is approved at `/api/prayer-admin` (same `ADMIN_TOKEN` password). You can edit the name and text before publishing, to take out last names or private details. Requests that may mention self-harm are flagged at the top.
- "Keep it private" requests are never published; they appear in their own list on the review page for the team to pray for.
- Every request expires 30 days after it was sent (KV deletes it). Spam protection: hidden honeypot field, a 3-second minimum, 3 requests per IP per hour, and no links, emails or phone numbers.
- "I prayed" counts once per visitor per request per day (two KV writes each; the free plan allows 1,000 writes a day).

### Site search, seasons and the Bible reader

- `src/searchindex.py` builds `site/data/search-<lang>.json` from the finished pages on every build; `site/assets/js/search.js` runs the search at `/search` (es `/buscar`, pt `/buscar`, tl `/maghanap`). Any heading or card with an `id` becomes its own result.
- `src/seasons.py` fills `{{ADVENT_DATES}}` on the Advent pages and the seasonal `{{SEASON_BANNER}}` card on the home pages (shown by `main.js` from three weeks before Advent to the Baptism of the Lord). The weekly rebuild keeps the year current.
- `/read-the-bible` reads the Douay-Rheims Bible (Challoner revision, public domain) from `site/data/bible/drb/`, made once by `scripts/make_bible.py` from the scrollmapper/bible_databases `DRC.json`.

### Prayer reminders

`/api/devotions.ics?set=angelus12,angelus6,mercy,stations,novenas&lang=en|es|pt` is a subscribable calendar (see `worker/devotions.js`). Novena dates come from `src/data/novenas.json`; the build writes `worker/novenas-data.js` from it, so rebuild after editing.

## Data and licensing

- Church locations come from OpenStreetMap (ODbL). `scripts/fetch_churches.py`, run weekly by `.github/workflows/churches.yml`, saves them to `site/data/churches/` so the map loads instantly; it falls back to the live Overpass API only if that copy is missing, with geocoding from Nominatim and map tiles from tile.openstreetmap.org. Nothing is scraped from MassTimes.org or other directories. If traffic grows, move tiles to a provider with a free tier (OSM's tile usage policy asks heavy users to do so).
- Scripture quotations: RSV, Second Catholic Edition (used within the NCC's permission for short quotations). Daily readings link to the USCCB rather than copying the NABRE. The full Bible reader uses the public-domain Douay-Rheims.
- Leaflet is bundled under its BSD-2 license (`site/assets/vendor/leaflet/LICENSE`).
