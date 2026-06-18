# 网页数据更新报告

## 1. 实际读取的主表文件

- `/Users/sariel_cxy/Desktop/codex/taikang_20_new_materials/03_final_output/泰康故事库主表_260602.xlsx`
- 已确认该文件为唯一匹配文件。
- 主表实际有效故事数：117 条。
- 主表最后编号：`TK-00117`。
- 主表包含 `TK-00085` 至 `TK-00117`。
- 主表不包含 `TK-00118`。
- `TK-00026` 标题为：`郑洞天：把“晚年剧本”交给燕园，在电影与沙龙中重生`，已是合并 `NEW-034` 后版本。
- 未发现 `NEW-034` 独立故事行。

## 2. 实际更新的数据文件

- `data/story-data.js`
- `story-dashboard/data/story-data.js`

两份数据文件均已由 `泰康故事库主表_260602.xlsx` 重新导出。

## 3. 是否更新 data/story-data.js

- 是。
- 更新前最后编号：`TK-00084`。
- 更新后最后编号：`TK-00117`。
- 更新后故事总数：117 条。

## 4. 是否更新 story-dashboard/data/story-data.js

- 是。
- 更新前最后编号：`TK-00084`。
- 更新后最后编号：`TK-00117`。
- 更新后故事总数：117 条。

## 5. 是否隐藏“数据来源”和“最新修改时间”

- 是。
- 已在 `index.html` 中隐藏顶部 `hero-meta` 信息卡。
- 已在 `story-dashboard/index.html` 中隐藏顶部 `hero-meta` 信息卡。
- 数据字段仍保留在 `story-data.js` 的 `meta` 中，前端页面不再展示该信息卡。

## 6. 是否保留“来源标题”“来源链接”“原文”等故事字段

- 是。
- 未修改故事卡详情页字段展示逻辑。
- `来源标题`、`来源链接`、`原文` 字段仍存在于网页数据中。

## 7. 更新前网页数据最后编号

- `data/story-data.js`：`TK-00084`
- `story-dashboard/data/story-data.js`：`TK-00084`

## 8. 更新后网页数据最后编号

- `data/story-data.js`：`TK-00117`
- `story-dashboard/data/story-data.js`：`TK-00117`

## 9. 网页数据是否包含 TK-00085 至 TK-00117

- 是。
- 两份 `story-data.js` 均完整包含 `TK-00085` 至 `TK-00117`。

## 10. 网页数据是否不包含 TK-00118

- 是。
- 两份 `story-data.js` 均未发现 `TK-00118`。

## 11. TK-00026 是否为合并 NEW-034 后版本

- 是。
- 网页数据中 `TK-00026` 标题为：`郑洞天：把“晚年剧本”交给燕园，在电影与沙龙中重生`。

## 12. 是否发现字段缺失或字段映射问题

- 未发现影响网页展示的字段映射问题。
- 说明：`泰康故事库主表_260602.xlsx` 当前表头实际为 34 个正式字段；导出脚本沿用既有兼容逻辑，将 `一级标签（总领概念）` 映射为前端使用的 `一级标签（战略概念）`。
- 未新增 `A/B/C/D` 分类字段。
- 未新增 `入库形态` 字段。
- `金句` 字段已同步；空值保持为空。

## 13. 是否发现原文模板残留

- 未发现。
- 对 `TK-00105` 至 `TK-00117` 的 `原文` 字段检查，未发现 `武汉大学泰康生命医学中心` 模板残留。

## 14. git diff --name-only 结果

```text
data/story-data.js
index.html
story-dashboard/data/story-data.js
story-dashboard/index.html
```

## 15. 是否可以进入本地预览检查

- 已完成本地静态预览检查。
- 临时 HTTP 服务可正常访问：
  - `/`
  - `/data/story-data.js`
  - `/story-dashboard/`
  - `/story-dashboard/data/story-data.js`
- 故事总数与主表一致：117 条。
- `TK-00026` 可在数据中检索到合并后内容。
- `TK-00117` 可在数据中检索到。
- `TK-00118` 无结果。
- `金句` 字段存在并正常同步。
- `原文` 字段存在并正常同步。
- `数据来源` 与 `最新修改时间/最近生成` 信息卡已隐藏。
- 标签筛选字段仍保留，筛选选项非空。

## 16. 其他说明

- 本轮只修改网页数据文件和必要的前端展示文件。
- 未修改 Excel、Word、`story-data.js` 以外的数据源文件。
- 未修改 `story-cards.html`、`assets/story-cards.js` 或筛选逻辑。
- 未自动提交 git。
- 当前 `git status --short` 中存在若干未跟踪文件，均为本轮开始前已存在的项目文件/备份文件，本轮未处理。
