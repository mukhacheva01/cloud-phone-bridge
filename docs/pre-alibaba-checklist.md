# Pre-Alibaba readiness checklist

## Baseline

- [x] Docker Compose: API, worker, Redis, PostgreSQL
- [x] Mock inventory: 100 devices
- [x] Async batch start/stop via Celery
- [x] Redis-backed jobs and idempotency
- [x] OpenAPI aligned with runtime responses
- [x] Bearer auth enforced outside development mode
- [x] Mock connection-info envelope
- [x] Mock ADB command allowlist
- [x] Audit event writer

## Must pass before Alibaba credentials

- [ ] Replace demo `API_BEARER_TOKEN` and disable development bypass
- [ ] Add PostgreSQL migrations for phones, jobs, job_items, credentials and audit events
- [ ] Add idempotency fingerprint: actor + operation + request body
- [ ] Add Redis distributed locks per phone for conflicting operations
- [ ] Add retry metadata: `next_retry_at`, `last_error`, `vendor_code`, `retry_after`
- [ ] Add contract tests for 401, 400, 404, duplicate idempotency and partial failure
- [ ] Add load test for 100-device batches and worker restart recovery
- [ ] Add secret-manager integration, never store Alibaba keys in `.env` in production
- [ ] Add panel-to-API authentication and real job polling
- [ ] Define Alibaba region, API version, network mode and ADB key policy

## Exit gate

The mock environment is ready for Alibaba integration only when the checklist above is green, the OpenAPI file validates in CI, and a 100-device start/stop test passes after restarting the worker.
