// Copyright (c) 2025-2026 Bob Jansen
// SPDX-License-Identifier: AGPL-3.0-only

// Adds an expand button to Mermaid diagram containers.
// Material for MkDocs renders Mermaid content in a way that prevents
// appending children to the .mermaid div. This script wraps each
// .mermaid div in a container and places the button on the wrapper.

(function () {
  "use strict";

  function createButton() {
    var btn = document.createElement("button");
    btn.className = "ev-diagram-expand";
    btn.title = "Expand diagram";
    btn.setAttribute("aria-label", "Expand diagram");
    btn.textContent = "\u2922";
    return btn;
  }

  function collapse(wrapper, btn) {
    wrapper.classList.remove("ev-diagram-expanded");
    btn.textContent = "\u2922";
    btn.title = "Expand diagram";
  }

  function toggle(wrapper, btn) {
    var expanded = wrapper.classList.toggle("ev-diagram-expanded");
    btn.textContent = expanded ? "\u2923" : "\u2922";
    btn.title = expanded ? "Collapse diagram" : "Expand diagram";
    if (expanded) {
      wrapper.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      var expanded = document.querySelector(".ev-diagram-expanded");
      if (expanded) {
        var btn = expanded.querySelector(".ev-diagram-expand");
        collapse(expanded, btn);
      }
    }
  });

  function process() {
    document.querySelectorAll("div.mermaid").forEach(function (div) {
      if (div.parentElement && div.parentElement.classList.contains("ev-diagram-wrapper")) return;

      var wrapper = document.createElement("div");
      wrapper.className = "ev-diagram-wrapper";
      div.parentNode.insertBefore(wrapper, div);
      wrapper.appendChild(div);

      var btn = createButton();
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        toggle(wrapper, btn);
      });
      wrapper.appendChild(btn);
    });
  }

  var mo = new MutationObserver(function () {
    if (document.querySelector("div.mermaid:not(.ev-diagram-wrapper > div.mermaid)")) {
      process();
    }
  });

  function start() {
    mo.observe(document.body, { childList: true, subtree: true });
    process();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
