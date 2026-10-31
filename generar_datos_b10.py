"""Rellena las columnas elemento, etiquetas y pasiva de cartas.csv con los valores automáticos (una sola vez).
Las celdas que ya tengan algo NO se tocan. Uso: python generar_datos_b10.py <ruta a cartas.csv>"""
import csv, sys
ELEMENTOS = ["Vocal", "Baile", "Rap", "Visual", "Carisma"]
ETIQUETAS = ["Debut", "Escenario", "Casual"]
DESFASE = {"C": 0, "R": 2, "E": 4, "L": 1}
PASIVAS = {"Tank": ["aguante", "coraza"], "DPS": ["filo", "cazajefes"], "Support": ["inspirar", "fortuna"]}
ruta = sys.argv[1]
with open(ruta, encoding="utf-8-sig", newline="") as f:
    filas = list(csv.reader(f))
cab = filas[0][:5] + ["elemento", "etiquetas", "pasiva"]
nuevas = [cab]
for r in filas[1:]:
    if not r or not r[0].strip():
        continue
    r = [c.strip() for c in r] + [""] * 8
    cid, rol = r[0], r[2]
    n = max(1, int(cid[1:])); off = DESFASE[cid[0]]
    elem = r[5] or ELEMENTOS[(n - 1 + off) % 5]
    etq = r[6] or ETIQUETAS[(n - 1 + off) % 3]
    pas = r[7] or PASIVAS[rol][n % 2]
    nuevas.append(r[:5] + [elem, etq, pas])
with open(ruta, "w", encoding="utf-8", newline="") as f:
    csv.writer(f, lineterminator="\n").writerows(nuevas)
print(len(nuevas) - 1, "cartas con elemento, etiquetas y pasiva")
