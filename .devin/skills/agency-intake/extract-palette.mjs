#!/usr/bin/env node
// Extract the dominant palette from a harvested image or screenshot —
// palette evidence becomes data, not eyeballing.
//
// Usage: node extract-palette.mjs <image-or-dir> [image-or-dir ...]
// Requires: npm i node-vibrant
// Output: JSON to stdout { file, swatches: [{name,hex,population}] }

import { Vibrant } from "node-vibrant/node";
import { readdir, stat } from "node:fs/promises";
import path from "node:path";

const targets = process.argv.slice(2);
if (!targets.length) {
	console.error("usage: extract-palette.mjs <image-or-dir> [...]");
	process.exit(1);
}

const IMG_RE = /\.(png|jpe?g|webp|avif)$/i;
const files = [];
for (const t of targets) {
	const s = await stat(t);
	if (s.isDirectory()) {
		for (const f of await readdir(t)) {
			if (IMG_RE.test(f)) files.push(path.join(t, f));
		}
	} else if (IMG_RE.test(t)) {
		files.push(t);
	}
}

const out = [];
for (const file of files) {
	try {
		const p = await Vibrant.from(file).getPalette();
		const swatches = Object.entries(p)
			.filter(([, sw]) => sw)
			.map(([name, sw]) => ({
				name,
				hex: sw.hex,
				population: sw.population,
			}))
			.sort((a, b) => b.population - a.population);
		out.push({ file, swatches });
	} catch (e) {
		out.push({ file, error: String(e) });
	}
}
console.log(JSON.stringify(out, null, 2));
