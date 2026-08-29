from datetime import datetime
import uuid
from typing import List, Dict, Any
from backend.contracts.education import (
    ThreatKnowledge, LearningModule, AwarenessReport, 
    StartupPostureReport, SocietalImpactReport
)
from backend.contracts.evidence import DetectionEvidence

def create_threat_knowledge(title: str, description: str, severity: str, sources: List[str], mitigation: List[str]) -> ThreatKnowledge:
    """Builds the Educational Knowledge Base (Phase 5R). Prioritize authoritative sources."""
    # Enforce or suggest CERT-In and OWASP if no authoritative sources provided
    if not sources:
        sources = ["CERT-In Guidelines", "OWASP Top 10"]
    else:
        # Prioritize CERT-In and OWASP in the list if relevant
        auth_sources = [s for s in sources if "cert" in s.lower() or "owasp" in s.lower()]
        other_sources = [s for s in sources if not ("cert" in s.lower() or "owasp" in s.lower())]
        sources = auth_sources + other_sources

    return ThreatKnowledge(
        id=str(uuid.uuid4()),
        title=title,
        description=description,
        severity=severity,
        authoritative_sources=sources,
        mitigation_steps=mitigation
    )

def generate_learning_module(threat: ThreatKnowledge, audience: str) -> LearningModule:
    """Implements Threat-Aware Education and Learning Modules (Phase 5S, 5T). Uses Quarkdown."""
    qd_content = f"# {threat.title}\n\n**Severity**: {threat.severity}\n\n"
    qd_content += f"## Description\n{threat.description}\n\n"
    qd_content += f"## Mitigation Steps\n"
    for step in threat.mitigation_steps:
        qd_content += f"- {step}\n"
    if threat.authoritative_sources:
        qd_content += "\n## Authoritative Sources\n"
        for source in threat.authoritative_sources:
            qd_content += f"- {source}\n"

    return LearningModule(
        id=str(uuid.uuid4()),
        threat_knowledge_id=threat.id,
        title=f"Learning Module: {threat.title}",
        content=qd_content,
        quiz_questions=[],
        target_audience=audience
    )

def generate_awareness_report(telemetry: List[DetectionEvidence], external_stats: Dict[str, Any]) -> AwarenessReport:
    """Generates Awareness Reports (Phase 5U) based purely on real telemetry and verified stats."""
    total_events = len(telemetry)
    # Using Quarkdown for report rendering
    qd_report = f"# CyberOS Awareness Report\n\nTotal Telemetry Events Analyzed: {total_events}\n"
    
    if external_stats:
        qd_report += f"\n## External Verified Statistics\n"
        for k, v in external_stats.items():
            qd_report += f"- **{k}**: {v}\n"
            
    return AwarenessReport(
        id=str(uuid.uuid4()),
        telemetry_summary={"total_analyzed": total_events},
        key_threats=[],
        quarkdown_report=qd_report
    )

def generate_startup_posture_report(startup_id: str, telemetry: List[DetectionEvidence]) -> StartupPostureReport:
    """Generates Startup Security Posture Reports (Phase 5V) based on telemetry."""
    incidents = len(telemetry)
    qd_report = f"# Security Posture Report: {startup_id}\n\n"
    qd_report += f"**Incidents Detected/Prevented**: {incidents}\n"
    
    return StartupPostureReport(
        id=str(uuid.uuid4()),
        startup_id=startup_id,
        incidents_prevented=incidents,
        quarkdown_report=qd_report
    )

def generate_societal_impact_report(region: str, citizens: int, loss_prevented: float) -> SocietalImpactReport:
    """Generates Societal Impact Reports (Phase 5W) purely on real data."""
    qd_report = f"# Societal Impact Report - {region}\n\n"
    qd_report += f"**Citizens Protected**: {citizens}\n"
    qd_report += f"**Estimated Financial Loss Prevented**: ${loss_prevented:.2f}\n"
    
    return SocietalImpactReport(
        id=str(uuid.uuid4()),
        region=region,
        citizens_protected=citizens,
        estimated_financial_loss_prevented=loss_prevented,
        quarkdown_report=qd_report
    )
