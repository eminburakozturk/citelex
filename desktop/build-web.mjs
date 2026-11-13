import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const webDir = path.resolve(__dirname, "..", "web");

const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
const env = { ...process.env, NEXT_PUBLIC_API_URL: apiUrl };
const npmCmd = process.platform === "win32" ? "npm.cmd" : "npm";
const useShell = process.platform === "win32";

console.log(`[citelex desktop] Building web/ with NEXT_PUBLIC_API_URL=${apiUrl}`);

if (!fs.existsSync(path.join(webDir, "node_modules"))) {
  const ciRes = spawnSync(npmCmd, ["ci"], {
    cwd: webDir,
    env,
    stdio: "inherit",
    shell: useShell,
  });
  if (ciRes.status !== 0) {
    process.exit(ciRes.status ?? 1);
  }
}

const buildRes = spawnSync(npmCmd, ["run", "build"], {
  cwd: webDir,
  env,
  stdio: "inherit",
  shell: useShell,
});
process.exit(buildRes.status ?? 0);
