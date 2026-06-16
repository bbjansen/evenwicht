#!/usr/bin/env bash
# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.
# Adds license headers to all source and documentation files.
# Safe to run multiple times — skips files that already have the header.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# License headers
read -r -d '' TS_HEADER << 'EOF' || true
/**
 *	∫∫∫	Evenwicht
 *
 *		Mathematical Operators
 *		Algebraic Structures
 *		Probability & Statistics
 *
 *		Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
 *
 *		SPDX-License-Identifier: AGPL-3.0-only
 *		See LICENSE for full terms. Commercial licensing available.
 */
EOF

read -r -d '' MD_HEADER << 'EOF' || true
<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->
EOF

read -r -d '' SH_HEADER << 'EOF' || true
# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.
EOF

added=0
skipped=0

# TypeScript/JavaScript files
echo "=== TypeScript/JavaScript files ==="
if [ -d "$PROJECT_ROOT/src" ]; then
    find "$PROJECT_ROOT/src" -name "*.ts" -o -name "*.js" 2>/dev/null | while read -r f; do
        if grep -q "SPDX-License-Identifier" "$f" 2>/dev/null; then
            skipped=$((skipped+1))
        else
            { echo "$TS_HEADER"; echo ""; cat "$f"; } > "${f}.tmp" && mv "${f}.tmp" "$f"
            echo "  + $(basename "$f")"
            added=$((added+1))
        fi
    done
fi

# Test files
for dir in "$PROJECT_ROOT/test" "$PROJECT_ROOT/tests"; do
    [ -d "$dir" ] || continue
    find "$dir" -name "*.ts" -o -name "*.js" 2>/dev/null | while read -r f; do
        if grep -q "SPDX-License-Identifier" "$f" 2>/dev/null; then
            :
        else
            { echo "$TS_HEADER"; echo ""; cat "$f"; } > "${f}.tmp" && mv "${f}.tmp" "$f"
            echo "  + $(basename "$f")"
        fi
    done
done

# Documentation files (Markdown)
echo ""
echo "=== Documentation files ==="
for f in "$PROJECT_ROOT"/docs/domains/*.md; do
    if grep -q "SPDX-License-Identifier" "$f" 2>/dev/null; then
        :
    else
        { echo "$MD_HEADER"; echo ""; cat "$f"; } > "${f}.tmp" && mv "${f}.tmp" "$f"
        echo "  + $(basename "$f")"
    fi
done

for f in "$PROJECT_ROOT"/docs/*.md; do
    if grep -q "SPDX-License-Identifier" "$f" 2>/dev/null; then
        :
    else
        { echo "$MD_HEADER"; echo ""; cat "$f"; } > "${f}.tmp" && mv "${f}.tmp" "$f"
        echo "  + $(basename "$f")"
    fi
done

# README
if ! grep -q "SPDX-License-Identifier" "$PROJECT_ROOT/README.md" 2>/dev/null; then
    { echo "$MD_HEADER"; echo ""; cat "$PROJECT_ROOT/README.md"; } > "$PROJECT_ROOT/README.md.tmp" && mv "$PROJECT_ROOT/README.md.tmp" "$PROJECT_ROOT/README.md"
    echo "  + README.md"
fi

# Shell scripts
echo ""
echo "=== Shell scripts ==="
for f in "$PROJECT_ROOT"/scripts/*.sh; do
    if grep -q "SPDX-License-Identifier" "$f" 2>/dev/null; then
        :
    else
        # Insert after the shebang line (line 1) if present
        if head -1 "$f" | grep -q "^#!"; then
            { head -1 "$f"; echo "$SH_HEADER"; tail -n +2 "$f"; } > "${f}.tmp" && mv "${f}.tmp" "$f"
        else
            { echo "$SH_HEADER"; echo ""; cat "$f"; } > "${f}.tmp" && mv "${f}.tmp" "$f"
        fi
        echo "  + $(basename "$f")"
    fi
done

# Python files (verify + build tools)
echo ""
echo "=== Python files ==="
find "$PROJECT_ROOT/verify" "$PROJECT_ROOT/build" -name "*.py" -type f 2>/dev/null | while read -r f; do
    if grep -q "SPDX-License-Identifier" "$f" 2>/dev/null; then
        :
    else
        if head -1 "$f" | grep -q "^#!"; then
            { head -1 "$f"; echo ""; echo "$SH_HEADER"; echo ""; tail -n +2 "$f"; } > "${f}.tmp" && mv "${f}.tmp" "$f"
        else
            { echo "$SH_HEADER"; echo ""; cat "$f"; } > "${f}.tmp" && mv "${f}.tmp" "$f"
        fi
        echo "  + $(basename "$f")"
    fi
done

echo ""
echo "Done."
