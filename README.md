# ✍️ Obsidian-Native 웹소설 에이전트 하네스 (Harness Novel Engine)

본 프로젝트는 작가의 개별 마크다운(Obsidian) 환경에서 세계관 설정, 복선(떡밥) 추적 대장, 인물 설정을 에이전트 파이프라인과 직접 연계하여 고품질의 장편 소설을 연속 집필하고 검증할 수 있도록 돕는 **하이브리드 에이전트 하네스 템플릿 엔진**입니다.

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
[내_소설_작품_폴더]/
├── novel-config.md        # 작품 메타데이터 및 분석 대상 캐릭터 매핑
├── 00_설정/
│   ├── 02_인물_및_관계도.md # 등장인물의 마크다운 세로 표(Table) 설정
│   └── 05_음양침법_상세_설정.md # 장르 특화 상세 설정 파일들
├── 01_본문/
│   ├── 001화_프롤로그.md  # 회차별 본문 원고 파일 (글자 수 5,500자+ 타겟)
│   └── 010화_비림의_사육.md
└── 03_줄거리/
    └── foreshadowing.md  # 🔴 미회수, 🟡 진행중, 🟢 회수완료 상태를 추적하는 복선 대장
```

* **[novel-config.md] 예시:**
  ```markdown
  - 작품명: 성인무협 십이경락의 밤
  - 장르: 무협, 피카레스크, 배덕
  - 핵심 분석 캐릭터 리스트: ['백운', '설하', '야화']
  ```

---

## ⚙️ 3. 파이프라인 구동 방법 (Execution)

가상환경을 활성화한 후, 스크립트 실행 시 **[작품 폴더의 절대 경로]**와 **[집필/검증할 회차 번호]**를 인자로 넘겨 기동합니다.

```powershell
# Windows PowerShell 기준 실행 예시
.\venv\Scripts\Activate.ps1
python scripts/runner.py "j:\eBooks\Converted_65001\[TXT소설]\창작소설\성인무협_십이경락의밤" "010"
```

---

## 🛠️ 4. 하네스 파이프라인 핵심 흐름 (PGE Pipeline)

1. **Step 1 (Context Prep):** `parser.py`가 설정집의 인물 표와 복선 대장(`foreshadowing.md`)의 실시간 상태를 동적으로 파싱 및 수집.
2. **Step 2 (Plot Planner):** 수집된 맥락과 미회수 복선을 엮어 4단 비트시트 기획안 생성.
3. **Step 3 (Draft Engine):** 기획안을 바탕으로 집필 10계명을 투영한 1차 초고 작성.
4. **Step 4 (Humanizer DB):** 기존 연재분 중 가장 문체가 우수한 Few-Shot을 벡터 유사도 매칭하여, 감각 묘사(오감)를 입힌 고품질 휴머나이징 윤문 수행.
5. **Step 5 (State Extractor & Sync):** 집필 결과 발생한 인물/복선 상태 변화를 분석하여 중앙 SSOT 파일들에 실시간 업데이트 동기화.
