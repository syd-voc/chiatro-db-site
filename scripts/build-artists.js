import fs from "fs";
import path from "path";

const SONG_DIR = "data/songs";
const QUIZ_DIR = "data/quizzes";
const OUT_DIR = "data/artists";
const ARTIST_SLUG_OUT = "data/artists_slug.json";

fs.rmSync(OUT_DIR, { recursive: true, force: true });
fs.mkdirSync(OUT_DIR, { recursive: true });

/* ---------- load songs ---------- */

const songs = fs.readdirSync(SONG_DIR)
    .map(f => JSON.parse(fs.readFileSync(path.join(SONG_DIR, f))));

/* ---------- load quizzes ---------- */

const quizzes = fs.readdirSync(QUIZ_DIR)
    .filter(f => f.startsWith("quiz_"))
    .map(f => JSON.parse(fs.readFileSync(path.join(QUIZ_DIR, f))));

/* ---------- artist map ---------- */

const artistMap = new Map();

songs.forEach(song => {
    song.artist.forEach(a => {
        if (!artistMap.has(a)) {
            artistMap.set(a, {
                artist: a,
                songs: [],
                songIdSet: new Set()
            });
        }
        artistMap.get(a).songs.push(song);
        artistMap.get(a).songIdSet.add(song.contentId);
    });
});

/* ---------- slug helper ---------- */

const artistSlugMap = {};
const usedSlugs = new Set();

function makeSlug(name) {
    let slug = encodeURIComponent(name).replaceAll("%", "G");

    let base = slug;
    let i = 2;

    while (usedSlugs.has(slug)) {
        slug = `${base}-${i++}`;
    }

    usedSlugs.add(slug);
    return slug;
}

/* ---------- build per artist ---------- */

for (const [artist, data] of artistMap) {

    const idSet = data.songIdSet;

    /* 出題回数 */
    const appearanceMap = new Map();

    /* 正解数 */
    const userCorrect = new Map();

    quizzes.forEach(q => {
        q.songs.forEach(qs => {
            if (!idSet.has(qs.contentId)) return;

            appearanceMap.set(
                qs.contentId,
                (appearanceMap.get(qs.contentId) || 0) + 1
            );

            qs.answers.forEach(a => {
                if (a.result.startsWith("OK") || a.result.startsWith("WIN")) {
                    userCorrect.set(
                        a.user,
                        (userCorrect.get(a.user) || 0) + 1
                    );
                }
            });
        });
    });

    const songRows = data.songs.map(s => ({
        contentId: s.contentId,
        title: s.song,
        startTime: s.startTime ?? null,
        viewCounter: s.viewCounter ?? null,
        appearanceCount: appearanceMap.get(s.contentId) || 0
    }));

    songRows.sort((a, b) => b.appearanceCount - a.appearanceCount);

    const topUsers = [...userCorrect.entries()]
        .map(([user, count]) => ({ user, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10);

    const slug = makeSlug(artist);
    artistSlugMap[artist] = slug;


    fs.writeFileSync(
        `${OUT_DIR}/${slug}.json`,
        JSON.stringify({
            artist,
            slug,
            songs: songRows,
            topUsers
        }, null, 2)
    );
}

console.log("artists done");

fs.writeFileSync(
    ARTIST_SLUG_OUT,
    JSON.stringify(artistSlugMap, null, 2)
);

console.log("Artist slug map written.");

