# 🎰 Lotto Auto Purchase

동행복권 자동구매 시스템 - 로또 6/45 및 연금복권 720 자동화

> [!IMPORTANT]
> 이 프로젝트는 동행복권 구매를 간편하게 도와주는 도구이며, **모든 구매 결과 및 예치금 사용에 대한 책임은 사용자 본인에게 있습니다.** 자동 구매 설정 시 신중하게 확인하시기 바랍니다.

## 📋 목차

- [기능](#-기능)
- [프로젝트 구조](#-프로젝트-구조)
- [설치](#-설치)
- [사용법](#-사용법)
- [Systemd 타이머 설정](#-systemd-타이머-설정)
- [환경 변수](#-환경-변수)
- [스크립트 설명](#-스크립트-설명)

## ✨ 기능

### 자동화된 로또 구매 워크플로우
1. **잔액 확인** - 구매가능 금액 조회
2. **조건부 충전** - 잔액 부족 시 자동 충전 (10,000원)
3. **연금복권 720 구매** - 자동 구매
4. **로또 6/45 구매** - 자동/수동 번호 선택 구매

### 주요 기능
- ✅ **완전 자동화** - Playwright 기반 브라우저 자동화
- ✅ **OCR 키패드 인식** - 랜덤 키패드 자동 입력 (Tesseract)
- ✅ **결제 금액 검증** - 구매 전 금액 확인
- ✅ **Systemd 타이머** - 매주 일요일 자동 실행
- ✅ **유연한 설정** - 커맨드라인 인자 또는 .env 파일

## 📁 프로젝트 구조

```
lotto/
├── src/                          # Python 스크립트
│   ├── balance.py               # 잔액 조회
│   ├── charge.py                # 예치금 충전 (간편 충전)
│   ├── login.py                 # 로그인 모듈
│   ├── lotto645.py              # 로또 6/45 구매
│   └── lotto720.py              # 연금복권 720 구매
├── scripts/                      # 실행 스크립트
│   ├── run-lotto.sh             # 메인 워크플로우 스크립트
│   ├── setup-env.sh             # 환경 설정 (venv, pip)
│   ├── install-systemd.sh       # Systemd 타이머 설치
│   └── systemd/                 # Systemd 설정 파일
│       ├── lotto.service        # 서비스 정의
│       └── lotto.timer          # 타이머 정의 (매주 일요일 09:00)
├── .env                          # 환경 변수 (비공개)
├── .env.example                  # 환경 변수 예시
├── requirements.txt              # Python 의존성
└── README.md                     # 이 파일
```

## 🚀 시작하기

이 프로젝트는 두 가지 방식으로 사용할 수 있습니다. 상황에 맞는 방법을 선택하세요.

1.  **Option A: 개인 서버/로컬 컴퓨터** - 내 컴퓨터나 Linux 서버(EC2, 홈서버 등)에서 직접 실행
2.  **Option B: GitHub Actions** - 서버 없이 GitHub 클라우드에서 자동 실행

---

## 🖥️ Option A: 개인 서버/로컬 컴퓨터

### 1. 설치

**저장소 클론:**
```bash
git clone https://github.com/yoonbae81/lotto.git
cd lotto
```

**환경 설정:**
```bash
cd scripts
./setup-env.sh
```
이 스크립트는 Python 가상환경 생성, 의존성 설치, 브라우저 설치, .env 파일 생성을 자동으로 수행합니다.

### 2. 환경 변수 설정

`.env` 파일을 편집하여 로또 계정 정보를 입력하세요:
```bash
nano ../.env
```

### 3. 수동 실행 (테스트)

설정이 잘 되었는지 확인하기 위해 수동으로 실행해 볼 수 있습니다.

```bash
cd ~/GitHub/lotto
source .venv/bin/activate
```

-   **잔액 확인**: `./src/balance.py`
-  #### 5. 전체 워크플로우 실행
```bash
./scripts/purchase.sh
```

### 4. 자동화 설정 (Systemd 타이머)

Linux 서버라면 Systemd를 이용해 매주 일요일 아침에 자동으로 실행되도록 설정할 수 있습니다.

**설치:**
```bash
cd scripts
./install-systemd.sh
```

**관리 명령어:**
```bash
systemctl --user status lotto.timer      # 상태 확인
systemctl --user list-timers lotto.timer # 다음 실행 시간 확인
journalctl --user -u lotto.service -f    # 로그 확인
```

---

## ☁️ Option B: GitHub Actions (서버 없음)

개인 서버가 없다면 GitHub Actions를 이용해 매주 자동으로 실행할 수 있습니다. 컴퓨터를 켜둘 필요가 없습니다.

### 1. Fork 하기
이 저장소를 본인의 GitHub 계정으로 **Fork** 하세요.

### 2. Secrets 설정

Fork한 리포지토리의 **Settings > Secrets and variables > Actions**에서 `New repository secret`을 클릭하여 다음 변수들을 추가하세요:

| Name | Value | 설명 |
|------|-------|------|
| `USER_ID` | `your_id` | 동행복권 아이디 |
| `PASSWD` | `your_password` | 동행복권 비밀번호 |
| `CHARGE_PIN` | `123456` | 충전용 PIN 6자리 |
| `AUTO_GAMES` | `3` | (선택) 자동 게임 수 |
| `MANUAL_NUMBERS` | `[[1,2,3,4,5,6]]` | (선택) 수동 번호 JSON |

### 3. 실행 확인

-   **자동 실행**: 매주 일요일 09:00 (KST)에 자동으로 실행됩니다.
-   **수동 실행**: 상단 **Actions** 탭 > **Lotto Purchase** 워크플로우 선택 > **Run workflow** 버튼 클릭.

---

## 🔧 환경 변수

### 필수 변수

| 변수 | 설명 | 예시 |
|------|------|------|
| `USER_ID` | 동행복권 아이디 | `your_id` |
| `PASSWD` | 동행복권 비밀번호 | `your_password` |
| `CHARGE_PIN` | 충전용 6자리 PIN | `123456` |

### 선택 변수

| 변수 | 설명 | 기본값 | 예시 |
|------|------|--------|------|
| `AUTO_GAMES` | 로또 6/45 자동 게임 수 | `0` | `5` |
| `MANUAL_NUMBERS` | 로또 6/45 수동 번호 (JSON) | `[]` | `[[1,2,3,4,5,6]]` |

### .env 파일 예시

```env
# 동행복권 계정 정보
USER_ID=myid
PASSWD=mypassword

# 간편충전 PIN (6자리)
CHARGE_PIN=123456

# 로또 6/45 설정
AUTO_GAMES=1
MANUAL_NUMBERS=[]

# 또는 수동 번호 지정
# MANUAL_NUMBERS=[[1,2,3,4,5,6], [7,8,9,10,11,12]]
```

## 📜 스크립트 설명

### Python 스크립트 (`src/`)

#### `balance.py`
- 예치금 잔액 및 구매가능 금액 조회
- 반환값: `{'deposit_balance': int, 'available_amount': int}`

#### `charge.py`
- 간편충전 기능 (가상계좌 입금 아님)
- OCR로 랜덤 키패드 자동 인식
- 지원 금액: 5,000원, 10,000원, 20,000원

#### `login.py`
- 공통 로그인 모듈
- 다른 스크립트에서 import하여 사용

#### `lotto645.py`
- 로또 6/45 구매
- 자동/수동 번호 선택 가능
- 결제 금액 검증

#### `lotto720.py`
- 연금복권 720 구매
- 임의의 숫자로 모든 조(組) 자동 선택
- 고정 금액: 5,000원
- 결제 금액 검증

### Shell 스크립트 (`scripts/`)

#### `setup-env.sh`
환경 설정 스크립트:
- Python 가상환경 생성
- pip 및 의존성 설치
- Playwright 브라우저 설치
- .env 파일 생성

#### `purchase.sh`
메인 워크플로우 스크립트:
1. 잔액 확인
2. 조건부 충전 (10,000원 미만 시)
3. 로또 720 구매
4. 로또 645 구매

#### `install-systemd.sh`
Systemd 타이머 설치:
- 서비스/타이머 파일 복사
- 경로 자동 설정 (`{{PROJECT_ROOT}}` 치환)
- 타이머 활성화 및 시작

#### `test.sh`
테스트 스크립트

## 🛠️ 기술 스택

- **Python 3.9+**
- **Playwright** - 브라우저 자동화
- **Tesseract OCR** - 키패드 숫자 인식
- **Pillow** - 이미지 처리
- **python-dotenv** - 환경 변수 관리
- **Systemd** - 스케줄링 (Linux)

## ⚠️ 주의사항

1. **간편 충전 사용**: 이 시스템은 [간편충전] 기능을 사용합니다. [가상계좌 입금]이 아닙니다.
2. **OCR 정확도**: 키패드 숫자 인식률은 약 90-95%입니다. 실패 시 재시도하거나 수동으로 확인하세요.
3. **Linux 전용**: Systemd 타이머는 Linux에서만 작동합니다. macOS는 launchd를 사용해야 합니다.
4. **보안**: `.env` 파일은 절대 Git에 커밋하지 마세요. `.gitignore`에 포함되어 있습니다.
5. **테스트**: 실제 사용 전 수동으로 각 스크립트를 테스트하세요.

## 🐛 트러블슈팅

### OCR 인식 실패
```bash
# Tesseract 재설치 (macOS)
brew reinstall tesseract

# Tesseract 재설치 (Ubuntu/Debian)
sudo apt-get install --reinstall tesseract-ocr
```

### Playwright 브라우저 오류
```bash
# 브라우저 재설치
.venv/bin/playwright install chromium
```

### 환경 변수 로드 안됨
```bash
# .env 파일 위치 확인
ls -la .env

# 권한 확인
chmod 600 .env
```

### Systemd 타이머 작동 안함
```bash
# 사용자 세션 유지 (로그아웃 후에도 실행)
loginctl enable-linger $USER

# 타이머 재시작
systemctl --user daemon-reload
systemctl --user restart lotto.timer
```

### GitHub Actions 자동 실행 활성화
기본적으로 `.github/workflows/purchase.yml`의 자동 실행 스케줄은 주석 처리되어 있습니다.
자동 실행을 원하면 해당 파일에서 `schedule` 부분의 주석(` # `)을 제거하세요.

**Cron 설정 참고:**
- **시간**: UTC 기준입니다 (한국 시간보다 9시간 느림).
  - 예: `30 0 * * 1` → UTC 00:30 (한국 시간 월요일 오전 09:30)
- **요일**: `0` (일요일) ~ `6` (토요일)

```yaml
# 수정 전
# schedule:
#   - cron: '0 0 * * 0'

# 수정 후
schedule:
  - cron: '0 0 * * 0'
```
