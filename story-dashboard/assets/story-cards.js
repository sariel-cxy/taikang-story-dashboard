(function () {
  const data = window.STORY_DATA;
  const container = document.querySelector("#story-cards-list");
  const exportButton = document.querySelector("#export-tag-overrides");
  const clearButton = document.querySelector("#clear-tag-overrides");
  const statusNode = document.querySelector("#tag-export-status");
  if (!data || !container) {
    return;
  }

  const LOCAL_TAG_KEY = "taikang-story-tag-overrides-v1";
  const TAG_FIELDS = {
    "重要程度": ["", "S", "A", "B", "C"],
    "是否30周年重点故事": ["", "是", "否", "备选"],
    "是否适合对外传播": ["", "公开可用", "待内部审批", "内部参考", "敏感待审"],
  };
  const FIELD_GROUPS = [
    ["故事摘要", true],
    ["一级标签（战略概念）", false],
    ["二级标签（业务板块）", false],
    ["三级标签（八大关系）", false],
    ["四级标签（叙事类型）", false],
    ["主角角色", false],
    ["协同角色", false],
    ["关键人物名称", false],
    ["人物主题标签", false],
    ["价值观标签", false],
    ["传播用途标签", false],
    ["时间（仅开始年份）", false],
    ["地点", false],
    ["细分地点", false],
    ["金句", true],
    ["背景", true],
    ["核心情节", true],
    ["关键转折/细节", true],
    ["结果/影响", true],
    ["价值意义/传播价值", true],
    ["关联故事", true],
    ["来源标题", true],
    ["来源类型", false],
    ["来源链接", true],
    ["故事提供者", false],
    ["首次发布时间", false],
    ["备注", true],
  ];

  function readOverrides() {
    try {
      return JSON.parse(window.localStorage.getItem(LOCAL_TAG_KEY) || "{}");
    } catch {
      return {};
    }
  }

  function writeOverrides(overrides) {
    window.localStorage.setItem(LOCAL_TAG_KEY, JSON.stringify(overrides));
  }

  function escapeHtml(value) {
    return String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function csvCell(value) {
    const text = String(value || "").replaceAll('"', '""');
    return `"${text}"`;
  }

  function currentStories() {
    const overrides = readOverrides();
    return data.stories.map((story) => ({ ...story, ...(overrides[story["编号"]] || {}) }));
  }

  function tagList(story) {
    return [
      story["一级标签（战略概念）"],
      story["二级标签（业务板块）"],
      story["三级标签（八大关系）"],
      story["主角角色"],
      story["价值观标签"],
    ].filter(Boolean);
  }

  function renderField(label, value, spanTwo) {
    if (!value) {
      return "";
    }

    if (label === "来源链接") {
      return `
        <div class="story-field ${spanTwo ? "span-2" : ""}">
          <p class="story-field-label">${escapeHtml(label)}</p>
          <p class="story-field-value"><a class="story-source-link" href="${escapeHtml(value)}" target="_blank" rel="noreferrer">打开原始链接</a></p>
        </div>
      `;
    }

    return `
      <div class="story-field ${spanTwo ? "span-2" : ""}">
        <p class="story-field-label">${escapeHtml(label)}</p>
        <p class="story-field-value">${escapeHtml(value)}</p>
      </div>
    `;
  }

  function renderTagEditor(story) {
    const selects = Object.entries(TAG_FIELDS)
      .map(([field, options]) => {
        const optionHtml = options
          .map((option) => {
            const label = option || "未填写";
            const selected = option === (story[field] || "") ? ' selected' : "";
            return `<option value="${escapeHtml(option)}"${selected}>${escapeHtml(label)}</option>`;
          })
          .join("");
        return `
          <div class="tag-editor-field">
            <label for="tag-${story["编号"]}-${field}">${escapeHtml(field)}</label>
            <select class="story-tag-select" id="tag-${story["编号"]}-${field}" data-story-id="${escapeHtml(story["编号"])}" data-field="${escapeHtml(field)}">
              ${optionHtml}
            </select>
          </div>
        `;
      })
      .join("");

    return `
      <section class="story-tag-editor">
        <h3>网页快速打标签</h3>
        <div class="tag-editor-grid">${selects}</div>
        <p class="tag-editor-hint">变更会保存在当前浏览器，可导出为 CSV 后回填 Excel。</p>
      </section>
    `;
  }

  function updateStatus() {
    const overrides = readOverrides();
    const count = Object.keys(overrides).length;
    statusNode.textContent =
      count > 0 ? `当前有 ${count} 条故事存在网页侧标签变更` : "当前没有网页侧标签变更";
  }

  function renderCards() {
    const stories = currentStories();
    container.innerHTML = stories
      .map((story) => {
        const tags = tagList(story)
          .map((tag) => `<span class="story-tag">${escapeHtml(tag)}</span>`)
          .join("");
        const fields = FIELD_GROUPS.map(([field, spanTwo]) => renderField(field, story[field], spanTwo)).join("");
        return `
          <article class="story-card" id="story-${story["编号"]}">
            <div class="story-card-header">
              <div>
                <p class="story-card-id">${escapeHtml(story["编号"] || "")}</p>
                <h2 class="story-card-title">${escapeHtml(story["故事标题"] || "")}</h2>
              </div>
              <div class="story-card-tags">${tags}</div>
            </div>
            ${renderTagEditor(story)}
            <div class="story-card-grid">${fields}</div>
            <div class="story-card-footer">
              <a class="inline-link" href="./index.html">返回仪表盘</a>
              <span class="story-card-id">${escapeHtml(story["首次发布时间"] || "")}</span>
            </div>
          </article>
        `;
      })
      .join("");

    container.querySelectorAll(".story-tag-select").forEach((select) => {
      select.addEventListener("change", onTagChange);
    });

    updateStatus();
  }

  function onTagChange(event) {
    const storyId = event.target.dataset.storyId;
    const field = event.target.dataset.field;
    const value = event.target.value;
    const sourceStory = data.stories.find((story) => story["编号"] === storyId);
    const overrides = readOverrides();
    const next = { ...(overrides[storyId] || {}) };

    if (value === (sourceStory[field] || "")) {
      delete next[field];
    } else {
      next[field] = value;
    }

    if (Object.keys(next).length === 0) {
      delete overrides[storyId];
    } else {
      overrides[storyId] = next;
    }

    writeOverrides(overrides);
    updateStatus();
  }

  function exportOverrides() {
    const overrides = readOverrides();
    const rows = [["编号", "故事标题", "重要程度", "是否30周年重点故事", "是否适合对外传播"]];
    data.stories.forEach((story) => {
      const changed = overrides[story["编号"]];
      if (!changed) {
        return;
      }
      rows.push([
        story["编号"],
        story["故事标题"],
        changed["重要程度"] ?? story["重要程度"] ?? "",
        changed["是否30周年重点故事"] ?? story["是否30周年重点故事"] ?? "",
        changed["是否适合对外传播"] ?? story["是否适合对外传播"] ?? "",
      ]);
    });

    const csv = "\uFEFF" + rows.map((row) => row.map(csvCell).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "泰康故事库_网页补标导出.csv";
    link.click();
    URL.revokeObjectURL(link.href);
  }

  exportButton.addEventListener("click", exportOverrides);
  clearButton.addEventListener("click", () => {
    window.localStorage.removeItem(LOCAL_TAG_KEY);
    renderCards();
  });

  renderCards();

  if (window.location.hash) {
    const target = document.querySelector(window.location.hash);
    if (target) {
      target.style.outline = "3px solid rgba(15, 118, 110, 0.22)";
      target.style.outlineOffset = "4px";
    }
  }
})();
