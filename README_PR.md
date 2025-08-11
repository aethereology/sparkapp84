# sparkapp84 — Prod hardening + Terraform
Adds API (/api/v1), web, CI, Redis caching, webhook security/idempotency, signed GCS URLs, and Terraform infra.
After `terraform apply` set secrets: REDIS_URL (redis://<memorystore_ip>:6379/0), GCP_VPC_CONNECTOR, etc.
