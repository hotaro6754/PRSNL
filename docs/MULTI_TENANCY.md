# MULTI-TENANCY

CyberOS utilizes a logical separation model for multi-tenancy. All primary resources (CyberCase, Alert, CyberEvidence, User) are stored in shared MongoDB collections but are strictly segmented by an explicit organization_id.

## Tenant Identity
Every resource carries the organization_id field.
* Incoming requests are resolved to an authenticated identity (JWT).
* The identity provides Organization Membership.
* The backend forcibly overrides any client-supplied organization_id with the authenticated context.

## Tenant Context Resolution
`python
def get_current_tenant(token: str = Depends(oauth2_scheme)):
    user = verify_jwt(token)
    if not user.organization_id:
        raise HTTPException(status_code=403, detail="No tenant context")
    return user.organization_id
`

## Black-Box Isolation
The MongoDB Data Access Layer implicitly appends {"organization_id": current_tenant_id} to all .find() and .find_one() queries prior to database execution. Cross-tenant leakage is mathematically prevented at the database driver level.
