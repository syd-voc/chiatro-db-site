import fs from "fs/promises";
import path from "path";

const FILE = path.resolve("data/snapshot/last_modified.json");

/* JST ISO文字列を作る */
function nowJSTISOString() {
    const now = new Date();

    // UTC → JST (+9h)
    const jst = new Date(now.getTime() + 9 * 60 * 60 * 1000);

    const yyyy = jst.getUTCFullYear();
    const mm = String(jst.getUTCMonth() + 1).padStart(2, "0");
    const dd = String(jst.getUTCDate()).padStart(2, "0");
    const hh = String(jst.getUTCHours()).padStart(2, "0");
    const mi = String(jst.getUTCMinutes()).padStart(2, "0");
    const ss = String(jst.getUTCSeconds()).padStart(2, "0");

    return `${yyyy}-${mm}-${dd}T${hh}:${mi}:${ss}+09:00`;
}

async function main() {
    let json = {};

    try {
        const txt = await fs.readFile(FILE, "utf-8");
        json = JSON.parse(txt);
    } catch {
        console.log("last_modified.json を新規作成します");
    }

    const now = nowJSTISOString();
    json.deployed_at = now;

    await fs.mkdir(path.dirname(FILE), { recursive: true });
    await fs.writeFile(FILE, JSON.stringify(json, null, 2), "utf-8");

    console.log("deployed_at (JST) を更新:", now);
}

main().catch(console.error);
