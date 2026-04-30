# AI 로컬 초기세팅 가이드

`feature/ai-refactoring` 기준으로 음성/영상 AI 파이프라인을 로컬에서 실행하기 위한 초기세팅 절차입니다.

이 문서는 **초기세팅만** 다룹니다. 실제 테스트 실행 명령은 별도 문서/검증 단계에서 다룹니다.

## 1. 기준 환경

권장 구조는 가상환경을 2개로 나누는 방식입니다.

```text
.venv-audio  # AntiDeepfake / audio stage1 전용
.venv-video  # DeepfakeBench / video stage1 전용
```

이유:

- audio는 `torch==2.6.0`, `torchaudio==2.6.0`, `fairseq`, `speechbrain`에 의존합니다.
- video는 `tensorflow`, `retina-face`, `opencv`, `torchvision`, `efficientnet-pytorch`에 의존합니다.
- 두 환경을 하나로 합치면 TensorFlow/Torch/Numpy 버전 충돌 가능성이 큽니다.

## 2. 공통 준비

repo root에서 실행합니다.

```bash
cd <verifake-repo-root>
```

필요 도구:

```text
python
pip 또는 uv
GitHub CLI(gh) 또는 브라우저 다운로드
```

시스템에 `pip`가 없거나 Python 버전을 고르기 어렵다면 `uv` 사용을 권장합니다.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

설치 후 새 터미널을 열거나 PATH를 반영합니다.

## 3. 모델 파일 배치

모델 가중치는 git에 커밋하지 않습니다. 아래 기본 경로에 직접 배치합니다.

현재 코드 기준으로 **직접 준비해야 하는 필수 가중치 파일은 2개**입니다.

```text
1. Audio AntiDeepfake: services/ai/checkpoints/audio/antideepfake/mms_300m.ckpt
2. Video EfficientNet-B4: services/ai/checkpoints/video/effnb4_best.pth
```

추가로 audio hparams 설정 파일 1개가 필요합니다. 이것은 큰 가중치 파일은 아니지만, audio wrapper 기본 경로에서 필수로 찾습니다.

```text
services/ai/antideepfake/hparams/mms_300m_audio_pipeline.yaml
```

첫 video 실행 때 `retinaface.h5`가 추가로 다운로드될 수 있지만, 이것은 현재 repo의 checkpoint 경로에 직접 배치하는 필수 파일이라기보다 `retina-face/deepface` 런타임 캐시 파일입니다.

### 3.1 Audio AntiDeepfake checkpoint

필요 가중치 파일:

```text
services/ai/checkpoints/audio/antideepfake/mms_300m.ckpt
```

현재 확인된 Release asset:

```text
repo: oocij1jl/verifake
release: audio-weights-v1
asset: mms_300m.ckpt
size: 약 1.2GB
```

GitHub CLI 사용 시:

```bash
mkdir -p services/ai/checkpoints/audio/antideepfake

gh release download audio-weights-v1 \
  --repo oocij1jl/verifake \
  -p mms_300m.ckpt \
  -D services/ai/checkpoints/audio/antideepfake
```

### 3.2 Audio hparams

필요 파일:

```text
services/ai/antideepfake/hparams/mms_300m_audio_pipeline.yaml
```

현재 코드의 기본 경로가 이 파일을 요구합니다.

만약 repo에 없다면 upstream AntiDeepfake의 `hparams/mms_300m.yaml`을 가져와서 아래 이름으로 저장합니다.

```bash
mkdir -p services/ai/antideepfake/hparams

curl -L \
  https://raw.githubusercontent.com/nii-yamagishilab/AntiDeepfake/main/hparams/mms_300m.yaml \
  -o services/ai/antideepfake/hparams/mms_300m_audio_pipeline.yaml
```

> 주의: 이 파일은 `audio_pipeline/antideepfake.py`의 기본값 `DEFAULT_HPARAMS_PATH`와 맞아야 합니다.

### 3.3 Video EfficientNet-B4 checkpoint

필요 가중치 파일:

```text
services/ai/checkpoints/video/effnb4_best.pth
```

현재 확인된 Release asset:

```text
repo: Wison05/verifake
release: video-weights-v1
asset: effnb4_best.pth
size: 약 68MB
```

GitHub CLI 사용 시:

```bash
mkdir -p services/ai/checkpoints/video

gh release download video-weights-v1 \
  --repo Wison05/verifake \
  -p effnb4_best.pth \
  -D services/ai/checkpoints/video
```

## 4. Audio 가상환경 세팅

권장 Python: **3.10 이상**

현재 audio 코드가 `str | None` 같은 Python 3.10 타입 문법을 사용합니다. Python 3.9에서도 `eval_type_backport`를 추가하면 일부 동작 가능하지만, 팀원 재현성 기준으로는 Python 3.10+가 더 안전합니다.

### uv 사용 예시

```bash
uv venv --python 3.10 .venv-audio

uv pip install --python .venv-audio/bin/python \
  'pip==24.0'

uv pip install --python .venv-audio/bin/python \
  -r services/ai/antideepfake/requirements.txt

uv pip install --python .venv-audio/bin/python \
  -r services/ai/requirements.txt \
  static-ffmpeg
```

Python 3.9를 써야 한다면 추가로 설치합니다.

```bash
uv pip install --python .venv-audio/bin/python eval_type_backport
```

### 일반 venv/pip 사용 예시

```bash
python3.10 -m venv .venv-audio
source .venv-audio/bin/activate

python -m pip install --upgrade 'pip==24.0'
python -m pip install -r services/ai/antideepfake/requirements.txt
python -m pip install -r services/ai/requirements.txt static-ffmpeg
```

`pip==24.0`을 권장하는 이유:

- `fairseq` / `omegaconf 2.0.x` metadata 문제로 최신 pip에서 설치가 깨질 수 있습니다.
- repo의 `services/ai/README.md`에도 Python 3.9 AntiDeepfake 환경에서 `pip==24.0` pin을 권장하고 있습니다.

## 5. Video 가상환경 세팅

권장 Python: **3.11 또는 3.10**

Video stage1은 아래 파일을 기준으로 설치합니다.

```text
services/backend/requirements-ai-stage1.txt
```

### uv 사용 예시

```bash
uv venv --python 3.11 .venv-video

uv pip install --python .venv-video/bin/python \
  -r services/backend/requirements-ai-stage1.txt
```

### 일반 venv/pip 사용 예시

```bash
python3.11 -m venv .venv-video
source .venv-video/bin/activate

python -m pip install --upgrade pip
python -m pip install -r services/backend/requirements-ai-stage1.txt
```

설치되는 주요 패키지:

```text
numpy
opencv-python-headless
retina-face
tensorflow
tf-keras
pyyaml
torch
torchvision
efficientnet-pytorch
Pillow
```

## 6. 첫 실행 때 추가 다운로드되는 파일

초기 pip 설치가 끝나도 첫 실행 때 추가 다운로드가 발생할 수 있습니다.

### static_ffmpeg

`static-ffmpeg`는 첫 사용 시 ffmpeg binary zip을 내려받을 수 있습니다.

예상 위치 예시:

```text
.venv-video/lib/python*/site-packages/static_ffmpeg/bin/
```

### RetinaFace weight

`retina-face`/`deepface`는 첫 face detection 때 `retinaface.h5`를 내려받을 수 있습니다.

예상 위치:

```text
~/.deepface/weights/retinaface.h5
```

따라서 “첫 테스트 시간”에는 아래가 포함될 수 있습니다.

```text
ffmpeg binary download
retinaface.h5 download
TensorFlow 초기 로딩
Torch 모델 초기 로딩
```

정확한 모델 실행 시간만 보고 싶다면, 첫 실행 다운로드가 끝난 뒤 같은 샘플을 다시 한 번 실행해서 측정하는 것이 좋습니다.

## 7. 환경변수

Backend에서 audio stage1을 subprocess로 부를 때는 `VERIFAKE_AI_PYTHON`이 필요합니다.

```bash
export VERIFAKE_AI_PYTHON="$PWD/.venv-audio/bin/python"
```

device 기본값은 CPU를 권장합니다.

```bash
export VERIFAKE_AI_DEVICE=cpu
```

GPU 사용자는 환경에 맞게 변경합니다.

```bash
export VERIFAKE_AI_DEVICE=cuda:0
```

## 8. 설치 확인 체크리스트

초기세팅 완료 후 아래 파일이 있어야 합니다.

필수 가중치 2개:

```text
services/ai/checkpoints/audio/antideepfake/mms_300m.ckpt
services/ai/checkpoints/video/effnb4_best.pth
```

필수 audio 설정 파일 1개:

```text
services/ai/antideepfake/hparams/mms_300m_audio_pipeline.yaml
```

가상환경:

```text
.venv-audio/
.venv-video/
```

패키지 import 확인:

```bash
.venv-audio/bin/python - <<'PY'
import numpy, torch, torchaudio, pydantic, soundfile
print('audio env ok')
PY

.venv-video/bin/python - <<'PY'
import numpy, cv2, torch, torchvision, tensorflow, retinaface
print('video env ok')
PY
```

## 9. 내가 로컬에서 확인한 초기세팅 시간 참고값

테스트 환경 기준 참고값입니다. 네트워크/캐시/GPU/OS에 따라 달라질 수 있습니다.

```text
uv 설치: 약 0:02
모델 가중치 다운로드: 약 2:38
Audio venv + requirements 설치: 약 1:13
Audio 추가 의존성 설치(pydantic/static-ffmpeg 등): 약 0:01
Video venv + requirements 설치: 약 1:31
```

즉, 캐시 없는 첫 세팅 기준으로는 최소 수 분 이상 걸립니다. 특히 가중치와 Torch/TensorFlow wheel 다운로드 시간이 대부분입니다.

## 10. 주의사항

- audio/video 샘플 테스트 시에는 반드시 같은 job id 쌍을 사용합니다.

```text
storage/audio/<JOB_ID>_audio.wav
storage/video/<JOB_ID>_video.mp4
```

- `storage/jobs/`, `storage/audio/`, `storage/video/`, `outputs/`는 실행 산출물이므로 PR에 포함하지 않는 것이 좋습니다.
- checkpoint `.ckpt`, `.pth` 파일은 repo에 커밋하지 말고 Release asset/외부 다운로드 방식으로 관리합니다.
- `retinaface.h5`는 첫 video 실행 때 `~/.deepface/weights/` 아래에 캐시될 수 있습니다. 이것까지 포함하면 런타임에서 쓰이는 weight성 파일은 3개처럼 보일 수 있지만, repo에 직접 배치해야 하는 필수 AI checkpoint는 위의 2개입니다.
- CPU 환경에서는 video face detection과 model inference가 오래 걸릴 수 있습니다.
