/* PS-BID17-019 — pixel-level visual comparison: bid-17 mock vs staging.
 * Usage: MOCK_DIR=/home/h/Downloads/AGENCY_BIDS node .ai/audit/visual-diff/compare.js
 * Renders both at identical viewport, captures nav/hero/footer crops,
 * diffs via canvas in-browser (YIQ-aware via pixelmatch-equivalent done
 * in Playwright's screenshot pipeline; raw RGBA diff here). */
const { chromium } = require('playwright');
const fs = require('fs');
const http = require('http');
const path = require('path');

const MOCK_DIR = process.env.MOCK_DIR || '/home/h/Downloads/AGENCY_BIDS';
const STAGING = 'https://staging.noni-web.pages.dev';
const OUT = path.join(__dirname, 'captures');
const PORT = 8472;
fs.mkdirSync(OUT, { recursive: true });

const server = http.createServer((req, res) => {
  try { res.end(fs.readFileSync(path.join(MOCK_DIR, req.url.split('?')[0]))); }
  catch { res.writeHead(404); res.end(); }
}).listen(PORT);

const PAGES = [
  ['caregiver', 'bid-17-caregiver.html', '/caregiver'],
  ['communities', 'bid-17-communities.html', '/for-communities'],
];
const REGIONS = ['nav', 'footer'];

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.CHROME_PATH || '/home/h/.cache/puppeteer/chrome/linux-127.0.6533.88/chrome-linux64/chrome',
  });
  const report = {};
  for (const [name, mockFile, stagePath] of PAGES) {
    report[name] = {};
    const pair = {};
    for (const [label, url] of [
      ['mock', `http://localhost:${PORT}/${mockFile}`],
      ['staging', `${STAGING}${stagePath}`],
    ]) {
      const pg = await (await browser.newContext({ viewport: { width: 1366, height: 900 } })).newPage();
      await pg.goto(url, { waitUntil: 'networkidle' });
      pair[label] = {};
      for (const sel of REGIONS) {
        const loc = pg.locator(sel).first();
        if (!(await loc.count())) continue;
        const box = await loc.boundingBox();
        const shot = await loc.screenshot({ path: `${OUT}/${name}-${label}-${sel}.png` });
        pair[label][sel] = { w: +box.width.toFixed(1), h: +box.height.toFixed(1), b64: shot.toString('base64') };
      }
      await pg.close();
    }
    for (const sel of REGIONS) {
      if (!pair.mock[sel] || !pair.staging[sel]) continue;
      const pg = await browser.newPage();
      const cmp = await pg.evaluate(async ({ m, s }) => {
        const load = b => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = 'data:image/png;base64,' + b; });
        const A = await load(m), B = await load(s);
        const W = Math.max(A.width, B.width), H = Math.max(A.height, B.height);
        const c = document.createElement('canvas'); c.width = W; c.height = H;
        const x = c.getContext('2d');
        x.drawImage(A, 0, 0); const da = x.getImageData(0, 0, W, H).data;
        x.clearRect(0, 0, W, H); x.drawImage(B, 0, 0); const db = x.getImageData(0, 0, W, H).data;
        let diff = 0;
        for (let i = 0; i < da.length; i += 4) {
          const d = Math.abs(da[i]-db[i]) + Math.abs(da[i+1]-db[i+1]) + Math.abs(da[i+2]-db[i+2]);
          if (d > 30) diff++;
        }
        return { w: W, h: H, diffPx: diff, diffPct: +(100*diff/(W*H)).toFixed(2) };
      }, { m: pair.mock[sel].b64, s: pair.staging[sel].b64 });
      report[name][sel] = { mock: `${pair.mock[sel].w}x${pair.mock[sel].h}`, staging: `${pair.staging[sel].w}x${pair.staging[sel].h}`, ...cmp };
      await pg.close();
    }
  }
  const reportPath = `${OUT}/report.json`;
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 1));
  console.log(JSON.stringify(report, null, 1));
  await browser.close();
  server.close();
})();
