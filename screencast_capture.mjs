// Record the game in real time with Chrome's own screencast (CDP
// Page.startScreencast). Round-trip Page.captureScreenshot calls cost
// ~0.7 s each on this box, which turned the clip into a timelapse; the
// screencast streams frames from the compositor instead, evenly spaced
// in real time. Usage:
//   node screencast_capture.mjs <frames-dir> <seconds> <every-nth-frame>
//
// Chrome must already be running with --remote-debugging-port=9222.
// Frames are written as f-0001.jpg ... plus frames.json with the
// timestamp of each frame. The page is reloaded first so the recording
// starts at score 0. Width/height come from env CAPTURE_W/CAPTURE_H
// (default 1080x1920); a smaller frame captures faster on a slow box
// and is upscaled back in the video assembly.

import { writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const dir = process.argv[2] || 'frames/gameplay3';
const seconds = Number(process.argv[3] || 16);
const everyNth = Number(process.argv[4] || 4);
const capW = Number(process.env.CAPTURE_W || 1080);
const capH = Number(process.env.CAPTURE_H || 1920);

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
const stamps = [];
let count = 0;
let recording = false;
const startedAt = { t: 0 };

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    if (msg.error) reject(new Error(msg.error.message));
    else resolve(msg.result);
    return;
  }
  if (msg.method === 'Page.screencastFrame' && recording) {
    count++;
    const name = 'f-' + String(count).padStart(4, '0') + '.jpg';
    writeFileSync(join(dir, name), Buffer.from(msg.params.data, 'base64'));
    stamps.push({ frame: count, t: (Date.now() - startedAt.t) / 1000 });
    ws.send(JSON.stringify({
      id: nextId++, method: 'Page.screencastFrameAck',
      params: { sessionId: msg.params.sessionId }
    }));
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
  width: capW, height: capH, deviceScaleFactor: 1, mobile: false
});
await send('Page.navigate', {
  url: 'file:///home/hatch/workspace/makefun/post-x-game-build/game.html?auto=1'
});
await sleep(1200);

recording = true;
startedAt.t = Date.now();
await send('Page.startScreencast', {
  format: 'jpeg', quality: 85,
  maxWidth: capW, maxHeight: capH, everyNthFrame: everyNth
});
await sleep(seconds * 1000);
recording = false;
await send('Page.stopScreencast');
writeFileSync(join(dir, 'frames.json'), JSON.stringify(stamps, null, 1));
const elapsed = (Date.now() - startedAt.t) / 1000;
console.log('done: ' + count + ' frames in ' + dir +
  ' over ' + elapsed.toFixed(1) + 's = ' + (count / elapsed).toFixed(1) + ' fps');
ws.close();
process.exit(0);
