# API KEYS

Machine-to-machine integrations are governed via API Keys.
* API Keys are scoped exactly like Users, mapping to specific Roles/Permissions.
* They carry explicit expiration epochs.
* Keys are hashed in the database; only the plaintext prefix and final 4 characters are retrievable post-creation.
