# Tutorial sources and build scripts

The published pages (`../portfolio-1/`, `../portfolio-2/`, `../portfolio-3/`) are generated from the files here.
Each tutorial page is also published as a claude.ai artifact. That copy is the same file without the `<!DOCTYPE>` and
`<head>` wrapper (the artifact viewer adds them).

| Task | Source | Published page |
|---|---|---|
| 1. HTML/CSS portfolio | `portfolio-tutorial.html` | `../portfolio-1/index.html` |
| 2. JS filters + GitHub Desktop | `portfolio-2-tutorial.html` | `../portfolio-2/index.html` |
| 3. React + Vite | `portfolio-3-tutorial.src.html` → `build_task3.py` | `../portfolio-3/index.html` |

## How the pages work

All the example code lives inside each page, in `<script type="text/plain" data-snippet="…">` blocks. A snippet
writes `<\/script>` for a closing script tag. The page's script uses these snippets to render the code blocks, assemble
the "Полный код" section and build the live preview, so the steps, the full code and the preview always match.

## Changing text (any task)

1. Edit the source file.
2. Rebuild the published page:

   ```bash
   python make_standalone.py portfolio-tutorial.html ../portfolio-1/index.html
   python make_standalone.py portfolio-2-tutorial.html ../portfolio-2/index.html
   ```

   Task 3 has an extra build step first; see below.
3. Commit and push. GitHub Pages updates within a minute.

## Changing the example code

**Task 1:** the example site is in `site-test/` (`index.html`, `style.css`, `images/`). It's assembled from the
snippets in `portfolio-tutorial.html`, so when you change a snippet, update `site-test/` to match.

**Task 2:**

```bash
python build_task2_tests.py
```

This checks that each step's code matches the final files. It also writes two test sites into `site-test-2/`: `part3/`
(the filters that hide entries) and `final/` (built from `data.js`). Serve the folder (`python -m http.server`) and
click through the filters.

**Task 3** (needs Node.js 20.19+ or 22.12+):

```bash
python build_task3.py
python make_standalone.py portfolio-3-tutorial.html ../portfolio-3/index.html
```

`build_task3.py` does four things:
1. It writes a real Vite project from the snippets to `react-test/`, running `npm install` on the first run.
2. It runs `vite build` for every stage the student reaches (steps 5, 6, 8, 11, 12, 14, the optional lightbox, and
   the final version) into `stage-builds/`.
3. It checks the deploy workflow and confirms that `package-lock.json` includes the Linux packages GitHub Actions needs.
4. It embeds the final build as the page's live preview and writes `portfolio-3-tutorial.html`.

To try a stage in the dev server:

```bash
python build_task3.py --use s14-state
cd react-test
npm run dev
```

The script expects Node.js in `C:\Program Files\nodejs`; edit `NODE_DIR` at the top of the script if yours is
elsewhere.

`site-test/images/` contains neutral placeholder pictures that use the file names from the tutorials.
