import os
import re
import yaml

def parse_frontmatter(file_path):
    """
    마크다운 파일에서 YAML Frontmatter를 파싱하여 딕셔너리로 반환합니다.
    """
    if not os.path.exists(file_path):
        return {}
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if match:
        yaml_content = match.group(1)
        try:
            return yaml.safe_load(yaml_content)
        except yaml.YAMLError:
            return {}
    return {}

def parse_markdown_table_to_dicts(file_path):
    """
    마크다운 파일 내의 모든 표(Table)를 파싱하여 데이터 목록으로 반환합니다.
    """
    if not os.path.exists(file_path):
        return []
        
    results = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    in_table = False
    headers = []
    
    for line in lines:
        line_str = line.strip()
        if line_str.startswith("|"):
            parts = [p.strip().replace("**", "").replace("`", "") for p in line_str.split("|")[1:-1]]
            if not in_table:
                # 첫 행은 헤더
                headers = parts
                in_table = True
            elif line_str.replace(" ", "").startswith("|:-") or line_str.replace(" ", "").startswith("|:-"):
                # 구분선 행
                continue
            else:
                # 데이터 행
                row_data = {}
                for i, part in enumerate(parts):
                    if i < len(headers):
                        row_data[headers[i]] = part
                results.append(row_data)
        else:
            in_table = False
            
    return results

def parse_markdown_tables_to_dict_list(file_path):
    """
    마크다운 파일에서 각 테이블(표)을 파싱하여, 테이블별 키-값 쌍 딕셔너리의 리스트로 반환합니다.
    (헤더가 항목/내용 등으로 고정된 세로형 테이블 대응)
    """
    if not os.path.exists(file_path):
        return []
        
    tables = []
    current_table = {}
    
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for line in lines:
        line_str = line.strip()
        if line_str.startswith("|"):
            parts = [p.strip().replace("**", "").replace("`", "") for p in line_str.split("|")[1:-1]]
            if len(parts) >= 2:
                # 구분선이거나 첫 줄 헤더(항목, 내용 등)인 경우 건너뜀
                if parts[0] == "항목" or parts[0].startswith(":-") or parts[0] == "구분":
                    continue
                current_table[parts[0]] = parts[1]
        else:
            if current_table:
                tables.append(current_table)
                current_table = {}
                
    if current_table:
        tables.append(current_table)
        
    return tables

def get_context(novel_root, entity_names):
    """
    지정된 엔티티 이름들(예: ['강한울', 'Unit-X'])의 캐릭터 정보를 수집하여 반환합니다.
    통합 설정집 파싱 및 기존 개별 마크다운 파싱을 모두 지원합니다.
    """
    context = {}
    
    # 1. 통합 설정집 검색 후보 경로 목록 구축
    integrated_files = [
        os.path.join(novel_root, "03_줄거리", "설정_및_인물관계도.md"),
        os.path.join(novel_root, "00_설정", "02_인물_및_관계도.md")
    ]
    # 추가적으로 novel_root 밑의 "인물" 혹은 "관계도"가 들어간 마크다운 파일 검색
    for root_dir, dirs, files in os.walk(novel_root):
        for file in files:
            if file.endswith(".md") and ("인물" in file or "character" in file or "관계도" in file):
                full_path = os.path.join(root_dir, file)
                if full_path not in integrated_files:
                    integrated_files.append(full_path)
                    
    # 2. 통합 파일 파싱 적용 (헤더 파싱 방식 + 표 추출 방식 하이브리드)
    for file_path in integrated_files:
        if not os.path.exists(file_path):
            continue
            
        # 방법 A: 표(Table) 추출 파싱 방식
        tables = parse_markdown_tables_to_dict_list(file_path)
        for table in tables:
            # 인물명 혹은 이름 키 탐색
            name_key = next((k for k in table.keys() if "인물명" in k or "이름" in k or "character" in k.lower()), None)
            if name_key:
                raw_name = table[name_key]
                clean_name = re.split(r"[\s\(\:]", raw_name)[0].strip()
                
                # 타겟 캐릭터 이름 중 하나와 일치하거나 포함되는지 확인
                for name in entity_names:
                    if name in clean_name or clean_name in name:
                        context[name] = table
                        
        # 방법 B: 헤더 쪼개기 방식 (기존 SF 소설 형식 백업)
        if len(context) < len(entity_names):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                sections = re.split(r"###\s+(?:\d+\.\d+\s+)?(?:주인공:|조력자/현장 사령관:|적대자:|🔬|🤖)?\s*([a-zA-Z가-힣0-9_\-\s\(\)]+)", content)
                for i in range(1, len(sections), 2):
                    raw_name = sections[i].strip()
                    clean_name = re.split(r"[\s\(\:]", raw_name)[0].strip()
                    section_content = sections[i+1]
                    
                    table_data = {}
                    lines = section_content.strip().split("\n")
                    for line in lines:
                        line_str = line.strip()
                        if line_str.startswith("|"):
                            parts = [p.strip().replace("**", "").replace("`", "") for p in line_str.split("|")[1:-1]]
                            if len(parts) >= 2 and parts[0] != "항목" and not parts[0].startswith(":-"):
                                table_data[parts[0]] = parts[1]
                    
                    for name in entity_names:
                        if name not in context and (name in clean_name or clean_name in name):
                            context[name] = table_data
            except Exception:
                pass

    # 3. 만약 매칭되지 않은 엔티티가 있다면 기존의 Characters 디렉토리 백업 파싱 진행
    characters_dir = os.path.join(novel_root, "Vault-gurupia", "01_Wiki", "Characters")
    if os.path.exists(characters_dir):
        for name in entity_names:
            if name not in context:
                file_path = os.path.join(characters_dir, f"{name}.md")
                if os.path.exists(file_path):
                    data = parse_frontmatter(file_path)
                    if data:
                        context[name] = data
                        
    return context

def get_open_foreshadowing(novel_root):
    """
    foreshadowing.md 파일의 테이블 또는 기존 Foreshadowing 디렉토리에서 미회수 상태의 떡밥 목록을 반환합니다.
    """
    open_foreshadowing = []
    
    # 1. foreshadowing.md 테이블 기반 파싱
    foreshadowing_file = os.path.join(novel_root, "03_줄거리", "foreshadowing.md")
    if os.path.exists(foreshadowing_file):
        table_rows = parse_markdown_table_to_dicts(foreshadowing_file)
        for row in table_rows:
            # 현재 상태 열 매핑 확인 (🔴 미회수, 🟡 진행 중, OPEN, PENDING 등)
            status = row.get("현재 상태", row.get("status", ""))
            if "미회수" in status or "진행" in status or "OPEN" in status or "PENDING" in status:
                mapped_data = {
                    "id": row.get("ID", row.get("id", "")),
                    "title": row.get("복선/떡밥 내용", row.get("title", "")),
                    "appeared": row.get("최초 등장", row.get("appeared", "")),
                    "resolve_plan": row.get("회수 예정 (부/화)", row.get("resolve_plan", "")),
                    "status": "OPEN",  # 시스템 호환용 상태명 통일
                    "description": row.get("상세 설명 및 서사적 연계", row.get("description", ""))
                }
                # 호환성을 위한 엔티티 네임 부여
                mapped_data["entity_name"] = mapped_data["title"]
                open_foreshadowing.append(mapped_data)
        return open_foreshadowing
        
    # 2. 기존 개별 마크다운 백업 파싱
    foreshadowing_dir = os.path.join(novel_root, "Vault-gurupia", "01_Wiki", "Foreshadowing")
    if os.path.exists(foreshadowing_dir):
        for file_name in os.listdir(foreshadowing_dir):
            if file_name.endswith(".md"):
                file_path = os.path.join(foreshadowing_dir, file_name)
                data = parse_frontmatter(file_path)
                if data and (data.get("status") == "OPEN" or data.get("status") == "PENDING"):
                    entity_name = os.path.splitext(file_name)[0]
                    data["entity_name"] = entity_name
                    open_foreshadowing.append(data)
                    
    return open_foreshadowing

def get_episode_memory(novel_root, target_ep, window_size=3):
    """
    episode_memory.md 파일의 테이블을 파싱하여,
    target_ep 직전의 에피소드 데이터를 window_size 만큼 슬라이딩 윈도우 형태로 반환합니다.
    """
    memory_file = os.path.join(novel_root, "03_줄거리", "episode_memory.md")
    if not os.path.exists(memory_file):
        return []
        
    all_rows = parse_markdown_table_to_dicts(memory_file)
    
    try:
        target_num = int(re.findall(r"\d+", str(target_ep))[0])
    except Exception:
        return all_rows[-window_size:]
        
    previous_rows = []
    for row in all_rows:
        ep_col = row.get("회차", row.get("ep", ""))
        try:
            ep_num = int(re.findall(r"\d+", str(ep_col))[0])
            if ep_num < target_num:
                previous_rows.append((ep_num, row))
        except Exception:
            continue
            
    previous_rows.sort(key=lambda x: x[0])
    selected_rows = [item[1] for item in previous_rows[-window_size:]]
    
    return selected_rows

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    root = r"j:\eBooks\Converted_65001\[TXT소설]\창작소설\성인무협_십이경락의밤"
    print("Characters Context:", get_context(root, ["백운", "설하"]))
    print("Open Foreshadowing:", get_open_foreshadowing(root))
    print("Episode Memory (Ep 10):", get_episode_memory(root, 10, 3))

