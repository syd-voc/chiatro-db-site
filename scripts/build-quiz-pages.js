import fs from "fs";
import path from "path";

const QUIZ_DIR = "data/quizzes";
const SONG_DIR = "data/songs";
const OUT_DIR = "data/quiz_pages";

fs.rmSync(OUT_DIR, { recursive: true, force: true });
fs.mkdirSync(OUT_DIR, { recursive: true });

/* ===== songs map ===== */

const songMap = new Map();

for (const f of fs.readdirSync(SONG_DIR)) {
    const s = JSON.parse(fs.readFileSync(path.join(SONG_DIR, f)));
    songMap.set(s.contentId, s);
}

/* ===== quizzes ===== */

for (const f of fs.readdirSync(QUIZ_DIR)) {
    if (!f.startsWith("quiz_")) continue;

    const quiz = JSON.parse(fs.readFileSync(path.join(QUIZ_DIR, f)));

    const songs = quiz.songs.map((qs) => {
        const s = songMap.get(qs.contentId);

        return {
            order: qs.order,
            contentId: qs.contentId,
            answers: qs.answers,

            song: s?.song ?? null,
            artist: s?.artist ?? [],
            thumbnailUrl: s?.thumbnailUrl ?? null,
        };
    });

    const page = {
        quiz_no: quiz.quiz_no,
        group: quiz.group,
        date: quiz.date,
        id: `${quiz.quiz_no}${quiz.group}`,
        songs,
    };

    fs.writeFileSync(
        path.join(OUT_DIR, `${page.id}.json`),
        JSON.stringify(page, null, 2)
    );
}

console.log("quiz pages built");
