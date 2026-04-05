#!/usr/bin/env python3
"""DOWNLOAD 블록(팝오버) ↔ README.md 내용 일치 검증"""
import os
import re
import glob

CONTENT_DIR = "public/content"
FILES_DIR = "public/files"

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

    zip_m = re.search(r"\[.*?\]\(/files/week\d+/(week[^)]+\.zip)\)", content)
    if not zip_m:
        continue
    zip_name = zip_m.group(1)
    folder_name = zip_name.replace(".zip", "")
    target_dir = f"{FILES_DIR}/week{week}/{folder_name}"
    readme_path = os.path.join(target_dir, "README.md")

    if not os.path.isfile(readme_path):
        print(f"❌ {label}: README.md 없음")
        continue

    # DOWNLOAD 블록에서 파일 목록 추출
    dl_match = re.search(r"> \[!DOWNLOAD\](.*?)(?=\n[^>]|\n\n[^>]|\Z)", content, re.DOTALL)
    if not dl_match:
        continue
    dl_block = dl_match.group(1)
    dl_file_lines = [l.strip() for l in re.findall(r"^> (- `.+)$", dl_block, re.MULTILINE)]
    dl_task_lines = [l.strip() for l in re.findall(r"^> (- 태스크.+)$", dl_block, re.MULTILINE)]

    # README에서 파일 목록 / 태스크 추출
    with open(readme_path, "r", encoding="utf-8") as f:
        readme = f.read()

    readme_file_lines = []
    readme_task_lines = []
    in_files = False
    in_tasks = False
    for line in readme.splitlines():
        if line.startswith("## 포함 파일"):
            in_files = True
            in_tasks = False
            continue
        elif line.startswith("## 관련 태스크"):
            in_tasks = True
            in_files = False
            continue
        elif line.startswith("## ") or line.startswith("# "):
            in_files = False
            in_tasks = False
            continue

        stripped = line.strip()
        if in_files and stripped.startswith("- "):
            readme_file_lines.append(stripped)
        elif in_tasks and stripped.startswith("- "):
            readme_task_lines.append(stripped)

    # 비교
    issues = []
    if dl_file_lines != readme_file_lines:
        issues.append("파일 목록 불일치")
        for i, (d, r) in enumerate(zip(dl_file_lines, readme_file_lines)):
            if d != r:
                issues.append(f"  DOWNLOAD: {d}")
                issues.append(f"  README:   {r}")
        if len(dl_file_lines) != len(readme_file_lines):
            issues.append(f"  DOWNLOAD {len(dl_file_lines)}개 vs README {len(readme_file_lines)}개")

    if dl_task_lines != readme_task_lines:
        issues.append("태스크 목록 불일치")
        for i, (d, r) in enumerate(zip(dl_task_lines, readme_task_lines)):
            if d != r:
                issues.append(f"  DOWNLOAD: {d}")
                issues.append(f"  README:   {r}")
        if len(dl_task_lines) != len(readme_task_lines):
            issues.append(f"  DOWNLOAD {len(dl_task_lines)}개 vs README {len(readme_task_lines)}개")

    if issues:
        print(f"\n⚠️  {label}")
        for issue in issues:
            print(f"   {issue}")
    else:
        print(f"✅ {label}: 일치")

print("\n완료!")
