#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

def parse_delta_metadata(novel_root):
    """
    03_줄거리 디렉토리 하위의 Ep_*_Review.md 파일들에서 Delta 메타데이터를 파싱하여 타임라인을 구축합니다.
    """
    story_dir = os.path.join(novel_root, "03_줄거리")
    if not os.path.exists(story_dir):
        print(f"[Error] Directory not found: {story_dir}")
        return None

    # 에피소드 리뷰 파일 스캔 및 정렬
    review_files = []
    for file in os.listdir(story_dir):
        match = re.match(r"Ep_(\d+)_Review\.md", file)
        if match:
            ep_num = int(match.group(1))
            review_files.append((ep_num, os.path.join(story_dir, file)))

    review_files.sort(key=lambda x: x[0])

    if not review_files:
        print("[Warning] No Ep_*_Review.md files found in 03_줄거리.")
        return None

    timeline = {
        "characters": {},  # char_name -> [(ep_num, desc)]
        "items": {},       # item_name -> [(ep_num, desc)]
        "foreshadowing": {} # f_code -> {"title": "", "history": [(ep_num, status, desc)]}
    }

    # 카테고리 식별용 정규식
    char_header_re = re.compile(r"캐릭터|👤")
    item_header_re = re.compile(r"아이템|🎒|설비")
    fore_header_re = re.compile(r"떡밥|복선|📍")

    for ep_num, file_path in review_files:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        current_section = None
        for line in lines:
            line_strip = line.strip()
            
            # 섹션 전환 헤더 파싱 (### 또는 ####)
            if line_strip.startswith("###") or line_strip.startswith("####"):
                header_text = line_strip.replace("#", "").strip()
                if char_header_re.search(header_text):
                    current_section = "characters"
                elif item_header_re.search(header_text):
                    current_section = "items"
                elif fore_header_re.search(header_text):
                    current_section = "foreshadowing"
                else:
                    current_section = None
                continue

            # 리스트 아이템 파싱
            if current_section and (line_strip.startswith("- [ ]") or line_strip.startswith("- [x]") or line_strip.startswith("-")):
                # 체크박스 및 불릿 제거
                content = re.sub(r"^-\s*(\[[ xX]\])?\s*", "", line_strip).strip()
                if not content:
                    continue

                if current_section == "foreshadowing":
                    # 떡밥 코드 파싱 (예: F-03 또는 [F-03] 등)
                    f_match = re.search(r"\b(F-\d+|F-[A-Za-z0-9-_]+)\b", content)
                    if f_match:
                        f_code = f_match.group(1)
                        # 진척도 아이콘 파싱 (🔴, 🟡, 🟢)
                        status = "🔴 미회수"
                        if "🟢" in content or "회수 완료" in content:
                            status = "🟢 회수 완료"
                        elif "🟡" in content or "진행 중" in content:
                            status = "🟡 진행 중"
                        
                        desc = content.replace(f_code, "").strip()
                        # 기호 정리
                        desc = re.sub(r"^[(\[\])\s\-:]+", "", desc).strip()

                        if f_code not in timeline["foreshadowing"]:
                            timeline["foreshadowing"][f_code] = {"title": desc.split(":")[0], "history": []}
                        
                        timeline["foreshadowing"][f_code]["history"].append((ep_num, status, content))
                
                elif current_section == "characters":
                    # 이름과 설명 분리 (예: "강한울: 데이터 링크...")
                    parts = content.split(":", 1)
                    char_name = parts[0].strip()
                    char_desc = parts[1].strip() if len(parts) > 1 else content
                    
                    if char_name not in timeline["characters"]:
                        timeline["characters"][char_name] = []
                    timeline["characters"][char_name].append((ep_num, char_desc))
                    
                elif current_section == "items":
                    parts = content.split(":", 1)
                    item_name = parts[0].strip()
                    item_desc = parts[1].strip() if len(parts) > 1 else content
                    
                    if item_name not in timeline["items"]:
                        timeline["items"][item_name] = []
                    timeline["items"][item_name].append((ep_num, item_desc))

    return timeline

def generate_report(novel_root, timeline):
    """
    파싱된 타임라인 데이터를 토대로 마크다운 보고서 및 LLM 진단 프롬프트 파일을 생성합니다.
    """
    report_lines = []
    report_lines.append("# 📊 하네스 메타데이터 기반 정합성 검증 보고서\n")
    report_lines.append("이 보고서는 각 에피소드 리뷰 파일에서 추출한 설정 변경점(Delta) 데이터를 정적으로 분석하여 작성되었습니다.\n")
    report_lines.append("---\n")

    # 1. 떡밥/복선 추적 분석
    report_lines.append("## 📍 1. 떡밥(복선) 수명 주기 상태")
    if not timeline["foreshadowing"]:
        report_lines.append("검출된 떡밥 메타데이터가 없습니다.\n")
    else:
        report_lines.append("| 떡밥 코드 | 설명/식별칭 | 최초 등장 | 최근 상태 | 히스토리 추적 |")
        report_lines.append("| :---: | :--- | :---: | :---: | :--- |")
        
        unresolved_count = 0
        resolved_count = 0
        
        for f_code, info in sorted(timeline["foreshadowing"].items()):
            history = info["history"]
            first_ep = history[0][0]
            latest_status = history[-1][1]
            
            if "🟢" in latest_status:
                resolved_count += 1
            else:
                unresolved_count += 1

            # 히스토리 요약 스트링
            hist_steps = []
            for ep, stat, text in history:
                icon = "🔴" if "🔴" in stat else ("🟡" if "🟡" in stat else "🟢")
                hist_steps.append(f"Ep.{ep}({icon})")
            hist_str = " -> ".join(hist_steps)
            
            report_lines.append(f"| `{f_code}` | {info['title'][:40]} | Ep.{first_ep} | {latest_status} | {hist_str} |")
        
        report_lines.append(f"\n* **통계:** 총 {resolved_count + unresolved_count}개 떡밥 중 **미회수/진행중 {unresolved_count}개**, **회수 완료 {resolved_count}개**\n")

    # 2. 캐릭터 상태 추적
    report_lines.append("## 👤 2. 캐릭터 설정 변경점 시간선")
    if not timeline["characters"]:
        report_lines.append("검출된 캐릭터 설정 변경 데이터가 없습니다.\n")
    else:
        for char_name, history in sorted(timeline["characters"].items()):
            report_lines.append(f"### {char_name}")
            for ep, desc in history:
                report_lines.append(f"* **Ep.{ep:03d}**: {desc}")
            report_lines.append("")

    # 3. 아이템 및 설비 상태 추적
    report_lines.append("## 🎒 3. 아이템 및 세계관 설비 타임라인")
    if not timeline["items"]:
        report_lines.append("검출된 아이템/설비 상태 변경 데이터가 없습니다.\n")
    else:
        for item_name, history in sorted(timeline["items"].items()):
            report_lines.append(f"### {item_name}")
            for ep, desc in history:
                report_lines.append(f"* **Ep.{ep:03d}**: {desc}")
            report_lines.append("")

    # 파일로 리포트 쓰기
    report_path = os.path.join(novel_root, "03_줄거리", "Metadata_QA_Report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"[Success] Static metadata report saved to: {report_path}")

    # 4. LLM용 정합성 진단 프롬프트 어셈블링
    prompt_lines = []
    prompt_lines.append("# 🤖 [프롬프트] LLM용 초정밀 메타데이터 설정 검증 요청서\n")
    prompt_lines.append("아래 프롬프트 텍스트 전체를 복사하여 LLM 에이전트에 입력하시면, 극소량의 토큰으로 정밀한 설정 모순 진단을 받을 수 있습니다.\n")
    prompt_lines.append("```markdown")
    prompt_lines.append("당신은 소설의 개연성과 일관성을 검증하는 전문 편집자입니다.")
    prompt_lines.append("아래에 각 에피소드별로 추출된 캐릭터, 아이템, 떡밥의 설정 상태 변화 타임라인 데이터를 제공합니다.")
    prompt_lines.append("이 타임라인 흐름에서 인과가 붕괴하거나 직접적으로 모순된 설정 변경 사항이 있는지 철저히 분석해 주십시오.\n")
    
    prompt_lines.append("[검증 대상 설정 타임라인 데이터]")
    
    # 떡밥 데이터 요약
    prompt_lines.append("■ 떡밥/복선 흐름:")
    for f_code, info in sorted(timeline["foreshadowing"].items()):
        hist_str = " -> ".join([f"Ep.{ep}({stat})" for ep, stat, _ in info["history"]])
        prompt_lines.append(f"- {f_code} ({info['title']}): {hist_str}")
        
    # 캐릭터 데이터 요약
    prompt_lines.append("\n■ 캐릭터 상태 변화 이력:")
    for char_name, history in sorted(timeline["characters"].items()):
        prompt_lines.append(f"- {char_name}:")
        for ep, desc in history:
            prompt_lines.append(f"  * Ep.{ep}: {desc}")
            
    # 아이템 데이터 요약
    prompt_lines.append("\n■ 아이템/설비 상태 변화 이력:")
    for item_name, history in sorted(timeline["items"].items()):
        prompt_lines.append(f"- {item_name}:")
        for ep, desc in history:
            prompt_lines.append(f"  * Ep.{ep}: {desc}")
            
    prompt_lines.append("\n[검증 및 지적 기준]")
    prompt_lines.append("1. **인과관계 단절:** 이전에 특정 상태 이상(예: 중상, 기절, 능력 상실)에 빠진 캐릭터가 아무런 회복/대안 묘사 없이 다음 화에서 갑자기 정상 활동하는 경우.")
    prompt_lines.append("2. **설정 충돌:** 특정 아이템/능력의 설정 수치나 기전이 에피소드 변경에 따라 서로 모순되게 묘사된 경우.")
    prompt_lines.append("3. **떡밥 미회수 연기:** 미회수 🔴 상태의 떡밥이 완결 시점까지 아무 설명 없이 방치되었거나, 🟢 회수되었다고 표기되었으나 실제로는 관련 인물이 회수 장소에 가지 않았던 정황 모순.")
    prompt_lines.append("4. **출력 양식:** 발견된 모순점을 심각도(🔴 CRITICAL, 🟡 WARNING)별로 나누고 구체적인 회차와 모순 사유, 권장 해결 방향을 제안할 것.")
    prompt_lines.append("```")

    prompt_path = os.path.join(novel_root, "03_줄거리", "Metadata_QA_Prompt.md")
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(prompt_lines))
    print(f"[Success] LLM validation prompt template saved to: {prompt_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python metadata_validator.py <novel_root_directory>")
        sys.exit(1)

    novel_root = sys.argv[1]
    if not os.path.exists(novel_root):
        print(f"[Error] Novel root path does not exist: {novel_root}")
        sys.exit(1)

    print(f"\n[Metadata QA] Analyzing project delta logs under: {novel_root}")
    timeline = parse_delta_metadata(novel_root)
    if timeline:
        generate_report(novel_root, timeline)
        print("[Metadata QA] Analysis successfully completed.")
    else:
        print("[Metadata QA] Analysis failed due to missing metadata.")

if __name__ == "__main__":
    main()
