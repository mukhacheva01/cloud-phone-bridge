# Архитектура Cloud Phone Bridge

## Принципы

1. **Provider-agnostic core**: бизнес-логика не зависит от SDK конкретного вендора.
2. **Async by default**: массовые и долгие операции выполняются через jobs.
3. **Per-item result**: каждый телефон имеет независимый результат.
4. **State reconciliation**: локальное состояние периодически сверяется с провайдером.
5. **Secrets by reference**: секреты передаются через secret manager, а не конфигурационные файлы.

## Компоненты

### API Gateway

Проверяет авторизацию, JSON schema, лимиты размера batch и `Idempotency-Key`. Создает correlation ID и возвращает `202 Accepted` для асинхронных команд.

### Orchestrator

1. Загружает телефоны и группирует их по провайдеру.
2. Проверяет допустимость перехода состояния.
3. Делит набор на чанки согласно capabilities адаптера.
4. Создает Job и PhoneOperation для каждого устройства.
5. Передает операции воркерам через очередь.
6. Агрегирует состояния без потери частичных результатов.

### Vendor Adapter

Минимальный интерфейс:

```text
capabilities()
create(configs)
start(vendor_ids)
stop(vendor_ids)
delete(vendor_ids)
get_connection_info(vendor_ids)
install_marketplace_app(vendor_ids, app_id, version_id)
get_status(vendor_ids)
```

Адаптер нормализует vendor-specific ошибки в единый набор: `RATE_LIMITED`, `AUTH_FAILED`, `NOT_FOUND`, `INVALID_STATE`, `TEMPORARY_UNAVAILABLE`, `PERMANENT_FAILURE`.

### ADB Manager

Создает краткоживущую сессию, получает connection info, подключается, выполняет разрешенную операцию и гарантированно закрывает соединение. Параллелизм ограничивается глобально и на провайдера.

### Storage

Рекомендуемые таблицы: `phones`, `groups`, `phone_tags`, `jobs`, `job_items`, `vendor_accounts`, `connection_leases`, `audit_events`, `outbox_events`. Для надежной публикации заданий используется transactional outbox.

## Поток batch-start

```text
Client -> POST /phones/batch-start
Gateway -> validate auth/idempotency/input
Orchestrator -> resolve phones -> group by vendor -> create job/items
Queue -> vendor workers -> adapter.start(chunks)
Workers -> persist per-phone result -> retry transient errors
Aggregator -> finalize job
Client -> GET /jobs/{job_id}
```

## Состояния и конкуренция

Команды для одного устройства сериализуются. `start` для `running` завершается успешно без вызова вендора; `stop` для `stopped` аналогично. Конфликтующие операции возвращают `INVALID_STATE` либо ожидают завершения активной операции согласно выбранной политике.

## Масштабирование

API stateless и масштабируется горизонтально. Воркеры масштабируются отдельно по очередям/провайдерам. Rate limit хранится централизованно, например в Redis. Основное состояние хранится в PostgreSQL; бинарные APK находятся в object storage.

## Рекомендуемый MVP

Первая версия: один vendor adapter, lifecycle start/stop, connection info, jobs, idempotency, retries, базовый inventory и ADB connect/install. Создание/удаление устройств, marketplace и сложные UI-команды лучше добавить после проверки ограничений реального провайдера.
