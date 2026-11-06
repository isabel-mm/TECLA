"""Nube de palabras de los candidatos a término.

Se dibuja con Pillow y numpy (ya instalados con matplotlib), sin dependencias
nuevas: cada candidato se coloca, de mayor a menor peso, en el primer hueco
libre de una espiral que parte del centro de la imagen.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Paleta de TECLA: violetas y verdes azulados
DEFAULT_COLORS = ("#7c3aed", "#6d28d9", "#4c1d95", "#0d9488", "#0f766e", "#a855f7")


def _font_path() -> str | None:
    """Ruta de DejaVu Sans, la fuente que acompaña a matplotlib."""
    try:
        from matplotlib import font_manager
        return font_manager.findfont("DejaVu Sans", fallback_to_default=True)
    except Exception:
        return None


def _load_font(path: str | None, size: int):
    if path:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def generate_word_cloud(
    words: Iterable[tuple[str, float]],
    path: Path | str,
    width: int = 1600,
    height: int = 900,
    max_words: int = 120,
    min_font: int = 14,
    max_font: int = 120,
    background: str = "#ffffff",
    colors: Sequence[str] = DEFAULT_COLORS,
    margin: int = 4,
) -> Path | None:
    """Dibuja la nube y la guarda como PNG en ``path``.

    ``words`` son pares (forma, peso); el tamaño de cada forma es proporcional
    a la raíz de su peso. Devuelve la ruta guardada o ``None`` si no hay
    palabras con peso positivo.
    """
    items = sorted(((w.strip(), float(v)) for w, v in words if w and w.strip() and v > 0),
                   key=lambda x: -x[1])[:max_words]
    if not items:
        return None

    top, low = math.sqrt(items[0][1]), math.sqrt(items[-1][1])
    span = (top - low) or 1.0

    img = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(img)
    occupied = np.zeros((height, width), dtype=bool)
    font_file = _font_path()
    cx, cy = width / 2, height / 2

    for i, (word, weight) in enumerate(items):
        size = int(min_font + (max_font - min_font) * (math.sqrt(weight) - low) / span)
        while size >= min_font:
            font = _load_font(font_file, size)
            x0, y0, x1, y1 = draw.textbbox((0, 0), word, font=font)
            w, h = x1 - x0 + 2 * margin, y1 - y0 + 2 * margin
            if w < width and h < height:
                spot = _find_spot(occupied, w, h, cx, cy)
                if spot is not None:
                    break
            size = int(size * 0.85)   # no cabe: se prueba más pequeña
        else:
            continue                  # ni siquiera al tamaño mínimo
        px, py = spot
        occupied[py:py + h, px:px + w] = True
        draw.text((px + margin - x0, py + margin - y0), word, font=font,
                  fill=colors[i % len(colors)])

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return path


def _find_spot(occupied: np.ndarray, w: int, h: int, cx: float, cy: float):
    """Primer hueco libre de ``w`` × ``h`` a lo largo de una espiral."""
    H, W = occupied.shape
    aspect = W / H
    t = 0.0
    limit = math.hypot(W, H)
    while True:
        r = 2.2 * t
        if r > limit:
            return None
        x = int(cx + r * math.cos(t) * aspect - w / 2)
        y = int(cy + r * math.sin(t) - h / 2)
        if 0 <= x and 0 <= y and x + w <= W and y + h <= H:
            if not occupied[y:y + h, x:x + w].any():
                return x, y
        t += 0.35 if r < 40 else 6.0 / r
