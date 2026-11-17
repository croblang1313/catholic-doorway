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

## Data and licensing

- Church locations come from OpenStreetMap via the Overpass API (ODbL), with geocoding from Nominatim and map tiles from tile.openstreetmap.org. Nothing is scraped from MassTimes.org or other directories. If traffic grows, move tiles to a provider with a free tier (OSM's tile usage policy asks heavy users to do so).
- Scripture quotations: RSV, Second Catholic Edition (used within the NCC's permission for short quotations). Daily readings link to the USCCB rather than copying the NABRE.
- Leaflet is bundled under its BSD-2 license (`site/assets/vendor/leaflet/LICENSE`).
