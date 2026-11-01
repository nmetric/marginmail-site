#!/usr/bin/env python3
"""The release notes pages (board 100): /releases/ and one /releases/<version>-<build>/ per build (stdlib only).

Apart from build.py on purpose. A release runs this one file and pushes releases/ alone, and these pages must not
get what every page from build.py gets: the visit beacon, a sitemap line, llms.txt, the nav. They carry a noindex,
a strict CSP and no site.js, and follow the system to dark; only releases/releases.css does that, so the rest of
the site stays light. check.py holds them to all of it.

  releases.py --check <notes.md> --refs <folder> --screens <screens.txt>       every problem with the notes; exits 1 if any
  releases.py --images <notes.md> --refs <folder>                              the screenshots this page would show
  releases.py --publish <notes.md> --version 1.0 --build 14 --channel beta --date 2026-11-09 --refs <folder> --screens <screens.txt>
  releases.py --rebuild --notes-dir <folder> --refs <folder> --screens <screens.txt>     every page again, after a template change

A notes file (docs/release-notes/ in the app's repo) is paragraphs and "- " bullets, plus two kinds of line:
  Note: one folder per trip                       the hand note: in the slip, and in this page's margin
  Shot: files-receipt-cards | What it shows.      a fixture screen by name, then its caption and alt text

Screenshots are named, never supplied: a Shot must be a screen in the app's Apps/MarginMacSnapshots/screens.txt, and
its images are that screen's recorded references, so no real mail can reach a page. releases/builds.json keeps each
build's date and channel, which the notes don't hold.
"""
import argparse
import datetime
import html
import json
import os
import re
import shutil
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'releases')
SHOT_LIMIT = 3
SHOT_ID = re.compile(r'[a-z0-9]+(-[a-z0-9]+)*\Z')
NOT_ON_A_PAGE = re.compile(r'\b(ben|nowacky)\b', re.I)  # his name never goes on a public page
CSP = "default-src 'none'; style-src 'self'; script-src 'self'; img-src 'self'; font-src 'self'; base-uri 'none'; form-action 'none'"
e = html.escape


def first_sentence(text):
    """UpdateNotes.firstSentence in the app, so the index reads as the slip does."""
    line = next((x for x in text.split('\n') if x), text)
    m = re.search(r'[.?](\s|$)', line)
    return line[:m.start() + 1] if m else line


class Notes:
    def __init__(self, text):
        self.note = None
        self.shots = []  # (id, caption)
        self.paragraphs = []
        self.bullets = []
        run = []

        def end_paragraph():
            if run:
                self.paragraphs.append(' '.join(run))
                run.clear()
        for raw in text.splitlines():
            line = raw.strip()
            if line.startswith('Note:'):
                self.note = self.note or line[5:].strip() or None
            elif line.startswith('Shot:'):
                shot, _, caption = line[5:].partition('|')
                self.shots.append((shot.strip(), caption.strip()))
            elif line.startswith('- '):
                end_paragraph()
                self.bullets.append(line[2:].strip())
            elif line:
                run.append(line)
            else:
                end_paragraph()
        end_paragraph()

    @property
    def sentence(self):
        return first_sentence(self.paragraphs[0]) if self.paragraphs else ''

    def words(self):
        return self.paragraphs + self.bullets + [self.note or ''] + [c for _, c in self.shots]


def reference(refs, shot, side):
    return os.path.join(refs, f'{shot}-{side}.png')


def screens_in(path):
    with open(path, encoding='utf-8') as fh:
        return {line.split()[0] for line in fh if line.strip() and not line.startswith('#')}


def problems(notes, refs, screens):
    found = []
    if not notes.paragraphs:
        found.append('the notes have no text')
    if notes.note and notes.note.startswith('['):
        found.append('the hand note is still the placeholder')
    if len(notes.shots) > SHOT_LIMIT:
        found.append(f'{len(notes.shots)} screenshots: a build has at most {SHOT_LIMIT}')
    if any(NOT_ON_A_PAGE.search(w) for w in notes.words()):
        found.append("the notes name Ben, and his name never goes on a public page")
    known = screens_in(screens)
    for shot, caption in notes.shots:
        if not SHOT_ID.match(shot) or shot not in known:
            found.append(f"Shot {shot!r} isn't a fixture screen in screens.txt")
        elif not all(os.path.isfile(reference(refs, shot, s)) for s in ('light', 'dark')):
            found.append(f'Shot {shot} needs both recorded references (light and dark)')
        if not caption:
            found.append(f'Shot {shot} has no caption: write Shot: {shot} | what it shows')
    return found


def png_size(path):
    with open(path, 'rb') as fh:
        head = fh.read(24)
    if head[:8] != b'\x89PNG\r\n\x1a\n':
        raise SystemExit(f"{path} isn't a PNG")
    return struct.unpack('>II', head[16:24])


def shell(title, description, body):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="{e(CSP)}">
<meta name="robots" content="noindex">
<meta name="referrer" content="no-referrer">
<meta name="color-scheme" content="light dark">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/css/site.css">
<link rel="stylesheet" href="/releases/releases.css">
<script src="/releases/releases.js" defer></script>
</head>
<body class="rn">
<a class="skip" href="#main">Skip to content</a>
<header class="rn-nav"><a class="rn-brand" href="/">MarginMail</a><a href="/releases/">All release notes</a></header>
<main class="rn-main" id="main">
{body}
</main>
<footer class="rn-foot">Made with love for the Mac.</footer>
</body>
</html>
'''


def stamp(entry):
    d = datetime.date.fromisoformat(entry['date'])
    return f"{d.strftime('%a, %b')} {d.day} · {entry['channel'].capitalize()}"


def build_page(notes, entry, sizes):
    parts = []
    if notes.note:
        parts.append(f'<div class="rn-note">{e(notes.note)}</div>')
    parts.append('<p class="rn-eyebrow">Release notes</p>')
    parts.append(f"<h1>MarginMail {e(entry['version'])} ({e(entry['build'])})</h1>")
    parts.append(f'<p class="rn-stamp">{e(stamp(entry))}</p>')
    parts.extend(f'<p>{e(p)}</p>' for p in notes.paragraphs)
    if notes.shots:
        parts.append('<div class="rn-shots">')
        for shot, caption in notes.shots:
            cap = e(caption, quote=True)
            w, h = sizes[shot]
            parts.append(f'<figure class="rn-shot"><a href="{shot}-light.png" aria-label="See larger: {cap}"><picture>'
                         f'<source srcset="{shot}-dark.png" media="(prefers-color-scheme: dark)">'
                         f'<img src="{shot}-light.png" width="{w}" height="{h}" alt="{cap}" loading="lazy">'
                         f'</picture></a><figcaption>{e(caption)}</figcaption></figure>')
        parts.append('</div>')
    if notes.bullets:
        parts.append('<h2>Also in this build</h2>')
        parts.append('<ul>' + ''.join(f'<li>{e(b)}</li>' for b in notes.bullets) + '</ul>')
    return shell(f"MarginMail {entry['version']} ({entry['build']}) release notes", notes.sentence, '\n'.join(parts))


def index_page(builds):
    rows = [f'<li><a href="/releases/{e(b["version"])}-{e(b["build"])}/">MarginMail {e(b["version"])} ({e(b["build"])})</a>'
            f'<p class="rn-stamp">{e(stamp(b))}</p><p>{e(b["sentence"])}</p></li>' for b in builds]
    body = '<h1>Release notes</h1>\n<ol class="rn-list">\n' + '\n'.join(rows) + '\n</ol>'
    return shell('MarginMail release notes', 'What changed in each build of MarginMail.', body)


def load_ledger():
    path = os.path.join(OUT, 'builds.json')
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)


def write_page(notes, entry, refs):
    page = os.path.join(OUT, f"{entry['version']}-{entry['build']}")
    os.makedirs(page, exist_ok=True)
    sizes = {}
    for shot, _ in notes.shots:
        sizes[shot] = png_size(reference(refs, shot, 'light'))
        for side in ('light', 'dark'):
            shutil.copyfile(reference(refs, shot, side), os.path.join(page, f'{shot}-{side}.png'))
    write_text(os.path.join(page, 'index.html'), build_page(notes, entry, sizes))


def write_index(builds):
    builds.sort(key=lambda b: int(b['build']), reverse=True)
    write_text(os.path.join(OUT, 'builds.json'), json.dumps(builds, indent=1, ensure_ascii=False) + '\n')
    write_text(os.path.join(OUT, 'index.html'), index_page(builds))


def read_notes(path):
    with open(path, encoding='utf-8') as fh:
        return Notes(fh.read())


def refuse(notes, refs, screens):
    found = problems(notes, refs, screens)
    for p in found:
        print(f'✘ {p}', file=sys.stderr)
    return bool(found)


def main():
    ap = argparse.ArgumentParser(description='The /releases/ pages.')
    action = ap.add_mutually_exclusive_group(required=True)
    action.add_argument('--check', metavar='NOTES')
    action.add_argument('--images', metavar='NOTES')
    action.add_argument('--publish', metavar='NOTES')
    action.add_argument('--rebuild', action='store_true')
    ap.add_argument('--refs', required=True)
    ap.add_argument('--screens')
    ap.add_argument('--notes-dir')
    ap.add_argument('--version')
    ap.add_argument('--build')
    ap.add_argument('--channel', choices=['beta', 'stable'])
    ap.add_argument('--date')
    a = ap.parse_args()

    if a.images:
        for shot, _ in read_notes(a.images).shots:
            for side in ('light', 'dark'):
                print(reference(a.refs, shot, side))
        return 0
    if not a.screens:
        ap.error('--screens is required')
    if a.check:
        return 1 if refuse(read_notes(a.check), a.refs, a.screens) else 0
    if a.publish:
        if not (a.version and a.build and a.channel and a.date):
            ap.error('--publish needs --version, --build, --channel and --date')
        datetime.date.fromisoformat(a.date)
        notes = read_notes(a.publish)
        if refuse(notes, a.refs, a.screens):
            return 1
        entry = dict(version=a.version, build=a.build, channel=a.channel, date=a.date, sentence=notes.sentence)
        write_page(notes, entry, a.refs)
        write_index([b for b in load_ledger() if b['build'] != a.build] + [entry])
        return 0
    if not a.notes_dir:
        ap.error('--rebuild needs --notes-dir')
    builds = load_ledger()
    for entry in builds:
        notes = read_notes(os.path.join(a.notes_dir, f"{entry['version']}-b{entry['build']}.md"))
        if refuse(notes, a.refs, a.screens):
            return 1
        write_page(notes, entry, a.refs)
    write_index(builds)
    return 0


if __name__ == '__main__':
    sys.exit(main())
