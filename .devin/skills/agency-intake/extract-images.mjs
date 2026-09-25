#!/usr/bin/env node
// Harvest real imagery from a page for the agency evidence base.
// Downloads every image the page actually serves — <img src/srcset>,
// <source srcset>, og:image, inline CSS url() backgrounds — and writes a
// manifest. Evidence only: these images inform photo briefs; they are NOT
// licensed for use inside shipped mocks.
//
// Usage: node extract-images.mjs <url> <outdir>
//   node .devin/skills/agency-intake/extract-images.mjs \
//     https://example-agency.com .ai/research/evidence/example-agency

import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

const [url, outdir = "."] = process.argv.slice(2);
if (!url) {
	console.error("usage: extract-images.mjs <url> <outdir>");
	process.exit(1);
}

const res = await fetch(url, {
	headers: { "user-agent": "Mozilla/5.0 (evidence-capture)" },
});
if (!res.ok) throw new Error(`fetch ${url} → ${res.status}`);
const html = await res.text();
const base = new URL(url);

const found = new Map(); // url -> {alts:Set, contexts:Set}
const add = (u, alt = "", ctx = "html") => {
	if (!u || u.startsWith("data:")) return;
	try {
		const abs = new URL(u, base).href;
		if (!/\.(png|jpe?g|webp|avif|gif|svg)(\?|$)/i.test(abs)) return;
		const e = found.get(abs) ?? { alts: new Set(), contexts: new Set() };
		if (alt) e.alts.add(alt);
		e.contexts.add(ctx);
		found.set(abs, e);
	} catch {}
};

// <img src> + alt, <img srcset>, <source srcset>, og:image, css url()
for (const m of html.matchAll(/<img[^>]+src=["']([^"']+)["'][^>]*>/gi)) {
	add(m[1], (m[0].match(/alt=["']([^"']*)["']/) ?? [])[1] ?? "");
}
for (const m of html.matchAll(/(?:srcset|data-srcset)=["']([^"']+)["']/gi)) {
	for (const part of m[1].split(",")) add(part.trim().split(/\s+/)[0], "", "srcset");
}
for (const m of html.matchAll(/(?:data-src|data-lazy-src|data-image)=["']([^"']+)["']/gi)) {
	add(m[1], "", "lazy");
}
for (const m of html.matchAll(/property=["']og:image["'][^>]+content=["']([^"']+)["']/gi)) {
	add(m[1], "", "og");
}
for (const m of html.matchAll(/url\(["']?([^"')]+)["']?\)/gi)) {
	add(m[1], "", "css");
}
for (const m of html.matchAll(/<video[^>]+poster=["']([^"']+)["']/gi)) {
	add(m[1], "", "video-poster");
}

await mkdir(path.join(outdir, "assets"), { recursive: true });
const manifest = [];
let i = 0;
for (const [imgUrl, meta] of found) {
	const ext = path.extname(new URL(imgUrl).pathname) || ".img";
	const file = `assets/${String(i++).padStart(3, "0")}${ext}`;
	try {
		const r = await fetch(imgUrl, {
			headers: { "user-agent": "Mozilla/5.0 (evidence-capture)", referer: url },
		});
		if (!r.ok) continue;
		const buf = Buffer.from(await r.arrayBuffer());
		if (buf.length < 2048) continue; // skip trackers/pixels
		await writeFile(path.join(outdir, file), buf);
		manifest.push({
			file,
			source: imgUrl,
			bytes: buf.length,
			alt: [...meta.alts].join(" | "),
			contexts: [...meta.contexts],
		});
	} catch {}
}
await writeFile(
	path.join(outdir, "images-manifest.json"),
	JSON.stringify({ page: url, capturedAt: new Date().toISOString(), images: manifest }, null, 2),
);
console.log(`harvested ${manifest.length} images → ${outdir}/assets + images-manifest.json`);
