import sys
import re
import os

def check_style(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # 1. 메타데이터(YAML frontmatter) 제거
    text_body = re.sub(r'^---[\s\S]*?---\n', '', text)
    # 2. Markdown 헤더(제목 등) 제거
    text_body = re.sub(r'^#.*$', '', text_body, flags=re.MULTILINE)
    
    # PASS 0: 분량 검증 (공백 포함 글자수)
    char_count = len(text_body.strip())
    
    pass0_status = "🟢" if char_count >= 5500 else "🔴"
    pass0_info = f"{char_count}자"
    if char_count < 5500:
        pass0_info += " (미달)"

    # PASS 1: Stutter Spam (동일 어절 연속 반복 탐지)
    words = text_body.split()
    stutter_spams = []
    for i in range(len(words)-1):
        # 특수문자, 구두점 제거 후 순수 단어 비교
        w1 = re.sub(r'[^\w가-힣]', '', words[i])
        w2 = re.sub(r'[^\w가-힣]', '', words[i+1])
        if w1 and w1 == w2:
            stutter_spams.append(words[i] + " " + words[i+1])
    
    pass1_critical = len(stutter_spams)
    pass1_status = "🟢" if pass1_critical == 0 else "🔴"
    pass1_info = "발견됨: " + ", ".join(stutter_spams[:3]) if pass1_critical > 0 else "양호"

    # PASS 2: Meta Narrative (메타 서술 탐지)
    meta_patterns = [
        r'제\s*[0-9]+\s*(화|장|부)',
        r'회차\s*[0-9]+',
        r'피날레를 장식',
        r'연재 마감'
    ]
    meta_findings = []
    for pattern in meta_patterns:
        matches = re.findall(pattern, text_body)
        if matches:
            meta_findings.extend(matches)
    
    pass2_critical = len(meta_findings)
    
    # WS-16: Pronoun Overuse Check
    sentences = re.split(r'[.!?]\s+', text_body)
    pronoun_warnings = 0
    # Python's re.findall returns groups if present, so we should be careful or use a non-capturing group for the outer part if we need the match.
    # Actually, we just need to count matches.
    pronoun_regex = re.compile(r'(?:^|\s)(?:그|그녀|그들)(?:이|가|은|는|의|를|을|에게|와|과|도|!|\?|,|\.|\s|$)')
    for i in range(len(sentences) - 2):
        window_text = ' '.join(sentences[i:i+3])
        matches = pronoun_regex.findall(window_text)
        if matches and len(matches) >= 3:
            pronoun_warnings += 1
            
    pass2_status = "🔴" if pass2_critical > 0 else ("🟡" if pronoun_warnings > 0 else "🟢")
    pass2_info = "양호"
    if pass2_critical > 0:
        pass2_info = f"메타 서술 {pass2_critical}건 발견"
    elif pronoun_warnings > 0:
        pass2_info = f"대명사 남용 {pronoun_warnings}구간 발견"

    # 결과 리포트 생성
    report_content = f"## 검증 리포트 자동 산출 ({os.path.basename(filepath)})\n\n"
    report_content += "| PASS | 판정 | 🔴 Critical | 🟡 Warning | 🔵 Info | 비고 |\n"
    report_content += "|------|------|------------|-----------|--------|------|\n"
    report_content += f"| 0 분량 | {pass0_status} | — | — | — | {pass0_info} |\n"
    report_content += f"| 1 문법 | {pass1_status} | {pass1_critical}건 | 0건 | 0건 | {pass1_info} |\n"
    report_content += f"| 2 문체 | {pass2_status} | {pass2_critical}건 | {pronoun_warnings}건 | 0건 | {pass2_info} |\n"
    report_content += f"| 3 설정 | ⚪ | - | - | - | 수동 검증 요망 |\n"
    report_content += f"| 4 서사 | ⚪ | - | - | - | 수동 검증 요망 |\n\n"
    
    if pass0_status == "🔴" or pass1_status == "🔴" or pass2_status == "🔴":
        report_content += "**종합 판정: 🔴 REWRITE 필요 (스크립트 판정)**\n"
    elif pass2_status == "🟡":
        report_content += "**종합 판정: 🟡 REVISE 필요 (대명사 남용 등 수정 권장)**\n"
    else:
        report_content += "**종합 판정: 🟢 정량적 조건 PASS (정성 평가 진행 요망)**\n"

    # 콘솔 출력
    print(report_content)

    # 파일 저장
    try:
        file_basename = os.path.splitext(os.path.basename(filepath))[0]
        # 원고 파일 위치(04_회차/연재_정식원고/)에서 3레벨 위로 올라가면 프로젝트 루트
        project_root = os.path.abspath(os.path.join(filepath, "../../.."))
        qa_dir = os.path.join(project_root, "qa", "style_checks")

        if not os.path.exists(qa_dir):
            os.makedirs(qa_dir, exist_ok=True)

        report_path = os.path.join(qa_dir, f"{file_basename}_Report.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"리포트가 파일로 저장되었습니다: {report_path}")
    except Exception as e:
        print(f"Error saving report file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_style_check.py <filepath>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    check_style(filepath)
