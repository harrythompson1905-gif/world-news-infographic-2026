import os
import struct
import zlib
import textwrap

# World News infographic - 18 November 2026
# Uses only Python's standard library. No Pillow or extra packages required.

WIDTH, HEIGHT = 800, 800
OUT_DIR = "output"
OUT_FILE = os.path.join(OUT_DIR, "entry.png")

BG = (244, 245, 247)
NAVY = (15, 23, 42)
WHITE = (255, 255, 255)
DARK = (30, 41, 59)
MUTED = (100, 116, 139)
BLUE = (37, 99, 235)
GREEN = (16, 185, 129)
ORANGE = (234, 88, 12)
PURPLE = (124, 58, 237)

# Simple built-in 5x7 pixel font. This keeps the script dependency-free.
FONT = {
'A':["01110","10001","10001","11111","10001","10001","10001"],
'B':["11110","10001","10001","11110","10001","10001","11110"],
'C':["01111","10000","10000","10000","10000","10000","01111"],
'D':["11110","10001","10001","10001","10001","10001","11110"],
'E':["11111","10000","10000","11110","10000","10000","11111"],
'F':["11111","10000","10000","11110","10000","10000","10000"],
'G':["01111","10000","10000","10111","10001","10001","01111"],
'H':["10001","10001","10001","11111","10001","10001","10001"],
'I':["11111","00100","00100","00100","00100","00100","11111"],
'J':["00111","00010","00010","00010","10010","10010","01100"],
'K':["10001","10010","10100","11000","10100","10010","10001"],
'L':["10000","10000","10000","10000","10000","10000","11111"],
'M':["10001","11011","10101","10101","10001","10001","10001"],
'N':["10001","11001","10101","10011","10001","10001","10001"],
'O':["01110","10001","10001","10001","10001","10001","01110"],
'P':["11110","10001","10001","11110","10000","10000","10000"],
'Q':["01110","10001","10001","10001","10101","10010","01101"],
'R':["11110","10001","10001","11110","10100","10010","10001"],
'S':["01111","10000","10000","01110","00001","00001","11110"],
'T':["11111","00100","00100","00100","00100","00100","00100"],
'U':["10001","10001","10001","10001","10001","10001","01110"],
'V':["10001","10001","10001","10001","10001","01010","00100"],
'W':["10001","10001","10001","10101","10101","10101","01010"],
'X':["10001","10001","01010","00100","01010","10001","10001"],
'Y':["10001","10001","01010","00100","00100","00100","00100"],
'Z':["11111","00001","00010","00100","01000","10000","11111"],
'0':["01110","10001","10011","10101","11001","10001","01110"],
'1':["00100","01100","00100","00100","00100","00100","01110"],
'2':["01110","10001","00001","00010","00100","01000","11111"],
'3':["11110","00001","00001","01110","00001","00001","11110"],
'4':["00010","00110","01010","10010","11111","00010","00010"],
'5':["11111","10000","10000","11110","00001","00001","11110"],
'6':["01110","10000","10000","11110","10001","10001","01110"],
'7':["11111","00001","00010","00100","01000","01000","01000"],
'8':["01110","10001","10001","01110","10001","10001","01110"],
'9':["01110","10001","10001","01111","00001","00001","01110"],
' ':["00000"]*7, '-':["00000","00000","00000","11111","00000","00000","00000"],
':':["00000","00100","00100","00000","00100","00100","00000"],
'.':["00000","00000","00000","00000","00000","00110","00110"],
',':["00000","00000","00000","00000","00110","00110","00100"],
"'":["00100","00100","00000","00000","00000","00000","00000"],
'/':["00001","00010","00010","00100","01000","01000","10000"],
'$':["00100","01111","10100","01110","00101","11110","00100"],
'%':["11001","11010","00100","01000","10110","00110","00000"],
'&':["01100","10010","10100","01000","10101","10010","01101"],
'(':["00010","00100","01000","01000","01000","00100","00010"],
')':["01000","00100","00010","00010","00010","00100","01000"],
'|':["00100","00100","00100","00100","00100","00100","00100"],
'+':["00000","00100","00100","11111","00100","00100","00000"],
'?':["01110","10001","00001","00010","00100","00000","00100"],
}

def make_canvas(w, h, color):
    return [[color for _ in range(w)] for _ in range(h)]

pixels = make_canvas(WIDTH, HEIGHT, BG)

def rect(x1, y1, x2, y2, color):
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(WIDTH, x2), min(HEIGHT, y2)
    for y in range(y1, y2):
        pixels[y][x1:x2] = [color] * (x2 - x1)

def text_width(s, scale):
    return max(0, len(s) * 6 * scale - scale)

def draw_text(s, x, y, color, scale=2):
    s = s.upper()
    cursor = x
    for ch in s:
        glyph = FONT.get(ch, FONT['?'])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    rect(cursor + gx*scale, y + gy*scale,
                         cursor + (gx+1)*scale, y + (gy+1)*scale, color)
        cursor += 6 * scale

def wrap_words(s, max_chars):
    return textwrap.wrap(s.upper(), width=max_chars, break_long_words=True)

def draw_wrapped(s, x, y, color, scale, max_chars, line_gap=5, max_lines=None):
    lines = wrap_words(s, max_chars)
    if max_lines:
        lines = lines[:max_lines]
    line_h = 7 * scale + line_gap
    for i, line in enumerate(lines):
        draw_text(line, x, y + i*line_h, color, scale)
    return y + len(lines)*line_h

def card(x, y, w, h, accent, category, headline, summary, source):
    rect(x, y, x+w, y+h, WHITE)
    rect(x, y, x+7, y+h, accent)
    draw_text(category, x+22, y+20, accent, 2)
    # Small divider
    rect(x+22, y+43, x+w-22, y+45, (226, 232, 240))
    hy = draw_wrapped(headline, x+22, y+61, DARK, 2, 25, 6, 4)
    sy = hy + 8
    draw_wrapped(summary, x+22, sy, MUTED, 1, 49, 5, 5)
    # Source credit sits near the bottom of each card.
    rect(x+22, y+h-39, x+w-22, y+h-38, (226, 232, 240))
    draw_text("SOURCE: " + source, x+22, y+h-27, MUTED, 1)

def create_png_image():
    # Header
    rect(0, 0, WIDTH, 120, NAVY)
    draw_text("WORLD NEWS", 40, 24, WHITE, 5)
    draw_text("WEDNESDAY  /  18 NOVEMBER 2026", 42, 82, (203, 213, 225), 2)

    # Four news cards
    card(40, 145, 345, 292, BLUE,
         "CLIMATE & ENERGY",
         "COP31: PACIFIC PUSHES FOR STRONGER CLIMATE ACTION",
         "Pacific-backed calls for a fossil-fuel transition remain in focus at COP31, alongside efforts to protect the 1.5C goal.",
         "PACNEWS / ISLANDS BUSINESS")

    card(415, 145, 345, 292, PURPLE,
         "AI & TECHNOLOGY",
         "CARNEY: GLOBAL AI RULES ARE URGENT",
         "Canada's prime minister says the lack of global AI governance creates major economic, biosecurity and democratic risks.",
         "EURONEWS / AFP")

    card(40, 465, 345, 292, GREEN,
         "SPACE & SCIENCE",
         "NASA LAUNCHES STUDENT SPACE-POWER CHALLENGE",
         "The 2026-27 Power to Explore challenge invites US K-12 students to imagine how nuclear power could support lunar missions.",
         "NASA")

    card(415, 465, 345, 292, ORANGE,
         "ECONOMY & TRADE",
         "NVIDIA REVENUE MORE THAN DOUBLES TO $115.8B",
         "NVIDIA reported third-quarter fiscal 2027 revenue of $115.8 billion, up 103% year over year, as AI infrastructure demand grows.",
         "NVIDIA / REUTERS")

    # Footer strip and credits
    rect(0, 770, WIDTH, 800, NAVY)
    draw_text("GLOBAL BRIEFING  |  18 NOVEMBER 2026", 40, 782, WHITE, 2)

    # Encode RGB pixels as a PNG
    raw = bytearray()
    for row in pixels:
        raw.append(0)  # PNG filter: None
        for color in row:
            raw.extend(color)

    compressed = zlib.compress(raw, 9)

    def write_chunk(f, chunk_type, data):
        f.write(struct.pack(">I", len(data)))
        f.write(chunk_type)
        f.write(data)
        crc = zlib.crc32(chunk_type)
        crc = zlib.crc32(data, crc)
        f.write(struct.pack(">I", crc & 0xFFFFFFFF))

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_FILE, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        write_chunk(f, b"IHDR", struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0))
        write_chunk(f, b"IDAT", compressed)
        write_chunk(f, b"IEND", b"")

    print("Created:", os.path.abspath(OUT_FILE))
    print("Open output/entry.png to inspect your infographic.")

if __name__ == "__main__":
    create_png_image()
