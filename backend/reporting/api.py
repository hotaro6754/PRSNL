from fastapi import APIRouter, HTTPException, Depends
from backend.repositories.mongo import MongoRepository
from backend.contracts.report import CyberReport
from backend.reporting.statistics import StatisticsEngine
from backend.reporting.mermaid import MermaidGenerator
from backend.reporting.quarkdown import QuarkdownEngine
from backend.contracts.case import CyberCase
import uuid
import datetime

router = APIRouter()

@router.post("/api/reports", response_model=CyberReport)
async def create_report(case_id: str):
    mongo = MongoRepository()
    db_case = await mongo.cases.find_one({"case_id": case_id})
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    # Drop _id before parsing
    if "_id" in db_case:
        del db_case["_id"]
    case = CyberCase(**db_case)
    
    stats_engine = StatisticsEngine(mongo)
    stats = await stats_engine.generate_statistics()
    
    mermaid_gen = MermaidGenerator()
    mermaid_src = mermaid_gen.generate_entity_graph(case)
    
    quarkdown = QuarkdownEngine()
    render_res = quarkdown.render(
        title=f"Incident Report: {case.title}",
        summary=case.threat_summary,
        mermaid_src=mermaid_src,
        stats_dict=stats.model_dump()
    )
    
    report = CyberReport(
        report_id=uuid.uuid4(),
        title=f"Incident Report: {case.title}",
        summary=case.threat_summary,
        statistics=stats,
        mermaid_content=mermaid_src,
        markdown_content=render_res["markdown"],
        html_content=render_res["html"],
        pdf_path=render_res["pdf"]
    )
    
    # Save report to mongo
    report_dict = report.model_dump(mode="json")
    await mongo.db.reports.insert_one(report_dict)
    return report

@router.get("/api/reports", response_model=list[CyberReport])
async def list_reports():
    mongo = MongoRepository()
    cursor = mongo.db.reports.find({}).sort("generated_at", -1).limit(50)
    reports = await cursor.to_list(length=50)
    res = []
    for r in reports:
        if "_id" in r:
            del r["_id"]
        res.append(CyberReport(**r))
    return res
