(() => {
  const roots = window.document.querySelectorAll('.lf-figure-card[data-figure-id="iv-dag-figure"]');
  for (const root of roots) {
    if (root.dataset.interactiveReady === "true") {
      continue;
    }
    root.dataset.interactiveReady = "true";

    const surface = root.querySelector("[data-figure-surface]");
    if (!surface) {
      continue;
    }

    const controls = window.document.createElement("div");
    controls.className = "lf-figure-controls";
    controls.innerHTML = [
      '<button type="button" data-mode="default">Base DAG</button>',
      '<button type="button" data-mode="relevance">Highlight relevance</button>',
      '<button type="button" data-mode="exclusion">Show exclusion risk</button>',
    ].join("");

    const explainer = window.document.createElement("p");
    explainer.className = "lf-figure-explainer";
    root.insertBefore(controls, surface);
    root.appendChild(explainer);

    const zx = surface.querySelector('[data-figure-part="edge-zx"]');
    const xy = surface.querySelector('[data-figure-part="edge-xy"]');
    const direct = surface.querySelector('[data-figure-part="edge-zy-direct"]');
    const directArrow = surface.querySelector('[data-figure-part="edge-zy-direct-arrow"]');
    const directLabel = surface.querySelector('[data-figure-part="edge-zy-direct-label"]');
    const nodeZ = surface.querySelector('[data-figure-part="node-z"]');
    const nodeX = surface.querySelector('[data-figure-part="node-x"]');
    const nodeY = surface.querySelector('[data-figure-part="node-y"]');

    function setMode(mode) {
      for (const button of controls.querySelectorAll("button")) {
        button.classList.toggle("is-active", button.dataset.mode === mode);
      }

      if (zx) {
        zx.setAttribute("stroke-width", mode === "relevance" ? "9" : "6");
      }
      if (xy) {
        xy.setAttribute("stroke-width", mode === "relevance" ? "5" : "6");
      }
      if (nodeX) {
        nodeX.setAttribute("stroke", mode === "relevance" ? "#1d4ed8" : "#ca8a04");
        nodeX.setAttribute("stroke-width", mode === "relevance" ? "6" : "4");
      }
      if (nodeY) {
        nodeY.setAttribute("stroke-width", mode === "exclusion" ? "6" : "4");
      }

      const showDirect = mode === "exclusion";
      for (const item of [direct, directArrow, directLabel]) {
        if (item) {
          item.setAttribute("opacity", showDirect ? "1" : "0");
        }
      }

      if (mode === "relevance") {
        explainer.textContent = "Relevance means the instrument must move treatment strongly enough to matter.";
        return;
      }
      if (mode === "exclusion") {
        explainer.textContent = "If Z can move Y directly, the exclusion restriction fails and IV breaks.";
        return;
      }
      explainer.textContent = "The baseline DAG shows the intended IV path: Z moves X, and X moves Y.";
    }

    controls.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-mode]");
      if (!button) {
        return;
      }
      setMode(button.dataset.mode || "default");
    });

    setMode("default");
  }
})();
