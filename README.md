# Cloud Phone Bridge

MVP Control Layer РґР»СЏ С‚РµСЃС‚РёСЂРѕРІР°РЅРёСЏ СѓРїСЂР°РІР»РµРЅРёСЏ 100 РІРёСЂС‚СѓР°Р»СЊРЅС‹РјРё Android-С‚РµР»РµС„РѕРЅР°РјРё Р±РµР· РїРѕРґРєР»СЋС‡РµРЅРёСЏ Alibaba Cloud.

## Р§С‚Рѕ СѓР¶Рµ СЂР°Р±РѕС‚Р°РµС‚

- 100 РїСЂРµРґСЃРѕР·РґР°РЅРЅС‹С… mock-С‚РµР»РµС„РѕРЅРѕРІ;
- batch start/stop РґРѕ 100 СѓСЃС‚СЂРѕР№СЃС‚РІ;
- idempotency С‡РµСЂРµР· `Idempotency-Key`;
- СЃС‚Р°С‚СѓСЃС‹ С‚РµР»РµС„РѕРЅРѕРІ `stopped/running` Рё `offline/online`;
- job status СЃ СЂРµР·СѓР»СЊС‚Р°С‚РѕРј РїРѕ РєР°Р¶РґРѕРјСѓ С‚РµР»РµС„РѕРЅСѓ;
- connection info СЃ mock ADB endpoint;
- FastAPI Swagger UI;
- Docker Compose: API, worker, PostgreSQL Рё Redis;
- РёРЅС‚РµСЂС„РµР№СЃ `VendorAdapter`, РєРѕС‚РѕСЂС‹Р№ РїРѕР·Р¶Рµ Р·Р°РјРµРЅРёС‚ `MockAdapter` РЅР° `AlibabaAdapter`.

## Р›РѕРєР°Р»СЊРЅС‹Р№ Р·Р°РїСѓСЃРє

```bash
cp .env.example .env
docker compose up --build
```

API: `http://localhost:8000`\r\nSwagger: `http://localhost:8000/docs`\r\nHealthcheck: `http://localhost:8000/health`

## Р‘С‹СЃС‚СЂС‹Р№ СЃС†РµРЅР°СЂРёР№ С‡РµСЂРµР· Swagger

1. РћС‚РєСЂРѕР№С‚Рµ `GET /phones` Рё РІРѕР·СЊРјРёС‚Рµ UUID СѓСЃС‚СЂРѕР№СЃС‚РІ.
2. Р’С‹Р·РѕРІРёС‚Рµ `POST /phones/batch-start` СЃ РјР°СЃСЃРёРІРѕРј РёР· 100 `phone_ids` Рё Р·Р°РіРѕР»РѕРІРєРѕРј `Idempotency-Key: demo-start-001`.
3. РћС‚РєСЂРѕР№С‚Рµ `GET /jobs/{job_id}` Рё РїСЂРѕРІРµСЂСЊС‚Рµ `succeeded` РїРѕ РєР°Р¶РґРѕРјСѓ item.
4. РџСЂРѕРІРµСЂСЊС‚Рµ `GET /phones?status_filter=running`.
5. Р’С‹Р·РѕРІРёС‚Рµ `POST /phones/connection-info` РґР»СЏ РїРѕР»СѓС‡РµРЅРёСЏ mock IP, РїРѕСЂС‚Р° Рё ticket.
6. Р’С‹Р·РѕРІРёС‚Рµ `POST /phones/batch-stop` СЃ РЅРѕРІС‹Рј idempotency key.

## Р’Р°Р¶РЅРѕ

Mock-СЃРµСЂРІРёСЃ РЅРµ РїРѕРґРєР»СЋС‡Р°РµС‚СЃСЏ Рє СЂРµР°Р»СЊРЅС‹Рј С‚РµР»РµС„РѕРЅР°Рј Рё РЅРµ РІС‹РїРѕР»РЅСЏРµС‚ РЅР°СЃС‚РѕСЏС‰РёР№ ADB. РћРЅ РїСЂРѕРІРµСЂСЏРµС‚ Control Layer, batch-Р»РѕРіРёРєСѓ, РєРѕРЅС‚СЂР°РєС‚С‹, СЃС‚Р°С‚СѓСЃС‹ Рё РѕР±СЂР°Р±РѕС‚РєСѓ jobs. РџРµСЂРµРґ Alibaba Cloud РЅСѓР¶РЅРѕ РґРѕР±Р°РІРёС‚СЊ persistence jobs РІ PostgreSQL, РЅР°СЃС‚РѕСЏС‰РёР№ worker fan-out Рё РёРЅС‚РµРіСЂР°С†РёРѕРЅРЅС‹Рµ С‚РµСЃС‚С‹ СЃ sandbox API РїСЂРѕРІР°Р№РґРµСЂР°.

## РЎР»РµРґСѓСЋС‰РёР№ СЌС‚Р°Рї

РџРѕСЃР»Рµ СЂРµРіРёСЃС‚СЂР°С†РёРё Alibaba Cloud С„РёРєСЃРёСЂСѓРµРј API РІРµСЂСЃРёРё, СЂРµРіРёРѕРЅ, Р»РёРјРёС‚С‹, lifecycle endpoints, connection info Рё СЃРїРѕСЃРѕР± ADB-РґРѕСЃС‚СѓРїР°, Р·Р°С‚РµРј СЂРµР°Р»РёР·СѓРµРј `AlibabaAdapter` Р±РµР· РёР·РјРµРЅРµРЅРёСЏ РІРЅРµС€РЅРµРіРѕ API.

