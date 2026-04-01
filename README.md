# 泰康故事库仪表盘

这是一个纯静态 HTML 仪表盘，适合做内部汇报、检索和后续版本管理。

## 目录结构

- `index.html`: 主页面
- `story-cards.html`: 故事卡页面
- `assets/styles.css`: 页面样式
- `assets/app.js`: 仪表盘交互逻辑
- `assets/story-cards.js`: 故事卡页面交互逻辑
- `scripts/update_site_data.sh`: 一键更新网页数据
- `scripts/export_excel.py`: 从 Excel 导出前端数据
- `scripts/build_optimized_workbook.py`: 生成持续入库模板
- `scripts/audit_publication.py`: 发布前检查数据是否适合公开
- `data/story-data.js`: 导出的数据文件
- `.nojekyll`: GitHub Pages 发布兼容文件
- `PUBLICATION_CHECKLIST.md`: GitHub 公开发布检查清单

## 如何更新数据

优先使用一键脚本：

```bash
./scripts/update_site_data.sh
```

如果 Excel 文件名或路径变了，可以显式指定：

```bash
./scripts/update_site_data.sh '/你的/Excel路径.xlsx'
```

如果你想自定义页面里的“数据来源”显示名，可以传第二个参数：

```bash
./scripts/update_site_data.sh '/你的/Excel路径.xlsx' '泰康故事库工作版'
```

它内部会自动调用 `scripts/export_excel.py`，并刷新 `data/story-data.js`。

然后直接双击打开 `index.html`，或把改动提交到 GitHub Pages。

## 如何生成持续入库模板

运行：

```bash
python3 scripts/build_optimized_workbook.py '/你的/Excel路径.xlsx'
```

默认会生成一个带有 `录入说明`、`标签词表`、`待补标签清单` 的新 Excel。

## 当前实现

- 首页核心指标
- 多标签筛选
- 关键词模糊搜索
- 战略概念条形图和饼图
- 业务板块分布，自动适配最新标签值
- 八大关系分布，自动适配最新标签值
- 主角角色分布
- 时间分布（2006年及以前 / 2007-2016年 / 2017-2026年）
- 地点 Top 10 条形图
- 故事列表
- 故事卡页面，可从列表标题跳转
- 故事卡页面支持网页侧补 3 个标签，并导出 CSV

## 网页补标签流程

1. 打开 `story-cards.html`
2. 在每条故事卡中补这 3 个字段：
   - `重要程度`
   - `是否30周年重点故事`
   - `是否适合对外传播`
3. 点击“导出标签变更 CSV”
4. 将导出的 CSV 回填到 Excel 主表

网页侧补标会先保存在当前浏览器，本地可反映到首页图表和指标，但不会自动写回 Excel。

## GitHub Pages 推荐目录结构

如果这个仓库专门用于发布仪表盘，推荐直接把当前目录内容作为仓库根目录：

```text
story-dashboard/
├── index.html
├── story-cards.html
├── assets/
├── data/
├── scripts/
├── README.md
├── .gitignore
└── .nojekyll
```

这样最简单，GitHub Pages 可以直接把仓库根目录作为静态站点发布。

## GitHub Pages 发布步骤

1. 新建一个 GitHub 仓库，例如 `taikang-story-dashboard`
2. 将当前目录中的文件上传到仓库根目录
3. 进入 GitHub 仓库页面
4. 打开 `Settings`
5. 打开左侧 `Pages`
6. 在 `Build and deployment` 中选择：
   - `Source`: `Deploy from a branch`
   - `Branch`: `main`
   - 文件夹选择 `/ (root)`
7. 保存后等待 GitHub 发布
8. 发布成功后，访问：

```text
https://你的GitHub用户名.github.io/仓库名/
```

如果仓库名是 `taikang-story-dashboard`，链接通常会是：

```text
https://你的GitHub用户名.github.io/taikang-story-dashboard/
```

## 更新发布内容

1. 本地更新 Excel
2. 运行：

```bash
./scripts/update_site_data.sh '/你的/Excel路径.xlsx'
```

3. 把更新后的 `data/story-data.js` 连同其他改动一起提交到 GitHub
4. GitHub Pages 会自动刷新站点内容

## 注意事项

- GitHub Pages 发布的是静态文件，所以 `data/story-data.js` 中的数据会被访问者看到
- 网页补标签功能目前只保存在访问者自己的浏览器本地，不会自动同步到 GitHub
- 如果要让多人共享网页补标结果，需要单独加后台，不属于当前 GitHub Pages 方案
- 发布前建议先看 `PUBLICATION_CHECKLIST.md`，并运行：

```bash
python3 scripts/audit_publication.py
```

## 本地演示

在目录下运行：

```bash
python3 -m http.server 8000
```
