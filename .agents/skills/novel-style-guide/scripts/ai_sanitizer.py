# -*- coding: utf-8 -*-
import os
import sys
import re
import math
import argparse

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ======================================================================
# 🛡️ 1. 장르 및 용도별 다중 프리셋 마스터 데이터베이스 (Preset DB)
# ======================================================================
PRESETS = {
    "hardboiled": {
        "name": "현대 법정 하드보일드 노와르 (Novel Hardboiled)",
        "modifier_limit": 7.0,      # 부사/형용사 비중 7.0% 이하 엄격 통제
        "burstiness_limit": 18.0,   # 문장 리듬 다이내믹스 표준편차 18.0 이상 권장
        "buzzwords": [
            "일순간", "뇌리", "안구", "심장박", "마치 ~인 듯한", "자신의 손끝", 
            "그림자의 장막", "바벨탑", "톱니바퀴", "음지에서", "거대한 음모", 
            "사법의 신", "단죄의", "구원의", "위선 가득한", "기계 괴물",
            "유기체처럼", "소름 끼치는", "나직하게", "나지막이", "소스라치게",
            "독사 같은", "운명의 장난", "피할 수 없는", "차가운 메탈", "어둠의 족쇄",
            "영혼의 울림", "침묵의 격벽", "벼랑 끝에 선", "분노의 불꽃", "죽음의 무도",
            "거대 리밋", "오버플로우", "시스템의 굴레", "절대적인 정의", "정의의 이름으로",
            "파괴 폭발 와해", "오열 통곡", "쇠망치 폭파", "수직 다이빙", "육탄 힘껏"
        ],
        "tells": [
            r"분노했다", r"절망했다", r"경악했다", r"두려워했다", r"슬퍼했다", 
            r"분노가 치밀었다", r"절망감에", r"두려움에", r"경외감", r"슬픔이",
            r"자괴감에", r"역겨움을 느꼈다", r"엄청난 폭발", r"기괴하게 일렁이는",
            r"오열 오열", r"절규 절규", r"폭사 폭사", r"꼭대기 꼭대기", r"바닥 바닥",
            r"살의가 끓어올랐다", r"배신감에 몸서리", r"심리적 타격", r"두려움의 도가니"
        ],
        "endings": [
            r"그리하여", r"이로써", r"이것은", r"톱니바퀴들은", r"방아쇠는", 
            r"서막이", r"진실의 법정", "장막의 문은", "막을 올린다",
            r"피날레를 장식", r"대장정의 마감", r"이야기는 계속된다", r"밤은 길고 잔혹할",
            r"새로운 복수의 막", r"새벽이 도래했다", r"의미를 남긴 채", r"거대한 전쟁의 예고",
            r"대미를 장식하고", r"정식 연재", r"회차의 피날레", r"다음 부의 서막"
        ],
        "format_strict": True       # 볼드/백틱 등 마크다운 기호 금지 엄격화
    },
    
    "fantasy": {
        "name": "정통 및 퓨전 판타지 (Classic/Fusion Fantasy)",
        "modifier_limit": 9.0,      # 다소 웅장하고 묘사 중심이므로 9.0%까지 완화
        "burstiness_limit": 15.0,
        "buzzwords": [
            "상태창", "나노", "마치 신의", "초월적인", "인과율", "로그가", 
            "마치 기적인", "차원을 넘어", "절대적인 법칙", "시스템의 인도", "신화적인",
            "마나의 파동", "영혼의 계약", "심연의 수호자", "대륙의 구원자", "운명의 선택",
            "고대 마법", "각성자", "헌터 리미터", "클래스 전직", "스킬 포인트",
            "서클 아크", "차원의 균열", "무한의 동력", "차원 폭발", "스킬 쿨타임",
            "초월자들의", "마법식 오버플로", "영혼 흡수", "불사의 존재", "무한 전이"
        ],
        "tells": [
            r"경외감을 느꼈다", r"전율이 일었다", r"압도당했다", r"절망의 심연",
            r"자비 없는 힘", r"상상도 할 수 없는", r"위압감에 짓눌려", r"극한의 공포",
            r"가늠할 수 없는", r"신화급 위력", r"신의 분노", r"피할 수 없는 종막"
        ],
        "endings": [
            r"그의 전설은", r"대륙의 역사는", r"신화가 시작", r"그리하여 새로운",
            r"그의 이름은 영원히", r"누구도 넘볼 수 없는", r"새로운 시대의 문", r"전설의 서막",
            r"이것이 각성자의", r"대역사의 장이", r"신조차 예측하지 못한", r"마침내 영웅의"
        ],
        "format_strict": False
    },
    
    "romance": {
        "name": "로맨스 및 로맨스 판타지 (Romance / Rom-Fan)",
        "modifier_limit": 11.0,     # 인물의 내면 정서 묘사가 풍부하므로 11.0% 완화
        "burstiness_limit": 15.0,
        "buzzwords": [
            "숨결이 닿", "눈동자에 스치는", "심장박동이", "붉게 물든", "가슴이 내려앉",
            "영원히 잊지 못할", "어둠 속의 빛", "운명적인 장난", "애틋한", "찬란하게 빛나는",
            "뺨을 쓸어내리며", "턱을 들어 올리", "뜨거운 시선", "사랑의 굴레", "거부할 수 없는",
            "애절한 안타까움", "가냘픈 떨림", "마음의 문을", "숨 막히는 긴장", "눈물이 흘러내",
            "설레는 감정", "애틋한 그리움", "사랑의 불꽃", "영원히 간직할", "마주한 두 눈"
        ],
        "tells": [
            r"사랑스러웠다", r"애달팠다", r"슬픔이 차올랐다", r"사랑을 갈구했다",
            r"가슴이 찢어지는", r"행복에 겨워", r"서글픈 미소", r"자괴감이 밀려왔다",
            r"애가 타들어 갔다", r"설레는 마음을 숨기지", r"미칠 것 같은 그리움"
        ],
        "endings": [
            r"그들의 운명은", r"서로를 향한 마음은", r"영원한 사랑이", r"꽃잎이 흩날리며",
            r"사랑의 마침표", r"비로소 하나가", r"영원한 안식", r"눈물겨운 해후",
            r"약속된 미래를 향해", r"다시는 헤어지지 않을", r"기적 같은 만남의 끝"
        ],
        "format_strict": False
    },
    
    "wuxia": {
        "name": "정통 및 퓨전 무협 (Classic Wuxia)",
        "modifier_limit": 8.5,
        "burstiness_limit": 16.0,
        "buzzwords": [
            "일장을 내뻗", "절대적인", "마치 신기루처럼", "하늘을 찌를 듯한", "공력을 끌어",
            "천지를 뒤흔드는", "서슬 퍼런 안광", "기혈이", "단전의", "검강을",
            "무림의 풍운", "천하제일의", "살수를 펼쳐", "초식을 전개", "신형이 흔들",
            "장풍을 쏘아", "내력이 끓어", "검끝의 전율", "강호의 법칙", "비무를 신청",
            "혈로를 뚫", "검귀의 기세", "신형을 날려", "기운이 팽창", "독문 병기"
        ],
        "tells": [
            r"경악을 금치 못했다", r"오만함이 하늘을", r"살기를 내뿜었다",
            r"공포에 질려", r"기세에 눌려", r"비참한 몰락", r"분노에 가득 차",
            r"살의에 불타올랐다", r"무릎을 꿇고 애걸", r"치욕스러운 패배"
        ],
        "endings": [
            r"강호의 풍운은", r"맹주로의 길은", r"피바람이 불어올", r"검끝이 향하는",
            r"새로운 전설이 강호에", r"강호의 질서가", r"비극의 씨앗은", r"비로소 칼날을 거두",
            r"천하무림의 운명이", r"영웅의 검은 비로소", r"강호의 역사는 다시"
        ],
        "format_strict": False
    },
    
    "blog_seo": {
        "name": "블로그 및 에세이 SEO 최적화 (Blog & Essay SEO)",
        "modifier_limit": 8.0,      # 웹 가독성을 위해 불필요한 부사 억제 8.0%
        "burstiness_limit": 13.0,   # 웹 문서는 너무 길지 않아도 되므로 13.0 기준
        "buzzwords": [
            "솔직히 말해", "아주 유용한", "꼭 확인해봐야", "추천해 드립니다",
            "이 글을 통해", "지금 바로", "인생 꿀팁", "상세히 알아보겠습니다",
            "마지막으로", "결과적으로", "우선적으로", "여러분들을 위해",
            "매우 중요한", "완벽하게 정리", "성공적인 결과를", "가장 효율적인",
            "차근차근 하나씩", "잊지 말고", "반드시 알아두어야", "도움이 되는 정보"
        ],
        "tells": [
            r"매우 유익하다", r"정말 신기했다", r"무척 당황했다", r"솔직히 걱정됐다",
            r"엄청 만족스럽다", r"정말 유용하다", r"강력히 추천한다", r"불안감에 휩싸"
        ],
        "endings": [
            r"도움이 되셨다면", r"구독과 좋아요", r"댓글로 남겨주세요", r"다음 포스팅에서",
            r"함께 읽으면 좋은 글", "공감 버튼 꾹", "오늘도 행복한 하루", "포스팅을 마칩니다"
        ],
        "format_strict": False
    },
    
    "resume": {
        "name": "자기소개서 및 비즈니스 보고서 (Resume & Report)",
        "modifier_limit": 5.0,      # 미사여구와 형용사를 극단으로 배제하고 수치적 사실만 5.0%
        "burstiness_limit": 12.0,
        "buzzwords": [
            "혁신적인", "글로벌 역량", "시너지를 창출", "융합인재", "마중물이 되어",
            "역량을 발휘하여", "도모하며", "선제적 대응", "적극적인 자세로",
            "주도적으로 해결", "가치를 더하여"
        ],
        "tells": [
            r"크게 보람을 느꼈다", r"열정적으로 임했다", r"소통에 주력했다"
        ],
        "endings": [
            r"이바지하겠습니다", r"기여하는 인재가", r"성공으로 이끌겠습니다", r"약속드립니다"
        ],
        "format_strict": True       # 비즈니스 공적 문서이므로 날것의 볼드/백틱 마크다운 엄격 규제
    }
}

# ======================================================================
# 🛡️ 2. 검사 규칙 마스터 정의 (Textbook & Indirect Emotions)
# ======================================================================
TEXTBOOK_PATTERNS = [
    r"에\s*따라[\s,]\s*(적법|불법|합법|영장|기소|판결)", 
    r"원칙에\s*(의하면|따르면|부합)",
    r"(이란|라\s*함은)\s*(것은|것이다|개념이다)",
    r"일반적으로\s*(알려진|알려져|인정되)",
    r"(학설|이론|판례|헌법|법률)에\s*(따르면|의하면|비추어)",
    r"형사소송법\s*제\s*\d+\s*조",
    r"독수독과\s*원칙",
    r"위법수집증거\s*배제\s*원칙"
]

INDIRECT_EMOTION_MARKERS = [
    r"(손끝|손가락|입술|턱|어깨|주먹|손톱).*(떨|긁|깨물|움켜|쥐|지|진|파르르|올라|굳)", 
    r"(숨|호흡|마른침|침).*(멎|삼키|몰아|가쁘|내쉬|턱)",
    r"(목소리|음성|목구멍).*(갈라|잠기|떨|막히|튀어)",
    r"(시선|눈동자|눈길|동공).*(피|돌리|내리깔|흔들|풀리|고정)"
]

# ======================================================================
# 🛡️ 3. 분석 핵심 엔진 (Core Sanitizer Engine)
# ======================================================================
def analyze_text(file_path, mode="hardboiled"):
    if not os.path.exists(file_path):
        return None
        
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
        
    lines = content.splitlines()
    
    # 1) 프리셋 가져오기
    preset = PRESETS.get(mode, PRESETS["hardboiled"])
    MODIFIER_LIMIT = preset["modifier_limit"]
    BURSTINESS_LIMIT = preset["burstiness_limit"]
    BUZZWORDS = preset["buzzwords"]
    EMOTION_TELLS = preset["tells"]
    ENDING_TELLS = preset["endings"]
    FORMAT_STRICT = preset["format_strict"]
    
    # 2) YAML 프론트매터(L1~L8 구역) 자동 예외 필터 처리
    pure_lines = []
    in_frontmatter = False
    frontmatter_bounds = []
    
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "---":
            frontmatter_bounds.append(idx)
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        pure_lines.append((idx + 1, line))  # (1-indexed 라인번호, 내용)
        
    frontmatter_end_line = 0
    if len(frontmatter_bounds) >= 2:
        frontmatter_end_line = frontmatter_bounds[1] + 1
        
    analyzed_lines = [line for idx, line in pure_lines if line.strip() and not line.strip().startswith("#")]
    pure_text = "\n".join(analyzed_lines)
    
    # 3) 한국어 부사/형용사 수식어 밀도 정규식 근사 로직
    adverb_pattern = r"\b\w+(히|하게|적으로|스레|스럽게|히도|하게도|의외로|급격히|필사적으로)\b"
    adjective_pattern = r"\b\w+(한|하는|스러운|적인|비장한|서슬 퍼런|처절한|쓸쓸한|찬란한|요란한)\b"
    
    adverbs_found = re.findall(adverb_pattern, pure_text)
    adjectives_found = re.findall(adjective_pattern, pure_text)
    
    words = pure_text.split()
    total_words = len(words) if words else 1
    adverb_ratio = (len(adverbs_found) / total_words) * 100
    adjective_ratio = (len(adjectives_found) / total_words) * 100
    total_modifier_ratio = adverb_ratio + adjective_ratio
    
    # 문장 분할 (정교한 마침표/물음표/느낌표 기준)
    sentences = re.split(r'(?<=[.!?])\s+', pure_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # 4) Burstiness 및 Delta(Δ) 분석
    sentence_lengths = [len(s) for s in sentences]
    char_count = len(content)
    
    if sentence_lengths:
        avg_len = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((x - avg_len) ** 2 for x in sentence_lengths) / len(sentence_lengths)
        std_dev = math.sqrt(variance)
        
        # 인접 문장 간 길이 변화율 (Δ) 분석
        deltas = [abs(sentence_lengths[i] - sentence_lengths[i-1]) for i in range(1, len(sentence_lengths))]
        avg_delta = sum(deltas) / len(deltas) if deltas else 0
        
        # 3문장 이상 리듬 평탄도 검사 (Delta 가 극도로 적은 연속 문장군 탐지)
        flat_runs = 0
        for i in range(2, len(sentence_lengths)):
            if abs(sentence_lengths[i] - sentence_lengths[i-1]) < 5 and abs(sentence_lengths[i-1] - sentence_lengths[i-2]) < 5:
                flat_runs += 1
    else:
        avg_len = 0
        std_dev = 0
        avg_delta = 0
        flat_runs = 0
        
    # 5) AI Buzzwords 및 상투어 감지
    detected_buzzwords = []
    for word in BUZZWORDS:
        count = len(re.findall(re.escape(word), pure_text))
        if count > 0:
            detected_buzzwords.append((word, count))
            
    # 6) Show, Don't Tell 위반 감지 (감정 직접 서술)
    detected_tells = []
    for pattern in EMOTION_TELLS:
        matches = re.finditer(pattern, content)
        for m in matches:
            line_no = content[:m.start()].count("\n") + 1
            if line_no < frontmatter_end_line:
                continue
            start = max(0, m.start() - 15)
            end = min(len(content), m.end() + 15)
            snippet = content[start:end].replace("\n", " ")
            detected_tells.append(f"...{snippet}...")
            
    # 7) [신규] 감정 간접화 반응 감지 (물리적/감각적 간접 묘사)
    detected_indirects = []
    for pattern in INDIRECT_EMOTION_MARKERS:
        matches = re.finditer(pattern, content)
        for m in matches:
            line_no = content[:m.start()].count("\n") + 1
            if line_no < frontmatter_end_line:
                continue
            start = max(0, m.start() - 15)
            end = min(len(content), m.end() + 15)
            snippet = content[start:end].replace("\n", " ")
            detected_indirects.append(f"...{snippet}...")

    # 8) [신규] 교과서적 설명/정의 톤 감지
    detected_textbooks = []
    for pattern in TEXTBOOK_PATTERNS:
        matches = re.finditer(pattern, content)
        for m in matches:
            line_no = content[:m.start()].count("\n") + 1
            if line_no < frontmatter_end_line:
                continue
            start = max(0, m.start() - 20)
            end = min(len(content), m.end() + 20)
            snippet = content[start:end].replace("\n", " ")
            detected_textbooks.append(f"Line {line_no}: ...{snippet}...")

    # 9) 접속사 남용 (Conjunction Spam) 검사
    conjunctions = ["하지만", "그리고", "그러나", "그리하여", "이로써"]
    detected_conjunctions = {}
    for conj in conjunctions:
        count = len(re.findall(r"^\s*" + re.escape(conj), pure_text, re.MULTILINE))
        if count > 0:
            detected_conjunctions[conj] = count
            
    # 10) 마지막 3문단 웅장 해설/자평 엔딩 검사
    ending_issues = []
    last_paragraphs = analyzed_lines[-3:] if len(analyzed_lines) >= 3 else analyzed_lines
    for idx, para in enumerate(last_paragraphs):
        for pattern in ENDING_TELLS:
            if re.search(pattern, para):
                ending_issues.append(f"마지막 단락 [{len(last_paragraphs)-idx}번째 뒤]: '{pattern}' 검출 -> {para[:40]}...")
                break
                
    # 11) 마크다운 포맷 기호 소독 여부 검사 (프론트매터 영역 배제)
    raw_markdown = []
    for idx, line in enumerate(lines):
        if idx < frontmatter_end_line:
            continue
        if "**" in line:
            raw_markdown.append(f"Line {idx+1} (볼드체 '**'): {line[:50]}...")
        if "`" in line:
            raw_markdown.append(f"Line {idx+1} (백틱 '`'): {line[:50]}...")
            
    # 12) 씬 구분선 단일 규격 (* * *) 검사 (프론트매터 영역 배제)
    invalid_separators = []
    for idx, line in enumerate(lines):
        if idx < frontmatter_end_line:
            continue
        stripped = line.strip()
        if stripped in ["---", "--- ", "---", "–-", "—-"]:
            invalid_separators.append(f"Line {idx+1}: '{stripped}' 사용 금지. 오직 * * * 만 사용 가능")

    # ======================================================================
    # ⚖️ 4. 채점 및 감점 로직 (Score Card)
    # ======================================================================
    score = 100
    deductions = []
    
    # Burstiness 감점
    if std_dev < (BURSTINESS_LIMIT - 6):
        score -= 20
        deductions.append(f"Burstiness 경고: 문장 리듬이 지독하게 평탄함 (표준편차 {std_dev:.2f} < 기준 {BURSTINESS_LIMIT}) (-20점)")
    elif std_dev < BURSTINESS_LIMIT:
        score -= 10
        deductions.append(f"Burstiness 경보: 문장 리듬이 다소 단조로움 (표준편차 {std_dev:.2f} < 기준 {BURSTINESS_LIMIT}) (-10점)")
        
    # Delta (문장 간 호흡 변주) 및 평탄화 감점
    if avg_delta < 10.0:
        score -= 10
        deductions.append(f"리듬 변주(Delta) 경보: 인접 문장 간 길이 편차가 너무 작아 호흡이 지루함 (평균 편차 {avg_delta:.2f}자) (-10점)")
    if flat_runs > 2:
        score -= 10
        deductions.append(f"단조성 경보: 3연속 이상 유사 길이 문장 반복 {flat_runs}회 검출 (-10점)")
        
    # 수식어 밀도 감점
    if total_modifier_ratio > (MODIFIER_LIMIT + 3.0):
        score -= 15
        deductions.append(f"수식어 과잉 경고: 부사/형용사 밀도가 너무 높음 ({total_modifier_ratio:.2f}% > 기준 {MODIFIER_LIMIT}%) (-15점)")
    elif total_modifier_ratio > MODIFIER_LIMIT:
        score -= 5
        deductions.append(f"수식어 주의: 부사/형용사 비중이 기준치보다 소폭 높음 ({total_modifier_ratio:.2f}% > 기준 {MODIFIER_LIMIT}%) (-5점)")
        
    # Buzzwords 감점
    total_buzz = sum(count for _, count in detected_buzzwords)
    if total_buzz > 5:
        penalty = min(20, total_buzz * 3)
        score -= penalty
        deductions.append(f"Buzzwords 경보: AI 상투어가 다량 검출됨 ({total_buzz}회) (-{penalty}점)")
    elif total_buzz > 0:
        penalty = min(10, total_buzz * 2)
        score -= penalty
        deductions.append(f"Buzzwords 경보: 일부 AI 상투어가 발견됨 ({total_buzz}회) (-{penalty}점)")
        
    # Tells 감점
    if detected_tells:
        penalty = min(25, len(detected_tells) * 5)
        score -= penalty
        deductions.append(f"Tells 직접적 감정 명사 사용 위반 ({len(detected_tells)}회) (-{penalty}점)")
        
    # 감정 간접화 품질 가산점 (Tells 비율 대비 간접 묘사가 많으면 점수 보강)
    indirect_ratio = len(detected_indirects) / (len(detected_tells) if detected_tells else 1)
    if len(detected_indirects) > 3 and indirect_ratio >= 1.0:
        score = min(100, score + 10)
        deductions.append(f"✨ 감정 간접화 묘사 우수 가산점: 물리적 행동/반응 적극 사용 (+10점)")
    elif len(detected_indirects) < 2:
        score -= 10
        deductions.append(f"감정 묘사 결핍 감점: 인물의 물리적 반응/행동 묘사가 지독히 부족함 ({len(detected_indirects)}회) (-10점)")

    # 교과서 톤 감점
    if detected_textbooks:
        penalty = min(20, len(detected_textbooks) * 5)
        score -= penalty
        deductions.append(f"교과서 톤 위반: 백과사전/위키식 법률/원칙 해설체 검출 ({len(detected_textbooks)}회) (-{penalty}점)")

    # 웅장 엔딩 자평 감점
    if ending_issues:
        score -= 20
        deductions.append("AI 요약 엔딩 경고: 마지막 문단에 3인칭 자평/정리 뉘앙스 강하게 검출됨 (-20점)")
        
    # 마크다운 포맷 및 구분선 감점 (포맷 엄격 모드 작동 시)
    if FORMAT_STRICT:
        if raw_markdown or invalid_separators:
            score -= 15
            deductions.append("하네스 포맷 오류: 볼드/백틱 노출 또는 구분선 규격 위반 (-15점)")
 
    # 최종 판정
    if score >= 85:
        decision = "🟢 PASS (인간 친화적 자연스러운 문체 합격)"
    elif score >= 70:
        decision = "🟡 REVISE (수식어 및 AI Buzzwords 일부 소독 권장)"
    else:
        decision = "🔴 REWRITE (AI 문체 다량 유입, 전면 소독 및 리라이팅 요망)"
 
    return {
        "char_count": char_count,
        "avg_len": avg_len,
        "std_dev": std_dev,
        "avg_delta": avg_delta,
        "flat_runs": flat_runs,
        "adverb_ratio": adverb_ratio,
        "adjective_ratio": adjective_ratio,
        "total_modifier_ratio": total_modifier_ratio,
        "buzzwords": detected_buzzwords,
        "tells": detected_tells,
        "indirects": detected_indirects,
        "textbooks": detected_textbooks,
        "conjunctions": detected_conjunctions,
        "ending_issues": ending_issues,
        "raw_markdown": raw_markdown,
        "invalid_separators": invalid_separators,
        "score": max(0, score),
        "deductions": deductions,
        "decision": decision
    }

# ======================================================================
# 🛡️ 4. CLI 인터페이스 및 실행부 (CLI Parser)
# ======================================================================
def main():
    parser = argparse.ArgumentParser(
        description="🛡️ 초고정밀 AI 문체 소독 및 하드보일드/다중 프리셋 검사 시스템 v4.0 (범용)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "target", 
        nargs="?", 
        default=None,
        help="검사 대상 회차 번호 또는 파일명 (예: 031 또는 031화)"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=list(PRESETS.keys()),
        default="hardboiled",
        help="검사 프리셋 모드 선택:\n" + "\n".join([f"  - {k}: {v['name']}" for k, v in PRESETS.items()])
    )
    parser.add_argument(
        "--file", "-f",
        default=None,
        help="직접 검사할 마크다운 파일의 경로"
    )
    parser.add_argument(
        "--dir", "-d",
        default=None,
        help="회차 정식 원고들이 위치한 기본 디렉토리 경로"
    )
    
    args = parser.parse_args()
    
    mode = args.mode
    preset_name = PRESETS[mode]["name"]
    file_path = None
    
    # 직접 파일 경로 지정 시
    if args.file:
        file_path = args.file
    else:
        if not args.target:
            parser.print_help()
            return
            
        target = args.target
        # 기본 디렉토리 매핑 (옵션으로 받거나 실행 환경에 따라 동적 탐지)
        dir_path = args.dir if args.dir else os.getcwd()
        
        # 회차 숫자 매핑 처리
        try:
            val = int(target)
            file_name = f"{val:03d}화.md"
            file_path = os.path.join(dir_path, file_name)
            if not os.path.exists(file_path):
                # 031_ 혹은 031화 로 시작하는 파일 패턴 탐색
                files = [f for f in os.listdir(dir_path) if f.startswith(f"{val:03d}") and f.endswith(".md")]
                if files:
                    file_path = os.path.join(dir_path, files[0])
        except ValueError:
            # 문자열로 직접 지정 시
            file_path = os.path.join(dir_path, target)
            if not os.path.exists(file_path):
                # 상대 경로/절대 경로로 다시 체크
                file_path = target
                
    if not file_path or not os.path.exists(file_path):
        print(f"❌ 검사 대상을 찾을 수 없습니다: {file_path}")
        print("💡 --dir (-d) 로 원고 폴더를 지정하거나 --file (-f) 로 정확한 파일 경로를 입력해주세요.")
        return
        
    res = analyze_text(file_path, mode=mode)
    if not res:
        print("❌ 분석 중 치명적인 내부 오류가 발생했습니다.")
        return
        
    print("="*70)
    print(f"🛡️ 초고정밀 AI 문체 소독 및 하드보일드/다중 프리셋 검사 시스템 v4.0 (범용)")
    print(f"🎯 실행 프리셋 모드: {preset_name}")
    print(f"📂 대상 파일: {os.path.basename(file_path)}")
    print(f"📏 총 글자 수: {res['char_count']:,}자 (공백 포함)")
    print("="*70)
    
    print(f"📊 [1] 문장 다이내믹스 & 버스티니스 (Burstiness)")
    print(f"  - 평균 문장 길이: {res['avg_len']:.1f}자")
    print(f"  - 문장 길이 변동성(표준편차): {res['std_dev']:.2f}자 (기준값: {PRESETS[mode]['burstiness_limit']:.1f} 이상)")
    print(f"  - 호흡 변동폭(Delta): {res['avg_delta']:.2f}자")
    print(f"  - 단조로운 연속 문장군 패턴: {res['flat_runs']}회 검출")
    print("-" * 60)
    
    print(f"📈 [2] 한국어 수식어(부사/형용사) 밀도 판독")
    print(f"  - 부사 밀도: {res['adverb_ratio']:.2f}%")
    print(f"  - 형용사 밀도: {res['adjective_ratio']:.2f}%")
    print(f"  - 합산 수식어 비중: {res['total_modifier_ratio']:.2f}% (기준값: {PRESETS[mode]['modifier_limit']:.1f}% 이하)")
    print("-" * 60)
    
    print(f"🔍 [3] AI Buzzwords 및 상투어 검출")
    if res["buzzwords"]:
        for word, count in res["buzzwords"]:
            print(f"  ❌ '{word}': {count}회 검출됨")
    else:
        print("  🟢 검출된 AI 상투어 없음 (완벽한 어휘 통제)")
    print("-" * 60)
    
    print(f"📢 [4] Show, Don't Tell 직접 감정 명사 검출")
    if res["tells"]:
        for tell in res["tells"]:
            print(f"  ❌ 직접 진술 경고: {tell}")
    else:
        print("  🟢 관념적 감정 직접 진술 없음 (완벽한 물리적 행동/간접 묘사)")
    print("-" * 60)

    print(f"✨ [5] 감정 간접화 물리적 행동/반응 검출")
    if res["indirects"]:
        print(f"  🟢 행동 묘사 발견 ({len(res['indirects'])}회):")
        for ind in res["indirects"][:5]:  # 상위 5개만 스니펫 표시
            print(f"    - {ind}")
    else:
        print("  ❌ 물리적 행동/반응 묘사 없음 (감정이 너무 메말라 있거나 직접 명명으로 때움)")
    print("-" * 60)

    print(f"📚 [6] 교과서적/위키피디아 법률 및 원칙 설명 톤 검출")
    if res["textbooks"]:
        for textb in res["textbooks"]:
            print(f"  ❌ 교과서체 설명 경고: {textb}")
    else:
        print("  🟢 설명조 교과서 톤 없음 (인물 대사/행동 및 내면 독백 속 규정 변환 통과)")
    print("-" * 60)
    
    print(f"🔗 [7] Conjunction Spam (접속 부사 문두 남용)")
    if res["conjunctions"]:
        for conj, count in res["conjunctions"].items():
            print(f"  ⚠️ 문단 첫머리 '{conj}': {count}회 발견")
    else:
        print("  🟢 긴밀하고 매끄러운 단락 흐름 유지 통과")
    print("-" * 60)
    
    print(f"🎬 [8] AI 요약/자평 엔딩 검사 (마지막 3문단)")
    if res["ending_issues"]:
        for issue in res["ending_issues"]:
            print(f"  ❌ {issue}")
    else:
        print("  🟢 장평 해설/자평식 웅장 엔딩 없음 (서늘한 여운/마감 유지 통과)")
    print("-" * 60)
    
    print(f"🎛️ [9] 포맷팅 및 장면 전환선 규격 검사")
    format_ok = True
    if res["raw_markdown"]:
        format_ok = False
        for err in res["raw_markdown"]:
            print(f"  ❌ 포맷 오류: {err}")
    if res["invalid_separators"]:
        format_ok = False
        for err in res["invalid_separators"]:
            print(f"  ❌ 씬 구분선 오류: {err}")
    if format_ok:
        print("  🟢 모든 마크다운/구분선 포맷팅 통과")
        
    print("="*70)
    print(f"📋 감점/가산 내역:")
    if res["deductions"]:
        for ded in res["deductions"]:
            print(f"  - {ded}")
    else:
        print("  - 없음 (감점 없는 완전무결한 문장)")
    print("-" * 60)
    print(f"✨ 종합 하네스 AI-ness 획득 점수: {res['score']}점 / 100점")
    print(f"🛡️ 최종 하네스 검증 판정: {res['decision']}")
    print("="*70)

    # ======================================================================
    # 📋 5. AI 문체 소독 가이드 우선순위 자동 출력
    # ======================================================================
    if res["score"] < 85:
        print("📋 [AI 문체 소독 교정 가이드 우선순위]")
        print("-" * 60)
        idx = 1
        if res["total_modifier_ratio"] > PRESETS[mode]["modifier_limit"]:
            print(f"  {idx}. [형용사/부사 줄이기] 합산 수식어 밀도가 기준치({PRESETS[mode]['modifier_limit']:.1f}%)보다 높은 {res['total_modifier_ratio']:.2f}%입니다.")
            print("     👉 명사구 앞 형용사/부사를 1개 이하로 극도로 줄이고 핵심 동사로 전환하십시오.")
            idx += 1
        if res["std_dev"] < PRESETS[mode]["burstiness_limit"] or res["avg_delta"] < 10.0 or res["flat_runs"] > 0:
            print(f"  {idx}. [문장 길이 변주 및 리듬 깨기] 문장 리듬이 단조롭거나 호흡 변폭(Delta)이 작습니다.")
            print("     👉 묘사를 길게 쓴 문단 뒤에 1~3어절의 극단 단문(예: '법정은 고요했다. 숨조차 없었다.')을 배치하여 리듬을 일부러 깨십시오.")
            idx += 1
        if res["tells"]:
            print(f"  {idx}. [감정 간접화] 감정을 '분노했다', '자괴감에' 처럼 명사나 형용사로 설명하는 직접 진술이 검출되었습니다.")
            print("     👉 감정 단어 대신 '손끝이 바닥을 긁었다', '어깨가 파르르 떨려왔다' 처럼 간접적인 물리 반응과 미세 행동으로 묘사하십시오.")
            idx += 1
        if res["textbooks"]:
            print(f"  {idx}. [교과서 톤 변환] 위키피디아식 법률 원칙/규정 설명조가 노출되었습니다.")
            print("     👉 인물의 독백이나 비꼬는 독백(예: '책 속에서만 보던 말이, 오늘은 아이의 무덤이 되었다.')으로 사건 속에 변환해 서술하십시오.")
            idx += 1
        if res["buzzwords"]:
            print(f"  {idx}. [AI Buzzwords 소독] '{', '.join([w for w,_ in res['buzzwords']])}' 과 같은 AI 상호 상투어가 감지되었습니다.")
            print("     👉 식상한 어휘를 100% 제거하고 보다 입체적이고 현대적인 사실 묘사로 문장을 재작성하십시오.")
            idx += 1
        print("="*70)

if __name__ == '__main__':
    main()
