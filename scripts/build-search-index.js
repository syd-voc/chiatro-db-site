import fs from "fs";
import path from "path";

const SONG_DIR = "data/songs";
const ARTIST_DIR = "data/artists";
const USER_DIR = "data/users";

function readAll(dir) {
    return fs.readdirSync(dir).map(f =>
        JSON.parse(fs.readFileSync(path.join(dir, f), "utf8"))
    );
}

const songs = readAll(SONG_DIR).map(s => ({
    id: s.contentId,
    song: s.song,
    artist: s.artist.join(" ")
}));

const artists = readAll(ARTIST_DIR).map(a => ({
    name: a.artist,
    slug: a.slug
}));

const users = readAll(USER_DIR).map(u => ({
    name: u.user,
    slug: u.slug
}));

fs.writeFileSync(
    "data/search_index.json",
    JSON.stringify({ songs, artists, users })
);

console.log("search_index.json built");
