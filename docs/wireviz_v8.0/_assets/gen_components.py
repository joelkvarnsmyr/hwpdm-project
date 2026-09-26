"""Genererar resistor-färgkodsbilder (5-band, 1% metallfilm) + en diod.
Banden är deterministiska från värdet → ingen extern repo behövs.
Kör: python gen_components.py  (sparar PNG i samma mapp)
"""
from PIL import Image, ImageDraw, ImageFont

# Färgband → RGB (DIN/IEC standard)
BANDCOL = {
    'black': (20, 20, 20), 'brown': (120, 70, 30), 'red': (200, 30, 30),
    'orange': (230, 120, 20), 'yellow': (235, 205, 40), 'green': (40, 150, 60),
    'blue': (40, 90, 200), 'violet': (150, 60, 180), 'grey': (130, 130, 130),
    'white': (245, 245, 245), 'gold': (200, 160, 60), 'silver': (190, 190, 190),
}
DIGIT = ['black','brown','red','orange','yellow','green','blue','violet','grey','white']
# multiplikator-exponent → färg
MULT = {-2:'silver', -1:'gold', 0:'black', 1:'brown', 2:'red', 3:'orange',
        4:'yellow', 5:'green', 6:'blue'}

def bands_5(value_ohm):
    """3 signifikanta + multiplikator + tolerans(brun=1%)."""
    # normalisera till 3 sigfigs
    exp = 0
    v = float(value_ohm)
    # hitta mantissa 100..999
    while v >= 1000:
        v /= 10; exp += 1
    while v < 100:
        v *= 10; exp -= 1
    m = int(round(v))            # 100..999
    d1, d2, d3 = m // 100, (m // 10) % 10, m % 10
    return [DIGIT[d1], DIGIT[d2], DIGIT[d3], MULT[exp], 'brown']

def label(value_ohm):
    if value_ohm >= 1000:
        s = value_ohm/1000
        return (f"{s:g}k").replace('.0k','k') + "Ω"
    return f"{value_ohm:g}Ω"

def draw_resistor(value_ohm, fname):
    W, H = 360, 150
    img = Image.new('RGB', (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    # ledningar
    bodyL, bodyR, cy = 90, 270, 70
    d.line([(20, cy), (bodyL, cy)], fill=(120,120,120), width=4)
    d.line([(bodyR, cy), (W-20, cy)], fill=(120,120,120), width=4)
    # kropp (beige metallfilm)
    d.rounded_rectangle([bodyL, cy-26, bodyR, cy+26], radius=14, fill=(225, 215, 180), outline=(150,140,110), width=2)
    # band
    bands = bands_5(value_ohm)
    xs = [bodyL+28, bodyL+58, bodyL+88, bodyL+128, bodyR-28]
    for x, b in zip(xs, bands):
        d.rectangle([x-7, cy-26, x+7, cy+26], fill=BANDCOL[b])
    # text
    try:
        font = ImageFont.truetype("arialbd.ttf", 26)
        fsm = ImageFont.truetype("arial.ttf", 15)
    except Exception:
        font = ImageFont.load_default(); fsm = font
    txt = label(value_ohm) + " 1%"
    d.text((W/2, cy+44), txt, fill=(20,20,20), anchor="mm", font=font)
    bandnames = '-'.join(bands)
    d.text((W/2, H-12), bandnames, fill=(110,110,110), anchor="mm", font=fsm)
    img.save(fname)
    print(f"{value_ohm} ohm  {bandnames}  -> {fname}")

def draw_diode(fname):
    W, H = 360, 130
    img = Image.new('RGB', (W, H), (255,255,255))
    d = ImageDraw.Draw(img)
    cy = 60
    d.line([(20, cy), (120, cy)], fill=(120,120,120), width=4)   # anod-lead
    d.line([(240, cy), (W-20, cy)], fill=(120,120,120), width=4) # katod-lead
    d.rounded_rectangle([120, cy-24, 240, cy+24], radius=8, fill=(35,35,35), outline=(0,0,0), width=2)
    # katod-band (vit stripe nära katoden = höger)
    d.rectangle([224, cy-24, 234, cy+24], fill=(245,245,245))
    try:
        font = ImageFont.truetype("arialbd.ttf", 22); fsm = ImageFont.truetype("arial.ttf", 15)
    except Exception:
        font = ImageFont.load_default(); fsm = font
    d.text((70, cy-40), "ANOD", fill=(20,20,20), anchor="mm", font=fsm)
    d.text((300, cy-40), "KATOD (band)", fill=(20,20,20), anchor="mm", font=fsm)
    d.text((W/2, H-16), "Spärrdiod — band mot C3", fill=(20,20,20), anchor="mm", font=font)
    img.save(fname)
    print(f"diod -> {fname}")

if __name__ == '__main__':
    for v in [5600, 10000, 4700, 22000, 2200, 82, 150]:
        tag = (f"{v//1000}k{(v%1000)//100}" if v >= 1000 else f"{v}r").replace('k0','k')
        draw_resistor(v, f"r_{tag}.png")
    draw_diode("diode.png")
