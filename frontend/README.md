# Sentinel-26145 dashboard

Analyst console for the Sentinel API. Every figure on screen comes from the API
(`/api/*`) or its live stream (`/api/stream`); the dashboard holds no sample data.

| Page | Shows |
|------|-------|
| Overview | alert counts per problem-statement category (a–f), severity, custody chain head, recent sources |
| Alerts | filterable alert list, live arrivals; detail page with evidence, visibility, custody and evidence-bundle export |
| Cases | alerts grouped by host, escalation, analyst status changes (admin token) |
| Evaluation | measured detection results, throughput benchmark and DGA model card, read from the report files |
| Sensor | access tokens, capture replay / upload, pipeline health, custody chain verification |

```bash
npm ci
NEXT_PUBLIC_SENTINEL_API=http://localhost:8000 npx next build
npx next start -p 3000
```

`NEXT_PUBLIC_SENTINEL_API` is read at build time. Tokens entered on the Sensor page are kept in the tab's session storage.
