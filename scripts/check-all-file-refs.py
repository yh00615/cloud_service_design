#!/usr/bin/env python3
"""마크다운 본문에서 참조하는 모든 파일명이 zip 폴더에 존재하는지 검증
1. DOWNLOAD 블록 파일 목록 vs 폴더
2. 본문에서 백틱으로 참조하는 파일명 vs 폴더
"""
import os
import re
import glob

CONTENT_DIR = "public/content"
FILES_DIR = "public/files"

# 파일 확장자 패턴
FILE_EXT = re.compile(r"^.+\.(yaml|yml|py|js|ts|sh|json|sql|csv|txt|html|css|drawio|env|example|md)$", re.IGNORECASE)
# zip 파일명은 제외
ZIP_PAT = re.compile(r"\.zip$")
# README는 자동 생성이므로 제외
README_PAT = re.compile(r"^README\.(md|txt)$", re.IGNORECASE)

for md_path in sorted(glob.glob(f"{CONTENT_DIR}/week*/*.md")):
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        continue
    fm = fm_match.group(1)
    week_m = re.search(r"week:\s*(\d+)", fm)
    session_m = re.search(r"session:\s*(\d+)", fm)
    if not all([week_m, session_m]):
        continue
    week = week_m.group(1)
    session = session_m.group(1)
    label = f"week{week}-{session}"

    # zip 폴더 찾기
    zip_m = re.search(r"\[.*?\]\(/files/week\d+/(week[^)]+\.zip)\)", content)
    if not zip_m:
        continue
    zip_name = zip_m.group(1)
    folder_name = zip_name.replace(".zip", "")
    target_dir = f"{FILES_DIR}/week{week}/{folder_name}"

    # 실제 폴더 내 파일 목록 (재귀, README 제외)
    actual_files = set()
    if os.path.isdir(target_dir):
        for root, dirs, files in os.walk(target_dir):
            for f in files:
                if not README_PAT.match(f):
                    actual_files.add(f)

    # DOWNLOAD 블록에서 파일명 추출
    dl_match = re.search(r"> \[!DOWNLOAD\](.*?)(?=\n[^>]|\n\n[^>]|\Z)", content, re.DOTALL)
    dl_files = set()
    if dl_match:
        dl_block = dl_match.group(1)
        for m in re.finditer(r"`([^`]+)`", dl_block):
            fname = m.group(1)
            if FILE_EXT.match(fname) and not ZIP_PAT.search(fname) and not README_PAT.match(fname):
                dl_files.add(fname)

    # 본문(DOWNLOAD 블록 이후)에서 백틱 파일명 추출
    # frontmatter 이후 본문
    body = content[fm_match.end():]
    body_files = set()
    for m in re.finditer(r"`([^`]+)`", body):
        fname = m.group(1)
        if FILE_EXT.match(fname) and not ZIP_PAT.search(fname) and not README_PAT.match(fname):
            # 서비스명이나 코드 조각 제외 (파일명처럼 보이는 것만)
            if "/" not in fname and " " not in fname:
                body_files.add(fname)

    # 합집합: DOWNLOAD + 본문에서 참조하는 모든 파일
    all_referenced = dl_files | body_files

    # 대조
    missing_in_folder = all_referenced - actual_files
    extra_in_folder = actual_files - all_referenced

    if missing_in_folder or extra_in_folder:
        print(f"\n⚠️  {label} ({os.path.basename(md_path)})")
        print(f"   폴더: {target_dir}")
        if missing_in_folder:
            for f in sorted(missing_in_folder):
                src = []
                if f in dl_files:
                    src.append("DOWNLOAD")
                if f in body_files:
                    src.append("본문")
                print(f"   ❌ 참조됨({'+'.join(src)})이지만 폴더에 없음: {f}")
        if extra_in_folder:
            for f in sorted(extra_in_folder):
                print(f"   ➕ 폴더에 있지만 어디서도 참조 안 됨: {f}")
    else:
        print(f"✅ {label}: 완전 일치 ({len(actual_files)}개)")

print("\n완료!")
