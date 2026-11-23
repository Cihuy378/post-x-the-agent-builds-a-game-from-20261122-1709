// Capture real-time gameplay frames from Star Catcher via the Chrome
// DevTools Protocol. The game runs on requestAnimationFrame, which the
// --virtual-time-budget screenshot path does not drive, so this script
// talks to a live headless Chrome and grabs screenshots on a wall-clock
// schedule instead. JPEG is used because a 1080x1920 PNG capture takes
// ~0.5 s each, which would turn the clip into a timelapse; JPEG stays
// inside the frame budget. Usage:
//   node capture_gameplay.mjs <frames-dir> <seconds> <fps>
//
// Chrome must already be running with --remote-debugging-port=9222.
// Frames are written as f-0001.jpg ... The page is reloaded first so
// the capture starts at score 0.

import { writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const dir = process.argv[2] || 'frames/gameplay';
const seconds = Number(process.argv[3] || 16);
const fps = Number(process.argv[4] || 12);
const intervalMs = 1000 / fps;
const total = Math.round(seconds * fps);

mkdirSync(dir, { recursive: true });

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function findPageSocket() {
  for (let attempt = 0; attempt < 30; attempt++) {
    try {
      const res = await fetch('http://127.0.0.1:9222/json/list');
      const targets = await res.json();
      const page = targets.find((t) => t.type === 'page' && t.url.includes('game.html'));
      if (page && page.webSocketDebuggerUrl) return page.webSocketDebuggerUrl;
    } catch {
      // Chrome is still starting; retry below.
    }
    await sleep(500);
  }
  throw new Error('game page target not found on port 9222');
}

const wsUrl = await findPageSocket();
const ws = new WebSocket(wsUrl);
await new Promise((resolve, reject) => {
  ws.onopen = resolve;
  ws.onerror = (err) => reject(new Error('WebSocket failed: ' + err.message));
});

let nextId = 1;
const pending = new Map();
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    if (msg.error) reject(new Error(msg.error.message));
    else resolve(msg.result);
  }
};

function send(method, params = {}) {
  const id = nextId++;
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
  });
}

await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', {
  width: 1080, height: 1920, deviceScaleFactor: 1, mobile: false
});

// Reload the game so the capture starts at score 0, then let it settle.
await send('Page.navigate', {
  url: 'file:///home/hatch/workspace/makefun/post-x-game-build/game.html?auto=1'
});
await sleep(1200);
const started = Date.now();
for (let i = 0; i < total; i++) {
  const shot = await send('Page.captureScreenshot', { format: 'jpeg', quality: 88 });
  const name = 'f-' + String(i + 1).padStart(4, '0') + '.jpg';
  writeFileSync(join(dir, name), Buffer.from(shot.data, 'base64'));
  if ((i + 1) % 25 === 0) console.log('captured ' + (i + 1) + '/' + total);
  const due = started + (i + 1) * intervalMs;
  const wait = due - Date.now();
  if (wait > 0) await sleep(wait);
}
const elapsedMs = Date.now() - started;
console.log('done: ' + total + ' frames in ' + dir +
  ' over ' + (elapsedMs / 1000).toFixed(1) + 's (target ' + seconds + 's)');
ws.close();
process.exit(0);
