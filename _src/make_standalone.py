"""Wrap the artifact page (a fragment without <head>) into a standalone HTML document."""
import sys
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
page = src.read_text(encoding="utf-8")

head_end = page.index("</style>") + len("</style>")
head, body = page[:head_end], page[head_end:].lstrip("\n")

# The artifact platform adds these itself; a plain web host does not.
reset = "\n<style>\n  body { margin: 0; }\n  img { max-width: 100%; }\n</style>"

doc = (
    "<!DOCTYPE html>\n"
    '<html lang="ru">\n'
    "<head>\n"
    '<meta charset="UTF-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    f"{head}{reset}\n"
    "</head>\n"
    "<body>\n\n"
    f"{body.rstrip()}\n\n"
    "</body>\n"
    "</html>\n"
)

dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text(doc, encoding="utf-8", newline="\n")
print(f"wrote {dst} ({len(doc.encode('utf-8'))} bytes)")
