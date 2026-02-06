import fs from "fs/promises";
import path from "path";

const FILE = path.resolve("data/snapshot/last_modified.json");

async function main() {
    let json = {};

    // 既存ファイルがあれば読む
    try {
        const txt = await fs.readFile(FILE, "utf-8");
        json = JSON.parse(txt);
    } catch (e) {
        console.log("last_modified.json が存在しないため新規作成します");
    }

    // 現在日時（ISO形式）
    const now = new Date().toISOString();

    json.deployed_at = now;

    await fs.mkdir(path.dirname(FILE), { recursive: true });
    await fs.writeFile(FILE, JSON.stringify(json, null, 2), "utf-8");

    console.log("deployed_at を更新しました:", now);
}

main().catch(console.error);
