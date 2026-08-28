import json

class QuarkdownEngine:
    def __init__(self):
        pass
        
    def render(self, title: str, summary: str, mermaid_src: str, stats_dict: dict) -> dict:
        markdown_content = f"# {title}\n\n## Summary\n{summary}\n\n## Entity Graph\n```mermaid\n{mermaid_src}\n```\n\n## Statistics & Infographics\n"
        
        # Core Stats
        markdown_content += f"- **Total Cases**: {stats_dict.get('total_cases', 0)}\n"
        markdown_content += f"- **Active Cases**: {stats_dict.get('active_cases', 0)}\n"
        markdown_content += f"- **Critical Cases**: {stats_dict.get('critical_cases', 0)}\n"
        markdown_content += f"- **Total Alerts**: {stats_dict.get('total_alerts', 0)}\n\n"

        # Alerts by Severity (Infographic representation)
        markdown_content += "### Alerts by Severity (Chart Data)\n"
        if "alerts_by_severity" in stats_dict and stats_dict["alerts_by_severity"]:
            markdown_content += "| Severity | Count |\n|---|---|\n"
            for sev, count in stats_dict["alerts_by_severity"].items():
                markdown_content += f"| {sev} | {count} |\n"
        markdown_content += "\n"

        # Top Entities (Infographic representation)
        markdown_content += "### Top Targeted Entities (Chart Data)\n"
        if "top_entities" in stats_dict and stats_dict["top_entities"]:
            markdown_content += "| Entity | Count |\n|---|---|\n"
            for ent in stats_dict["top_entities"]:
                markdown_content += f"| {ent.get('entity')} | {ent.get('count')} |\n"
        markdown_content += "\n"

        # Timeline Metrics (Infographic representation)
        markdown_content += "### Case Timeline (Chart Data)\n"
        if "timeline_metrics" in stats_dict and stats_dict["timeline_metrics"]:
            markdown_content += "| Date | Cases |\n|---|---|\n"
            for point in stats_dict["timeline_metrics"]:
                markdown_content += f"| {point.get('date')} | {point.get('count')} |\n"
        markdown_content += "\n"

        # Basic HTML conversion
        html_content = f"<html><body><h1>{title}</h1><p>{summary}</p>"
        html_content += "<h2>Entity Graph</h2><pre><code>" + (mermaid_src or "") + "</code></pre>"
        html_content += "<h2>Statistics & Infographics</h2><ul>"
        html_content += f"<li><b>Total Cases</b>: {stats_dict.get('total_cases', 0)}</li>"
        html_content += f"<li><b>Active Cases</b>: {stats_dict.get('active_cases', 0)}</li>"
        html_content += f"<li><b>Critical Cases</b>: {stats_dict.get('critical_cases', 0)}</li>"
        html_content += f"<li><b>Total Alerts</b>: {stats_dict.get('total_alerts', 0)}</li>"
        html_content += "</ul></body></html>"
        
        return {
            "markdown": markdown_content,
            "html": html_content,
            "pdf": None # PDF rendering requires external tools like wkhtmltopdf
        }
