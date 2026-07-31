"""
Med Spa Site Generator — 5 design variants, real YP data, $1,799 offer
Usage: python tools/local-biz/premium/medspa/generate.py
Reads:  tools/local-biz/output/medspa_leads.csv
Writes: tools/local-biz/premium/medspa/<slug>/index.html  (one per no-website lead)
        tools/local-biz/output/medspa_call_list.csv        (with preview URLs)
"""
import csv, hashlib, re, unicodedata
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
TEMPLATE  = Path(__file__).parent / "template.html"
OUT_SITES = Path(__file__).parent
CSV_IN    = Path(__file__).parent.parent.parent / "output" / "medspa_leads.csv"
CSV_OUT   = Path(__file__).parent.parent.parent / "output" / "medspa_call_list.csv"
BASE_URL  = "https://drezdnerabraham-cyber.github.io/local-biz-previews"

# ── 5 Design Variants ──────────────────────────────────────────────────────
VARIANTS = [
    {   # v1 — Clinical Luxury (antique gold)
        "class":    "v1",
        "hero_img": "https://images.unsplash.com/photo-1616394584738-fc6e612e71b9?w=1920&q=80&fit=crop",
        "hl1":      "Where Science Meets",
        "hl2":      "Timeless Beauty",
        "sub":      "Medical-grade aesthetics, precisely calibrated to you. Delivered by board-certified practitioners in a setting designed for comfort.",
        "about_p1": "At {name}, every treatment begins with a conversation. We believe the best aesthetic results are invisible — natural-looking, confidence-building, and precisely calibrated to who you are.",
        "about_p2": "Our board-certified practitioners bring advanced clinical training to every appointment. Whether you're considering your first treatment or a comprehensive rejuvenation plan, we meet you exactly where you are.",
    },
    {   # v2 — Rose Copper (boutique feminine)
        "class":    "v2",
        "hero_img": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=1920&q=80&fit=crop",
        "hl1":      "Beauty Refined.",
        "hl2":      "Confidence Restored.",
        "sub":      "Boutique aesthetic treatments tailored to your natural beauty. Where artistry and medicine become one.",
        "about_p1": "At {name}, beauty is deeply personal. Every face tells a story, and our role is to help yours tell it beautifully — with treatments as individual as you are.",
        "about_p2": "As a boutique practice in {city}, we see a curated number of patients each day. That's intentional. You deserve unhurried attention from practitioners who truly know your goals.",
    },
    {   # v3 — Champagne (results-first)
        "class":    "v3",
        "hero_img": "https://images.unsplash.com/photo-1512290923902-8a9f81dc236c?w=1920&q=80&fit=crop",
        "hl1":      "Precision Aesthetics.",
        "hl2":      "Exceptional Results.",
        "sub":      "Advanced aesthetic medicine that delivers. Natural-looking results, zero guesswork, expert hands every time.",
        "about_p1": "{name} was built on a simple principle: results should be real, measurable, and worth every dollar invested. No upselling. No guesswork. Just evidence-based treatments that deliver.",
        "about_p2": "Our specialists bring decades of combined experience to every consultation. We'll tell you what will work for you — and equally important, what won't.",
    },
    {   # v4 — Ice Blue (authority / clinical)
        "class":    "v4",
        "hero_img": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=1920&q=80&fit=crop",
        "hl1":      "The Science of",
        "hl2":      "Looking Your Best",
        "sub":      "Evidence-based aesthetic medicine from board-certified practitioners. Clinical precision — genuinely transformative results.",
        "about_p1": "Medicine is at the core of everything we do at {name}. Our practitioners hold advanced certifications and train annually with the leading aesthetic physicians in the country.",
        "about_p2": "When you choose {name}, you're choosing a practice that stays ahead of the science. We bring the latest FDA-cleared technologies and techniques to {city} — before they become trends.",
    },
    {   # v5 — Sage (wellness / holistic)
        "class":    "v5",
        "hero_img": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874?w=1920&q=80&fit=crop",
        "hl1":      "Aesthetic Care,",
        "hl2":      "Naturally Elevated.",
        "sub":      "Holistic medical aesthetics in harmony with your wellbeing. Treatments that restore balance, inside and out.",
        "about_p1": "At {name}, we treat the whole person — not just the concern. Our integrative approach combines medical-grade aesthetics with a deep respect for your body's natural intelligence.",
        "about_p2": "We believe confidence doesn't require transformation — it requires reveal. Our practitioners in {city} are committed to bringing out what's already there, more fully and beautifully than ever before.",
    },
]

# ── Helpers ────────────────────────────────────────────────────────────────
def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_]+", "-", text.strip())
    return re.sub(r"-+", "-", text)[:60].rstrip("-")

def phone_digits(phone):
    return re.sub(r"\D", "", phone)

def pick_variant(name):
    h = int(hashlib.md5(name.encode()).hexdigest(), 16)
    return VARIANTS[h % len(VARIANTS)]

def build_stats(rating_raw, reviews_raw):
    """Return (stat1, stat2, stat3) each as (num, suffix, label)."""
    # Stat 1: always patients treated
    s1 = ("4800", "+", "Patients Treated")

    # Stat 2: real review count or years of experience
    try:
        reviews = int(re.sub(r"[^\d]", "", reviews_raw or ""))
        s2 = (str(reviews), "+", "Patient Reviews") if reviews > 5 else ("12", "", "Years of Experience")
    except (ValueError, TypeError):
        s2 = ("12", "", "Years of Experience")

    # Stat 3: real star rating or satisfaction %
    try:
        rating = float(re.sub(r"[^\d.]", "", rating_raw or ""))
        if 1.0 <= rating <= 5.0:
            s3 = (str(rating).rstrip("0").rstrip("."), "★", "Google Rating")
        else:
            s3 = ("98", "%", "Patient Satisfaction")
    except (ValueError, TypeError):
        s3 = ("98", "%", "Patient Satisfaction")

    return s1, s2, s3

def build_rating_display(rating_raw, reviews_raw):
    parts = []
    try:
        r = float(re.sub(r"[^\d.]", "", rating_raw or ""))
        if 1.0 <= r <= 5.0:
            parts.append(f'<span>{r}★</span> Google Rating')
    except (ValueError, TypeError):
        pass
    try:
        v = int(re.sub(r"[^\d]", "", reviews_raw or ""))
        if v > 5:
            parts.append(f'<span>{v:,}</span> reviews')
    except (ValueError, TypeError):
        pass
    return " · ".join(parts) if parts else ""

# ── Main ───────────────────────────────────────────────────────────────────
template_html = TEMPLATE.read_text(encoding="utf-8")

if not CSV_IN.exists():
    print(f"ERROR: {CSV_IN} not found.")
    print("Download the medspa_leads.csv artifact from GitHub Actions and place it there.")
    raise SystemExit(1)

rows = list(csv.DictReader(CSV_IN.open(encoding="utf-8")))
targets = [
    r for r in rows
    if r.get("Has Website", "").strip().lower() == "no" and r.get("Name", "").strip()
]

print(f"Found {len(targets)} no-website med spa leads\n")

generated = []
slugs_seen = set()

for lead in targets:
    name    = lead["Name"].strip()
    city    = lead["City"].strip()
    phone   = lead["Phone"].strip() or "(000) 000-0000"
    address = lead.get("Address", "").strip() or city
    rating  = lead.get("Rating", "")
    reviews = lead.get("Reviews", "")

    # Unique slug
    base_slug = slugify(name)
    slug = f"medspa/{base_slug}"
    n = 2
    while slug in slugs_seen:
        slug = f"medspa/{base_slug}-{n}"; n += 1
    slugs_seen.add(slug)

    digits      = phone_digits(phone) or "0000000000"
    preview_url = f"{BASE_URL}/{slug}/"
    variant     = pick_variant(name)
    s1, s2, s3  = build_stats(rating, reviews)
    rating_disp = build_rating_display(rating, reviews)

    about_p1 = variant["about_p1"].replace("{name}", name).replace("{city}", city)
    about_p2 = variant["about_p2"].replace("{name}", name).replace("{city}", city)

    html = (template_html
        # Business identity
        .replace("{{SPA_NAME}}",      name)
        .replace("{{CITY}}",          city)
        .replace("{{PHONE}}",         phone)
        .replace("{{PHONE_DIGITS}}",  digits)
        .replace("{{ADDRESS}}",       address)
        .replace("{{RATING_DISPLAY}}",rating_disp)
        # Design variant
        .replace("{{VARIANT}}",       variant["class"])
        .replace("{{HERO_IMG_URL}}",  variant["hero_img"])
        .replace("{{HEADLINE1}}",     variant["hl1"])
        .replace("{{HEADLINE2}}",     variant["hl2"])
        .replace("{{HERO_SUB}}",      variant["sub"])
        .replace("{{ABOUT_P1}}",      about_p1)
        .replace("{{ABOUT_P2}}",      about_p2)
        # Stats
        .replace("{{STAT1_NUM}}",     s1[0]).replace("{{STAT1_SFX}}", s1[1]).replace("{{STAT1_LBL}}", s1[2])
        .replace("{{STAT2_NUM}}",     s2[0]).replace("{{STAT2_SFX}}", s2[1]).replace("{{STAT2_LBL}}", s2[2])
        .replace("{{STAT3_NUM}}",     s3[0]).replace("{{STAT3_SFX}}", s3[1]).replace("{{STAT3_LBL}}", s3[2])
    )

    out_dir = OUT_SITES / slug.replace("medspa/", "")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html, encoding="utf-8")

    v_label = {"v1":"Gold","v2":"Rose","v3":"Champagne","v4":"Blue","v5":"Sage"}[variant["class"]]
    stats_info = f"{s2[0]}{s2[1]} {s2[2]}, {s3[0]}{s3[1]} {s3[2]}"
    print(f"  [{v_label:9s}] {name} ({city}) | {stats_info}")

    generated.append({
        **lead,
        "Slug":        slug,
        "Preview URL": preview_url,
        "Variant":     v_label,
        "Email":       lead.get("Email", ""),
    })

# Write enriched call list CSV
fieldnames = list(rows[0].keys())
for f in ["Slug", "Preview URL", "Variant", "Email"]:
    if f not in fieldnames:
        fieldnames.append(f)

with CSV_OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(generated)

print(f"\n✅ Generated {len(generated)} sites across 5 design variants")
print(f"📄 Call list: {CSV_OUT}")
print(f"🌐 Preview base: {BASE_URL}/medspa/")
