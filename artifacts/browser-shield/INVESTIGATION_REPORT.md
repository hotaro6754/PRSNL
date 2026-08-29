# INVESTIGATION & CASE WORKFLOW
* **Functionality:** The `warning.html` UX deeply links to `/cases/${case_id}`.
* **UI Elements:** When the user clicks "INVESTIGATE", they land on the CyberOS Case view containing the Entity Graph, evidence ledger, and timeline. 
* **Zero Dummy Cases:** The investigation button does not use a placeholder template. If the API fails to create a case, the button degrades or passes an `UNKNOWN` state which correctly 404s the frontend case lookup.
