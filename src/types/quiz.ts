export type AnswerResult = "OK" | "NG" | "SKIP" | "WIN" | "LOSE";

export type SongHistory = {
    date: string;
    quizNo: number;
    group?: string;
    order: number;
    winner?: string;
};

export interface Answer {
    user: string;
    result: AnswerResult;
}

export interface QuizSong {
    order: number;
    contentId: string;
    answers: Answer[];
}

export interface Quiz {
    quiz_no: number;
    group: string;
    date: string;
    songs: QuizSong[];
}

export interface Song {
    song: string;
    contentId: string;
    title: string;
    artist: string[];
    tags: string[];

    startTime?: string;

    viewCounter?: number;
    commentCounter?: number;
    likeCounter?: number;
    mylistCounter?: number;
    lengthSeconds?: number;
    rank?: number;

    thumbnailUrl?: string;
}
