// Pre-commit guard: prevent raw `axios.<verb>(...)` calls that bypass
// the shared `apiClient` interceptor (which attaches the Clerk Bearer
// token). Calls without the interceptor silently send unauthenticated
// requests, surfacing as confusing 401s in the UI.
//
// Detects: axios.get(, axios.post(, axios.put(, axios.patch(,
//          axios.delete(, axios.request(, axios.head(, axios.options(
// Allows:  axios.create, axios.isAxiosError, axios.CancelToken, etc.
//
// Opt-out: append `// noqa: raw-axios-allowed` to the offending line
//          (intended for unauthenticated public endpoints like the
//          landing page, or for the apiClient definition itself).

const fs = require("fs");
const path = require("path");

const ROOT = path.join("frontend", "src");
const VERB_PATTERN =
  /\baxios\.(get|post|put|patch|delete|request|head|options)\s*\(/;
const ALLOW_MARKER = "noqa: raw-axios-allowed";
const FILE_EXT = /\.(ts|tsx|js|jsx)$/;

function walk(dir, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const name of fs.readdirSync(dir)) {
    const full = path.join(dir, name);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) {
      walk(full, out);
    } else if (FILE_EXT.test(name)) {
      out.push(full);
    }
  }
  return out;
}

const errors = [];
for (const file of walk(ROOT)) {
  const lines = fs.readFileSync(file, "utf8").split(/\r?\n/);
  lines.forEach((line, i) => {
    if (VERB_PATTERN.test(line) && !line.includes(ALLOW_MARKER)) {
      errors.push(
        `${file}:${i + 1}: raw axios call \u2014 use apiClient or annotate ` +
          `with '// ${ALLOW_MARKER}'`
      );
    }
  });
}

if (errors.length > 0) {
  console.log("\n\u274c Raw axios usage outside apiClient:\n");
  console.log(errors.join("\n"));
  process.exit(1);
}
console.log("\u2705 Axios usage safe");
