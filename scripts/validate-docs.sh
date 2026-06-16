#!/bin/bash
# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.
#
# Evenwicht Documentation Validator
# Checks all 48 domain chapters + 48 API docs against current standards.
# Run from project root: ./scripts/validate-docs.sh

DOCS_DIR="docs/domains"
API_DIR="docs/api"
PASS=0
WARN=0
FAIL=0

red()    { printf "\033[31m%s\033[0m\n" "$1"; }
yellow() { printf "\033[33m%s\033[0m\n" "$1"; }
green()  { printf "\033[32m%s\033[0m\n" "$1"; }

echo "=========================================="
echo "  Evenwicht Documentation Validator"
echo "=========================================="
echo ""

# ─────────────────────────────────────────────
# 1. DOMAIN STRUCTURE: 12 required H2 sections
# ─────────────────────────────────────────────
echo "=== 1. Domain Section Structure ==="
struct_fail=0
for f in $DOCS_DIR/[0-9]*.md; do
  ch=$(basename "$f" .md | cut -c1-2)
  missing=""
  for section in "Historical Context" "Why This Chapter Matters" "Notation" "Core Theory" "Formulas" "Algorithms" "Numerical" "Worked Examples" "Connections" "Exercises" "References" "Glossary"; do
    grep -q "^## .*$section" "$f" || missing="$missing [$section]"
  done
  if [ -n "$missing" ]; then
    red "  FAIL Ch $ch: missing$missing"
    struct_fail=$((struct_fail+1))
    FAIL=$((FAIL+1))
  fi
done
[ $struct_fail -eq 0 ] && green "  All 48 chapters: 12/12 sections present"
echo ""

# ─────────────────────────────────────────────
# 2. PURE MATH CHECK: No TypeScript in domains
# ─────────────────────────────────────────────
echo "=== 2. Pure Math Check (no code in domains) ==="
code_fail=0
for f in $DOCS_DIR/[0-9]*.md; do
  ch=$(basename "$f" .md | cut -c1-2)
  ts_blocks=$(grep -c '```typescript' "$f")
  src_refs=$(grep -c 'src/' "$f")
  impl_notes=$(grep -c "Implementation Notes" "$f")
  issues=""
  [ "$ts_blocks" -gt 0 ] && issues="$issues ${ts_blocks}xTS"
  [ "$src_refs" -gt 0 ] && issues="$issues ${src_refs}xsrc/"
  [ "$impl_notes" -gt 0 ] && issues="$issues impl_notes"
  if [ -n "$issues" ]; then
    red "  FAIL Ch $ch:$issues"
    code_fail=$((code_fail+1))
    FAIL=$((FAIL+1))
  fi
done
[ $code_fail -eq 0 ] && green "  All 48 chapters: pure math (no TypeScript, no src/ paths)"
echo ""

# ─────────────────────────────────────────────
# 3. DIAGRAM PLACEMENT: timeline + mindmap as openers
# ─────────────────────────────────────────────
echo "=== 3. Diagram Placement ==="
diag_warn=0
for f in $DOCS_DIR/[0-9]*.md; do
  ch=$(basename "$f" .md | cut -c1-2)
  total=$(grep -c '```mermaid' "$f")
  if [ "$total" -eq 0 ]; then
    yellow "  WARN Ch $ch: no mermaid diagrams"
    diag_warn=$((diag_warn+1))
    WARN=$((WARN+1))
  fi
  # Check timeline is first content after Historical Context
  hist_line=$(grep -n "^## .*Historical Context" "$f" | head -1 | cut -d: -f1)
  if [ -n "$hist_line" ]; then
    next_content=$(tail -n +"$((hist_line+1))" "$f" | grep -n -m1 '[^ ]' | head -1)
    first_after=$(tail -n +"$((hist_line+1))" "$f" | head -5 | grep -c '```mermaid')
    if [ "$first_after" -eq 0 ]; then
      yellow "  WARN Ch $ch: timeline not immediately after Historical Context"
      diag_warn=$((diag_warn+1))
      WARN=$((WARN+1))
    fi
  fi
done
[ $diag_warn -eq 0 ] && green "  All diagrams correctly placed"
echo ""

# ─────────────────────────────────────────────
# 4. H3 SUBSECTION CONSISTENCY
# ─────────────────────────────────────────────
echo "=== 4. H3 Subsection Consistency ==="
h3_warn=0
for f in $DOCS_DIR/[0-9]*.md; do
  ch=$(basename "$f" .md | cut -c1-2)
  # Connections must have: Within This Book, Applications
  grep -q "### Within This Book" "$f" || { yellow "  WARN Ch $ch: missing ### Within This Book"; h3_warn=$((h3_warn+1)); WARN=$((WARN+1)); }
  grep -q "### Applications" "$f" || { yellow "  WARN Ch $ch: missing ### Applications"; h3_warn=$((h3_warn+1)); WARN=$((WARN+1)); }
  # References must have: Textbooks, Historical, Online Resources
  grep -q "### Textbooks" "$f" || { yellow "  WARN Ch $ch: missing ### Textbooks"; h3_warn=$((h3_warn+1)); WARN=$((WARN+1)); }
  grep -q "### Historical" "$f" || { yellow "  WARN Ch $ch: missing ### Historical"; h3_warn=$((h3_warn+1)); WARN=$((WARN+1)); }
  grep -q "### Online Resources" "$f" || { yellow "  WARN Ch $ch: missing ### Online Resources"; h3_warn=$((h3_warn+1)); WARN=$((WARN+1)); }
  # Exercises must have: Routine, Intermediate, Challenging
  grep -q "### Routine" "$f" || { yellow "  WARN Ch $ch: missing ### Routine"; h3_warn=$((h3_warn+1)); WARN=$((WARN+1)); }
  grep -q "### Intermediate" "$f" || { yellow "  WARN Ch $ch: missing ### Intermediate"; h3_warn=$((h3_warn+1)); WARN=$((WARN+1)); }
  grep -q "### Challenging" "$f" || { yellow "  WARN Ch $ch: missing ### Challenging"; h3_warn=$((h3_warn+1)); WARN=$((WARN+1)); }
done
[ $h3_warn -eq 0 ] && green "  All H3 subsections consistent"
echo ""

# ─────────────────────────────────────────────
# 5. LICENSE HEADERS
# ─────────────────────────────────────────────
echo "=== 5. License Headers ==="
lic_fail=0
for f in $DOCS_DIR/[0-9]*.md; do
  ch=$(basename "$f" .md | cut -c1-2)
  head -1 "$f" | grep -q "<!-- Copyright" || { red "  FAIL Ch $ch: missing license header"; lic_fail=$((lic_fail+1)); FAIL=$((FAIL+1)); }
done
[ $lic_fail -eq 0 ] && green "  All 48 chapters have license headers"
echo ""

# ─────────────────────────────────────────────
# 6. CHAPTER TITLE FORMAT
# ─────────────────────────────────────────────
echo "=== 6. Chapter Title Format ==="
title_fail=0
for f in $DOCS_DIR/[0-9]*.md; do
  ch=$(basename "$f" .md | cut -c1-2)
  grep -q "^# Chapter [0-9]*:" "$f" || { red "  FAIL Ch $ch: missing '# Chapter N:' title"; title_fail=$((title_fail+1)); FAIL=$((FAIL+1)); }
done
[ $title_fail -eq 0 ] && green "  All 48 chapters have correct title format"
echo ""

# ─────────────────────────────────────────────
# 7. PART LABEL FORMAT
# ─────────────────────────────────────────────
echo "=== 7. Part Label Format ==="
part_fail=0
for f in $DOCS_DIR/[0-9]*.md; do
  ch=$(basename "$f" .md | cut -c1-2)
  grep -q '^\*\*Part [IXV]*\*\*:' "$f" || { yellow "  WARN Ch $ch: non-standard part label"; part_fail=$((part_fail+1)); WARN=$((WARN+1)); }
done
[ $part_fail -eq 0 ] && green "  All part labels correctly formatted"
echo ""

# ─────────────────────────────────────────────
# 8. LATEX DELIMITER CHECK
# ─────────────────────────────────────────────
echo "=== 8. LaTeX Delimiters ==="
for f in $DOCS_DIR/[0-9]*.md; do
  ch=$(basename "$f" .md | cut -c1-2)
  dollar_count=$(sed '/^```/,/^```/d' "$f" | sed 's/\\\$//g' | sed 's/\$\$/DBLDLR/g' | tr -cd '$' | wc -c)
  if [ $((dollar_count % 2)) -ne 0 ]; then
    red "  FAIL Ch $ch: odd number of \$ ($dollar_count) — unmatched delimiter"
    FAIL=$((FAIL+1))
  fi
done
green "  LaTeX delimiters checked"
echo ""

# ─────────────────────────────────────────────
# 9. ALIGNED ENVIRONMENT CHECK
# ─────────────────────────────────────────────
echo "=== 9. Aligned Environments ==="
aligned_fail=0
for f in $DOCS_DIR/[0-9]*.md; do
  ch=$(basename "$f" .md | cut -c1-2)
  begins=$(grep -c '\\begin{aligned}' "$f")
  ends=$(grep -c '\\end{aligned}' "$f")
  if [ "$begins" -ne "$ends" ]; then
    red "  FAIL Ch $ch: $begins \\begin{aligned} vs $ends \\end{aligned}"
    aligned_fail=$((aligned_fail+1))
    FAIL=$((FAIL+1))
  fi
done
[ $aligned_fail -eq 0 ] && green "  All aligned environments balanced"
echo ""

# ─────────────────────────────────────────────
# 10. CONSECUTIVE $$ BLOCKS
# ─────────────────────────────────────────────
echo "=== 10. Consecutive Display Math ==="
consec_warn=0
for f in $DOCS_DIR/[0-9]*.md; do
  ch=$(basename "$f" .md | cut -c1-2)
  count=$(awk 'prev ~ /\$\$$/ && /^\$\$/ {n++} {prev=$0} END {print n+0}' "$f")
  if [ "$count" -gt 0 ]; then
    yellow "  WARN Ch $ch: $count consecutive \$\$ blocks (should use aligned)"
    consec_warn=$((consec_warn+1))
    WARN=$((WARN+1))
  fi
done
[ $consec_warn -eq 0 ] && green "  No consecutive display math blocks"
echo ""

# ─────────────────────────────────────────────
# 11. EXERCISE FORMAT
# ─────────────────────────────────────────────
echo "=== 11. Exercise Format ==="
ex_warn=0
for f in $DOCS_DIR/[0-9]*.md; do
  ch=$(basename "$f" .md | cut -c1-2)
  count=$(grep -cE '^\*\*Exercise' "$f")
  if [ "$count" -lt 6 ]; then
    yellow "  WARN Ch $ch: only $count exercises (min 6)"
    ex_warn=$((ex_warn+1))
    WARN=$((WARN+1))
  fi
done
[ $ex_warn -eq 0 ] && green "  All chapters have 6+ exercises"
echo ""

# ─────────────────────────────────────────────
# 12. COMPOUND NAME HYPHENS
# ─────────────────────────────────────────────
echo "=== 12. Compound Name Hyphens ==="
dash_warn=0
patterns="Cauchy-Schwarz|Gauss-Markov|Runge-Kutta|Hardy-Weinberg|Wright-Fisher|Michaelis-Menten|Black-Scholes|Diffie-Hellman|Cooley-Tukey|Box-Jenkins|Neyman-Pearson"
for f in $DOCS_DIR/[0-9]*.md; do
  ch=$(basename "$f" .md | cut -c1-2)
  count=$(grep -cE "$patterns" "$f")
  if [ "$count" -gt 0 ]; then
    yellow "  WARN Ch $ch: $count compound names with hyphen (should be en-dash)"
    dash_warn=$((dash_warn+1))
    WARN=$((WARN+1))
  fi
done
[ $dash_warn -eq 0 ] && green "  All compound names use en-dash"
echo ""

# ─────────────────────────────────────────────
# 13. API DOC CONSISTENCY
# ─────────────────────────────────────────────
echo "=== 13. API Doc Structure ==="
api_fail=0
for f in $API_DIR/[0-9]*.md; do
  ch=$(basename "$f" .md | cut -c1-2)
  missing=""
  for section in "Module Structure" "Data Representation" "API Preview" "Error Handling" "Dependencies" "Usage Examples"; do
    grep -q "### $section" "$f" || missing="$missing [$section]"
  done
  if [ -n "$missing" ]; then
    yellow "  WARN API $ch: missing$missing"
    api_fail=$((api_fail+1))
    WARN=$((WARN+1))
  fi
done
[ $api_fail -eq 0 ] && green "  All 48 API docs have required sections"
echo ""

# ─────────────────────────────────────────────
# 14. DIAGRAM COUNT
# ─────────────────────────────────────────────
echo "=== 14. Diagram Count ==="
total_diagrams=0
for f in $DOCS_DIR/[0-9]*.md; do
  c=$(grep -c '```mermaid' "$f")
  total_diagrams=$((total_diagrams + c))
done
echo "  Total Mermaid diagrams: $total_diagrams"
echo ""

# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────
echo "=========================================="
echo "  SUMMARY"
echo "=========================================="
echo "  Domain chapters: $(ls $DOCS_DIR/[0-9]*.md | wc -l | tr -d ' ')"
echo "  API docs:        $(ls $API_DIR/[0-9]*.md | wc -l | tr -d ' ')"
echo "  Total lines:     $(cat $DOCS_DIR/[0-9]*.md | wc -l | tr -d ' ')"
echo "  Diagrams:        $total_diagrams"
green "  PASS: $PASS"
[ $WARN -gt 0 ] && yellow "  WARN: $WARN"
[ $FAIL -gt 0 ] && red "  FAIL: $FAIL"
[ $WARN -eq 0 ] && [ $FAIL -eq 0 ] && green "  ALL CLEAN"
echo ""
