# Cloud Phone Bridge

MVP Control Layer для тестирования управления 100 виртуальными Android-телефонами до подключения Alibaba Cloud.

## Что работает

- 100 mock-телефонов;
- async batch start/stop через Celery и Redis;
- Redis-backed jobs, idempotency и per-phone results;
- статусы телефонов и ADB;
- connection-info envelope;
- Bearer auth вне development режима;
- mock ADB с allowlist команд и timeout policy;
- audit event writer;
- OpenAPI 3.1 контракт;
- Docker Compose: API, worker, PostgreSQL и Redis.

## Запуск

```bash
cp .env.example .env
docker compose up --build
```

API: `http://localhost:8000`  
Swagger: `http://localhost:8000/docs`  
Healthcheck: `http://localhost:8000/health`

## Smoke test

```bash
docker compose exec api python -c "import urllib.request,json; base='http://localhost:8000'; d=json.load(urllib.request.urlopen(base+'/v1/phones')); ids=[x['phone_id'] for x in d]; req=urllib.request.Request(base+'/v1/phones/batch-start',data=json.dumps({'phone_ids':ids}).encode(),headers={'Content-Type':'application/json','Idempotency-Key':'smoke-001'},method='POST'); print(json.load(urllib.request.urlopen(req)))"
```

## До Alibaba

Рабочий список находится в [pre-Alibaba checklist](docs/pre-alibaba-checklist.md). Не подключаем Alibaba credentials, пока не закрыты миграции PostgreSQL, locks, retry metadata, contract/load tests, secret management и panel-to-API polling.

## Следующий этап

После прохождения checklist фиксируем регион и API Cloud Phone, режим сети, ADB key policy и реализуем `AlibabaAdapter` без изменения внешнего API.
