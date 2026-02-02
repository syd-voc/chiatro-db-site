import fs from "fs/promises";
import path from "path";

const SONG_DIR = "data/songs";
const QUIZ_DIR = "data/quizzes";
const OUT_DIR = "data/cache";

const RANGES = [
    { key: "2007-2008", from: 2007, to: 2008 },
    { key: "2009", from: 2009, to: 2009 },
    { key: "2010", from: 2010, to: 2010 },
    { key: "2011", from: 2011, to: 2011 },
    { key: "2012", from: 2012, to: 2012 },
    { key: "2013", from: 2013, to: 2013 },
    { key: "2014", from: 2014, to: 2014 },
    { key: "2015", from: 2015, to: 2015 },
    { key: "2016", from: 2016, to: 2016 },
    { key: "2017", from: 2017, to: 2017 },
    { key: "2018", from: 2018, to: 2018 },
    { key: "2019", from: 2019, to: 2019 },
    { key: "2020", from: 2020, to: 2020 },
    { key: "2021", from: 2021, to: 2021 },
    { key: "2022", from: 2022, to: 2022 },
    { key: "2023", from: 2023, to: 2023 },
    { key: "2024", from: 2024, to: 2024 },
    { key: "2025-", from: 2025, to: 3000 },
];

await fs.mkdir(OUT_DIR, { recursive: true });

/* ---------- songs 読み込み ---------- */

const songFiles = await fs.readdir(SONG_DIR);
const songs = [];

for (const f of songFiles) {
    const data = JSON.parse(
        await fs.readFile(path.join(SONG_DIR, f), "utf-8")
    );
    if (!data.startTime) continue;
    songs.push(data);
}

/* ---------- 出題回数カウント ---------- */

const countById = {};

const quizFiles = await fs.readdir(QUIZ_DIR);
for (const f of quizFiles) {
    const q = JSON.parse(
        await fs.readFile(path.join(QUIZ_DIR, f), "utf-8")
    );

    for (const s of q.songs) {
        countById[s.contentId] = (countById[s.contentId] || 0) + 1;
    }
}

/* ---------- range別出力 ---------- */

for (const r of RANGES) {
    const list = songs
        .filter((s) => {
            const y = new Date(s.startTime).getFullYear();
            return y >= r.from && y <= r.to;
        })
        .map((s) => ({
            contentId: s.contentId,
            song: s.song,
            artist: s.artist,
            count: countById[s.contentId] || 0,
        }))
        .sort((a, b) => b.count - a.count);

    await fs.writeFile(
        `${OUT_DIR}/range_${r.key}.json`,
        JSON.stringify(list)
    );
}

console.log("range stats built");
