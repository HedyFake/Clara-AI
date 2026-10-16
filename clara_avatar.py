"""Clara avatar renderer.

Prioritas v3.3 memakai 15 frame hasil crop spritesheet ekspresi pengguna. Frame dibuat
transparan, dipilih menurut mood/status mendengar/berpikir/berbicara, dan diberi gerak
halus. Renderer prosedural lama tetap disimpan sebagai fallback bila aset tidak ada.

Frame di-cache per kombinasi ekspresi/status/ukuran agar animasi tetap ringan. Modul
ini tidak membutuhkan tkinter, jadi jalur render dapat diuji terpisah.
"""

from __future__ import annotations

import io
import math
import sys
from pathlib import Path
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

# Warna kunci transparan untuk jendela mengambang Windows (-transparentcolor).
# Dibuat hampir hitam supaya tepi anti-alias tampak seperti garis tepi gelap,
# bukan "pinggiran magenta".
KEY_COLOR = (1, 2, 3)

INK = (14, 16, 30)
HAIR = (11, 13, 26)
HAIR_HI = (46, 56, 98)
SKIN = (253, 229, 218)
SKIN_SH = (240, 200, 190)
BLUSH = (255, 150, 170)
HOOD = (44, 74, 138)
HOOD_DK = (28, 48, 100)
HOOD_LT = (78, 112, 180)
SHIRT = (26, 44, 92)
PHONE = (150, 163, 188)
PHONE_LT = (205, 214, 232)
PHONE_DK = (92, 104, 128)
GLASS_FRAME = (22, 28, 44)
CYAN = (111, 216, 255)
CYAN_DK = (28, 118, 205)
IRIS = (30, 62, 150)
LIP = (170, 66, 96)
GLOVE = (24, 26, 38)

MOODS = ("happy", "listening", "thinking", "speaking", "surprised", "sad", "sleepy")

VW, VH = 400, 470  # kanvas virtual


def _catmull(points, closed=True, steps=8):
    """Spline Catmull-Rom supaya bentuk rambut/wajah mulus."""
    pts = list(points)
    n = len(pts)
    out = []
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if closed or i > 0 else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed or i + 2 < n else pts[(i + 1) % n]
        for s in range(steps):
            t = s / steps
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    if not closed:
        out.append(pts[-1])
    return out


class _Canvas:
    """Pembungkus ImageDraw dengan koordinat virtual 400x470.

    ImageDraw pada gambar RGBA TIDAK melakukan alpha-blending, jadi warna semi-transparan
    digambar di layer sementara lalu di-composite (supaya pipi/lensa tampak benar)."""

    def __init__(self, scale: float, size=(VW, VH)):
        self.k = scale
        self.img = Image.new("RGBA", (int(size[0] * scale), int(size[1] * scale)), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def _go(self, fn, *colors):
        if any(isinstance(c, tuple) and len(c) == 4 and c[3] < 255 for c in colors):
            layer = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
            fn(ImageDraw.Draw(layer))
            self.img.alpha_composite(layer)
        else:
            fn(self.d)

    def p(self, x, y):
        return (x * self.k, y * self.k)

    def pts(self, points):
        return [self.p(x, y) for x, y in points]

    def w(self, v):
        return max(1, int(round(v * self.k)))

    def poly(self, points, fill=None, outline=None, width=2, smooth=True, steps=8):
        pts = _catmull(points, True, steps) if smooth else list(points)
        pp = self.pts(pts)
        if fill is not None:
            self._go(lambda d: d.polygon(pp, fill=fill), fill)
        if outline:
            self._go(lambda d: d.line(pp + [pp[0]], fill=outline, width=self.w(width), joint="curve"), outline)

    def ellipse(self, cx, cy, rx, ry, fill=None, outline=None, width=2):
        box = [*self.p(cx - rx, cy - ry), *self.p(cx + rx, cy + ry)]
        self._go(lambda d: d.ellipse(box, fill=fill, outline=outline, width=self.w(width)), fill, outline)

    def line(self, points, fill, width=2, smooth=False):
        pts = self.pts(_catmull(points, False, 8) if smooth else points)
        self._go(lambda d: d.line(pts, fill=fill, width=self.w(width), joint="curve"), fill)

    def rrect(self, x1, y1, x2, y2, r, fill=None, outline=None, width=2):
        box = [*self.p(x1, y1), *self.p(x2, y2)]
        self._go(lambda d: d.rounded_rectangle(box, radius=r * self.k, fill=fill, outline=outline, width=self.w(width)), fill, outline)

    def arc(self, box, start, end, fill, width=2):
        x1, y1, x2, y2 = box
        b = [*self.p(x1, y1), *self.p(x2, y2)]
        self._go(lambda d: d.arc(b, start, end, fill=fill, width=self.w(width)), fill)


def _draw_back_hair(c: _Canvas, sway: float):
    # Rambut belakang panjang jatuh di kedua sisi bahu.
    left = [(92, 170), (70, 250), (62, 340), (74, 430), (112, 462), (140, 400), (132, 300), (128, 200)]
    right = [(308, 170), (330, 250), (338, 340), (326, 430), (288, 462), (260, 400), (268, 300), (272, 200)]
    top = [(96, 150), (112, 80), (160, 46), (200, 40), (240, 46), (288, 80), (304, 150), (296, 240), (104, 240)]
    for shape in (left, right, top):
        c.poly(shape, fill=HAIR, outline=INK, width=2.5)
    c.line([(86, 260), (80, 340), (88, 420)], HAIR_HI, 3, smooth=True)
    c.line([(314, 260), (320, 340), (312, 420)], HAIR_HI, 3, smooth=True)


def _draw_body(c: _Canvas, breathe: float, hands_y: float | None, typing: int):
    b = breathe
    # Hoodie: bahu + badan
    body = [(46, 470), (58, 392 + b), (96, 346 + b), (150, 322 + b), (200, 332 + b), (250, 322 + b), (304, 346 + b), (342, 392 + b), (354, 470)]
    c.poly(body, fill=HOOD, outline=INK, width=3, steps=6)
    # lipatan lengan
    c.line([(96, 360 + b), (80, 420), (84, 470)], HOOD_DK, 4, smooth=True)
    c.line([(304, 360 + b), (320, 420), (316, 470)], HOOD_DK, 4, smooth=True)
    c.line([(110, 352 + b), (130, 392), (126, 440)], HOOD_LT, 3, smooth=True)
    # tudung belakang leher
    c.poly([(128, 318 + b), (160, 296 + b), (240, 296 + b), (272, 318 + b), (250, 352 + b), (150, 352 + b)], fill=HOOD_DK, outline=INK, width=2.5)
    # leher
    c.rrect(176, 276, 224, 338 + b, 14, fill=SKIN, outline=INK, width=2.5)
    c.poly([(176, 316), (224, 316), (224, 338 + b), (176, 338 + b)], fill=SKIN_SH, smooth=False)
    # kerah V + kaos dalam
    c.poly([(150, 330 + b), (176, 318 + b), (200, 366 + b), (224, 318 + b), (250, 330 + b), (236, 400), (164, 400)], fill=SHIRT, outline=INK, width=2.5, smooth=False)
    c.poly([(160, 326 + b), (176, 318 + b), (200, 360 + b), (176, 352 + b)], fill=HOOD, outline=INK, width=2, smooth=False)
    c.poly([(240, 326 + b), (224, 318 + b), (200, 360 + b), (224, 352 + b)], fill=HOOD, outline=INK, width=2, smooth=False)
    # tali hoodie
    c.line([(178, 340 + b), (172, 390), (170, 424)], (214, 224, 244), 3, smooth=True)
    c.line([(222, 340 + b), (230, 392), (232, 428)], (214, 224, 244), 3, smooth=True)
    c.ellipse(170, 427, 3.6, 5, fill=(214, 224, 244), outline=INK, width=1.5)
    c.ellipse(232, 431, 3.6, 5, fill=(214, 224, 244), outline=INK, width=1.5)
    if hands_y is not None:
        _draw_hands(c, hands_y, typing)


def _draw_hands(c: _Canvas, y, typing):
    # Meja + keyboard + tangan bersarung hitam (hanya di mode besar).
    c.rrect(40, y + 22, 360, y + 56, 10, fill=(34, 42, 66), outline=INK, width=2.5)
    c.rrect(72, y + 6, 328, y + 30, 8, fill=(70, 82, 112), outline=INK, width=2.5)
    for i in range(14):
        x = 82 + i * 17.2
        c.rrect(x, y + 11, x + 12, y + 17, 2, fill=(130, 144, 176))
        c.rrect(x + 4, y + 20, x + 16, y + 25, 2, fill=(130, 144, 176))
    for side, cx in ((0, 132), (1, 268)):
        dy = (typing if (typing and ((side + typing) % 2)) else 0) * -3
        c.ellipse(cx, y - 6 + dy, 38, 20, fill=GLOVE, outline=INK, width=2.5)
        for f in range(4):
            fx = cx - 24 + f * 16
            c.rrect(fx, y - 4 + dy + (f % 2) * 2, fx + 10, y + 14 + dy, 5, fill=GLOVE, outline=(70, 76, 104), width=1.5)
        c.line([(cx - 20, y - 14 + dy), (cx + 16, y - 14 + dy)], (60, 68, 100), 2)
        # manset hoodie
        c.rrect(cx - 34, y - 36 + dy, cx + 34, y - 18 + dy, 8, fill=HOOD, outline=INK, width=2.5)


def _eye_region(c: _Canvas, mood: str, blink: bool, look: float):
    """Gambar mata di balik kacamata. look: -1..1 arah pandang horizontal."""
    for cx in (156, 244):
        happy = mood == "happy" and not blink
        if blink or mood == "sleepy":
            c.arc((cx - 24, 196, cx + 24, 226), 200, 340, INK, 4)
            continue
        if mood == "happy":
            c.arc((cx - 22, 196, cx + 22, 236), 205, 335, INK, 5)
            continue
        big = 1.18 if mood == "surprised" else 1.0
        ry = 17 * big
        c.ellipse(cx, 208, 20 * big, ry, fill=(250, 252, 255), outline=INK, width=2)
        ix = cx + look * 5
        iy = 208 + (-5 if mood == "thinking" else 0)
        c.ellipse(ix, iy, 12 * big, 15 * big, fill=IRIS, outline=INK, width=1.5)
        c.ellipse(ix, iy + 1, 6 * big, 8 * big, fill=(8, 14, 40))
        c.ellipse(ix - 4, iy - 5, 4, 4.6, fill=(255, 255, 255))
        c.ellipse(ix + 5, iy + 6, 2.2, 2.2, fill=(170, 230, 255))
        c.line([(cx - 22, 196), (cx - 8, 190), (cx + 12, 190), (cx + 22, 197)], INK, 4, smooth=True)


def _draw_glasses(c: _Canvas, t: float, thinking: bool):
    # Lensa transparan biru (mata terlihat samar), bingkai gelap, pantulan bergerak saat berpikir.
    lens_l = [(118, 196), (130, 184), (176, 182), (192, 192), (192, 220), (176, 234), (134, 236), (118, 224)]
    lens_r = [(208, 192), (224, 182), (270, 184), (282, 196), (282, 224), (266, 236), (224, 234), (208, 220)]
    for lens in (lens_l, lens_r):
        c.poly(lens, fill=(*CYAN_DK, 85), outline=None, smooth=True, steps=6)
    # gradien tipis (bagian bawah lebih gelap)
    for lens in (lens_l, lens_r):
        xs = [p[0] for p in lens]
        c.poly([(min(xs) + 4, 214), (max(xs) - 4, 214), (max(xs) - 6, 232), (min(xs) + 6, 232)], fill=(*CYAN_DK, 70), smooth=False)
    for lens in (lens_l, lens_r):
        c.poly(lens, fill=None, outline=GLASS_FRAME, width=5, smooth=True, steps=6)
    c.line([(192, 200), (200, 196), (208, 200)], GLASS_FRAME, 5, smooth=True)
    # gagang menuju telinga
    c.line([(118, 200), (104, 196), (96, 200)], GLASS_FRAME, 5)
    c.line([(282, 200), (296, 196), (304, 200)], GLASS_FRAME, 5)
    # kilau
    sweep = (math.sin(t * (2.2 if thinking else 0.6)) + 1) / 2
    gx = 124 + sweep * 56
    c.line([(gx, 232), (gx + 14, 186)], (255, 255, 255, 190), 5)
    c.line([(gx + 12, 232), (gx + 20, 210)], (255, 255, 255, 120), 3)
    gx2 = 214 + sweep * 56
    c.line([(gx2, 232), (gx2 + 14, 186)], (255, 255, 255, 190), 5)
    c.line([(gx2 + 12, 232), (gx2 + 20, 210)], (255, 255, 255, 120), 3)


def _draw_mouth(c: _Canvas, mood: str, mouth: int):
    cx, cy = 200, 270
    if mood in ("speaking",) or mouth:
        shapes = {1: (7, 4), 2: (10, 8), 3: (12, 11)}
        rx, ry = shapes.get(mouth or 1, (8, 5))
        c.ellipse(cx, cy + 2, rx, ry, fill=(112, 30, 58), outline=INK, width=2)
        if ry >= 7:
            c.ellipse(cx, cy + ry - 1, rx * 0.6, ry * 0.38, fill=(236, 110, 130))
    elif mood == "surprised":
        c.ellipse(cx, cy + 3, 7, 9, fill=(112, 30, 58), outline=INK, width=2)
    elif mood == "sad":
        c.arc((cx - 12, cy - 2, cx + 12, cy + 16), 200, 340, LIP, 3)
    elif mood == "thinking":
        c.line([(cx - 8, cy + 3), (cx + 6, cy + 1)], LIP, 3)
    elif mood == "sleepy":
        c.line([(cx - 6, cy + 3), (cx + 6, cy + 3)], LIP, 3)
    elif mood == "listening":
        c.arc((cx - 11, cy - 7, cx + 11, cy + 9), 20, 160, LIP, 3)
    else:  # happy
        c.arc((cx - 15, cy - 10, cx + 15, cy + 10), 15, 165, LIP, 3.5)


def _draw_head(c: _Canvas, mood: str, blink: bool, mouth: int, t: float, look: float, glow: float):
    # Telinga
    c.ellipse(108, 226, 9, 15, fill=SKIN, outline=INK, width=2.5)
    c.ellipse(292, 226, 9, 15, fill=SKIN, outline=INK, width=2.5)
    # Wajah (dagu agak runcing ala anime)
    face = [(106, 196), (112, 150), (140, 112), (200, 100), (260, 112), (288, 150), (294, 196), (284, 244), (246, 284), (200, 296), (154, 284), (116, 244)]
    c.poly(face, fill=SKIN, outline=INK, width=3, steps=7)
    # bayangan dagu & leher
    c.poly([(150, 270), (200, 296), (250, 270), (236, 288), (200, 300), (164, 288)], fill=SKIN_SH, smooth=False)
    # pipi merah
    blush_a = 120 if mood in ("happy", "speaking", "surprised") else 70
    for cx in (140, 262):
        c.ellipse(cx, 252, 17, 8, fill=(*BLUSH, blush_a))
    # mata + kacamata
    _eye_region(c, mood, blink, look)
    _draw_glasses(c, t, mood == "thinking")
    # tahi lalat kecil seperti referensi
    c.ellipse(168, 244, 1.8, 1.8, fill=(110, 70, 80))
    # hidung
    c.line([(200, 246), (197, 252), (203, 253)], (214, 160, 150), 2.4, smooth=True)
    _draw_mouth(c, mood, mouth)
    # Poni lurus + belahan
    bangs = [(104, 192), (104, 142), (128, 100), (168, 80), (200, 76), (240, 80), (274, 100), (296, 142), (296, 192),
             (288, 178), (272, 170), (252, 182), (234, 164), (214, 150), (200, 146), (186, 150), (166, 164), (148, 182), (128, 170), (112, 178)]
    c.poly(bangs, fill=HAIR, outline=INK, width=2.5, steps=6)
    c.line([(150, 112), (176, 100), (208, 98)], HAIR_HI, 3, smooth=True)
    c.line([(232, 100), (260, 112), (278, 134)], HAIR_HI, 3, smooth=True)
    # Rambut samping depan menutupi pipi
    c.poly([(98, 170), (116, 150), (126, 200), (122, 270), (110, 330), (94, 340), (88, 260)], fill=HAIR, outline=INK, width=2.5, steps=6)
    c.poly([(302, 170), (284, 150), (274, 200), (278, 270), (290, 330), (306, 340), (312, 260)], fill=HAIR, outline=INK, width=2.5, steps=6)
    # Headphone: band + earcup + cahaya
    c.arc((98, 58, 302, 266), 186, 354, INK, 17)
    c.arc((98, 58, 302, 266), 188, 352, PHONE, 12)
    c.arc((104, 64, 296, 260), 205, 300, PHONE_LT, 3)
    for cx in (96, 304):
        c.rrect(cx - 21, 186, cx + 21, 254, 16, fill=PHONE, outline=INK, width=3)
        c.rrect(cx - 14, 196, cx + 14, 244, 11, fill=PHONE_LT, outline=PHONE_DK, width=2)
        if glow > 0:
            a = int(60 + 150 * glow)
            c.ellipse(cx, 220, 10, 18, fill=(*CYAN, a))
    if glow > 0:
        # gelombang suara di dekat telinga kanan
        for i, r in enumerate((26, 36)):
            c.arc((304 - r, 220 - r, 304 + r, 220 + r), -40, 40, (*CYAN, int(200 * glow) - i * 50), 3)
            c.arc((96 - r, 220 - r, 96 + r, 220 + r), 140, 220, (*CYAN, int(200 * glow) - i * 50), 3)
    # Aksesori kabel headphone
    c.line([(80, 252), (74, 300), (92, 340)], (60, 66, 88), 2.5, smooth=True)


def _draw_thinking_dots(c: _Canvas, t: float):
    c.ellipse(332, 70, 40, 24, fill=(240, 248, 255, 235), outline=INK, width=2.5)
    c.ellipse(292, 112, 6, 5, fill=(240, 248, 255, 235), outline=INK, width=2)
    for i in range(3):
        on = int(t * 2.4) % 3 == i
        c.ellipse(316 + i * 16, 70 - (4 if on else 0), 5.2, 5.2, fill=CYAN_DK if on else (110, 130, 170))


def render_frame(size: int = 150, mood: str = "happy", t: float = 0.0, blink: bool = False,
                 mouth: int = 0, scene: bool = False, typing: int = 0, glow: float = 0.0,
                 look: float = 0.0, bg=None) -> Image.Image:
    """Render satu frame avatar. size = lebar piksel. scene=True memunculkan keyboard & tangan."""
    mood = mood if mood in MOODS else "happy"
    ss = 2  # supersampling
    k = size * ss / VW
    vh = VH + (80 if scene else 0)
    c = _Canvas(k, (VW, vh))
    breathe = math.sin(t * 1.6) * 3.0
    sway = math.sin(t * 1.1) * (2.4 if mood != "sleepy" else 4.5)
    if mood == "listening":
        sway += 3.0
    if mood == "sad":
        sway -= 2.0

    _draw_back_hair(c, sway)
    _draw_body(c, breathe, (VH - 40) if scene else None, typing if mood in ("thinking", "speaking") else 0)

    # Kepala digambar di layer sendiri lalu dirotasi sedikit di sekitar leher
    head = _Canvas(k, (VW, VH))
    _draw_head(head, mood, blink, mouth, t, look, glow)
    pivot = (200 * k, 330 * k)
    rotated = head.img.rotate(sway, resample=Image.BICUBIC, center=pivot)
    # bob vertikal kecil
    dy = int(round(breathe * k * 0.6))
    c.img.alpha_composite(rotated, (0, dy))
    if mood == "thinking":
        _draw_thinking_dots(c, t)

    out = c.img.resize((size, int(vh * size / VW)), Image.LANCZOS)
    if bg is not None:
        base = Image.new("RGBA", out.size, (*bg, 255))
        base.alpha_composite(out)
        out = base
    return out


def frame_png(size: int, mood: str, t: float, blink: bool, mouth: int, scene: bool, typing: int, glow: float, look: float,
              bg=KEY_COLOR) -> bytes:
    img = render_frame(size, mood, t, blink, mouth, scene, typing, glow, look, bg)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG", optimize=False, compress_level=1)
    return buf.getvalue()


@lru_cache(maxsize=420)
def cached_frame_png(size: int, mood: str, phase: int, blink: bool, mouth: int, scene: bool, typing: int, glow_q: int,
                     look_q: int, bg=KEY_COLOR) -> bytes:
    """Versi ber-cache. phase 0..11 (kuantisasi waktu) supaya jumlah frame unik terbatas."""
    t = phase * (2 * math.pi / 12.0)
    return frame_png(size, mood, t, blink, mouth, scene, typing, glow_q / 4.0, (look_q - 1) * 0.8, bg)


class AvatarAnimator:
    """State animasi murni (tanpa tkinter). Panggil tick(dt) lalu next_frame()."""

    def __init__(self):
        self.mood = "happy"
        self.speaking = False
        self.listening = False
        self.thinking = False
        self.phase = 0
        self._tick = 0
        self._blink_left = 0
        self._next_blink = 30
        self._mouth_i = 0
        self.typing = 0

    def effective_mood(self) -> str:
        if self.thinking:
            return "thinking"
        if self.speaking:
            return "speaking"
        if self.listening:
            return "listening"
        return self.mood

    def step(self):
        self._tick += 1
        self.phase = (self._tick // 3) % 12
        if self._blink_left > 0:
            self._blink_left -= 1
        elif self._tick >= self._next_blink:
            self._blink_left = 2
            self._next_blink = self._tick + 28 + (self._tick * 7919) % 40
        if self.speaking:
            self._mouth_i = (self._mouth_i + 1) % 6
            self.mouth = (0, 1, 2, 3, 2, 1)[self._mouth_i]
        else:
            self.mouth = 0
        self.typing = (self._tick // 3) % 2 + 1 if self.thinking or self.speaking else 0
        glow = 0.0
        if self.listening and not self.speaking:
            glow = (math.sin(self._tick / 4.0) + 1) / 2
        self.glow_q = int(round(glow * 4))
        return self.key()

    def key(self, size: int = 150, scene: bool = False):
        look = 1 if not self.thinking else (self._tick // 14) % 3
        return (size, self.effective_mood(), self.phase, self._blink_left > 0, getattr(self, "mouth", 0), scene,
                self.typing, getattr(self, "glow_q", 0), look)


def circular_portrait(path: str, size: int = 96, box=(188, 19, 538, 369)) -> Image.Image:
    """Potongan wajah bundar dari gambar referensi untuk header/ikon."""
    img = Image.open(path).convert("RGB").crop(box).resize((size * 2, size * 2), Image.LANCZOS)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).ellipse([0, 0, img.size[0] - 1, img.size[1] - 1], fill=255)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out.resize((size, size), Image.LANCZOS)


@lru_cache(maxsize=420)
def uploaded_expression_frame_png(size: int, mood: str, phase: int, blink: bool, mouth: int,
                                 scene: bool, typing: int, glow_q: int, look_q: int) -> bytes:
    """Render sprite dari 15 ekspresi gambar pengguna; variasi fase memberi animasi ringan.

    Gambar bukan live facial motion capture: Clara memilih ekspresi yang sesuai status
    (mendengarkan/berpikir/berbicara/emosi) dan mengganti frame saat suara berlangsung.
    """
    from PIL import Image
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    folder = base / "assets" / "expressions"
    mood = (mood or "happy").casefold()
    if mood in ("happy", "greeting", "success", "friendly"):
        cells = [(0, 0), (0, 1), (0, 0), (0, 4)]
    elif mood == "speaking":
        cells = [(0, 0), (0, 1), (2, 3), (0, 1), (0, 0), (1, 3)]
    elif mood in ("listening", "attentive"):
        cells = [(0, 0), (1, 4), (0, 0), (1, 4)]
    elif mood in ("thinking", "curious", "analysing", "analysis"):
        cells = [(2, 2), (0, 4), (1, 0), (2, 2)]
    elif mood in ("sad", "worried", "concerned", "sorry", "empathetic"):
        cells = [(1, 0), (1, 1), (1, 2), (1, 1)]
    elif mood in ("surprised", "confused", "question"):
        cells = [(1, 3), (2, 3), (1, 4), (2, 3)]
    elif mood in ("angry", "warning", "frustrated"):
        cells = [(2, 0), (2, 1), (2, 0), (2, 1)]
    elif mood in ("shy", "embarrassed"):
        cells = [(0, 2), (0, 0), (0, 2)]
    elif mood in ("sleepy", "calm", "neutral"):
        cells = [(0, 4), (0, 0), (0, 4)]
    else:
        cells = [(0, 0), (0, 1)]
    # Fast talking switches among closed and open-mouth expressions; no synthetic face edits.
    idx = (phase // 2) % len(cells) if len(cells) > 1 else 0
    if blink and mood not in ("speaking", "surprised"):
        cell = (0, 4)  # uploaded image with closed eyes / gentle expression
    else:
        cell = cells[idx]
    path = folder / f"expression_{cell[0]}_{cell[1]}.png"
    try:
        with Image.open(path) as src:
            im = src.convert("RGBA")
    except Exception:
        # Fallback to the procedural avatar if the sprite is missing in a custom build.
        return cached_frame_png(size, mood if mood in MOODS else "happy", phase, blink, mouth, scene, typing, glow_q, look_q)
    target_h = max(1, round(im.height * size / im.width))
    im = im.resize((size, target_h), Image.Resampling.LANCZOS)
    # Subtle breathing/bobbing, composited on transparent canvas to keep the pet floating.
    pad = 7 if size <= 180 else 12
    canvas = Image.new("RGBA", (size, target_h + pad * 2), (KEY_COLOR[0], KEY_COLOR[1], KEY_COLOR[2], 0))
    dy = round(math.sin(phase * math.pi / 6.0) * (2 if size <= 180 else 3))
    canvas.alpha_composite(im, (0, pad + dy))
    if scene:
        framed = Image.new("RGBA", (size, canvas.height + max(18, size // 12)), (0, 0, 0, 0))
        framed.alpha_composite(canvas, (0, 0))
        canvas = framed
    buf = io.BytesIO()
    canvas.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


class AvatarRenderer:
    """Render frame di thread latar belakang agar GUI tidak tersendat.

    request(key) -> bytes | None. Jika frame belum siap, kembalikan None dan GUI
    cukup mempertahankan gambar sebelumnya."""

    def __init__(self):
        import queue
        import threading
        self._cache = {}
        self._q = queue.Queue(maxsize=8)
        self._pending = set()
        self._lock = threading.Lock()
        self._t = threading.Thread(target=self._run, daemon=True, name="ClaraAvatarRender")
        self._t.start()

    def _run(self):
        while True:
            key = self._q.get()
            try:
                size, mood, phase, blink, mouth, scene, typing, glow_q, look = key
                # Utamakan sprite sheet karakter yang dikirim pengguna; fallback procedural.
                data = uploaded_expression_frame_png(size, mood, phase, blink, mouth, scene, typing, glow_q, look)
                with self._lock:
                    self._cache[key] = data
                    if len(self._cache) > 300:
                        self._cache.pop(next(iter(self._cache)))
            except Exception:
                pass
            finally:
                with self._lock:
                    self._pending.discard(key)

    def request(self, key):
        with self._lock:
            data = self._cache.get(key)
            if data is not None:
                return data
            if key not in self._pending:
                try:
                    self._q.put_nowait(key)
                    self._pending.add(key)
                except Exception:
                    pass
        return None
