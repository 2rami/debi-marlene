"""
SRT 자막 파일 정리 스크립트
- 중복/겹침 대사 제거
- 타임스탬프 제거하고 순수 텍스트만 추출
- 결과를 txt로 저장
"""
import re
import os

RAW_DIR = os.path.join(os.path.dirname(__file__), "raw_data")


def parse_srt(filepath: str) -> list[dict]:
    """SRT 파일을 파싱해서 (start_ms, text) 리스트로 반환"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)",
        re.DOTALL
    )

    entries = []
    for m in pattern.finditer(content):
        start_str = m.group(2)
        text = m.group(4).strip().replace("\n", " ")
        if not text:
            continue

        # 타임스탬프 -> ms
        h, mi, rest = start_str.split(":")
        s, ms = rest.split(",")
        start_ms = int(h) * 3600000 + int(mi) * 60000 + int(s) * 1000 + int(ms)

        entries.append({"start_ms": start_ms, "text": text})

    return entries


def deduplicate(entries: list[dict], overlap_threshold_ms: int = 2000) -> list[str]:
    """
    겹치는 자막 합치기 + 중복 제거
    자동 자막은 같은 대사가 여러 청크에 걸쳐 나옴
    """
    if not entries:
        return []

    entries.sort(key=lambda x: x["start_ms"])

    lines = []
    prev_text = ""

    for entry in entries:
        text = entry["text"].strip()
        if not text:
            continue

        # 이전 텍스트와 완전 동일하면 스킵
        if text == prev_text:
            continue

        # 이전 텍스트가 현재 텍스트에 포함되면 (더 긴 버전으로 교체)
        if prev_text and prev_text in text:
            if lines:
                lines[-1] = text
            prev_text = text
            continue

        # 현재 텍스트가 이전 텍스트에 포함되면 스킵
        if prev_text and text in prev_text:
            continue

        lines.append(text)
        prev_text = text

    return lines


def process_file(srt_path: str, output_name: str):
    """SRT -> 정리된 txt"""
    print(f"[*] Processing: {os.path.basename(srt_path)}")

    entries = parse_srt(srt_path)
    print(f"    Raw entries: {len(entries)}")

    lines = deduplicate(entries)
    print(f"    After dedup: {len(lines)}")

    output_path = os.path.join(RAW_DIR, output_name)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"    Saved: {output_path}")
    return lines


def main():
    all_lines = []

    # Video 1
    srt1 = os.path.join(RAW_DIR, "video1_quotes.ko.srt")
    if os.path.exists(srt1):
        lines1 = process_file(srt1, "video1_cleaned.txt")
        all_lines.extend(lines1)

    # Video 2
    srt2 = os.path.join(RAW_DIR, "video2_quotes.ko.srt")
    if os.path.exists(srt2):
        lines2 = process_file(srt2, "video2_cleaned.txt")
        all_lines.extend(lines2)

    # 전체 합본
    combined_path = os.path.join(RAW_DIR, "all_quotes_combined.txt")
    with open(combined_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_lines))

    print(f"\n=== Total: {len(all_lines)} lines saved to all_quotes_combined.txt ===")


if __name__ == "__main__":
    main()
