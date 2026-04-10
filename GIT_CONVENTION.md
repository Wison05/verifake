# VeriFake Git 컨벤션 가이드

---

## 목차
1. [브랜치 전략](#1-브랜치-전략)
2. [커밋 컨벤션](#2-커밋-컨벤션)
3. [PR 규칙](#3-pr-규칙)
4. [이슈 규칙](#4-이슈-규칙)
5. [프로젝트 디렉토리 구조](#5-프로젝트-디렉토리-구조)

---

## 1. 브랜치 전략

### 브랜치 종류

| 브랜치명 | 용도 |
|---|---|
| `main` | 최종 배포 브랜치. 직접 푸시 금지 |
| `develop` | 통합 개발 브랜치. 모든 feature는 여기로 머지 |
| `feature/` | 기능 개발 브랜치 |
| `fix/` | 버그 수정 브랜치 |
| `refactor/` | 리팩토링 브랜치 |

### 브랜치 네이밍 규칙

```
{타입}/{파트}/{id}/{기능}
```

**예시**
```
feature/app/kwj0175/login-screen
```

### 브랜치 흐름

```
main
 ▲
 │ (배포 시 머지)
develop ◀── feature/app/xxx
         ◀── feature/ai/xxx
         ◀── feature/backend/xxx
         ◀── feature/security/xxx
```

---

## 2. 커밋 컨벤션

### 커밋 메시지 형식

```
{타입}({파트}): {작업 내용 요약}

{본문 - 선택사항}

{꼬리말 - 선택사항}
```

### 커밋 타입

| 타입 | 설명 |
|---|---|
| `feat` | 새로운 기능 추가 |
| `fix` | 버그 수정 |
| `docs` | 문서 수정 (README, 설계문서 등) |
| `refactor` | 코드 리팩토링 (기능/버그 변경 없음) |
| `perf` | 성능 개선 |

### 파트 스코프

| 스코프 | 담당 파트 |
|---|---|
| `app` | React Native 모바일 앱 |
| `ai` | 영상/음성 탐지 모델, LLM 설명 |
| `backend` | FastAPI 백엔드 서버 |
| `security` | 보안 모듈 |
| `infra` | 인프라, Docker, CI/CD |
| `docs` | 문서 |

### 커밋 메시지 예시

```bash
# 기능 추가
feat(app): 딥페이크 탐지 결과 화면 구현
feat(ai): EfficientNet 기반 영상 딥페이크 탐지기 추가
feat(ai): Wav2Vec2 기반 음성 위조 탐지기 추가
feat(ai): GPT-4o 기반 탐지 결과 자연어 설명 생성 추가
feat(backend): 영상 업로드 및 탐지 요청 API 구현
feat(security): JWT 기반 사용자 인증 구현

# 버그 수정
fix(app): 결과 화면 렌더링 오류 수정
fix(backend): 토큰 만료 예외 처리 누락 수정

# 문서
docs(security): STRIDE 위협 모델 분석 문서 추가
docs(ai): 모델 학습 데이터셋 명세 작성

# 리팩토링
refactor(ai): 영상 전처리 파이프라인 구조 개선
```

### 커밋 메시지 규칙

- 제목은 **50자 이내**로 작성
- 제목 끝에 **마침표(.) 금지**
- 제목은 **현재형 동사**로 작성 (`추가했다` → `추가`)
- 본문이 필요할 경우 제목과 **빈 줄로 구분**
- 본문은 **무엇을, 왜** 변경했는지 설명 (어떻게는 코드로 설명)

---

## 3. PR 규칙

### PR 제목 형식

```
[{타입}][{파트}] {작업 내용 요약}
```

**예시**
```
[feat][ai] 영상 딥페이크 탐지 모델 초기 구현
[fix][backend] JWT 토큰 만료 처리 오류 수정
[docs][security] STRIDE 위협 모델 문서 추가
```

### PR 규칙

- `develop` 브랜치로 머지 시 **최소 1명 이상의 리뷰 승인** 필요
- `main` 브랜치로 머지 시 **최소 2명 이상의 리뷰 승인** 필요
- PR 단위는 **하나의 기능 또는 수정 사항**으로 최소화
- 리뷰어는 **CODEOWNERS** 기준 자동 지정
---



### 이슈 라벨

| 라벨 | 설명 |
|---|---|
| `feat` | 신규 기능 요청 |
| `bug` | 버그 리포트 |
| `docs` | 문서 작업 |
| `question` | 질문 및 논의 |
| `app` | 앱 파트 |
| `ai` | AI 파트 |
| `backend` | 백엔드 파트 |
| `security` | 보안 파트 |

### 이슈 템플릿

**기능 요청 (`.github/ISSUE_TEMPLATE/feature_request.md`)**
```markdown
---
name: 기능 요청
about: 새로운 기능을 제안합니다
labels: feat
---

## 기능 요약
<!-- 어떤 기능이 필요한지 설명해주세요 -->

## 배경 및 목적
<!-- 왜 이 기능이 필요한지 설명해주세요 -->

## 구현 아이디어
<!-- 구현 방법에 대한 아이디어가 있다면 작성해주세요 -->

## 관련 파트
- [ ] 앱
- [ ] AI
- [ ] 백엔드
- [ ] 보안
```

---

## 5. 프로젝트 디렉토리 구조

```
verifake/
├── apps/
│   └── mobile/                  # React Native 모바일 앱
│       ├── src/
│       │   ├── components/      # 공통 컴포넌트
│       │   ├── screens/         # 화면 단위 컴포넌트
│       │   ├── hooks/           # 커스텀 훅
│       │   ├── services/        # API 통신 레이어
│       │   └── utils/           # 유틸리티 함수
│       └── package.json
│
├── services/
│   ├── backend/                 # FastAPI 백엔드
│   │   ├── app/
│   │   │   ├── api/             # 라우터 (엔드포인트)
│   │   │   ├── core/            # 설정, 의존성
│   │   │   ├── models/          # DB 모델
│   │   │   └── schemas/         # Pydantic 스키마
│   │   ├── tests/
│   │   └── requirements.txt
│   │
│   ├── ai/                      # AI 탐지 서버
│   │   ├── video_detector/      # 영상 딥페이크 탐지 (ViT/EfficientNet)
│   │   ├── audio_detector/      # 음성 위조 탐지 (Wav2Vec2)
│   │   ├── explainer/           # LLM 자연어 설명 생성 (GPT-4o)
│   │   ├── preprocessing/       # 전처리 파이프라인
│   │   └── requirements.txt
│   │
│   └── security/                # 보안 모듈
│       ├── auth/                # 인증/인가 (JWT)
│       ├── audit/               # 감사 로그
│       ├── privacy/             # pHash 기반 프라이버시 보호
│       └── threat_model/        # STRIDE 위협 모델 문서
│
├── infra/                       # 인프라
│   ├── docker/                  # Dockerfile, docker-compose
│   └── ci/                      # GitHub Actions 워크플로우
│
├── docs/                        # 설계 문서
│   ├── architecture.md          # 시스템 아키텍처
│   ├── api-spec.md              # API 명세
│   └── threat-model.md          # 위협 모델
│
└── .github/
    ├── CODEOWNERS
    ├── PULL_REQUEST_TEMPLATE.md
    └── ISSUE_TEMPLATE/
        ├── feature_request.md
        └── bug_report.md
```
## 참고 자료

- [Conventional Commits 스펙](https://www.conventionalcommits.org/en/v1.0.0/)
- [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow)
- [GitHub CODEOWNERS 공식 문서](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [GitHub Issue & PR 템플릿](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)
