import os
from typing import List, Dict, Any
from backend.contracts.case import CyberCase

class MermaidGenerator:
    def __init__(self, output_dir: str = "artifacts/reports/mermaid"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_entity_graph(self, case: CyberCase) -> str:
        """Generates a Mermaid graph from a CyberCase."""
        lines = ["graph TD"]
        nodes = set()
        edges = set()
        
        case_id_str = str(case.case_id)
        
        if case.primary_entity:
            nodes.add(f'E["{case.primary_entity}"]')
            
        for ev in case.evidence:
            if hasattr(ev, 'value') and ev.value:
                # safe string for mermaid node
                val = str(ev.value).replace('"', "'")
                node_id = f'N_{hash(val) % 100000}'
                nodes.add(f'{node_id}["{val}"]')
                if case.primary_entity:
                    edges.add(f'E -->|evidence| {node_id}')
        
        for n in nodes:
            lines.append(f"    {n}")
        for e in edges:
            lines.append(f"    {e}")
            
        mermaid_src = "\n".join(lines)
        
        # Save to artifacts
        filename = os.path.join(self.output_dir, f"graph_{case_id_str}.mmd")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(mermaid_src)
            
        return mermaid_src
