# TENANT ISOLATION
* **Architecture:** Tenant context is strictly derived from the JWT `sub` and `organization_id` payload on the backend.
* **Browser Trust:** The browser is not permitted to declare its own organization. 
* **Result:** A user with an Org B token cannot query the `/cases/` endpoint for an Org A `case_id`.
