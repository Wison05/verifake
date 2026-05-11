const DEFAULT_API_BASE_URL = 'http://localhost:8000';
const API_BASE_URL = (process.env.EXPO_PUBLIC_API_URL ?? DEFAULT_API_BASE_URL).replace(/\/$/, '');
const DEFAULT_POLL_ATTEMPTS = 120;
const DEFAULT_POLL_INTERVAL_MS = 2000;

export type MediaTaskStatus = 'PENDING' | 'DOWNLOADING' | 'PROCESSING' | 'DONE' | 'FAILED';

export interface MediaTaskResponse {
    task_id: string;
    timestamp: string;
    message: string;
}

export interface MediaTaskResult {
    task_id: string;
    status: MediaTaskStatus;
    verdict: string | null;
    video_path?: string | null;
    audio_path?: string | null;
    error?: string | null;
    timestamp: string;
}

class ApiError extends Error {
    constructor(message: string, readonly status: number) {
        super(message);
        this.name = 'ApiError';
    }
}

function getErrorMessage(payload: unknown, fallback: string): string {
    if (typeof payload !== 'object' || payload === null) {
        return fallback;
    }

    const detail = (payload as Record<string, unknown>).detail;
    if (typeof detail === 'string') {
        return detail;
    }

    const message = (payload as Record<string, unknown>).message;
    if (typeof message === 'string') {
        return message;
    }

    return fallback;
}

async function parseJsonResponse<T>(response: Response): Promise<T> {
    const payload: unknown = await response.json().catch(() => null);

    if (!response.ok) {
        throw new ApiError(getErrorMessage(payload, `HTTP ${response.status}`), response.status);
    }

    return payload as T;
}

function getFilenameFromUri(uri: string): string {
    const withoutQuery = uri.split('?')[0] ?? uri;
    const filename = withoutQuery.split('/').filter(Boolean).at(-1);
    return filename && filename.includes('.') ? filename : 'upload.mp4';
}

async function createVideoUploadBody(uri: string, title: string): Promise<FormData> {
    const fileResponse = await fetch(uri);
    if (!fileResponse.ok) {
        throw new ApiError('선택한 영상을 읽을 수 없습니다.', fileResponse.status);
    }

    const blob = await fileResponse.blob();
    const body = new FormData();
    body.append('title', title);
    body.append('videoFile', blob, getFilenameFromUri(uri));
    return body;
}

export async function uploadVideoForSeparation(uri: string, title = 'mobile-upload'): Promise<MediaTaskResponse> {
    const body = await createVideoUploadBody(uri, title);
    const response = await fetch(`${API_BASE_URL}/api/v1/video`, {
        method: 'POST',
        body,
    });

    return parseJsonResponse<MediaTaskResponse>(response);
}

export async function collectInstagramVideo(link: string, title = 'mobile-link'): Promise<MediaTaskResponse> {
    const body = new FormData();
    body.append('title', title);
    body.append('link', link);

    const response = await fetch(`${API_BASE_URL}/api/v1/instagram`, {
        method: 'POST',
        body,
    });

    return parseJsonResponse<MediaTaskResponse>(response);
}

export async function getMediaTaskStatus(taskId: string): Promise<MediaTaskResult> {
    const response = await fetch(`${API_BASE_URL}/api/v1/status/${encodeURIComponent(taskId)}`);
    return parseJsonResponse<MediaTaskResult>(response);
}

function delay(milliseconds: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

export async function waitForMediaSeparation(
    taskId: string,
    maxAttempts = DEFAULT_POLL_ATTEMPTS,
    intervalMs = DEFAULT_POLL_INTERVAL_MS,
): Promise<MediaTaskResult> {
    for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
        const result = await getMediaTaskStatus(taskId);

        if (result.status === 'DONE') {
            return result;
        }

        if (result.status === 'FAILED') {
            throw new ApiError(result.error ?? '영상/음성 분리에 실패했습니다.', 500);
        }

        await delay(intervalMs);
    }

    throw new ApiError('영상/음성 분리 결과를 기다리는 시간이 초과되었습니다.', 408);
}
