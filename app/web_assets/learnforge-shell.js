window.document.addEventListener("DOMContentLoaded", () => {
  setupShellPanels();
  setupSearch();
});

function setupShellPanels() {
  const toggles = Array.from(
    window.document.querySelectorAll(".lf-shell-toggle[data-shell-toggle]"),
  );
  if (!toggles.length) {
    return;
  }

  const desktopQuery = window.matchMedia("(min-width: 641px)");

  function closePanels() {
    for (const toggle of toggles) {
      const targetId = toggle.dataset.shellToggle;
      if (!targetId) {
        continue;
      }
      const panel = window.document.getElementById(targetId);
      if (!panel) {
        continue;
      }
      panel.hidden = true;
      toggle.setAttribute("aria-expanded", "false");
    }
  }

  for (const toggle of toggles) {
    toggle.addEventListener("click", () => {
      if (desktopQuery.matches) {
        return;
      }

      const targetId = toggle.dataset.shellToggle;
      if (!targetId) {
        return;
      }

      const panel = window.document.getElementById(targetId);
      if (!panel) {
        return;
      }

      const willOpen = panel.hidden;
      closePanels();
      if (willOpen) {
        panel.hidden = false;
        toggle.setAttribute("aria-expanded", "true");
      }
    });
  }

  window.document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closePanels();
    }
  });

  const handleViewportChange = () => {
    closePanels();
  };
  if (typeof desktopQuery.addEventListener === "function") {
    desktopQuery.addEventListener("change", handleViewportChange);
  } else if (typeof desktopQuery.addListener === "function") {
    desktopQuery.addListener(handleViewportChange);
  }

  closePanels();
}

function setupSearch() {
  const form = window.document.querySelector(".lf-search-form");
  if (!form) {
    return;
  }

  const input = form.querySelector('input[type="search"]');
  const results = form.querySelector(".lf-search-results");
  const emptyResultsMessage = form.dataset.emptyResultsMessage || "No matching pages.";
  const searchUnavailableMessage =
    form.dataset.searchUnavailableMessage ||
    "Search index is not available for this page yet.";
  let payloadPromise;

  function loadPayload() {
    if (!payloadPromise) {
      payloadPromise = window.fetch(form.dataset.searchIndex).then((response) => {
        if (!response.ok) {
          throw new Error("search-index-unavailable");
        }
        return response.json();
      });
    }
    return payloadPromise;
  }

  function scoreEntry(entry, tokens) {
    const haystack = [
      entry.id,
      entry.kind,
      entry.title,
      entry.description || "",
      ...(entry.topics || []),
      ...(entry.tags || []),
      ...(entry.courses || []),
    ].join(" ").toLowerCase();
    return tokens.reduce((score, token) => score + (haystack.includes(token) ? 1 : 0), 0);
  }

  function renderResults(matches) {
    results.hidden = false;
    if (!matches.length) {
      results.innerHTML = `<p>${emptyResultsMessage}</p>`;
      return;
    }
    const items = matches
      .map((entry) => {
        const description = entry.description ? ` - ${entry.description}` : "";
        return `<li><a href="${entry.href}">${entry.title}</a> [${entry.kind}]${description}</li>`;
      })
      .join("");
    results.innerHTML = `<ul>${items}</ul>`;
  }

  async function handleSearch(event) {
    event.preventDefault();
    const query = (input.value || "").trim().toLowerCase();
    if (!query) {
      results.hidden = true;
      results.innerHTML = "";
      return;
    }

    try {
      const payload = await loadPayload();
      const tokens = query.split(/\s+/).filter(Boolean);
      const matches = (payload.entries || [])
        .map((entry) => ({ entry, score: scoreEntry(entry, tokens) }))
        .filter((item) => item.score > 0)
        .sort(
          (left, right) =>
            right.score - left.score || left.entry.title.localeCompare(right.entry.title),
        )
        .slice(0, 8)
        .map((item) => item.entry);
      renderResults(matches);
    } catch (_error) {
      results.hidden = false;
      results.innerHTML = `<p>${searchUnavailableMessage}</p>`;
    }
  }

  form.addEventListener("submit", handleSearch);
}
