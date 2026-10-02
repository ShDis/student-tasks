"""Extract code snippets from the Task 2 tutorial, check that step fragments match the
final files, and build two test sites (Part 3 and final) from exactly that code."""
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).parent
page = (HERE / "portfolio-2-tutorial.html").read_text(encoding="utf-8")

S = {}
for key, body in re.findall(r'<script type="text/plain" data-snippet="([^"]+)">(.*?)</script>', page, re.S):
    S[key] = re.sub(r"^\r?\n", "", body).rstrip().replace("<\\/script>", "</script>")

S["full-css"] = S["css-task1"] + "\n\n" + S["css-filters"]
S["full-js"] = "\n\n".join([S["js-timeline"], S["js-cards"], S["js-filters"]])


def norm(text):
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


task1 = HERE / "site-test"
errors = []

# CSS from task 1 must be copied exactly
if S["css-task1"] != (task1 / "style.css").read_text(encoding="utf-8").rstrip():
    errors.append("css-task1 differs from task 1 style.css")

# Part 3 index.html: task 1 page + script tag + buttons + data-category
part3 = (task1 / "index.html").read_text(encoding="utf-8")
part3 = part3.replace(
    '    <link rel="stylesheet" href="style.css">\n',
    '    <link rel="stylesheet" href="style.css">\n    <script src="script.js" defer></script>\n', 1)
filters = "\n".join(" " * 16 + l if l else l for l in S["html-filters"].splitlines())
part3 = part3.replace("                <h2>Мой путь</h2>\n\n", "                <h2>Мой путь</h2>\n\n" + filters + "\n\n", 1)
cats = iter(["study", "study", "hackathon", "hobby", "study", "hobby"])
part3 = re.sub(r'<article class="timeline-item">', lambda m: f'<article class="timeline-item" data-category="{next(cats)}">', part3)

# The category example shows two separate (non-adjacent) entries: check each one
for i, chunk in enumerate(S["html-category-example"].split("\n\n")):
    S[f"html-category-example[{i}]"] = chunk

checks = [
    ("html-category-example[0]", part3),
    ("html-category-example[1]", part3),
    ("html-filters", part3),
    ("html-filters", S["full-html"]),
    ("html-scripts-part4", S["full-html"]),
    ("html-timeline-part4", S["full-html"]),
    ("html-cards-part4", S["full-html"]),
]
for key, target in checks:
    if norm(S[key]) not in norm(target):
        errors.append(f"{key} not found in its target file")

if errors:
    print("ERRORS:\n  " + "\n  ".join(errors))
    sys.exit(1)

out = HERE / "site-test-2"
if out.exists():
    shutil.rmtree(out)
for name, files in {
    "part3": {"index.html": part3, "style.css": S["full-css"], "script.js": S["js-part3"]},
    "final": {"index.html": S["full-html"], "style.css": S["full-css"], "data.js": S["js-data"], "script.js": S["full-js"]},
}.items():
    d = out / name
    shutil.copytree(task1 / "images", d / "images")
    for fname, text in files.items():
        (d / fname).write_text(text + "\n", encoding="utf-8", newline="\n")

print(f"OK: {len(S)} snippets, all fragments match; test sites in {out}")
