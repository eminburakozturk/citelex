import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { DEFAULT_API_URL, extractApiOrigin } from "./csp-config.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const webDir = path.resolve(__dirname, "..", "web");
const webOutDir = path.join(webDir, "out");
const distDir = path.join(__dirname, "dist");

const apiUrl = process.env.NEXT_PUBLIC_API_URL || DEFAULT_API_URL;
const apiOrigin = extractApiOrigin(apiUrl);

if (process.env.TAURI_ENV_PLATFORM && apiOrigin && apiOrigin !== DEFAULT_API_URL) {
  const tauriConfig = process.env.TAURI_CONFIG || "";
  if (!tauriConfig.includes(apiOrigin)) {
    console.error(
      `[citelex desktop] HATA: CSP içinde API kökeni (${apiOrigin}) eksik. ` +
        `Derlemeden önce 'node csp-config.mjs' çalıştırıp '--config src-tauri/tauri.csp.json' verin.`
    );
    process.exit(1);
  }
}

function runNpm(command, targetApiUrl) {
  const res = spawnSync(command, {
    cwd: webDir,
    env: { ...process.env, NEXT_PUBLIC_API_URL: targetApiUrl },
    stdio: "inherit",
    shell: true,
  });
  if (res.status !== 0) {
    process.exit(res.status ?? 1);
  }
}

function runWebBuild(targetApiUrl) {
  console.log(`[citelex desktop] Building web/ with NEXT_PUBLIC_API_URL=${targetApiUrl}`);
  runNpm("npm run build", targetApiUrl);
}

if (!fs.existsSync(path.join(webDir, "node_modules"))) {
  runNpm("npm ci", apiUrl);
}

runWebBuild(apiUrl);

console.log("[citelex desktop] Copying web/out -> desktop/dist");
fs.rmSync(distDir, { recursive: true, force: true });
fs.cpSync(webOutDir, distDir, { recursive: true });

if (apiUrl !== "same-origin") {
  console.log("[citelex desktop] Restoring web/out with NEXT_PUBLIC_API_URL=same-origin");
  runWebBuild("same-origin");
}
