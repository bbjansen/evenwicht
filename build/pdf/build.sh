#!/usr/bin/env bash
# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.
#
# Evenwicht Documentation → PDF Build Script
#
# Pipeline:
#   Phase 1:  mmdc pre-renders Mermaid diagrams to PNG (via Chromium)
#   Phase 1b: Set DPI metadata on PNGs for correct LaTeX sizing
#   Phase 1c: Strip heading numbers, apply captions, generate bibliography
#   Phase 2:  pandoc + lualatex → PDF using custom academic template
#
# Prerequisites:
#   brew install pandoc
#   pip3 install Pillow
#   npm install -g @mermaid-js/mermaid-cli
#   brew install --cask basictex
#   export PATH="/usr/local/texlive/2026basic/bin/universal-darwin:$PATH"
#   sudo tlmgr update --self
#   sudo tlmgr install collection-latexrecommended fontspec

set -euo pipefail

# ── Paths ──────────────────────────────────────
BUILD_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$BUILD_DIR/../.." && pwd)"
TEMPLATE_DIR="$BUILD_DIR/template"
TOOLS_DIR="$BUILD_DIR/tools"
DOCS="$PROJECT_ROOT/docs/domains"
OUT="$PROJECT_ROOT/dist"
RENDERED="$OUT/rendered"

# Ensure TeX Live is on PATH and custom .sty files are found
export PATH="/usr/local/texlive/2026basic/bin/universal-darwin:$PATH"
export TEXINPUTS="${TEMPLATE_DIR}:${TEXINPUTS:-}"

SKIP_RENDER=false
DRAFT=false
for arg in "$@"; do
    case "$arg" in
        --skip-render|-s) SKIP_RENDER=true ;;
        --draft|-d) DRAFT=true ;;
    esac
done

# Clean previous build (skip if reusing rendered files)
if [ "$SKIP_RENDER" = false ]; then
    rm -rf "$RENDERED"
fi
mkdir -p "$RENDERED"

echo "============================================"
echo "  Evenwicht PDF Builder"
echo "============================================"
echo ""

# ──────────────────────────────────────────────
# Phase 1: Pre-render Mermaid diagrams to PNG
# ──────────────────────────────────────────────
if [ "$SKIP_RENDER" = true ]; then
    echo "Phase 1: SKIPPED (using existing rendered files)"
    echo ""
else
    echo "Phase 1: Pre-rendering Mermaid diagrams to PNG..."
    echo ""

    # Strip inline Mermaid theme directives so the B&W config takes effect.
    # Also strip xychart-beta config and inline style lines for clean B&W.
    MMDC_PREP="$OUT/mmdc-prep"
    rm -rf "$MMDC_PREP"
    mkdir -p "$MMDC_PREP"
    for f in "$DOCS"/[0-9]*.md; do
        outname="$MMDC_PREP/$(basename "$f")"
        python3 -c "
import re, sys
text = open(sys.argv[1]).read()
# Strip %%{init:...}%% directives
text = re.sub(r'%%\{init:.*?\}%%', '', text)
# Strip Mermaid YAML front-matter blocks (---\ntitle: ...\n---)
text = re.sub(
    r'(\x60\x60\x60mermaid\s*\n)\s*---\n.*?\s*---\n',
    r'\1',
    text,
    flags=re.DOTALL,
)
# Strip all inline style, classDef, and linkStyle lines for clean B&W
text = re.sub(r'^\s+style\s+\w+\s+\S.*$', '', text, flags=re.MULTILINE)
text = re.sub(r'^\s+classDef\s+.*$', '', text, flags=re.MULTILINE)
text = re.sub(r'^\s+linkStyle\s+.*$', '', text, flags=re.MULTILINE)
open(sys.argv[2], 'w').write(text)
" "$f" "$outname"
    done
    echo "  Prepared Mermaid-clean copies for B&W rendering"

    TOTAL_DIAGRAMS=0
    for f in "$MMDC_PREP"/[0-9]*.md; do
        base=$(basename "$f")

        if mmdc \
            --input "$f" \
            --output "$RENDERED/$base" \
            --outputFormat png \
            --scale 3 \
            --backgroundColor white \
            --configFile "$BUILD_DIR/mermaid-config.json" \
            --puppeteerConfigFile "$BUILD_DIR/puppeteer-config.json" \
            --quiet 2>/dev/null; then

            count=$(grep -c '\.png)' "$RENDERED/$base" 2>/dev/null || echo 0)
            TOTAL_DIAGRAMS=$((TOTAL_DIAGRAMS + count))
            echo "  ✓ $base ($count diagrams)"
        else
            cp "$f" "$RENDERED/$base"
            echo "  ✗ $base (mmdc failed, copied original)"
        fi
    done

    echo ""
    echo "  Total diagrams rendered: $TOTAL_DIAGRAMS"
    rm -rf "$MMDC_PREP"
    echo ""
fi

# ──────────────────────────────────────────────
# Phase 1b: Set DPI on PNGs for correct sizing
# ──────────────────────────────────────────────
echo "Phase 1b: Setting DPI and resizing square PNGs..."
PNG_COUNT=0
RESIZED=0
for png in "$RENDERED"/*.png; do
    [ -f "$png" ] || continue
    python3 -c "
from PIL import Image
img = Image.open('$png')
w, h = img.size
# Square, near-square, or tall charts (aspect ratio > 0.6): scale down
# to 65% so they don't dominate the page. Catches pie charts, xy plots,
# state diagrams, and mindmaps.
ratio = h / w if w > 0 else 0
if ratio > 0.6 and w > 800:
    scale = 0.65
    new_w = int(w * scale)
    new_h = int(h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    print('resized')
img.save('$png', dpi=(216, 216))
" 2>/dev/null
    result=$?
    if [ $result -eq 0 ]; then
        PNG_COUNT=$((PNG_COUNT + 1))
    fi
done
echo "  Processed $PNG_COUNT PNGs"

# Stamp DRAFT watermark on copies (preserve originals for non-draft rebuilds)
RENDERED_ACTIVE="$RENDERED"
if [ "$DRAFT" = true ]; then
    RENDERED_DRAFT="$OUT/rendered-draft"
    rm -rf "$RENDERED_DRAFT"
    cp -a "$RENDERED" "$RENDERED_DRAFT"
    echo "  Stamping DRAFT on diagram PNGs (working on copies)..."
    python3 -c "
from PIL import Image, ImageDraw, ImageFont
import glob, math

for path in sorted(glob.glob('$RENDERED_DRAFT/*.png')):
    img = Image.open(path).convert('RGBA')
    w, h = img.size

    # Create transparent overlay
    overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Size the text relative to image
    font_size = max(w, h) // 8
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', font_size)
    except:
        font = ImageFont.load_default()

    text = 'DRAFT'
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Draw centered, rotated
    txt_img = Image.new('RGBA', (tw + 20, th + 20), (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_img)
    txt_draw.text((10, 10), text, fill=(0, 0, 0, 30), font=font)
    rotated = txt_img.rotate(30, expand=True, resample=Image.BICUBIC)

    # Paste centered
    rw, rh = rotated.size
    pos = ((w - rw) // 2, (h - rh) // 2)
    img.paste(rotated, pos, rotated)

    img = img.convert('RGB')
    img.save(path, dpi=(216, 216))
" 2>/dev/null
    RENDERED_ACTIVE="$RENDERED_DRAFT"
    echo "  Done"
fi
echo ""

# ──────────────────────────────────────────────
# Phase 1c: Prepare markdown for LaTeX
# ──────────────────────────────────────────────
echo "Phase 1c: Preparing markdown..."
for f in "$RENDERED_ACTIVE"/[0-9]*.md; do
    # Strip heading numbers (LaTeX adds its own)
    perl -i -pe 's/^# Chapter [0-9]+: /# /' "$f"
    perl -i -pe 's/^## [0-9]+\. /## /' "$f"

    # Strip Mermaid YAML title blocks that Pandoc misreads as document metadata.
    # Pattern: ```mermaid\n---\ntitle: "..."\n---  →  ```mermaid
    python3 -c "
import re, sys
text = open('$f').read()
text = re.sub(
    r'(\`\`\`mermaid\s*\n)---\ntitle:\s*\"[^\"]*\"\n---\n',
    r'\1',
    text,
)
open('$f', 'w').write(text)
"

    # Convert all MkDocs admonition blocks (??? / ???+ / !!!) to
    # LaTeX-friendly markdown. Strips the header line, dedents the body,
    # and emits a bold title for non-Proof blocks.
    python3 -c "
import re, sys
lines = open('$f').readlines()
out = []
in_admonition = False
for line in lines:
    stripped = line.rstrip('\n')
    s = stripped.lstrip()
    m = re.match(r'^(!!!|\?\?\?\+?)\s+\w+(\s+\"([^\"]*)\")?', s)
    if m:
        in_admonition = True
        title = m.group(3)
        if title and title.startswith('Proof'):
            pass
        elif title:
            out.append('**' + title + '.**\n\n')
        continue
    if in_admonition:
        if stripped.strip() == '':
            out.append('\n')
            continue
        if stripped.startswith('    '):
            out.append(stripped[4:] + '\n')
            continue
        in_admonition = False
        out.append(line)
    else:
        out.append(line)
open('$f', 'w').writelines(out)
"
    # Dedent all 4-space-indented content that isn't inside code fences.
    # MkDocs uses 4-space indent for admonition/details content; Pandoc
    # treats it as a code block. Strip one level of indentation globally.
    python3 -c "
import sys
lines = open('$f').readlines()
out = []
in_code = False
for line in lines:
    s = line.rstrip('\n')
    if s.strip().startswith('\x60\x60\x60'):
        in_code = not in_code
        out.append(line)
        continue
    if in_code:
        out.append(line)
        continue
    # Dedent one level (4 spaces) if indented
    if s.startswith('    ') and not s.startswith('        '):
        out.append(s[4:] + '\n')
    elif s.startswith('        '):
        # Two levels of indent: remove one
        out.append(s[4:] + '\n')
    else:
        out.append(line)
open('$f', 'w').writelines(out)
"
done
echo "  Stripped heading numbers"
echo "  Stripped Mermaid YAML titles"
echo "  Converted admonition blocks (proofs, derivations, warnings, etc.)"
echo "  Dedented admonition content"


# Apply diagram captions for List of Figures
python3 "$TOOLS_DIR/diagram-captions.py" "$RENDERED_ACTIVE"

# Generate appendix content
python3 "$TOOLS_DIR/generate-stat-tables.py"
[ -f "$TOOLS_DIR/generate-math-tables.py" ] && python3 "$TOOLS_DIR/generate-math-tables.py"
[ -f "$TOOLS_DIR/generate-notation-index.py" ] && python3 "$TOOLS_DIR/generate-notation-index.py"
[ -f "$TOOLS_DIR/generate-subject-index.py" ] && python3 "$TOOLS_DIR/generate-subject-index.py"
# Assemble exercise solutions if they exist
SOLUTIONS_DIR="$PROJECT_ROOT/docs/solutions"
if [ -d "$SOLUTIONS_DIR" ]; then
    echo "# Solutions to Exercises" > "$OUT/solutions.md"
    echo "" >> "$OUT/solutions.md"
    for sf in "$SOLUTIONS_DIR"/[0-9]*.md; do
        [ -f "$sf" ] || continue
        # Strip copyright headers, demote H1 to H2 so they become sections
        # within the Solutions chapter (not standalone chapters)
        sed '/^<!--.*-->$/d' "$sf" | sed '/^$/N;/^\n$/d' | sed 's/^# /## /' >> "$OUT/solutions.md"
        echo "" >> "$OUT/solutions.md"
    done
    echo "  Assembled exercise solutions ($(ls "$SOLUTIONS_DIR"/[0-9]*.md 2>/dev/null | wc -l | tr -d ' ') chapters)"

    # Process admonitions in assembled solutions (??? success "Solution", etc.)
    python3 -c "
import re, sys
f = '$OUT/solutions.md'
lines = open(f).readlines()
out = []
in_admonition = False
for line in lines:
    stripped = line.rstrip('\n')
    s = stripped.lstrip()
    m = re.match(r'^(!!!|\?\?\?\+?)\s+\w+(\s+\"([^\"]*)\")?', s)
    if m:
        in_admonition = True
        title = m.group(3)
        if title and title.startswith('Proof'):
            pass
        elif title:
            out.append('**' + title + '.**\n\n')
        continue
    if in_admonition:
        if stripped.strip() == '':
            out.append('\n')
            continue
        if stripped.startswith('    '):
            out.append(stripped[4:] + '\n')
            continue
        in_admonition = False
        out.append(line)
    else:
        out.append(line)
open(f, 'w').writelines(out)
"
    echo "  Processed admonitions in solutions"
fi

python3 "$TOOLS_DIR/extract-bibliography.py"
echo ""

# ──────────────────────────────────────────────
# Phase 2: Pandoc → PDF via lualatex
# ──────────────────────────────────────────────
echo "Phase 2: Building PDF with pandoc + lualatex..."
echo ""

DRAFT_LINE=""
if [ "$DRAFT" = true ]; then
    DRAFT_LINE="draft: true"
    echo "  Draft watermark enabled"
fi

# Read version from package.json
VERSION=$(python3 -c "import json; print(json.load(open('$PROJECT_ROOT/package.json'))['version'])")
echo "  Version: v${VERSION}"

cat > "$OUT/metadata.yaml" << METAEOF
---
title: "Evenwicht"
subtitle: "Quantitative Methods from Foundations to Frontiers"
author: "B.B. Jansen"
version: "${VERSION}"
toc: true
toc-depth: 2
geometry: "margin=1in"
fontsize: 11pt
linestretch: 1.3
graphics: true
indent: false
${DRAFT_LINE}
---
METAEOF

# Create appendix font-size wrapper
cat > "$OUT/appendix-start.md" << 'APPEOF'
```{=latex}
\small
\setstretch{1.15}
```
APPEOF

# Build input file list: metadata + front matter + chapters + appendices
FRONT="$PROJECT_ROOT/docs/front"
INPUTS=("$OUT/metadata.yaml")
[ -f "$FRONT/how-to-read.md" ] && INPUTS+=("$FRONT/how-to-read.md")
[ -f "$FRONT/acknowledgments.md" ] && INPUTS+=("$FRONT/acknowledgments.md")
[ -f "$FRONT/errata.md" ] && INPUTS+=("$FRONT/errata.md")
INPUTS+=("$RENDERED_ACTIVE"/[0-9]*.md "$OUT/appendix-start.md")
[ -f "$OUT/math-tables.md" ] && INPUTS+=("$OUT/math-tables.md")
[ -f "$OUT/stat-tables.md" ] && INPUTS+=("$OUT/stat-tables.md")
[ -f "$OUT/notation-index.md" ] && INPUTS+=("$OUT/notation-index.md")
[ -f "$OUT/solutions.md" ] && INPUTS+=("$OUT/solutions.md")
[ -f "$OUT/subject-index.md" ] && INPUTS+=("$OUT/subject-index.md")
[ -f "$OUT/bibliography.md" ] && INPUTS+=("$OUT/bibliography.md")

pandoc \
    "${INPUTS[@]}" \
    --pdf-engine=lualatex \
    --template="$TEMPLATE_DIR/academic.latex" \
    --toc \
    --toc-depth=2 \
    --resource-path="$RENDERED_ACTIVE" \
    --wrap=none \
    --top-level-division=chapter \
    -o "$OUT/evenwicht.pdf"

rm -f "$OUT/metadata.yaml"

# Clean up draft copies
if [ "$DRAFT" = true ] && [ -d "$OUT/rendered-draft" ]; then
    rm -rf "$OUT/rendered-draft"
fi

# Copy versioned PDF to /book
BOOK_DIR="$PROJECT_ROOT/book"
mkdir -p "$BOOK_DIR"
VERSIONED_NAME="evenwicht-v${VERSION}.pdf"
cp "$OUT/evenwicht.pdf" "$BOOK_DIR/$VERSIONED_NAME"
# Also keep a latest symlink
ln -sf "$VERSIONED_NAME" "$BOOK_DIR/evenwicht-latest.pdf"

echo ""
echo "============================================"
echo "  Build complete!"
echo "  Output: $OUT/evenwicht.pdf"
echo "  Book:   $BOOK_DIR/$VERSIONED_NAME"
echo "  Size:   $(du -h "$OUT/evenwicht.pdf" | cut -f1)"
echo "============================================"
