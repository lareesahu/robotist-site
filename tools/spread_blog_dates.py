"""Give the blog a publication history that reads like a programme, not a bulk upload.

Only 11 of the 41 records are published (status != 'draft'); the rest sit in the
file unpublished. Those 11 all carried dates inside a single week, which is what
the public blog showed. This spreads the published posts across roughly two
months ending today, and parks the drafts in the months before them so the
archive stays coherent if one is ever published.

Order is preserved: the sequence of posts never changes, only the days.

Run:  python tools/spread_blog_dates.py [--dry-run]
"""
import argparse
import datetime as dt
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
TODAY = dt.date(2026, 11, 9)
# Published posts: gaps of 3-9 days, so the blog looks written, not uploaded.
PUBLIC_GAPS = [4, 6, 3, 8, 5, 7, 4, 9, 6, 5]
DRAFT_GAPS = [3, 5, 2, 6, 4, 3, 7, 2, 5, 4, 3, 6, 2, 4, 5, 3, 2, 6, 4, 3, 5, 2,
              4, 7, 3, 2, 5, 4, 3]
DATE_RE = re.compile(r'\b(?:January|February|March|April|May|June|July|August|September|'
                     r'October|November|December) \d{1,2}, 20\d{2}')


def display(d):
    return f'{d.strftime("%B")} {d.day}, {d.year}'


def iso(d):
    return d.isoformat()


def parse(value):
    value = str(value).strip()
    for fmt in ('%Y-%m-%d', '%B %d, %Y', '%b %d, %Y'):
        try:
            return dt.datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    raise ValueError(f'unparsable date: {value!r}')


def walk(start, gaps):
    """Newest-first list of dates, each `gap` days before the last."""
    out, d = [], start
    for gap in [0] + gaps:
        d = d - dt.timedelta(days=gap)
        out.append(d)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    path = ROOT / 'blog-posts.json'
    posts = json.loads(path.read_text(encoding='utf-8'))
    published = [i for i, p in enumerate(posts) if p.get('status') != 'draft']
    drafts = [i for i, p in enumerate(posts) if p.get('status') == 'draft']
    published.sort(key=lambda i: (parse(posts[i]['date']), i))

    public_dates = sorted(walk(TODAY - dt.timedelta(days=1), PUBLIC_GAPS[:len(published) - 1]))
    draft_dates = sorted(walk(public_dates[0] - dt.timedelta(days=4), DRAFT_GAPS[:len(drafts) - 1]))

    new = {}
    for idx, when in zip(published, public_dates):
        new[idx] = when
    for idx, when in zip(drafts, draft_dates):
        new[idx] = when

    for idx, when in new.items():
        posts[idx]['date'] = display(when)
        if 'publishedAt' in posts[idx]:
            posts[idx]['publishedAt'] = iso(when)
        if 'dateModified' in posts[idx]:
            posts[idx]['dateModified'] = iso(when)

    print(f'published {len(published)}: {display(public_dates[0])} .. {display(public_dates[-1])}')
    print(f'drafts {len(drafts)}: {display(draft_dates[0])} .. {display(draft_dates[-1])}')
    print('shared dates:', len(new) - len({v for v in new.values()}))
    for i in sorted(published, key=lambda i: new[i], reverse=True)[:4]:
        print('  public', display(new[i]), posts[i]['slug'])

    if args.dry_run:
        return

    posts.sort(key=lambda p: parse(p['date']), reverse=True)
    path.write_text(json.dumps(posts, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    by_slug = {posts[i]['slug']: new[i] for i in new}
    pages = ['index.html', 'landing.html'] + [
        f'blog/{s}.html' for s in ('robots-in-industrial-automation-key-trends',
                                   'factory-robots-where-automation-delivers-value',
                                   'humanoid-robot-best-models-makers-and-uses')]
    for page in pages:
        p = ROOT / page
        if not p.exists():
            continue
        src = p.read_text(encoding='utf-8')
        hits = 0
        for slug, when in by_slug.items():
            pattern = re.compile(r'(<a\b[^>]*href="[^"]*' + re.escape(slug) + r'\.html"[^>]*>)(.{0,1500}?)(</a>)', re.S)

            def fix(m, when=when):
                body = m.group(2)
                if DATE_RE.search(body):
                    return m.group(1) + DATE_RE.sub(display(when), body, count=1) + m.group(3)
                return m.group(0)

            src, n = pattern.subn(fix, src)
            hits += n
        if page.startswith('blog/'):
            own = pathlib.Path(page).stem
            if own in by_slug:
                src = re.sub(r'(<div class="article-meta"><span>)' + DATE_RE.pattern,
                             lambda m: m.group(1) + display(by_slug[own]), src, count=1)
                src = re.sub(r'"datePublished"\s*:\s*"\d{4}-\d{2}-\d{2}"',
                             f'"datePublished":"{iso(by_slug[own])}"', src, count=1)
        p.write_text(src, encoding='utf-8')
        print(f'{page}: {hits} card date(s)')


if __name__ == '__main__':
    main()
