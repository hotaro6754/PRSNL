"""Build a relationship graph for a case from its stored alerts.

Nodes and edges come only from real alert fields and evidence — hosts, external
peers, domains, TLS fingerprints, threat classes. No enrichment, no lookups; the
graph is a view of what the sensor already recorded, so it stays offline and
every node traces back to a signed alert.
"""

from __future__ import annotations

import ipaddress


def _is_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except (ValueError, TypeError):
        return False


def _host_kind(value: str, internal_nets) -> str:
    if not _is_ip(value):
        return "domain"
    try:
        addr = ipaddress.ip_address(value)
        return "host" if any(addr in net for net in internal_nets) else "external"
    except ValueError:
        return "domain"


def build_case_graph(case: dict, internal_nets=None) -> dict:
    """Return {nodes:[{id,label,kind,...}], edges:[{source,target,kind,...}]}."""
    nets = internal_nets or []
    nodes: dict[str, dict] = {}
    edges: dict[tuple, dict] = {}

    def add_node(node_id: str, kind: str, **extra) -> str:
        if not node_id:
            return node_id
        node = nodes.get(node_id)
        if node is None:
            nodes[node_id] = {"id": node_id, "label": node_id, "kind": kind, "alerts": 0, **extra}
        elif kind != "multiple" and nodes[node_id]["kind"] != kind and kind in ("host", "external", "domain"):
            pass  # keep first concrete kind
        return node_id

    def add_edge(src: str, tgt: str, kind: str, **extra) -> None:
        if not src or not tgt or src == tgt:
            return
        key = (src, tgt, kind)
        if key not in edges:
            edges[key] = {"source": src, "target": tgt, "kind": kind, "count": 0, **extra}
        edges[key]["count"] += 1

    entity = case.get("entity", "")
    if entity:
        add_node(entity, _host_kind(entity, nets), pinned=True)

    for alert in case.get("alerts", []):
        cls = alert["threat_class"]
        threat_id = f"threat:{cls}"
        add_node(threat_id, "threat", label=cls, severity=alert.get("severity"))
        src = alert.get("src", "")
        dst = alert.get("dst", "")
        # "multiple (…)" summaries are kept as a single aggregate node
        src_kind = "aggregate" if src.startswith("multiple") else _host_kind(src, nets)
        dst_kind = "aggregate" if dst.startswith("multiple") else _host_kind(dst, nets)
        if src:
            add_node(src, src_kind)
            nodes[src]["alerts"] += 1
        if dst:
            add_node(dst, dst_kind)
        if src and dst:
            add_edge(src, dst, "communicates", dport=alert.get("dport"))
        for node in (src, dst):
            if node:
                add_edge(node, threat_id, "raises")
        # pull domains and TLS fingerprints out of the evidence
        for ev in alert.get("evidence", []):
            feature, value = ev.get("feature"), ev.get("value")
            if not isinstance(value, str) or not value:
                continue
            if feature in ("registered_domain", "tls_sni") and "." in value and not _is_ip(value):
                add_node(value, "domain")
                if src:
                    add_edge(src, value, "resolves" if feature == "registered_domain" else "sni")
            elif feature == "tls_ja4":
                fp = f"ja4:{value}"
                add_node(fp, "fingerprint", label=value[:24])
                if src:
                    add_edge(src, fp, "fingerprint")

    return {
        "case_id": case.get("case_id"),
        "entity": entity,
        "nodes": list(nodes.values()),
        "edges": list(edges.values()),
    }
