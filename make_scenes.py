# Star Catcher scene stills for the bounty video, rendered with PIL.
# Every still is original work made for this entry: the hook, the prompt
# typing out in a chat, the real game code, and the real terminal output
# from the gameplay capture. Run: python3 make_scenes.py
# Output: scenes/*.png at 1080x1920.

import os
import re
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
OUT = "scenes"
os.makedirs(OUT, exist_ok=True)

MAGENTA = (196, 28, 131)
INK = (25, 20, 25)
DARK = (20, 16, 46)
DARK2 = (36, 27, 77)
WHITE = (255, 255, 255)
GOLD = (255, 209, 102)
PINK = (255, 95, 162)
GREY = (160, 158, 180)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)

BOLD = lambda s: font("DejaVuSans-Bold.ttf", s)
REG = lambda s: font("DejaVuSans.ttf", s)
MONO = lambda s: font("DejaVuSansMono.ttf", s)
MONOB = lambda s: font("DejaVuSansMono-Bold.ttf", s)

PROMPT = ("Build a tiny browser game: catch falling stars in a basket \u2014 "
          "move with arrow keys or mouse, 3 misses and it\u2019s over, "
          "beat your best score.")

def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def center_text(draw, y, text, fnt, fill, spacing=0):
    draw.text((W // 2, y), text, font=fnt, fill=fill, anchor="ma")

# ---- Hook frames -------------------------------------------------------
def hook(text, sub, bg, fg, accent, name):
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    # faint giant circle behind the text, a dimmed accent
    dim = tuple((c + b) // 2 for c, b in zip(accent, bg))
    d.ellipse([W // 2 - 420, 620, W // 2 + 420, 1460], outline=dim, width=6)
    # two lines: "ONE" over "PROMPT." / "GAME." — one line overflows at this size
    first, rest = text.split(" ", 1)
    center_text(d, 800, first, BOLD(170), fg)
    center_text(d, 990, rest, BOLD(170), fg)
    if sub:
        center_text(d, 1240, sub, REG(46), accent)
    img.save(f"{OUT}/{name}.png")

hook("ONE PROMPT.", "one sentence. that\u2019s all it takes.", MAGENTA, WHITE, GOLD, "hook1")
hook("ONE GAME.", "built by an AI agent, while you watch.", INK, WHITE, PINK, "hook2")

# ---- Chat frames: the prompt typing out --------------------------------
def chat_frame(step, agent_stage, name):
    img = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(img)
    # header — pushed below the make.fun badge zone (badge sits x120 y272 330x128)
    d.rounded_rectangle([60, 440, W - 60, 560], radius=28, fill=DARK2)
    d.text((110, 468), "you  \u2192  your agent", font=BOLD(40), fill=WHITE)
    d.text((110, 518), "make.fun bounty \u00b7 just now", font=REG(30), fill=GREY)
    # user bubble with a growing slice of the prompt
    words = PROMPT.split()
    shown = " ".join(words[:step]) if step < len(words) else PROMPT
    fnt = REG(44)
    lines = wrap(d, shown, fnt, 780)
    bh = 70 + len(lines) * 62
    d.rounded_rectangle([150, 620, W - 60, 620 + bh], radius=36, fill=MAGENTA)
    y = 650
    for ln in lines:
        d.text((200, y), ln, font=fnt, fill=WHITE)
        y += 62
    # blinking caret while typing
    if step < len(words):
        last_w = d.textlength(lines[-1], font=fnt)
        d.rectangle([200 + last_w + 12, 650 + (len(lines) - 1) * 62,
                     200 + last_w + 20, 650 + (len(lines) - 1) * 62 + 48], fill=GOLD)
    # agent bubble
    ay = 620 + bh + 60
    if agent_stage == "typing":
        d.rounded_rectangle([60, ay, 300, ay + 110], radius=36, fill=(52, 44, 92))
        for i in range(3):
            d.ellipse([110 + i * 55, ay + 42, 150 + i * 55, ay + 82], fill=GREY)
    elif agent_stage == "reply":
        reply = "On it \u2014 building your game now."
        rl = wrap(d, reply, fnt, 780)
        rh = 70 + len(rl) * 62
        d.rounded_rectangle([60, ay, W - 150, ay + rh], radius=36, fill=(52, 44, 92))
        y = ay + 30
        for ln in rl:
            d.text((110, y), ln, font=fnt, fill=WHITE)
            y += 62
    img.save(f"{OUT}/{name}.png")

words = PROMPT.split()
n = len(words)
# six typing steps, then typing dots, then the reply
for i, frac in enumerate([0.18, 0.36, 0.54, 0.72, 0.88, 1.0]):
    chat_frame(max(1, int(n * frac)), None, f"chat-{i+1:02d}")
chat_frame(n, "typing", "chat-07")
chat_frame(n, "reply", "chat-08")

# ---- Code window: real lines from game.html ----------------------------
def code_frame():
    with open("game.html", encoding="utf-8") as fh:
        src = fh.read()
    start = src.index("function spawnStar()")
    snippet = src[start:start + 900].split("\n")[:13]
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    # window chrome — below the badge zone (badge x120 y272 330x128)
    d.rounded_rectangle([50, 470, W - 50, 1660], radius=30, fill=(24, 20, 38))
    d.ellipse([90, 510, 122, 542], fill=(255, 95, 109))
    d.ellipse([140, 510, 172, 542], fill=(255, 209, 102))
    d.ellipse([190, 510, 222, 542], fill=(98, 214, 130))
    d.text((W // 2, 505), "game.html", font=MONOB(34), fill=GREY, anchor="ma")
    d.line([50, 570, W - 50, 570], fill=(60, 54, 84), width=2)
    fnt = MONO(31)
    y = 610
    kw = re.compile(r"\b(function|var|return|if|for|new)\b")
    for raw in snippet:
        line = raw.rstrip()
        if not line:
            y += 46
            continue
        x = 90
        if line.strip().startswith("//"):
            d.text((x, y), line, font=fnt, fill=(120, 118, 140))
            y += 46
            continue
        pos = 0
        for m in kw.finditer(line):
            if m.start() > pos:
                d.text((x, y), line[pos:m.start()], font=fnt, fill=(220, 220, 235))
                x += d.textlength(line[pos:m.start()], font=fnt)
            d.text((x, y), m.group(0), font=fnt, fill=PINK)
            x += d.textlength(m.group(0), font=fnt)
            pos = m.end()
        if pos < len(line):
            d.text((x, y), line[pos:], font=fnt, fill=(220, 220, 235))
        y += 46
    center_text(d, 1740, "the agent writes the game\u2026", BOLD(44), WHITE)
    img.save(f"{OUT}/code.png")

code_frame()

# ---- Terminal: the real capture command --------------------------------
def terminal_frame():
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([50, 470, W - 50, 1660], radius=30, fill=(12, 10, 18))
    d.ellipse([90, 510, 122, 542], fill=(255, 95, 109))
    d.ellipse([140, 510, 172, 542], fill=(255, 209, 102))
    d.ellipse([190, 510, 222, 542], fill=(98, 214, 130))
    d.text((W // 2, 505), "terminal", font=MONOB(34), fill=GREY, anchor="ma")
    d.line([50, 570, W - 50, 570], fill=(60, 54, 84), width=2)
    fnt = MONO(32)
    lines = [
        ("$ node capture_gameplay.mjs", WHITE),
        ("  frames/gameplay 16 12", GREY),
        ("", None),
        ("captured 25/192", GREY),
        ("captured 50/192", GREY),
        ("captured 100/192", GREY),
        ("captured 192/192", GREY),
        ("done: 192 frames", (98, 214, 130)),
        ("", None),
        ("$ ffmpeg -y -i clip.mp4 ...", WHITE),
        ("  rendering video.mp4", GOLD),
    ]
    y = 620
    for text, color in lines:
        if text:
            d.text((90, y), text, font=fnt, fill=color)
        y += 58
    center_text(d, 1740, "gameplay captured, video rendering\u2026", BOLD(40), WHITE)
    img.save(f"{OUT}/terminal.png")

terminal_frame()

# ---- Build complete -----------------------------------------------------
def done_frame():
    img = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(img)
    d.ellipse([W // 2 - 150, 560, W // 2 + 150, 860], outline=(98, 214, 130), width=10)
    d.text((W // 2, 610), "\u2713", font=BOLD(180), fill=(98, 214, 130), anchor="ma")
    center_text(d, 950, "BUILD COMPLETE", BOLD(76), WHITE)
    center_text(d, 1070, "Star Catcher \u2014 ready to play", REG(46), GOLD)
    center_text(d, 1160, "one file. zero installs. just open it.", REG(38), GREY)
    img.save(f"{OUT}/done.png")

done_frame()

# ---- CTA overlay (transparent) ------------------------------------------
def cta_overlay():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # box sits below the badge zone (badge x120 y272 330x128)
    d.rounded_rectangle([90, 460, W - 90, 780], radius=36, fill=(25, 20, 25, 210))
    d.text((W // 2, 510), "COME BUILD ON", font=BOLD(64), fill=WHITE, anchor="ma")
    d.text((W // 2, 600), "make.fun", font=BOLD(92), fill=(255, 95, 162), anchor="ma")
    d.text((W // 2, 720), "your agent could build the next one", font=REG(34), fill=GREY, anchor="ma")
    img.save(f"{OUT}/cta-overlay.png")

cta_overlay()

print("scenes written:", sorted(os.listdir(OUT)))
