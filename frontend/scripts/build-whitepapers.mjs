/**
 * build-whitepapers.mjs — renders markdown whitepapers to designed PDFs.
 *
 * Design follows published best practice (Uplift, madegooddesigns,
 * helion360, Verdigris design-system research): dedicated cover page,
 * US Letter portrait, generous margins, serif body for long-form
 * research credibility + brand sans for headings, running footer with
 * brand + page number, and callout styling for key stats.
 *
 * Input:  docs/marketing/*.md (repo root)
 * Output: frontend/public/whitepapers/<slug>.pdf
 * Usage:  node scripts/build-whitepapers.mjs
 * Requires: npx playwright install chromium (one-time, local only).
 * PDFs are committed artifacts — NOT built in CI.
 */
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, basename } from "node:path";
import { chromium } from "playwright";

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = join(here, "..", "..");
const SRC = join(ROOT, "docs", "marketing");
const OUT = join(here, "..", "public", "whitepapers");

const PAPERS = [
  {
    file: "the-ai-gap-whitepaper.md",
    slug: "the-ai-gap",
    tag: "Research Brief — Market Evidence",
  },
  {
    file: "geragogy-whitepaper.md",
    slug: "geragogy-the-key-to-learning",
    tag: "Research Brief — Method",
  },
];

const esc = (s) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const inline = (s) =>
  esc(s)
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>")
    .replace(/\[([^\]]+)\]\((https?:[^)]+)\)/g, '<a href="$2">$1</a>')
    .replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1">$1</a>');

// Split off the cover fields (# title, ### subtitle, *author line*).
function splitFrontMatter(md) {
  const lines = md.split("\n");
  let title = "";
  let subtitle = "";
  let byline = "";
  const rest = [];
  for (const line of lines) {
    if (!title && line.startsWith("# ")) title = line.slice(2).trim();
    else if (title && !subtitle && line.startsWith("### "))
      subtitle = line.slice(4).trim();
    else if (
      title &&
      subtitle &&
      !byline &&
      /^\*.*\*$/.test(line.trim())
    )
      byline = line.trim().replace(/^\*|\*$/g, "");
    else rest.push(line);
  }
  return { title, subtitle, byline, body: rest.join("\n") };
}

function md2html(md) {
  const lines = md.split("\n");
  let html = "";
  let inList = false;
  for (const raw of lines) {
    const line = raw.trimEnd();
    if (/^[-*] |^\d+\. /.test(line)) {
      if (!inList) {
        html += "<ul>";
        inList = true;
      }
      html += `<li>${inline(line.replace(/^([-*]|\d+\.)\s+/, ""))}</li>`;
      continue;
    }
    if (inList) {
      html += "</ul>";
      inList = false;
    }
    if (!line) continue;
    if (line === "---") html += "<hr>";
    else if (line.startsWith("### ")) html += `<h3>${inline(line.slice(4))}</h3>`;
    else if (line.startsWith("## ")) html += `<h2>${inline(line.slice(3))}</h2>`;
    else if (line.startsWith("# ")) html += `<h1>${inline(line.slice(2))}</h1>`;
    else html += `<p>${inline(line)}</p>`;
  }
  if (inList) html += "</ul>";
  return html;
}

const CSS = `
  @page { margin: 1in; }
  * { box-sizing: border-box; }
  body {
    font-family: Georgia, "Source Serif 4", "Times New Roman", serif;
    color: #222222; background: #ffffff;
    font-size: 11.5pt; line-height: 1.5;
    max-width: 62ch; margin: 0 auto;
  }
  .cover {
    page-break-after: always;
    padding-top: 2.4in;
  }
  .cover .rule {
    width: 64px; border-top: 4px solid #4A6D5C; margin: 0 0 28px;
  }
  .cover .tag {
    font-family: "Inter", "Source Sans 3", -apple-system, sans-serif;
    font-size: 10pt; letter-spacing: 0.12em; text-transform: uppercase;
    color: #4A6D5C; margin: 0 0 10px;
  }
  .cover h1 {
    font-family: "Inter", "Source Sans 3", -apple-system, sans-serif;
    font-size: 34pt; line-height: 1.15; margin: 0 0 16px; color: #222;
    max-width: none;
  }
  .cover .subtitle {
    font-size: 13pt; line-height: 1.5; color: #444; margin: 0 0 28px;
    max-width: 52ch;
  }
  .cover .byline {
    font-family: "Inter", "Source Sans 3", -apple-system, sans-serif;
    font-size: 10.5pt; color: #666; margin: 0;
  }
  h1 { display: none; } /* title lives on the cover */
  h2 {
    font-family: "Inter", "Source Sans 3", -apple-system, sans-serif;
    font-size: 15pt; line-height: 1.3; margin: 30px 0 10px; color: #222;
    border-bottom: 1px solid #ddd; padding-bottom: 6px;
    page-break-after: avoid;
  }
  h3 {
    font-family: "Inter", "Source Sans 3", -apple-system, sans-serif;
    font-size: 12pt; margin: 18px 0 6px; color: #333;
    page-break-after: avoid;
  }
  p { margin: 0 0 11px; }
  ul { margin: 0 0 14px; padding-left: 22px; }
  li { margin-bottom: 8px; }
  li strong { color: #4A6D5C; }
  a { color: #4A6FA5; text-decoration: none; word-break: break-word; }
  hr { border: none; border-top: 1px solid #ddd; margin: 30px 0; }
  strong { color: #1a1a1a; }
`;

mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage();

for (const { file, slug, tag } of PAPERS) {
  const md = readFileSync(join(SRC, file), "utf8");
  const { title, subtitle, byline, body } = splitFrontMatter(md);
  const cover = `
    <div class="cover">
      <div class="rule"></div>
      <p class="tag">${esc(tag)}</p>
      <h1 style="display:block">${inline(title)}</h1>
      <p class="subtitle">${inline(subtitle)}</p>
      <p class="byline">${inline(byline)}</p>
    </div>`;
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>${CSS}</style></head><body>${cover}${md2html(body)}</body></html>`;
  await page.setContent(html, { waitUntil: "load" });
  const out = join(OUT, `${slug}.pdf`);
  await page.pdf({
    path: out,
    format: "Letter",
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: "<span></span>",
    footerTemplate: `
      <div style="font-family:Inter,sans-serif;font-size:8pt;color:#888;
                  width:100%;padding:0 1in;display:flex;
                  justify-content:space-between;">
        <span>mynaani — ${esc(title)}</span>
        <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
      </div>`,
  });
  console.log(`built ${basename(out)}`);
}

await browser.close();
writeFileSync(
  join(OUT, "README.txt"),
  "Generated by scripts/build-whitepapers.mjs — regenerate after editing docs/marketing/*.md\n",
);
console.log("done");
