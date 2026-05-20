# ✍️ Obsidian-Native 웹소설 에이전트 하네스 (Harness Novel Engine)

본 프로젝트는 작가의 개별 마크다운(Obsidian) 환경에서 세계관 설정, 복선(떡밥) 추적 대장, 인물 설정, 에피소드 요약을 에이전트 파이프라인과 직접 연계하여 고품질의 장편 소설을 연속 집필하고 검증할 수 있도록 돕는 **하이브리드 에이전트 하네스 템플릿 엔진**입니다.

---

## 🚀 1. 원클릭 퀵스타트 (Quick Start)

새로운 컴퓨터나 워크스페이스 환경에서 아래의 단 한 줄 명령어를 터미널(PowerShell)에 입력하면 저장소 복제부터 가상환경 및 필수 라이브러리 설치까지 한 번에 완료됩니다.

```powershell
git clone https://github.com/gurupia/harness-novel.git && cd harness-novel && .\setup_env.bat
```

---

## 📂 2. 작품 디렉터리 표준 규격 (SSOT)

하네스가 소설 정보를 올바르게 파싱하고 상태를 역추적할 수 있도록 대상 작품의 내부 구조를 다음과 같이 규격화해 주어야 합니다.

```
매지컬사이버펑크_제로코스트의마법사/
├── novel-config.md        # 작품 메타데이터 및 분석 대상 캐릭터 매핑
├── 00_설정/
│   ├── 02_인물_및_관계도.md # 등장인물의 마크다운 세로 표(Table) 설정
│   └── 04_사이버네틱스_설정.md # 장르 특화 상세 설정 파일들
├── 01_본문/
│   ├── 001화.md           # 회차별 본문 원고 파일 (글자 수 5,500자+ 타겟)
│   └── 080화.md
└── 03_줄거리/
    ├── foreshadowing.md  # 🔴 미회수, 🟡 진행중, 🟢 회수완료 상태를 추적하는 복선 대장
    ├── episode_memory.md # 각 회차별 주요 전개 사건과 인물들의 세부 상태 전이를 추적하는 누적 대장 (SSOT 메모리 맵)
    └── Ep_080_Review.md  # 각 에피소드 완료 시 자동 생성되는 설정 변경점(Delta) 및 작가 검토서
```

* **[novel-config.md] 예시:**
  ```markdown
  - 작품명: 매지컬 사이버펑크: 제로 코스트의 마법사
  - 장르: SF, 사이버펑크, 판타지
  - 핵심 분석 캐릭터 리스트: ['주인공', '나오', '린']
  ```

---

## ⚙️ 3. 파이프라인 구동 방법 (Execution)

### 3.1 단일 회차 집필 및 프롬프트 생성 (`runner.py`)
가상환경을 활성화한 후, 스크립트 실행 시 **[작품 폴더의 절대 경로]**와 **[집필/검증할 회차 번호]**를 인자로 넘겨 기동합니다.

```powershell
# Windows PowerShell 기준 단일 회차 실행 예시
.\venv\Scripts\Activate.ps1
python scripts/runner.py "j:\eBooks\Converted_65001\[TXT소설]\창작소설\성인무협_십이경락의밤" "011"
```

### 3.2 다중 회차 순차 배치 교정 (`batch_proofreader.py`)
여러 에피소드를 일괄 품질 검증할 때, 하나의 대형 프롬프트에 쏟아붓지 않고 **1화씩 격리 및 루프 구동**하여 상태 동기화 체인을 유지하고 망각 현상을 방지합니다.

```powershell
# 11화부터 13화까지 순차 배치 QA 진행
python scripts/batch_proofreader.py "j:\eBooks\Converted_65001\[TXT소설]\창작소설\성인무협_십이경락의밤" 11 13
```

### 3.3 메타데이터 기반 초고속 설정 정합성 검증 (`metadata_validator.py`)
수십만 자의 본문 전체를 읽지 않고, 기존 축적된 에피소드 리뷰 파일들의 **Delta 설정 테이블만 정적 취합**하여 미회수 복선 및 타임라인 모순을 1초 만에 스캔하고 LLM 진단 프롬프트를 자동 생성합니다.

```powershell
# 전체 에피소드 리뷰의 Delta 데이터 통합 대조
python scripts/metadata_validator.py "j:\eBooks\Converted_65001\[TXT소설]\창작소설\성인무협_십이경락의밤"
```

---

## 🛠️ 4. 하네스 파이프라인 핵심 흐름 (PGE Pipeline)

1. **Step 1 (Context Prep & Diet):** `parser.py`가 캐릭터 아크, 미회수 복선(`foreshadowing.md`)의 실시간 상태를 동적으로 수집.
   * *토큰 최적화:* `novel-config.md`에서 이번 에피소드 집필계획에 실제로 언급/등장하는 **활성 인물(Active Characters)**만 정규식으로 동적 필터링 로딩.
   * *메모리 대장 조회:* 전체 본문을 여는 대신 `episode_memory.md`에서 **최근 3화 분량만 슬라이딩 윈도우**로 가볍게 로딩하여 입력 토큰 65% 이상 절약.
2. **Step 2 (Plot Planner):** 수집된 맥락과 미회수 복선을 엮어 4단 비트시트 기획안 생성.
3. **Step 3 (Draft Engine):** 기획안을 바탕으로 집필 10계명을 투영한 1차 초고 작성.
4. **Step 4 (Humanizer DB):** 기존 연재분 중 가장 문체가 우수한 Few-Shot을 벡터 유사도 매칭하여, 감각 묘사(오감)를 입힌 고품질 휴머나이징 윤문 수행.
5. **Step 5 (State Extractor & Sync):** 집필 결과 발생한 인물/복선 상태 변화를 분석하여 중앙 SSOT 파일들에 실시간 업데이트 동기화.
