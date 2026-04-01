#!/usr/bin/env python3
import argparse
import json
import re
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SOURCE_XLSX = ROOT.parent / "泰康故事库_v260401.xlsx"
DEFAULT_OUTPUT_JS = ROOT / "data" / "story-data.js"
TARGET_DATE = "2026-08-22"

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}

SEARCH_FIELDS = [
    "故事标题",
    "故事摘要",
    "金句",
    "背景",
    "核心情节",
    "关键转折/细节",
    "结果/影响",
    "价值意义/传播价值",
    "关键人物名称",
    "地点",
    "细分地点",
]

FILTER_FIELDS = [
    "一级标签（战略概念）",
    "二级标签（业务板块）",
    "三级标签（八大关系）",
    "主角角色",
    "价值观标签",
    "是否30周年重点故事",
]


def read_shared_strings(archive):
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return [
        "".join(node.text or "" for node in item.iterfind(".//a:t", NS))
        for item in root.findall("a:si", NS)
    ]


def workbook_sheet_map(archive):
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    rel_map = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels.findall("pr:Relationship", NS)
    }
    return {
        sheet.attrib["name"]: rel_map[
            sheet.attrib[
                "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
            ]
        ]
        for sheet in workbook.find("a:sheets", NS)
    }


def column_index(cell_ref):
    match = re.match(r"[A-Z]+", cell_ref or "A1")
    value = 0
    for char in match.group(0):
        value = value * 26 + ord(char) - 64
    return value


def cell_text(cell, shared_strings):
    cell_type = cell.attrib.get("t")
    value_node = cell.find("a:v", NS)
    inline_str = cell.find("a:is", NS)

    if cell_type == "s" and value_node is not None:
        return shared_strings[int(value_node.text)]
    if cell_type == "inlineStr" and inline_str is not None:
        return "".join(node.text or "" for node in inline_str.iterfind(".//a:t", NS))
    if value_node is not None:
        return value_node.text or ""
    return ""


def load_sheet_rows(xlsx_path, sheet_name):
    with zipfile.ZipFile(xlsx_path) as archive:
        shared_strings = read_shared_strings(archive)
        sheet_map = workbook_sheet_map(archive)
        sheet_xml = ET.fromstring(archive.read(f"xl/{sheet_map[sheet_name]}"))
        rows = sheet_xml.find("a:sheetData", NS).findall("a:row", NS)

        table_rows = []
        max_col = 0
        for row in rows:
            row_map = {}
            for cell in row.findall("a:c", NS):
                idx = column_index(cell.attrib.get("r", "A1"))
                row_map[idx] = cell_text(cell, shared_strings).strip()
                max_col = max(max_col, idx)
            table_rows.append([row_map.get(idx, "") for idx in range(1, max_col + 1)])

    headers = table_rows[0]
    records = []
    for row in table_rows[1:]:
        if not any(str(value).strip() for value in row):
            continue
        record = {}
        for index, header in enumerate(headers):
            if not header:
                continue
            record[header] = row[index].strip() if index < len(row) else ""
        records.append(record)
    return records


def normalize_flag(value):
    normalized = str(value or "").strip().lower()
    return normalized in {"是", "y", "yes", "true", "1", "重点", "已标记"}


def to_chart_rows(counter, limit=None):
    items = counter.most_common(limit)
    return [{"label": key, "value": value} for key, value in items]


def parse_args():
    parser = argparse.ArgumentParser(description="从 Excel 导出泰康故事库前端数据")
    parser.add_argument("source", nargs="?", default=str(SOURCE_XLSX), help="Excel 文件路径")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_JS),
        help="输出的 story-data.js 路径",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    source_xlsx = Path(args.source).expanduser().resolve()
    output_js = Path(args.output).expanduser().resolve()

    stories = load_sheet_rows(source_xlsx, "故事库主表")

    enriched_stories = []
    for story in stories:
        enriched = dict(story)
        enriched["__isKeyStory"] = normalize_flag(story.get("是否30周年重点故事"))
        enriched["__searchText"] = " ".join(
            story.get(field, "") for field in SEARCH_FIELDS if story.get(field, "")
        ).lower()
        enriched_stories.append(enriched)

    strategic_counter = Counter(
        story.get("一级标签（战略概念）", "")
        for story in enriched_stories
        if story.get("一级标签（战略概念）", "")
    )
    location_counter = Counter(
        story.get("地点", "") for story in enriched_stories if story.get("地点", "")
    )

    filter_options = {}
    for field in FILTER_FIELDS:
        options = sorted(
            {story.get(field, "") for story in enriched_stories if story.get(field, "")}
        )
        if field == "是否30周年重点故事" and not options:
            options = ["是", "否"]
        filter_options[field] = options

    payload = {
        "meta": {
            "title": "泰康故事库仪表盘",
            "sourceFile": source_xlsx.name,
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "targetDate": TARGET_DATE,
            "totalStories": len(enriched_stories),
            "keyStories": sum(1 for story in enriched_stories if story["__isKeyStory"]),
        },
        "filters": {
            "fields": FILTER_FIELDS,
            "options": filter_options,
        },
        "charts": {
            "strategicConcepts": to_chart_rows(strategic_counter),
            "topLocations": to_chart_rows(location_counter, limit=10),
        },
        "stories": enriched_stories,
    }

    output_js.write_text(
        "window.STORY_DATA = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"Exported {len(enriched_stories)} stories to {output_js}")


if __name__ == "__main__":
    main()
