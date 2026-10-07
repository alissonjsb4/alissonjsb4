"""Builds assets/banner.gif from assets/vhs-moon.jpg.

The still is a VHS capture, so the overlay copies a VCR's on-screen display:
PLAY and the tape speed at the top, a tracking band that rolls down the
picture once per loop. Run from the repository root:

    python assets/make_banner.py
"""
from pathlib import Path
import random

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "vhs-moon.jpg"
FONT = ROOT / "fonts" / "VT323-Regular.ttf"
OUT = ROOT / "banner.gif"

W, H = 1200, 402
FRAMES = 22
FRAME_MS = 110
BAND_FRAMES = 11          # frames in which the tracking band is on screen
BAND = 10                 # half height of the band, in pixels

TITLE = "ALISSON JAIME"
SUBTITLE = "RTL · FPGA · RISC-V · RADIATION TESTING"
PLACE = "FORTALEZA, BRAZIL"

WHITE = (236, 240, 255)


def font(size):
    return ImageFont.truetype(str(FONT), size)


def background():
    im = Image.open(SRC).convert("RGB").resize((W, H), Image.BICUBIC)
    # Darken the lower half so the text reads over the clouds.
    ramp = Image.linear_gradient("L").resize((W, H))
    mask = ramp.point(lambda v: 0 if v < 120 else min(200, int((v - 120) * 1.5)))
    im = Image.composite(Image.new("RGB", (W, H), (3, 5, 18)), im, mask)
    # Scanlines: every third row a little darker.
    lines = Image.new("L", (W, H), 255)
    draw = ImageDraw.Draw(lines)
    for y in range(0, H, 3):
        draw.line([(0, y), (W, y)], fill=205)
    return ImageChops.multiply(im, Image.merge("RGB", [lines] * 3))


def put(im, xy, text, f, shift=0, alpha=255):
    """Text with a drop shadow and, if shift > 0, a red/cyan colour fringe."""
    x, y = xy
    passes = [((x + 3, y + 3), (0, 0, 0, 150))]
    if shift:
        passes += [((x - shift, y), (255, 50, 100, 120)),
                   ((x + shift, y), (40, 220, 255, 120))]
    passes.append(((x, y), WHITE + (alpha,)))
    for pos, colour in passes:
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).text(pos, text, font=f, fill=colour)
        im = Image.alpha_composite(im, layer)
    return im


def static_frame():
    im = background().convert("RGBA")
    osd = font(42)
    im = put(im, (44, 26), "PLAY", osd)
    tri_x = 44 + ImageDraw.Draw(im).textlength("PLAY ", font=osd)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).polygon(
        [(tri_x, 38), (tri_x, 66), (tri_x + 24, 52)], fill=WHITE + (255,))
    im = Image.alpha_composite(im, layer)
    sp_w = ImageDraw.Draw(im).textlength("SP", font=osd)
    im = put(im, (W - 44 - sp_w, 26), "SP", osd)

    title_f, sub_f, place_f = font(104), font(40), font(34)
    im = put(im, (40, H - 166), TITLE, title_f, shift=3)
    im = put(im, (44, H - 70), SUBTITLE, sub_f)
    place_w = ImageDraw.Draw(im).textlength(PLACE, font=place_f)
    im = put(im, (W - 44 - place_w, H - 64), PLACE, place_f, alpha=200)
    return im.convert("RGB")


def tracking_band(im, i, rng):
    """Shift the rows of a band sideways and lift them, like bad tracking."""
    centre = int(-BAND + (H + 2 * BAND) * i / (BAND_FRAMES - 1))
    out = im.copy()
    for y in range(max(0, centre - BAND), min(H, centre + BAND)):
        dx = rng.randint(-6, 6)
        row = im.crop((0, y, W, y + 1))
        row = Image.blend(row, Image.new("RGB", (W, 1), (190, 200, 255)), 0.10)
        out.paste(row, (dx, y))
    noise = ImageDraw.Draw(out)
    for _ in range(40):
        x = rng.randrange(W)
        y = centre + rng.randint(-BAND, BAND)
        if 0 <= y < H:
            noise.line([(x, y), (x + rng.randint(4, 22), y)], fill=(225, 230, 255))
    return out


def main():
    still = static_frame()
    rng = random.Random(7)
    frames = []
    for i in range(FRAMES):
        frames.append(tracking_band(still, i, rng) if i < BAND_FRAMES else still)

    palette = frames[0].quantize(colors=160, method=Image.Quantize.MEDIANCUT)
    frames = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    frames[0].save(OUT, save_all=True, append_images=frames[1:],
                   duration=FRAME_MS, loop=0, disposal=1)
    print(f"{OUT.name}: {OUT.stat().st_size // 1024} KB, {len(frames)} frames")


if __name__ == "__main__":
    main()
