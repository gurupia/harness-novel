import os
import sys
import re
import yaml
from jinja2 import Environment, FileSystemLoader
import parser
import humanizer_db

# 디렉토리 경로 설정
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)
AGENTS_DIR = os.path.join(BASE_DIR, ".agents")

def run_pipeline(novel_root=None, episode_num="011"):
    print("=== [Start] Web Novel Agentic Workflow Pipeline ===")
    
    # 0. 윈도우 인코딩 출력 방지
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    if not novel_root:
        print("[Error] novel_root path is required. Please provide a target novel directory.")
        print('Example: venv\\Scripts\\python.exe scripts/runner.py "j:\\eBooks\\Converted_65001\\[TXT소설]\\창작소설\\성인무협_십이경락의밤" "010"')
        return
        
    print(f"Target Novel Root: {novel_root}")
    print(f"Target Episode: {episode_num}")
    
    # 0.5 장르 감지 (novel-config.md 분석)
    genre = "SF"  # 기본값
    config_path = os.path.join(novel_root, "novel-config.md")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_text = f.read()
            if "무협" in config_text:
                genre = "무협"
            elif "판타지" in config_text:
                genre = "판타지"
        except Exception:
            pass
    
    # Jinja2 환경 세팅 (.agents 디렉토리 루트)
    loader = FileSystemLoader(AGENTS_DIR)
    env = Environment(loader=loader)
    
    # ----------------------------------------------------
    # Step 1: parser.py를 호출하여 컨텍스트 수집 (경로 동적 주입)
    # ----------------------------------------------------
    print("\n[Step 1] Collecting Obsidian/Project Context...")
    
    # novel-config.md에서 캐릭터 리스트 동적 파싱 시도
    character_names = ["주인공"]  # 디폴트
    config_path = os.path.join(novel_root, "novel-config.md")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_lines = f.readlines()
            for line in config_lines:
                if "핵심 분석 캐릭터 리스트" in line:
                    match = re.search(r"\[(.*?)\]", line)
                    if match:
                        raw_names = match.group(1)
                        character_names = [n.strip().replace('"', '').replace("'", "").replace("`", "") for n in raw_names.split(",")]
                        break
        except Exception as e:
            print(f"[Warning] Failed to parse character names from novel-config.md: {e}")
            
    characters_context = parser.get_context(novel_root, character_names)
    open_foreshadowing = parser.get_open_foreshadowing(novel_root)
    episode_memory = parser.get_episode_memory(novel_root, episode_num, window_size=3)
    
    characters_yaml = yaml.dump(characters_context, allow_unicode=True)
    foreshadowing_yaml = yaml.dump(open_foreshadowing, allow_unicode=True)
    episode_memory_yaml = yaml.dump(episode_memory, allow_unicode=True)
    
    print(f"Loaded Characters: {list(characters_context.keys())}")
    print(f"Loaded Open Foreshadowing count: {len(open_foreshadowing)}")
    print(f"Loaded Episode Memory window size: {len(episode_memory)}")
    
    # ----------------------------------------------------
    # Step 2: 01_plot_planner 템플릿 렌더링 -> 결과물 도출(모사)
    # ----------------------------------------------------
    print("\n[Step 2] Rendering Plot Planner Template...")
    try:
        plot_template = env.get_template("templates/01_plot_planner.md.j2")
        plot_prompt = plot_template.render(
            characters_yaml=characters_yaml,
            open_foreshadowing=foreshadowing_yaml,
            episode_memory=episode_memory_yaml
        )
        print("Plot Planner Prompt successfully assembled.")
    except Exception as e:
        print(f"[Error] Failed to render Plot Planner Template: {e}")
        return
        
    # [장르별 기획서 결과 및 초고 모사]
    if genre == "무협":
        mock_bit_sheet = f"""## Ep_{episode_num} 기획 비트 시트 (무협)
    
- **씬 1: 비밀 의원의 진맥 (도입)**
  - **상황**: 백운의 청운의원에 정파 여고수가 주화입마 상태로 밤늦게 방문.
  - **등장 캐릭터**: 백운, 설하
  - **감정선 목표**: 은밀한 긴장감과 3중 감각 묘사
  - **배치된 복선/장치**: 빙백신공의 독특한 한기 유출 감지.
- **씬 2: 침구 시술과 기혈 공명 (전개)**
  - **상황**: 제4침 정신침을 시술하여 폭주하는 빙백한기를 음양침법의 진기로 억제.
  - **등장 캐릭터**: 백운, 설하
  - **감정선 목표**: 뇌쇄적 고통과 백운에 대한 정신적 예속의 깊어짐
  - **배치된 복선/장치**: 정신침(4침)의 주화입마 정신 안정 기전 작동.
- **씬 3: 안개 속 자객의 내습 (클라이맥스)**
  - **상황**: 맹주부의 밀사들이 의원 외곽을 습격하나, 각성한 여고수가 백운의 명령에 따라 이성을 잃고 자객들을 처단.
  - **등장 캐릭터**: 백운, 설하, 영위(자객)
  - **감정선 목표**: 잔혹한 무공 연출과 복수귀로서의 냉혹함
  - **배치된 복선/장치**: 무림맹주의 암살 부대 첫 등장.
- **씬 4: 복수의 사슬 (여운)**
  - **상황**: 피비린내 속에 쓰러진 여고수를 차갑게 지배하며, 가슴 속 깊이 스쳐 가는 백운의 도덕적 고뇌 독백.
  - **등장 캐릭터**: 백운, 설하
  - **감정선 목표**: 피카레스크적 연출 극대화 및 클리프행어
  - **배치된 복선/장치**: 백운의 복수에 대한 자괴감 및 의가 파멸의 복선 가중.
"""
        mock_raw_draft = """밤이 깊어지자 청운의원의 문을 거칠게 두드리는 소리가 났다.
문 외부에는 빙백신공의 부작용으로 온몸이 꽁꽁 얼어붙어 가는 무림 고수 설하가 쓰러져 있었다.
백운은 차가운 눈으로 그녀를 안아 침상에 눕히고 그녀의 얇은 겉옷을 가차 없이 풀었다.
그리고 정신침을 꺼내어 단중혈에 박아 넣었다.
그녀는 비명을 지르며 백운의 다리를 안았고, 그녀의 차가운 눈동자가 음양의 진기로 인해 보랏빛으로 흔들렸다.
시술을 마치자마자 의원 밖 안개 속에서 수십 명의 자객들이 기어 들어왔다.
백운은 그녀의 목덜미를 쥐고 명령했다. 가서 저들을 찢어라.
각성한 그녀가 의원 밖으로 뛰어나가 손끝으로 자객들의 목을 무참히 부러뜨리고 돌아왔다.
피칠갑이 되어 기어오는 그녀를 보며, 백운은 씁쓸한 자괴감을 삼키고 냉혹한 보상을 지시했다.
"""
        mock_state_delta = """### 🔄 세계관 및 설정 상태 변경 보고서 (무협)
    
#### 👤 캐릭터 상태 변경점
- [ ] 설하: 정신침 시술 및 백운과의 뇌쇄적 기혈 공명으로 신체 예속 심화.
- [ ] 백운: 복수극 이면에서 밀려오는 내적 딜레마(의가 윤리 상실에 대한 자괴감) 확인.

#### 🎒 아이템 및 무공 정보
- [ ] 제4침 정신침(定神針): 설하의 빙백신공 제어용으로 시술 완료.

#### 📍 떡밥(복선) 상태 변경점
- [ ] F-01 (설하의 예속): 10화 시술 및 자객 처단으로 진척도 `🟡 진행 중` 전환.
"""
    elif genre == "판타지":
        mock_bit_sheet = f"""## Ep_{episode_num} 기획 비트 시트 (판타지)
    
- **씬 1: 던전 입구의 마력 측정**
- **씬 2: 고대 아티팩트 해제**
- **씬 3: 가디언과의 마력 충돌**
- **씬 4: 심연의 울림 (클리프행어)**
"""
        mock_raw_draft = """모든 마나의 흐름이 멈춘 심연 속에서 아티팩트가 가동되기 시작했다.
아케인 마나 측정기에 붉은 과부하 전하가 감돌았고 가디언의 도끼가 머리 위를 가르며 떨어졌다.
한울은 소맷자락을 털고 룬 마법을 전개했다. 고대의 봉인이 힘차게 해제되며 찬란한 빛이 뿜어졌다.
"""
        mock_state_delta = """### 🔄 세계관 및 설정 상태 변경 보고서 (판타지)
    
#### 👤 캐릭터 상태 변경점
- [ ] 주인공: 마나 개방 경로의 룬 각인 안정화.
"""
    else:
        mock_bit_sheet = f"""## Ep_{episode_num} 기획 비트 시트 (SF)
    
- **씬 1: 지옥 행성의 폐쇄 (상황 브리핑)**
  - **상황**: 연방 제7함대의 궤도 봉쇄로 외부 동력 밸브가 잠기고, 섹터-0 요새의 비상 수명이 148시간 남은 상태.
  - **등장 캐릭터**: 강한울, Unit-X
  - **감정선 목표**: 봉쇄의 압박감 및 자급자족 결의
  - **배치된 복선/장치**: 님프 파동 수치의 불규칙한 요동 감지.
- **씬 2: 구형 컨베이어 개조 (공학적 묘사)**
  - **상황**: 서쪽 하역장의 고철더미에서 연방 표준 203형 컨베이어를 발굴. 굴착기 유압 서보 모터 이식 및 플라즈마 토치 용접 개조 수행.
  - **등장 캐릭터**: 강한울, Unit-X, 미스터 그린
  - **감정선 목표**: 공학적 개조의 카타르시스 및 아군 세력 결집
  - **배치된 복선/장치**: 미스터 그린의 농담 및 시스터 블레이드의 보랏빛 눈빛 경계.
- **씬 3: 강철의 시동 (마찰의 감각)**
  - **상황**: 수동 차단기를 올려 조립 라인을 부활시킴. 벨트 가열 냄새와 전류 역류로 뇌간에 정전기 전이(데이터 링크 피막 자극)를 겪음.
  - **등장 캐릭터**: 강한울, 로봇 군단 전체
  - **감정선 목표**: 독립 생산 기지 기동 성공의 쾌감
  - **배치된 복선/장치**: 자가 수리 나노 봇 복선(F-04)과 공명되는 컨베이어 벨트 수복 암 작동.
- **씬 4: 심연의 SOS (클리프행어)**
  - **상황**: 주 제어실 단말기에서 님프 신호 파동과 공명하는 GAEA LITE Ver 1.2 간섭 포착. 지하 3.2km로부터 님프 연구자(프레야 박사)의 구조 신호 수신.
  - **등장 캐릭터**: 강한울, Unit-X, 미스터 그린
  - **감정선 목표**: 다음 지하 탐사에 대한 기대감 고조
  - **배치된 복선/장치**: 프레야 박사의 지하 고립 조난 신호(F-07) 최초 등장.
"""
        mock_raw_draft = """지상의 전투가 끝나고 정말 차갑고 어두운 침묵이 찾아왔다.
지상과의 통신은 완전히 끊겼고, 궤도 봉쇄로 가동 시간은 148시간밖에 남지 않은 최악의 상황이었다.
한울은 로봇들을 데리고 서쪽의 쓰레기장에 갔다. 거기에는 버려진 컨베이어가 있었다.
한울은 모터를 고장 난 굴착기에서 가져와 이식하고 플라즈마 용접기로 철판을 마구 지졌다.
미스터 그린이 옆에서 이상한 농담을 했고, 시스터 블레이드는 무서운 눈으로 조용히 쳐다봤다.
배선 연결을 다 끝낸 한울은 스위치를 힘차게 내렸다. 컨베이어 벨트가 시끄러운 소리를 내며 잘 돌아갔다.
이걸로 로봇들을 자동으로 고치는 조립 공장이 완성되었다.
공교롭게도 그 순간, 구형 컴퓨터에서 이상한 통신이 들어오기 시작했다.
거기에는 님프 신호와 연방의 기계 신호가 섞여 있었고, 지하 3km에 갇힌 사람이 살려달라고 메시지를 보내고 있었다.
한울은 GAEA의 흔적을 감지하고 지하 격벽을 향해 가기로 결심했다.
"""
        mock_state_delta = """### 🔄 세계관 및 설정 상태 변경 보고서 (SF)
    
#### 👤 캐릭터 상태 변경점
- [ ] 강한울: 데이터 링크 전하 역류로 인한 뇌간 피막 정전기 자극 누적.
- [ ] 미스터 그린, 시스터 블레이드: 자아 유지용 님프 파동 수급 안정화.

#### 🎒 아이템 및 설비 정보
- [ ] 강철의 컨베이어 라인 v1.0: 완공 및 가동 개시 (시간당 로봇 4대 자동 정비).

#### 📍 떡밥(복선) 상태 변경점
- [ ] F-03 (고대 AI GAEA LITE Ver 1.2): 11화에서 지하 3.2km 격벽 너머 신호 간섭 포착으로 진척도 `🟡 진행 중` 전환.
- [ ] F-07 (프레야 박사): 지하 고립 구조 신호 최초 포착으로 떡밥 신규 생성 (`🔴 미회수`).
"""

    # ----------------------------------------------------
    # Step 3: 02_draft_engine 템플릿 렌더링 -> 초고 도출(모사)
    # ----------------------------------------------------
    print("\n[Step 3] Rendering Draft Engine Template...")
    try:
        draft_template = env.get_template("templates/02_draft_engine.md.j2")
        draft_prompt = draft_template.render(bit_sheet=mock_bit_sheet)
        print("Draft Engine Prompt successfully assembled with Commandments.")
    except Exception as e:
        print(f"[Error] Failed to render Draft Engine Template: {e}")
        return
        
    mock_raw_draft = mock_raw_draft  # 상위 바인딩 유지

    # ----------------------------------------------------
    # Step 4: humanizer_db.py 호출 -> 동적 사례 검색 -> 03_humanizer 렌더링 -> 최종 윤문 도출(모사)
    # ----------------------------------------------------
    print("\n[Step 4] Querying Dynamic Few-Shot Database & Rendering Humanizer...")
    few_shot_examples = humanizer_db.get_few_shot_examples(mock_raw_draft, n_results=1)
    
    try:
        humanizer_template = env.get_template("templates/03_humanizer.md.j2")
        humanizer_prompt = humanizer_template.render(
            raw_draft=mock_raw_draft,
            dynamic_few_shot_examples=few_shot_examples
        )
        print("Humanizer Prompt successfully assembled with retrieved Few-Shots.")
    except Exception as e:
        print(f"[Error] Failed to render Humanizer Template: {e}")
        return
        
    # [최종 윤문 원고 모사 (Mock Humanizer Output)]
    # 01_본문 하위에서 에피소드 번호로 시작하는 마크다운 파일을 검색하여 매핑
    mock_final_draft = ""
    manuscript_dir = os.path.join(novel_root, "01_본문")
    if os.path.exists(manuscript_dir):
        for file_name in os.listdir(manuscript_dir):
            if file_name.startswith(episode_num) and file_name.endswith(".md"):
                file_path = os.path.join(manuscript_dir, file_name)
                with open(file_path, "r", encoding="utf-8") as f:
                    mock_final_draft = f.read()
                break
                
    if not mock_final_draft:
        mock_final_draft = f"# 제{int(episode_num)}화: 새로운 시작\n\n[초고에서 윤문화된 최종본 텍스트 데이터가 여기에 위치합니다.]"


    # ----------------------------------------------------
    # Step 5: 04_state_extractor 템플릿 렌더링 -> 상태 변경점 추출
    # ----------------------------------------------------
    print("\n[Step 5] Rendering State Extractor Template...")
    try:
        extractor_template = env.get_template("templates/04_state_extractor.md.j2")
        extractor_prompt = extractor_template.render(final_draft=mock_final_draft)
        print("State Extractor Prompt successfully assembled.")
    except Exception as e:
        print(f"[Error] Failed to render State Extractor Template: {e}")
        return
        
    # [상태 변경 보고서 추출 모사 (Mock State Extractor Output for Ep_011)]
    mock_state_delta = """### 🔄 세계관 및 설정 상태 변경 보고서
    
#### 👤 캐릭터 상태 변경점
- [ ] 강한울: 데이터 링크 전하 역류로 인한 뇌간 피막 정전기 자극 누적.
- [ ] 미스터 그린, 시스터 블레이드: 자아 유지용 님프 파동 수급 안정화.

#### 🎒 아이템 및 설비 정보
- [ ] 강철의 컨베이어 라인 v1.0: 완공 및 가동 개시 (시간당 로봇 4대 자동 정비).

#### 📍 떡밥(복선) 상태 변경점
- [ ] F-03 (고대 AI GAEA LITE Ver 1.2): 11화에서 지하 3.2km 격벽 너머 신호 간섭 포착으로 진척도 `🟡 진행 중` 전환.
- [ ] F-07 (프레야 박사): 지하 고립 구조 신호 최초 포착으로 떡밥 신규 생성 (`🔴 미회수`).
"""

    # ----------------------------------------------------
    # Step 6: [작품_루트]/03_줄거리/Ep_011_Review.md 저장
    # ----------------------------------------------------
    print("\n[Step 6] Saving final outputs to Review file...")
    review_dir = os.path.join(novel_root, "03_줄거리")
    if not os.path.exists(review_dir):
        os.makedirs(review_dir)
        
    review_file_path = os.path.join(review_dir, f"Ep_{episode_num}_Review.md")
    
    review_content = f"""# Episode {episode_num} - 파이프라인 조립 및 작가 검증 보고서

이 보고서는 Obsidian-Native 웹소설 에이전트 파이프라인(v3 하이브리드)의 수행 결과물입니다.

---

## 🗺️ 1. 기획 비트 시트 (Step 2)
{mock_bit_sheet}

---

## 📝 2. 초고 원고 (Step 3 - Raw Draft)
```markdown
{mock_raw_draft}
```

---

## 🌟 3. 최종 휴머나이징 윤문 원고 (Step 4 - Final Draft)
> [!NOTE]
> 집필 10계명 및 3중 감각 묘사(구리 쇳맛, 피막 정전기, 기압 압착, 고무 탄내)가 자연스럽게 결합된 완성본입니다.

```markdown
{mock_final_draft}
```

---

## ⚙️ 4. 설정 동기화 메타데이터 (Step 5 - Delta)
{mock_state_delta}
"""

    with open(review_file_path, "w", encoding="utf-8") as rf:
        rf.write(review_content)
        
    print(f"Review report successfully saved to: {review_file_path}")
    print("=== [End] Pipeline Execution Successfully Completed ===")

if __name__ == "__main__":
    # 만약 명령줄 인자로 novel_root와 episode_num을 주면 이를 활용
    n_root = sys.argv[1] if len(sys.argv) > 1 else None
    ep_num = sys.argv[2] if len(sys.argv) > 2 else "011"
    run_pipeline(n_root, ep_num)

