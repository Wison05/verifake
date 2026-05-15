from __future__ import annotations

from typing import Any, TypedDict

from fcm_service import send_push_notification


class AnalysisSummary(TypedDict):
    """분석 요약 정보"""
    deepfake_chance: int
    confidence: int
    consistency: int


class VideoAnalysis(TypedDict):
    """영상 분석 결과"""
    manipulation_chance: int
    suspicious_segments: list[str]
    detection_rate: int


class AudioAnalysis(TypedDict):
    """음성 분석 결과"""
    manipulation_chance: int
    suspicious_segments: list[str]
    detection_rate: int


class AIAnalysisResult(TypedDict):
    """AI 분석 전체 결과"""
    summary: AnalysisSummary
    video_analysis: VideoAnalysis
    audio_analysis: AudioAnalysis


def _build_notification_title(ai_results: AIAnalysisResult) -> str:
    """알림 제목 생성
    
    Args:
        ai_results: AI 분석 결과
        
    Returns:
        알림 제목
    """
    deepfake_chance = ai_results["summary"]["deepfake_chance"]
    
    # 위험도에 따라 제목 구분
    if deepfake_chance >= 80:
        return "🚨 높은 위험도 감지"
    elif deepfake_chance >= 50:
        return "⚠️ 의심 신호 감지"
    else:
        return "✅ 정밀 분석"


def _build_notification_body(ai_results: AIAnalysisResult) -> str:
    """알림 본문 생성
    
    Args:
        ai_results: AI 분석 결과
        
    Returns:
        알림 본문
    """
    deepfake_chance = ai_results["summary"]["deepfake_chance"]
    return f"딥페이크 가능성 {deepfake_chance}% 감지. 상세보기에서 의심 구간을 확인하세요."


def _build_extra_data(ai_results: AIAnalysisResult) -> dict[str, str]:
    """푸시 알림 상세 데이터 구성
    
    앱에서 '상세보기' 화면을 띄울 때 필요한 데이터
    
    Args:
        ai_results: AI 분석 결과
        
    Returns:
        FCM extra_data 딕셔너리
    """
    video_suspicious = ", ".join(ai_results["video_analysis"]["suspicious_segments"])
    audio_suspicious = ", ".join(ai_results["audio_analysis"]["suspicious_segments"])
    
    return {
        "deepfake_chance": str(ai_results["summary"]["deepfake_chance"]),
        "confidence": str(ai_results["summary"]["confidence"]),
        "consistency": str(ai_results["summary"]["consistency"]),
        "video_suspicious": video_suspicious,
        "video_detection_rate": str(ai_results["video_analysis"]["detection_rate"]),
        "audio_suspicious": audio_suspicious,
        "audio_detection_rate": str(ai_results["audio_analysis"]["detection_rate"]),
        "analysis_type": "detailed",
    }


def _send_analysis_notification(
    fcm_token: str,
    ai_results: AIAnalysisResult,
) -> None:
    """분석 결과 알림 발송
    
    Args:
        fcm_token: FCM 토큰
        ai_results: AI 분석 결과
        
    Raises:
        ValueError: fcm_token이 유효하지 않을 때
    """
    if not fcm_token:
        raise ValueError("FCM 토큰이 유효하지 않습니다.")
    
    title = _build_notification_title(ai_results)
    body = _build_notification_body(ai_results)
    extra_data = _build_extra_data(ai_results)
    
    send_push_notification(fcm_token, title, body, data=extra_data)


def run_total_analysis(user_id: str, fcm_token: str, ai_results: AIAnalysisResult | None = None) -> None:
    """전체 분석 실행 및 알림 발송
    
    Args:
        user_id: 사용자 ID
        fcm_token: FCM 토큰
        ai_results: AI 분석 결과 (None이면 더미 데이터 사용)
        
    Raises:
        ValueError: 입력값 검증 실패 시
    """
    if not user_id:
        raise ValueError("user_id가 필요합니다.")
    if not fcm_token:
        raise ValueError("fcm_token이 필요합니다.")
    
    print(f"{user_id}님의 영상 분석중...")

    # AI 분석 결과 (실제 연동 시에는 AI 파트에서 받음)
    if ai_results is None:
        ai_results = _get_dummy_ai_results()

    # 분석 결과 알림 발송
    _send_analysis_notification(fcm_token, ai_results)
    
    print(f"{user_id}님의 분석 알림이 발송되었습니다.")


def _get_dummy_ai_results() -> AIAnalysisResult:
    """테스트용 더미 AI 분석 결과 생성
    
    Returns:
        AI 분석 결과
    """
    return {
        "summary": {
            "deepfake_chance": 87,
            "confidence": 64,
            "consistency": 71,
        },
        "video_analysis": {
            "manipulation_chance": 91,
            "suspicious_segments": ["3:12~3:18", "5:02~5:09"],
            "detection_rate": 94,
        },
        "audio_analysis": {
            "manipulation_chance": 74,
            "suspicious_segments": ["2:45~2:51", "4:30~4:35"],
            "detection_rate": 88,
        },
    }


# ============ 테스트 코드 ============

if __name__ == "__main__":
    TEST_USER = "테스트 사용자"
    TEST_TOKEN = "test_fcm_token_value"

    print("=== 테스트 시작 ===")
    
    try:
        # 1. 더미 데이터로 전체 분석 로직 실행
        run_total_analysis(TEST_USER, TEST_TOKEN)
        print("=== ✅ 테스트 프로세스 종료 ===")
        
    except Exception as exc:
        print(f"=== ❌ 테스트 중 에러 발생: {exc} ===")