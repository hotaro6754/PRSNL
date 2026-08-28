from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4

class ReportStatistics(BaseModel):
    total_cases: int = 0
    critical_cases: int = 0
    active_cases: int = 0
    total_alerts: int = 0
    alerts_by_severity: Dict[str, int] = Field(default_factory=dict)
    cases_by_status: Dict[str, int] = Field(default_factory=dict)
    top_entities: List[Dict[str, Any]] = Field(default_factory=list)
    timeline_metrics: List[Dict[str, Any]] = Field(default_factory=list)
    additional_stats: Dict[str, Any] = Field(default_factory=dict)

class CyberReport(BaseModel):
    report_id: UUID = Field(default_factory=uuid4)
    title: str
    summary: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    statistics: ReportStatistics = Field(default_factory=ReportStatistics)
    mermaid_content: Optional[str] = None
    markdown_content: Optional[str] = None
    html_content: Optional[str] = None
    pdf_path: Optional[str] = None
