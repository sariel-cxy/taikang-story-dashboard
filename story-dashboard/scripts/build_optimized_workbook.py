#!/usr/bin/env python3
import argparse
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

from export_excel import load_sheet_rows


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT.parent / "泰康故事库_v260401.xlsx"
DEFAULT_OUTPUT = ROOT.parent / "泰康故事库_持续入库模板_v260401.xlsx"

MAIN_HEADERS = [
    "编号",
    "故事标题",
    "故事摘要",
    "一级标签（战略概念）",
    "二级标签（业务板块）",
    "场景标签",
    "三级标签（八大关系）",
    "四级标签（叙事类型）",
    "主角角色",
    "协同角色",
    "关键人物名称",
    "人物主题标签",
    "价值观标签",
    "重要程度",
    "是否30周年重点故事",
    "是否适合对外传播",
    "传播用途标签",
    "时间（仅开始年份）",
    "地点",
    "细分地点",
    "金句",
    "背景",
    "核心情节",
    "关键转折/细节",
    "结果/影响",
    "价值意义/传播价值",
    "关联故事",
    "来源标题",
    "来源类型",
    "来源链接",
    "故事提供者",
    "首次发布时间",
    "备注",
]

KEY_TAG_FIELDS = ["重要程度", "是否30周年重点故事", "是否适合对外传播", "传播用途标签"]

GUIDE_ROWS = [
    ["模块", "内容"],
    ["建议工作流", "1. 先新增故事基础信息；2. 再补核心标签；3. 最后检查可传播级别与用途标签；4. 更新网页数据。"],
    ["建议必填字段", "编号、故事标题、故事摘要、时间（仅开始年份）、一级标签、二级标签、主角角色、地点。"],
    ["建议第二轮补齐字段", "三级标签、价值观标签、重要程度、是否30周年重点故事、是否适合对外传播、传播用途标签。"],
    ["编号规范", "建议连续编号，例如 TK-00032。不要重复，不要跳号过多。"],
    ["标签原则", "单选字段只填一个标准值；多选字段用中文顿号“ / ”分隔，并保持口径一致。"],
    ["网页同步", "每次更新 Excel 后，运行 python3 story-dashboard/scripts/export_excel.py 'Excel路径'。"],
    ["版本管理", "建议以日期保存版本，例如 泰康故事库_v260405.xlsx。大版本保留，小修订可覆盖当前工作版。"],
]

TAXONOMY_ROWS = [
    ["标签组", "标准值", "是否单选", "建议规则", "备注"],
    ["一级标签（战略概念）", "长寿时代 / 新寿险 / 医养康宁 / 三端协同", "是", "优先选最能代表故事母题的一项", ""],
    ["二级标签（业务板块）", "人寿 / 养老 / 在线 / 资产 / 之家 / 医疗 / 口腔 / 公益", "是", "优先选择故事归属的业务主体", ""],
    ["场景标签", "养老社区 / 医院 / 健康服务 / 纪念园 / 乡村振兴 / 支付理赔 / 财富管理 / 商业洞见", "是", "没有合适选项时再补充新词，并同步更新词表", ""],
    ["三级标签（八大关系）", "党政关系 / 地区关系 / 行业关系 / 法律关系 / 媒体关系 / 员工关系 / 客户关系 / 投资者关系", "是", "按故事主要作用对象选择", ""],
    ["四级标签（叙事类型）", "创业故事 / 战略故事 / 转型故事 / 服务故事 / 创新故事 / 品牌故事 / 治理故事 / 公益故事 / 文化故事 / 风险应对故事", "否", "建议 1-2 个", "多选时使用 / 分隔"],
    ["主角角色", "创始人 / 高管 / HWP（健康财富规划师） / 金融人 / 一线员工 / 客户", "是", "只选第一主角", ""],
    ["协同角色", "创始人 / 高管 / HWP（健康财富规划师） / 金融人 / 一线员工 / 客户", "否", "辅助角色可多选", "多选时使用 / 分隔"],
    ["人物主题标签", "家庭与成长 / 创业与起步 / 战略思想 / 公益与责任 / 关键决策 / 行业影响 / 时代判断 / 领导风格 / 管理实践 / 战略执行 / 业务创新 / 专业表达 / 团队带领 / 关键应对 / 人生转折 / 真实受益 / 全生命周期服务 / 需求洞察 / 价值传递 / 团队协作 / 日常坚守", "否", "用于专题策划时补充检索维度", "多选时使用 / 分隔"],
    ["价值观标签", "尊重生命 / 关爱生命 / 礼赞生命 / 初心不改 / 创新永续 / 商业向善 / 以人为本 / 敢打敢拼 / 不畏艰辛 / 爱司敬业 / 战无不胜", "否", "建议 1-2 个", "多选时使用 / 分隔"],
    ["重要程度", "S / A / B / C", "是", "S 为可进入核心汇报池；A 为重点故事；B 为可用；C 为待完善", ""],
    ["是否30周年重点故事", "是 / 否 / 备选", "是", "优先只用这三个值，不要混用 Y/N", ""],
    ["是否适合对外传播", "公开可用 / 待内部审批 / 内部参考 / 敏感待审", "是", "对外传播前优先筛选公开可用", ""],
    ["传播用途标签", "周年册 / 领导讲话 / 短视频 / 海报长图 / 媒体采访 / 党建文化 / 展厅展陈 / 案例研究 / 公众号专题", "否", "面向具体项目时补齐", "多选时使用 / 分隔"],
]


def parse_args():
    parser = argparse.ArgumentParser(description="生成适合持续入库和补标签的 Excel 模板")
    parser.add_argument("source", nargs="?", default=str(DEFAULT_SOURCE), help="原始 Excel 路径")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="输出 Excel 路径")
    return parser.parse_args()


def normalize_record(record):
    return [str(record.get(header, "") or "") for header in MAIN_HEADERS]


def build_backlog_rows(records):
    rows = [["编号", "故事标题", "缺失字段", "建议下一步"]]
    for record in records:
        missing = [field for field in KEY_TAG_FIELDS if not str(record.get(field, "") or "").strip()]
        if not missing:
            continue
        suggestion = "先补齐 " + "、".join(missing[:2])
        if "是否适合对外传播" in missing:
            suggestion = "先判断传播级别，再补传播用途"
        rows.append(
            [
                str(record.get("编号", "")),
                str(record.get("故事标题", "")),
                " / ".join(missing),
                suggestion,
            ]
        )
    return rows


def col_name(index):
    result = []
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        result.append(chr(65 + remainder))
    return "".join(reversed(result))


def inline_cell(ref, value):
    text = escape("" if value is None else str(value))
    return f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{text}</t></is></c>'


def worksheet_xml(rows):
    row_xml = []
    max_col = max((len(row) for row in rows), default=1)
    for row_idx, row in enumerate(rows, start=1):
        cells = []
        for col_idx, value in enumerate(row):
            if value == "":
                continue
            ref = f"{col_name(col_idx)}{row_idx}"
            cells.append(inline_cell(ref, value))
        row_xml.append(f'<row r="{row_idx}">{"".join(cells)}</row>')
    dim = f"A1:{col_name(max_col - 1)}{max(len(rows), 1)}"
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <dimension ref="{dim}"/>
  <sheetViews><sheetView workbookViewId="0"/></sheetViews>
  <sheetFormatPr defaultRowHeight="15"/>
  <sheetData>{"".join(row_xml)}</sheetData>
</worksheet>
'''


def content_types():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet3.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet4.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
'''


def root_rels():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
'''


def workbook_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <fileVersion appName="xl"/>
  <bookViews><workbookView xWindow="0" yWindow="0" windowWidth="24000" windowHeight="12000"/></bookViews>
  <sheets>
    <sheet name="录入说明" sheetId="1" r:id="rId1"/>
    <sheet name="故事库主表" sheetId="2" r:id="rId2"/>
    <sheet name="标签词表" sheetId="3" r:id="rId3"/>
    <sheet name="待补标签清单" sheetId="4" r:id="rId4"/>
  </sheets>
</workbook>
'''


def workbook_rels():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet3.xml"/>
  <Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet4.xml"/>
  <Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>
'''


def styles_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>
  <fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>
'''


def app_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex</Application>
</Properties>
'''


def core_xml():
    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{created}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{created}</dcterms:modified>
</cp:coreProperties>
'''


def build_workbook(source_path, output_path):
    records = load_sheet_rows(source_path, "故事库主表")
    main_rows = [MAIN_HEADERS] + [normalize_record(record) for record in records]
    backlog_rows = build_backlog_rows(records)

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
      archive.writestr("[Content_Types].xml", content_types())
      archive.writestr("_rels/.rels", root_rels())
      archive.writestr("docProps/app.xml", app_xml())
      archive.writestr("docProps/core.xml", core_xml())
      archive.writestr("xl/workbook.xml", workbook_xml())
      archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels())
      archive.writestr("xl/styles.xml", styles_xml())
      archive.writestr("xl/worksheets/sheet1.xml", worksheet_xml(GUIDE_ROWS))
      archive.writestr("xl/worksheets/sheet2.xml", worksheet_xml(main_rows))
      archive.writestr("xl/worksheets/sheet3.xml", worksheet_xml(TAXONOMY_ROWS))
      archive.writestr("xl/worksheets/sheet4.xml", worksheet_xml(backlog_rows))


def main():
    args = parse_args()
    source_path = Path(args.source).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    build_workbook(source_path, output_path)
    print(f"Generated optimized workbook: {output_path}")


if __name__ == "__main__":
    main()
