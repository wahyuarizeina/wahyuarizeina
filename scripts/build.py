#!/usr/bin/env python3
"""Generator aset SVG untuk README profil.

Jalankan dari root repo:  python3 scripts/build.py
Butuh: pip install fonttools brotli

Semua teks memakai font yang di-embed (subset, base64) supaya tampilannya sama
di browser mana pun — SVG yang dimuat lewat <img> di GitHub tidak bisa memuat
font eksternal. Ubah konten di bagian DATA di bawah, lalu jalankan ulang.
"""
import base64
import io
import math
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "scripts" / "fonts"
OUT = ROOT / "assets"

# ───────────────────────────── palet ─────────────────────────────
INK = "#0e0e10"
MUTED = "#4a4a55"
PAPER = "#fffdf5"
CREAM = "#fff3c4"
YELLOW = "#ffd43b"
BLUE = "#74c0fc"
COBALT = "#4c6ef5"
MINT = "#8ce99a"
PINK = "#ff8fab"
PURPLE = "#b197fc"
ORANGE = "#ffa94d"
TEAL = "#38d9a9"
WHITE = "#ffffff"

# ───────────────────────────── DATA ─────────────────────────────
NAME = "Wahyu"
FULL_NAME = "Wahyu Surya"
HANDLE = "@wahyuarizeina"
ROLES = ["Game Developer", "Technical Designer @ RIVRS", "AI & Data Analyst", "Full-Stack Web Developer"]
TAGLINE = [
    "Membangun game, mengolah data jadi insight, dan",
    "merakit produk web yang benar-benar dipakai orang.",
]
HERO_CHIPS = [("Game Dev", PINK), ("Data & AI", BLUE), ("Full-Stack Web", MINT)]
RING_TEXT = "GAME  •  DATA  •  AI  •  WEB  •  DESIGN  •  "

MARQUEE = ["GAME DEVELOPMENT", "TECHNICAL DESIGN", "DATA ANALYSIS", "MACHINE LEARNING", "NEXT.JS",
           "SUPABASE", "TYPESCRIPT", "PYTHON", "POSTGRESQL", "AUTOMATION"]

SECTIONS = {
    "about": ("01", "Tentang Aku", YELLOW),
    "projects": ("02", "Proyek Pilihan", BLUE),
    "toolkit": ("03", "Toolkit", PINK),
    "activity": ("04", "Jejak Kontribusi", PURPLE),
}

PROJECTS = [
    dict(slug="tofav", title="Tofav Game", label="GAME STORE · 2026", color=MINT, art="game",
         status="LIVE",
         desc=["Storefront top-up game: order 6 langkah, validasi", "Gamepass Roblox, chat bot Minfav & dasbor admin."],
         tags=["Next.js 16", "Supabase", "Tailwind v4", "iPaymu"]),
    dict(slug="pemilu", title="Pemilu 2024 Analytics", label="DATA & AI · 2024", color=BLUE, art="chart",
         status="OPEN SOURCE",
         desc=["Analisis elektoral end-to-end: EDA, segmentasi", "K-Means, model prediktif & simulasi kursi DPR."],
         tags=["Python", "scikit-learn", "Jupyter", "Next.js"]),
    dict(slug="kitapunya", title="Kita Punya Project", label="SAAS · 2026", color=YELLOW, art="browser",
         status="LIVE",
         desc=["Layanan manajemen website untuk UMKM: portal", "klien, invoice PDF & pengingat otomatis."],
         tags=["Next.js", "Supabase", "Resend", "Playwright"]),
    dict(slug="markalani", title="Markalani Music", label="MUSIK · 2026", color=PINK, art="music",
         status="LIVE",
         desc=["Situs label musik: profil artis, galeri foto", "& video, dikelola lewat panel admin."],
         tags=["Next.js 16", "React 19", "Supabase", "Tailwind"]),
]

TOOLKIT = [
    ("Data & AI", "olah · modelkan · ceritakan", BLUE,
     ["Python", "pandas", "NumPy", "scikit-learn", "Matplotlib", "Seaborn", "Jupyter", "Google Colab"]),
    ("Frontend", "cepat · rapi · aksesibel", PINK,
     ["Next.js", "React", "TypeScript", "Tailwind CSS", "Framer Motion", "Radix UI"]),
    ("Backend", "aman dari database ke atas", MINT,
     ["Supabase", "PostgreSQL", "Row Level Security", "Auth", "Resend", "iPaymu", "Turnstile"]),
    ("Kualitas & Rilis", "uji dulu, baru kirim", YELLOW,
     ["Playwright", "Vitest", "GitHub Actions", "Vercel", "Hostinger", "Git", "Claude Code"]),
]

FOOTER_TITLE = "Makasih udah mampir!"
FOOTER_SUB = ["Punya ide game, data yang perlu diceritakan, atau", "web yang mau dibangun? Ayo ngobrol."]

# ───────────────────────────── font ─────────────────────────────
FACES = {"display": "brico800", "sans": "work500", "bold": "work700", "mono": "mono400", "monob": "mono500"}


class Font:
    def __init__(self, key):
        self.key = key
        self.path = FONT_DIR / f"{FACES[key]}.woff"
        tt = TTFont(self.path)
        self.upm = tt["head"].unitsPerEm
        self.cmap = tt.getBestCmap()
        self.hmtx = tt["hmtx"]

    def width(self, text, size, ls=0.0):
        adv = 0
        for ch in text:
            g = self.cmap.get(ord(ch))
            if g is None:
                raise ValueError(f"Glyph {ch!r} tidak ada di font {self.key}")
            adv += self.hmtx[g][0]
        return adv * size / self.upm + ls * len(text)


FONTS = {k: Font(k) for k in FACES}


def tw(text, font, size, ls=0.0):
    return FONTS[font].width(text, size, ls)


def font_face(key, chars):
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga", "calt"]
    opts.name_IDs = ["*"]
    tt = TTFont(FONTS[key].path)
    s = subset.Subsetter(opts)
    s.populate(text="".join(sorted(chars)))
    s.subset(tt)
    tt.flavor = "woff2"
    buf = io.BytesIO()
    tt.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"@font-face{{font-family:'{key}';src:url(data:font/woff2;base64,{b64}) format('woff2');}}"


# ───────────────────────────── SVG ─────────────────────────────
class Svg:
    def __init__(self, w, h, title, desc=""):
        self.w, self.h, self.title, self.desc = w, h, title, desc
        self.parts, self.css, self.defs = [], [], []
        self.used = {k: set() for k in FACES}

    def add(self, *s):
        self.parts.extend(s)

    def text(self, x, y, s, font="sans", size=16, fill=INK, anchor="start", ls=0, cls="", extra=""):
        FONTS[font].width(s, size)  # validasi glyph
        self.used[font].update(s)
        c = f' class="{cls}"' if cls else ""
        l = f' letter-spacing="{ls}"' if ls else ""
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" fill="{fill}"'
                f'{a}{l}{c} {extra}>{escape(s)}</text>')

    def render(self, path):
        faces = "".join(font_face(k, v) for k, v in self.used.items() if v)
        css = faces + "".join(self.css)
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        d = f"<desc>{escape(self.desc)}</desc>" if self.desc else ""
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
               f'viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{escape(self.title)}">'
               f"<title>{escape(self.title)}</title>{d}<style>{css}</style>{defs}{''.join(self.parts)}</svg>")
        path.write_text(svg, encoding="utf-8")
        print(f"  {path.relative_to(ROOT)}  {len(svg) / 1024:.1f} KB")


def box(x, y, w, h, fill, r=16, shadow=6, stroke=3, extra=""):
    sh = f'<rect x="{x + shadow}" y="{y + shadow}" width="{w}" height="{h}" rx="{r}" fill="{INK}"/>' if shadow else ""
    return sh + (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" '
                 f'stroke="{INK}" stroke-width="{stroke}" {extra}/>')


def chip(svg, x, y, label, fill, font="bold", size=16, padx=16, h=36, shadow=3, stroke=2.5):
    w = tw(label, font, size) + padx * 2
    out = box(x, y, w, h, fill, r=h / 2, shadow=shadow, stroke=stroke)
    out += svg.text(x + w / 2, y + h / 2 + size * 0.36, label, font, size, anchor="middle")
    return out, w


def sparkle(cx, cy, r, fill, cls=""):
    k = r * 0.28
    d = (f"M{cx},{cy - r} C{cx + k * 0.4},{cy - k} {cx + k},{cy - k * 0.4} {cx + r},{cy} "
         f"C{cx + k},{cy + k * 0.4} {cx + k * 0.4},{cy + k} {cx},{cy + r} "
         f"C{cx - k * 0.4},{cy + k} {cx - k},{cy + k * 0.4} {cx - r},{cy} "
         f"C{cx - k},{cy - k * 0.4} {cx - k * 0.4},{cy - k} {cx},{cy - r}Z")
    c = f' class="{cls}"' if cls else ""
    return (f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"{c} '
            f'style="transform-origin:{cx}px {cy}px"/>')


def arrow_ne(x, y, s=12, color=INK, sw=2.6):
    return (f'<path d="M{x},{y + s} L{x + s},{y} M{x + s * 0.3},{y} L{x + s},{y} L{x + s},{y + s * 0.7}" '
            f'fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')


def lock(x, y, color=INK):
    return (f'<rect x="{x}" y="{y + 6}" width="12" height="9" rx="2" fill="{color}"/>'
            f'<path d="M{x + 2.5},{y + 6.5} V{y + 3.5} a3.5,3.5 0 0 1 7,0 V{y + 6.5}" fill="none" '
            f'stroke="{color}" stroke-width="2.2"/>')


def dots_pattern(pid, color=INK, gap=22, r=1.5, op=0.16):
    return (f'<pattern id="{pid}" width="{gap}" height="{gap}" patternUnits="userSpaceOnUse">'
            f'<circle cx="{gap / 2}" cy="{gap / 2}" r="{r}" fill="{color}" fill-opacity="{op}"/></pattern>')


ANIM_CSS = """
.float{animation:float 4s ease-in-out infinite}
.float2{animation:float 5s ease-in-out -2s infinite}
.twinkle{animation:twinkle 2.6s ease-in-out infinite}
.twinkle2{animation:twinkle 3.2s ease-in-out -1.2s infinite}
.spin{animation:spin 26s linear infinite}
.blink{animation:blink 1s steps(1) infinite}
.pulse{animation:pulse 1.8s ease-in-out infinite}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes twinkle{0%,100%{transform:scale(1) rotate(0deg)}50%{transform:scale(.72) rotate(20deg)}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes blink{50%{opacity:0}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


# ───────────────────────────── header ─────────────────────────────
def build_header():
    W, H = 1200, 500
    s = Svg(W, H, f"Hai, aku {NAME} — {', '.join(ROLES[:2])}", " · ".join(TAGLINE))
    s.css.append(ANIM_CSS)
    s.defs.append(dots_pattern("dots"))
    s.add(f'<rect width="{W}" height="{H}" fill="{CREAM}"/><rect width="{W}" height="{H}" fill="url(#dots)"/>')

    cx0, cy0, cw, ch = 34, 32, 1128, 428
    s.add(box(cx0, cy0, cw, ch, PAPER, r=24, shadow=9, stroke=3.5))
    # window bar
    s.add(f'<path d="M{cx0},{cy0 + 54} H{cx0 + cw}" stroke="{INK}" stroke-width="3"/>')
    for i, col in enumerate([PINK, YELLOW, MINT]):
        s.add(f'<circle cx="{cx0 + 32 + i * 26}" cy="{cy0 + 27}" r="8" fill="{col}" stroke="{INK}" stroke-width="2.5"/>')
    s.add(s.text(W / 2, cy0 + 33, f"github.com/{HANDLE[1:]}  —  README.md", "mono", 15, MUTED, anchor="middle"))
    s.add(f'<circle cx="{cx0 + cw - 118}" cy="{cy0 + 27}" r="5" fill="#2fb344" class="pulse"/>')
    s.add(s.text(cx0 + cw - 106, cy0 + 32, "online", "mono", 14, MUTED))

    x = 84
    s.add(s.text(x, 150, "HALO, SALAM KENAL —", "monob", 16, MUTED, ls=2.5))
    # headline + highlight
    pre = "Hai, aku "
    size = 84
    wpre = tw(pre, "display", size, -2)
    wname = tw(NAME, "display", size, -2)
    hx, hy, pad = x + wpre + 6, 166, 14
    s.add(f'<g transform="rotate(-2.5 {hx + wname / 2} {hy + 40})">'
          + box(hx, hy, wname + pad * 2, 78, YELLOW, r=12, shadow=5) + "</g>")
    s.add(s.text(x, 232, pre.strip(), "display", size, INK, ls=-2))
    s.add(s.text(hx + pad, 232, NAME, "display", size, INK, ls=-2))
    sx = hx + wname + pad * 2 + 14
    s.add(sparkle(sx, 160, 16, PINK, "twinkle"))

    # rotating roles
    n = len(ROLES)
    period = 3.2 * n
    s.css.append(
        f".role{{opacity:0;animation:role {period}s ease-in-out infinite}}"
        f".role0{{opacity:1}}"
        f"@keyframes role{{0%{{opacity:0;transform:translateY(16px)}}"
        f"{100 / n * 0.12:.2f}%{{opacity:1;transform:translateY(0)}}"
        f"{100 / n * 0.88:.2f}%{{opacity:1;transform:translateY(0)}}"
        f"{100 / n:.2f}%{{opacity:0;transform:translateY(-16px)}}100%{{opacity:0}}}}"
    )
    s.add(s.text(x, 292, ">", "monob", 30, COBALT))
    for i, role in enumerate(ROLES):
        rx = x + 30
        w = tw(role, "display", 36, -0.5)
        s.add(f'<g class="role role{i}" style="animation-delay:{i * period / n:.2f}s">'
              + s.text(rx, 292, role, "display", 36, INK, ls=-0.5)
              + f'<rect x="{rx + w + 8:.1f}" y="262" width="4" height="36" fill="{COBALT}" class="blink"/></g>')

    for i, line in enumerate(TAGLINE):
        s.add(s.text(x, 340 + i * 28, line, "sans", 21, MUTED))

    cxp = x
    for label, col in HERO_CHIPS:
        c, w = chip(s, cxp, 392, label, col, size=16)
        s.add(c)
        cxp += w + 14

    # right composition: rotating ring + chart badge
    rcx, rcy, R = 958, 268, 128
    s.add(f'<circle cx="{rcx + 8}" cy="{rcy + 8}" r="{R}" fill="{INK}"/>')
    s.add(f'<circle cx="{rcx}" cy="{rcy}" r="{R}" fill="{BLUE}" stroke="{INK}" stroke-width="3.5"/>')
    s.add(f'<circle cx="{rcx}" cy="{rcy}" r="{R - 44}" fill="{PAPER}" stroke="{INK}" stroke-width="3"/>')
    tr = R - 24
    s.defs.append(f'<path id="ring" d="M{rcx},{rcy} m-{tr},0 a{tr},{tr} 0 1,1 {tr * 2},0 a{tr},{tr} 0 1,1 -{tr * 2},0"/>')
    circ = 2 * math.pi * tr
    s.used["monob"].update(RING_TEXT)
    FONTS["monob"].width(RING_TEXT, 17)
    s.add(f'<g class="spin" style="transform-origin:{rcx}px {rcy}px">'
          f'<text font-family="monob" font-size="17" fill="{INK}" dy="6">'
          f'<textPath href="#ring" textLength="{circ - 4:.1f}" lengthAdjust="spacing">{escape(RING_TEXT)}</textPath></text></g>')
    # mini chart inside
    bw, base = 16, rcy + 34
    bars = [(26, PINK), (40, YELLOW), (34, MINT), (58, COBALT)]
    bx0 = rcx - (len(bars) * bw + (len(bars) - 1) * 8) / 2
    pts = []
    for i, (bh, col) in enumerate(bars):
        bx = bx0 + i * (bw + 8)
        s.add(f'<rect x="{bx:.1f}" y="{base - bh}" width="{bw}" height="{bh}" rx="3" fill="{col}" stroke="{INK}" stroke-width="2.5"/>')
        pts.append((bx + bw / 2, base - bh - 12))
    s.add(f'<path d="M{pts[0][0]:.1f},{pts[0][1]} ' + " ".join(f"L{px:.1f},{py}" for px, py in pts[1:])
          + f'" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    for px, py in pts:
        s.add(f'<circle cx="{px:.1f}" cy="{py}" r="4.5" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
    s.add(f'<path d="M{rcx - 46},{base + 3} H{rcx + 46}" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')

    s.add(sparkle(812, 128, 20, YELLOW, "twinkle"))
    s.add(sparkle(1112, 140, 13, PURPLE, "twinkle2"))
    s.add(sparkle(1118, 420, 17, MINT, "twinkle"))
    # tilted handle sticker
    st = f'<g class="float"><g transform="rotate(-7 842 418)">'
    hw = tw(HANDLE, "monob", 16) + 30
    st += box(842 - hw / 2, 398, hw, 40, PINK, r=10, shadow=4)
    st += s.text(842, 424, HANDLE, "monob", 16, INK, anchor="middle")
    st += "</g></g>"
    s.add(st)
    s.render(OUT / "header.svg")


# ───────────────────────────── marquee ─────────────────────────────
def build_marquee():
    W, H = 1200, 64
    s = Svg(W, H, " · ".join(MARQUEE))
    size, gap = 24, 30
    items, x = [], 0
    for word in MARQUEE:
        w = tw(word, "display", size)
        items.append((x, word))
        x += w + gap + 18 + gap
    seq = x
    s.css.append(f".track{{animation:slide {seq / 70:.1f}s linear infinite}}"
                 f"@keyframes slide{{to{{transform:translateX(-{seq:.1f}px)}}}}"
                 "@media (prefers-reduced-motion:reduce){.track{animation:none}}")
    s.add(f'<rect width="{W}" height="{H}" fill="{INK}"/>')
    s.add(f'<rect x="0" y="5" width="{W}" height="{H - 10}" fill="{YELLOW}"/>')
    track = '<g class="track">'
    reps = math.ceil((W + seq) / seq)
    for r in range(reps):
        for ix, word in items:
            px = ix + r * seq + 20
            track += s.text(px, H / 2 + 9, word, "display", size, INK)
            star_x = px + tw(word, "display", size) + gap + 9
            track += sparkle(star_x, H / 2, 10, PAPER)
    track += "</g>"
    s.add(track)
    s.render(OUT / "marquee.svg")


# ───────────────────────────── section headers ─────────────────────────────
def build_sections():
    for key, (num, title, color) in SECTIONS.items():
        size = 34
        twid = tw(title, "display", size, -0.5)
        bw = 16 + 46 + 16 + twid + 26
        W, H = int(bw + 60), 80
        s = Svg(W, H, f"{num} — {title}")
        s.css.append(ANIM_CSS)
        s.add(box(4, 8, bw, 60, color, r=14, shadow=6))
        s.add(f'<circle cx="{4 + 16 + 23}" cy="38" r="22" fill="{INK}"/>')
        s.add(s.text(4 + 16 + 23, 44.5, num, "monob", 17, WHITE, anchor="middle"))
        s.add(s.text(4 + 16 + 46 + 16, 50, title, "display", size, INK, ls=-0.5))
        s.add(sparkle(bw + 34, 26, 13, WHITE, "twinkle"))
        s.render(OUT / f"section-{key}.svg")


# ───────────────────────────── project cards ─────────────────────────────
def art(kind, x, y, color):
    """Ilustrasi kecil di area cover kartu (kotak ~170x86 mulai x,y)."""
    st = f'stroke="{INK}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"'
    if kind == "chart":
        o = f'<rect x="{x}" y="{y}" width="170" height="86" rx="10" fill="{PAPER}" {st}/>'
        for i, h in enumerate([22, 38, 30, 52, 44]):
            o += f'<rect x="{x + 18 + i * 28}" y="{y + 74 - h}" width="18" height="{h}" rx="3" fill="{[PINK, YELLOW, MINT, COBALT, PURPLE][i]}" {st}/>'
        return o
    if kind == "game":
        o = f'<path d="M{x + 30},{y + 26} H{x + 140} a30,30 0 0 1 22,50 l-6,6 a16,16 0 0 1 -26,-4 l-8,-12 H{x + 58} l-8,12 a16,16 0 0 1 -26,4 l-6,-6 a30,30 0 0 1 22,-50Z" fill="{PAPER}" {st}/>'
        o += f'<path d="M{x + 44},{y + 44} v20 M{x + 34},{y + 54} h20" {st} fill="none"/>'
        o += f'<circle cx="{x + 122}" cy="{y + 46}" r="7" fill="{PINK}" {st}/><circle cx="{x + 138}" cy="{y + 60}" r="7" fill="{YELLOW}" {st}/>'
        o += f'<circle cx="{x + 152}" cy="{y + 10}" r="10" fill="{YELLOW}" {st}/>'
        return o
    if kind == "browser":
        o = f'<rect x="{x}" y="{y}" width="170" height="86" rx="10" fill="{PAPER}" {st}/>'
        o += f'<path d="M{x},{y + 22} H{x + 170}" {st}/>'
        for i, c in enumerate([PINK, YELLOW, MINT]):
            o += f'<circle cx="{x + 14 + i * 14}" cy="{y + 11}" r="4" fill="{c}" stroke="{INK}" stroke-width="2"/>'
        o += f'<rect x="{x + 14}" y="{y + 34}" width="60" height="38" rx="5" fill="{BLUE}" {st}/>'
        for i in range(3):
            o += f'<path d="M{x + 88},{y + 40 + i * 13} H{x + 156 - i * 18}" {st}/>'
        return o
    if kind == "mountain":
        o = f'<path d="M{x},{y + 86} L{x + 58},{y + 16} L{x + 92},{y + 56} L{x + 116},{y + 32} L{x + 170},{y + 86}Z" fill="{PAPER}" {st}/>'
        o += f'<path d="M{x + 42},{y + 36} L{x + 58},{y + 16} L{x + 74},{y + 36} L{x + 64},{y + 32} L{x + 58},{y + 40} L{x + 50},{y + 32}Z" fill="{WHITE}" {st}/>'
        o += f'<path d="M{x + 116},{y + 32} V{y + 2}" {st}/><path d="M{x + 116},{y + 2} L{x + 140},{y + 9} L{x + 116},{y + 16}Z" fill="{PINK}" {st}/>'
        o += f'<circle cx="{x + 18}" cy="{y + 18}" r="11" fill="{YELLOW}" {st}/>'
        return o
    if kind == "music":
        cx, cy = x + 60, y + 44
        o = f'<g class="spin" style="transform-origin:{cx}px {cy}px;animation-duration:8s"><circle cx="{cx}" cy="{cy}" r="42" fill="{INK}"/>'
        o += f'<circle cx="{cx}" cy="{cy}" r="30" fill="none" stroke="#3a3a42" stroke-width="2"/><circle cx="{cx}" cy="{cy}" r="14" fill="{YELLOW}" stroke="{INK}" stroke-width="2"/>'
        o += f'<rect x="{cx - 2}" y="{cy - 38}" width="4" height="10" rx="2" fill="#55555f"/></g>'
        o += f'<path d="M{x + 128},{y + 70} V{y + 14} L{x + 160},{y + 6} V{y + 60}" fill="none" {st}/>'
        o += f'<ellipse cx="{x + 120}" cy="{y + 72}" rx="10" ry="8" fill="{PAPER}" {st}/><ellipse cx="{x + 152}" cy="{y + 62}" rx="10" ry="8" fill="{PAPER}" {st}/>'
        return o
    if kind == "flower":
        cx, cy = x + 120, y + 44
        o = f'<g class="spin" style="transform-origin:{cx}px {cy}px;animation-duration:30s">'
        for i in range(8):
            o += f'<ellipse cx="{cx}" cy="{cy - 24}" rx="13" ry="22" fill="{PINK}" {st} transform="rotate({i * 45} {cx} {cy})"/>'
        o += f'</g><circle cx="{cx}" cy="{cy}" r="14" fill="{YELLOW}" {st}/>'
        o += f'<rect x="{x}" y="{y + 22}" width="58" height="58" rx="8" fill="{PAPER}" {st} transform="rotate(-8 {x + 29} {y + 51})"/>'
        o += f'<path d="M{x + 12},{y + 40} h30 M{x + 12},{y + 54} h22" {st} transform="rotate(-8 {x + 29} {y + 51})"/>'
        return o
    return ""


STATUS_STYLE = {"LIVE": (WHITE, "dot"), "OPEN SOURCE": (WHITE, "arrow"), "DIKERJAKAN": (WHITE, "pulse"),
                "PRIVATE": (WHITE, "lock")}


def build_projects():
    for p in PROJECTS:
        W, H = 600, 330
        s = Svg(W, H, f"{p['title']} — {' '.join(p['desc'])}")
        s.css.append(ANIM_CSS)
        x0, y0, cw, ch = 8, 8, 576, 306
        s.defs.append(dots_pattern("d", gap=18, op=0.22))
        s.defs.append(f'<clipPath id="top"><rect x="{x0}" y="{y0}" width="{cw}" height="{ch}" rx="18"/></clipPath>')
        s.add(box(x0, y0, cw, ch, PAPER, r=18, shadow=8, stroke=3))
        s.add(f'<g clip-path="url(#top)"><rect x="{x0}" y="{y0}" width="{cw}" height="118" fill="{p["color"]}"/>'
              f'<rect x="{x0}" y="{y0}" width="{cw}" height="118" fill="url(#d)"/></g>')
        s.add(f'<path d="M{x0},{y0 + 118} H{x0 + cw}" stroke="{INK}" stroke-width="3"/>')
        # label chip
        c, _ = chip(s, 30, 28, p["label"], PAPER, font="monob", size=13, padx=12, h=30, shadow=0, stroke=2.5)
        s.add(c)
        # status chip
        status = p["status"]
        stw = tw(status, "monob", 13) + 24 + 18
        sx = 30
        sy = 70
        s.add(box(sx, sy, stw, 30, INK, r=15, shadow=0, stroke=2.5))
        icon = STATUS_STYLE[status][1]
        if icon == "dot":
            s.add(f'<circle cx="{sx + 16}" cy="{sy + 15}" r="5" fill="#40c057" class="pulse"/>')
        elif icon == "pulse":
            s.add(f'<circle cx="{sx + 16}" cy="{sy + 15}" r="5" fill="{YELLOW}" class="pulse"/>')
        elif icon == "arrow":
            s.add(arrow_ne(sx + 10, sy + 9, 11, WHITE, 2.4))
        elif icon == "lock":
            s.add(lock(sx + 10, sy + 6, WHITE))
        s.add(s.text(sx + 30, sy + 20, status, "monob", 13, WHITE))
        s.add(art(p["art"], 384, 22, p["color"]))
        # body
        s.add(s.text(32, 170, p["title"], "display", 32, INK, ls=-0.6))
        assert tw(p["title"], "display", 32, -0.6) < 530, f"judul terlalu panjang: {p['title']!r}"
        for i, line in enumerate(p["desc"]):
            assert tw(line, "sans", 17) < 530, f"deskripsi terlalu panjang: {line!r}"
            s.add(s.text(32, 202 + i * 24, line, "sans", 17, MUTED))
        tx = 32
        for t in p["tags"]:
            c, w = chip(s, tx, 258, t, WHITE, font="monob", size=13, padx=11, h=30, shadow=2, stroke=2.2)
            s.add(c)
            tx += w + 10
        assert tx < x0 + cw - 70, f"tag terlalu banyak/panjang di {p['slug']}"
        # arrow button
        s.add(f'<circle cx="{x0 + cw - 40}" cy="{273}" r="20" fill="{p["color"]}" stroke="{INK}" stroke-width="2.5"/>')
        s.add(arrow_ne(x0 + cw - 47, 266, 14))
        s.render(OUT / f"project-{p['slug']}.svg")


# ───────────────────────────── toolkit ─────────────────────────────
def build_toolkit():
    W = 1200
    colw, gap = 568, 28
    x_cols = [(W - (2 * colw + gap)) / 2 - 4, (W - (2 * colw + gap)) / 2 - 4 + colw + gap]
    layouts = []
    for title, sub, col, items in TOOLKIT:
        rows, row, rw = [], [], 0
        for it in items:
            w = tw(it, "bold", 16) + 28
            if row and rw + w > colw - 52:
                rows.append(row)
                row, rw = [], 0
            row.append((it, w))
            rw += w + 12
        rows.append(row)
        layouts.append((title, sub, col, rows))
    row_heights = []
    for r in range(0, len(layouts), 2):
        hs = [96 + len(l[3]) * 50 + 14 for l in layouts[r:r + 2]]
        row_heights.append(max(hs))
    H = int(sum(row_heights) + 34 * (len(row_heights) - 1) + 30)
    s = Svg(W, H, "Toolkit: " + "; ".join(f"{t}: {', '.join(i)}" for t, _, _, i in TOOLKIT))
    s.css.append(ANIM_CSS)
    y = 8
    for r, rh in enumerate(row_heights):
        for c, (title, sub, col, rows) in enumerate(layouts[r * 2:r * 2 + 2]):
            x = x_cols[c]
            s.add(box(x, y, colw, rh, PAPER, r=18, shadow=7))
            s.add(f'<circle cx="{x + 38}" cy="{y + 44}" r="16" fill="{col}" stroke="{INK}" stroke-width="3"/>')
            s.add(s.text(x + 66, y + 53, title, "display", 28, INK, ls=-0.5))
            s.add(s.text(x + colw - 24, y + 51, sub, "mono", 14, MUTED, anchor="end"))
            s.add(f'<path d="M{x + 24},{y + 76} H{x + colw - 24}" stroke="{INK}" stroke-width="2" stroke-dasharray="2 6" stroke-linecap="round"/>')
            cy = y + 96
            for row in rows:
                cx = x + 26
                for it, w in row:
                    ch, _ = chip(s, cx, cy, it, col, size=16, padx=14, h=36, shadow=3)
                    s.add(ch)
                    cx += w + 12
                cy += 50
        y += rh + 34
    s.render(OUT / "toolkit.svg")


# ───────────────────────────── footer ─────────────────────────────
def build_footer():
    W, H = 1200, 270
    s = Svg(W, H, FOOTER_TITLE + " " + " ".join(FOOTER_SUB))
    s.css.append(ANIM_CSS)
    s.defs.append(dots_pattern("fd", gap=20, op=0.18))
    s.add(box(30, 20, 1132, 214, COBALT, r=24, shadow=9, stroke=3.5))
    s.defs.append('<clipPath id="fc"><rect x="30" y="20" width="1132" height="214" rx="24"/></clipPath>')
    s.add('<rect x="30" y="20" width="1132" height="214" fill="url(#fd)" clip-path="url(#fc)"/>')
    s.add(s.text(84, 112, FOOTER_TITLE, "display", 58, WHITE, ls=-1.5))
    for i, line in enumerate(FOOTER_SUB):
        s.add(s.text(86, 156 + i * 30, line, "sans", 22, "#e7ebff"))
    # stacked stickers
    cx, cy = 980, 128
    s.add(f'<g class="float"><g transform="rotate(8 {cx} {cy})">'
          + box(cx - 92, cy - 62, 184, 124, YELLOW, r=16, shadow=6)
          + s.text(cx, cy - 12, "LET'S", "display", 36, INK, anchor="middle")
          + s.text(cx, cy + 30, "BUILD", "display", 36, INK, anchor="middle")
          + "</g></g>")
    s.add(sparkle(860, 60, 18, PINK, "twinkle"))
    s.add(sparkle(1112, 206, 14, MINT, "twinkle2"))
    s.add(sparkle(1120, 56, 11, WHITE, "twinkle"))
    s.render(OUT / "footer.svg")


# ───────────────────────────── placeholder snake ─────────────────────────────
def build_snake_placeholder():
    # Ditimpa oleh workflow .github/workflows/snake.yml setelah berjalan pertama kali.
    for mode, bg, fg in [("light", PAPER, INK), ("dark", "#0d1117", "#e6edf3")]:
        path = OUT / f"snake-{mode}.svg"
        if path.exists():
            continue
        s = Svg(880, 192, "Animasi kontribusi sedang disiapkan")
        s.add(f'<rect width="880" height="192" rx="16" fill="{bg}"/>')
        for wk in range(52):
            for d in range(7):
                op = 0.12 + ((wk * 7 + d) * 37 % 100) / 100 * 0.5
                s.add(f'<rect x="{24 + wk * 16}" y="{24 + d * 16}" width="12" height="12" rx="3" fill="{COBALT}" fill-opacity="{op:.2f}"/>')
        s.add(s.text(440, 172, "animasi kontribusi sedang disiapkan…", "mono", 15, fg, anchor="middle"))
        s.render(path)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    print("Membangun aset:")
    build_header()
    build_marquee()
    build_sections()
    build_projects()
    build_toolkit()
    build_footer()
    build_snake_placeholder()
