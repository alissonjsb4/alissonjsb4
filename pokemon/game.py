"""Wild Pokémon encounter at the bottom of the profile README.

Run by .github/workflows/pokemon.yml when someone opens an issue titled
"pokemon|throw" or "pokemon|run". Updates pokemon/state.json, draws a new
encounter GIF when a new Pokémon shows up, rewrites the block between the
pokemon markers in README.md and prints the reply that goes on the issue.

    python pokemon/game.py throw <github-login>
    python pokemon/game.py run <github-login>
    python pokemon/game.py new [dex-id]     # maintenance: force an encounter
    python pokemon/game.py render           # maintenance: redraw README only
"""
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
import io
import json
import math
import random
import re
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageSequence

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "pokemon"
STATE = DIR / "state.json"
POOL = DIR / "pool.json"
README = ROOT / "README.md"
BACKGROUND = ROOT / "assets" / "void.jpg"
FONT = ROOT / "assets" / "fonts" / "VT323-Regular.ttf"

REPO = "alissonjsb4/alissonjsb4"
SPRITE = ("https://raw.githubusercontent.com/PokeAPI/sprites/master/"
          "sprites/pokemon/other/showdown/{shiny}{id}.gif")
START, END = "<!-- pokemon:start -->", "<!-- pokemon:end -->"

BALLS = 3            # throws before the Pokémon flees
SHINY_ODDS = 128
RECENT = 5           # catches listed in the README
KEEP = 50            # catches kept in state.json
MAX_FRAMES = 40
W, H = 720, 405
WHITE = (236, 240, 255)

BROKE_FREE = [
    "Oh no! The Pokémon broke free!",
    "Aww! It appeared to be caught!",
    "Aargh! Almost had it!",
    "Shoot! It was so close, too!",
]

rng = random.SystemRandom()


# ---------- state ----------

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(state):
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8")


def empty_state():
    return {"encounter": None, "caught": [],
            "stats": {"throws": 0, "caught": 0, "fled": 0, "trainers": []}}


def display(enc):
    return ("shiny " if enc["shiny"] else "") + enc["name"]


# ---------- encounter ----------

def new_encounter(state, pool, dex_id=None):
    if dex_id is None:
        tiers = pool["tiers"]
        tier = rng.choices(list(tiers), weights=[t["weight"] for t in tiers.values()])[0]
        mon = rng.choice([p for p in pool["pokemon"] if p["tier"] == tier])
    else:
        mon = next(p for p in pool["pokemon"] if p["id"] == dex_id)
    number = state["encounter"]["n"] + 1 if state["encounter"] else 1
    state["encounter"] = {
        "n": number, "id": mon["id"], "name": mon["name"], "tier": mon["tier"],
        "shiny": rng.randrange(SHINY_ODDS) == 0, "balls": BALLS,
    }
    draw_encounter(state["encounter"], pool)
    for old in DIR.glob("encounter-*.gif"):
        if old.name != gif_name(state["encounter"]):
            old.unlink()
    return state["encounter"]


def gif_name(enc):
    # A new name per encounter, so browsers and GitHub's cache never show the old one.
    return f"encounter-{enc['n']}.gif"


def throw(state, pool, trainer):
    enc = state["encounter"]
    stats = state["stats"]
    stats["throws"] += 1
    if trainer not in stats["trainers"]:
        stats["trainers"].append(trainer)
    lines = [f"@{trainer} threw a Poké Ball at the wild {display(enc)}..."]

    if rng.random() < pool["tiers"][enc["tier"]]["catch"]:
        stats["caught"] += 1
        state["caught"].insert(0, {
            "id": enc["id"], "name": enc["name"], "shiny": enc["shiny"],
            "trainer": trainer,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        })
        del state["caught"][KEEP:]
        lines.append(f"Gotcha! {display(enc)} was caught!")
        if enc["tier"] == "partner":
            lines.append("That one is my partner. Take good care of it.")
        nxt = new_encounter(state, pool)
        lines.append(f"A wild {display(nxt)} appeared on the profile.")
        return lines

    enc["balls"] -= 1
    lines.append(rng.choice(BROKE_FREE))
    if enc["balls"] == 0:
        stats["fled"] += 1
        lines.append(f"The wild {display(enc)} fled!")
        nxt = new_encounter(state, pool)
        lines.append(f"A wild {display(nxt)} appeared on the profile.")
    else:
        left = enc["balls"]
        lines.append(f"{left} Poké Ball{'s' if left > 1 else ''} left before it runs away.")
    return lines


def run_away(state, pool, trainer):
    old = state["encounter"]
    nxt = new_encounter(state, pool)
    return [f"@{trainer} ran from the wild {display(old)}.", "Got away safely!",
            f"A wild {display(nxt)} appeared on the profile."]


# ---------- drawing ----------

def font(size):
    return ImageFont.truetype(str(FONT), size)


def background():
    im = Image.open(BACKGROUND).convert("RGB").resize((W, H), Image.BICUBIC)
    lines = Image.new("L", (W, H), 255)
    draw = ImageDraw.Draw(lines)
    for y in range(0, H, 3):
        draw.line([(0, y), (W, y)], fill=210)
    im = ImageChops.multiply(im, Image.merge("RGB", [lines] * 3)).convert("RGBA")

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle([24, H - 92, W - 24, H - 20], radius=10,
                           fill=(6, 10, 32, 225), outline=(190, 200, 255, 255), width=3)
    return Image.alpha_composite(im, layer)


def text(im, xy, s, f, fill=WHITE):
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.text((xy[0] + 2, xy[1] + 2), s, font=f, fill=(0, 0, 0, 160))
    draw.text(xy, s, font=f, fill=fill + (255,))
    return Image.alpha_composite(im, layer)


def sprite_frames(enc):
    url = SPRITE.format(shiny="shiny/" if enc["shiny"] else "", id=enc["id"])
    req = Request(url, headers={"User-Agent": f"{REPO} profile game"})
    with urlopen(req, timeout=30) as resp:
        gif = Image.open(io.BytesIO(resp.read()))
    frames, durations = [], []
    for frame in ImageSequence.Iterator(gif):
        frames.append(frame.convert("RGBA"))
        durations.append(max(int(frame.info.get("duration", 80)), 40))
    if len(frames) > MAX_FRAMES:
        step = math.ceil(len(frames) / MAX_FRAMES)
        durations = [sum(durations[i:i + step]) for i in range(0, len(frames), step)]
        frames = frames[::step]
    return frames, durations


def draw_encounter(enc, pool):
    frames, durations = sprite_frames(enc)

    # Crop every frame to the union of their bounding boxes so the sprite stays put.
    box = None
    for f in frames:
        b = f.getchannel("A").getbbox()
        if b:
            box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]),
                                         max(box[2], b[2]), max(box[3], b[3]))
    frames = [f.crop(box) for f in frames]
    sw, sh = frames[0].size
    scale = max(1, min(3, 200 // max(sw, sh)))
    frames = [f.resize((sw * scale, sh * scale), Image.NEAREST) for f in frames]
    sw, sh = frames[0].size
    ground = H - 112
    x, y = (W - sw) // 2, ground - sh

    still = background()
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse(
        [W // 2 - sw * 0.38, ground - 9, W // 2 + sw * 0.38, ground + 9], fill=(0, 0, 0, 120))
    still = Image.alpha_composite(still, shadow)

    osd = font(34)
    still = text(still, (40, 22), f"ENCOUNTER {enc['n']:03d}", osd)
    label = pool["tiers"][enc["tier"]]["label"]
    if enc["shiny"]:
        label = (label + "  SHINY").strip()
    if label:
        width = ImageDraw.Draw(still).textlength(label, font=osd)
        still = text(still, (W - 40 - width, 22), label, osd)

    line = f"A wild {display(enc).upper()} appeared!"
    size = 40
    while ImageDraw.Draw(still).textlength(line, font=font(size)) > W - 100:
        size -= 2
    still = text(still, (48, H - 56 - size // 2 - 4), line, font(size))

    composed = []
    for f in frames:
        canvas = still.copy()
        canvas.alpha_composite(f, (x, y))
        composed.append(canvas.convert("RGB"))

    sample = Image.new("RGB", (W, H * min(4, len(composed))))
    for i, c in enumerate(composed[:4]):
        sample.paste(c, (0, H * i))
    palette = sample.quantize(colors=200, method=Image.Quantize.MEDIANCUT)
    out = [c.quantize(palette=palette, dither=Image.Dither.NONE) for c in composed]
    out[0].save(DIR / gif_name(enc), save_all=True, append_images=out[1:],
                duration=durations, loop=0, disposal=1)


# ---------- README ----------

def issue_link(move):
    body = ("Just submit this issue. A GitHub Action plays the move, replies here "
            "and updates the profile in about a minute.")
    return (f"https://github.com/{REPO}/issues/new?title={quote('pokemon|' + move)}"
            f"&body={quote(body)}")


def render(state):
    enc = state["encounter"]
    stats = state["stats"]
    left = enc["balls"]
    parts = [
        START,
        '<p align="center">',
        f'  <img src="pokemon/{gif_name(enc)}" width="600" alt="A wild {display(enc)} appeared">',
        "</p>",
        '<p align="center">',
        f'  <a href="{issue_link("throw")}">Throw a Poké Ball</a> &nbsp;·&nbsp; '
        f'<a href="{issue_link("run")}">Run</a>',
        "</p>",
        '<p align="center"><sub>Each link opens an issue with the move in the title. '
        "Submit it and a GitHub Action rolls the throw, replies in the issue and updates "
        f"this page in about a minute. Poké Balls left for this one: {left}.</sub></p>",
        "",
    ]
    if state["caught"]:
        parts += ["Recently caught", "", "| | Pokémon | Trainer | Date |", "|---|---|---|---|"]
        for c in state["caught"][:RECENT]:
            img = SPRITE.format(shiny="shiny/" if c["shiny"] else "", id=c["id"])
            name = ("Shiny " if c["shiny"] else "") + c["name"]
            parts.append(f'| <img src="{img}" height="40" alt=""> | {name} | '
                         f'[@{c["trainer"]}](https://github.com/{c["trainer"]}) | {c["date"]} |')
        parts.append("")
    trainers = len(stats["trainers"])
    if stats["throws"]:
        tally = (f"{stats['caught']} caught, {stats['fled']} fled, "
                 f"{stats['throws']} Poké Ball{'s' if stats['throws'] != 1 else ''} thrown by "
                 f"{trainers} trainer{'s' if trainers != 1 else ''}.")
    else:
        tally = "No Poké Balls thrown yet."
    parts.append(f'<p align="center"><sub>{tally} Sprites from PokéAPI.</sub></p>')
    parts.append(END)

    readme = README.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + ".*?" + re.escape(END), re.S)
    if not pattern.search(readme):
        sys.exit("README has no pokemon markers")
    README.write_text(pattern.sub(lambda _: "\n".join(parts), readme), encoding="utf-8")


# ---------- entry point ----------

def main(argv):
    if not argv:
        sys.exit(__doc__)
    sys.stdout.reconfigure(encoding="utf-8")
    move = argv[0].strip().lower()
    pool = load(POOL)
    state = load(STATE) if STATE.exists() else empty_state()

    if move == "render":
        render(state)
        return
    if move == "new":
        new_encounter(state, pool, int(argv[1]) if len(argv) > 1 else None)
        save_state(state)
        render(state)
        return

    trainer = argv[1] if len(argv) > 1 else ""
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", trainer):
        sys.exit(f"not a GitHub login: {trainer!r}")
    if state["encounter"] is None:
        new_encounter(state, pool)
    if move == "throw":
        lines = throw(state, pool, trainer)
    elif move == "run":
        lines = run_away(state, pool, trainer)
    else:
        sys.exit(f"unknown move: {move!r}")

    save_state(state)
    render(state)
    print("\n\n".join(lines))
    print(f"\n[Back to the profile](https://github.com/{REPO.split('/')[0]})")


if __name__ == "__main__":
    main(sys.argv[1:])
