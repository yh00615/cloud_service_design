#!/usr/bin/env python3
"""DOWNLOAD 블록 기준으로 README.md 생성"""
import os
import re
import glob

CONTENT_DIR = "public/content"
FILES_DIR = "public/files"

for md_path in sorted(glob.glob(f"{CONTENT_DIR}/week*/*.md")):
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # frontmatter 파싱
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        continue
    fm = fm_match.group(1)

    title_m = re.search(r"title:\s*['\"](.+?)['\"]", fm)
    week_m = re.search(r"week:\s*(\d+)", fm)
    session_m = re.search(r"session:\s*(\d+)", fm)
    if not all([title_m, week_m, session_m]):
        continue

    title = title_m.group(1)
    week = week_m.group(1)
    session = session_m.group(1)

    # DOWNLOAD 블록에서 zip 파일명 추출
    zip_m = re.search(r"\[.*?\]\(/files/week\d+/(week[^)]+\.zip)\)", content)
    if not zip_m:
        continue
    zip_name = zip_m.group(1)
    folder_name = zip_name.replace(".zip", "")
    target_dir = f"{FILES_DIR}/week{week}/{folder_name}"

    if not os.path.isdir(target_dir):
        print(f"SKIP (no folder): {target_dir}")
        continue

    # DOWNLOAD 블록 추출
    dl_match = re.search(r"> \[!DOWNLOAD\](.*?)(?=\n[^>]|\n\n[^>]|\Z)", content, re.DOTALL)
    if not dl_match:
        continue
    dl_block = dl_match.group(1)

    # 파일 목록 추출
    file_lines = re.findall(r"^> (- `.+)$", dl_block, re.MULTILINE)

    # 관련 태스크 추출
    task_lines = re.findall(r"^> (- 태스크.+)$", dl_block, re.MULTILINE)

    # README 생성
    readme_path = os.path.join(target_dir, "README.md")
    lines = [f"# Week {week}-{session}: {title}", "", "## 포함 파일", ""]
    for fl in file_lines:
        lines.append(fl)
    lines.append("")
    lines.append("## 관련 태스크")
    lines.append("")
    for tl in task_lines:
        lines.append(tl)
    lines.append("")

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ {readme_path}")

print("\nDone!")
