"""Capturas numeradas de la guía de uso (docs/guia/img/), a partir de las de la web (web/img/).
Las coordenadas son las de una ventana de 1420 px de ancho; las de Evaluación, de una vista de 2000 px.
Uso, desde la raíz del repositorio: python3 docs/guia/anotar_capturas.py"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[2]; SRC = ROOT / "web/img"; OUT = ROOT / "docs/guia/img"
COL = (124, 58, 237)   # #7c3aed, el violeta de TECLA
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
SPECS = {
    "inicio": (1420, [(14, 105, 272, 500), (16, 506, 264, 602), (10, 805, 280, 857), (308, 14, 1402, 58)]),
    "corpus": (1420, [(308, 140, 1402, 307), (353, 380, 549, 643), (1088, 380, 1298, 643), (316, 700, 1018, 802)]),
    "extraccion": (1420, [(308, 140, 1402, 220), (308, 262, 1402, 356), (308, 420, 975, 512), (308, 518, 1402, 805), (1236, 386, 1402, 418)]),
    "evaluacion": (2000, [(437, 200, 1972, 494), (445, 522, 852, 815), (450, 828, 830, 870), (872, 505, 1492, 780), (872, 795, 1492, 1134), (1507, 505, 1970, 1134)]),
    "revision": (1420, [(305, 140, 905, 164), (310, 215, 568, 846), (1058, 238, 1368, 278), (603, 336, 797, 362), (603, 380, 1366, 682), (603, 703, 1366, 788)]),
}
OUT.mkdir(exist_ok=True)
for name, (base, boxes) in SPECS.items():
    im = Image.open(SRC / f"{name}.png").convert("RGB"); k = im.width / base
    s = im.width / 1420                       # grosor y tamaño de los números, según el ancho de la ventana
    d = ImageDraw.Draw(im); font = ImageFont.truetype(FONT, round(21 * s)); r = round(15 * s)
    for i, (x0, y0, x1, y1) in enumerate(boxes, 1):
        d.rounded_rectangle([x0 * k, y0 * k, x1 * k, y1 * k], radius=round(8 * s), outline=COL, width=max(2, round(3 * s)))
        cx = min(x1 * k - 2 * s, im.width - r - 2); cy = max(y0 * k + 2 * s, r + 2)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=COL); d.text((cx, cy), str(i), fill="white", font=font, anchor="mm")
    im.save(OUT / f"{name}.png", optimize=True); print(name, im.size)
