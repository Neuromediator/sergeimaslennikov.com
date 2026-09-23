# sergeimaslennikov.com

Personal identity site. Two pages: the home page, and `/avatar/`, which frames
the digital twin that runs on Fly.

Plain HTML and CSS, no framework. `build.py` fills the templates from the
content files and writes `public/`. Cloudflare Pages runs that same script on
every push to `main`, so **editing a content file and pushing puts it live**.

## Adding a project

Open `content/en.json`, find `"projects"`, copy one entry:

```json
{
  "when": "Oct 2026",
  "name": "Name of the project",
  "body": "One paragraph, plain sentences.",
  "caveat": "",
  "live": "https://...",
  "code": "https://github.com/Neuromediator/..."
}
```

`caveat` is the small grey line under the text (`"Not a betting tool"` on the
tennis dashboard). Leave it `""` when there is none.

Then:

```sh
python3 build.py                  # regenerate public/
python3 -m http.server 8000 -d public   # look at it: http://localhost:8000
git add -A && git commit -m "Add the X project" && git push
```

The push is the deploy. Cloudflare builds and the site is live in about a
minute. `public/` is not in git — it is generated on both sides.

## Where things live

| Path | What it is |
|---|---|
| `content/en.json` | every word on the English pages |
| `content/et.json`, `ru.json` | finished Estonian and Russian text, not built yet |
| `template.html` | the home page |
| `template-avatar.html` | the page that frames the twin |
| `partials/head.html`, `partials/nav.html` | shared `<head>` and nav bar |
| `assets/style.css` | the whole design |
| `assets/img/`, `assets/favicon.svg` | copied into `public/` as they are |
| `build.py` | the build; `SITE`, `AVATAR_URL` and `BUILD` live at the top |
| `KNOWLEDGE.MD` | the source of truth for the facts, never published |

## Two switches in `build.py`

```python
AVATAR_URL = "https://avatar-sergei.fly.dev/"   # -> https://avatar.sergeimaslennikov.com/
BUILD = ["en"]                                   # -> ["en", "et", "ru"]
```

Adding `"et"` and `"ru"` brings back `/et/` and `/ru/`, the EN·ET·RU toggle in
the nav and the `hreflang` tags. Nothing else needs touching.

## Rules for the text

- Every claim traceable to `KNOWLEDGE.MD`. No invented dates.
- Plain declarative sentences. No marketing verbs, no closing zingers.
- Job titles, school names and course names stay in their original form.
