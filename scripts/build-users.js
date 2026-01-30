import fs from "fs";
import path from "path";

/* =========================
   パス設定
========================= */

const QUIZ_DIR = "data/quizzes";
const SONG_DIR = "data/songs";
const OUTPUT_DIR = "data/users";

fs.mkdirSync(OUTPUT_DIR, { recursive: true });

/* =========================
   定数
========================= */

const VIEW_RANGES = [
    { order: 0, key: "-1万", min: 0, max: 9_999 },
    { order: 1, key: "1-10万", min: 10_000, max: 99_999 },
    { order: 2, key: "10-30万", min: 100_000, max: 299_999 },
    { order: 3, key: "30-50万", min: 300_000, max: 499_999 },
    { order: 4, key: "50-100万", min: 500_000, max: 999_999 },
    { order: 5, key: "100-200万", min: 1_000_000, max: 1_999_999 },
    { order: 6, key: "200-300万", min: 2_000_000, max: 2_999_999 },
    { order: 7, key: "300-500万", min: 3_000_000, max: 4_999_999 },
    { order: 8, key: "500-1000万", min: 5_000_000, max: 9_999_999 },
    { order: 9, key: "1000万-", min: 10_000_000, max: Infinity },
];

/* =========================
   util
========================= */

function isCorrect(result) {
    return result.startsWith("OK") || result.startsWith("WIN");
}

function getEra(startTime) {
    if (!startTime) return null;

    const year = new Date(startTime).getFullYear();

    if (year <= 2008) return "2007-2008";
    if (year >= 2025) return "2025-";
    return String(year);
}

function getViewRange(viewCount) {
    const range = VIEW_RANGES.find(
        (r) => viewCount >= r.min && viewCount <= r.max
    );
    return range?.key ?? null;
}

function median(values) {
    if (!values.length) return null;

    const sorted = [...values].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);

    return sorted.length % 2
        ? sorted[mid]
        : Math.round((sorted[mid - 1] + sorted[mid]) / 2);
}

/* =========================
   Load songs
========================= */

const songMap = new Map();

fs.readdirSync(SONG_DIR).forEach((file) => {
    const song = JSON.parse(
        fs.readFileSync(path.join(SONG_DIR, file), "utf-8")
    );

    songMap.set(song.contentId, song);
});

/* =========================
   Load quizzes
========================= */

const quizzes = fs
    .readdirSync(QUIZ_DIR)
    .filter((f) => f.startsWith("quiz_"))
    .map((file) =>
        JSON.parse(fs.readFileSync(path.join(QUIZ_DIR, file), "utf-8"))
    );

/* =========================
   Collect users
========================= */

const userSet = new Set();

quizzes.forEach((quiz) => {
    quiz.songs.forEach((qs) => {
        qs.answers.forEach((a) => userSet.add(a.user));
    });
});

const users = [...userSet];

console.log(`Users: ${users.length}`);

/* =========================
   Build per user
========================= */

for (const user of users) {
    console.log("building", user);

    /* ---------- joined quizzes ---------- */

    const joinedQuizzes = quizzes.filter((quiz) =>
        quiz.songs.some((qs) =>
            qs.answers.some((a) => a.user === user)
        )
    );

    /* ---------- correct songs ---------- */

    const correctSongMap = new Map();

    quizzes.forEach((quiz) => {
        quiz.songs.forEach((qs) => {
            const song = songMap.get(qs.contentId);
            if (!song) return;

            const correctAnswers = qs.answers.filter(
                (a) => a.user === user && isCorrect(a.result)
            );

            if (!correctAnswers.length) return;

            if (!correctSongMap.has(song.contentId)) {
                correctSongMap.set(song.contentId, {
                    contentId: song.contentId,
                    title: song.song,
                    artist: song.artist.join(", "),
                    artistList: song.artist,
                    startTime: song.startTime,
                    viewCounter: song.viewCounter ?? null,
                    correctCount: 0,
                });
            }

            correctSongMap.get(song.contentId).correctCount +=
                correctAnswers.length;
        });
    });

    const correctSongs = [...correctSongMap.values()];

    /* ---------- artist stats ---------- */

    const artistMap = new Map();

    quizzes.forEach((quiz) => {
        quiz.songs.forEach((qs) => {
            const song = songMap.get(qs.contentId);
            if (!song) return;

            const correctAnswers = qs.answers.filter(
                (a) => a.user === user && isCorrect(a.result)
            );

            if (!correctAnswers.length) return;

            song.artist.forEach((artist) => {
                if (!artistMap.has(artist)) {
                    artistMap.set(artist, {
                        artist,
                        correctCount: 0,
                        songSet: new Set(),
                    });
                }

                const stat = artistMap.get(artist);
                stat.correctCount += correctAnswers.length;
                stat.songSet.add(song.contentId);
            });
        });
    });

    const artistStats = [...artistMap.values()].map((a) => ({
        artist: a.artist,
        correctCount: a.correctCount,
        correctSongCount: a.songSet.size,
    }));

    /* ---------- era stats ---------- */

    const eraMap = new Map();

    quizzes.forEach((quiz) => {
        quiz.songs.forEach((qs) => {
            const song = songMap.get(qs.contentId);
            if (!song) return;

            const era = getEra(song.startTime);
            if (!era) return;

            const correctAnswers = qs.answers.filter(
                (a) => a.user === user && isCorrect(a.result)
            );

            if (!correctAnswers.length) return;

            if (!eraMap.has(era)) {
                eraMap.set(era, {
                    era,
                    correctCount: 0,
                    songSet: new Set(),
                });
            }

            const stat = eraMap.get(era);
            stat.correctCount += correctAnswers.length;
            stat.songSet.add(song.contentId);
        });
    });

    const eraStats = [...eraMap.values()].map((e) => ({
        era: e.era,
        correctCount: e.correctCount,
        correctSongCount: e.songSet.size,
    }));

    /* ---------- view stats ---------- */

    const viewMap = new Map();

    quizzes.forEach((quiz) => {
        quiz.songs.forEach((qs) => {
            const song = songMap.get(qs.contentId);
            if (!song) return;

            if (typeof song.viewCounter !== "number") return;

            const range = getViewRange(song.viewCounter);
            if (!range) return;

            const correctAnswers = qs.answers.filter(
                (a) => a.user === user && isCorrect(a.result)
            );

            if (!correctAnswers.length) return;

            if (!viewMap.has(range)) {
                viewMap.set(range, {
                    range,
                    correctCount: 0,
                    songSet: new Set(),
                });
            }

            const stat = viewMap.get(range);
            stat.correctCount += correctAnswers.length;
            stat.songSet.add(song.contentId);
        });
    });

    const viewStats = VIEW_RANGES.map((r) => {
        const stat = viewMap.get(r.key);
        return {
            range: r.key,
            order: r.order,
            correctCount: stat?.correctCount ?? 0,
            correctSongCount: stat?.songSet.size ?? 0,
        };
    });

    /* ---------- summary ---------- */

    let totalAnswers = 0;
    let okAnswers = 0;
    let ngAnswers = 0;
    let participatedQuizCount = 0;
    let winQuizCount = 0;
    let loseQuizCount = 0;

    const correctSongViews = [];

    joinedQuizzes.forEach((quiz) => {
        let hasWin = false;
        let hasLose = false;

        quiz.songs.forEach((qs) => {
            const song = songMap.get(qs.contentId);

            qs.answers.forEach((a) => {
                if (a.user !== user) return;

                totalAnswers++;

                if (a.result.startsWith("OK")) {
                    okAnswers++;
                    if (song?.viewCounter)
                        correctSongViews.push(song.viewCounter);
                }

                if (a.result.startsWith("WIN")) {
                    okAnswers++;
                    hasWin = true;
                }

                if (a.result === "NG") ngAnswers++;
                if (a.result === "LOSE") hasLose = true;
            });
        });

        participatedQuizCount++;

        if (hasWin) winQuizCount++;
        if (hasLose) loseQuizCount++;
    });

    const summary = {
        totalAnswers,
        okAnswers,
        ngAnswers,
        participatedQuizCount,
        winQuizCount,
        loseQuizCount,
        medianViews: median(correctSongViews),
    };

    /* ---------- scatter ---------- */

    const scatter = [];

    correctSongs.forEach((s) => {
        if (!s.startTime || typeof s.viewCounter !== "number") return;

        scatter.push({
            title: s.title,
            contentId: s.contentId,
            startTime: new Date(s.startTime).getTime(),
            viewCounter: s.viewCounter,
        });
    });

    /* ---------- output ---------- */

    fs.writeFileSync(
        path.join(OUTPUT_DIR, `${user}.json`),
        JSON.stringify(
            {
                user,
                correctSongs,
                artistStats,
                eraStats,
                viewStats,
                scatter,
                summary,
            },
            null,
            2
        )
    );
}

console.log("Done.");
