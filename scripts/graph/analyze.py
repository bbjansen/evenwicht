# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
"""Analyze the knowledge graph and output metrics to the terminal or JSON."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def _load_graph(project_root: Path) -> dict[str, Any]:
    path = project_root / "docs" / "javascripts" / "graph-data.json"
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ── graph construction ────────────────────────────────────────────────


def _build_lookups(
    data: dict[str, Any],
) -> tuple[
    dict[str, dict[str, str]],
    dict[str, int],
    dict[str, int],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    nodes_by_id: dict[str, dict[str, str]] = {}
    for node in data["nodes"]:
        nodes_by_id[node["id"]] = node

    in_degree: dict[str, int] = defaultdict(int)
    out_degree: dict[str, int] = defaultdict(int)
    for nid in nodes_by_id:
        in_degree[nid] = 0
        out_degree[nid] = 0

    ref_edges: list[dict[str, Any]] = []
    shared_edges: list[dict[str, Any]] = []

    for edge in data["edges"]:
        src, tgt = edge["source"], edge["target"]
        out_degree[src] += 1
        in_degree[tgt] += 1
        if edge.get("type") == "reference":
            ref_edges.append(edge)
        else:
            shared_edges.append(edge)

    return nodes_by_id, dict(in_degree), dict(out_degree), ref_edges, shared_edges


# ── metrics ───────────────────────────────────────────────────────────


def _top_n(
    degree: dict[str, int], nodes: dict[str, dict[str, str]], n: int = 10
) -> list[tuple[str, str, int]]:
    ranked = sorted(degree.items(), key=lambda x: x[1], reverse=True)[:n]
    return [(nid, nodes[nid]["title"], count) for nid, count in ranked]


def _isolated(
    nodes: dict[str, dict[str, str]],
    in_deg: dict[str, int],
    out_deg: dict[str, int],
) -> list[tuple[str, str]]:
    return [
        (nid, n["title"])
        for nid, n in sorted(nodes.items())
        if in_deg.get(nid, 0) == 0 and out_deg.get(nid, 0) == 0
    ]


def _orphans(
    nodes: dict[str, dict[str, str]],
    in_deg: dict[str, int],
    out_deg: dict[str, int],
) -> list[tuple[str, str]]:
    return [
        (nid, n["title"])
        for nid, n in sorted(nodes.items())
        if in_deg.get(nid, 0) == 0 and out_deg.get(nid, 0) > 0
    ]


# ── Tarjan's SCC (reference edges only) ──────────────────────────────


def _tarjan_scc(
    nodes: dict[str, dict[str, str]], ref_edges: list[dict[str, Any]]
) -> list[list[str]]:
    adj: dict[str, list[str]] = defaultdict(list)
    for e in ref_edges:
        adj[e["source"]].append(e["target"])

    index_counter = [0]
    stack: list[str] = []
    on_stack: set[str] = set()
    index_map: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    result: list[list[str]] = []

    def strongconnect(v: str) -> None:
        index_map[v] = index_counter[0]
        lowlink[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack.add(v)

        for w in adj.get(v, []):
            if w not in index_map:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in on_stack:
                lowlink[v] = min(lowlink[v], index_map[w])

        if lowlink[v] == index_map[v]:
            component: list[str] = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                component.append(w)
                if w == v:
                    break
            if len(component) > 1:
                result.append(sorted(component))

    # increase recursion limit for large graphs
    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_limit, len(nodes) * 4))
    try:
        for nid in sorted(nodes):
            if nid not in index_map:
                strongconnect(nid)
    finally:
        sys.setrecursionlimit(old_limit)

    return result


# ── topological sort (reference edges, Kahn's algorithm) ─────────────


def _topological_sort(
    nodes: dict[str, dict[str, str]], ref_edges: list[dict[str, Any]]
) -> tuple[list[str], list[str]]:
    adj: dict[str, list[str]] = defaultdict(list)
    in_deg: dict[str, int] = {nid: 0 for nid in nodes}
    for e in ref_edges:
        adj[e["source"]].append(e["target"])
        in_deg[e["target"]] += 1

    queue = sorted([nid for nid, d in in_deg.items() if d == 0])
    order: list[str] = []

    while queue:
        v = queue.pop(0)
        order.append(v)
        for w in sorted(adj.get(v, [])):
            in_deg[w] -= 1
            if in_deg[w] == 0:
                queue.append(w)
        queue.sort()

    unordered = sorted(set(nodes) - set(order))
    return order, unordered


# ── one-way references ───────────────────────────────────────────────


def _one_way_references(
    edges: list[dict[str, Any]],
) -> list[tuple[str, str]]:
    pair_set: set[tuple[str, str]] = set()
    for e in edges:
        pair_set.add((e["source"], e["target"]))

    one_way: list[tuple[str, str]] = []
    for src, tgt in sorted(pair_set):
        if (tgt, src) not in pair_set:
            one_way.append((src, tgt))
    return one_way


# ── part cohesion ─────────────────────────────────────────────────────


def _part_cohesion(
    nodes: dict[str, dict[str, str]], edges: list[dict[str, Any]]
) -> list[tuple[str, int, int, float]]:
    part_of: dict[str, str] = {nid: n.get("part", "Unknown") for nid, n in nodes.items()}
    parts = sorted(set(part_of.values()))

    intra: dict[str, int] = defaultdict(int)
    total: dict[str, int] = defaultdict(int)

    for e in edges:
        src_part = part_of.get(e["source"], "Unknown")
        tgt_part = part_of.get(e["target"], "Unknown")
        total[src_part] += 1
        if src_part != tgt_part:
            total[tgt_part] += 1
        else:
            intra[src_part] += 1

    result: list[tuple[str, int, int, float]] = []
    for part in parts:
        t = total.get(part, 0)
        i = intra.get(part, 0)
        ratio = i / t if t > 0 else 0.0
        result.append((part, i, t, ratio))
    return result


# ── formatting ────────────────────────────────────────────────────────

WIDTH = 50


def _header(title: str) -> str:
    pad = max(0, WIDTH - len(title) - 6)
    return f"\n  {chr(9472)*2} {title} {chr(9472) * (pad + 5)}"


def _print_report(data: dict[str, Any], metrics: dict[str, Any]) -> None:
    nodes = data["nodes"]
    edges = data["edges"]
    n_ref = sum(1 for e in edges if e.get("type") == "reference")
    n_shared = len(edges) - n_ref
    bar = chr(9552) * WIDTH

    print(f"\n{bar}")
    print(f"  KNOWLEDGE GRAPH ANALYSIS")
    print(f"  {len(nodes)} nodes, {len(edges)} edges ({n_ref} reference, {n_shared} shared-api)")
    print(bar)

    # in-degree
    print(_header("In-Degree (top 10)"))
    for nid, title, count in metrics["in_degree_top"]:
        print(f"  Ch {nid}  {title:<36s} {count:>3}")

    # out-degree
    print(_header("Out-Degree (top 10)"))
    for nid, title, count in metrics["out_degree_top"]:
        print(f"  Ch {nid}  {title:<36s} {count:>3}")

    # isolated
    print(_header("Isolated Chapters"))
    if metrics["isolated"]:
        for nid, title in metrics["isolated"]:
            print(f"  Ch {nid}  {title}")
    else:
        print("  None")

    # orphans
    print(_header("Orphan Chapters (zero in-degree)"))
    if metrics["orphans"]:
        for nid, title in metrics["orphans"]:
            print(f"  Ch {nid}  {title}")
    else:
        print("  None")

    # SCCs
    print(_header("Strongly Connected Components (reference edges)"))
    nodes_by_id = metrics["_nodes_by_id"]
    if metrics["sccs"]:
        for i, scc in enumerate(metrics["sccs"], 1):
            members = ", ".join(f"Ch {nid} ({nodes_by_id[nid]['title']})" for nid in scc)
            print(f"  SCC {i}: {members}")
    else:
        print("  No cycles detected")

    # topological sort
    print(_header("Topological Sort (reference edges)"))
    order, unordered = metrics["topo_order"], metrics["topo_unordered"]
    for pos, nid in enumerate(order, 1):
        print(f"  {pos:>3}. Ch {nid}  {nodes_by_id[nid]['title']}")
    if unordered:
        print(f"\n  Could not order (in cycles): {', '.join('Ch ' + n for n in unordered)}")

    # cross-reference integrity
    print(_header("Cross-Reference Integrity"))
    one_way = metrics["one_way"]
    print(f"  One-way references: {len(one_way)}")
    for src, tgt in one_way[:5]:
        src_t = nodes_by_id.get(src, {}).get("title", src)
        tgt_t = nodes_by_id.get(tgt, {}).get("title", tgt)
        print(f"    Ch {src} ({src_t}) -> Ch {tgt} ({tgt_t})")
    if len(one_way) > 5:
        print(f"    ... and {len(one_way) - 5} more")

    # part cohesion
    print(_header("Part Cohesion"))
    bar_width = 20
    for part, intra, total, ratio in metrics["part_cohesion"]:
        filled = round(ratio * bar_width)
        bar_str = chr(9608) * filled + chr(9617) * (bar_width - filled)
        print(f"  {part:<30s} {bar_str} {ratio:>5.0%}  ({intra}/{total})")

    print()


# ── JSON output ───────────────────────────────────────────────────────


def _write_json(project_root: Path, metrics: dict[str, Any]) -> None:
    output: dict[str, Any] = {}

    output["in_degree_top"] = [
        {"id": nid, "title": title, "count": count}
        for nid, title, count in metrics["in_degree_top"]
    ]
    output["out_degree_top"] = [
        {"id": nid, "title": title, "count": count}
        for nid, title, count in metrics["out_degree_top"]
    ]
    output["isolated"] = [
        {"id": nid, "title": title} for nid, title in metrics["isolated"]
    ]
    output["orphans"] = [
        {"id": nid, "title": title} for nid, title in metrics["orphans"]
    ]
    output["sccs"] = [
        [{"id": nid, "title": metrics["_nodes_by_id"][nid]["title"]} for nid in scc]
        for scc in metrics["sccs"]
    ]
    output["topological_order"] = [
        {"position": i, "id": nid, "title": metrics["_nodes_by_id"][nid]["title"]}
        for i, nid in enumerate(metrics["topo_order"], 1)
    ]
    output["topological_unordered"] = metrics["topo_unordered"]
    output["one_way_references"] = [
        {
            "source": src,
            "source_title": metrics["_nodes_by_id"].get(src, {}).get("title", src),
            "target": tgt,
            "target_title": metrics["_nodes_by_id"].get(tgt, {}).get("title", tgt),
        }
        for src, tgt in metrics["one_way"]
    ]
    output["part_cohesion"] = [
        {"part": part, "intra_edges": intra, "total_edges": total, "ratio": round(ratio, 4)}
        for part, intra, total, ratio in metrics["part_cohesion"]
    ]

    out_path = project_root / "graph" / "analysis.json"
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, ensure_ascii=False)
    print(f"Written to {out_path}")


# ── main ──────────────────────────────────────────────────────────────


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    data = _load_graph(project_root)

    nodes_by_id, in_deg, out_deg, ref_edges, _ = _build_lookups(data)
    all_edges = data["edges"]

    metrics: dict[str, Any] = {
        "_nodes_by_id": nodes_by_id,
        "in_degree_top": _top_n(in_deg, nodes_by_id),
        "out_degree_top": _top_n(out_deg, nodes_by_id),
        "isolated": _isolated(nodes_by_id, in_deg, out_deg),
        "orphans": _orphans(nodes_by_id, in_deg, out_deg),
        "sccs": _tarjan_scc(nodes_by_id, ref_edges),
        "one_way": _one_way_references(all_edges),
        "part_cohesion": _part_cohesion(nodes_by_id, all_edges),
    }

    topo_order, topo_unordered = _topological_sort(nodes_by_id, ref_edges)
    metrics["topo_order"] = topo_order
    metrics["topo_unordered"] = topo_unordered

    if "--json" in sys.argv:
        _write_json(project_root, metrics)
    else:
        _print_report(data, metrics)


if __name__ == "__main__":
    main()
