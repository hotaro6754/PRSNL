# SECURITY ARCHITECTURE

## Permissions (Manifest V3)
- `tabs`: Required to monitor and intercept high-risk navigation.
- `storage`: Required for local policy caching and verdict state management.
- `activeTab`: Required for popup interactions.
- `host_permissions: ["http://localhost:8000/*"]`: Restricts backend API calls explicitly to the CyberOS instance.

## Offline / Degraded Mode
If the CyberOS backend is unavailable, the extension degrades gracefully. It will display a "LIMITED PROTECTION" state rather than claiming "SAFE".
