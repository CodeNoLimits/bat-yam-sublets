#!/usr/bin/env python3
"""Construit carte.html : carte réelle (OpenStreetMap) centrée sur la gare Bat Yam – Yoseftal.
Chaque appartement = un point ; au clic : heure du RDV, prix, adresse exacte, téléphone, WhatsApp, lien de l'annonce.
Données : visites.json (planning du jour) + apartments.json et fiches Yad2 (liens retrouvés par numéro de téléphone).
Géocodage Nominatim mis en cache dans carte_geo.json (1 requête/s, uniquement pour les nouvelles adresses).
Usage : python3 construire_carte.py   (appelé aussi à la fin de construire_site.py)"""
import glob, html, json, os, re, time, urllib.parse, urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.expanduser("~/Library/Application Support/Claude/scratch-workspaces/20ef188e-88be-4157-8b3d-721115ac1a8c/"
                         "82601c1b-6660-428b-92a5-b63a973e972f/scratch-2026-10-19-eb9d78")
YAD2 = "/private/tmp/claude-501/-Users-dreamnova/abfeee62-3dd5-48b9-b63c-85f96251bde3/scratchpad/yad2/items"
GARE = (32.0146109, 34.7619817)  # gare Bat Yam – Yoseftal (Israel Railways), OSM
CACHE = os.path.join(ICI, "carte_geo.json")
UA = "DreamNova-carte/1.0 (admin@holyrentals.com)"


def chiffres(t):
    d = re.sub(r"\D", "", t or "")
    return d[-9:] if len(d) >= 9 else ""


def liens_par_tel():
    """numéro (9 derniers chiffres) → URL de l'annonce."""
    out = {}
    for a in json.load(open(os.path.join(ICI, "apartments.json"))):
        for t in re.split(r"[·/,]", a.get("phone") or ""):
            if chiffres(t) and a.get("source_url"):
                out.setdefault(chiffres(t), a["source_url"])
    return out


def yad2_par_adresse():
    """« rue hébreu|numéro » → (lat, lon, url) d'après les fiches Yad2 (coordonnées exactes de l'annonce)."""
    out = {}
    for f in glob.glob(os.path.join(YAD2, "*.json")):
        try:
            d = json.load(open(f))
            a = d["full"]["address"]
            c = a["coords"]
            k = f"{a['street']['text']}|{a['house']['number']}"
            # plusieurs annonces à la même adresse → position gardée, lien retiré (impossible de savoir laquelle)
            out[k] = (float(c["lat"]), float(c["lon"]), None if k in out else d.get("url"))
        except Exception:
            continue
    return out


def en_hebreu(adr):
    for en, h in sorted(HE.items(), key=lambda x: -len(x[0])):
        adr = adr.replace(en, h)
    return adr


def adresse_propre(a):
    a = re.split(r" — |→|\(", a or "")[0].strip(" ,")
    a = re.sub(r",?\s*(Ramat Yosef|Amidar)\b", ", Bat Yam", a)
    if not re.search(r"Bat Yam|Holon", a):
        a += ", Bat Yam"
    return a


# Noms hébreux des rues (OSM connaît mieux les numéros en hébreu)
HE = {"Rothschild": "רוטשילד", "HaTanaim": "התנאים", "Anielewicz": "אנילביץ", "Eilat": "אילת", "Pinkas": "פנקס",
      "HaArava": "הערבה", "HaTchiya": "התחייה", "Tanin": "תנין", "Balfour": "בלפור", "Mivtza Sinai": "מבצע סיני",
      "Simtat HaTziporim": "סמטת הצפורנים", "Kibbutz Galuyot": "קיבוץ גלויות", "HaTzanhanim": "הצנחנים",
      "Bar Yehuda": "בר יהודה", "Ehad BeMai": "אחד במאי", "HaRav Uziel": "הרב עוזיאל", "Weizmann": "ויצמן",
      "Studios Herzl": "הרצל", "Herzl": "הרצל", "Sokolov": "סוקולוב", "Arlozorov": "ארלוזורוב", "Geoulim": "גאולים",
      "Bat Yam": "בת ים", "Holon": "חולון"}


def nominatim(q):
    r = json.load(urllib.request.urlopen(urllib.request.Request(
        "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
            {"format": "json", "limit": 1, "countrycodes": "il", "addressdetails": 1, "q": q}),
        headers={"User-Agent": UA}), timeout=20))
    time.sleep(1.1)
    if not r:
        return None
    return [float(r[0]["lat"]), float(r[0]["lon"]), "house_number" in r[0].get("address", {})]


def geocoder(adr, cache):
    """[lat, lon, numéro_trouvé] ; essaie l'anglais puis l'hébreu, garde le résultat au numéro exact."""
    if adr in cache and cache[adr] and len(cache[adr]) == 3:
        return cache[adr]
    he = en_hebreu(adr)
    try:
        best = None
        for q in (adr, he):
            r = nominatim(q)
            if r and (best is None or (r[2] and not best[2])):
                best = r
            if best and best[2]:
                break
    except Exception:
        return None  # erreur réseau : pas de cache, on retentera au prochain build
    cache[adr] = best
    return best


def main():
    v = json.load(open(os.path.join(SRC, "visites.json")))
    liens = liens_par_tel()
    y2 = yad2_par_adresse()
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    groupes = [("visites", "RDV aujourd'hui"), ("appeler", "À appeler"), ("attente", "En attente de réponse"),
               ("sans_numero", "Sans numéro (annonce)")]
    points, non_places = [], []
    for g, libelle in groupes:
        for x in v.get(g, []):
            brut = x.get("adresse") or x.get("titre") or ""
            adr = adresse_propre(brut)
            m_he = re.match(r"(.+?)\s+(\d+)\s*,", en_hebreu(adr))
            hit = y2.get(f"{m_he.group(1)}|{m_he.group(2)}") if m_he else None
            pos = [hit[0], hit[1], True] if hit else geocoder(adr, cache)
            tel = x.get("tel") or ""
            lien = x.get("source") or (hit[2] if hit else "") or ""
            if not lien:
                for t in re.split(r"[·/]", tel):
                    lien = lien or liens.get(chiffres(t), "")
            if not lien:
                m = re.search(r"Yad2 ([a-z0-9]{8})", x.get("note", ""))
                lien = f"https://www.yad2.co.il/realestate/item/{m.group(1)}" if m else ""
            p = {"groupe": g, "libelle": libelle, "statut": x.get("statut", ""), "heure": x.get("heure", ""),
                 "titre": x.get("titre", ""), "adresse": brut, "prix": x.get("prix", ""), "prix_note": x.get("prix_note", ""),
                 "contact": x.get("contact", ""), "tel": tel, "lien": lien,
                 "note": x.get("alerte") or x.get("note") or "", "distance": x.get("quartier", "")}
            if pos:
                p["lat"], p["lon"], p["exact"] = pos
                points.append(p)
            else:
                non_places.append(p)
    json.dump(cache, open(CACHE, "w"), ensure_ascii=False, indent=1)

    nav = open(os.path.join(ICI, "nav_commun.html")).read()
    page = PAGE.replace("__NAV__", nav).replace("__MAJ__", html.escape(v.get("maj", ""))) \
        .replace("__POINTS__", json.dumps(points, ensure_ascii=False)) \
        .replace("__GARE__", json.dumps(GARE)) \
        .replace("__NONPLACES__", "".join(
            f"<li><b>{html.escape(p['titre'] or p['adresse'])}</b> — {html.escape(p['adresse'])} · {html.escape(p['prix'])}"
            + (f" · <a href='tel:{html.escape(p['tel'])}'>{html.escape(p['tel'])}</a>" if chiffres(p['tel']) else "")
            + (f" · <a href='{html.escape(p['lien'])}' target='_blank' rel='noopener'>annonce</a>" if p['lien'] else "") + "</li>"
            for p in non_places))
    open(os.path.join(ICI, "carte.html"), "w").write(page)
    print(f"carte.html : {len(points)} points placés, {len(non_places)} non placés, "
          f"{sum(1 for p in points if p['lien'])} avec lien d'annonce")


PAGE = r"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Carte des appartements</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
:root{--fond:#f6f7f5;--texte:#1d2a2b;--doux:#5b6b6c;--carte:#fff;--bord:#dfe5e4}
@media (prefers-color-scheme:dark){:root{--fond:#121818;--texte:#e8eeee;--doux:#9fb0b0;--carte:#1b2324;--bord:#2c3839}}
*{box-sizing:border-box}body{margin:0;background:var(--fond);color:var(--texte);font:15px/1.45 -apple-system,system-ui,Segoe UI,sans-serif}
header{padding:12px 16px}h1{font-size:19px;margin:0 0 2px}header p{margin:0;color:var(--doux);font-size:13px}
#carte{height:72vh;min-height:420px;margin:0 16px;border-radius:14px;border:1px solid var(--bord)}
.legende{display:flex;flex-wrap:wrap;gap:10px;padding:10px 16px;font-size:13px;color:var(--doux)}
.legende span{display:inline-flex;align-items:center;gap:6px}.legende i{width:12px;height:12px;border-radius:50%;display:inline-block}
.leaflet-popup-content{margin:12px 14px;font:14px/1.45 -apple-system,system-ui,sans-serif;min-width:220px}
.pop h3{margin:0 0 4px;font-size:15px}.pop .h{font-weight:700;color:#0f6e74}.pop .px{font-size:16px;font-weight:700}
.pop .l{display:block;margin-top:6px}.pop .btn{display:inline-block;margin:6px 6px 0 0;padding:6px 10px;border-radius:8px;background:#0f6e74;color:#fff!important;text-decoration:none;font-weight:600;font-size:13px}
.pop .btn.wa{background:#1f9d55}.pop .btn.gris{background:#6b7b7c}.pop small{color:#5b6b6c}
.etiq{background:#fff;border:1px solid #0f6e74;border-radius:6px;padding:0 4px;font:700 11px system-ui;color:#0f6e74;white-space:nowrap}
section{padding:8px 16px 24px}section ul{padding-left:18px}a{color:#0f6e74}
</style></head><body>__NAV__
<header><h1>🗺️ Appartements autour de la gare Bat Yam – Yoseftal</h1>
<p>Mis à jour : __MAJ__ · cercles = 1 km et 2 km autour de la gare · clique sur un point pour l'adresse, le téléphone et l'annonce.</p></header>
<div class="legende"><span><i style="background:#1f9d55"></i>RDV confirmé</span><span><i style="background:#e08a00"></i>RDV proposé / à confirmer</span>
<span><i style="background:#2f6fd6"></i>À appeler</span><span><i style="background:#8a96a0"></i>En attente de réponse</span><span>🚆 gare</span></div>
<div id="carte" role="application" aria-label="Carte des appartements"></div>
<section><h2 style="font-size:16px">Non placés sur la carte (adresse imprécise)</h2><ul>__NONPLACES__</ul></section>
<script>
const P=__POINTS__, G=__GARE__;
const m=L.map('carte').setView(G,15);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap'}).addTo(m);
L.marker(G,{icon:L.divIcon({html:'<div style="font-size:26px">🚆</div>',className:'',iconSize:[28,28],iconAnchor:[14,14]})})
 .addTo(m).bindPopup('<b>Gare Bat Yam – Yoseftal</b><br><a target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&query='+G[0]+','+G[1]+'">Ouvrir dans Maps</a>');
[1000,2000].forEach(r=>L.circle(G,{radius:r,color:'#0f6e74',weight:1,fill:false,dashArray:'4 6'}).addTo(m));
const esc=s=>(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const couleur=p=>p.groupe==='visites'?(p.statut==='confirme'?'#1f9d55':'#e08a00'):p.groupe==='appeler'?'#2f6fd6':'#8a96a0';
const tels=t=>(t||'').split(/[·\/]/).map(x=>x.trim()).filter(x=>x.replace(/\D/g,'').length>=9);
const wa=t=>'https://wa.me/972'+t.replace(/\D/g,'').replace(/^0/,'');
const pts=[], vus={};
P.forEach(p=>{
  const k=p.lat.toFixed(5)+','+p.lon.toFixed(5); const n=vus[k]=(vus[k]||0)+1;
  if(n>1){p.lat+=0.00018*(n-1); p.lon+=0.00018*(n-1);}
  const c=couleur(p);
  const mk=L.circleMarker([p.lat,p.lon],{radius:10,color:'#fff',weight:2,dashArray:p.exact?null:'3 3',fillColor:c,fillOpacity:.95}).addTo(m);
  if(p.heure) mk.bindTooltip(p.heure+' · '+p.prix,{permanent:true,direction:'top',offset:[0,-8],className:'etiq'});
  let h='<div class="pop">';
  if(p.heure) h+='<div class="h">🕒 '+esc(p.heure)+' — '+esc(p.libelle)+'</div>'; else h+='<div class="h">'+esc(p.libelle)+'</div>';
  h+='<h3>'+esc(p.titre||p.adresse)+'</h3>';
  h+='<div class="px">'+esc(p.prix)+'</div>'+(p.prix_note?'<small>'+esc(p.prix_note)+'</small>':'');
  if(!p.exact) h+='<small>⚠️ Position approximative (milieu de la rue, numéro introuvable sur la carte)</small>';
  h+='<span class="l">📍 <a target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&query='+p.lat+','+p.lon+'">'+esc(p.adresse)+'</a></span>';
  if(p.distance) h+='<small>'+esc(p.distance)+'</small>';
  if(p.contact) h+='<span class="l">👤 '+esc(p.contact)+'</span>';
  const T=tels(p.tel);
  if(T.length) T.forEach(t=>{h+='<a class="btn" href="tel:'+t.replace(/[^\d+]/g,'')+'">📞 '+esc(t)+'</a><a class="btn wa" target="_blank" rel="noopener" href="'+wa(t)+'">WhatsApp</a>';});
  else if(p.tel) h+='<span class="l">📞 '+esc(p.tel)+'</span>';
  h+=p.lien?'<a class="btn gris" target="_blank" rel="noopener" href="'+esc(p.lien)+'">🔗 Voir l\'annonce</a>':'<span class="l"><small>Pas de lien d\'annonce enregistré</small></span>';
  if(p.note) h+='<p style="margin:8px 0 0"><small>'+esc(p.note)+'</small></p>';
  mk.bindPopup(h+'</div>'); pts.push([p.lat,p.lon]);
});
if(pts.length) m.fitBounds(L.latLngBounds(pts.concat([G])).pad(.08));
</script></body></html>"""

if __name__ == "__main__":
    main()
