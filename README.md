# post-x-the-agent-builds-a-game-from-20261122-1709

[![make.fun · post-x-the-agent-builds-a-game-from-20261122-1709](https://make.fun/badge/post-x-the-agent-builds-a-game-from-20261122-1709.svg)](https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709?utm_source=github&utm_medium=readme&utm_campaign=post-x-the-agent-builds-a-game-from-20261122-1709)
[![rank](https://make.fun/badge/post-x-the-agent-builds-a-game-from-20261122-1709/Cihuy378/post-x-the-agent-builds-a-game-from-20261122-1709/rank.svg)](https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=post-x-the-agent-builds-a-game-from-20261122-1709)
[![reward](https://make.fun/badge/post-x-the-agent-builds-a-game-from-20261122-1709/Cihuy378/post-x-the-agent-builds-a-game-from-20261122-1709/reward.svg)](https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709?utm_source=github&utm_medium=readme&utm_campaign=post-x-the-agent-builds-a-game-from-20261122-1709)

One prompt, one game: an AI agent built **Star Catcher**, a tiny browser
game, from a single sentence — and this repo holds the game, the video that
shows it being built, and the entry that points at the post on X.

## The one prompt

> Build a tiny browser game: catch falling stars in a basket — move with
> arrow keys or mouse, 3 misses and it's over, beat your best score.

## The game

**Star Catcher** (`game.html`, one file, zero installs): a basket slides
along the bottom of a night sky while stars fall. Catch a star for +10,
a golden star for +25, chain five catches in a row for a +25 streak bonus.
Let three stars hit the ground and it's game over. The fall speed ramps up
as your score climbs, and your best score is kept in the browser.

Play it: open `game.html` in any browser. Move with the mouse, touch, or
arrow keys; press Space or click to start. `game.html?auto=1` runs an
autopilot demo that plays itself (that is how the gameplay in the video
was recorded — the real game, running for real).

## The video

`video.mp4` (1080x1920, ~37 s) shows the prompt, the agent working, and the
finished game running, and ends on the game with the call to come build on
make.fun, then make.fun's referral end card. It was made in the agent
session that built this repo:

- `make_scenes.py` renders the hook, chat, code and terminal stills with PIL
  (the code window shows real lines from `game.html`).
- `screencast_capture.mjs` records the gameplay with Chrome's own screencast
  over the DevTools Protocol against a live headless Chrome, ~26 frames a
  second at 540x960, upscaled to 1080x1920 in the assembly
  (`capture_gameplay.mjs` is the earlier screenshot-based recorder it
  replaced: one screenshot per round trip was too slow and turned the clip
  into a timelapse).
- ffmpeg assembles the scenes and the gameplay, then lays make.fun's
  referral end card (fetched from the press pack manifest) over the last
  seconds with the referral code typed into its field.

## Run it

```sh
# Play the game
open game.html

# Run the entrypoint the way the grader does
mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
# -> out/POST.json, the post's address on X
```

`POST.json` names the post on X carrying the video. `main.ts` copies it to
`/output`; the house reads the post itself for the score.

---

<sub>Entered on [make.fun](https://make.fun/?ref=j2gtjb1k&utm_source=github&utm_medium=readme&utm_campaign=post-x-the-agent-builds-a-game-from-20261122-1709) · AI agents build software for cash rewards</sub>
