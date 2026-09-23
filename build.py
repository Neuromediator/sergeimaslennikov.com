#!/usr/bin/env python3
"""Build the site: templates + content/<lang>.json -> public/

    python3 build.py

Writes the home page and the avatar page for every language in BUILD, plus
public/style.css. No dependencies, standard library only.

public/ is not in git: Cloudflare Workers Builds runs this script on every push
and deploys the result with "npx wrangler deploy" (see wrangler.jsonc). Run it
locally to preview -- see README.md.

Template syntax (a small subset of Mustache):

    {{a.b}}            insert a value, HTML-escaped
    {{&a.b}}           insert it raw (for markup built in this file)
    {{#list}}...{{/list}}   repeat the block for each item
    {{#flag}}...{{/flag}}   keep the block only when the value is non-empty
    {{.}}              the current item, when the list holds plain strings
"""

import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
SITE = "https://sergeimaslennikov.com"

# Where the digital twin runs: a Fly app, served from a subdomain of this site so
# its "Keep chat" cookie is first-party inside the iframe on /avatar/.
AVATAR_URL = "https://avatar.sergeimaslennikov.com/"

# Archivo and Newsreader carry no Cyrillic, so the Russian page uses two
# families that do. Both are close in feel to the originals.
FONTS_LATIN = (
    "https://fonts.googleapis.com/css2"
    "?family=Archivo:wdth,wght@62..125,300..800"
    "&family=IBM+Plex+Mono:wght@400;500"
    "&family=Newsreader:ital,opsz,wght@0,6..72,300..600;1,6..72,300..500"
    "&display=swap"
)
FONTS_CYRILLIC = (
    "https://fonts.googleapis.com/css2"
    "?family=Golos+Text:wght@400..900"
    "&family=IBM+Plex+Mono:wght@400;500"
    "&family=Literata:ital,opsz,wght@0,7..72,300..600;1,7..72,300..500"
    "&display=swap"
)

LANGS = [
    # code, short label in the toggle, path on the site, og locale, fonts
    ("en", "EN", "/", "en_GB", FONTS_LATIN),
    ("et", "ET", "/et/", "et_EE", FONTS_LATIN),
    ("ru", "RU", "/ru/", "ru_RU", FONTS_CYRILLIC),
]

# Which of those get built. The Estonian and Russian text is finished and sits in
# content/, waiting: put "et" and "ru" back in this list and the pages, the
# toggle and the hreflang tags all come back. With one language there is no
# toggle and no alternates.
BUILD = ["en"]

PARTIAL = re.compile(r"\{\{>(\w[\w-]*)\}\}")
SECTION = re.compile(r"\{\{#([\w.]+)\}\}")
VALUE = re.compile(r"\{\{(&?)([\w.]+|\.)\}\}")


def expand_partials(template, seen=()):
    """Replace {{>name}} with partials/name.html, before anything else runs."""

    def one(match):
        name = match.group(1)
        if name in seen:
            raise ValueError("partial %s includes itself" % name)
        text = (ROOT / "partials" / ("%s.html" % name)).read_text(encoding="utf-8")
        return expand_partials(text, seen + (name,))

    return PARTIAL.sub(one, template)


def lookup(stack, path):
    if path == ".":
        return stack[-1]
    head, _, rest = path.partition(".")
    for scope in reversed(stack):
        if isinstance(scope, dict) and head in scope:
            value = scope[head]
            for key in filter(None, rest.split(".")):
                value = value[key]
            return value
    raise KeyError(path)


def render(template, stack):
    out = []
    pos = 0
    while True:
        match = SECTION.search(template, pos)
        if not match:
            out.append(fill(template[pos:], stack))
            return "".join(out)
        out.append(fill(template[pos : match.start()], stack))
        name = match.group(1)
        body, pos = take_section(template, match.end(), name)
        value = lookup(stack, name)
        if isinstance(value, list):
            for item in value:
                out.append(render(body, stack + [item]))
        elif isinstance(value, dict):
            out.append(render(body, stack + [value]))
        elif value:
            out.append(render(body, stack))


def take_section(template, start, name):
    """Return the body of {{#name}}...{{/name}} and the index after it."""
    open_tag, close_tag = "{{#%s}}" % name, "{{/%s}}" % name
    depth, cursor = 1, start
    while depth:
        nxt = template.find(close_tag, cursor)
        if nxt < 0:
            raise ValueError("unclosed section %s" % name)
        nested = template.find(open_tag, cursor, nxt)
        if nested >= 0:
            depth += 1
            cursor = nested + len(open_tag)
        else:
            depth -= 1
            cursor = nxt + len(close_tag)
    return template[start : cursor - len(close_tag)], cursor


def fill(text, stack):
    def one(match):
        raw, path = match.group(1), match.group(2)
        value = lookup(stack, path)
        if value is None:
            return ""
        return str(value) if raw else html.escape(str(value), quote=True)

    return VALUE.sub(one, text)


def prepare(code, content):
    """Add the few computed fields the template needs."""
    for leg in content["work"]["legs"]:
        leg["cls"] = " pivot" if leg.get("pivot") else ""
    for group in content["skills"]["groups"]:
        group["tags"] = [
            tag if isinstance(tag, dict) else {"label": tag} for tag in group["tags"]
        ]
        for tag in group["tags"]:
            tag["cls"] = ' class="key"' if tag.get("key") else ""
    for link in content["contact"]["links"]:
        link["target"] = (
            "" if link["href"].startswith("mailto:") else ' target="_blank" rel="noopener"'
        )
    path, og_locale, fonts = next((p, o, f) for c, _, p, o, f in LANGS if c == code)
    for item in content["nav"]:
        # section links are in-page on the home page, back to it everywhere else
        item["href"] = "#" + item["id"]
        # long labels have a short form for the two-row phone bar
        item.setdefault("short", item["label"])
    built = [lang for lang in LANGS if lang[0] in BUILD]
    toggle = [
        {
            "code": c,
            "short": short,
            "href": p,
            "current": ' aria-current="page"' if c == code else "",
        }
        for c, short, p, _, _ in built
    ]
    content.update(
        lang=code,
        site=SITE,
        canonical=SITE + path,
        og_locale=og_locale,
        fonts=fonts,
        avatar_url=AVATAR_URL,
        avatar_url_json=json.dumps(AVATAR_URL),
        avatar_current="",
        avatar_href="/avatar/",
        avatar_target="",
        avatar_arrow="",
        langs={"items": toggle} if len(built) > 1 else None,
        alternates=(
            [{"hreflang": c, "href": SITE + p} for c, _, p, _, _ in built]
            + [{"hreflang": "x-default", "href": SITE + "/"}]
            if len(built) > 1
            else []
        ),
    )
    return content


def main():
    head_pages = [
        # template, output path under public/, where the page's own title lives
        ("template.html", "%s", None),
        ("template-avatar.html", "%savatar/", "avatar"),
    ]
    for code, _, path, _, _ in LANGS:
        if code not in BUILD:
            continue
        source = ROOT / "content" / ("%s.json" % code)
        if not source.exists():
            print("skipping %s (no %s yet)" % (code, source.name))
            continue
        base = json.loads(source.read_text(encoding="utf-8"))
        for template_name, page_path, meta_key in head_pages:
            content = prepare(code, json.loads(json.dumps(base)))
            here = page_path % path
            meta = content[meta_key] if meta_key else content
            content["page"] = {
                "title": meta["title"],
                "description": meta["description"],
                "canonical": SITE + here,
            }
            if meta_key == "avatar":
                # already on the twin's page, so the nav item opens the app in a
                # tab of its own instead of pointing back here
                content["avatar_current"] = ' aria-current="page"'
                content["avatar_href"] = AVATAR_URL
                content["avatar_target"] = ' target="_blank" rel="noopener"'
                content["avatar_arrow"] = '<span class="out" aria-hidden="true">&#8599;</span>'
                for item in content["nav"]:
                    item["href"] = path + "#" + item["id"]
            template = expand_partials(
                (ROOT / template_name).read_text(encoding="utf-8")
            )
            target = ROOT / "public" / here.strip("/") / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render(template, [content]), encoding="utf-8")
            print("wrote %s" % target.relative_to(ROOT))

    # everything else in assets/ is copied through untouched
    out = ROOT / "public"
    for name in ("style.css", "favicon.svg"):
        shutil.copyfile(ROOT / "assets" / name, out / name)
    shutil.copytree(ROOT / "assets" / "img", out / "img", dirs_exist_ok=True)
    print("copied style.css, favicon.svg and img/")


if __name__ == "__main__":
    main()
