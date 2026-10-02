"""Build and test the Task 3 (React) tutorial.

1. Extract the code snippets from portfolio-3-tutorial.src.html.
2. Write a real Vite + React project to react-test/ and npm install it once.
3. Compile every stage the student passes through (vite build), so each one is known to work.
4. Embed the final build into the tutorial as the live preview -> portfolio-3-tutorial.html.

Usage: python build_task3.py              build everything
       python build_task3.py --use STAGE  only write STAGE's files into react-test/src (for dev-server tests)
"""
import base64
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
PROJECT = HERE / "react-test"
BUILDS = HERE / "stage-builds"
NODE_DIR = Path(r"C:\Program Files\nodejs")
NPM, NPX = str(NODE_DIR / "npm.cmd"), str(NODE_DIR / "npx.cmd")

SNIPPET_RE = re.compile(r'<script type="text/plain" data-snippet="([^"]+)">(.*?)</script>', re.S)


def snippets(page):
    return {k: re.sub(r"^\r?\n", "", v).rstrip().replace("<\\/script>", "</script>") for k, v in SNIPPET_RE.findall(page)}


src_page = (HERE / "portfolio-3-tutorial.src.html").read_text(encoding="utf-8")
task2_page = (HERE / "portfolio-2-tutorial.html").read_text(encoding="utf-8")
S, T2 = snippets(src_page), snippets(task2_page)

STYLE_CSS = T2["css-task1"] + "\n\n" + T2["css-filters"]  # style.css after task 2, unchanged
DATA_V2 = T2["js-data"]                                    # data.js before step 9 (no export yet)

COMMON = {"src/main.jsx": "main-jsx"}
STAGE_FILES = {
    "s05-hello": {"src/App.jsx": "app-hello", "src/projects.js": DATA_V2},
    "s06-header": {"src/App.jsx": "app-header", "src/components/Header.jsx": "header-jsx", "src/projects.js": DATA_V2},
    "s08-layout": {"src/App.jsx": "app-layout", "src/components/Header.jsx": "header-jsx",
                   "src/components/Profile.jsx": "profile-jsx", "src/projects.js": DATA_V2},
}
base = {"src/components/Header.jsx": "header-jsx", "src/components/Profile.jsx": "profile-jsx",
        "src/projects.js": "projects-js", "src/components/TimelineItem.jsx": "timelineitem-jsx"}
STAGE_FILES["s11-timeline"] = {**base, "src/App.jsx": "app-timeline", "src/components/Timeline.jsx": "timeline-basic"}
base = {**base, "src/components/ProjectCard.jsx": "projectcard-jsx"}
STAGE_FILES["s12-cards"] = {**base, "src/App.jsx": "app-final", "src/components/Timeline.jsx": "timeline-basic"}
base = {**base, "src/App.jsx": "app-final", "src/components/FilterBar.jsx": "filterbar-jsx"}
STAGE_FILES["s14-state"] = {**base, "src/components/Timeline.jsx": "timeline-state"}
STAGE_FILES["lightbox"] = {**base, "src/components/Timeline.jsx": "timeline-final", "src/App.jsx": "app-lightbox",
                           "src/components/ProjectCard.jsx": "projectcard-lightbox",
                           "src/components/Lightbox.jsx": "lightbox-jsx",
                           "src/style.css": STYLE_CSS + "\n\n" + S["css-lightbox"]}
STAGE_FILES["final"] = {**base, "src/components/Timeline.jsx": "timeline-final"}


def text_of(value):
    return S[value] if value in S else value


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n", encoding="utf-8", newline="\n")


def use_stage(name):
    """Make react-test/src exactly what the student has at this stage."""
    shutil.rmtree(PROJECT / "src", ignore_errors=True)
    files = {"src/style.css": STYLE_CSS, **COMMON, **STAGE_FILES[name]}
    for rel, value in files.items():
        write(PROJECT / rel, text_of(value))


def setup_project():
    PROJECT.mkdir(exist_ok=True)
    for rel, key in {"package.json": "package-json", "vite.config.js": "vite-config", ".gitignore": "gitignore",
                     "index.html": "index-html", ".github/workflows/deploy.yml": "deploy-yml"}.items():
        write(PROJECT / rel, S[key])
    # old/ exists during steps 3-19, exactly as the student has it
    write(PROJECT / "old/index.html", T2["full-html"])
    write(PROJECT / "old/script.js", "\n\n".join([T2["js-timeline"], T2["js-cards"], T2["js-filters"]]))
    if not (PROJECT / "public/images").exists():
        shutil.copytree(HERE / "site-test/images", PROJECT / "public/images")
    if not (PROJECT / "node_modules").exists():
        print("npm install ...")
        subprocess.run([NPM, "install", "--no-audit", "--no-fund"], cwd=PROJECT, check=True)


def checks():
    errors = []
    pkg = json.loads(S["package-json"])
    if set(pkg["dependencies"]) != {"react", "react-dom"}:
        errors.append("unexpected dependencies in package.json")
    if 'src="/src/main.jsx"' not in S["index-html"] or 'id="root"' not in S["index-html"]:
        errors.append("index.html lacks root div or main.jsx script")
    official = ["actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
                "actions/setup-node@820762786026740c76f36085b0efc47a31fe5020",
                "actions/configure-pages@45bfe0192ca1faeb007ade9deae92b16b8254a0d",
                "actions/upload-pages-artifact@fc324d3547104276b827a68afc52ff2a11cc49c9",
                "actions/deploy-pages@368f82528645a54fb793d4d04e342629a3f51346"]
    if re.findall(r"uses: (\S+)", S["deploy-yml"]) != official:
        errors.append("deploy.yml actions differ from the Vite docs")
    lock = (PROJECT / "package-lock.json").read_text(encoding="utf-8")
    linux = sorted(set(re.findall(r'"node_modules/([^"]*linux-x64-gnu[^"]*)"', lock)))
    print("linux bindings in package-lock.json:", linux or "NONE")
    if not linux:
        errors.append("package-lock.json has no linux-x64 bindings: npm ci on GitHub Actions would fail")
    for name in ["header-jsx", "profile-jsx", "timelineitem-jsx", "projectcard-jsx", "filterbar-jsx", "timeline-final", "app-final"]:
        for bad in ["querySelector", "classList", "innerHTML", "class="]:
            if bad in S[name]:
                errors.append(f"{name} contains {bad}")
    return errors


def build_stage(name):
    use_stage(name)
    out = BUILDS / name
    r = subprocess.run([NPX, "vite", "build", "--base", "./", "--outDir", str(out), "--emptyOutDir"],
                       cwd=PROJECT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = (r.stdout + r.stderr).strip()
    noisy = [l for l in log.splitlines() if re.search(r"warn|error|fail", l, re.I)]
    status = "OK" if r.returncode == 0 else "FAILED"
    print(f"  {name:13} {status}" + ("".join(f"\n      {l}" for l in noisy)))
    if r.returncode != 0:
        print(log)
    return r.returncode == 0


def assemble_page():
    t2_style = task2_page[task2_page.index("<style>") + len("<style>"):task2_page.index("</style>")].strip("\n")
    assets = BUILDS / "final" / "assets"
    js = next(assets.glob("*.js")).read_bytes()
    css = next(assets.glob("*.css")).read_bytes()
    page = (src_page.replace("/*@include task2-style*/", t2_style)
            .replace("__STYLE_CSS__", STYLE_CSS)
            .replace("__PREVIEW_JS_B64__", base64.b64encode(js).decode())
            .replace("__PREVIEW_CSS_B64__", base64.b64encode(css).decode()))
    assert "__" + "PREVIEW" not in page and "__STYLE_CSS__" not in page
    out = HERE / "portfolio-3-tutorial.html"
    out.write_text(page, encoding="utf-8", newline="\n")
    print(f"tutorial: {out.name} ({len(page.encode()) // 1024} KB; preview js {len(js) // 1024} KB, css {len(css) // 1024} KB)")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--use":
        use_stage(sys.argv[2])
        print(f"react-test/src now at stage {sys.argv[2]}")
        sys.exit(0)
    setup_project()
    errs = checks()
    print("stage builds:")
    ok = all([build_stage(name) for name in STAGE_FILES])  # 'final' is last, so react-test ends at the final stage
    if errs or not ok:
        print("ERRORS:\n  " + "\n  ".join(errs or ["a stage failed to build"]))
        sys.exit(1)
    assemble_page()
