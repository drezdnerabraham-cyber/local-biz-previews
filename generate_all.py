"""
Multi-Industry Site Generator
Reads:  tools/local-biz/output/multi_leads.csv
Writes: tools/local-biz/premium/<industry>/<slug>/index.html
        tools/local-biz/output/multi_call_list.csv
"""
import csv, hashlib, re, unicodedata
from pathlib import Path

BASE_URL  = "https://drezdnerabraham-cyber.github.io/local-biz-previews"
ROOT      = Path(__file__).parent
CSV_IN    = ROOT.parent / "output" / "multi_leads.csv"
CSV_OUT   = ROOT.parent / "output" / "multi_call_list.csv"

# ── Industry configs ──────────────────────────────────────────────────────────
INDUSTRIES = {
    "dental": {
        "template": ROOT / "dental" / "template.html",
        "out_dir":  ROOT / "dental",
        "variants": [
            {
                "hero":     "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=1400&q=80&fit=crop",
                "about":    "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=1200&q=80&fit=crop",
                "hl1": "Your Best Smile", "hl2": "Starts Here",
                "sub": "Comprehensive dental care delivered by experienced, caring professionals. New patients welcome — same-day appointments available.",
                "h2":  "Dentistry Built Around You",
                "p1":  "At {name}, we believe a healthy smile is one of the most valuable things you can invest in. Every patient is treated as a priority — never rushed, always heard.",
                "p2":  "Our team brings years of advanced training to every procedure. Whether it's a routine cleaning or a complete smile makeover, we deliver results that last.",
            },
            {
                "hero":     "https://images.unsplash.com/photo-1606811971618-4486d14f3f99?w=1400&q=80&fit=crop",
                "about":    "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=1200&q=80&fit=crop",
                "hl1": "The Smile You", "hl2": "Deserve",
                "sub": "Modern dentistry in a comfortable, judgment-free environment. We treat patients of all ages and accept most insurance plans.",
                "h2":  "Trusted by Families in {city}",
                "p1":  "{name} has been caring for smiles in {city} for years. We've built our reputation one patient at a time — on honesty, skill, and genuine care.",
                "p2":  "From first-time visitors to long-time patients, everyone gets the same attention to detail. We don't cut corners, and we never recommend treatment you don't need.",
            },
        ],
        "stats": [("3200", "+", "Patients Treated"), ("15", "+", "Years Serving {city}"), ("98", "%", "Patient Satisfaction")],
    },
    "hvac": {
        "template": ROOT / "hvac-pro" / "template.html",
        "out_dir":  ROOT / "hvac-pro",
        "variants": [
            {
                "hero":     "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=1400&q=80&fit=crop",
                "about":    "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=1200&q=80&fit=crop",
                "hl1": "Your Comfort Is", "hl2": "Our Emergency",
                "sub": "Fast HVAC repair and installation across {city}. We answer 24/7 and show up on time — guaranteed.",
                "h2":  "The HVAC Team {city} Counts On",
                "p1":  "{name} was built on a simple idea: show up fast, fix it right, charge a fair price. Every technician on our team is licensed, background-checked, and trained on every major brand.",
                "p2":  "We don't do high-pressure sales. If your system needs a repair, we'll tell you. If it needs a replacement, we'll tell you that too — and we'll give you options that fit your budget.",
            },
            {
                "hero":     "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1400&q=80&fit=crop",
                "about":    "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=1200&q=80&fit=crop",
                "hl1": "Fast HVAC Service.", "hl2": "Fair Price. Done Right.",
                "sub": "Same-day HVAC service available throughout {city}. Licensed, insured, and upfront about every cost before we start.",
                "h2":  "Honest HVAC Service in {city}",
                "p1":  "We started {name} because we were tired of seeing homeowners get overcharged by HVAC companies that treat service calls like a blank check. Every quote is itemized, every price is explained.",
                "p2":  "Our technicians are paid to do good work — not to upsell. That's how we've built the reputation we have in {city}, and it's how we intend to keep it.",
            },
        ],
        "stats": [("5400", "+", "Jobs Completed"), ("12", "+", "Years in Business"), ("97", "%", "Same-Day Resolution")],
    },
    "electric": {
        "template": ROOT / "electric-pro" / "template.html",
        "out_dir":  ROOT / "electric-pro",
        "variants": [
            {
                "hero":     "https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=1400&q=80&fit=crop",
                "about":    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&q=80&fit=crop",
                "hl1": "Safe Electrical Work.", "hl2": "Done Right.",
                "sub": "Licensed electricians serving {city}. Upfront pricing, same-day availability, zero shortcuts on safety.",
                "h2":  "Electrical Work You Can Trust",
                "p1":  "{name} has handled electrical jobs across {city} for years. Every job is permitted, every installation is inspected, every panel we touch is left safer than we found it.",
                "p2":  "Electrical work isn't something to cut corners on. Our technicians are licensed and insured, and we stand behind every job with a written warranty.",
            },
            {
                "hero":     "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1400&q=80&fit=crop",
                "about":    "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=1200&q=80&fit=crop",
                "hl1": "Your Local Licensed", "hl2": "Electrician",
                "sub": "Residential and commercial electrical service throughout {city}. We quote before we start and finish what we promise.",
                "h2":  "{city}'s Reliable Electrical Contractor",
                "p1":  "When you call {name}, a licensed electrician answers — not a call center. We schedule fast, show up on time, and give you a clear price before any work begins.",
                "p2":  "From single outlet repairs to full panel replacements, we handle it all. Small jobs get the same attention as big ones because every customer matters.",
            },
        ],
        "stats": [("4100", "+", "Jobs Completed"), ("10", "+", "Years Licensed"), ("100", "%", "Permit-Ready Work")],
    },
    "plumbing": {
        "template": ROOT / "plumbing-pro" / "template.html",
        "out_dir":  ROOT / "plumbing-pro",
        "variants": [
            {
                "hero":     "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=1400&q=80&fit=crop",
                "about":    "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=1200&q=80&fit=crop",
                "hl1": "Fast Plumbing.", "hl2": "No Surprises.",
                "sub": "Licensed plumbers serving {city} 24/7. We fix it right the first time and tell you the price before we start.",
                "h2":  "The Plumber {city} Calls First",
                "p1":  "{name} has built its reputation on one thing: honest work at fair prices. No bait-and-switch, no inflated estimates, no unnecessary repairs. Just skilled plumbers who fix what's broken.",
                "p2":  "We serve all of {city} and surrounding areas. Whether it's a dripping faucet or a burst main line, our team responds fast and solves it completely.",
            },
            {
                "hero":     "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1400&q=80&fit=crop",
                "about":    "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=1200&q=80&fit=crop",
                "hl1": "We Fix It Right", "hl2": "The First Time",
                "sub": "Dependable plumbing service across {city}. Available nights and weekends. Upfront pricing always.",
                "h2":  "Plumbing Done the Right Way",
                "p1":  "At {name}, we don't believe in temporary fixes. Every repair is done to last, every installation is done to code, and every customer leaves knowing exactly what was done and why.",
                "p2":  "We've served homeowners and businesses throughout {city} for years. Our reviews speak for themselves — and our repeat customers speak even louder.",
            },
        ],
        "stats": [("3800", "+", "Jobs Completed"), ("24/7", "", "Emergency Service"), ("98", "%", "First-Visit Fix Rate")],
    },
    "roofing": {
        "template": ROOT / "roofing" / "template.html",
        "out_dir":  ROOT / "roofing",
        "variants": [
            {
                "hero":     "https://images.unsplash.com/photo-1632823471565-1ecdf5c6da3c?w=1400&q=80&fit=crop",
                "about":    "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=1200&q=80&fit=crop",
                "hl1": "Protect What", "hl2": "Matters Most",
                "sub": "Licensed roofing contractor serving {city}. Free inspections, insurance claim help, and a workmanship warranty on every job.",
                "h2":  "The Roofer {city} Trusts",
                "p1":  "{name} has installed and repaired hundreds of roofs across {city}. We work with every insurance company, use premium materials, and back every job with a written warranty.",
                "p2":  "Roofing is one of the biggest investments a homeowner makes. We take that seriously — which is why we do a thorough inspection before recommending anything, and only suggest what's genuinely needed.",
            },
            {
                "hero":     "https://images.unsplash.com/photo-1609220136736-443140cffec6?w=1400&q=80&fit=crop",
                "about":    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&q=80&fit=crop",
                "hl1": "Your Roof Done Right.", "hl2": "Guaranteed.",
                "sub": "Full-service roofing in {city}. Repair, replacement, storm damage — one crew, one standard of quality.",
                "h2":  "Quality Roofing in {city}",
                "p1":  "At {name}, quality isn't a sales pitch — it's the standard every crew member is held to. We use the same materials on every roof whether it's a $5,000 repair or a $30,000 replacement.",
                "p2":  "We've helped hundreds of {city} homeowners through storm damage claims and aging roofs. Our process is transparent, our timelines are realistic, and our work lasts.",
            },
        ],
        "stats": [("850", "+", "Roofs Completed"), ("15", "+", "Years in {city}"), ("5★", "", "Average Google Rating")],
    },
    "auto": {
        "template": ROOT / "auto-repair" / "template.html",
        "out_dir":  ROOT / "auto-repair",
        "variants": [
            {
                "hero":     "https://images.unsplash.com/photo-1487754180451-c456f719a1fc?w=1400&q=80&fit=crop",
                "about":    "https://images.unsplash.com/photo-1530046339160-ce3e530c7d2f?w=1200&q=80&fit=crop",
                "hl1": "Honest Auto Repair.", "hl2": "Every Time.",
                "sub": "Full-service auto repair in {city}. We diagnose it accurately, quote it upfront, and fix it right — on every car, every time.",
                "h2":  "The Auto Shop {city} Actually Trusts",
                "p1":  "{name} was built for drivers who are tired of being overcharged and under-informed. We show you exactly what's wrong, explain your options, and let you decide — no pressure.",
                "p2":  "Our mechanics are ASE certified and trained on every major make and model. We service everything from daily drivers to luxury imports, and we warranty every repair we perform.",
            },
            {
                "hero":     "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=1400&q=80&fit=crop",
                "about":    "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=1200&q=80&fit=crop",
                "hl1": "Your Car Fixed Right.", "hl2": "No Surprises.",
                "sub": "Reliable auto repair across {city}. Free diagnostics, upfront pricing, certified mechanics. No dealer markups.",
                "h2":  "Auto Repair You Can Count On",
                "p1":  "At {name}, you'll always know the price before we start. We run a full diagnostic, walk you through what we found, and get your approval — every single time.",
                "p2":  "We serve {city} drivers across all makes and models. Our repeat customer rate says everything: when people find a shop they can trust, they stop looking.",
            },
        ],
        "stats": [("6200", "+", "Vehicles Serviced"), ("12", "+", "Years in Business"), ("100", "%", "Upfront Pricing")],
    },
}

# YP search terms → industry key
CATEGORY_MAP = {
    "dentists": "dental", "dental": "dental", "orthodontists": "dental",
    "hvac": "hvac", "air conditioning": "hvac", "heating": "hvac",
    "electricians": "electric", "electrical": "electric",
    "plumbers": "plumbing", "plumbing": "plumbing",
    "roofing": "roofing", "roofers": "roofing",
    "auto repair": "auto", "auto": "auto", "mechanics": "auto", "car repair": "auto",
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text.strip())[:60].rstrip("-")

def phone_digits(p):
    return re.sub(r"\D", "", p)

def pick_variant(industry_key, name):
    h = int(hashlib.md5(name.encode()).hexdigest(), 16)
    variants = INDUSTRIES[industry_key]["variants"]
    return variants[h % len(variants)]

def build_stats(industry_key, rating_raw, reviews_raw, name, city):
    defaults = INDUSTRIES[industry_key]["stats"]
    out = []
    for num, sfx, lbl in defaults:
        num = num.replace("{city}", city).replace("{name}", name)
        lbl = lbl.replace("{city}", city).replace("{name}", name)
        # Try to use real rating for last stat if it looks like a star rating label
        if "Rating" in lbl or "Satisfaction" in lbl:
            try:
                r = float(re.sub(r"[^\d.]", "", rating_raw or ""))
                if 1.0 <= r <= 5.0:
                    out.append((str(r), "★", "Google Rating"))
                    continue
            except (ValueError, TypeError):
                pass
        # Try to use real reviews for review count
        if "Review" in lbl or "review" in lbl:
            try:
                v = int(re.sub(r"[^\d]", "", reviews_raw or ""))
                if v > 5:
                    out.append((str(v), "+", "Customer Reviews"))
                    continue
            except (ValueError, TypeError):
                pass
        out.append((num, sfx, lbl))
    return out

def build_rating_display(rating_raw, reviews_raw):
    parts = []
    try:
        r = float(re.sub(r"[^\d.]", "", rating_raw or ""))
        if 1.0 <= r <= 5.0:
            parts.append(f"{r}★ Google Rating")
    except (ValueError, TypeError):
        pass
    try:
        v = int(re.sub(r"[^\d]", "", reviews_raw or ""))
        if v > 5:
            parts.append(f"{v:,} reviews")
    except (ValueError, TypeError):
        pass
    return " · ".join(parts) if parts else "Highly Rated"

def resolve_industry(category_raw):
    cat = (category_raw or "").lower().strip()
    for key, val in CATEGORY_MAP.items():
        if key in cat:
            return val
    return None

# ── Main ──────────────────────────────────────────────────────────────────────
if not CSV_IN.exists():
    print(f"ERROR: {CSV_IN} not found. Run the scraper first.")
    raise SystemExit(1)

rows = list(csv.DictReader(CSV_IN.open(encoding="utf-8")))
targets = [r for r in rows if r.get("Has Website", "").strip().lower() == "no" and r.get("Name", "").strip()]
print(f"Found {len(targets)} no-website leads\n")

generated = []
slugs_seen = set()
skipped_unknown = 0

for lead in targets:
    name     = lead["Name"].strip()
    city     = lead.get("City", "").strip()
    phone    = lead.get("Phone", "").strip() or "(000) 000-0000"
    address  = lead.get("Address", "").strip() or city
    rating   = lead.get("Rating", "")
    reviews  = lead.get("Reviews", "")
    category = lead.get("Category", "")

    industry_key = resolve_industry(category)
    if not industry_key:
        skipped_unknown += 1
        continue

    cfg     = INDUSTRIES[industry_key]
    tmpl    = cfg["template"].read_text(encoding="utf-8")
    variant = pick_variant(industry_key, name)
    stats   = build_stats(industry_key, rating, reviews, name, city)
    r_disp  = build_rating_display(rating, reviews)
    digits  = phone_digits(phone) or "0000000000"

    # Unique slug under industry subdir
    base_slug = slugify(name)
    slug_key  = f"{industry_key}/{base_slug}"
    n = 2
    while slug_key in slugs_seen:
        slug_key = f"{industry_key}/{base_slug}-{n}"; n += 1
    slugs_seen.add(slug_key)
    preview_url = f"{BASE_URL}/{slug_key}/"

    about_p1 = variant["p1"].replace("{name}", name).replace("{city}", city)
    about_p2 = variant["p2"].replace("{name}", name).replace("{city}", city)
    about_h2 = variant["h2"].replace("{name}", name).replace("{city}", city)

    try:
        review_count = f"{int(re.sub(r'[^\\d]', '', reviews or '')):,}" if reviews else "150+"
    except ValueError:
        review_count = "150+"

    html = (tmpl
        .replace("{{BIZ_NAME}}",       name)
        .replace("{{CITY}}",           city)
        .replace("{{PHONE}}",          phone)
        .replace("{{PHONE_DIGITS}}",   digits)
        .replace("{{ADDRESS}}",        address)
        .replace("{{RATING_DISPLAY}}", r_disp)
        .replace("{{REVIEW_COUNT}}",   review_count)
        .replace("{{HERO_IMG}}",       variant["hero"])
        .replace("{{ABOUT_IMG}}",      variant["about"])
        .replace("{{HEADLINE1}}",      variant["hl1"])
        .replace("{{HEADLINE2}}",      variant["hl2"])
        .replace("{{HERO_SUB}}",       variant["sub"].replace("{city}", city).replace("{name}", name))
        .replace("{{ABOUT_H2}}",       about_h2)
        .replace("{{ABOUT_P1}}",       about_p1)
        .replace("{{ABOUT_P2}}",       about_p2)
        .replace("{{S1_NUM}}",  stats[0][0]).replace("{{S1_SFX}}", stats[0][1]).replace("{{S1_LBL}}", stats[0][2])
        .replace("{{S2_NUM}}",  stats[1][0]).replace("{{S2_SFX}}", stats[1][1]).replace("{{S2_LBL}}", stats[1][2])
        .replace("{{S3_NUM}}",  stats[2][0]).replace("{{S3_SFX}}", stats[2][1]).replace("{{S3_LBL}}", stats[2][2])
    )

    out_dir = cfg["out_dir"] / base_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html, encoding="utf-8")

    print(f"  [{industry_key:8s}] {name} ({city})")
    generated.append({**lead, "Slug": slug_key, "Preview URL": preview_url,
                       "Industry": industry_key, "Email": lead.get("Email", "")})

# Write call list
fieldnames = list(rows[0].keys())
for f in ["Slug", "Preview URL", "Industry", "Email"]:
    if f not in fieldnames:
        fieldnames.append(f)

with CSV_OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(generated)

print(f"\n✅ Generated {len(generated)} sites | Skipped (unknown category): {skipped_unknown}")
print(f"📄 Call list: {CSV_OUT}")
print(f"🌐 Preview base: {BASE_URL}/")
