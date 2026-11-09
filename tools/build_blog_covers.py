"""Generate blog covers in one photographic system.

Half the draft posts have no cover at all and the rest are a mix of studio renders
and one warehouse shot, so the blog index looks like three different publications.
This writes one 16:9 editorial photograph per draft post, same light, same palette,
subject tied to what the article is actually about.

Source of truth for WHICH posts: blog-posts.json (status: draft).
Output: blog/covers/<slug>.jpg at 1600x900.

    python tools/build_blog_covers.py [--only slug,slug] [--force] [--dry-run]
"""
import argparse
import concurrent.futures as cf
import io
import json
import os
import pathlib
import time
import urllib.request

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
COVERS = ROOT / 'blog/covers'
FAL_URL = 'https://fal.run/fal-ai/flux/dev'

STYLE = ('Editorial documentary photograph for a robotics industry publication. '
         '{scene} Shot on a 35mm full-frame camera, available light with one warm practical lamp, '
         'deep shadows, muted cool palette, near-black background falloff, fine film grain, '
         'shallow depth of field, one clear focal point, generous empty space, clean uncluttered set, '
         'nothing on the surfaces except the subject. No text, no logos, no watermarks, no interfaces. {anatomy}')

SCENES = {
    'inspection-robot-dog-patrol-round': 'A quadruped inspection robot with a sensor mast walking an industrial plant corridor at night, pipes and pressure gauges along the wall.',
    'humanoid-robot-university-labs': 'A humanoid robot standing beside a workbench in a university robotics laboratory, student desks softly out of focus behind it.',
    'humanoid-robot-examples': 'A humanoid robot seated at an assembly bench fitting a machined component with its hands, tools laid out beside it.',
    'humanoid-robot-jobs': 'A humanoid robot working beside a human technician inside an assembly cell, both focused on the same part.',
    'humanoid-robot-price-what-moves-it': 'A humanoid robot torso mounted on a service stand in a workshop, actuators and cabling visible, hand tools on the bench.',
    'quadruped-robot-dog-models': 'Three quadruped robots of different sizes lined up on a pale concrete floor in a bright testing hall with tall windows, side daylight, clean silhouettes.',
    'quadruped-robot-kit-teaching-research': 'A small quadruped robot kit on a laboratory bench beside an open laptop and hand tools.',
    'quadruped-robot-price-decisions': 'A quadruped robot standing next to an open shipping crate with foam inserts, warehouse lighting.',
    'how-much-is-a-robot-dog': 'A quadruped robot climbing an outdoor concrete stair at first light, long shadows on the steps.',
    'what-is-a-robot-dog': 'A four-legged robot dog standing on a rooftop terrace at dusk with city lights behind it, three-quarter view, rim light along its back.',
    'service-robot-after-the-demo': 'A floor-cleaning robot working alone across a hotel lobby at night, empty seating, marble floor reflecting the machine.',
    'delivery-robots-australia': 'A small delivery robot crossing a quiet city footpath at dusk, wet pavement reflecting the streetlights.',
    'restaurant-service-robot-floor-plan': 'A restaurant service robot carrying a loaded tray moving between set tables in a dim dining room.',
    'hotel-delivery-robot': 'A delivery robot waiting beside a hotel lift at night, warm sconce light on the brushed metal doors, clearly lit machine.',
    'service-robots-examples': 'A mixed fleet of service robots of different shapes standing on a polished concrete floor, seen from a low angle.',
    'how-to-buy-commercial-robot-australia': 'A commercial mobile service robot on a loading dock being inspected by an engineer holding a clipboard, daylight through the roller door.',
    'robot-hire-australia': 'A cleaning robot strapped to a timber pallet, ready for dispatch in a distribution centre.',
    'autonomous-mobile-robots-vocabulary': 'An autonomous mobile robot carrying a tote passing a warehouse worker in a narrow aisle.',
    'warehouse-robot-cleaner': 'A ride-on floor scrubber cleaning a warehouse aisle between pallet racks, overhead lights on, wet sheen on the concrete.',
    'inspection-robot-price': 'Close three-quarter detail of the sensor head on a quadruped inspection robot, lidar dome and camera cluster, lit from one side against darkness.',
    'commercial-cleaning-robots-australia': 'A cleaning robot working through an empty airport terminal at night, departure boards dark.',
    'floor-scrubber-robot-which-floor': 'A floor scrubber robot at the edge where polished concrete meets tile, water sheen on the floor.',
    'are-cleaning-robots-worth-it': 'A cleaning robot and a cleaner with a mop working in the same corridor, both visible, honest comparison.',
    'floor-cleaning-robot-australia': 'A cleaning robot working under the skylight of a shopping mall atrium, closed shops around.',
    'gausium-phantas-mapping': 'A cleaning robot with a raised lidar turret crossing a tiled lobby floor, side light, faint reflection under the machine.',
    'keenon-c40-datasheet': 'A compact commercial cleaning robot three-quarter view in a hotel lobby beside a glass wall, full machine visible, clean empty floor.',
    'robots-that-clean-where-they-stop': 'A cleaning robot stopped at the threshold of an open doorway, a person standing beyond it in the next room.',
    'humanoid-robot-research-projects': 'Two pairs of hands adjusting the arm of a humanoid robot mounted on a test stand, tight crop, laboratory bench below.',
    'human-robot-interaction-research': 'A person standing at conversational distance facing a humanoid robot in a laboratory, both lit from the side.',
    'cost-to-build-a-humanoid-robot': 'A humanoid robot standing on a steel build frame in a workshop with a neat row of actuators on a bench beside it, cool overhead light.',
}


def load_posts():
    posts = json.loads((ROOT / 'blog-posts.json').read_text(encoding='utf-8'))
    return [p for p in posts if p.get('status') == 'draft']


def generate(post, key, force=False):
    slug = post['slug']
    out = COVERS / f'{slug}.jpg'
    if out.exists() and not force:
        return slug, 'kept'
    scene = SCENES.get(slug)
    if not scene:
        return slug, 'no scene defined'
    if 'quadruped' in scene or 'robot dog' in scene:
        anatomy = ('The subject is a four-legged robot dog: four legs, low horizontal body, sensor head, '
                   'no arms, no upright torso, no humanoid shape.')
    elif 'humanoid' in scene:
        anatomy = 'The subject is a bipedal humanoid robot: two legs, two arms, a head with a sensor face.'
    else:
        anatomy = ''
    body = json.dumps({
        'prompt': STYLE.format(scene=scene, anatomy=anatomy),
        'image_size': {'width': 1536, 'height': 864},
        'num_inference_steps': 28,
        'guidance_scale': 3.2,
        'num_images': 1,
        'enable_safety_checker': True,
    }).encode()
    req = urllib.request.Request(FAL_URL, data=body, headers={
        'Authorization': f'Key {key}', 'Content-Type': 'application/json'})
    for attempt in range(3):
        try:
            data = json.load(urllib.request.urlopen(req, timeout=180))
            url = data['images'][0]['url']
            raw = urllib.request.urlopen(url, timeout=120).read()
            img = Image.open(io.BytesIO(raw)).convert('RGB')
            # Lock the card ratio: cover-crop to 16:9 at 1600x900.
            target = 16 / 9
            w, h = img.size
            if w / h > target:
                nw = int(h * target)
                img = img.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
            else:
                nh = int(w / target)
                img = img.crop((0, (h - nh) // 2, w, (h + nh) // 2))
            img.resize((1600, 900), Image.LANCZOS).save(out, quality=88, optimize=True)
            return slug, 'ok'
        except Exception as exc:  # noqa: BLE001 — report and retry
            if attempt == 2:
                return slug, f'failed: {str(exc)[:80]}'
            time.sleep(3 + attempt * 4)
    return slug, 'failed'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default='')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    posts = load_posts()
    if args.only:
        wanted = {s.strip() for s in args.only.split(',')}
        posts = [p for p in posts if p['slug'] in wanted]
    missing = [p['slug'] for p in posts if p['slug'] not in SCENES]
    if missing:
        print('no scene for:', ', '.join(missing))
    if args.dry_run:
        for p in posts:
            print(('scene: ' if p['slug'] in SCENES else 'MISSING: ') + p['slug'])
        return

    key = ''
    for line in (pathlib.Path.home() / 'AppData/Local/hermes/.env').read_text(encoding='utf-8', errors='replace').splitlines():
        if line.startswith('FAL_KEY='):
            key = line.split('=', 1)[1].strip().strip('"')
    if not key:
        raise SystemExit('FAL_KEY missing from hermes .env')

    COVERS.mkdir(parents=True, exist_ok=True)
    todo = [p for p in posts if p['slug'] in SCENES]
    done = 0
    with cf.ThreadPoolExecutor(max_workers=3) as pool:
        for slug, status in pool.map(lambda p: generate(p, key, args.force), todo):
            done += 1
            print(f'{done:2}/{len(todo)} {slug:48} {status}')


if __name__ == '__main__':
    main()
