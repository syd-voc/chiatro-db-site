import fs from "fs/promises";

const quizDir = "data/quizzes";
const songDir = "data/songs";
const userDir = "data/users";

async function countFiles(dir, filterFn) {
    const files = await fs.readdir(dir);
    return files.filter(filterFn).length;
}

const stats = {
    quizCount: await countFiles(quizDir, f => f.startsWith("quiz_") && f.endsWith(".json")),
    songCount: await countFiles(songDir, f => f.endsWith(".json")),
    userCount: await countFiles(userDir, f => f.endsWith(".json")),
};

await fs.writeFile("data/stats.json", JSON.stringify(stats, null, 2), "utf-8");

console.log("stats.json generated");
