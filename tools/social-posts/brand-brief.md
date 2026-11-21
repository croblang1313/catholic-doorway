# Brand Brief: Catholic Doorway

> Captured: 2026-11-19 (drafted by Claude from the project's settled facts; Christopher can edit any line)
> Read by the brand-brief, content-coach, post-writer, post-grader, viral-hooks and repurpose skills.
> Where a skill's default disagrees with **House Rules** below, the House Rules win.

## Business
CatholicDoorway.com: a free, all-in-one guide to the Catholic faith. Prayers, the Bible, daily readings,
a map of Catholic churches, OCIA (becoming Catholic) guides, saints, the Church calendar, devotions,
Catholic terms, and how-to guides for the sacraments. English, Spanish, Portuguese and Filipino. No ads, no paywall, no sign-up.

## Customer
Two real people:
- **Maria, 34**: raised Catholic, drifted away, now has a toddler and wonders about Baptism and going back to Mass. Scrolls Facebook and Instagram at night. Afraid of being judged for being away.
- **Jake, 27**: not Catholic, dating a Catholic or just curious after a funeral Mass or a video about the saints. Wants plain answers without a sales pitch. On X, TikTok and Instagram.

## Primary CTA
Visit the website: open the page on catholicdoorway.com that the post is about.

## Strong Opinion / Wedge
You don't need to have it all figured out to walk through the door. The Church is a home, not a test.
(Gentle myth-busting about what Catholics actually believe and do is the "contrarian" fuel. Example:
"Most people think Catholics pray *to* statues. Here's what's really happening.")

## Story Vault
- 2026-11-17: the site launched with about 14,600 Catholic churches on the map and every U.S. diocese (204).
- The homepage verse: "I am the door; if any one enters by me, he will be saved." (John 10:9, RSV-CE)
- The Stations of the Cross walk-through has 16 original illustrated scenes.
- Free in 4 languages: English, Spanish, Portuguese and Filipino.
- Facts and numbers used in posts must be true and checkable on the site. Never invent a story, a convert, a
  reader, a quote, or a statistic.

## Voice
Warm and personal, plain-spoken, reverent. "A friendly parishioner at the door holding it open for you."
5 words: welcoming, clear, faithful, hopeful, unhurried.

## House Rules (these win over any skill default)
1. **Drafts only.** Nothing posts until Christopher approves it on social.catholicdoorway.com.
2. **Faithful to Catholic teaching.** No politics, no partisan or culture-war takes, no criticizing other
   churches, religions, clergy or people. Polarity means gentle myth-busting about Catholic belief, never a fight.
3. **Scripture in RSV-CE wording only**, short quotes, with the reference.
4. **One caption goes to Facebook, Instagram, X and TikTok**, so: at most 270 characters (X limit), it ends with a
   catholicdoorway.com link to a page that exists, plus 1 or 2 hashtags. (This overrides the skills'
   per-platform hashtag and no-link advice.)
5. **No engagement bait**: no "comment YES", "like if", "share or else". Soft asks are fine:
   "Save this for Sunday", "Send this to someone who's been away", "Which saint is yours?"
6. **No fear, shame or urgency hooks** ("You're doing Mass wrong", "Stop praying like this"). The
   Negative Frame and Urgency categories become invitations: "3 things nobody tells you before your first Mass".
7. Hooks in the Confession, Receipt or Stolen Lessons categories must be true of the site or of the Church's
   own history. Don't write "I" as if Christopher said something he didn't.
8. Universal voice rules from the skills apply: contractions, active voice, "you", numbers as digits,
   **no em dashes**, one idea per post, no filler words.
9. Image text (the 1080x1350 card) carries the hook or title; the caption carries the hook again plus the
   link. Keep image body under about 160 characters.
10. Grade every draft with post-grader. Aim for 8/10 or better, but never break a House Rule to raise a score.

## Weekly article (added 2026-11-21, Christopher approved)
Every Monday run also writes ONE "This Week in the Church" article for the website, before the posts.
1. Read /mnt/project-files/social-posts/articles/README.md and follow its writing rules exactly (seed/ has 3 examples).
2. Save it as weeks/<monday-date>/article.json and check it with
   `python3 /mnt/project-files/social-posts/articles/post_article.py article.json --dry-run`.
3. Make one of the week's 3 posts (the one nearest the feast) about the article. Its caption links to
   https://catholicdoorway.com/this-week/<slug>, and in plan.json it carries `"article": "article.json"`.
   send_drafts.py then sends the article draft first and puts its review link in that post's coach notes.
4. In the final summary, list the article title and its review link first. Christopher taps "Publish now"
   there (or uses https://catholicdoorway.com/this-week/review) before approving the post.
