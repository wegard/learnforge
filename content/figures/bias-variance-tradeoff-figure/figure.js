// @learnforge:requires d3
(() => {
  const roots = document.querySelectorAll(
    '.lf-figure-card[data-figure-id="bias-variance-tradeoff-figure"]'
  );
  for (const root of roots) {
    if (root.dataset.interactiveReady === "true") continue;
    root.dataset.interactiveReady = "true";
    const surface = root.querySelector("[data-figure-surface]");
    if (!surface) continue;
    surface.innerHTML = "";

    const margin = { top: 40, right: 30, bottom: 50, left: 55 };
    const width = 520 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    const svg = d3
      .select(surface)
      .append("svg")
      .attr("class", "lf-figure-svg")
      .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleLinear().domain([0, 1]).range([0, width]);
    const y = d3.scaleLinear().domain([0, 1]).range([height, 0]);

    // Error curves as functions of complexity t in [0, 1]
    function bias2(t) {
      return 0.7 * Math.pow(1 - t, 2);
    }
    function variance(t) {
      return 0.6 * Math.pow(t, 2.2);
    }
    const irreducible = 0.05;
    function testError(t) {
      return bias2(t) + variance(t) + irreducible;
    }
    function trainError(t) {
      return Math.max(0.02, 0.45 * Math.pow(1 - t, 1.4) - 0.02 * t);
    }

    // Generate curve data
    const n = 100;
    const curveData = d3.range(n + 1).map((i) => {
      const t = i / n;
      return { t, bias2: bias2(t), variance: variance(t), test: testError(t), train: trainError(t) };
    });

    // Axes
    svg
      .append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x).ticks(0))
      .selectAll("text")
      .remove();
    svg.append("g").call(d3.axisLeft(y).ticks(5).tickFormat(d3.format(".1f")));
    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", height + 38)
      .attr("text-anchor", "middle")
      .attr("font-size", "13px")
      .attr("fill", "#475569")
      .text("Model complexity");
    svg
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", -42)
      .attr("x", -height / 2)
      .attr("text-anchor", "middle")
      .attr("font-size", "13px")
      .attr("fill", "#475569")
      .text("Error");

    // Line generators
    const line = d3
      .line()
      .x((d) => x(d.t))
      .curve(d3.curveBasis);

    // Training error
    svg
      .append("path")
      .datum(curveData)
      .attr("fill", "none")
      .attr("stroke", "#2563eb")
      .attr("stroke-width", 2.5)
      .attr("d", line.y((d) => y(d.train)));

    // Test error
    svg
      .append("path")
      .datum(curveData)
      .attr("fill", "none")
      .attr("stroke", "#dc2626")
      .attr("stroke-width", 2.5)
      .attr("d", line.y((d) => y(d.test)));

    // Bias^2 area
    const biasArea = svg
      .append("path")
      .datum(curveData)
      .attr("fill", "#93c5fd")
      .attr("opacity", 0)
      .attr(
        "d",
        d3
          .area()
          .x((d) => x(d.t))
          .y0(height)
          .y1((d) => y(d.bias2))
          .curve(d3.curveBasis)(curveData)
      );

    // Variance area
    const varianceArea = svg
      .append("path")
      .datum(curveData)
      .attr("fill", "#fca5a5")
      .attr("opacity", 0)
      .attr(
        "d",
        d3
          .area()
          .x((d) => x(d.t))
          .y0((d) => y(d.bias2))
          .y1((d) => y(d.bias2 + d.variance))
          .curve(d3.curveBasis)(curveData)
      );

    // Legend
    const legendData = [
      { label: "Training error", color: "#2563eb" },
      { label: "Test error", color: "#dc2626" },
    ];
    const legend = svg.append("g").attr("transform", `translate(${width - 130}, 0)`);
    legendData.forEach((d, i) => {
      const g = legend.append("g").attr("transform", `translate(0, ${i * 18})`);
      g.append("line").attr("x1", 0).attr("x2", 18).attr("y1", 4).attr("y2", 4).attr("stroke", d.color).attr("stroke-width", 2.5);
      g.append("text").attr("x", 22).attr("y", 8).attr("font-size", "11px").attr("fill", "#334155").text(d.label);
    });

    // Complexity indicator line
    const indicator = svg
      .append("line")
      .attr("y1", 0)
      .attr("y2", height)
      .attr("stroke", "#16a34a")
      .attr("stroke-width", 2)
      .attr("stroke-dasharray", "6 4")
      .attr("opacity", 0);

    // Indicator dot on test curve
    const indicatorDot = svg
      .append("circle")
      .attr("r", 5)
      .attr("fill", "#16a34a")
      .attr("stroke", "white")
      .attr("stroke-width", 2)
      .attr("opacity", 0);

    // Controls
    const controls = document.createElement("div");
    controls.className = "lf-figure-controls";

    const sliderLabel = document.createElement("label");
    sliderLabel.textContent = "Complexity: ";
    sliderLabel.style.fontWeight = "600";
    sliderLabel.style.fontSize = "14px";

    const slider = document.createElement("input");
    slider.type = "range";
    slider.min = "0";
    slider.max = "100";
    slider.value = "50";
    slider.style.width = "180px";
    slider.style.verticalAlign = "middle";
    sliderLabel.appendChild(slider);
    controls.appendChild(sliderLabel);

    const decomposeBtn = document.createElement("button");
    decomposeBtn.type = "button";
    decomposeBtn.textContent = "Show decomposition";
    decomposeBtn.dataset.mode = "decompose";
    controls.appendChild(decomposeBtn);

    root.insertBefore(controls, surface);

    const explainer = document.createElement("p");
    explainer.className = "lf-figure-explainer";
    root.appendChild(explainer);

    let showDecomposition = false;

    function update() {
      const t = parseInt(slider.value, 10) / 100;

      indicator.attr("x1", x(t)).attr("x2", x(t)).attr("opacity", 1);
      indicatorDot.attr("cx", x(t)).attr("cy", y(testError(t))).attr("opacity", 1);

      biasArea.attr("opacity", showDecomposition ? 0.35 : 0);
      varianceArea.attr("opacity", showDecomposition ? 0.35 : 0);

      if (t < 0.3) {
        explainer.textContent =
          "Underfitting: the model is too simple. High bias dominates — it cannot capture the true pattern.";
      } else if (t > 0.65) {
        explainer.textContent =
          "Overfitting: the model is too complex. High variance dominates — it fits noise in the training data.";
      } else {
        explainer.textContent =
          "Near optimal: bias and variance are balanced. Total test error is close to its minimum.";
      }
    }

    slider.addEventListener("input", update);
    decomposeBtn.addEventListener("click", () => {
      showDecomposition = !showDecomposition;
      decomposeBtn.textContent = showDecomposition ? "Hide decomposition" : "Show decomposition";
      decomposeBtn.classList.toggle("is-active", showDecomposition);
      update();
    });

    update();
  }
})();
