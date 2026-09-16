# Cloud Phone Bridge

MVP Control Layer для тестирования управления 100 виртуальными Android-телефонами без подключения Alibaba Cloud.

## Что уже работает

- 100 предсозданных mock-телефонов;
- batch start/stop до 100 устройств;
- idempotency через `Idempotency-Key`;
- статусы телефонов `stopped/running` и `offline/online`;
- job status с результатом по каждому телефону;
- connection info с mock ADB endpoint;
- FastAPI Swagger UI;
- Docker Compose: API, worker, PostgreSQL и Redis;
- интерфейс `VendorAdapter`, который позже заменит `MockAdapter` на `AlibabaAdapter`.

## Локальный запуск

```bash
cp .env.example .env
docker compose up --build
```

API: `http://localhost:8000`  
Swagger: `http://localhost:8000/docs`  
Healthcheck: `http://localhost:8000/health`

## Быстрый сценарий через Swagger

1. Откройте `GET /phones` и возьмите UUID устройств.
2. Вызовите `POST /phones/batch-start` с массивом из 100 `phone_ids` и заголовком `Idempotency-Key: demo-start-001`.
3. Откройте `GET /jobs/{job_id}` и проверьте `succeeded` по каждому item.
4. Проверьте `GET /phones?status_filter=running`.
5. Вызовите `POST /phones/connection-info` для получения mock IP, порта и ticket.
6. Вызовите `POST /phones/batch-stop` с новым idempotency key.

## Важно

Mock-сервис не подключается к реальным телефонам и не выполняет настоящий ADB. Он проверяет Control Layer, batch-логику, контракты, статусы и обработку jobs. Перед Alibaba Cloud нужно добавить persistence jobs в PostgreSQL, настоящий worker fan-out и интеграционные тесты с sandbox API провайдера.

## Следующий этап

После регистрации Alibaba Cloud фиксируем API версии, регион, лимиты, lifecycle endpoints, connection info и способ ADB-доступа, затем реализуем `AlibabaAdapter` без изменения внешнего API.
