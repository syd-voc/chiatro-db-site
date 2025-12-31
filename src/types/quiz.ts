export interface Answer {
    user: string;
    result: "correct" | "wrong" | string;
}

export interface Song {
    order: number;
    videoId: string;
    title: string;
    artist?: string;
    answers: Answer[];
}

export interface Quiz {
    quizId: number;
    date?: string;
    participants?: string[];
    songs: Song[];
}

export type StaticPath = {
    params: { id: string };
    props: { quiz: Quiz };
};
