#!/usr/bin/env python3
"""Sends the Bilingual (English + Hebrew) Bat Yam Sublets Dossier (Links + PDF + Photos) to David & Leeya."""
import json
import os
import time
import urllib.request

BASE = "/Users/dreamnova/.gemini/antigravity/scratch/bat-yam-sublets"
WA_URL = "http://127.0.0.1:3010"
TOKEN = open(os.path.expanduser("~/.nova/wa_token")).read().strip()

DAVID_JID = "972584921492@s.whatsapp.net"
LEEYA_JID = "91564458151954@lid"

SITE_URL = "https://codenolimits.github.io/bat-yam-sublets/"
PDF_URL = "https://codenolimits.github.io/bat-yam-sublets/bat-yam-sublets-en-he.pdf"
PDF_PATH = os.path.join(BASE, "bat-yam-sublets-en-he.pdf")


def wa_post(endpoint: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"{WA_URL}{endpoint}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=40) as resp:
        return json.loads(resp.read().decode("utf-8"))


MESSAGE_EN_HE = f"""🏖️ *BAT YAM SUBLETS & STUDIOS ≤ ₪3,000 (IMMEDIATE MOVE-IN BEFORE TUESDAY — NO CHECKS)*
🇮🇱 *סאבלט ודירות בבת ים עד 3,000 ₪ — כניסה מיידית לפני יום שלישי (ללא צ'קים / כולל הכל)*

🌐 *Live Bilingual Website (Photos + Direct Links):*
{SITE_URL}

📄 *Direct PDF Link (English + עברית + Photos):*
{PDF_URL}

━━━━━━━━━━━━━━━
🥇 *#1 — Beachfront Hotel Studio — ₪3,000 ALL-INCLUSIVE (כולל הכל)*
🇬🇧 *EN:* Furnished studio inside a beachfront hotel (Derech Ben Gurion 59). ₪3,000/month ALL-INCLUSIVE (electricity, water, Arnona). Zero checks, zero bill transfers, immediate entry.
🇮🇱 *HE:* יחידה בתוך מלון מרוהטת מול הים (דרך בן גוריון 59) — 3,000 ש"ח לחודש כולל הכל! כניסה מיידית ללא העברת חשבונות וללא צ'קים.
👤 Katia (קטיה)
🔗 Yad2: https://www.yad2.co.il/realestate/item/jrrvxsu7
🔗 Card: https://dorin.app/apartments/123e4797-95be-42ef-9c11-5661acfd8c87

🥈 *#2 — Whole Apt Sublet / Immediate Takeover — ₪2,800 (Herzl 1)*
🇬🇧 *EN:* Tenant moving out immediately! ₪2,800/mo + electricity only — *Landlord pays Arnona & all other bills!* Washer + dryer included. Near Light Rail & beach.
🇮🇱 *HE:* פינוי מיידי של דירה בהרצל 1 (קומה 4)! קיים מייבש ומכונת כביסה. רק 2,800 ש"ח + חשמל — כל שאר התשלומים על בעל הדירה!
👤 Lior Palatshi: *050-5988688*
💬 WhatsApp: https://wa.me/972505988688
🔗 Facebook: https://www.facebook.com/groups/201105170260427/posts/2917317895305794/

🥉 *#3 — Furnished Studios Short/Long Term — ₪2,950 (Rothschild 39)*
🇬🇧 *EN:* Ground floor furnished studio with yard & parking in central Bat Yam. *All taxes included & NO utility bill transfers (ללא העברת חשבונות)*, no broker, immediate entry.
🇮🇱 *HE:* ללא תווך! דירת סטודיו מרוהטת ומאובזרת ברחוב רוטשילד 39 במרכז בת ים, קומת קרקע, כולל כל המסים וללא העברת חשבונות! לכניסה מיידית.
📞 Direct: *052-555-1920*
💬 WhatsApp: https://wa.me/972525551920
🔗 Link: https://www.glotels.com/IL/Bat-Yam/113533053613891/%D7%A1%D7%90%D7%91%D7%9C%D7%98-%D7%91%D7%AA-%D7%99%D7%9D.-%D7%93%D7%99%D7%A8%D7%95%D7%AA-%D7%9C%D7%98%D7%95%D7%95%D7%97-%D7%90%D7%A8%D7%95%D7%9A%5C%D7%A7%D7%A6%D7%A8

⭐ *#4 — 100% Furnished Sublet — ₪2,750 (Bank Transfer & Simple Contract)*
🇬🇧 *EN:* 100% furnished (new A/C), *very simple contract*, bills paid by *bank transfer*, 50% Olim Arnona discount active.
🇮🇱 *HE:* סאבלט מרוהט ב-100% בבת ים (מזגן חדש), חוזה פשוט ביותר ותשלום בהעברה בנקאית (2,750 ש"ח).
👤 Jacob Lee
🔗 Facebook: https://www.facebook.com/groups/1424244737803677/posts/4702245673336884/
🔗 Card (11 Photos): https://dorin.app/apartments/f2e0a51f-cfee-409e-96aa-951a2c966ce5

⭐ *#5 — Direct Beach Sublet — ₪2,000 + ~₪500 Bills (Rothschild St.)*
🇬🇧 *EN:* Cozy sublet 5 min walk from the beach, zero checks.
🇮🇱 *HE:* סאבלט ברחוב רוטשילד (5 דק' הליכה מהים), אווירה ביתית — 2,000 ש"ח + 500 חשבונות.
👤 Sivan Zaudi: *053-9620132*
💬 WhatsApp: https://wa.me/972539620132
🔗 Facebook: https://www.facebook.com/groups/101875683484689/posts/3043521049320123/

⭐ *#6 — Furnished Room w/ Balcony — ₪2,200 ALL BILLS INCLUDED (Balfour 88)*
🇬🇧 *EN:* Fully furnished room with balcony, ₪2,200/mo including all bills, immediate entry.
🇮🇱 *HE:* חדר מרוהט מלא עם מרפסת בבלפור 88 — 2,200 ש"ח כולל חשבונות, כניסה מיידית.
👤 Tais Netanel
🔗 Yad2: https://www.yad2.co.il/realestate/item/i6vv6o68

⭐ *#7 — Full 3-Room Apartment (70m²) — ₪3,000 Only (Givati St.)*
🇬🇧 *EN:* Whole 3-room apartment (70 sqm) for ₪3,000/mo, immediate entry (discounted for short/medium term due to Tama 38).
🇮🇱 *HE:* דירת 3 חדרים שלמה (70 מ"ר) ברחוב גבעתי ב-3,000 ש"ח בלבד לכניסה מיידית!
👤 Roman Eylon: *052-8555977*
💬 WhatsApp: https://wa.me/972528555977
🔗 Facebook: https://www.facebook.com/groups/201105170260427/posts/2942598629444387/

🔥 *More Direct Short-Term / Studio Numbers:*
• *#8 Erez Nahom (1–6 Months Sublet, Rova Ayalon, Furnished option):* `052-2424676` · https://wa.me/972522424676
• *#9 Shai (Housing Unit / יחידת דיור Kinamon St., Immediate entry):* `054-2474592` · https://wa.me/972542474592
• *#10 Andrey Sokach (Seafront Short-Term Studio, Park HaYam):* `+972-52-321-1155` · https://wa.me/972523211155
• *#11 Ahmad Magdoub (2.5 Rooms 70m², Bar Yehuda 3 — ₪3,000):* https://www.yad2.co.il/realestate/item/ymth4hcu
• *#12 David (2 Rooms Eilat 13 — ₪3,100 Immediate):* `054-5655206` · https://wa.me/972545655206

🤖 *Autonomous Search Agent:* Active every 6 hours (cron) — any new Bat Yam sublet ≤ ₪3,200 is automatically added to {SITE_URL} and sent here!"""

KEY_PHOTOS = [
    ("photos/123e4797_0.jpg", "🥇 #1 — ₪3,000 All-Inclusive Beachfront Hotel Studio (Derech Ben Gurion 59) | יחידה במלון מול הים 3,000 ₪ כולל הכל\n🔗 https://www.yad2.co.il/realestate/item/jrrvxsu7"),
    ("photos/085ee373_0.jpg", "🥈 #2 — ₪2,800 Whole Apt Sublet Herzl 1 (Landlord pays taxes!) | סאבלט דירה שלמה הרצל 1 — ליאור 050-5988688\n💬 https://wa.me/972505988688"),
    ("photos/f2e0a51f_0.jpg", "⭐ #4 — ₪2,750 100% Furnished Sublet (Simple Contract + Bank Transfer) | סאבלט מרוהט קומפלט 2,750 ₪\n🔗 https://dorin.app/apartments/f2e0a51f-cfee-409e-96aa-951a2c966ce5"),
    ("photos/f20a754b_0.jpg", "⭐ #6 — ₪2,200 All Bills Included (Balfour 88 w/ Balcony) | בלפור 88 כולל חשבונות 2,200 ₪\n🔗 https://www.yad2.co.il/realestate/item/i6vv6o68"),
]


def send_bundle(target_jid: str, label: str):
    print(f"Sending bilingual message to {label} ({target_jid})...")
    r1 = wa_post("/send", {"to": target_jid, "text": MESSAGE_EN_HE})
    print("  Text sent:", r1)
    time.sleep(1.5)

    print(f"Sending PDF document to {label} ({target_jid})...")
    r2 = wa_post("/send-doc", {
        "to": target_jid,
        "path": PDF_PATH,
        "mime": "application/pdf",
        "caption": f"📄 Bat Yam Sublets & Studios ≤ ₪3,000 (English + עברית + Photos)\n🌐 Web: {SITE_URL}"
    })
    print("  PDF sent:", r2)
    time.sleep(1.5)

    for rel_img, cap in KEY_PHOTOS:
        img_path = os.path.join(BASE, rel_img)
        if os.path.exists(img_path):
            r_img = wa_post("/send-doc", {
                "to": target_jid,
                "path": img_path,
                "mime": "image/jpeg",
                "caption": cap
            })
            print(f"  Photo {rel_img} sent:", r_img.get("ok"))
            time.sleep(1.2)


if __name__ == "__main__":
    send_bundle(DAVID_JID, "David")
    send_bundle(LEEYA_JID, "Leeya")
    print("ALL SENT SUCCESSFULLY TO DAVID & LEEYA!")
