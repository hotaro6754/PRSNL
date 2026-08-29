# AUDIT LOGGING

CyberOS maintains a durable, immutable Audit Log.

## Schema
`json
{
  "organization_id": "uuid",
  "actor_id": "uuid",
  "actor_type": "USER",
  "action": "EVIDENCE.EXPORT",
  "resource_type": "CyberEvidence",
  "resource_id": "uuid",
  "timestamp": "ISO8601",
  "source_ip": "1.2.3.4"
}
`

## Immutability
Normal API scopes explicitly forbid udit.update and udit.delete operations. Logs are append-only.
