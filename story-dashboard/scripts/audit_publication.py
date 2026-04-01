#!/usr/bin/env python3
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "story-data.js"

CHECK_FIELDS = [
    "来源链接",
    "关键人物名称",
    "故事提供者",
    "备注",
    "金句",
    "背景",
    "核心情节",
]


def main():
    text = DATA_FILE.read_text(encoding="utf-8")
    print(f"检查文件: {DATA_FILE}")
    print()

    has_http = "http://" in text or "https://" in text
    has_phone = bool(re.search(r"1[3-9]\d{9}", text))
    has_email = bool(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text))

    print("基础检查")
    print(f"- 包含外部链接: {'是' if has_http else '否'}")
    print(f"- 包含手机号痕迹: {'是' if has_phone else '否'}")
    print(f"- 包含邮箱痕迹: {'是' if has_email else '否'}")
    print()

    print("敏感字段存在性")
    for field in CHECK_FIELDS:
      print(f"- {field}: {'存在' if field in text else '未发现字段名'}")
    print()

    print("建议判断")
    if has_http or any(field in text for field in ["来源链接", "故事提供者", "备注"]):
      print("- 当前数据更适合作为内部工作版，不建议直接公开发布。")
      print("- 如需公开，请先制作公开版数据。")
    else:
      print("- 当前数据未发现明显高风险字段，但仍建议人工复核。")


if __name__ == "__main__":
    main()
