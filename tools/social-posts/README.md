# Social Posts (catholicdoorway-social Worker)

Private posting page at https://social.catholicdoorway.com. Write a post once, preview it, approve it.
Facebook (and Instagram once linked) post through Meta's Graph API; X and TikTok finish from a phone's share button.

This is Social Posts 1.0.0 trimmed for Catholic Doorway: only Facebook, Instagram, X and TikTok,
gold accent, links to catholicdoorway.com, and an optional `post_on` date (YYYY-MM-DD) on drafts,
shown as "planned for ..." in the list.

It is a separate Worker from the website. Nothing in `site/` uses it.

- Edit `src/server.js` / `src/app.html`, then `cd src && python3 build.py` to rebuild `worker.js`.
- Deploy by uploading `worker.js` to the `catholicdoorway-social` Worker (KV binding `SOCIAL`,
  secrets `ADMIN_PASSWORD`, `SESSION_SECRET`, `DRAFTS_TOKEN`, text var `SITE_NAME`).
- Drafts API: `POST /api/media` (raw JPEG) then `POST /api/drafts` with
  `{"kind":"photo","platforms":[...],"media":[key],"caption":"...","post_on":"2026-11-23"}`,
  both with `Authorization: Bearer <DRAFTS_TOKEN>`.

## Coach notes (1.1.0)

Drafts can carry an optional `coach` object from the posting skills (content-coach, post-writer,
post-grader, viral-hooks, repurpose, brand-brief): score, hook pattern, why it works, scorecard,
fixes, and up to 3 alternate captions. The draft page shows it as "Coach notes" with a
"Use this version" button that swaps an alternate in (the old text is kept as an alternate).
Editing the text by hand keeps the notes and marks the score as being for the earlier wording.
`brand-brief.md` holds the voice and the House Rules; the House Rules win over skill defaults.

License: GPL-2.0-or-later.
