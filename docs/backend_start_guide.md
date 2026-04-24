## 빌드 과정

### 1. 파이썬 가상환경 생성 및 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. 패키지 다운

```bash
pip install -r services/backend/requirments.txt
```

### 3. 서버 실행 명령어
**실행할 떄 항상 가상환경 안에서 실행할 것**
```bash
# 환경에 따라 접속 안될 수도 있음.
# wsl은 끝에 --host 0.0.0.0 추가
uvicorn services.backend.main:app --reload
```

**Swagger: http://localhost:8000/docs**