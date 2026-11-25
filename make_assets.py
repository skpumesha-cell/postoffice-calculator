import io
import os
import struct

from PIL import Image, ImageChops

os.makedirs("assets", exist_ok=True)

src = None
for p in ("assets/logo.png", "logo.png", "src/logo.png"):
    if os.path.exists(p):
        src = p
        break

if src is None:
    print("WARNING: logo.png not found, making a plain placeholder")
    img = Image.new("RGB", (600, 600), (255, 255, 255))
    img.paste((26, 77, 140), (150, 150, 450, 450))
else:
    img = Image.open(src).convert("RGB")
    print("Using logo:", src, img.size)


def tight(im, pad=8):
    """Crop away the white/grey background around the artwork."""
    mask = im.convert("L").point(lambda v: 255 if v < 225 else 0)
    box = mask.getbbox()
    if not box:
        return im
    l, t, r, b = box
    return im.crop((max(0, l - pad), max(0, t - pad),
                    min(im.width, r + pad), min(im.height, b + pad)))


def soft_alpha(im):
    """Turn the white background into transparency (for the icon)."""
    im = im.convert("RGB")
    r, g, b = im.split()
    mn = ImageChops.darker(ImageChops.darker(r, g), b)
    a = mn.point(lambda v: 255 if v <= 190 else max(0, int((255 - v) * 255 / 65)))
    out = im.convert("RGBA")
    out.putalpha(a)
    return out


def square(im, side):
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(im, ((side - im.width) // 2, (side - im.height) // 2), im)
    return canvas


def bmp_frame(im):
    """32-bit BMP icon frame (works on every Windows version)."""
    w, h = im.size
    px = im.load()
    header = struct.pack("<IiiHHIIiiII", 40, w, h * 2, 1, 32, 0, w * h * 4, 0, 0, 0, 0)
    rows = []
    for y in range(h - 1, -1, -1):
        row = bytearray()
        for x in range(w):
            r, g, b, a = px[x, y]
            row += bytes((b, g, r, a))
        rows.append(bytes(row))
    mask = bytes(((w + 31) // 32) * 4 * h)
    return header + b"".join(rows) + mask


def write_ico(path, master):
    frames = []
    for s in (16, 24, 32, 48):
        frames.append((s, bmp_frame(master.resize((s, s), Image.LANCZOS))))
    buf = io.BytesIO()
    master.resize((256, 256), Image.LANCZOS).save(buf, "PNG")
    frames.append((256, buf.getvalue()))
    out = struct.pack("<HHH", 0, 1, len(frames))
    offset = 6 + 16 * len(frames)
    data = b""
    for s, blob in frames:
        out += struct.pack("<BBBBHHII", 0 if s == 256 else s, 0 if s == 256 else s,
                           0, 0, 1, 32, len(blob), offset + len(data))
        data += blob
    with open(path, "wb") as f:
        f.write(out + data)


W, H = img.size
full = tight(img)
mark = tight(img.crop((int(W * 0.38), int(H * 0.15), int(W * 0.62), int(H * 0.60))))

# full logo for the form and report (about 200 px wide)
fw = 200
full.resize((fw, int(full.height * fw / full.width)), Image.LANCZOS).save("assets/logo_full.png")

# small emblem next to the title (about 90 px tall)
mh = 90
mark.resize((int(mark.width * mh / mark.height), mh), Image.LANCZOS).save("assets/logo_mark.png")

# icon for the .exe, window, shortcuts
side = max(mark.size) + 24
master = square(soft_alpha(mark), side).resize((256, 256), Image.LANCZOS)
write_ico("assets/icon.ico", master)
print("assets ready:", sorted(os.listdir("assets")))
