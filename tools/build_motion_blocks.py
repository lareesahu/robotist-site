
"""Inject a per-model motion block into every product page.

Source of truth: motion-library/models.json (platform class per product slug)
plus motion-library/data/index.json (clip names/groups). The block is
region-marked so a re-run replaces it instead of stacking copies.
"""
import json, re, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'motion-library/models.json').read_text(encoding='utf-8'))
CLIPS = {c['id']: c for c in json.loads((ROOT / 'motion-library/data/index.json').read_text(encoding='utf-8'))['clips']}

CSS = """/* Motion records block (generated) */
.motion-block{border-top:1px solid var(--line, #1E2D3D);padding:clamp(44px,5vw,80px) clamp(20px,5.5vw,80px)}
.mb-inner{max-width:1280px;margin:0 auto}
.mb-narrow.motion-block{padding:clamp(36px,4vw,64px) 0}
.mb-narrow .mb-inner{max-width:1052px}
.motion-block .mb-head{display:flex;justify-content:space-between;align-items:baseline;gap:20px;flex-wrap:wrap;margin-bottom:22px}
.motion-block h2{margin:8px 0 0;font-size:clamp(22px,2.4vw,32px);font-weight:500;letter-spacing:-.03em}
.motion-block .mb-lede{margin:12px 0 0;color:#A9BACB;font-size:14px;line-height:1.7;max-width:62ch}
.mb-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:26px}
.mb-card{display:block;text-decoration:none;border:1px solid var(--line, #1E2D3D);background:#0A1420;overflow:hidden;transition:border-color .2s,transform .2s}
.mb-card:hover{border-color:var(--accent, #4AA8C8);transform:translateY(-2px)}
.mb-card img{display:block;width:100%;aspect-ratio:16/10;object-fit:cover;background:#04101C}
.mb-card-body{padding:12px 14px 14px}
.mb-card-name{font-size:13.5px;font-weight:600;color:#F0F4F8;letter-spacing:-.01em}
.mb-card-spec{font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:#8FA3B5;margin-top:5px}
.mb-chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:26px}
.mb-chip{font-size:12px;color:#A8DCEF;border:1px solid var(--line, #1E2D3D);background:rgba(74,168,200,.06);padding:5px 11px;text-decoration:none}
.mb-chip:hover{border-color:var(--accent, #4AA8C8);color:#fff}
.mb-foot{margin:22px 0 0;font-size:12.5px;color:#8FA3B5}
.mb-foot a{color:#A8DCEF;border-bottom:1px solid #4AA8C8;text-decoration:none}
@media(max-width:820px){.mb-grid{grid-template-columns:1fr 1fr}}
@media(max-width:560px){.mb-grid{grid-template-columns:1fr}}
"""

def block(slug, title, wide=True):
    cls = DATA['models'].get(slug)
    if not cls:
        return None
    set_ids = DATA['clipSets'].get(cls, [])
    if set_ids:
        cards = []
        for cid in set_ids:
            c = CLIPS[cid]
            cards.append(
                f'<a class="mb-card" href="/motion-library/?clip={cid}">'
                f'<img src="/motion-library/thumbs/{cid}.webp" alt="{html.escape(c["name"])} — 23-joint rig" loading="lazy" decoding="async">'
                f'<div class="mb-card-body"><div class="mb-card-name">{html.escape(c["name"])}</div>'
                f'<div class="mb-card-spec">{c["group"]} · {c["seconds"]:g} s · {c["fps"]:g} fps</div></div></a>')
        body = ('<p class="mb-lede">The clips this platform is tested against before delivery. '
                'Each one opens in the library viewer on the rig that performs it.</p>'
                '<div class="mb-grid">' + ''.join(cards) + '</div>')
    else:
        cats = DATA['recordCats'][cls]
        chips = ''.join(f'<a class="mb-chip" href="/library.html?cat={c}">{c} records</a>' for c in cats)
        body = ('<p class="mb-lede">No humanoid motion set applies to this body. It is validated against '
                'the licensed catalogue records for the movement it actually performs.</p>'
                f'<div class="mb-chips">{chips}</div>')
    return (f'<!--MOTION:START — generated from motion-library/models.json, edit there and re-run tools/build_motion_blocks.py-->\n'
            f'<style>{CSS}</style>\n'
            f'<section class="motion-block{" motion-block--wide" if wide else " mb-narrow"}" aria-labelledby="mb-heading"><div class="mb-inner">\n'
            f'<div class="mb-head"><div><p class="eyebrow">Motion library</p>'
            f'<h2 id="mb-heading">What {html.escape(title)} is tested against</h2></div></div>\n'
            f'{body}\n'
            f'<p class="mb-foot">Full library: 26 playable clips and 25 licensed records — '
            f'<a href="/motion-library/">3D viewer</a> · <a href="/library.html">searchable catalogue</a></p>\n'
            f'</div></section>\n<!--MOTION:END-->\n')

changed = []
for page in sorted((ROOT / 'products').glob('*.html')):
    slug = page.stem
    src = page.read_text(encoding='utf-8')
    m = re.search(r'<h1[^>]*>(.*?)</h1>', src, re.S)
    title = re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else slug
    new = block(slug, title, wide=('companion-section' not in src))
    if not new:
        print('no class for', slug); continue
    if '<!--MOTION:START' in src:
        src = re.sub(r'<!--MOTION:START.*?<!--MOTION:END-->\n?', new, src, flags=re.S)
    else:
        anchor = '<section class="inquiry-section">'
        if anchor not in src:
            anchor = '</main>'
        if anchor not in src:
            print('no anchor in', slug); continue
        src = src.replace(anchor, new + anchor, 1)
    page.write_text(src, encoding='utf-8')
    changed.append(slug)

print('updated', len(changed), 'pages')
