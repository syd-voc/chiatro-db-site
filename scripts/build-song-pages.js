import fs from "fs";
import path from "path";

const SONG_DIR = "data/songs";
const QUIZ_DIR = "data/quizzes";
const OUT_DIR = "data/song_pages";

fs.mkdirSync(OUT_DIR, { recursive: true });

/* ========= songs 読み込み ========= */

const songs = fs.readdirSync(SONG_DIR)
    .filter(f => f.endsWith(".json"))
    .map(f => JSON.parse(
        fs.readFileSync(path.join(SONG_DIR, f), "utf-8")
    ));

/* ========= quizzes 読み込み ========= */

const quizzes = fs.readdirSync(QUIZ_DIR)
    .filter(f => f.endsWith(".json"))
    .map(f => JSON.parse(
        fs.readFileSync(path.join(QUIZ_DIR, f), "utf-8")
    ));

/* ========= 曲別履歴マップ ========= */

const historyMap = new Map();

for (const q of quizzes) {
    for (const s of q.songs) {
        const winner = s.answers?.find(a =>
            a.result?.startsWith("OK") ||
            a.result?.startsWith("WIN")
        )?.user;

        const h = {
            date: q.date,
            quizNo: q.quiz_no,
            group: q.group || undefined,
            order: s.order,
            winner
        };

        if (!historyMap.has(s.contentId)) {
            historyMap.set(s.contentId, []);
        }

        historyMap.get(s.contentId).push(h);
    }
}

/* ========= ページJSON生成 ========= */

for (const song of songs) {

    const histories = historyMap.get(song.contentId) ?? [];

    histories.sort(
        (a, b) => new Date(b.date) - new Date(a.date)
    );

    const appearanceCount = histories.length;
    const correctCount = histories.filter(h => h.winner).length;
    const accuracy =
        appearanceCount === 0
            ? 0
            : Math.round(correctCount / appearanceCount * 100);

    const pageData = {
        song,
        histories,
        appearanceCount,
        correctCount,
        accuracy
    };

    fs.writeFileSync(
        path.join(OUT_DIR, `${song.contentId}.json`),
        JSON.stringify(pageData, null, 2)
    );
}

console.log("song_pages build complete");
