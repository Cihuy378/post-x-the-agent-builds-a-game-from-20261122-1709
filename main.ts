// Star Catcher entrypoint for make.fun's "The agent builds a game from
// one prompt" bounty.
//
// The graded entry is the X post, not this program: all main.ts does is
// hand the house the post's address by copying POST.json into the output
// directory, where the gate reads it. Node 22, standard library only,
// no network access, no clock reads — the two grader runs must produce
// identical bytes, and a plain file copy guarantees that.

import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const sourceDir = process.env.MAKEFUN_BOT_DIR ?? here;
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const postFile = join(sourceDir, 'POST.json');
if (!existsSync(postFile)) {
  console.error('POST.json is missing from ' + sourceDir);
  process.exit(1);
}

const payload = readFileSync(postFile, 'utf8');
const parsed = JSON.parse(payload); // fail loudly on malformed JSON instead of copying junk
if (typeof parsed !== 'object' || parsed === null || typeof parsed.url !== 'string') {
  console.error('POST.json must be an object with a string url field');
  process.exit(1);
}

mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, 'POST.json'), payload);
