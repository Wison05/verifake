import subprocess
from pathlib import Path

# 결과 저장 폴더
VIDEO_DIR = Path("storage/video")
AUDIO_DIR = Path("storage/audio")

VIDEO_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def separate_streams(input_file: Path, job_id: str):
    video_out = VIDEO_DIR / f"{job_id}_video.mp4"
    audio_out = AUDIO_DIR / f"{job_id}_audio.wav"

    # 🎥 영상만 추출
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(input_file),
        "-an",
        "-c:v", "copy",
        str(video_out)
    ], check=True)

    # 🔊 음성만 추출 (wav)
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(input_file),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(audio_out)
    ], check=True)

    return str(video_out), str(audio_out)