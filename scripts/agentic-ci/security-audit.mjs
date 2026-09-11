/**
 * Agentic CI — Security Auditor
 *
 * Lightweight, local-only security pass. Runs npm audit, scans for common
 * secret patterns and committed .env files, and checks CORS/security headers
 * on the local staging server. Does not target production.
 */
import { execSync } from "node:child_process";
import { writeFileSync, readdirSync, readFileSync, statSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve, join } from "node:path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const BASE_URL = process.env.STAGING_BASE_URL || "http://127.0.0.1:5173";

const SECRET_PATTERNS = [
  { name: "AWS Access Key", regex: /AKIA[0-9A-Z]{16}/ },
  { name: "Private Key", regex: /-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----/ },
  { name: "Generic API key", regex: /(?:api[_-]?key|apikey)\s*[:=]\s*['""][a-zA-Z0-9_\-]{20,}['""]/i },
  { name: "Generic secret", regex: /(?:secret[_-]?key|secret_token)\s*[:=]\s*['""][a-zA-Z0-9_\-]{20,}['""]/i },
];

const SKIP_DIRS = new Set(["node_modules", ".git", "dist", "build", ".ai", ".devin"]);

function shouldSkipPath(fullPath) {
  const normalized = fullPath.replace(/\\/g, "/");
  if (normalized.includes("/.venv/")) return true;
  if (normalized.includes("/docs/ops/")) return true;
  if (normalized.endsWith(".pyc")) return true;
  return false;
}

function findFiles(dir, files = []) {
  const entries = readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (SKIP_DIRS.has(entry.name)) continue;
    const full = join(dir, entry.name);
    if (shouldSkipPath(full)) continue;
    if (entry.isDirectory()) {
      findFiles(full, files);
    } else if (entry.isFile()) {
      files.push(full);
    }
  }
  return files;
}

function scanSecrets(root) {
  const findings = [];
  const files = findFiles(root);
  for (const file of files) {
    if (file.endsWith(".env")) {
      findings.push({ file, pattern: "committed .env file", line: "" });
    }
    let text;
    try {
      text = readFileSync(file, "utf-8");
    } catch {
      continue;
    }
    const lines = text.split("\n");
    for (let i = 0; i < lines.length; i += 1) {
      for (const { name, regex } of SECRET_PATTERNS) {
        if (regex.test(lines[i])) {
          findings.push({ file, pattern: name, line: i + 1 });
        }
      }
    }
  }
  return findings;
}

function npmAudit(cwd) {
  try {
    const out = execSync("npm audit --json", { cwd, encoding: "utf-8" });
    return JSON.parse(out);
  } catch (e) {
    const out = e.stdout || "";
    try {
      return JSON.parse(out);
    } catch {
      return { error: e.message, stdout: out.slice(0, 500) };
    }
  }
}

async function checkHeaders(url) {
  const resp = await fetch(url);
  const headers = Object.fromEntries(resp.headers.entries());
  const findings = [];
  if (!headers["x-content-type-options"]) {
    findings.push("Missing X-Content-Type-Options header");
  }
  if (!headers["x-frame-options"] && !headers["content-security-policy"]) {
    findings.push("Missing X-Frame-Options or Content-Security-Policy header");
  }
  return { status: resp.status, headers, findings };
}

async function main() {
  const errors = [];

  const frontendRoot = resolve(__dirname, "../../frontend");
  const audit = npmAudit(frontendRoot);
  if (audit.metadata && audit.metadata.vulnerabilities) {
    const v = audit.metadata.vulnerabilities;
    const total = v.total ?? v.critical + v.high + v.moderate + v.low + v.info;
    if (total > 0) {
      errors.push({ type: "npm_audit", vulnerabilities: v });
    }
  }

  const secretFindings = scanSecrets(resolve(__dirname, "../.."));
  for (const finding of secretFindings) {
    errors.push({ type: "secret_scan", ...finding });
  }

  const headerCheck = await checkHeaders(BASE_URL);
  for (const finding of headerCheck.findings) {
    errors.push({ type: "security_header", finding });
  }

  const report = {
    timestamp: new Date().toISOString(),
    baseUrl: BASE_URL,
    npmAudit: audit.metadata ? audit.metadata.vulnerabilities : audit,
    headerCheck,
    secretFindings,
    errorCount: errors.length,
    errors,
    summary: errors.length === 0
      ? "No npm audit, secret, or security-header findings detected."
      : `Detected ${errors.length} security finding/s.`,
  };

  const outPath = resolve(
    __dirname,
    "../../.ai/audit/2026-09-11-agentic-security-audit.json",
  );
  writeFileSync(outPath, JSON.stringify(report, null, 2));
  console.log(report.summary);
  console.log(`Report written to ${outPath}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
