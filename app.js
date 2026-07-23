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
  hero: document.getElementById("hero"),
};

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

function renderIndex() {
  const query = state.query.trim().toLocaleLowerCase("fi");
  const rows = state.data.index.filter((row) => matchesQuery(row, query));

  els.count.textContent = `${rows.length} / ${state.data.index.length}`;
  els.emptyState.hidden = rows.length > 0;

  els.indexRows.innerHTML = rows
    .map(
      (row) => `
      <button
        class="index__row"
        type="button"
        data-id="${escapeHtml(row.id)}"
        aria-label="${escapeHtml(row.title)}"
      >
        <div class="cell">${escapeHtml(row.section)}</div>
        <div class="cell">${escapeHtml(row.title)}</div>
        <div class="cell">${escapeHtml(row.meta || "—")}</div>
        <div class="cell">${escapeHtml(row.macros || "—")}</div>
        <div class="cell"><span class="dot" aria-hidden="true"></span></div>
      </button>`
    )
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
  return `
    <p class="detail__meta">${escapeHtml(section.name)}${
      recipe.meta ? ` · ${escapeHtml(recipe.meta)}` : ""
    }</p>
    <h1 class="detail__title">${escapeHtml(recipe.title)}</h1>
    ${blocks}`;
}

function showIndex() {
  state.activeId = null;
  els.indexView.hidden = false;
  els.detailView.hidden = true;
  els.detailView.innerHTML = "";
  els.backBtn.hidden = true;
  els.filter.hidden = false;
  els.count.hidden = false;
  if (els.hero) els.hero.hidden = false;
  history.replaceState(null, "", location.pathname);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function showDetail(id) {
  const found = findRecipe(id);
  if (!found) {
    showIndex();
    return;
  }

  state.activeId = id;
  els.indexView.hidden = true;
  els.detailView.hidden = false;
  els.backBtn.hidden = false;
  els.filter.hidden = true;
  els.count.hidden = true;
  if (els.hero) els.hero.hidden = true;

  els.detailView.innerHTML =
    found.type === "table"
      ? renderTable(found.section)
      : renderRecipe(found.section, found.recipe);

  history.replaceState(null, "", `#${encodeURIComponent(id)}`);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function onHashChange() {
  const id = decodeURIComponent(location.hash.replace(/^#/, ""));
  if (id) showDetail(id);
  else showIndex();
}

async function init() {
  const res = await fetch("./recipes.json");
  state.data = await res.json();

  document.title = "Mikin reseptit";
  els.footerNote.textContent = state.data.footer || state.data.intro || "";

  renderIndex();

  els.filter.addEventListener("input", () => {
    state.query = els.filter.value;
    renderIndex();
  });

  els.indexRows.addEventListener("click", (event) => {
    const row = event.target.closest("[data-id]");
    if (!row) return;
    showDetail(row.dataset.id);
  });

  els.backBtn.addEventListener("click", showIndex);
  window.addEventListener("hashchange", onHashChange);

  if (location.hash) onHashChange();
}

init();
