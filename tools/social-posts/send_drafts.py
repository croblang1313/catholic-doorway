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

"coach" is optional. It holds the post-writer / post-grader / viral-hooks results and shows as
"Coach notes" on the draft's page, where Christopher can swap in an alternate with one tap.
Follow /mnt/project-files/social-posts/brand-brief.md; its House Rules win over the skills' defaults.

The drafts token comes from $DRAFTS_TOKEN or the file named by $DRAFTS_TOKEN_FILE.
It can only upload media and create drafts; it cannot approve or post.
"""
import json, os, subprocess, sys, urllib.request

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
        if len(cap) > 280 and "x" in post.get("platforms", []):
            print(f"warning: post {i} is {len(cap)} characters, over X's 280")
        spec = os.path.join(out_dir, f"post{i}.json")
        img = os.path.join(out_dir, f"{post['post_on']}-post{i}.jpg")
        json.dump(post["image"], open(spec, "w"))
        subprocess.run(["node", os.path.join(HERE, "make_post_image.js"), spec, img], check=True)
        print("rendered", img)
        if dry:
            continue
        media = call("/api/media", open(img, "rb").read(), "image/jpeg", tok, {"X-Width": "1080", "X-Height": "1350"})
        draft = call("/api/drafts", json.dumps({
            "kind": "photo", "platforms": post.get("platforms", ["facebook", "instagram", "x", "tiktok"]),
            "media": [media["key"]], "caption": cap, "post_on": post["post_on"],
            **({"coach": post["coach"]} if post.get("coach") else {})}).encode(), "application/json", tok)
        print("draft", post["post_on"], draft.get("review_url"))
        with open(sent, "a") as f:
            f.write(f"{post['post_on']} {draft.get('review_url')}\n")


if __name__ == "__main__":
    main()
