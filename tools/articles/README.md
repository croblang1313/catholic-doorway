# This Week in the Church: weekly articles

One short article a week on the coming week's feast, saint or season, published at
`https://catholicdoorway.com/this-week/<slug>`. Claude writes it every Monday with the social drafts;
Christopher reads it and publishes it with one tap. Nothing goes live without him.

## How it works

- Articles are stored in the site's KV namespace (`LISTINGS`), not in the repo, so publishing needs
  no rebuild. `worker/articles.js` serves the index, each article, RSS (`/this-week/feed.xml`) and a
  sitemap (`/sitemap-articles.xml`, listed in robots.txt). Pages reuse the built `/this-week` page for
  the header, menu, footer and verse banner, and carry Article structured data.
- `post_article.py article.json` leaves a draft. Christopher reviews it in the **Articles tab of
  Social Posts** (https://social.catholicdoorway.com/#articles): Read the preview, Publish on the
  website, Unpublish, Delete draft. That tab calls `GET /api/articles/all` and
  `POST /api/articles/action` on the site with the Social Posts DRAFTS_TOKEN.
- Backups: each draft's private review link (printed by the script) has a Publish button, and
  `https://catholicdoorway.com/this-week/review` lists everything with the site's ADMIN_TOKEN.
- In a weekly social plan, a post with `"article": "article.json"` sends the article first and its
  coach notes remind Christopher to publish the article in the Articles tab before approving the post.
- The drafts token is the Social Posts `DRAFTS_TOKEN`. The site keeps only its SHA-256
  (`ARTICLE_DRAFTS_SHA256` in wrangler.jsonc). It can leave drafts, never publish. A published article
  can't be overwritten by a draft; unpublish it in the Articles tab first.
- The weekly job never publishes. Only Christopher does.
- **Share picture and PDF.** Every draft carries a 1200x630 share picture and a PDF copy, both made by
  `post_article.py` (the PDF with `make_article_pdf.js`). The picture is the matching post's design at
  link-preview size, so a shared article shows the same graphic as the social post; it is what
  Facebook, X, WhatsApp and Pinterest show (og:image / twitter:image). The article page has share
  buttons (Facebook, X, WhatsApp, Pinterest, Email, Copy link, and the phone's share sheet) and a
  **Download PDF** button. To redo them on a live article: `post_article.py --attach article.json`.

## Writing rules (follow these every week)

The House Rules in `/mnt/project-files/social-posts/brand-brief.md` apply here too. In particular:

1. **Pick the week's most important day** from Sunday to Saturday after the Monday it is written:
   a solemnity or holy day first, then the Sunday, then a feast, a well-known saint or the season.
   Check the date and rank against the U.S. calendar (`/api/calendar.json`, the site's
   `src/seasons.py`), and the Sunday readings against the USCCB lectionary for that year's cycle.
2. **Faithful and checkable.** Only what the Church teaches. Cite the Catechism by paragraph and
   Scripture by reference. Quote Scripture only in RSV-CE wording, and only verses you are sure of;
   otherwise paraphrase. Never invent quotes, stories, statistics or readers. If a historical detail
   can't be verified, leave it out.
3. **No politics**, no criticism of other churches, religions, clergy or people.
4. **Plain and warm.** Written for Maria (drifted away) and Jake (curious, not Catholic). Explain
   every churchy word or link it to `/glossary`. Contractions, "you", active voice, numbers as digits,
   **no em dashes**.
5. **Shape:** 700 to 1,100 words. An opening that answers the title in 2 or 3 sentences, then
   `h2` sections: what it is, where it comes from, what the Church teaches (with a `blockquote
   class="ccc"` or `class="scripture"` and a `cite`), this year's details (dates, readings), how to
   keep it (a short list of concrete things), and a closing note for someone exploring the faith.
6. **Titles people search for:** "What Is ...?", "Why Do Catholics ...?", under 70 characters.
   Slug is short and evergreen (no year), e.g. `what-is-the-epiphany`. Check
   `https://catholicdoorway.com/this-week` so a slug or topic isn't repeated; next year's article on
   the same feast takes a new angle and a new slug.
7. **Link 3 to 6 site pages** in the body and in `related` (only pages that exist: /advent,
   /calendar, /prayers, /rosary, /reading-plans, /confession, /first-mass, /start-here, /saints,
   /glossary, /beliefs, /questions, /find-a-church, /watch-mass, /devotions, /liturgy-of-the-hours,
   /stations-of-the-cross, /examination-of-conscience, and so on).
8. **Verse banner:** one short RSV-CE verse that fits the feast.
9. **Sources:** the Catechism paragraphs, documents and readings used, with vatican.va or usccb.org
   links only when you are sure of the address (`https://www.vatican.va/archive/ENG0015/_INDEX.HTM`
   for the Catechism).
10. Make the week's matching social post link to the article, and send it with `"article"` in the plan.

`seed/` holds the first three articles (Christ the King, Advent, the Immaculate Conception) as
examples of the shape and tone.
