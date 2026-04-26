#!/usr/bin/env python3
"""curriculum.ts와 마크다운 frontmatter 동기화 검증

frontmatter가 정본(source of truth). 불일치 시 curriculum.ts를 수정해야 함.
검증 항목: title, awsServices, learningObjectives, markdownPath
"""
import os
import re
import json
import glob

CONTENT_DIR = "public/content"
CURRICULUM_PATH = "src/data/curriculum.ts"

def parse_frontmatter(md_path):
    """마크다운 파일에서 frontmatter 파싱"""
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return None
    fm_text = fm_match.group(1)

    result = {}
    # title
    m = re.search(r"title:\s*['\"](.+?)['\"]", fm_text)
    if m:
        result["title"] = m.group(1)
    # week
    m = re.search(r"week:\s*(\d+)", fm_text)
    if m:
        result["week"] = int(m.group(1))
    # session
    m = re.search(r"session:\s*(\d+)", fm_text)
    if m:
        result["session"] = int(m.group(1))
    # awsServices (YAML list)
    services = re.findall(r"^\s+- (.+)$", fm_text[fm_text.find("awsServices"):fm_text.find("learningObjectives") if "learningObjectives" in fm_text else len(fm_text)], re.MULTILINE) if "awsServices" in fm_text else []
    result["awsServices"] = [s.strip().strip("'\"") for s in services if s.strip()]
    # learningObjectives (YAML list)
    lo_start = fm_text.find("learningObjectives")
    if lo_start >= 0:
        # Find next top-level key or end
        remaining = fm_text[lo_start:]
        lines = remaining.split("\n")[1:]  # skip the key line
        objectives = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("- "):
                obj = stripped[2:].strip().strip("'\"")
                objectives.append(obj)
            elif stripped and not stripped.startswith("-") and not stripped.startswith("#"):
                break
        result["learningObjectives"] = objectives
    else:
        result["learningObjectives"] = []

    return result

def parse_curriculum_ts(path):
    """curriculum.ts에서 세션 데이터 추출 (정규식 기반)"""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    sessions = {}
    # markdownPath로 세션 블록 찾기
    pattern = r"markdownPath:\s*['\"]([^'\"]+)['\"]"
    for m in re.finditer(pattern, content):
        md_path = m.group(1)
        pos = m.start()

        # markdownPath 앞쪽에서 session, title 찾기 (같은 세션 블록 내)
        block_before = content[max(0, pos-300):pos]
        sess_m = re.search(r"session:\s*(\d+)", block_before)
        title_m = re.search(r"title:\s*['\"](.+?)['\"]", block_before)

        # awsServices, learningObjectives는 markdownPath 뒤쪽에서 찾기
        # (앞쪽에서 찾으면 이전 세션의 데이터를 잘못 매칭할 수 있음)
        block_after = content[m.end():m.end()+1500]

        # awsServices
        aws_m = re.search(r"awsServices:\s*\[(.*?)\]", block_after, re.DOTALL)
        aws_services = []
        if aws_m:
            aws_str = aws_m.group(1)
            aws_services = [s.strip().strip("'\"") for s in re.findall(r"['\"](.+?)['\"]", aws_str)]

        # learningObjectives
        lo_m = re.search(r"learningObjectives:\s*\[(.*?)\]", block_after, re.DOTALL)
        lo = []
        if lo_m:
            lo_str = lo_m.group(1)
            lo = [s.strip().strip("'\"").rstrip(",") for s in re.findall(r"['\"](.+?)['\"]", lo_str)]

        key = md_path
        sessions[key] = {
            "title": title_m.group(1) if title_m else "",
            "session": int(sess_m.group(1)) if sess_m else 0,
            "awsServices": aws_services,
            "learningObjectives": lo,
            "markdownPath": md_path,
        }

    return sessions

# 파싱
curriculum_sessions = parse_curriculum_ts(CURRICULUM_PATH)

# 마크다운 frontmatter와 대조
for md_path in sorted(glob.glob(f"{CONTENT_DIR}/week*/*.md")):
    fm = parse_frontmatter(md_path)
    if not fm or "week" not in fm or "session" not in fm:
        continue

    week = fm["week"]
    session = fm["session"]
    label = f"week{week}-{session}"

    # curriculum.ts에서 대응하는 세션 찾기
    rel_path = md_path.replace("public", "")  # /content/week1/1-1-tag-editor-lab.md
    curr = curriculum_sessions.get(rel_path)

    if not curr:
        print(f"❌ {label}: curriculum.ts에 markdownPath '{rel_path}' 없음")
        continue

    issues = []

    # title 비교 (의미적 일치는 수동 확인 필요, 여기서는 존재 여부만)
    if not curr["title"]:
        issues.append("curriculum.ts에 title 없음")

    # awsServices 비교
    fm_aws = set(fm.get("awsServices", []))
    curr_aws = set(curr.get("awsServices", []))
    if fm_aws != curr_aws:
        missing_in_curr = fm_aws - curr_aws
        extra_in_curr = curr_aws - fm_aws
        if missing_in_curr:
            issues.append(f"awsServices - frontmatter에만 있음: {missing_in_curr}")
        if extra_in_curr:
            issues.append(f"awsServices - curriculum에만 있음: {extra_in_curr}")

    # learningObjectives 비교
    fm_lo = fm.get("learningObjectives", [])
    curr_lo = curr.get("learningObjectives", [])
    if len(fm_lo) != len(curr_lo):
        issues.append(f"learningObjectives 개수: frontmatter {len(fm_lo)}개 vs curriculum {len(curr_lo)}개")
    else:
        for i, (f_obj, c_obj) in enumerate(zip(fm_lo, curr_lo)):
            if f_obj != c_obj:
                issues.append(f"learningObjectives[{i}] 불일치:")
                issues.append(f"  FM: {f_obj}")
                issues.append(f"  CR: {c_obj}")

    if issues:
        print(f"\n⚠️  {label} ({os.path.basename(md_path)})")
        for issue in issues:
            print(f"   {issue}")
    else:
        print(f"✅ {label}: 일치")

print("\n완료!")
