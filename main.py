import struct
import zlib
import os
import math

# Constants
WIDTH, HEIGHT = 1024, 1024
PAPER = (242, 233, 213)
NAVY = (30, 58, 95)
GOLD = (176, 141, 62)
DESK = (34, 48, 60)
BLUE = (43, 76, 155)
RED = (163, 51, 39)
PURPLE = (107, 74, 138)

def get_val(c):
    if '0' <= c <= '9': return int(c)
    if 'A' <= c <= 'Z': return ord(c) - ord('A') + 10
    return 0

def checksum(s):
    weights = [7, 3, 1]
    res = 0
    for i, char in enumerate(s):
        res += get_val(char) * weights[i % 3]
    return res % 10

FONT = {
    'A': [0x7E, 0x11, 0x11, 0x11, 0x7E],
    'B': [0x7F, 0x49, 0x49, 0x49, 0x36],
    'C': [0x3E, 0x41, 0x41, 0x41, 0x22],
    'D': [0x7F, 0x41, 0x41, 0x22, 0x1C],
    'E': [0x7F, 0x49, 0x49, 0x49, 0x41],
    'F': [0x7F, 0x09, 0x09, 0x09, 0x01],
    'G': [0x3E, 0x41, 0x49, 0x49, 0x7A],
    'H': [0x7F, 0x08, 0x08, 0x08, 0x7F],
    'I': [0x41, 0x7F, 0x41],
    'J': [0x20, 0x40, 0x41, 0x3F, 0x01],
    'K': [0x7F, 0x08, 0x14, 0x22, 0x41],
    'L': [0x7F, 0x40, 0x40, 0x40, 0x40],
    'M': [0x7F, 0x06, 0x0C, 0x06, 0x7F],
    'N': [0x7F, 0x06, 0x08, 0x30, 0x7F],
    'O': [0x3E, 0x41, 0x41, 0x41, 0x3E],
    'P': [0x7F, 0x09, 0x09, 0x09, 0x06],
    'Q': [0x3E, 0x41, 0x51, 0x21, 0x5E],
    'R': [0x7F, 0x09, 0x19, 0x29, 0x46],
    'S': [0x46, 0x49, 0x49, 0x49, 0x31],
    'T': [0x01, 0x01, 0x7F, 0x01, 0x01],
    'U': [0x3F, 0x40, 0x40, 0x40, 0x3F],
    'V': [0x1F, 0x20, 0x40, 0x20, 0x1F],
    'W': [0x3F, 0x40, 0x38, 0x40, 0x3F],
    'X': [0x63, 0x14, 0x08, 0x14, 0x63],
    'Y': [0x07, 0x08, 0x70, 0x08, 0x07],
    'Z': [0x61, 0x51, 0x49, 0x45, 0x43],
    ' ': [0x00, 0x00, 0x00, 0x00, 0x00],
    '.': [0x00, 0x00, 0x60, 0x00, 0x00],
    '/': [0x04, 0x08, 0x10, 0x20, 0x40],
    '1': [0x02, 0x01, 0x7F, 0x00, 0x00],
    '2': [0x21, 0x43, 0x45, 0x49, 0x31],
    '3': [0x22, 0x41, 0x49, 0x49, 0x36],
    '4': [0x0C, 0x14, 0x24, 0x7F, 0x04],
    '5': [0x72, 0x51, 0x51, 0x51, 0x4E],
    '6': [0x3E, 0x49, 0x49, 0x49, 0x26],
    '7': [0x01, 0x01, 0x01, 0x01, 0x7F],
    '8': [0x36, 0x49, 0x49, 0x49, 0x36],
    '9': [0x32, 0x49, 0x49, 0x49, 0x3E],
    '0': [0x3E, 0x51, 0x49, 0x45, 0x3E],
    '<': [0x00, 0x00, 0x00, 0x00, 0x00],
    '-': [0x08, 0x08, 0x08, 0x08, 0x08],
    '(': [0x00, 0x7E, 0x40, 0x40, 0x40],
    ')': [0x40, 0x40, 0x40, 0x7E, 0x00],
    ':': [0x00, 0x00, 0x66, 0x00, 0x00],
    ',': [0x00, 0x00, 0x20, 0x00, 0x00],
    '\'': [0x00, 0x00, 0x07, 0x00, 0x00]
}

def draw_text(px, text, x, y, size, col):
    tx = x
    for char in text.upper():
        if char not in FONT: continue
        bits = FONT[char]
        for col_idx, col_data in enumerate(bits):
            for row_idx in range(7):
                if (col_data >> row_idx) & 1:
                    draw_rect(px, tx + col_idx * size, y + row_idx * size, size, size, col)
        tx += (len(bits) + 1) * size

# Calculate MRZ strings
line1 = "P<MRDRIBEIRO<<INES<CATARINA".ljust(44, '<')
doc_no = "MD0847132"
dob = "960312"
expiry = "340408"
personal = "<<<<<<<<<<<<<<"
c1 = str(checksum(doc_no))
c2 = str(checksum(dob))
c3 = str(checksum(expiry))
c4 = str(checksum(personal))
line2_core = doc_no + c1 + "MRD" + dob + c2 + "F" + expiry + c3 + personal + c4
line2 = line2_core.ljust(43, '<')
# Final checksum over the entire MRZ
c_final = str(checksum(line1 + line2))
line2 = line2 + c_final

pixels = [DESK] * (WIDTH * HEIGHT)

def draw_rect(px, x1, y1, w, h, col):
    for y in range(max(0, y1), min(HEIGHT, y1 + h)):
        for x in range(max(0, x1), min(WIDTH, x1 + w)):
            px[y * WIDTH + x] = col

def draw_ellipse(px, x0, y0, w, h, col):
    for y in range(max(0, y0 - h), min(HEIGHT, y0 + h + 1)):
        for x in range(max(0, x0 - w), min(WIDTH, x0 + w + 1)):
            if ((x - x0)**2 / (w**2 + 1e-9) + (y - y0)**2 / (h**2 + 1e-9)) <= 1:
                px[y * WIDTH + x] = col

def draw_polygon(px, pts, col):
    min_y = min(p[1] for p in pts)
    max_y = max(p[1] for p in pts)
    for y in range(max(0, min_y), min(HEIGHT, max_y + 1)):
        nodes = []
        j = len(pts) - 1
        for i in range(len(pts)):
            if (pts[i][1] < y and pts[j][1] >= y) or (pts[j][1] < y and pts[i][1] >= y):
                nodes.append(int(pts[i][0] + (y - pts[i][1]) / (pts[j][1] - pts[i][1]) * (pts[j][0] - pts[i][0])))
            j = i
        nodes.sort()
        for i in range(0, len(nodes), 2):
            if i + 1 < len(nodes):
                for x in range(max(0, nodes[i]), min(WIDTH, nodes[i+1] + 1)):
                    px[y * WIDTH + x] = col

# Fill desk
draw_rect(pixels, 0, 0, WIDTH, HEIGHT, DESK)

def draw_rotated_rect(px, x0, y0, w, h, angle, col):
    # Simplified center-based rotation
    cx, cy = x0 + w // 2, y0 + h // 2
    rad = math.radians(angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    for y in range(max(0, y0 - h), min(HEIGHT, y0 + 2 * h)):
        for x in range(max(0, x0 - w), min(WIDTH, x0 + 2 * w)):
            # Rotate back
            rx = (x - cx) * cos_a + (y - cy) * sin_a + cx
            ry = -(x - cx) * sin_a + (y - cy) * cos_a + cy
            if x0 <= rx < x0 + w and y0 <= ry < y0 + h:
                px[y * WIDTH + x] = col

# Draw pages
draw_rect(pixels, 32, 132, 480, 760, PAPER) # Left
draw_rect(pixels, 512, 132, 480, 760, PAPER) # Right

# Watermark
for y in range(132, 892, 100):
    for x in range(32, 992, 100):
        draw_text(pixels, "MRD", x, y, 4, (230, 230, 230))
# Guilloche
for i in range(0, 480, 20):
    for y in range(132, 150):
        px = 32 + i
        py = y + int(math.sin(i/20.0) * 5)
        if 32 <= px < 512 and 132 <= py < 892: pixels[py * WIDTH + px] = (200, 200, 200)

# Left page: Portrait, Data, Signature, Coat of Arms
draw_rect(pixels, 70, 250, 160, 200, NAVY) # Portrait frame
draw_rect(pixels, 75, 255, 150, 190, PAPER)
# Portrait: head, hair, neck, shoulders, simple duotone
draw_ellipse(pixels, 150, 290, 35, 45, GOLD) # Face
draw_rect(pixels, 120, 240, 60, 50, NAVY) # Hair
draw_rect(pixels, 130, 340, 40, 20, NAVY) # Shoulders
draw_rect(pixels, 145, 360, 10, 20, NAVY) # Neck placeholder base
draw_text(pixels, "TYPE P CODE MRD PASSPORT NO MD0847132", 70, 500, 2, NAVY)
draw_text(pixels, "SURNAME RIBEIRO", 70, 530, 2, NAVY)
draw_text(pixels, "GIVEN NAMES INES CATARINA", 70, 560, 2, NAVY)
draw_text(pixels, "NATIONALITY MERIDIAN", 70, 590, 2, NAVY)
draw_text(pixels, "DATE OF BIRTH 12 MAR 1996", 70, 620, 2, NAVY)
draw_text(pixels, "SEX F PLACE OF BIRTH PORT MERIDIA", 70, 650, 2, NAVY)
draw_text(pixels, "DATE OF ISSUE 08 APR 2024", 70, 680, 2, NAVY)
draw_text(pixels, "DATE OF EXPIRY 08 APR 2034", 70, 710, 2, NAVY)
draw_text(pixels, "AUTHORITY MINISTRY OF THE INTERIOR", 70, 740, 2, NAVY)
draw_text(pixels, "HOLDER'S SIGNATURE", 70, 800, 2, NAVY)
# Signature
pts = [(70, 830), (100, 810), (130, 840), (160, 820), (200, 830)]
for i in range(len(pts)-1):
    for t in range(10):
        px = int(pts[i][0] + (pts[i+1][0] - pts[i][0]) * t / 10)
        py = int(pts[i][1] + (pts[i+1][1] - pts[i][1]) * t / 10)
        pixels[py * WIDTH + px] = NAVY

# Coat of arms
draw_polygon(pixels, [(272, 220), (282, 240), (272, 260), (262, 240)], GOLD) # Replaced later
draw_text(pixels, "REPUBLIC OF MERIDIA", 70, 160, 3, NAVY)
draw_text(pixels, "PASSPORT", 70, 200, 3, NAVY)

# Replace visa box text
draw_text(pixels, "MULTIPLE ENTRY - 90 DAYS - NOT VALID FOR EMPLOYMENT", 520, 140, 2, NAVY)

# Add stamps on the right visa page
def draw_stamp(px, x, y, angle, col, text):
    # buffer stamp 60x60
    s_pixels = [PAPER] * (60 * 60)
    # simplified ring
    for i in range(0, 360, 10):
        rad = math.radians(i)
        sx, sy = 30 + int(28 * math.cos(rad)), 30 + int(28 * math.sin(rad))
        if 0 <= sx < 60 and 0 <= sy < 60: s_pixels[sy * 60 + sx] = col

    # Blit rotated
    rad = math.radians(angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    for sy in range(60):
        for sx in range(60):
            # Rotate back
            rx = int((sx - 30) * cos_a + (sy - 30) * sin_a + 30)
            ry = int(-(sx - 30) * sin_a + (sy - 30) * cos_a + 30)
            if 0 <= rx < 60 and 0 <= ry < 60:
                if s_pixels[ry * 60 + rx] == col:
                    if x+sx < WIDTH and y+sy < HEIGHT:
                        px[(y+sy) * WIDTH + (x+sx)] = col

draw_stamp(pixels, 600, 450, 10, BLUE, "ENTRY MERIDIA 14 JUN 2024")
draw_stamp(pixels, 700, 450, -10, RED, "ALDORIA ENTRY 02 SEP 2024")
draw_stamp(pixels, 800, 450, 5, PURPLE, "ALDORIA EXIT 09 SEP 2024")
draw_stamp(pixels, 600, 550, 0, BLUE, "TORVALD ENTRY 19 JAN 2025")
draw_stamp(pixels, 700, 550, 15, RED, "SILDARA ENTRY 27 MAY 2025")
draw_stamp(pixels, 800, 550, -15, PURPLE, "SILDARA EXIT 03 JUN 2025")
draw_stamp(pixels, 600, 650, 0, BLUE, "ALDORIA ENTRY 11 OCT 2026")
# Departure tax
draw_rect(pixels, 700, 650, 80, 40, BLUE)
draw_text(pixels, "TAX PAID 12 MD", 710, 660, 2, PAPER)

# Draw bottom strip
draw_text(pixels, line1, 40, 840, 2, NAVY)
draw_text(pixels, line2, 40, 860, 2, NAVY)

def save_png(pixels, filename):
    def make_chunk(type, data):
        length = struct.pack('>I', len(data))
        crc = struct.pack('>I', zlib.crc32(type + data) & 0xffffffff)
        return length + type + data + crc

    data = bytearray()
    for y in range(HEIGHT):
        data.append(0)
        for x in range(WIDTH):
            r, g, b = pixels[y * WIDTH + x]
            data.extend([r, g, b])
    cdata = zlib.compress(data)

    ihdr_data = struct.pack('>IIBBBBB', WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    ihdr = make_chunk(b'IHDR', ihdr_data)
    idat = make_chunk(b'IDAT', cdata)
    iend = make_chunk(b'IEND', b'')

    with open(filename, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + ihdr + idat + iend)

os.makedirs('/output', exist_ok=True)
save_png(pixels, '/output/entry.png')
