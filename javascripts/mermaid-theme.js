// Copyright (c) 2025-2026 Bob Jansen
// SPDX-License-Identifier: AGPL-3.0-only

// Override Material for MkDocs' mermaid theme.
//
// Material derives mermaid's primaryColor from the accent colour
// (deep orange → salmon nodes). This script patches mermaid.initialize()
// to force our grey palette and disable gradients.
//
// Strategy: patch mermaid.initialize BEFORE Material calls it.
// Material loads mermaid lazily via an IntersectionObserver, so our
// extra_javascript runs first.

(function () {
  "use strict";

  var EV_THEME = {
    primaryColor: "#e8e8e8",
    primaryTextColor: "#333333",
    primaryBorderColor: "#555555",
    lineColor: "#666666",
    secondaryColor: "#d1ecf1",
    tertiaryColor: "#c8e6c9",
    nodeBkg: "#e8e8e8",
    mainBkg: "#e8e8e8",
    nodeBorder: "#555555",
    stateBkg: "#e8e8e8",
    useGradient: false
  };

  function waitAndPatch() {
    if (typeof mermaid === "undefined") {
      requestAnimationFrame(waitAndPatch);
      return;
    }

    // Patch initialize to inject our theme into every call
    var original = mermaid.initialize;
    mermaid.initialize = function (config) {
      if (!config) config = {};
      if (!config.themeVariables) config.themeVariables = {};
      // Merge our values (ours win over Material's)
      for (var key in EV_THEME) {
        config.themeVariables[key] = EV_THEME[key];
      }
      config.theme = "base";
      return original.call(mermaid, config);
    };
  }

  // Start patching immediately — before Material's bundle runs
  waitAndPatch();
})();
