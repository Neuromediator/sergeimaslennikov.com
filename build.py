#!/usr/bin/env python3
"""Build the site: template.html + content/<lang>.json -> public/

    python3 build.py

Writes public/index.html (English), public/et/index.html, public/ru/index.html.
No dependencies. Run it after editing template.html or any content file, and
commit the result -- Cloudflare Pages only serves what is in public/.

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
from pathlib import Path

ROOT = Path(__file__).parent
SITE = "https://sergeimaslennikov.com"

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

SECTION = re.compile(r"\{\{#([\w.]+)\}\}")
VALUE = re.compile(r"\{\{(&?)([\w.]+|\.)\}\}")


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
        nav_class="" if len(built) > 1 else " nav-solo",
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
    template = (ROOT / "template.html").read_text(encoding="utf-8")
    for code, _, path, _, _ in LANGS:
        if code not in BUILD:
            continue
        source = ROOT / "content" / ("%s.json" % code)
        if not source.exists():
            print("skipping %s (no %s yet)" % (code, source.name))
            continue
        content = prepare(code, json.loads(source.read_text(encoding="utf-8")))
        target = ROOT / "public" / path.strip("/") / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(template, [content]), encoding="utf-8")
        print("wrote %s" % target.relative_to(ROOT))


if __name__ == "__main__":
    main()
