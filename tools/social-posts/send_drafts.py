#!/usr/bin/env python3
"""Render and send a week's social drafts to https://social.catholicdoorway.com for approval.

Usage: python3 send_drafts.py plan.json [--dry-run]

A real send refuses to run if sent.txt is in the plan's folder, and writes
sent.txt as each draft is created, so a week is never sent twice.

plan.json is a list of posts:
  [{"post_on": "2026-11-23", "platforms": ["facebook","instagram","x","tiktok"],
    "caption": "Post text with link and hashtags",
    "image": {"kicker": "...", "title": "...", "body": "...", "ref": "...", "theme": "cream|navy"},
    "coach": {"score": 8.4, "hook": "Myth-Buster", "why": "One sentence on why it works.",
              "scorecard": [{"name": "Hook strength", "score": 8}, ...],
              "fixes": ["What would raise the score"],
              "alternates": [{"caption": "Another full version", "hook": "Question Hook", "score": 7.9}]}}]

"video" is optional: extra fields for the TikTok video (make_post_video.js), e.g.
    {"format": "reveal"|"kinetic"|"list"|"split"|"scripture", "hook": "Big first line, *gold* words",
     "path": "/saints", "art": "window"|"none", plus "lines" (kinetic), "items"/"list_title" (list),
     "quote" (scripture). See make_post_video.js. Use a different format for each post in a week and
    don't open a week with the format that closed the previous one.
When "tiktok" is in platforms, TikTok gets its own 11-second video draft (motion + original sound)
and the photo draft goes to the other platforms. Set "video": false to send TikTok the photo instead.

"article" is optional: a path (relative to plan.json) to a "This Week in the Church" article JSON
(see tools/articles/README.md). It is sent first as a draft on catholicdoorway.com. It shows in the Articles
tab of Social Posts, and the post's coach notes remind Christopher to publish it before approving the post.
The article also gets a PDF copy (its "Download PDF" button) and a share picture: the post's "image"
design rendered at 1200x630, with a background color that changes every week (post_article.week_theme). Give the post
"article_image" (same fields as "image") to use a different design for the article. The caption should link to https://catholicdoorway.com/this-week/<slug>. Until the article
is published, that address opens the This Week index, so the link never breaks.

"coach" is optional. It holds the post-writer / post-grader / viral-hooks results and shows as
"Coach notes" on the draft's page, where Christopher can swap in an alternate with one tap.
Follow /mnt/project-files/social-posts/brand-brief.md; its House Rules win over the skills' defaults.

The drafts token comes from $DRAFTS_TOKEN or the file named by $DRAFTS_TOKEN_FILE.
It can only upload media and create drafts; it cannot approve or post.
"""
import json, os, subprocess, sys, urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "articles"))

BASE = os.environ.get("SOCIAL_URL", "https://social.catholicdoorway.com")
HERE = os.path.dirname(os.path.abspath(__file__))


def token():
    t = os.environ.get("DRAFTS_TOKEN", "").strip()
    if not t and os.environ.get("DRAFTS_TOKEN_FILE"):
        t = open(os.environ["DRAFTS_TOKEN_FILE"]).read().strip()
    if not t:
        sys.exit("No drafts token: set DRAFTS_TOKEN or DRAFTS_TOKEN_FILE.")
    return t


def call(path, data, ctype, tok, extra=None):
    req = urllib.request.Request(BASE + path, data=data, method="POST",
                                 headers={"Authorization": "Bearer " + tok, "Content-Type": ctype, **(extra or {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main():
    plan = json.load(open(sys.argv[1]))
    dry = "--dry-run" in sys.argv
    week_dir = os.path.dirname(os.path.abspath(sys.argv[1]))
    sent = os.path.join(week_dir, "sent.txt")
    if not dry and os.path.exists(sent):
        sys.exit(f"already sent: {sent} exists, so these drafts are on the site already. Nothing done.")
    out_dir = os.path.join(week_dir, "images")
    os.makedirs(out_dir, exist_ok=True)
    tok = None if dry else token()
    for i, post in enumerate(plan, 1):
        cap = post["caption"].strip()
        plats = post.get("platforms", ["facebook", "instagram", "x", "tiktok"])
        if len(cap) > 280 and "x" in plats:
            print(f"warning: post {i} is {len(cap)} characters, over X's 280")
        # TikTok gets its own video draft (motion + sound); the photo draft goes everywhere else.
        video = "tiktok" in plats and post.get("video") is not False
        photo_plats = [p for p in plats if not (video and p == "tiktok")]
        if post.get("article"):
            import post_article
            share = os.path.join(out_dir, f"{post['post_on']}-article-share.jpg")
            art_json = json.load(open(os.path.join(week_dir, post["article"]), encoding="utf-8"))
            spec = {**(post.get("article_image") or post["image"]), "theme": post_article.week_theme(art_json)}
            post_article.render_share_image(spec, share)
            art = post_article.send(os.path.join(week_dir, post["article"]), dry, tok, image=share)
            if art.get("review_url"):
                coach = dict(post.get("coach") or {})
                coach["why"] = ("ARTICLE: publish \"" + art.get("title", "the article") + "\" first in the Articles tab. " + coach.get("why", ""))[:400]
                post["coach"] = coach
                with open(sent, "a") as f:
                    f.write(f"{post['post_on']} article {art['review_url']}\n")
        extra = {"caption": cap, "post_on": post["post_on"], **({"coach": post["coach"]} if post.get("coach") else {})}
        if photo_plats:
            spec = os.path.join(out_dir, f"post{i}.json")
            img = os.path.join(out_dir, f"{post['post_on']}-post{i}.jpg")
            json.dump(post["image"], open(spec, "w"))
            subprocess.run(["node", os.path.join(HERE, "make_post_image.js"), spec, img], check=True)
            print("rendered", img)
            if not dry:
                media = call("/api/media", open(img, "rb").read(), "image/jpeg", tok, {"X-Width": "1080", "X-Height": "1350"})
                draft = call("/api/drafts", json.dumps({"kind": "photo", "platforms": photo_plats, "media": [media["key"]], **extra}).encode(), "application/json", tok)
                print("draft", post["post_on"], draft.get("review_url"))
                with open(sent, "a") as f:
                    f.write(f"{post['post_on']} photo {draft.get('review_url')}\n")
        if video:
            vspec = os.path.join(out_dir, f"video{i}.json")
            mp4 = os.path.join(out_dir, f"{post['post_on']}-video{i}.mp4")
            json.dump({**post["image"], **(post.get("video") or {})}, open(vspec, "w"))
            subprocess.run(["node", os.path.join(HERE, "make_post_video.js"), vspec, mp4], check=True)
            print("rendered", mp4)
            if not dry:
                media = call("/api/media", open(mp4, "rb").read(), "video/mp4", tok, {"X-Width": "1080", "X-Height": "1920", "X-Filename": os.path.basename(mp4)})
                draft = call("/api/drafts", json.dumps({"kind": "video", "platforms": ["tiktok"], "media": [media["key"]], **extra}).encode(), "application/json", tok)
                print("draft", post["post_on"], "tiktok video", draft.get("review_url"))
                with open(sent, "a") as f:
                    f.write(f"{post['post_on']} tiktok-video {draft.get('review_url')}\n")

if __name__ == "__main__":
    main()
