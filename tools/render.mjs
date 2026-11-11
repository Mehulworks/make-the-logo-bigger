// Renders index.html to one MP4 per scene by stepping a headless browser frame by frame.
// The page exposes window.__seek(t), so every frame is deterministic: no recording in real time.
//
//   node tools/render.mjs            render every scene
//   node tools/render.mjs 0,1,2      render only these scenes
//
// Also writes tools/timeline.json, which the audio and subtitle scripts read.
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT = path.join(ROOT, 'out');
const W = 1920, H = 1080, FPS = 30, QUALITY = 18;   // QUALITY is x264 CRF: lower is better

fs.mkdirSync(OUT, { recursive: true });
// Force sRGB so every machine renders the same colours, whatever its display profile.
const browser = await chromium.launch({ args: ['--force-color-profile=srgb'] });
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
page.on('pageerror', e => { console.error('page error:', e.message); process.exitCode = 2; });
await page.goto('file://' + path.join(ROOT, 'index.html') + '?film=1');
await page.evaluate(() => document.fonts.ready);

const timeline = await page.evaluate(() => ({ subs: window.__subs, spoken: window.__spoken, sfx: window.__sfx, cuts: window.__cuts, dur: window.__dur }));
fs.writeFileSync(path.join(ROOT, 'tools', 'timeline.json'), JSON.stringify(timeline));
const { cuts } = timeline;
const scenes = process.argv[2] ? process.argv[2].split(',').map(Number) : cuts.slice(0, -1).map((_, i) => i);

const started = Date.now();
let frames = 0;
for (const i of scenes) {
  const first = Math.round(cuts[i] * FPS), last = Math.round(cuts[i + 1] * FPS);
  const tmp = path.join(OUT, `s${i}.tmp.mp4`), done = path.join(OUT, `s${i}.mp4`);
  // JPEG frames are piped straight into ffmpeg: no PNG sequence on disk.
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-vf', 'scale=in_range=full:in_color_matrix=bt601:out_range=tv:out_color_matrix=bt709,format=yuv420p',
    '-c:v', 'libx264', '-crf', String(QUALITY), '-preset', 'veryfast', '-pix_fmt', 'yuv420p',
    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
    '-r', String(FPS), tmp], { stdio: ['pipe', 'inherit', 'inherit'] });
  const closed = new Promise(res => ff.on('close', res));

  for (let f = first; f < last; f++) {
    await page.evaluate(t => window.__seek(t), f / FPS);
    const shot = await page.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(shot)) await new Promise(r => ff.stdin.once('drain', r));
    frames++;
  }

  ff.stdin.end();
  const code = await closed;
  if (code !== 0) { console.error(`scene ${i}: ffmpeg exited ${code}`); process.exit(1); }
  fs.renameSync(tmp, done);   // rename only on success, so a killed render leaves no half file
  console.log(`scene ${i}: frames ${first}-${last - 1}  (${((Date.now() - started) / frames).toFixed(0)} ms/frame)`);
}
await browser.close();
console.log(`${frames} frames in ${((Date.now() - started) / 1000).toFixed(0)} s`);
