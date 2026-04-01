(function () {
  const data = window.STORY_DATA;
  if (!data) {
    return;
  }

  const LOCAL_TAG_KEY = "taikang-story-tag-overrides-v1";
  const FILTER_LABELS = {
    "一级标签（战略概念）": "战略概念",
    "二级标签（业务板块）": "业务板块",
    "三级标签（八大关系）": "八大关系",
    "主角角色": "主角角色",
    "价值观标签": "价值观标签",
    "是否30周年重点故事": "30周年重点故事",
  };
  const TIME_BUCKETS = [
    { label: "2006年及以前", min: -Infinity, max: 2006 },
    { label: "2007-2016年", min: 2007, max: 2016 },
    { label: "2017-2026年", min: 2017, max: 2026 },
  ];
  const PIE_COLORS = ["#0f766e", "#114b5f", "#d97706", "#8b5cf6", "#2563eb", "#65a30d"];

  const rawStories = applyTagOverrides(data.stories);
  const filterOptions = buildFilterOptions(rawStories);

  const state = {
    keyword: "",
    filters: Object.fromEntries(data.filters.fields.map((field) => [field, ""])),
  };

  const elements = {
    sourceFile: document.querySelector("#source-file"),
    generatedAt: document.querySelector("#generated-at"),
    metricTotal: document.querySelector("#metric-total"),
    metricCountdown: document.querySelector("#metric-countdown"),
    metricKeyStories: document.querySelector("#metric-key-stories"),
    filtersGrid: document.querySelector("#filters-grid"),
    keywordInput: document.querySelector("#keyword-input"),
    resultSummary: document.querySelector("#result-summary"),
    resetButton: document.querySelector("#reset-filters"),
    strategicBarChart: document.querySelector("#strategic-bar-chart"),
    strategicPieChart: document.querySelector("#strategic-pie-chart"),
    locationBarChart: document.querySelector("#location-bar-chart"),
    businessBarChart: document.querySelector("#business-bar-chart"),
    relationBarChart: document.querySelector("#relation-bar-chart"),
    roleBarChart: document.querySelector("#role-bar-chart"),
    timeBarChart: document.querySelector("#time-bar-chart"),
    timePieChart: document.querySelector("#time-pie-chart"),
    tableBody: document.querySelector("#story-table-body"),
  };

  function readOverrides() {
    try {
      return JSON.parse(window.localStorage.getItem(LOCAL_TAG_KEY) || "{}");
    } catch {
      return {};
    }
  }

  function normalizeTagValue(value) {
    return String(value || "").trim();
  }

  function normalizeSearchText(story) {
    const fields = [
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
      "重要程度",
      "是否30周年重点故事",
      "是否适合对外传播",
    ];
    return fields
      .map((field) => normalizeTagValue(story[field]))
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
  }

  function applyTagOverrides(stories) {
    const overrides = readOverrides();
    return stories.map((story) => {
      const override = overrides[story["编号"]] || {};
      const merged = { ...story, ...override };
      merged.__isKeyStory = isKeyStory(merged["是否30周年重点故事"]);
      merged.__searchText = normalizeSearchText(merged);
      return merged;
    });
  }

  function buildFilterOptions(stories) {
    const options = {};
    data.filters.fields.forEach((field) => {
      const values = new Set();
      stories.forEach((story) => {
        const value = normalizeTagValue(story[field]);
        if (value) {
          values.add(value);
        }
      });
      if (field === "是否30周年重点故事") {
        values.add("是");
        values.add("否");
        values.add("备选");
      }
      options[field] = [...values].sort((a, b) => a.localeCompare(b, "zh-CN"));
    });
    return options;
  }

  function formatDate(isoString) {
    const date = new Date(isoString);
    return new Intl.DateTimeFormat("zh-CN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  }

  function countdownDays(targetDate) {
    const target = new Date(`${targetDate}T00:00:00`);
    return Math.ceil((target.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
  }

  function isKeyStory(value) {
    return ["是", "y", "yes", "true", "1", "重点", "已标记"].includes(
      String(value || "").trim().toLowerCase()
    );
  }

  function escapeHtml(value) {
    return String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function extractYear(value) {
    const match = String(value || "").match(/\d{4}/);
    return match ? Number(match[0]) : null;
  }

  function renderFilters() {
    elements.filtersGrid.innerHTML = "";
    data.filters.fields.forEach((field) => {
      const wrapper = document.createElement("label");
      wrapper.className = "filter-field";

      const title = document.createElement("span");
      title.textContent = FILTER_LABELS[field] || field;

      const select = document.createElement("select");
      select.dataset.field = field;
      select.innerHTML = [
        `<option value="">全部${FILTER_LABELS[field] || field}</option>`,
        ...filterOptions[field].map(
          (option) => `<option value="${escapeHtml(option)}">${escapeHtml(option)}</option>`
        ),
      ].join("");
      select.addEventListener("change", (event) => {
        state.filters[field] = event.target.value;
        render();
      });

      wrapper.append(title, select);
      elements.filtersGrid.appendChild(wrapper);
    });
  }

  function getFilteredStories() {
    const keyword = state.keyword.trim().toLowerCase();

    return rawStories.filter((story) => {
      const matchesFilters = data.filters.fields.every((field) => {
        const selected = state.filters[field];
        if (!selected) {
          return true;
        }
        return normalizeTagValue(story[field]) === selected;
      });

      if (!matchesFilters) {
        return false;
      }

      return !keyword || (story.__searchText || "").includes(keyword);
    });
  }

  function countByField(stories, field, limit) {
    const counts = new Map();
    stories.forEach((story) => {
      const key = normalizeTagValue(story[field]);
      if (!key) {
        return;
      }
      counts.set(key, (counts.get(key) || 0) + 1);
    });

    return [...counts.entries()]
      .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], "zh-CN"))
      .slice(0, limit)
      .map(([label, value]) => ({ label, value }));
  }

  function countTimeBuckets(stories) {
    return TIME_BUCKETS.map((bucket) => ({
      label: bucket.label,
      value: stories.filter((story) => {
        const year = extractYear(story["时间（仅开始年份）"]);
        return year !== null && year >= bucket.min && year <= bucket.max;
      }).length,
    }));
  }

  function renderBarChart(container, rows, type) {
    const list = rows.filter((row) => row.value > 0 || type === "fixed");
    if (!list.length) {
      container.innerHTML = '<div class="empty-state">当前筛选条件下暂无数据</div>';
      return;
    }

    const max = Math.max(...list.map((row) => row.value), 1);
    container.innerHTML = list
      .map(
        (row) => `
          <div class="bar-row">
            <div class="bar-meta">
              <span>${escapeHtml(row.label)}</span>
              <strong>${row.value}</strong>
            </div>
            <div class="bar-track">
              <div class="bar-fill ${type || ""}" style="width:${(row.value / max) * 100}%"></div>
            </div>
          </div>
        `
      )
      .join("");
  }

  function renderPieChart(container, rows) {
    const list = rows.filter((row) => row.value > 0);
    if (!list.length) {
      container.innerHTML = '<div class="empty-state">当前筛选条件下暂无数据</div>';
      return;
    }

    const total = list.reduce((sum, row) => sum + row.value, 0);
    let current = 0;
    const segments = list
      .map((row, index) => {
        const portion = row.value / total;
        const start = current;
        current += portion;
        const color = PIE_COLORS[index % PIE_COLORS.length];
        return `${color} ${start * 100}% ${current * 100}%`;
      })
      .join(", ");

    const legend = list
      .map((row, index) => {
        const percent = ((row.value / total) * 100).toFixed(1);
        const color = PIE_COLORS[index % PIE_COLORS.length];
        return `
          <div class="legend-row">
            <span class="legend-label">
              <span class="legend-dot" style="background:${color}"></span>
              ${escapeHtml(row.label)}
            </span>
            <strong>${row.value} / ${percent}%</strong>
          </div>
        `;
      })
      .join("");

    container.innerHTML = `
      <div class="pie-wrap">
        <div style="width:220px;height:220px;border-radius:50%;background:conic-gradient(${segments});"></div>
        <div class="pie-legend">${legend}</div>
      </div>
    `;
  }

  function renderTable(stories) {
    if (!stories.length) {
      elements.tableBody.innerHTML = `
        <tr>
          <td colspan="8"><div class="empty-state">没有匹配到故事，请调整筛选条件或关键词。</div></td>
        </tr>
      `;
      return;
    }

    elements.tableBody.innerHTML = stories
      .map(
        (story) => `
          <tr>
            <td>${escapeHtml(story["编号"])}</td>
            <td>
              <div class="story-title">
                <a class="story-title-link" href="./story-cards.html#story-${story["编号"]}">${escapeHtml(story["故事标题"])}</a>
              </div>
              <div class="story-summary">${escapeHtml(story["故事摘要"] || "")}</div>
            </td>
            <td>${escapeHtml(story["一级标签（战略概念）"])}</td>
            <td>${escapeHtml(story["二级标签（业务板块）"])}</td>
            <td>${escapeHtml(story["三级标签（八大关系）"])}</td>
            <td>${escapeHtml(story["主角角色"])}</td>
            <td>${escapeHtml(story["价值观标签"])}</td>
            <td>${escapeHtml(story["地点"])}</td>
          </tr>
        `
      )
      .join("");
  }

  function renderMetrics(stories) {
    elements.metricTotal.textContent = String(stories.length);
    elements.metricCountdown.textContent = `${countdownDays(data.meta.targetDate)} 天`;
    elements.metricKeyStories.textContent = String(stories.filter((story) => story.__isKeyStory).length);
    elements.resultSummary.textContent = `当前共 ${stories.length} 条故事`;
  }

  function renderCharts(stories) {
    renderBarChart(elements.strategicBarChart, countByField(stories, "一级标签（战略概念）"));
    renderPieChart(elements.strategicPieChart, countByField(stories, "一级标签（战略概念）"));
    renderBarChart(elements.locationBarChart, countByField(stories, "地点", 10), "location");
    renderBarChart(elements.businessBarChart, countByField(stories, "二级标签（业务板块）"));
    renderBarChart(elements.relationBarChart, countByField(stories, "三级标签（八大关系）"));
    renderBarChart(elements.roleBarChart, countByField(stories, "主角角色"));
    const timeRows = countTimeBuckets(stories);
    renderBarChart(elements.timeBarChart, timeRows, "fixed");
    renderPieChart(elements.timePieChart, timeRows);
  }

  function renderMeta() {
    elements.sourceFile.textContent = data.meta.sourceFile;
    elements.generatedAt.textContent = formatDate(
      data.meta.lastModifiedAt || data.meta.generatedAt
    );
  }

  function render() {
    const stories = getFilteredStories();
    renderMetrics(stories);
    renderCharts(stories);
    renderTable(stories);
  }

  elements.keywordInput.addEventListener("input", (event) => {
    state.keyword = event.target.value;
    render();
  });

  elements.resetButton.addEventListener("click", () => {
    state.keyword = "";
    elements.keywordInput.value = "";
    Object.keys(state.filters).forEach((field) => {
      state.filters[field] = "";
    });
    document.querySelectorAll("select[data-field]").forEach((select) => {
      select.value = "";
    });
    render();
  });

  renderMeta();
  renderFilters();
  render();
})();
