"""Valida cartas.csv + banners.json + cartas/*.webp y genera catalogo.json y manifest.json.
Uso (en esta carpeta):  python publicar.py      Luego sube los cambios con GitHub Desktop."""
import csv, datetime, hashlib, json, os, sys

base = os.path.dirname(os.path.abspath(__file__))
RAREZAS = {"C": "Común", "R": "Rara", "E": "Épica", "L": "Legendaria"}
ROLES = {"Tank", "DPS", "Support"}
errores = []

# --- cartas ---
cartas, vistos = [], set()
with open(os.path.join(base, "cartas.csv"), encoding="utf-8-sig", newline="") as f:
    for n, r in enumerate(list(csv.reader(f))[1:], start=2):
        r = [c.strip() for c in r]
        if not r or not r[0]:
            continue
        if len(r) < 3:
            errores.append(f"cartas.csv fila {n}: faltan columnas"); continue
        cid, nombre, rol = r[0], r[1], r[2]
        cat = r[3] if len(r) > 3 else ""
        if cid[:1] not in RAREZAS: errores.append(f"{cid}: el prefijo debe ser C, R, E o L")
        if cid in vistos: errores.append(f"{cid}: id repetido")
        if rol not in ROLES: errores.append(f"{cid}: rol '{rol}' no válido")
        if not os.path.exists(os.path.join(base, "cartas", cid + ".webp")):
            errores.append(f"{cid}: falta cartas/{cid}.webp")
        vistos.add(cid)
        cartas.append({"id": cid, "nombre": nombre, "rol": rol, "categoria": cat, "imagen": f"cartas/{cid}.webp"})

# --- banners ---
with open(os.path.join(base, "banners.json"), encoding="utf-8") as f:
    banners = json.load(f)
ids_b = set()
for b in banners["banners"]:
    bid = b.get("id", "?")
    if bid in ids_b: errores.append(f"banner {bid}: id repetido")
    ids_b.add(bid)
    try:
        ini = datetime.date.fromisoformat(b["inicio"]); fin = datetime.date.fromisoformat(b["fin"])
        if fin <= ini: errores.append(f"banner {bid}: 'fin' debe ser posterior a 'inicio'")
    except Exception:
        errores.append(f"banner {bid}: fechas inválidas (usa AAAA-MM-DD)")
    for cid in [b.get("destacada")] + list(b.get("delanteras", [])):
        if cid not in vistos: errores.append(f"banner {bid}: la carta {cid} no existe")
    if abs(sum(b.get("probabilidades", {}).values()) - 100) > 0.01:
        errores.append(f"banner {bid}: las probabilidades no suman 100")

if errores:
    print("NO SE PUBLICÓ. Corrige esto:")
    for e in errores: print("  -", e)
    sys.exit(1)

catalogo = {"schema": 1, "cartas": cartas}
def volcar(nombre, datos):
    with open(os.path.join(base, nombre), "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
volcar("catalogo.json", catalogo)

# versión: sube solo si cambió el contenido (JSON o alguna imagen)
h = hashlib.sha256()
for nombre in ("catalogo.json", "banners.json"):
    h.update(open(os.path.join(base, nombre), "rb").read())
for c in cartas:
    h.update(open(os.path.join(base, c["imagen"]), "rb").read())
huella = h.hexdigest()[:16]
ruta_m = os.path.join(base, "manifest.json")
anterior = json.load(open(ruta_m)) if os.path.exists(ruta_m) else {"version": 0, "huella": ""}
if anterior.get("huella") == huella:
    print(f"Sin cambios (versión {anterior['version']}).")
else:
    volcar("manifest.json", {"schema": 1, "version": anterior["version"] + 1, "huella": huella,
                             "generado": datetime.datetime.now().isoformat(timespec="seconds")})
    print(f"Publicado: versión {anterior['version'] + 1} · {len(cartas)} cartas · {len(banners['banners'])} banner(s).")
    print("Ahora sube los cambios con GitHub Desktop (Commit + Push).")
