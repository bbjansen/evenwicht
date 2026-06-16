window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true,
    packages: { "[+]": ["boldsymbol", "mhchem"] },
  },
  loader: {
    load: ["[tex]/boldsymbol", "[tex]/mhchem"],
  },
};

document$.subscribe(() => {
  if (MathJax.startup && MathJax.startup.output) {
    MathJax.startup.output.clearCache();
    MathJax.typesetClear();
    MathJax.texReset();
    MathJax.typesetPromise();
  } else {
    MathJax.startup.promise.then(() => {
      MathJax.typesetPromise();
    });
  }
});
