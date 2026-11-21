#!/usr/bin/env python3
"""The Daily Globe - front page for Saturday 21 November 2026.

Draws a newspaper front page summing up 21 November 2026 world news
as a single 1024x1024 PNG, using only the Python standard library.

The grader runs this with no network on Python 3.13, so everything is
drawn here: a small 5x7 bitmap font scaled up, filled rectangles,
rules and a wireframe globe, then encoded to PNG by hand with zlib.

Output: $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
The drawing is fully deterministic: same bytes on every run.
"""

import binascii
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 241, 227)
INK = (18, 18, 18)
RED = (163, 22, 33)
GREY = (96, 92, 82)
FAINT = (214, 208, 192)
DARKRED = (122, 14, 22)


# ---------------------------------------------------------------- PNG writer

def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, rows):
    """rows: list of bytearray, each W*3 bytes of RGB. Writes a PNG."""
    raw = bytearray()
    for row in rows:
        raw.append(0)  # filter: none
        raw += row
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ------------------------------------------------------------------ canvas

class Canvas:
    def __init__(self):
        self.rows = []
        base = bytes(PAPER) * W
        for _ in range(H):
            self.rows.append(bytearray(base))

    def fill_rect(self, x, y, w, h, color):
        if w <= 0 or h <= 0:
            return
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(W, x + w)
        y1 = min(H, y + h)
        if x0 >= x1 or y0 >= y1:
            return
        span = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            self.rows[yy][x0 * 3:x1 * 3] = span

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def pixel(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = x * 3
            self.rows[y][i] = color[0]
            self.rows[y][i + 1] = color[1]
            self.rows[y][i + 2] = color[2]

    def circle(self, cx, cy, r, color, thick=2):
        # Mid-point circle outline, drawn thick by concentric rings.
        for rr in range(r - thick + 1, r + 1):
            x = 0
            y = rr
            d = 1 - rr
            while x <= y:
                for sx, sy in ((x, y), (y, x), (-x, y), (-y, x),
                               (x, -y), (y, -x), (-x, -y), (-y, -x)):
                    self.pixel(cx + sx, cy + sy, color)
                if d < 0:
                    d += 2 * x + 3
                else:
                    d += 2 * (x - y) + 5
                    y -= 1
                x += 1

    def ellipse(self, cx, cy, rx, ry, color):
        # Parametric ellipse outline, 1px.
        import math
        steps = max(48, int(2 * math.pi * max(rx, ry)))
        for i in range(steps):
            a = 2 * math.pi * i / steps
            self.pixel(int(cx + rx * math.cos(a)),
                       int(cy + ry * math.sin(a)), color)


# ------------------------------------------------------------- bitmap font
# A 5x7 pixel font, written out by hand: each glyph is 7 rows of 5 cells,
# '#' is ink, '.' is empty. Uppercase, lowercase, digits, punctuation.

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}

FONT.update({
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    "q": ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01001", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
})


def char_width(scale):
    return 6 * scale


def text_width(text, scale):
    return len(text) * char_width(scale) - scale


def draw_text(cv, x, y, text, scale=2, color=INK):
    """Draw text left-aligned at (x, y); returns width drawn."""
    cx = x
    for ch in text:
        glyph = FONT.get(ch)
        if glyph is None:
            cx += char_width(scale)
            continue
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    cv.fill_rect(cx + gx * scale, y + gy * scale,
                                 scale, scale, color)
        cx += char_width(scale)
    return cx - x


def draw_text_centered(cv, cx, y, text, scale=2, color=INK):
    w = text_width(text, scale)
    draw_text(cv, cx - w // 2, y, text, scale, color)
    return w


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns list of lines fitting max_width px."""
    max_chars = max(1, (max_width + scale) // char_width(scale))
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            # A single over-long word is split hard.
            while len(word) > max_chars:
                lines.append(word[:max_chars])
                word = word[max_chars:]
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_paragraph(cv, x, y, width, text, scale=2, color=INK, leading=4):
    """Draw a wrapped paragraph; returns the y just below it."""
    line_h = 7 * scale + leading
    for line in wrap_text(text, scale, width):
        draw_text(cv, x, y, line, scale, color)
        y += line_h
    return y


# ------------------------------------------------------------ page drawing

def draw_globe(cv, cx, cy, r, color=INK):
    """Wireframe globe: outline, meridians, parallels, three land dots."""
    cv.circle(cx, cy, r, color, thick=2)
    cv.ellipse(cx, cy, int(r * 0.45), r, color)
    cv.ellipse(cx, cy, int(r * 0.85), r, color)
    cv.hline(cx - r, cy, 2 * r, color, thick=1)
    cv.ellipse(cx, cy, r, int(r * 0.45), color)
    cv.ellipse(cx, cy, r, int(r * 0.85), color)
    # A few landmass dots to suggest continents.
    for dx, dy in ((-14, -12), (-6, -18), (10, 4), (18, -8), (-2, 16)):
        cv.fill_rect(cx + dx - 2, cy + dy - 2, 5, 5, color)


def section_box(cv, x, y, w, h, title, body, title_color=None):
    """A bordered box with a coloured header bar and wrapped body text."""
    cv.fill_rect(x, y, w, 26, RED)
    draw_text(cv, x + 10, y + 6, title, scale=2, color=PAPER)
    cv.fill_rect(x, y + 26, w, 1, INK)
    cv.vline(x, y, h, INK, thick=1)
    cv.vline(x + w - 1, y, h, INK, thick=1)
    cv.hline(x, y + h - 1, w, INK, thick=1)
    return draw_paragraph(cv, x + 10, y + 36, w - 20, body, scale=2)


def draw_page():
    cv = Canvas()

    # ---- dateline ------------------------------------------------------
    draw_text(cv, 30, 30, "SATURDAY 21 NOVEMBER 2026", scale=2)
    right = "WORLD EDITION  -  No. 325"
    draw_text(cv, W - 30 - text_width(right, 2), 30, right, scale=2, color=GREY)

    # ---- masthead ------------------------------------------------------
    draw_globe(cv, 76, 86, 36)
    draw_text_centered(cv, 540, 54, "THE DAILY GLOBE", scale=8)
    draw_text_centered(cv, 540, 122, "ALL THE WORLD'S NEWS IN ONE PAGE",
                       scale=2, color=GREY)

    # ---- rules under the masthead --------------------------------------
    cv.hline(30, 146, W - 60, INK, thick=4)
    cv.hline(30, 154, W - 60, INK, thick=1)

    # ---- kicker --------------------------------------------------------
    draw_text_centered(
        cv, W // 2, 168,
        "WAR IN EUROPE  -  MARKETS IN TURMOIL  -  A VERDICT FOR THE ROHINGYA",
        scale=2, color=RED)

    # ---- main headline -------------------------------------------------
    draw_text_centered(cv, W // 2, 194, "RUSSIA RAINS FIRE", scale=7)
    draw_text_centered(cv, W // 2, 252, "ON UKRAINE", scale=7, color=RED)

    # ---- subhead -------------------------------------------------------
    draw_text_centered(
        cv, W // 2, 312,
        "More than 400 drones and 110 missiles strike Kyiv and other cities",
        scale=2)
    draw_text_centered(
        cv, W // 2, 330,
        "overnight; two Russian missiles and a drone come down in Poland.",
        scale=2)

    cv.hline(30, 356, W - 60, INK, thick=2)

    # ---- left column: the lead story -----------------------------------
    lx, lw = 30, 570
    y = 372
    draw_text(cv, lx, y, "THE WAR IN EUROPE", scale=2, color=RED)
    y += 24
    y = draw_paragraph(
        cv, lx, y, lw,
        "Russia launched its biggest attacks of the year on Ukraine "
        "overnight, firing more than 400 drones and 110 missiles. At "
        "least eight people were killed in Kyiv, where strikes damaged "
        "bridges and railway stations. A later strike on Kryvyi Rih "
        "wounded about 20 people.", scale=2)
    y += 10
    y = draw_paragraph(
        cv, lx, y, lw,
        "Poland said two Russian missiles and a suspected drone came "
        "down on its territory. Prime Minister Donald Tusk called it a "
        "deliberate provocation, saying it came as Kyiv's allies held a "
        "military exercise.", scale=2)
    y += 16
    draw_text(cv, lx, y, "WASHINGTON", scale=2, color=RED)
    y += 24
    y = draw_paragraph(
        cv, lx, y, lw,
        "TRUMP CALLS PUTIN A FRIEND. President Trump called Vladimir "
        "Putin a friend as the strikes fell. President Zelensky replied "
        "that Putin is a killer. The US left any mention of Ukraine out "
        "of a joint statement after a summit with China and Russia.",
        scale=2)

    # ---- divider between columns ---------------------------------------
    cv.vline(612, 372, 398, GREY, thick=1)

    # ---- right column --------------------------------------------------
    rx, rw = 628, 366
    y = 372
    y = section_box(
        cv, rx, y, rw, 218, "MARKETS IN TURMOIL",
        "US stocks fell sharply on Friday as a sell-off in AI and chip "
        "shares pushed the S&P 500 down 3.7% and the Dow into "
        "correction. The Nasdaq is down 5% this year, erasing all its "
        "2026 gains. The SEC has opened a probe into Nvidia's "
        "accounting.")
    y += 12
    section_box(
        cv, rx, y, rw, 168, "A VERDICT FOR THE ROHINGYA",
        "The International Court of Justice found Myanmar responsible "
        "for genocide against the Rohingya. Britain expelled Myanmar's "
        "diplomat and demanded justice.")

    # ---- three stories across the foot ---------------------------------
    by = 786
    bh = 150
    boxes = [
        ("UK AND EU SIGN DEALS",
         "Three post-Brexit agreements on food trade, carbon markets "
         "and youth mobility for 100,000 young Britons."),
        ("COP31 RUNS PAST DEADLINE",
         "Climate talks in Antalya ran into overtime as nearly 200 "
         "nations failed to agree on fossil fuels."),
        ("A PILL THAT BEATS CANCER",
         "Trial pill daraxonrasib made pancreatic tumours undetectable "
         "in one in 12 patients."),
    ]
    for i, (title, body) in enumerate(boxes):
        bx = 30 + i * 326
        section_box(cv, bx, by, 308, bh, title, body)

    # ---- also today ----------------------------------------------------
    cv.hline(30, 950, W - 60, INK, thick=2)
    draw_paragraph(
        cv, 30, 962, W - 60,
        "ALSO TODAY: Gen Z protests in 25 European countries. Voyager 1, "
        "the first man-made object one light-day from Earth. Houthi "
        "missiles aimed at Riyadh downed for a third night.",
        scale=2, color=GREY)

    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = draw_page()
    write_png(os.path.join(out_dir, "entry.png"), cv.rows)


if __name__ == "__main__":
    main()
