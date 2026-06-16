# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only

"""Parse chapter markdown files and extract a knowledge graph."""

import json
import re
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


class _MkDocsLoader(yaml.SafeLoader):
    """Loader that ignores !!python/name and !!python/object tags used by MkDocs."""


def _ignore_python_tag(_loader: yaml.Loader, _suffix: str, _node: yaml.Node) -> None:
    return None


_MkDocsLoader.add_multi_constructor("tag:yaml.org,2002:python/", _ignore_python_tag)
DOMAINS_DIR = ROOT / "docs" / "domains"
OUTPUT_PATH = ROOT / "docs" / "javascripts" / "graph-data.json"

SINGLE_LETTER = re.compile(r"^[a-zA-Z]$")
IDENTIFIER_RE = re.compile(r"[a-zA-Z_]\w+")
MERMAID_BLOCK_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
ARROW_SOLID_RE = re.compile(
    r"(Ch(\d+))(?:\[.*?\])?\s*-->\s*(Ch(\d+))(?:\[.*?\])?"
)
ARROW_DOTTED_RE = re.compile(
    r"(Ch(\d+))(?:\[.*?\])?\s*-\.\s*(?:\".*?\"\s*)?\.?->\s*(Ch(\d+))(?:\[.*?\])?"
)
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*?(\d{2})-[a-z][a-z0-9-]*\.md\)")
BACKTICK_RE = re.compile(r"`([a-zA-Z_]\w+)`")


def parse_nav(mkdocs_path: Path) -> dict[str, tuple[str, int]]:
    """Return a mapping from chapter id (zero-padded) to (part_name, part_index)."""
    with open(mkdocs_path, encoding="utf-8") as f:
        config = yaml.load(f, Loader=_MkDocsLoader)

    chapter_to_part: dict[str, tuple[str, int]] = {}
    part_index = 0

    for nav_entry in config["nav"]:
        if not isinstance(nav_entry, dict):
            continue
        for part_label, items in nav_entry.items():
            if not isinstance(items, list):
                continue
            match = re.match(r"^[IVXLCDM]+\.\s", part_label)
            if not match:
                continue
            part_index += 1
            for item in items:
                if not isinstance(item, dict):
                    continue
                for _, md_path in item.items():
                    if not isinstance(md_path, str):
                        continue
                    fname_match = re.search(r"(\d{2})-", md_path)
                    if fname_match:
                        ch_id = fname_match.group(1)
                        chapter_to_part[ch_id] = (part_label, part_index)

    return chapter_to_part


def extract_title_from_nav(mkdocs_path: Path) -> dict[str, str]:
    """Return a mapping from chapter id to title (without the number prefix)."""
    with open(mkdocs_path, encoding="utf-8") as f:
        config = yaml.load(f, Loader=_MkDocsLoader)

    titles: dict[str, str] = {}
    for nav_entry in config["nav"]:
        if not isinstance(nav_entry, dict):
            continue
        for _, items in nav_entry.items():
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                for label, md_path in item.items():
                    if not isinstance(md_path, str):
                        continue
                    if not md_path.startswith("domains/"):
                        continue
                    fname_match = re.search(r"(\d{2})-", md_path)
                    if fname_match:
                        ch_id = fname_match.group(1)
                        title = re.sub(r"^\d+\.\s*", "", label)
                        titles[ch_id] = title

    return titles


def extract_title_from_file(path: Path) -> str:
    """Fallback: extract title from the H1 heading in the file."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^#\s+\d+\.\s+(.+)", line.strip())
            if m:
                return m.group(1).strip()
    return path.stem


def find_connections_section(text: str) -> str:
    """Extract the Connections section from chapter text."""
    pattern = re.compile(r"^##\s+(?:10\.\s+)?Connections\s*$", re.MULTILINE)
    m = pattern.search(text)
    if not m:
        return ""
    start = m.start()
    next_section = re.search(r"\n##\s+", text[m.end():])
    if next_section:
        end = m.end() + next_section.start()
    else:
        end = len(text)
    return text[start:end]


def extract_mermaid_edges(section: str) -> list[tuple[str, str]]:
    """Extract edges from mermaid diagrams in the connections section."""
    edges: list[tuple[str, str]] = []
    for block_match in MERMAID_BLOCK_RE.finditer(section):
        block = block_match.group(1)
        for line in block.split("\n"):
            for pattern in (ARROW_SOLID_RE, ARROW_DOTTED_RE):
                for m in pattern.finditer(line):
                    src_num = m.group(2).zfill(2)
                    tgt_num = m.group(4).zfill(2)
                    if src_num != tgt_num:
                        edges.append((src_num, tgt_num))
    return edges


def extract_md_link_edges(text: str, source_ch: str) -> list[tuple[str, str, str]]:
    """Extract edges from markdown links outside mermaid blocks in the chapter.

    Returns (source, target, link_text) triples.
    """
    clean_text = MERMAID_BLOCK_RE.sub("", text)
    edges: list[tuple[str, str, str]] = []
    for m in MD_LINK_RE.finditer(clean_text):
        link_text = m.group(1)
        target_ch = m.group(2)
        if target_ch != source_ch:
            edges.append((source_ch, target_ch, link_text))
    return edges


def strip_mermaid_blocks(text: str) -> str:
    """Remove all mermaid code blocks from text."""
    return MERMAID_BLOCK_RE.sub("", text)


def extract_api_names(text: str) -> set[str]:
    """Extract function/API identifiers from backtick code spans, excluding mermaid blocks."""
    clean = strip_mermaid_blocks(text)
    names: set[str] = set()
    for m in BACKTICK_RE.finditer(clean):
        name = m.group(1)
        if len(name) < 2:
            continue
        if SINGLE_LETTER.match(name):
            continue
        names.add(name)
    return names


def main() -> None:
    mkdocs_path = ROOT / "mkdocs.yml"
    chapter_to_part = parse_nav(mkdocs_path)
    nav_titles = extract_title_from_nav(mkdocs_path)

    domain_files = sorted(DOMAINS_DIR.glob("*.md"))

    nodes: list[dict] = []
    all_reference_edges: dict[tuple[str, str], str] = {}
    api_map: dict[str, set[str]] = defaultdict(set)

    for path in domain_files:
        fname_match = re.match(r"(\d{2})-", path.name)
        if not fname_match:
            continue
        ch_id = fname_match.group(1)

        title = nav_titles.get(ch_id) or extract_title_from_file(path)
        part_name, part_index = chapter_to_part.get(ch_id, ("Unknown", 0))

        nodes.append({
            "id": ch_id,
            "title": title,
            "part": part_name,
            "partIndex": part_index,
        })

        text = path.read_text(encoding="utf-8")

        connections_section = find_connections_section(text)
        mermaid_edges = extract_mermaid_edges(connections_section)
        for src, tgt in mermaid_edges:
            key = (src, tgt)
            if key not in all_reference_edges:
                all_reference_edges[key] = ""

        md_edges = extract_md_link_edges(text, ch_id)
        for src, tgt, link_text in md_edges:
            key = (src, tgt)
            if key not in all_reference_edges:
                all_reference_edges[key] = link_text

        api_names = extract_api_names(text)
        for name in api_names:
            api_map[name].add(ch_id)

    reference_edges: list[dict] = []
    for (src, tgt), context in sorted(all_reference_edges.items()):
        edge: dict = {"source": src, "target": tgt, "type": "reference"}
        if context:
            edge["context"] = context
        reference_edges.append(edge)

    shared_api_edges: list[dict] = []
    chapter_pair_functions: dict[tuple[str, str], list[str]] = defaultdict(list)
    for func_name, chapters in api_map.items():
        ch_list = sorted(chapters)
        for i in range(len(ch_list)):
            for j in range(i + 1, len(ch_list)):
                pair = (ch_list[i], ch_list[j])
                chapter_pair_functions[pair].append(func_name)

    for (src, tgt), functions in sorted(chapter_pair_functions.items()):
        if len(functions) < 2:
            continue
        functions_sorted = sorted(functions)
        shared_api_edges.append({
            "source": src,
            "target": tgt,
            "type": "shared-api",
            "functions": functions_sorted,
            "weight": len(functions_sorted),
        })

    all_edges = sorted(
        reference_edges + shared_api_edges,
        key=lambda e: (e["source"], e["target"]),
    )
    nodes.sort(key=lambda n: n["id"])

    output = {"nodes": nodes, "edges": all_edges}
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write("\n")

    ref_count = len(reference_edges)
    api_count = len(shared_api_edges)
    print(f"Parsed {len(nodes)} chapters")
    print(f"Found {ref_count} reference edges")
    print(f"Found {api_count} shared-api edges")
    print(f"Written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
