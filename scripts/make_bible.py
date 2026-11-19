"""Builds the on-site Douay-Rheims Bible (Challoner revision, public domain) from the
scrollmapper/bible_databases DRC.json file:

    python3 scripts/make_bible.py path/to/DRC.json

Writes site/data/bible/drb/books.json (names, Douay names, chapter counts) and one
file per book, site/data/bible/drb/<n>.json, holding a list of chapters, each a list of verses.
Run it again only if the source text changes.
"""
import json
import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "site" / "data" / "bible" / "drb"
# Modern name, Douay-Rheims name (when different), short code used in links
NAMES = [
    ("Genesis", "", "gen"), ("Exodus", "", "exod"), ("Leviticus", "", "lev"), ("Numbers", "", "num"), ("Deuteronomy", "", "deut"),
    ("Joshua", "Josue", "josh"), ("Judges", "", "judg"), ("Ruth", "", "ruth"), ("1 Samuel", "1 Kings", "1sam"), ("2 Samuel", "2 Kings", "2sam"),
    ("1 Kings", "3 Kings", "1kgs"), ("2 Kings", "4 Kings", "2kgs"), ("1 Chronicles", "1 Paralipomenon", "1chr"), ("2 Chronicles", "2 Paralipomenon", "2chr"),
    ("Ezra", "1 Esdras", "ezra"), ("Nehemiah", "2 Esdras", "neh"), ("Tobit", "Tobias", "tob"), ("Judith", "", "jdt"), ("Esther", "", "esth"),
    ("Job", "", "job"), ("Psalms", "", "ps"), ("Proverbs", "", "prov"), ("Ecclesiastes", "", "eccl"), ("Song of Songs", "Canticle of Canticles", "song"),
    ("Wisdom", "", "wis"), ("Sirach", "Ecclesiasticus", "sir"), ("Isaiah", "Isaias", "isa"), ("Jeremiah", "Jeremias", "jer"), ("Lamentations", "", "lam"),
    ("Baruch", "", "bar"), ("Ezekiel", "Ezechiel", "ezek"), ("Daniel", "", "dan"), ("Hosea", "Osee", "hos"), ("Joel", "", "joel"), ("Amos", "", "amos"),
    ("Obadiah", "Abdias", "obad"), ("Jonah", "Jonas", "jonah"), ("Micah", "Micheas", "mic"), ("Nahum", "", "nah"), ("Habakkuk", "Habacuc", "hab"),
    ("Zephaniah", "Sophonias", "zeph"), ("Haggai", "Aggeus", "hag"), ("Zechariah", "Zacharias", "zech"), ("Malachi", "Malachias", "mal"),
    ("1 Maccabees", "1 Machabees", "1macc"), ("2 Maccabees", "2 Machabees", "2macc"),
    ("Matthew", "", "matt"), ("Mark", "", "mark"), ("Luke", "", "luke"), ("John", "", "john"), ("Acts", "Acts of the Apostles", "acts"),
    ("Romans", "", "rom"), ("1 Corinthians", "", "1cor"), ("2 Corinthians", "", "2cor"), ("Galatians", "", "gal"), ("Ephesians", "", "eph"),
    ("Philippians", "", "phil"), ("Colossians", "", "col"), ("1 Thessalonians", "", "1thess"), ("2 Thessalonians", "", "2thess"),
    ("1 Timothy", "", "1tim"), ("2 Timothy", "", "2tim"), ("Titus", "", "titus"), ("Philemon", "", "phlm"), ("Hebrews", "", "heb"),
    ("James", "", "jas"), ("1 Peter", "", "1pet"), ("2 Peter", "", "2pet"), ("1 John", "", "1john"), ("2 John", "", "2john"), ("3 John", "", "3john"),
    ("Jude", "", "jude"), ("Revelation", "Apocalypse", "rev"),
]


def tidy(t):
    t = re.sub(r"\s+", " ", t).strip()
    return t


def main(src):
    books = json.loads(Path(src).read_text(encoding="utf-8"))["books"][:73]
    assert len(books) == len(NAMES) == 73
    OUT.mkdir(parents=True, exist_ok=True)
    index = []
    for i, (b, (name, douay, code)) in enumerate(zip(books, NAMES)):
        chapters = [[tidy(v["text"]) for v in sorted(c["verses"], key=lambda v: v["verse"])] for c in sorted(b["chapters"], key=lambda c: c["chapter"])]
        (OUT / f"{i + 1}.json").write_text(json.dumps(chapters, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        index.append({"n": i + 1, "name": name, "douay": douay, "code": code, "chapters": len(chapters), "nt": i >= 46})
    (OUT / "books.json").write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {len(index)} books, {sum(b['chapters'] for b in index)} chapters to {OUT}")


if __name__ == "__main__":
    main(sys.argv[1])
