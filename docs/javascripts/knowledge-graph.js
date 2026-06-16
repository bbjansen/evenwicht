// Copyright (c) 2025-2026 Bob Jansen
// SPDX-License-Identifier: AGPL-3.0-only

(function () {
  "use strict";

  var graphData = null;

  function init() {
    var container = document.getElementById("knowledge-graph-container");
    if (!container || container.querySelector("svg")) return;

    function loadAndRender() {
      if (graphData) {
        render(container, graphData);
        return;
      }

      var dataUrl = (document.querySelector('script[src*="knowledge-graph.js"]') || {})
        .getAttribute && document.querySelector('script[src*="knowledge-graph.js"]')
        .getAttribute("src").replace(/knowledge-graph\.js.*$/, "graph-data.json");

      if (!dataUrl) {
        dataUrl = "javascripts/graph-data.json";
      }

      fetch(dataUrl)
        .then(function (r) {
          if (!r.ok) throw new Error("Failed to load graph-data.json: " + r.status);
          return r.json();
        })
        .then(function (data) {
          graphData = data;
          render(container, data);
        })
        .catch(function (err) {
          var errP = document.createElement("p");
          errP.style.cssText = "color:var(--md-default-fg-color,#333);padding:2rem;";
          errP.textContent = "Could not load knowledge graph data. " + err.message;
          container.appendChild(errP);
        });
    }

    loadAndRender();
  }

  // Support both full page loads and MkDocs Material instant navigation
  document.addEventListener("DOMContentLoaded", init);
  if (document.readyState !== "loading") init();

  // MkDocs Material fires a custom event on instant navigation
  if (typeof document$ !== "undefined") {
    document$.subscribe(init);
  } else {
    // Fallback: observe DOM changes for SPA navigation
    var observer = new MutationObserver(function () {
      var container = document.getElementById("knowledge-graph-container");
      if (container && !container.querySelector("svg")) init();
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  // ── Palette ──────────────────────────────────────────────────────────
  // Warm-to-cool 9-color palette, readable on light and dark backgrounds.
  var PART_COLORS = [
    "#e6553a", // 1 – warm red
    "#e8862a", // 2 – orange
    "#d4a828", // 3 – amber
    "#8fb339", // 4 – yellow-green
    "#3bab5b", // 5 – green
    "#2ea0a0", // 6 – teal
    "#3987c9", // 7 – blue
    "#6b6ec7", // 8 – indigo
    "#9b59a5", // 9 – purple
  ];

  function partColor(partIndex) {
    var idx = Math.max(1, Math.min(9, partIndex || 1)) - 1;
    return PART_COLORS[idx];
  }

  // ── Render ───────────────────────────────────────────────────────────
  function render(container, data) {
    var nodes = data.nodes.map(function (n) {
      return Object.assign({}, n);
    });
    var edges = data.edges.map(function (e) {
      return Object.assign({}, e);
    });

    // Build degree map
    var degreeMap = {};
    nodes.forEach(function (n) {
      degreeMap[n.id] = 0;
    });
    edges.forEach(function (e) {
      var s = typeof e.source === "object" ? e.source.id : e.source;
      var t = typeof e.target === "object" ? e.target.id : e.target;
      degreeMap[s] = (degreeMap[s] || 0) + 1;
      degreeMap[t] = (degreeMap[t] || 0) + 1;
    });
    var maxDegree = Math.max(1, d3.max(Object.values(degreeMap)));

    function nodeRadius(n) {
      var deg = degreeMap[n.id] || 0;
      return 6 + (deg / maxDegree) * 14;
    }

    // Collect parts for legend and filters
    var partsMap = {};
    nodes.forEach(function (n) {
      if (n.part && !partsMap[n.partIndex]) {
        partsMap[n.partIndex] = n.part;
      }
    });
    var partEntries = Object.keys(partsMap)
      .map(Number)
      .sort(function (a, b) {
        return a - b;
      })
      .map(function (idx) {
        return { index: idx, name: partsMap[idx] };
      });

    // Max edge weight for scaling
    var maxWeight = Math.max(
      1,
      d3.max(edges, function (e) {
        return e.weight || 1;
      })
    );

    // ── Container setup ────────────────────────────────────────────────
    var width = container.clientWidth || 960;
    var height = 700;

    // Clear
    while (container.firstChild) container.removeChild(container.firstChild);
    container.style.position = "relative";
    container.style.overflow = "hidden";

    var svg = d3
      .select(container)
      .append("svg")
      .attr("width", "100%")
      .attr("height", height)
      .style("display", "block");

    var g = svg.append("g");

    // Zoom
    var zoom = d3
      .zoom()
      .scaleExtent([0.2, 5])
      .on("zoom", function (event) {
        g.attr("transform", event.transform);
      });
    svg.call(zoom);

    // Click background to reset highlight
    svg.on("click", function (event) {
      if (event.target.tagName === "svg" || event.target === svg.node()) {
        resetHighlight();
      }
    });

    // ── Initial positions clustered by part ────────────────────────────
    var partCount = partEntries.length || 1;
    nodes.forEach(function (n) {
      var angle = ((2 * Math.PI) / partCount) * ((n.partIndex || 1) - 1);
      var radius = Math.min(width, height) * 0.25;
      n.x = width / 2 + Math.cos(angle) * radius + (Math.random() - 0.5) * 60;
      n.y = height / 2 + Math.sin(angle) * radius + (Math.random() - 0.5) * 60;
    });

    // ── Simulation ─────────────────────────────────────────────────────
    var simulation = d3
      .forceSimulation(nodes)
      .force(
        "link",
        d3
          .forceLink(edges)
          .id(function (d) {
            return d.id;
          })
          .distance(function (e) {
            var w = e.weight || 1;
            return 80 + (1 - w / maxWeight) * 60;
          })
      )
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force(
        "collide",
        d3.forceCollide().radius(function (d) {
          return nodeRadius(d) + 4;
        })
      )
      .alphaDecay(0.02);

    // ── Edge rendering ─────────────────────────────────────────────────
    var linkGroup = g.append("g").attr("class", "kg-links");
    var linkSel = linkGroup
      .selectAll("line")
      .data(edges)
      .join("line")
      .attr("stroke", function (d) {
        return d.type === "reference" ? "#888" : "#bbb";
      })
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", function (d) {
        if (d.type === "shared-api") {
          return 1 + ((d.weight || 1) / maxWeight) * 3;
        }
        return 1.5;
      })
      .attr("stroke-dasharray", function (d) {
        return d.type === "shared-api" ? "5,3" : null;
      });

    // ── Node rendering ─────────────────────────────────────────────────
    var nodeGroup = g.append("g").attr("class", "kg-nodes");
    var nodeSel = nodeGroup
      .selectAll("g")
      .data(nodes)
      .join("g")
      .attr("class", "kg-node")
      .style("cursor", "pointer")
      .call(
        d3
          .drag()
          .on("start", function (event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", function (event, d) {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", function (event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );

    nodeSel
      .append("circle")
      .attr("r", nodeRadius)
      .attr("fill", function (d) {
        return partColor(d.partIndex);
      })
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5);

    nodeSel
      .append("text")
      .text(function (d) {
        return parseInt(d.id, 10);
      })
      .attr("text-anchor", "middle")
      .attr("dy", "0.35em")
      .attr("font-size", function (d) {
        return Math.max(8, nodeRadius(d) * 0.8) + "px";
      })
      .attr("fill", "#fff")
      .attr("font-weight", 600)
      .attr("pointer-events", "none")
      .style("font-family", "inherit");

    // ── Tooltip ────────────────────────────────────────────────────────
    var tooltipEl = document.createElement("div");
    tooltipEl.style.cssText =
      "position:absolute;pointer-events:none;background:var(--md-default-bg-color,rgba(255,255,255,0.96));" +
      "color:var(--md-default-fg-color,#333);border:1px solid var(--md-default-fg-color--lightest,#ccc);" +
      "border-radius:6px;padding:10px 14px;font-size:13px;line-height:1.5;max-width:280px;" +
      "box-shadow:0 2px 8px rgba(0,0,0,0.15);z-index:100;display:none;font-family:inherit;";
    container.appendChild(tooltipEl);
    var tooltip = d3.select(tooltipEl);

    function buildTooltipContent(d) {
      // Build tooltip using safe DOM methods
      while (tooltipEl.firstChild) tooltipEl.removeChild(tooltipEl.firstChild);

      var titleStrong = document.createElement("strong");
      titleStrong.textContent = "Ch. " + parseInt(d.id, 10) + ": " + (d.title || "");
      tooltipEl.appendChild(titleStrong);
      tooltipEl.appendChild(document.createElement("br"));

      var partSpan = document.createElement("span");
      partSpan.style.color = partColor(d.partIndex);
      partSpan.textContent = d.part || "";
      tooltipEl.appendChild(partSpan);

      // Gather neighbors
      var neighbors = [];
      edges.forEach(function (e) {
        var s = typeof e.source === "object" ? e.source.id : e.source;
        var t = typeof e.target === "object" ? e.target.id : e.target;
        if (s === d.id) {
          var tn = nodes.find(function (n) { return n.id === t; });
          if (tn) neighbors.push(tn.title || tn.id);
        } else if (t === d.id) {
          var sn = nodes.find(function (n) { return n.id === s; });
          if (sn) neighbors.push(sn.title || sn.id);
        }
      });
      var unique = neighbors.filter(function (v, i, a) { return a.indexOf(v) === i; });

      if (unique.length > 0) {
        tooltipEl.appendChild(document.createElement("br"));
        var emEl = document.createElement("em");
        emEl.textContent = "Connections (" + unique.length + "):";
        tooltipEl.appendChild(emEl);
        tooltipEl.appendChild(document.createElement("br"));
        unique.forEach(function (name, i) {
          var line = document.createTextNode("- " + name);
          tooltipEl.appendChild(line);
          if (i < unique.length - 1) tooltipEl.appendChild(document.createElement("br"));
        });
      }
    }

    nodeSel
      .on("mouseover", function (event, d) {
        buildTooltipContent(d);
        tooltip.style("display", "block");

        var rect = container.getBoundingClientRect();
        var x = event.clientX - rect.left + 14;
        var y = event.clientY - rect.top - 10;
        if (x + 280 > rect.width) x = x - 300;
        tooltip.style("left", x + "px").style("top", y + "px");
      })
      .on("mousemove", function (event) {
        var rect = container.getBoundingClientRect();
        var x = event.clientX - rect.left + 14;
        var y = event.clientY - rect.top - 10;
        if (x + 280 > rect.width) x = x - 300;
        tooltip.style("left", x + "px").style("top", y + "px");
      })
      .on("mouseout", function () {
        tooltip.style("display", "none");
      });

    // ── Click highlight ────────────────────────────────────────────────
    var highlightedNode = null;

    nodeSel.on("click", function (event, d) {
      event.stopPropagation();
      if (highlightedNode === d.id) {
        resetHighlight();
        return;
      }
      highlightedNode = d.id;

      var neighborIds = new Set();
      neighborIds.add(d.id);
      edges.forEach(function (e) {
        var s = typeof e.source === "object" ? e.source.id : e.source;
        var t = typeof e.target === "object" ? e.target.id : e.target;
        if (s === d.id) neighborIds.add(t);
        if (t === d.id) neighborIds.add(s);
      });

      nodeSel.select("circle").attr("opacity", function (n) {
        return neighborIds.has(n.id) ? 1 : 0.12;
      });
      nodeSel.select("text").attr("opacity", function (n) {
        return neighborIds.has(n.id) ? 1 : 0.12;
      });
      linkSel.attr("stroke-opacity", function (e) {
        var s = typeof e.source === "object" ? e.source.id : e.source;
        var t = typeof e.target === "object" ? e.target.id : e.target;
        return s === d.id || t === d.id ? 0.8 : 0.04;
      });
    });

    function resetHighlight() {
      highlightedNode = null;
      nodeSel.select("circle").attr("opacity", 1);
      nodeSel.select("text").attr("opacity", 1);
      linkSel.attr("stroke-opacity", 0.6);
      applyFilters();
    }

    // ── Simulation tick ────────────────────────────────────────────────
    simulation.on("tick", function () {
      linkSel
        .attr("x1", function (d) {
          return d.source.x;
        })
        .attr("y1", function (d) {
          return d.source.y;
        })
        .attr("x2", function (d) {
          return d.target.x;
        })
        .attr("y2", function (d) {
          return d.target.y;
        });

      nodeSel.attr("transform", function (d) {
        return "translate(" + d.x + "," + d.y + ")";
      });
    });

    // ── Filter panel ───────────────────────────────────────────────────
    var panel = document.createElement("div");
    panel.style.cssText =
      "position:absolute;top:10px;right:10px;background:var(--md-default-bg-color,rgba(255,255,255,0.92));" +
      "color:var(--md-default-fg-color,#333);border:1px solid var(--md-default-fg-color--lightest,#ddd);" +
      "border-radius:8px;padding:12px 16px;font-size:12px;line-height:1.8;max-height:640px;overflow-y:auto;" +
      "z-index:50;backdrop-filter:blur(6px);min-width:180px;font-family:inherit;" +
      "box-shadow:0 2px 8px rgba(0,0,0,0.1);";

    // Search
    var searchLabel = document.createElement("label");
    searchLabel.style.cssText = "display:block;margin-bottom:8px;font-weight:600;";
    searchLabel.textContent = "Search";
    var searchInput = document.createElement("input");
    searchInput.type = "text";
    searchInput.placeholder = "Filter by title...";
    searchInput.style.cssText =
      "width:100%;box-sizing:border-box;padding:4px 8px;border:1px solid var(--md-default-fg-color--lightest,#ccc);" +
      "border-radius:4px;font-size:12px;background:var(--md-default-bg-color,#fff);color:var(--md-default-fg-color,#333);" +
      "margin-top:4px;margin-bottom:10px;font-family:inherit;";
    searchLabel.appendChild(document.createElement("br"));
    searchLabel.appendChild(searchInput);
    panel.appendChild(searchLabel);

    // Edge type filters
    var edgeHeader = document.createElement("div");
    edgeHeader.style.cssText = "font-weight:600;margin-bottom:4px;";
    edgeHeader.textContent = "Edge types";
    panel.appendChild(edgeHeader);

    var edgeFilters = { reference: true, "shared-api": true };

    ["reference", "shared-api"].forEach(function (type) {
      var lbl = document.createElement("label");
      lbl.style.cssText = "display:flex;align-items:center;gap:6px;cursor:pointer;";
      var cb = document.createElement("input");
      cb.type = "checkbox";
      cb.checked = true;
      cb.style.cursor = "pointer";
      cb.addEventListener("change", function () {
        edgeFilters[type] = cb.checked;
        applyFilters();
      });
      var lineSpan = document.createElement("span");
      lineSpan.style.cssText =
        "display:inline-block;width:24px;height:0;border-top:2px " +
        (type === "shared-api" ? "dashed #bbb" : "solid #888") +
        ";vertical-align:middle;";
      lbl.appendChild(cb);
      lbl.appendChild(lineSpan);
      lbl.appendChild(document.createTextNode(type === "reference" ? " References" : " Shared API"));
      panel.appendChild(lbl);
    });

    // Part filters
    var partHeader = document.createElement("div");
    partHeader.style.cssText = "font-weight:600;margin-top:10px;margin-bottom:4px;";
    partHeader.textContent = "Parts";
    panel.appendChild(partHeader);

    var partFilters = {};
    partEntries.forEach(function (p) {
      partFilters[p.index] = true;

      var lbl = document.createElement("label");
      lbl.style.cssText = "display:flex;align-items:center;gap:6px;cursor:pointer;";
      var cb = document.createElement("input");
      cb.type = "checkbox";
      cb.checked = true;
      cb.style.cursor = "pointer";
      cb.addEventListener("change", function () {
        partFilters[p.index] = cb.checked;
        applyFilters();
      });
      var dot = document.createElement("span");
      dot.style.cssText =
        "display:inline-block;width:10px;height:10px;border-radius:50%;background:" +
        partColor(p.index) +
        ";flex-shrink:0;";
      lbl.appendChild(cb);
      lbl.appendChild(dot);
      lbl.appendChild(document.createTextNode(" " + p.name));
      panel.appendChild(lbl);
    });

    container.appendChild(panel);

    // ── Legend (bottom-left) ───────────────────────────────────────────
    var legend = document.createElement("div");
    legend.style.cssText =
      "position:absolute;bottom:10px;left:10px;background:var(--md-default-bg-color,rgba(255,255,255,0.92));" +
      "color:var(--md-default-fg-color,#333);border:1px solid var(--md-default-fg-color--lightest,#ddd);" +
      "border-radius:8px;padding:10px 14px;font-size:11px;line-height:1.7;z-index:50;" +
      "backdrop-filter:blur(6px);font-family:inherit;box-shadow:0 2px 8px rgba(0,0,0,0.1);";

    var legendTitle = document.createElement("div");
    legendTitle.style.cssText = "font-weight:600;margin-bottom:4px;";
    legendTitle.textContent = "Legend";
    legend.appendChild(legendTitle);

    partEntries.forEach(function (p) {
      var row = document.createElement("div");
      row.style.cssText = "display:flex;align-items:center;gap:6px;";
      var dot = document.createElement("span");
      dot.style.cssText =
        "display:inline-block;width:8px;height:8px;border-radius:50%;background:" +
        partColor(p.index) +
        ";flex-shrink:0;";
      row.appendChild(dot);
      row.appendChild(document.createTextNode(p.name));
      legend.appendChild(row);
    });

    // Edge legend entries
    var edgeLegend1 = document.createElement("div");
    edgeLegend1.style.cssText = "display:flex;align-items:center;gap:6px;margin-top:6px;";
    var line1 = document.createElement("span");
    line1.style.cssText = "display:inline-block;width:20px;height:0;border-top:2px solid #888;";
    edgeLegend1.appendChild(line1);
    edgeLegend1.appendChild(document.createTextNode("Reference"));
    legend.appendChild(edgeLegend1);

    var edgeLegend2 = document.createElement("div");
    edgeLegend2.style.cssText = "display:flex;align-items:center;gap:6px;";
    var line2 = document.createElement("span");
    line2.style.cssText = "display:inline-block;width:20px;height:0;border-top:2px dashed #bbb;";
    edgeLegend2.appendChild(line2);
    edgeLegend2.appendChild(document.createTextNode("Shared API"));
    legend.appendChild(edgeLegend2);

    container.appendChild(legend);

    // ── Search handler ─────────────────────────────────────────────────
    searchInput.addEventListener("input", function () {
      applyFilters();
    });

    // ── Apply filters ──────────────────────────────────────────────────
    function applyFilters() {
      var query = searchInput.value.trim().toLowerCase();

      var visibleNodeIds = new Set();
      nodes.forEach(function (n) {
        var partVisible = partFilters[n.partIndex] !== false;
        var matchesSearch = !query || (n.title && n.title.toLowerCase().indexOf(query) !== -1);
        if (partVisible && matchesSearch) {
          visibleNodeIds.add(n.id);
        }
      });

      nodeSel.select("circle").attr("opacity", function (n) {
        return visibleNodeIds.has(n.id) ? 1 : 0.08;
      });
      nodeSel.select("text").attr("opacity", function (n) {
        return visibleNodeIds.has(n.id) ? 1 : 0.08;
      });

      linkSel
        .attr("stroke-opacity", function (e) {
          var s = typeof e.source === "object" ? e.source.id : e.source;
          var t = typeof e.target === "object" ? e.target.id : e.target;
          var typeVisible = edgeFilters[e.type] !== false;
          var nodesVisible = visibleNodeIds.has(s) && visibleNodeIds.has(t);
          return typeVisible && nodesVisible ? 0.6 : 0.03;
        })
        .attr("pointer-events", function (e) {
          var typeVisible = edgeFilters[e.type] !== false;
          return typeVisible ? "auto" : "none";
        });

      // Highlight search matches with golden stroke
      if (query) {
        nodeSel.select("circle").attr("stroke-width", function (n) {
          if (n.title && n.title.toLowerCase().indexOf(query) !== -1) return 3;
          return 1.5;
        });
        nodeSel.select("circle").attr("stroke", function (n) {
          if (n.title && n.title.toLowerCase().indexOf(query) !== -1) return "#ffd700";
          return "#fff";
        });
      } else {
        nodeSel.select("circle").attr("stroke-width", 1.5).attr("stroke", "#fff");
      }
    }

    // ── Resize handler ─────────────────────────────────────────────────
    var resizeTimer;
    window.addEventListener("resize", function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () {
        var newWidth = container.clientWidth || 960;
        simulation.force("center", d3.forceCenter(newWidth / 2, height / 2));
        simulation.alpha(0.3).restart();
      }, 200);
    });
  }
})();
