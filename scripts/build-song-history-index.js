import fs from "fs";
import path from "path";

const QUIZ_DIR = "data/quizzes";
const OUT = "data/song_history_index.json";

const index = {};

for (const file of fs.readdirSync(QUIZ_DIR)) {
    if (!file.startsWith("quiz_")) continue;

    const quiz = JSON.parse(
        fs.readFileSync(path.join(QUIZ_DIR, file), "utf-8")
    );

    for (const song of quiz.songs) {
        const winner = song.answers.find(a =>
            a.result?.startsWith("OK") || a.result?.startsWith("WIN")
        );

        const entry = {
            date: quiz.date,
            quizNo: quiz.quiz_no,
            group: quiz.group || null,
            order: song.order,
            winner: winner?.user || null
        };

        if (!index[song.contentId]) {
            index[song.contentId] = [];
        }

        index[song.contentId].push(entry);
    }
}

fs.writeFileSync(OUT, JSON.stringify(index));
console.log("song_history_index.json generated");
