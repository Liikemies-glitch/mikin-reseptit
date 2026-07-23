const state = {
  data: null,
  query: "",
  activeId: null,
};

const els = {
  indexView: document.getElementById("indexView"),
  indexRows: document.getElementById("indexRows"),
  detailView: document.getElementById("detailView"),
  filter: document.getElementById("filter"),
  count: document.getElementById("count"),
  emptyState: document.getElementById("emptyState"),
  footerNote: document.getElementById("footerNote"),
  backBtn: document.getElementById("backBtn"),
};

const SECTION_ORDER = ["paaruuat", "jalkiruoat", "kastikkeet"];

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function formatInlineMarkdown(text) {
  return escapeHtml(text).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
}

function findRecipe(id) {
  for (const section of state.data.sections) {
    if (section.id === id && section.table) return { type: "table", section };
    const recipe = (section.recipes || []).find((r) => r.id === id);
    if (recipe) return { type: "recipe", section, recipe };
  }
  return null;
}

function matchesQuery(row, query) {
  if (!query) return true;
  const hay = [row.section, row.title, row.meta, row.macros]
    .join(" ")
    .toLocaleLowerCase("fi");
  return hay.includes(query);
}

function sectionRank(sectionId) {
  const idx = SECTION_ORDER.indexOf(sectionId);
  return idx === -1 ? SECTION_ORDER.length : idx;
}

function sortedIndexRows(query) {
  return state.data.index
    .filter((row) => row.id !== "perusarvot" && !String(row.title || "").toLowerCase().includes("perusravinto"))
    .filter((row) => matchesQuery(row, query))
    .slice()
    .sort((a, b) => {
      const bySection = sectionRank(a.sectionId) - sectionRank(b.sectionId);
      if (bySection !== 0) return bySection;
      const ra = typeof a.rating === "number" ? a.rating : -1;
      const rb = typeof b.rating === "number" ? b.rating : -1;
      if (ra !== rb) return rb - ra;
      return 0;
    });
}

function renderRecipeRow(row) {
  const rating =
    typeof row.rating === "number" ? String(row.rating) : "—";
  return `
      <button
        class="index__row"
        type="button"
        data-id="${escapeHtml(row.id)}"
        aria-label="${escapeHtml(row.title)}"
      >
        <div class="cell cell--rating">${rating}</div>
        <div class="cell cell__title">${escapeHtml(row.title)}</div>
        <div class="cell">${escapeHtml(row.meta || "—")}</div>
        <div class="cell">${escapeHtml(row.macros || "—")}</div>
        <div class="cell"><span class="dot" aria-hidden="true"></span></div>
      </button>`;
}

function renderIndexList() {
  const query = state.query.trim().toLocaleLowerCase("fi");
  const rows = sortedIndexRows(query);

  els.count.textContent = `${rows.length} / ${state.data.index.length}`;
  els.emptyState.hidden = rows.length > 0;

  const groups = [];
  let current = null;
  for (const row of rows) {
    if (!current || current.sectionId !== row.sectionId) {
      current = {
        sectionId: row.sectionId,
        section: row.section,
        rows: [],
      };
      groups.push(current);
    }
    current.rows.push(row);
  }

  els.indexRows.innerHTML = groups
    .map((group) => {
      const heading = `
      <div class="index__section" role="presentation">
        <h2 class="index__section-title">${escapeHtml(group.section)}</h2>
      </div>`;
      return heading + group.rows.map(renderRecipeRow).join("");
    })
    .join("");
}

function renderTable(section) {
  const { headers, rows } = section.table;
  return `
    <h1 class="detail__title">${escapeHtml(section.name)}</h1>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>${headers.map((h) => `<th>${formatInlineMarkdown(h)}</th>`).join("")}</tr>
        </thead>
        <tbody>
          ${rows
            .map(
              (row) =>
                `<tr>${row
                  .map((cell) => `<td>${formatInlineMarkdown(cell)}</td>`)
                  .join("")}</tr>`
            )
            .join("")}
        </tbody>
      </table>
    </div>`;
}

function renderBlock(block) {
  const label = escapeHtml(block.label || "");
  const content = block.content
    ? `<p class="detail__text">${formatInlineMarkdown(block.content)}</p>`
    : "";
  const items =
    block.items && block.items.length
      ? `<ul class="detail__list">${block.items
          .map((item) => `<li>${formatInlineMarkdown(item)}</li>`)
          .join("")}</ul>`
      : "";
  const steps =
    block.steps && block.steps.length
      ? `<ol class="detail__steps">${block.steps
          .map((step) => `<li>${formatInlineMarkdown(step)}</li>`)
          .join("")}</ol>`
      : "";

  if (block.type === "paragraph") {
    return `<div class="detail__block"><p class="detail__text">${formatInlineMarkdown(
      block.content
    )}</p></div>`;
  }

  return `
    <div class="detail__block">
      ${label ? `<p class="detail__label">${label}</p>` : ""}
      ${content}
      ${items}
      ${steps}
    </div>`;
}

function renderRecipe(section, recipe) {
  const blocks = (recipe.blocks || []).map(renderBlock).join("");
  const rating =
    typeof recipe.rating === "number"
      ? `<p class="detail__rating">Arvosana ${recipe.rating}/10</p>`
      : "";
  return `
    ${rating}
    <h1 class="detail__title">${escapeHtml(recipe.title)}</h1>
    ${blocks}`;
}

function recipeIdFromLocation() {
  const params = new URLSearchParams(location.search);
  const fromQuery = params.get("r");
  if (fromQuery) return fromQuery;
  // legacy hash links
  return decodeURIComponent(location.hash.replace(/^#/, ""));
}

function indexHref() {
  return `${location.pathname}`;
}

function detailHref(id) {
  return `${location.pathname}?r=${encodeURIComponent(id)}`;
}

function paintIndex() {
  state.activeId = null;
  els.indexView.hidden = false;
  els.detailView.hidden = true;
  els.detailView.innerHTML = "";
  els.backBtn.hidden = true;
  els.filter.hidden = false;
  els.count.hidden = false;
  window.scrollTo(0, 0);
}

function paintDetail(id) {
  const found = findRecipe(id);
  if (!found) {
    paintIndex();
    return false;
  }

  state.activeId = id;
  els.indexView.hidden = true;
  els.detailView.hidden = false;
  els.backBtn.hidden = false;
  els.filter.hidden = true;
  els.count.hidden = true;

  els.detailView.innerHTML =
    found.type === "table"
      ? renderTable(found.section)
      : renderRecipe(found.section, found.recipe);

  window.scrollTo(0, 0);
  return true;
}

function applyRoute() {
  const id = recipeIdFromLocation();
  if (id) paintDetail(id);
  else paintIndex();
}

function openDetail(id) {
  if (!findRecipe(id)) return;
  const href = detailHref(id);
  if (`${location.pathname}${location.search}` === href) {
    applyRoute();
    return;
  }
  history.pushState({ view: "detail", id }, "", href);
  applyRoute();
}

function goBackToIndex() {
  if (recipeIdFromLocation()) {
    history.back();
    return;
  }
  applyRoute();
}

async function init() {
  const res = await fetch("./recipes.json?v=48");
  state.data = await res.json();

  document.title = state.data.brand || state.data.title;
  const footerBits = [state.data.footer || state.data.intro || ""].filter(Boolean);
  footerBits.push(
    'Agentit: <a href="./llms.txt">llms.txt</a>'
  );
  els.footerNote.innerHTML = footerBits.join("<br>");

  // Migrate old #id links into history-friendly ?r=id URLs
  if (!new URLSearchParams(location.search).get("r") && location.hash.length > 1) {
    const legacyId = decodeURIComponent(location.hash.slice(1));
    if (findRecipe(legacyId)) {
      history.replaceState({ view: "detail", id: legacyId }, "", detailHref(legacyId));
    }
  }

  renderIndexList();
  applyRoute();

  els.filter.addEventListener("input", () => {
    state.query = els.filter.value;
    renderIndexList();
  });

  els.indexRows.addEventListener("click", (event) => {
    const row = event.target.closest("[data-id]");
    if (!row) return;
    openDetail(row.dataset.id);
  });

  els.backBtn.addEventListener("click", goBackToIndex);
  window.addEventListener("popstate", applyRoute);
}

init();
