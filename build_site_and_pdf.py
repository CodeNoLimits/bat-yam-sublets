#!/usr/bin/env python3
"""Builds index.html (Web App) and print.html -> bat-yam-sublets-en-he.pdf (with embedded photos & links)."""
import json
import os
import subprocess
from datetime import datetime

BASE = "/Users/dreamnova/.gemini/antigravity/scratch/bat-yam-sublets"

with open(os.path.join(BASE, "apartments.json"), "r", encoding="utf-8") as f:
    apts = json.load(f)

with open(os.path.join(BASE, "downloaded_photos.json"), "r", encoding="utf-8") as f:
    photos_map = json.load(f)

for a in apts:
    pk = a.get("photo_key", a["id"])
    a["photos"] = photos_map.get(pk, [])

now_str = datetime.now().strftime("%Y-%m-%d %H:%M (Israel Time)")

# Build cards HTML for index.html
cards_html = []
def _group(a):
    st = a.get("wa_status_en", "")
    if a.get("tier") == "TOP": return ("contact", "✅ In contact — visits & live chats", "✅ בקשר — ביקורים ושיחות פעילות")
    if "📩" in st: return ("sent", "📩 WhatsApp sent tonight — waiting for answer", "📩 נשלחה הודעת וואטסאפ הלילה — ממתינים לתשובה")
    if "📞" in st: return ("call", "📞 To call Monday morning — Yad2 virtual lines (no WhatsApp)", "📞 להתקשר ביום שני בבוקר — קווים וירטואליים של יד2 (בלי וואטסאפ)")
    return ("other", "🔥 Other leads", "🔥 הזדמנויות נוספות")
_counts = {}
for a in apts: _counts[_group(a)[0]] = _counts.get(_group(a)[0], 0) + 1
_prev = None
for a in apts:
    g = _group(a)
    if g[0] != _prev:
        _prev = g[0]
        cards_html.append(f'<h2 class="section-h" id="sec-{g[0]}"><span class="en">{g[1]} ({_counts[g[0]]})</span><span class="he">{g[2]} ({_counts[g[0]]})</span></h2>')
    photos = a["photos"]
    main_photo = photos[0] if photos else ""
    thumbs_html = ""
    if len(photos) > 1:
        thumbs = []
        for idx, p in enumerate(photos):
            thumbs.append(
                f'<img src="{p}" class="thumb" onclick="document.getElementById(\'main-img-{a["rank"]}\').src=\'{p}\'" alt="Photo {idx+1}" loading="lazy"/>'
            )
        thumbs_html = f'<div class="thumbs-row">{"".join(thumbs)}</div>'

    badges_en = "".join(f'<span class="badge badge-en">{b}</span>' for b in a["badges_en"])
    badges_he = "".join(f'<span class="badge badge-he">{b}</span>' for b in a["badges_he"])

    wa_btn = ""
    if a["whatsapp_url"]:
        wa_btn = f'''
        <a href="{a["whatsapp_url"]}" target="_blank" rel="noopener" class="btn btn-wa">
          💬 WhatsApp {a["phone"]} · שלח וואטסאפ
        </a>
        <a href="tel:{a["phone"].replace("-", "")}" class="btn btn-call">
          📞 Call / חייג {a["phone"]}
        </a>
        '''
    else:
        wa_btn = f'''
        <a href="{a["source_url"]}" target="_blank" rel="noopener" class="btn btn-wa">
          💬 Contact {a["contact_name"]} on {a["source_name"]} · יצירת קשר במודעה
        </a>
        '''

    if a["tier"] == "TOP":
        tier_badge = '<span class="tier-top">⭐ IN CONTACT · בקשר פעיל</span>'
    elif a["tier"] == "NEW_TOP":
        tier_badge = '<span class="tier-new">🆕 NEW · REAL YAD2 LISTING · מודעה אמיתית</span>'
    else:
        tier_badge = '<span class="tier-bonus">🔥 BONUS DIRECT · נוסף</span>'

    wa_status_en_html = f'<div class="wa-status-banner">{a["wa_status_en"]}</div>' if a.get("wa_status_en") else ""
    wa_status_he_html = f'<div class="wa-status-banner">{a["wa_status_he"]}</div>' if a.get("wa_status_he") else ""

    cards_html.append(f'''
    <article class="apt-card" id="apt-{a["rank"]}">
      <div class="card-header">
        <div class="rank-pill">#{a["rank"]}</div>
        {tier_badge}
        <div class="price-pill">₪{a["price_ils"]:,}/mo</div>
      </div>

      <div class="photo-section">
        <a href="{main_photo}" target="_blank">
          {f'<img id="main-img-{a["rank"]}" src="{main_photo}" class="main-photo" alt="{a["title_en"]}" loading="lazy"/>' if main_photo else '<div style="padding:12px;color:#94a3b8;text-align:center">No photo in the ad · אין תמונה במודעה</div>'}
        </a>
        {thumbs_html}
      </div>

      <div class="bilingual-grid">
        <!-- ENGLISH COLUMN -->
        <div class="lang-col lang-en" dir="ltr">
          <div class="lang-tag">🇬🇧 ENGLISH</div>
          <h2 class="apt-title">{a["title_en"]}</h2>
          <div class="price-detail">{a["price_label_en"]}</div>
          {wa_status_en_html}
          <div class="address-line">📍 <strong>Address:</strong> {a["address_en"]}</div>
          <div class="badges-wrap">{badges_en}</div>
          <p class="why-box">{a["why_en"]}</p>
          <div class="contact-line">👤 <strong>Contact:</strong> {a["contact_name"]} {("— <strong>" + a["phone"] + "</strong>") if a["phone"] else ""}</div>
        </div>

        <!-- HEBREW COLUMN -->
        <div class="lang-col lang-he" dir="rtl">
          <div class="lang-tag">🇮🇱 עברית</div>
          <h2 class="apt-title">{a["title_he"]}</h2>
          <div class="price-detail">{a["price_label_he"]}</div>
          {wa_status_he_html}
          <div class="address-line">📍 <strong>כתובת:</strong> {a["address_he"]}</div>
          <div class="badges-wrap">{badges_he}</div>
          <p class="why-box">{a["why_he"]}</p>
          <blockquote class="orig-quote">״{a["original_quote_he"]}״</blockquote>
          <div class="contact-line">👤 <strong>איש קשר:</strong> {a["contact_name"]} {("— <strong dir=\'ltr\'>" + a["phone"] + "</strong>") if a["phone"] else ""}</div>
        </div>
      </div>

      <div class="actions-bar">
        {wa_btn}
        <a href="{a["source_url"]}" target="_blank" rel="noopener" class="btn btn-source">
          🔗 Original Ad ({a["source_name"]}) · מודעה מקורית
        </a>
        <a href="{a["dorin_url"]}" target="_blank" rel="noopener" class="btn btn-dorin">
          🔗 Dorin Card · כרטיס דירה
        </a>
      </div>
    </article>
    ''')

index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta property="og:title" content="Bat Yam & Holon ≤ ₪3,500 — David & Leeya — visits 20/10" />
  <meta property="og:description" content="43 real Yad2 listings, phones, photos, visits plan. English + Hebrew." />
  <meta property="og:image" content="https://codenolimits.github.io/bat-yam-sublets/hero.jpg" />
  <meta property="og:type" content="website" />
  <title>Bat Yam & Holon ≤ ₪3,500 — visits 20/10 | דירות בבת ים וחולון עד 3,500 ₪ — ביקורים 20/10</title>
  <style>
    :root {{
      --bg: #0f172a;
      --card: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --muted: #94a3b8;
      --accent: #38bdf8;
      --green: #22c55e;
      --amber: #f59e0b;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.55;
      padding-bottom: 60px;
    }}
    .hero {{
      background: linear-gradient(135deg, #0284c7 0%, #1e3a8a 100%);
      padding: 28px 20px;
      text-align: center;
      border-bottom: 2px solid var(--accent);
    }}
    .hero h1 {{
      font-size: 1.65rem;
      margin-bottom: 6px;
      font-weight: 800;
    }}
    .hero h2 {{
      font-size: 1.35rem;
      margin-bottom: 12px;
      color: #e0f2fe;
      direction: rtl;
    }}
    .hero {{ background: linear-gradient(180deg, rgba(8,20,40,.55), rgba(8,20,40,.85)), url('hero.jpg') center/cover no-repeat; }}
    .section-h {{ margin: 28px 0 10px; font-size: 1.25rem; color: #fbbf24; display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; border-bottom: 2px solid #fbbf24; padding-bottom: 6px; }}
    .section-h .he {{ direction: rtl; }}
    body.mode-en .section-h .he, body.mode-he .section-h .en {{ display:none; }}
    .video-box {{ max-width: 1100px; margin: 18px auto 0; padding: 0 16px; }}
    .video-box video {{ width: 100%; border-radius: 14px; box-shadow: 0 8px 30px rgba(0,0,0,.45); background:#000; }}
    .video-box p {{ color:#cbd5e1; text-align:center; margin:8px 0 0; }}
    .hero-sub {{
      max-width: 820px;
      margin: 0 auto 16px;
      font-size: 0.95rem;
      color: #f0f9ff;
    }}
    .top-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      justify-content: center;
      align-items: center;
      margin-top: 14px;
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 10px 16px;
      border-radius: 10px;
      font-weight: 700;
      font-size: 0.92rem;
      text-decoration: none;
      cursor: pointer;
      border: none;
      transition: transform 0.12s ease, opacity 0.12s ease;
    }}
    .btn:hover {{ transform: translateY(-1px); opacity: 0.95; }}
    .btn-pdf {{ background: #ef4444; color: #fff; box-shadow: 0 4px 14px rgba(239,68,68,0.4); }}
    .btn-wa {{ background: #22c55e; color: #052e16; }}
    .btn-call {{ background: #eab308; color: #1e293b; }}
    .btn-source {{ background: #38bdf8; color: #0f172a; }}
    .btn-dorin {{ background: #64748b; color: #f8fafc; }}
    .lang-switch {{
      background: rgba(15,23,42,0.75);
      color: #fff;
      border: 1px solid #7dd3fc;
      padding: 8px 14px;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
    }}
    .cron-banner {{
      max-width: 1140px;
      margin: 18px auto 0;
      padding: 12px 18px;
      background: rgba(34,197,94,0.12);
      border: 1px solid #22c55e;
      border-radius: 12px;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      font-size: 0.9rem;
    }}
    .container {{
      max-width: 1140px;
      margin: 20px auto;
      padding: 0 14px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }}
    .apt-card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 10px 25px rgba(0,0,0,0.35);
    }}
    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 18px;
      background: #0f172a;
      border-bottom: 1px solid var(--border);
      flex-wrap: wrap;
      gap: 8px;
    }}
    .rank-pill {{
      background: var(--accent);
      color: #0f172a;
      font-weight: 900;
      font-size: 1.1rem;
      padding: 4px 12px;
      border-radius: 999px;
    }}
    .tier-top {{
      background: rgba(245,158,11,0.2);
      color: #fbbf24;
      border: 1px solid #f59e0b;
      padding: 4px 12px;
      border-radius: 999px;
      font-weight: 700;
      font-size: 0.85rem;
    }}
    .tier-bonus {{
      background: rgba(56,189,248,0.15);
      color: #7dd3fc;
      border: 1px solid #38bdf8;
      padding: 4px 12px;
      border-radius: 999px;
      font-weight: 700;
      font-size: 0.85rem;
    }}
    .tier-new {{
      background: rgba(34,197,94,0.2);
      color: #86efac;
      border: 1px solid #22c55e;
      padding: 4px 12px;
      border-radius: 999px;
      font-weight: 700;
      font-size: 0.85rem;
    }}
    .wa-status-banner {{
      background: rgba(34,197,94,0.16);
      border: 1px solid #22c55e;
      color: #bbf7d0;
      padding: 8px 11px;
      border-radius: 8px;
      font-size: 0.86rem;
      font-weight: 600;
      margin-bottom: 10px;
    }}
    .price-pill {{
      background: var(--green);
      color: #052e16;
      font-weight: 900;
      font-size: 1.15rem;
      padding: 4px 14px;
      border-radius: 999px;
    }}
    .photo-section {{
      background: #090d16;
      padding: 12px;
      text-align: center;
    }}
    .main-photo {{
      width: 100%;
      max-height: 400px;
      object-fit: cover;
      border-radius: 12px;
      border: 1px solid var(--border);
    }}
    .thumbs-row {{
      display: flex;
      gap: 10px;
      justify-content: center;
      margin-top: 10px;
      overflow-x: auto;
      padding-bottom: 4px;
    }}
    .thumb {{
      width: 82px;
      height: 62px;
      object-fit: cover;
      border-radius: 8px;
      cursor: pointer;
      border: 2px solid transparent;
      transition: border-color 0.15s;
    }}
    .thumb:hover {{ border-color: var(--accent); }}
    .bilingual-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
      padding: 18px;
    }}
    @media (max-width: 820px) {{
      .bilingual-grid {{ grid-template-columns: 1fr; }}
    }}
    .lang-col {{
      background: rgba(15,23,42,0.55);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
    }}
    .lang-tag {{
      font-size: 0.78rem;
      font-weight: 800;
      color: var(--accent);
      margin-bottom: 6px;
      letter-spacing: 0.05em;
    }}
    .apt-title {{
      font-size: 1.2rem;
      margin-bottom: 8px;
      color: #fff;
    }}
    .price-detail {{
      color: #4ade80;
      font-weight: 700;
      margin-bottom: 8px;
      font-size: 0.96rem;
    }}
    .address-line, .contact-line {{
      font-size: 0.92rem;
      margin-bottom: 8px;
      color: #e2e8f0;
    }}
    .badges-wrap {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 10px;
    }}
    .badge {{
      font-size: 0.76rem;
      padding: 3px 9px;
      border-radius: 6px;
      font-weight: 700;
      background: rgba(56,189,248,0.16);
      color: #bae6fd;
    }}
    .why-box {{
      font-size: 0.92rem;
      color: #cbd5e1;
      margin-bottom: 10px;
    }}
    .orig-quote {{
      font-size: 0.85rem;
      color: #fde68a;
      background: rgba(245,158,11,0.1);
      border-right: 3px solid #f59e0b;
      padding: 8px 10px;
      border-radius: 6px;
      margin-bottom: 10px;
    }}
    .actions-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      padding: 14px 18px;
      background: rgba(15,23,42,0.8);
      border-top: 1px solid var(--border);
    }}
    body.mode-en .lang-he {{ display: none; }}
    body.mode-en .bilingual-grid {{ grid-template-columns: 1fr; }}
    body.mode-he .lang-en {{ display: none; }}
    body.mode-he .bilingual-grid {{ grid-template-columns: 1fr; }}
  </style>
</head>
<body>
  <header class="hero">
    <h1>🏖️ Bat Yam & Holon ≤ ₪3,500 — 6 months, all-inclusive, near Yoseftal light rail · visits Monday 20/10</h1>
    <h2>דירות בבת ים וחולון עד 3,500 ₪ — חצי שנה, כולל הכל, ליד תחנת יוספטל · ביקורים יום שני 20/10</h2>
    <p class="hero-sub">
      Prepared for <strong>David & Leeya</strong> · 43 real private listings from Yad2 (Bat Yam + Holon), phones, photos, visit plan · <span dir="rtl">מוכן לדוד וליה · 43 מודעות פרטיות אמיתיות מיד2, טלפונים, תמונות ותוכנית ביקורים</span>
    </p>
    <div class="top-bar">
      <a href="bat-yam-sublets-en-he.pdf" target="_blank" class="btn btn-pdf">
        📄 Download Bilingual PDF (EN + עברית) · הורדת קובץ PDF מלא
      </a>
      <button class="lang-switch" onclick="document.body.className=''">🇬🇧 + 🇮🇱 Both Languages (דו-לשוני)</button>
      <button class="lang-switch" onclick="document.body.className='mode-en'">🇬🇧 English Only</button>
      <button class="lang-switch" onclick="document.body.className='mode-he'">🇮🇱 עברית בלבד</button>
    </div>
  </header>

  <div class="video-box">
    <video controls playsinline preload="metadata" poster="hero.jpg" src="plan-en.mp4"></video>
    <p>🎬 2-minute video: the Monday plan (English) · <a href="plan-en.mp3" style="color:#93c5fd">MP3</a> · <span dir="rtl">סרטון של 2 דקות: התוכנית ליום שני (אנגלית)</span></p>
  </div>

  <div class="cron-banner">
    <div>🤖 <strong>Autonomous Sublet Hunter Active (Every 6 Hours):</strong> Scanning Facebook Groups, Marketplace, Yad2, Dorin & Israela automatically.</div>
    <div dir="rtl">🔄 <strong>סוכן חיפוש אוטומטי פעיל (כל 6 שעות):</strong> עדכון אחרון: <code>{now_str}</code></div>
  </div>

  <main class="container">
    {"".join(cards_html)}
  </main>
</body>
</html>
'''

with open(os.path.join(BASE, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

# Also build print-friendly HTML for PDF generation
print_cards = []
for a in apts:
    photos = a["photos"][:2]
    imgs_html = "".join(
        f'<img src="{os.path.join(BASE, p)}" style="width:48%;height:165px;object-fit:cover;border-radius:8px;border:1px solid #cbd5e1;" />'
        for p in photos
    )
    wa_link = a["whatsapp_url"] if a["whatsapp_url"] else a["source_url"]
    p_wa_en = f'<div style="color:#15803d;font-weight:700;margin:3px 0;">{a["wa_status_en"]}</div>' if a.get("wa_status_en") else ""
    p_wa_he = f'<div style="color:#15803d;font-weight:700;margin:3px 0;">{a["wa_status_he"]}</div>' if a.get("wa_status_he") else ""
    print_cards.append(f'''
    <div class="print-card">
      <div class="print-head">
        <strong>#{a["rank"]} — {a["title_en"]}</strong>
        <span class="print-price">₪{a["price_ils"]:,}/mo</span>
      </div>
      <div class="print-photos">{imgs_html}</div>
      <div class="print-cols">
        <div class="p-en" dir="ltr">
          <div><strong>🇬🇧 {a["price_label_en"]}</strong></div>
          {p_wa_en}
          <div>📍 {a["address_en"]}</div>
          <p>{a["why_en"]}</p>
          <div>👤 <strong>Contact:</strong> {a["contact_name"]} {a["phone"]}</div>
        </div>
        <div class="p-he" dir="rtl">
          <div><strong>🇮🇱 {a["price_label_he"]}</strong></div>
          {p_wa_he}
          <div>📍 {a["address_he"]}</div>
          <p>{a["why_he"]}</p>
          <div>👤 <strong>איש קשר:</strong> {a["contact_name"]} <span dir="ltr">{a["phone"]}</span></div>
        </div>
      </div>
      <div class="print-links">
        🔗 <a href="{a["source_url"]}">Original Ad ({a["source_name"]}): {a["source_url"]}</a><br/>
        🔗 <a href="{a["dorin_url"]}">Dorin Card: {a["dorin_url"]}</a>
        {f'<br/>💬 <a href="{wa_link}">Direct WhatsApp ({a["phone"]}): https://wa.me/972{a["phone"].replace("-","").replace("+972","").lstrip("0")}</a>' if a["phone"] else ''}
      </div>
    </div>
    ''')

print_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Bat Yam & Holon ≤ ₪3,500 — David & Leeya — 20/10</title>
  <style>
    @page {{ size: A4; margin: 12mm; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; color: #0f172a; font-size: 11px; line-height: 1.4; }}
    h1 {{ font-size: 17px; margin: 0 0 4px 0; color: #0369a1; }}
    h2 {{ font-size: 14px; margin: 0 0 10px 0; color: #1e3a8a; direction: rtl; }}
    .print-card {{ border: 1.5px solid #94a3b8; border-radius: 10px; padding: 10px; margin-bottom: 12px; page-break-inside: avoid; }}
    .print-head {{ display: flex; justify-content: space-between; align-items: center; font-size: 13px; background: #f1f5f9; padding: 6px 10px; border-radius: 6px; margin-bottom: 8px; }}
    .print-price {{ background: #16a34a; color: #fff; padding: 2px 8px; border-radius: 999px; font-weight: bold; }}
    .print-photos {{ display: flex; gap: 2%; margin-bottom: 8px; }}
    .print-cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 6px; }}
    .p-en, .p-he {{ background: #f8fafc; padding: 8px; border-radius: 6px; border: 1px solid #e2e8f0; }}
    .p-en p, .p-he p {{ margin: 4px 0; }}
    .print-links {{ font-size: 10px; background: #eff6ff; padding: 6px 8px; border-radius: 6px; word-break: break-all; }}
    .print-links a {{ color: #0284c7; text-decoration: none; font-weight: 600; }}
  </style>
</head>
<body>
  <h1>🏖️ Bat Yam & Holon ≤ ₪3,500 — 6 months, all-inclusive, near Yoseftal (visits Monday 20/10)</h1>
  <h2>סאבלט ודירות בבת ים עד 3,000 ₪ — כניסה מיידית לפני יום שלישי (עבור דוד וליאה)</h2>
  <p style="margin-bottom:10px;">Generated: {now_str} · Click any link below to open the original listing or direct WhatsApp chat.</p>
  {"".join(print_cards)}
</body>
</html>
'''

print_html_path = os.path.join(BASE, "print.html")
pdf_path = os.path.join(BASE, "bat-yam-sublets-en-he.pdf")
with open(print_html_path, "w", encoding="utf-8") as f:
    f.write(print_html)

# Find Chrome/Chromium binary to render PDF cleanly
chrome_bins = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]
chrome = next((b for b in chrome_bins if os.path.exists(b)), None)
if chrome and not os.environ.get("NO_PDF"):
    subprocess.run([
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        f"file://{print_html_path}"
    ], check=True)
    print("PDF generated:", pdf_path, "Size:", os.path.getsize(pdf_path))
else:
    print("No Chrome binary found for PDF!")
