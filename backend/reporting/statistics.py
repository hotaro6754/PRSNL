from backend.repositories.mongo import MongoRepository
from backend.contracts.report import ReportStatistics

class StatisticsEngine:
    def __init__(self, mongo: MongoRepository):
        self.mongo = mongo

    async def generate_statistics(self) -> ReportStatistics:
        try:
            active = await self.mongo.cases.count_documents({"status": "OPEN"})
            critical = await self.mongo.cases.count_documents({"severity": {"$in": ["CRITICAL", "HIGH"]}})
            total_cases = await self.mongo.cases.count_documents({})
            total_alerts = await self.mongo.alerts.count_documents({})

            # Calculate real alerts by severity
            alerts_by_sev_cursor = self.mongo.alerts.aggregate([
                {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
            ])
            alerts_by_severity = {doc["_id"] or "UNKNOWN": doc["count"] for doc in await alerts_by_sev_cursor.to_list(None)}

            # Calculate cases by status
            cases_by_status_cursor = self.mongo.cases.aggregate([
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ])
            cases_by_status = {doc["_id"] or "UNKNOWN": doc["count"] for doc in await cases_by_status_cursor.to_list(None)}

            # Calculate top entities (most targeted)
            top_entities_cursor = self.mongo.cases.aggregate([
                {"$match": {"primary_entity": {"$exists": True, "$ne": None}}},
                {"$group": {"_id": "$primary_entity", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ])
            top_entities = [{"entity": doc["_id"], "count": doc["count"]} for doc in await top_entities_cursor.to_list(None)]

            # Calculate timeline metrics (cases by day)
            timeline_cursor = self.mongo.cases.aggregate([
                {"$match": {"created_at": {"$exists": True, "$ne": None}}},
                {"$project": {"date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}}},
                {"$group": {"_id": "$date", "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}},
                {"$limit": 14}
            ])
            timeline_metrics = [{"date": doc["_id"], "count": doc["count"]} for doc in await timeline_cursor.to_list(None)]

        except Exception:
            active = 0
            critical = 0
            total_cases = 0
            total_alerts = 0
            alerts_by_severity = {}
            cases_by_status = {}
            top_entities = []
            timeline_metrics = []
            
        return ReportStatistics(
            total_cases=total_cases,
            critical_cases=critical,
            active_cases=active,
            total_alerts=total_alerts,
            alerts_by_severity=alerts_by_severity,
            cases_by_status=cases_by_status,
            top_entities=top_entities,
            timeline_metrics=timeline_metrics
        )
