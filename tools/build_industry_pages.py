"""Rewrite the retail and warehousing industry pages properly.

facilities.html and hotels.html already speak to their own trade. retail.html and
warehousing.html were 88% identical to the facilities page — same headline, same
two cleaning robots, same copy — so a showroom visitor read about contract cleaners
and a warehouse visitor read about hotel floors.

This rewrites the body of each page (hero, what you can buy, the machines, the
assessment, the FAQ, the close) from the same markup as facilities.html so the CSS
never changes, and picks the machines each trade can actually use from the
catalogue. Manufacturer numbers stay labelled as manufacturer numbers.

Run:  python tools/build_industry_pages.py [--dry-run]
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

HERO = '''<section class="ho-hero" aria-labelledby="hotel-title">
    <div class="ho-wrap">
      <div class="ho-intro">
        <p class="ho-eyebrow">Robotist / {eyebrow}</p>
        <h1 id="hotel-title">{h1}</h1>
      </div>
      <div class="ho-hero-bottom">
        <p class="ho-hero-lead">{lead}</p>
        <div class="ho-hero-bottom-right">
          <p>{intro}</p>
          <div class="ho-actions">
            <a href="/contact.html" onclick="openInquiry();return false" class="btn-primary">Talk to us about your {site} ↗</a>
            <a href="#capabilities" class="ho-link">See how it works <span aria-hidden="true">↘</span></a>
          </div>
        </div>
      </div>
      <figure class="ho-blueprint">
        <div class="ho-blueprint-top"><span>{plan_kicker}</span><strong>{plan_title}</strong></div>
        <div class="ho-map">
          <svg viewBox="0 0 1120 425" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="floor-title floor-desc">
            <title id="floor-title">{plan_alt}</title>
            <desc id="floor-desc">{plan_desc}</desc>
            <defs>
              <pattern id="floor-grid" width="26" height="26" patternUnits="userSpaceOnUse"><path d="M26 0H0V26" fill="none" stroke="var(--grey-3)" stroke-width=".65" opacity=".6"/></pattern>
              <marker id="floor-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="var(--accent)"/></marker>
            </defs>
            <rect width="1120" height="425" fill="url(#floor-grid)"/>
            <g fill="var(--bg-2)" stroke="var(--grey-2)" stroke-width="1.3">
              <rect x="56" y="55" width="367" height="198" rx="2"/>
              <rect x="443" y="55" width="222" height="90" rx="2"/>
              <rect x="682" y="55" width="376" height="90" rx="2"/>
              <rect x="443" y="165" width="615" height="88" rx="2"/>
              <rect x="56" y="276" width="700" height="95" rx="2"/>
              <rect x="778" y="276" width="280" height="95" rx="2"/>
            </g>
            <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif" fill="var(--grey-1)" font-size="12" letter-spacing="2">
              <text x="79" y="84">{room_1}</text><text x="466" y="83">{room_2}</text><text x="706" y="83">{room_3}</text>
              <text x="465" y="193">{room_4}</text><text x="79" y="305">{room_5}</text><text x="802" y="305">{room_6}</text>
            </g>
            <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif" fill="var(--grey-2)" font-size="12">
              <text x="80" y="103">{note_1}</text><text x="465" y="103">{note_2}</text><text x="706" y="103">{note_3}</text>
              <text x="79" y="326">{note_4}</text><text x="802" y="326">{note_5}</text>
            </g>
            <path d="M103 213 V133 H365 V216 H519 V210 H892" fill="none" stroke="var(--accent)" stroke-width="3.6" marker-end="url(#floor-arrow)"/>
            <path d="M519 210 V335 H684" fill="none" stroke="var(--accent)" stroke-width="3.6" stroke-dasharray="10 9"/>
            <path d="M892 210 V335 H942" fill="none" stroke="var(--accent)" stroke-width="3.6" stroke-dasharray="10 9"/>
            <g fill="var(--accent-light)" stroke="var(--bg-0)" stroke-width="3">
              <circle cx="103" cy="213" r="10"/><circle cx="365" cy="216" r="10"/>
              <circle cx="519" cy="210" r="10"/><circle cx="892" cy="210" r="10"/>
            </g>
            <g fill="var(--bg-0)" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif" font-size="10" font-weight="700" text-anchor="middle">
              <text x="103" y="217">1</text><text x="365" y="220">2</text><text x="519" y="214">3</text><text x="892" y="214">4</text>
            </g>
            <g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif" fill="var(--accent-light)" font-size="11" letter-spacing="1.3">
              <text x="538" y="320">{check_a}</text><text x="803" y="389">{check_b}</text>
            </g>
            <path d="M112 393 H363" stroke="var(--grey-2)" stroke-width="1"/>
            <text x="112" y="408" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif" fill="var(--grey-1)" font-size="10" letter-spacing="1.3">NOT TO SCALE</text>
          </svg>
        </div>
        <ol class="ho-map-mobile" aria-label="Example assessment route">{mobile}</ol>
        <figcaption class="ho-blueprint-bottom">
          <span class="ho-key"><span><i aria-hidden="true"></i>Proposed route</span><span><i class="dash" aria-hidden="true"></i>Needs checking on site</span></span>
          <span class="ho-map-note">Example diagram. Not a finished installation, and not a promise of speed or coverage.</span>
        </figcaption>
      </figure>
    </div>
  </section>'''

CAPABILITIES = '''<section class="ho-section ho-tiers" id="capabilities" aria-labelledby="capabilities-title">
    <div class="ho-wrap">
      <div class="ho-heading-row">
        <div><p class="ho-eyebrow">What you can buy today</p><h2 id="capabilities-title">{title}</h2></div>
        <p class="ho-copy">{intro}</p>
      </div>
      <div class="ho-tier-list">{tiers}</div>
    </div>
  </section>'''

TIER = '''<article class="ho-tier">
          <div class="ho-tier-label"><span class="ho-tier-num">{num}</span><h3 class="ho-tier-word">{word}</h3></div>
          <div class="ho-tier-text"><h3>{h}</h3><p>{p}</p><span class="ho-tier-detail">{detail}</span></div>
        </article>'''

MACHINES = '''<section class="ho-section ho-products" id="machines" aria-labelledby="machines-title">
    <div class="ho-wrap">
      <div class="ho-products-head"><p class="ho-eyebrow">The machines</p><h2 id="machines-title">{title}</h2><p class="ho-copy">{intro}</p></div>
      <div class="ho-product-grid">{cards}</div>
      <a class="ho-panther" href="{wide_url}" aria-label="{wide_aria}">
        <div class="ho-panther-content"><span class="ho-machine-sub">{wide_sub}</span><h3 class="ho-machine-title">{wide_name}</h3><p>{wide_p}</p><div class="ho-panther-stats"><span>{wide_stat1}<small>{wide_stat1_l}</small></span><span>{wide_stat2}<small>{wide_stat2_l}</small></span></div><div class="ho-machine-bottom"><span class="ho-price"><small>Catalogue price / USD</small>{wide_price}</span><span class="ho-arrow">View machine ↗</span></div></div>
        <div class="ho-panther-visual"><img src="{wide_img}" loading="lazy" alt="{wide_alt}" width="500" height="560"></div>
      </a>
      <p class="ho-manufacturer-note">{note}</p>
    </div>
  </section>'''

CARD = '''<a class="ho-machine" href="{url}" aria-label="{aria}">
          <div class="ho-machine-visual"><span class="ho-machine-index">{index}</span><img src="{img}" loading="lazy" alt="{alt}" width="420" height="380"></div>
          <div class="ho-machine-body"><span class="ho-machine-sub">{sub}</span><h3 class="ho-machine-title">{name}</h3><p>{p}</p><div class="ho-machine-bottom"><span class="ho-price"><small>Catalogue price / USD</small>{price}</span><span class="ho-arrow">View machine ↗</span></div></div>
        </a>'''

PROOF = '''<section class="ho-section ho-proof" id="assessment" aria-labelledby="assessment-title">
    <div class="ho-wrap">
      <div class="ho-proof-head"><div><p class="ho-eyebrow">From demo to decision</p><h2 id="assessment-title">{title}</h2></div><p class="ho-copy">{intro}</p></div>
      <div class="ho-proof-steps">
        <article class="ho-proof-step"><span class="ho-step-no">Step 1</span><h3>Walk the {site}</h3><p>{step1}</p></article>
        <article class="ho-proof-step"><span class="ho-step-no">Step 2</span><h3>Write the job down</h3><p>Which areas, which hours, what the result has to look like, what staff still do and what the robot will not do — agreed before a model is picked.</p></article>
        <article class="ho-proof-step"><span class="ho-step-no">Step 3</span><h3>Test it if practical</h3><p>One route or one task, measured against the agreed numbers, including disruption to people and how often staff had to step in.</p></article>
        <article class="ho-proof-step"><span class="ho-step-no">Step 4</span><h3>Put it in the proposal</h3><p>The chosen system, the test results, the full cost, what your {site} has to provide, staff training, how we will judge the result and who fixes it.</p></article>
      </div>
      <div class="ho-proof-criteria"><div><p class="ho-eyebrow">What a proposal should show</p><h3>{crit_title}</h3></div><ul aria-label="Site evaluation criteria">{crit}</ul></div>
      <div class="ho-evidence"><h3>{ev_title}</h3><p>{ev_p}</p></div>
    </div>
  </section>'''

FAQ = '''<section class="ho-section ho-faq-section" id="faq" aria-labelledby="faq-title">
    <div class="ho-wrap ho-faq-grid"><div class="ho-faq-heading"><p class="ho-eyebrow">Before you buy</p><h2 id="faq-title">Questions <strong>worth asking.</strong></h2></div>
      <div class="ho-faq">{items}</div>
    </div>
  </section>'''

DECISION = '''<section class="ho-decision" aria-labelledby="decision-title">
    <div class="ho-wrap ho-decision-inner"><div><p class="ho-eyebrow">The next step</p><h2 id="decision-title">{title}</h2></div><div class="ho-decision-aside"><p>{p}</p><a href="/contact.html" onclick="openInquiry();return false" class="btn-primary">{cta} ↗</a></div></div>
  </section>
</main>'''


def tier(num, word, h, p, detail):
    return TIER.format(num=num, word=word, h=h, p=p, detail=detail)


def card(index, url, aria, img, alt, sub, name, p, price):
    return CARD.format(index=index, url=url, aria=aria, img=img, alt=alt, sub=sub, name=name, p=p, price=price)


def faq_item(q, a):
    return f'<details><summary>{q}</summary><p>{a}</p></details>'


PAGES = {
    'retail.html': {
        'title': 'Retail &amp; Showroom Robots - Robotist | Floor Care, Greeters, Stock Checks',
        'desc': 'Cleaning robots for stores, showrooms and shopping centres, plus what a customer-facing robot can and cannot do today. Catalogue prices, honest limits, a site check before you buy.',
        'eyebrow': 'Retail &amp; showrooms',
        'h1': 'Retail robots<br>for stores,<br><span>showrooms and centres.</span>',
        'lead': 'A shopping centre floor is walked thousands of times a day. A showroom floor has to look right before the doors open.',
        'intro': 'We sell floor-cleaning robots for stores and centres, and we trial front-of-house robots before anyone promises a greeter. Picking, restocking and stock moves are not in the catalogue — we say that rather than pretend.',
        'site': 'store',
        'plan_kicker': 'Example: a retail floor',
        'plan_title': 'Start here — the floor',
        'plan_alt': 'Example retail floor plan, with the areas still to be checked marked',
        'plan_desc': 'Example map of a retail floor. The dashed parts are what we still have to check on site: floor changes, customer traffic and charging access. This is an illustration, not a survey.',
        'room_1': '01 / ENTRANCE', 'room_2': 'FITTING ROOMS', 'room_3': 'TILLS',
        'room_4': 'MAIN AISLE', 'room_5': '02 / KIDS AREA', 'room_6': 'CHARGER',
        'note_1': 'polished tile', 'note_2': 'floor change', 'note_3': 'customer traffic',
        'note_4': 'tile + carpet', 'note_5': 'power access',
        'check_a': 'CHECK FLOOR CHANGE', 'check_b': 'CHECK CHARGING ACCESS',
        'mobile': (
            '<li><span class="n">01</span><span><strong>Entrance</strong><span class="s">Polished tile and mats — route to be checked on site</span></span></li>'
            '<li><span class="n">02</span><span><strong>Fitting rooms</strong><span class="s">Mixed floors — cleaning hours agreed around trading</span></span></li>'
            '<li><span class="n">03</span><span><strong>Main aisle</strong><span class="s">Busiest all day — night route to be agreed</span></span></li>'
            '<li><span class="n">04</span><span><strong>Tills</strong><span class="s">Display stands and cabling — we agree where staff step in</span></span></li>'
            '<li><span class="n">05</span><span><strong>Charger</strong><span class="s">Power access to be checked on site</span></span></li>'
        ),
        'cap_title': 'What you can buy now, <strong>and what needs a trial.</strong>',
        'cap_intro': 'Cleaning a large shop floor after hours is a purchase. A robot that talks to customers is a trial. Moving stock around is neither, yet.',
        'tiers': (
            tier('01', 'In catalogue.', 'Floor care after trading',
                 'The Gausium Phantas and Keenon C40-P1 sweep, scrub and mop on their own. Before we recommend one we check your floor types, your closing time, how the machine behaves with a customer standing in the aisle, and the finish you expect at opening.',
                 'In catalogue / Measured in your store') +
            tier('02', 'Trial first.', 'Greeting and product questions',
                 'A robot can answer a fixed list — opening hours, where a brand sits, whether an item is in stock — and pass everything else to your staff. We test the answers, the voice, the languages, the privacy and how customers actually react before it runs on a busy Saturday.',
                 'Limited scope / Staff oversight') +
            tier('03', 'Not yet.', 'Picking, restocking and stock moves',
                 'Nothing in our catalogue lifts stock off a shelf or moves a pallet to the floor. That work needs shelf-level manipulation and a link into your stock or POS system. It is an engineering project quoted per site, not a product on a price list.',
                 'Not in catalogue / Project only')
        ),
        'mach_title': 'Three machines, <strong>three different jobs.</strong>',
        'mach_intro': 'Two industrial cleaners for the floor. One service robot on wheels for a greeting trial. The job picks the machine, not the other way round.',
        'cards': (
            card('Machine 01 / Floor care', '/products/gausium-phantas.html',
                 'Explore Gausium Phantas cleaning robot', '/robots-cut/gausium_phantas.webp',
                 'Gausium Phantas commercial cleaning robot', 'Four-in-one cleaning', 'Gausium Phantas',
                 'Sweeps, scrubs, vacuums and mops in one pass. Manufacturer figures: 1,180 m² cleaned per hour — sized for centres and large-format stores.', '$9,250') +
            card('Machine 02 / Floor care', '/products/keenon-c40-p1.html',
                 'Explore Keenon C40-P1 cleaning robot', '/robots-cut/keenon_c40-p1.webp',
                 'Keenon C40-P1 commercial cleaning robot', 'Four-in-one cleaning', 'Keenon C40-P1',
                 'A commercial floor cleaner with a long shift. Manufacturer figures: 1,100 m² per hour, up to 15 hours on one charge — suits a store that cleans nightly.', '$10,700')
        ),
        'wide_url': '/products/unix-ai-wanda.html',
        'wide_aria': 'Explore UniX AI Wanda 2.0 service robot',
        'wide_sub': 'Machine 03 / Greeting trials',
        'wide_name': 'UniX AI Wanda 2.0',
        'wide_p': 'A wheeled humanoid sold for service work in public spaces: greeting, wayfinding, a scripted answer. We treat it as a trial candidate, not a proven shop assistant.',
        'wide_stat1': '33', 'wide_stat1_l': 'DOF, top variant',
        'wide_stat2': '8', 'wide_stat2_l': 'DoF bionic arms',
        'wide_price': '$54,900',
        'wide_img': '/robots-cut/unix_wanda.webp',
        'wide_alt': 'UniX AI Wanda 2.0 wheeled humanoid service robot',
        'mach_note': 'These are catalogue prices. Freight, setup, connecting it to your systems, training and support are extra. Every speed, runtime and coverage number above is the manufacturer\'s specification — we have not measured these machines in a retail store.',
        'proof_title': 'A demo is not <strong>a trading day.</strong>',
        'proof_intro': 'A robot can look good in a showroom. We turn that into a written plan for your store: which areas, which hours, what the floor has to look like at opening, and who is responsible when it is not.',
        'step1': 'Floor plans, floor types, matting, display stands, foot traffic, closing times, power outlets and the alarm and door systems involved.',
        'crit_title': 'Your store is the test, not the showroom.',
        'crit': '<li>Floor finish at opening</li><li>Routes completed</li><li>Times staff step in</li><li>Customer reaction</li><li>Cost per clean</li><li>Who handles repairs</li>',
        'ev_title': 'We have no retail case study <strong>yet.</strong>',
        'ev_p': 'Robotist has not published a verified installation in a retail store or shopping centre. Manufacturer figures describe equipment, not results on your floor. When we have real results from a site we will publish them. Until then, we say that plainly.',
        'faqs': (
            faq_item('Can it clean while the store is open?',
                     'Sometimes, depending on the layout and the machine. Cleaning after closing is easier to plan and easier to measure. A site check looks at customer traffic, the route and how the robot reacts when someone steps in front of it.') +
            faq_item('Will it mark a polished or sealed floor?',
                     'That depends on the machine, the pad and the cleaning agent. Polished concrete, sealed tile and vinyl are checked against the manufacturer\'s specification and, where practical, tested on a patch of your own floor before a schedule is agreed.') +
            faq_item('How does it cope with displays and stock on the floor?',
                     'The store is mapped first, and displays that move often are agreed as no-go zones or rescanned as part of the route. A store that rearranges weekly needs that routine built in, not assumed.') +
            faq_item('Can a robot greet customers and answer questions?',
                     'A fixed script, yes: hours, directions, a stock lookup if your system allows it. Anything outside the script goes to a person. We trial it at your store and measure the answers before it runs unsupervised.') +
            faq_item('Does it connect to our POS or stock system?',
                     'Only if that integration is scoped and quoted. None of the machines above ship with a link into a retail POS or stock system. We will tell you what is possible rather than assume it.') +
            faq_item('Can we try one before buying?',
                     'Yes. We start with a review of your store and agree what will be measured. A trial is included when it is practical and agreed in scope, and the results go into the proposal.')
        ),
        'dec_title': 'Start with <strong>your floor.</strong>',
        'dec_p': 'Tell us the floor area, the closing time and what the store has to look like at opening. We will tell you what the first site check covers, what your store needs, and what we still have to check.',
        'cta': 'Talk to us about your store',
    },
    'warehousing.html': {
        'title': 'Warehousing &amp; Logistics Robots - Robotist | Floor Care, Inspection, Handling Trials',
        'desc': 'Cleaning robots for large warehouse floors, quadruped platforms for inspection rounds, and humanoid handling quoted as a project. Catalogue prices, honest limits, a site check before you buy.',
        'eyebrow': 'Warehousing &amp; logistics',
        'h1': 'Robots for warehouses,<br>depots and<br><span>distribution centres.</span>',
        'lead': 'The same aisles get walked hundreds of times a night, and the floor is cleaned between shifts when nothing else is moving.',
        'intro': 'We sell floor-cleaning robots for large floors, we supply quadruped platforms for inspection rounds, and we quote humanoid handling as a project. Automated forklifts and shuttle systems are not in our catalogue — no pretending otherwise.',
        'site': 'warehouse',
        'plan_kicker': 'Example: a warehouse floor',
        'plan_title': 'Start here — the floor',
        'plan_alt': 'Example warehouse floor plan, with the areas still to be checked marked',
        'plan_desc': 'Example map of a warehouse floor. The dashed parts are what we still have to check on site: level changes, pallet traffic and charging access. This is an illustration, not a survey.',
        'room_1': '01 / LOADING DOCK', 'room_2': 'RACKING A', 'room_3': 'RACKING B',
        'room_4': 'MAIN AISLE', 'room_5': '02 / PACKING', 'room_6': 'CHARGER',
        'note_1': 'sealed concrete', 'note_2': 'level change', 'note_3': 'pallet traffic',
        'note_4': 'dock apron', 'note_5': 'power access',
        'check_a': 'CHECK LEVEL CHANGE', 'check_b': 'CHECK CHARGING ACCESS',
        'mobile': (
            '<li><span class="n">01</span><span><strong>Loading dock</strong><span class="s">Dock apron and levellers — route to be checked on site</span></span></li>'
            '<li><span class="n">02</span><span><strong>Racking A</strong><span class="s">Narrow aisles — cleaning window agreed around pick shifts</span></span></li>'
            '<li><span class="n">03</span><span><strong>Main aisle</strong><span class="s">Pallet traffic all night — route and safety agreed first</span></span></li>'
            '<li><span class="n">04</span><span><strong>Packing</strong><span class="s">Debris and tape on the floor — we agree who clears first</span></span></li>'
            '<li><span class="n">05</span><span><strong>Charger</strong><span class="s">Power access to be checked on site</span></span></li>'
        ),
        'cap_title': 'What you can buy now, <strong>and what is a project.</strong>',
        'cap_intro': 'A big open floor between shifts is the easy case. Inspection rounds need a network and a safety review. Moving goods needs engineering, not a purchase order.',
        'tiers': (
            tier('01', 'In catalogue.', 'Floor care between shifts',
                 'The Gausium Phantas sweeps, scrubs and mops a large open floor and works best when nothing else is moving. Before we recommend it we check floor condition, aisle width, debris, dock run-off and the window between shifts.',
                 'In catalogue / Measured on your floor') +
            tier('02', 'Project.', 'Night inspection rounds',
                 'A quadruped walks a route and carries cameras or sensors — the MagicLab MagicDog Y1 is listed at 6 m/s with a 45 kg payload. What it needs is a patrol route, network coverage through the racking, a safety review and someone to read the output.',
                 'Quoted per project / Network and safety check first') +
            tier('03', 'Not in catalogue.', 'Moving pallets and totes',
                 'No machine on our price list lifts a pallet or feeds a pick line. Automated forklifts, conveyors and shuttle systems are bought per project with a systems integrator and a link into your warehouse management system. We say so instead of selling you a humanoid as a forklift.',
                 'Not in catalogue / Systems project')
        ),
        'mach_title': 'Three machines, <strong>three different jobs.</strong>',
        'mach_intro': 'One floor cleaner for the aisles, one quadruped for the rounds, one humanoid we quote for handling trials. None of them replaces a forklift.',
        'cards': (
            card('Machine 01 / Floor care', '/products/gausium-phantas.html',
                 'Explore Gausium Phantas cleaning robot', '/robots-cut/gausium_phantas.webp',
                 'Gausium Phantas commercial cleaning robot', 'Four-in-one cleaning', 'Gausium Phantas',
                 'Sweeps, scrubs, vacuums and mops in one pass. Manufacturer figures: 1,180 m² cleaned per hour — the size that suits a distribution floor.', '$9,250') +
            card('Machine 02 / Inspection', '/products/magiclab-magicdog-y1.html',
                 'Explore MagicLab MagicDog Y1 quadruped', '/robots-cut/magiclab_magicdog_y1.webp',
                 'MagicLab MagicDog Y1 industrial quadruped robot', 'Industrial quadruped', 'MagicLab MagicDog Y1',
                 'A camera and sensor carrier for routes a wheeled machine cannot take. Manufacturer figures: 6 m/s top speed, 45 kg payload, all-terrain.', '$64,900')
        ),
        'wide_url': '/products/kepler-spe-bumblebee.html',
        'wide_aria': 'Explore Kepler S-PE BumbleBee humanoid',
        'wide_sub': 'Machine 03 / Handling trials',
        'wide_name': 'Kepler S-PE BumbleBee',
        'wide_p': 'A 30-DOF humanoid with onboard perception, sold for research, logistics and industrial trials. We quote it for a measured handling trial — not as a proven warehouse worker.',
        'wide_stat1': '30', 'wide_stat1_l': 'Degrees of freedom',
        'wide_stat2': '100', 'wide_stat2_l': 'TOPS compute',
        'wide_price': '$88,000',
        'wide_img': '/robots-cut/kepler_spe_bumblebee.webp',
        'wide_alt': 'Kepler S-PE BumbleBee humanoid robot',
        'mach_note': 'These are catalogue prices. Freight, setup, integration, training and support are extra. Every speed, payload and coverage number above is the manufacturer\'s specification — we have not measured these machines in a warehouse.',
        'proof_title': 'A demo is not <strong>a night shift.</strong>',
        'proof_intro': 'A robot can look good on a polished showroom floor. We turn that into a written plan for your site: which aisles, which window, what the floor has to look like at shift start, and who is responsible when it is not.',
        'step1': 'Floor plans, floor condition, aisle widths, racking layout, debris, dock traffic, shift times, power outlets, network coverage and the safety systems involved.',
        'crit_title': 'Your floor is the test, not the showroom.',
        'crit': '<li>Floor cleaned before shift start</li><li>Routes completed</li><li>Safety incidents and near misses</li><li>Times staff step in</li><li>Cost per night</li><li>Who handles repairs</li>',
        'ev_title': 'We have no warehousing case study <strong>yet.</strong>',
        'ev_p': 'Robotist has not published a verified installation in a warehouse or distribution centre. Manufacturer figures describe equipment, not results on your floor. When we have real results from a site we will publish them. Until then, we say that plainly.',
        'faqs': (
            faq_item('Should it clean during the shift or between shifts?',
                     'Between shifts is easier and safer: an empty floor, a fixed window, a measurable result. Cleaning while pickers are working is possible but needs the route, the safety zones and the speed agreed with your team first.') +
            faq_item('Can it handle dust, tape and packing debris?',
                     'A scrubber is built for dust and general floor dirt, not for wrapping, strapping or spilled product. If debris collects on the floor, someone clears it first — the site check agrees who and when.') +
            faq_item('What happens when pallets block the route?',
                     'The machine maps the floor, so a changed layout needs a rescan or an agreed no-go zone. A warehouse that rearranges weekly needs that routine written into the plan rather than discovered on the first night.') +
            faq_item('Can a quadruped patrol at night?',
                     'Yes as a project: route, network coverage through the racking, lighting, doors, a safety review and someone to read what the sensors record. The hardware is in our catalogue; the patrol is designed with you.') +
            faq_item('Do you supply forklifts, AMRs or conveyor systems?',
                     'No. Those are bought per project with a systems integrator, because they need a link into your warehouse management system and a safety case. We will tell you who needs to be involved rather than sell around it.') +
            faq_item('Can we try one before buying?',
                     'Yes. We start with a review of your site and agree what will be measured. A trial is included when it is practical and agreed in scope, and the results go into the proposal.')
        ),
        'dec_title': 'Start with <strong>your floor.</strong>',
        'dec_p': 'Tell us the floor area, the shift pattern and when the floor has to be clean. We will tell you what the first site check covers, what your site needs, and what we still have to check.',
        'cta': 'Talk to us about your site',
    },
}


def build(spec):
    body = HERO.format(**spec) + '\n\n  ' + CAPABILITIES.format(title=spec['cap_title'], intro=spec['cap_intro'], tiers=spec['tiers'])
    body += '\n\n  ' + MACHINES.format(title=spec['mach_title'], intro=spec['mach_intro'], cards=spec['cards'],
                                    wide_url=spec['wide_url'], wide_aria=spec['wide_aria'], wide_sub=spec['wide_sub'],
                                    wide_name=spec['wide_name'], wide_p=spec['wide_p'],
                                    wide_stat1=spec['wide_stat1'], wide_stat1_l=spec['wide_stat1_l'],
                                    wide_stat2=spec['wide_stat2'], wide_stat2_l=spec['wide_stat2_l'],
                                    wide_price=spec['wide_price'], wide_img=spec['wide_img'],
                                    wide_alt=spec['wide_alt'], note=spec['mach_note'])
    body += '\n\n  ' + PROOF.format(title=spec['proof_title'], intro=spec['proof_intro'], site=spec['site'],
                                   step1=spec['step1'], crit_title=spec['crit_title'], crit=spec['crit'],
                                   ev_title=spec['ev_title'], ev_p=spec['ev_p'])
    body += '\n\n  ' + FAQ.format(items=spec['faqs'])
    body += '\n\n  ' + DECISION.format(title=spec['dec_title'], p=spec['dec_p'], cta=spec['cta'])
    return body


def main(dry):
    for name, spec in PAGES.items():
        page = ROOT / 'industries' / name
        src = page.read_text(encoding='utf-8')
        start = src.index('<section class="ho-hero"')
        end = src.index('<footer class="footer"')
        new = src[:start] + build(spec) + '\n\n  ' + src[end:]
        # title, description and og/twitter copy follow the page
        new = re.sub(r'<title>.*?</title>', f'<title>{spec["title"]}</title>', new, count=1, flags=re.S)
        new = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + spec['desc'] + m.group(2), new, count=1)
        new = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + spec['desc'] + m.group(2), new, count=1)
        new = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1) + re.sub(r'&amp;', '&', spec['title']) + m.group(2), new, count=1)
        if dry:
            print(f'{name:24} would rewrite ({len(src)} -> {len(new)} chars)')
            continue
        page.write_text(new, encoding='utf-8')
        print(f'{name:24} rewritten ({len(src)} -> {len(new)} chars)')


if __name__ == '__main__':
    main('--dry-run' in sys.argv)
