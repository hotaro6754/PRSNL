# RBAC (Role-Based Access Control)

CyberOS abandons legacy hard-coded if user.role == "admin" conditional structures in favor of a granular Permission Registry.

## Roles & Permissions
A **Role** is a collection of explicitly defined **Permissions**.
Permissions are formatted as esource.action (e.g., cases.read, vidence.add).

### Base Roles
* **PLATFORM_ADMIN**: Superuser access.
* **ORGANIZATION_OWNER**: Full administrative access within the tenant scope.
* **SECURITY_ANALYST**: Read-write access to cases and evidence; no user management.
* **EXECUTIVE_VIEWER**: Read-only access to dashboards and reports.

## Middleware Enforcement
FastAPI enforces RBAC natively via dependency injection:
`python
@app.get('/api/cases')
def get_cases(tenant=Depends(get_current_tenant), authorized=Depends(require_permission('cases.read'))):
    pass
`
"@ > docs/RBAC.md

@"
# AUTHORIZATION

CyberOS Authorization relies on a multi-dimensional scope resolver:
USER + ORGANIZATION + ROLE + PERMISSION + RESOURCE OWNERSHIP

1. **Authentication**: Resolves WHO is acting.
2. **Tenancy**: Resolves WHERE they are acting.
3. **Role**: Resolves WHAT they are acting as.
4. **Ownership**: Resolves WHICH specific resource they are targeting (e.g., is the Case assigned to their Team?).

Authorization failures yield 403 Forbidden uniformly to prevent existence-leaking (e.g., distinguishing between 404 and 403 on another tenant's ID).
