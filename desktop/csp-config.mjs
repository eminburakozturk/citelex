import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const DEFAULT_API_URL = "http://127.0.0.1:8000";

export function extractApiOrigin(apiUrl) {
  if (!apiUrl || apiUrl === "same-origin") {
    return "";
  }
  try {
    return new URL(apiUrl).origin;
  } catch {
    return "";
  }
}

export function buildCspPolicy(apiOrigin) {
  const connectSrc = apiOrigin ? `'self' ${apiOrigin}` : "'self'";
  return `default-src 'self'; connect-src ${connectSrc}; img-src 'self' data:; style-src 'self' 'unsafe-inline'; font-src 'self'`;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || DEFAULT_API_URL;
  const origin = extractApiOrigin(apiUrl);
  const csp = buildCspPolicy(origin);
  const outPath = path.join(__dirname, "src-tauri", "tauri.csp.json");
  const payload = { app: { security: { csp } } };
  fs.writeFileSync(outPath, JSON.stringify(payload, null, 2) + "\n", "utf-8");
  console.log(`[citelex desktop] Wrote CSP config -> ${outPath}`);
  console.log(`[citelex desktop] CSP: ${csp}`);
}
