#!/usr/bin/env python3
"""Reconstruit apartments.json à partir (1) des fiches conservées de ce matin avec statut WhatsApp réel,
(2) des annonces Yad2 révélées ce soir (candidates.json). Télécharge les photos Yad2. Puis build (site + PDF)."""
import json, os, re, subprocess, urllib.request, urllib.parse
BASE = os.path.dirname(os.path.abspath(__file__))
SCR = "/private/tmp/claude-501/-Users-dreamnova/0ca0fc45-4268-48df-abb3-110aba170afc/scratchpad/yad2"
cands = json.load(open(f"{SCR}/candidates.json"))
old = json.load(open(f"{BASE}/apartments.json"))
photos = json.load(open(f"{BASE}/downloaded_photos.json"))
outreach = {}
for l in open(os.path.expanduser("~/.dreamnova/batyam_outreach_log.jsonl")):
    try:
        j = json.loads(l); outreach[j.get("phone")] = j
    except Exception: pass

def wa(num, text):
    return f"https://wa.me/{num}?text={urllib.parse.quote(text)}"

# ── 1. fiches conservées (statut réel lu dans WhatsApp ce soir) ──
KEEP = {
 "rothschild-39-sublet": ("✅ VISIT TOMORROW 12:00 — Rothschild 39 (Tzachi) · ₪4,000 ALL INCLUSIVE (over budget — negotiate)", "✅ ביקור מחר 12:00 — רוטשילד 39 (צחי) · 4,000 ₪ כולל הכל (מעל התקציב — לנסות להוריד)", "TOP", 4000),
 "1398a8e7-013a-4512-8465-2c31d2325019": ("⏳ VISIT TOMORROW (hour asked 23:30) — Kinamon unit (Shay) · ₪3,500 incl. Arnona · 6 months · ⚠️ asks post-dated checks", "⏳ ביקור מחר (ביקשנו שעה ב-23:30) — יחידה בקינמון (שי) · 3,500 ₪ כולל ארנונה · חצי שנה · ⚠️ מבקש צ'קים", "TOP", 3500),
 "6c30853c-0596-4888-92fb-a3b49fe01b9c": ("✍️ DAVID MUST WRITE HER HIMSELF (she spotted the assistant) — Sivan, Yerushalayim/Rothschild · ₪2,000 + ₪500 bills · roommate + dog", "✍️ דוד צריך לכתוב לה בעצמו (היא זיהתה את העוזר) — סיון, ירושלים/רוטשילד · 2,000 + 500 ₪ · שותף עם כלבה", "TOP", 2500),
 "f6466a28-a34a-40f9-9108-0cf50f0b5676": ("⏳ Roman (Givati, 3 rooms ₪3,000) will know by Thursday if it frees up", "⏳ רומן (גבעתי, 3 חד' 3,000 ₪) יידע עד יום חמישי אם מתפנה", "BONUS", 3000),
 "e6df8b11-d65c-4f57-a053-2507e891902e": ("📅 Palei Apartments: 2-room available from 30.10 (price asked 19:25, no answer yet)", "📅 פלאי: דירת 2 חד' פנויה מ-30.10 (שאלנו מחיר ב-19:25, אין תשובה)", "BONUS", 0),
 "0e621819-dbe5-4ffa-b04a-031a852132ea": ("📩 Vlad (Rothschild 60 studio ₪3,400) — no answer yet, re-asked 23:30 for a visit tomorrow", "📩 ולאד (סטודיו רוטשילד 60, 3,400 ₪) — עדיין לא ענה, שאלנו שוב ב-23:30 על ביקור מחר", "BONUS", 3400),
 "f2e0a51f-cfee-409e-96aa-951a2c966ce5": ("🔥 Facebook sublet ₪2,750 (roommate 25 from UK, prefers age 22-30) — contact via Facebook post only", "🔥 סאבלט מפייסבוק 2,750 ₪ (שותף בן 25, מעדיף גיל 22-30) — קשר דרך הפוסט בלבד", "BONUS", 2750),
}
REMOVED_WHY = {"f043b54e-b8d9-417b-86e1-c810dd8a3f8e": "Erez: ₪8,000-10,000", "0128147d-d7ae-463a-923e-12e0fd9f66be": "Pavel: ₪11,000, free 16.11", "8b6fae03-3349-4f2a-8278-f986ee567eea": "Lital: 'no'", "b2393c9b-70cb-4e6a-8d02-b230fea8c993": "Arena hotel, tourist short-term, no contact", "f20a754b-ccd7-4f17-8e85-6df10aa0768f": "Balfour 88 = agency (Tais Netanel)", "123e4797-95be-42ef-9c11-5661acfd8c87": "replaced by real Yad2 listing jrrvxsu7"}
new = []
for a in old:
    if a["id"] in KEEP:
        en, he, tier, price = KEEP[a["id"]]
        a["title_en"] = re.sub(r"^[^A-Za-z]*\[[^\]]*\]\s*", "", a["title_en"]); a["title_he"] = re.sub(r"^[^א-ת]*\[[^\]]*\]\s*", "", a["title_he"])
        a["wa_status_en"], a["wa_status_he"], a["tier"] = en, he, tier
        if price: a["price_ils"] = price
        new.append(a)
    elif a["id"] in REMOVED_WHY:
        print("retiré:", a["id"][:8], REMOVED_WHY[a["id"]])
    else:
        print("retiré (remplacé par la vraie annonce Yad2):", a["id"][:8], a["title_en"][:50])

# ── 2. annonces Yad2 révélées ce soir ──
SKIP = {"14bckurl": "exige chèques + bulletins de salaire", "rofz4zlb": "16 m²", "jrrvxsu7": None, "ixn2lgxe": "16 m²", "ewuyf64v": "20 m² (Holon)", "8u4ot23w": "20 m²", "z57n31do": "20 m²"}
def fmt_price(p): return f"₪{p:,}"
for r in cands:
    if r["token"] in SKIP and SKIP[r["token"]]:
        print("ignoré:", r["token"], SKIP[r["token"]]); continue
    if r["token"] in ("tgkep2mb",) : pass
    num = r["tel_digits"]; o = outreach.get(num)
    addr_he = f"{r['street']} {r['house'] or ''}".strip(); hood = r["hood"] or ""
    city_en = "Bat Yam" if r["city"] == "בת ים" else "Holon"
    furn = "furnished" if r["furnished"] else ("unfurnished" if r["furnished"] is False else "furniture: ask")
    furn_he = "מרוהט" if r["furnished"] else ("לא מרוהט" if r["furnished"] is False else "ריהוט: לשאול")
    imm = "immediate entry" if r["immediate"] else (f"entry {r['entrance']}" if r["entrance"] else "entry: ask")
    imm_he = "כניסה מיידית" if r["immediate"] else (f"כניסה {r['entrance']}" if r["entrance"] else "כניסה: לשאול")
    incl = " · bills included (per ad)" if r["all_inclusive_hint"] else ""
    incl_he = " · כולל חשבונות (לפי המודעה)" if r["all_inclusive_hint"] else ""
    km = f" · {r['km_yoseftal']} km from Yoseftal light-rail" if r["km_yoseftal"] is not None else ""
    km_he = f" · {r['km_yoseftal']} ק\"מ מתחנת יוספטל" if r["km_yoseftal"] is not None else ""
    if o:
        st_en = f"📩 WhatsApp sent {'19/10 23:40'} — visit proposed tomorrow at {o['slot']} (waiting for answer)"
        st_he = f"📩 נשלחה הודעת וואטסאפ 19/10 23:40 — הצענו ביקור מחר ב-{o['slot']} (ממתינים לתשובה)"
        tier = "NEW_TOP"
    elif r["virtual"]:
        st_en = f"📞 CALL TOMORROW MORNING (Yad2 virtual line, no WhatsApp): {r['tel']}"
        st_he = f"📞 להתקשר מחר בבוקר (קו וירטואלי של יד2, אין וואטסאפ): {r['tel']}"
        tier = "NEW_TOP" if (r["price"] or 0) <= 3400 else "BONUS"
    else:
        st_en = f"📱 WhatsApp / call: {r['tel']}"; st_he = f"📱 וואטסאפ / טלפון: {r['tel']}"; tier = "BONUS"
    warn_en = " ⚠️ ad mentions checks/guarantor" if r["checks_hint"] else ""
    warn_he = " ⚠️ במודעה: צ'קים/ערבות" if r["checks_hint"] else ""
    # photos
    plist = []
    for i, u in enumerate((r["images"] or [])[:5]):
        dst = f"photos/y2_{r['token']}_{i}.jpg"
        if not os.path.exists(f"{BASE}/{dst}"):
            try:
                urllib.request.urlretrieve(u, f"{BASE}/{dst}")
            except Exception as e:
                print("photo KO", r["token"], e); continue
        plist.append(dst)
    photos[r["token"]] = plist
    msg = f"היי, זה דוד. ראיתי את המודעה ביד2 על {r['prop']} ב{addr_he}. עדיין פנוי? אשמח לבוא לראות מחר."
    new.append({
        "id": r["token"], "tier": tier, "price_ils": r["price"], "price_label_en": f"{fmt_price(r['price'])}/month{incl}", "price_label_he": f"{fmt_price(r['price'])} לחודש{incl_he}",
        "title_en": f"{r['prop']} — {addr_he}, {hood}, {city_en} · {r['rooms']} rooms · {r['sqm']} m²{warn_en}",
        "title_he": f"{r['prop']} — {addr_he}, {hood}, {r['city']} · {r['rooms']} חד' · {r['sqm']} מ\"ר{warn_he}",
        "address_en": f"{addr_he}, {hood}, {city_en} (floor {r['floor']})", "address_he": f"{addr_he}, {hood}, {r['city']} (קומה {r['floor']})",
        "why_en": f"{furn} · {imm}{km} · published on Yad2 by a private owner ({r['name'] or 'no name'}), updated {r['updated']}.",
        "why_he": f"{furn_he} · {imm_he}{km_he} · מודעה פרטית ביד2 ({r['name'] or 'ללא שם'}), עודכן {r['updated']}.",
        "original_quote_he": (r["desc"] or "")[:400], "contact_name": r["name"] or "", "phone": r["tel"],
        "whatsapp_url": wa(num, msg) if (num and not r["virtual"]) else "",
        "source_name": "Yad2", "source_url": r["url"], "dorin_url": "", "badges_en": [b for b in [furn, imm, "bills included" if r["all_inclusive_hint"] else "", city_en] if b],
        "badges_he": [b for b in [furn_he, imm_he, "כולל חשבונות" if r["all_inclusive_hint"] else "", r["city"]] if b],
        "photo_key": r["token"], "wa_status_en": st_en, "wa_status_he": st_he, "rank": 0})

# ── 3. ordre : RDV/contacts actifs, puis messages envoyés, puis à appeler (prix croissant), puis bonus ──
order = {"TOP": 0, "NEW_TOP": 1, "BONUS": 2}
new.sort(key=lambda a: (order.get(a["tier"], 3), 0 if "📩" in a.get("wa_status_en", "") else 1, a.get("price_ils") or 9999))
for i, a in enumerate(new, 1): a["rank"] = i
json.dump(new, open(f"{BASE}/apartments.json", "w"), ensure_ascii=False, indent=1)
json.dump(photos, open(f"{BASE}/downloaded_photos.json", "w"), ensure_ascii=False, indent=1)
print(len(new), "fiches écrites")
for a in new: print(a["rank"], a["tier"], a["price_ils"], a["title_en"][:60], "|", a["phone"], "|", a.get("wa_status_en", "")[:60])
