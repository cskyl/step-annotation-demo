# Step-authorship annotation interface demo

A static site for trying two annotation pages in a browser. Every problem and dialogue here is made up; the site exists only to test the interface.

| Path | What it is |
|---|---|
| `index.html` | landing page with test steps and short instructions |
| `gold/index.html` | two-question page (Q1 / Q2 buttons), 7 units |
| `audit48/index.html` | three-label page (L1 / L2 / L3), 7 units |
| `demo_units.json` | the made-up units; `expected` holds the intended labels |
| `build_demo.py` | writes the units into the two pages |
| `display_clean.py` | display-only cleanup of pasted-math text, used by the build |
| `templates/` | the two page shells the build fills in |

Rebuild after editing `demo_units.json`:

```
python3 build_demo.py
```

Python 3.8+ with the standard library only.

Publish with GitHub Pages: push the folder to a repository, then Settings → Pages → Deploy from a branch, root folder. The `.nojekyll` file makes Pages serve the files unchanged.

Exports are saved by the browser to the Downloads folder; nothing is uploaded. Demo packet ids start with `DEMO-`.
