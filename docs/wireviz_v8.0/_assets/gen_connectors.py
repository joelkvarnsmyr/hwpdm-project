"""Genererar stiliserade DT-kontakt-ikoner (12-pol) i husfärg → _assets/connectors/.
Platshållare tills riktiga foton läggs in (samma filnamn). Kör: python gen_connectors.py
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "connectors")
os.makedirs(OUT, exist_ok=True)

HOUS = {
    "dt_gra":   ((140, 140, 140), "GRÅ",  "A"),
    "dt_gron":  ((45, 140, 75),   "GRÖN", "C"),
    "dt_svart": ((45, 45, 48),    "SVART","B"),
    "dt_brun":  ((110, 70, 42),   "BRUN", "D"),
}

def lighten(c, f=0.35):
    return tuple(int(v + (255 - v) * f) for v in c)
def darken(c, f=0.35):
    return tuple(int(v * (1 - f)) for v in c)

def draw(name, color, label, kontakt):
    W, H = 360, 210
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    # hus
    x0, y0, x1, y1 = 40, 30, 320, 150
    d.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=color, outline=darken(color), width=3)
    # litet "läpp"-spår upptill (DT-känsla)
    d.rounded_rectangle([x0 + 14, y0 - 8, x1 - 14, y0 + 12], radius=8, fill=darken(color, 0.15), outline=darken(color), width=2)
    # 12 håligheter (2 rader × 6)
    socket = lighten(color, 0.55) if name != "dt_svart" else (90, 90, 95)
    cols, rows = 6, 2
    gx0, gy0, gx1, gy1 = x0 + 26, y0 + 34, x1 - 26, y1 - 22
    for r in range(rows):
        for c in range(cols):
            cx = gx0 + (gx1 - gx0) * c / (cols - 1)
            cy = gy0 + (gy1 - gy0) * r / (rows - 1)
            d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=socket, outline=darken(color), width=2)
    # text
    try:
        f1 = ImageFont.truetype("arialbd.ttf", 26)
        f2 = ImageFont.truetype("arial.ttf", 16)
    except Exception:
        f1 = ImageFont.load_default(); f2 = f1
    d.text((W / 2, 174), f"Deutsch DT 12-pol", fill=(20, 20, 20), anchor="mm", font=f1)
    d.text((W / 2, 196), f"Kontakt {kontakt} · {label} hus", fill=(110, 110, 110), anchor="mm", font=f2)
    p = os.path.join(OUT, name + ".png")
    img.save(p)
    print("->", p)

if __name__ == "__main__":
    for name, (color, label, kontakt) in HOUS.items():
        draw(name, color, label, kontakt)
