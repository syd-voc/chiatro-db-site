/* =========================
   共通
========================= */

export type AnswerResult = "OK" | "NG" | "SKIP" | "WIN" | "LOSE";

/* =========================
   Quiz（ログ）
========================= */

export interface AnswerLog {
    user: string;          // SKIP の場合 ""
    result: AnswerResult;
}

export interface QuizSong {
    order: number;
    contentId: string;
    answers: AnswerLog[];
}

export interface Quiz {
    quiz_no: number;
    group: string;
    date: string;
    songs: QuizSong[];
}

/* =========================
   Song（マスタ）
========================= */

export interface Song {
    song: string;          // 表示用短縮名
    title: string;         // 正式タイトル
    contentId: string;
    artist: string[];
    tags: string[];

    userId?: number | null;
    channelId?: number | null;
    thumbnailUrl?: string;
    startTime?: string;
    lengthSeconds?: number;

    viewCounter?: number;
    commentCounter?: number;
    mylistCounter?: number;
    likeCounter?: number;
    rank?: number;
}
