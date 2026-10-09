# navigation-agents

Мультиагентная платформа коллективной навигационной памяти для незрячих пользователей носимых ассистивных устройств. Курсовой проект по дисциплине «ИИ-агенты», см. полное [ТЗ](<ТЗ_ платформа коллективной навигационной памяти.html>).

Учебная цель — собственный агентский харнесс и модуль управления контекстом (без LangChain/AutoGen и аналогов). Прикладная задача (навигация незрячих) — полигон для их проверки.

## Статус на сегодня

Реализован фундамент недель 1–2 по план-графику (§19 ТЗ): модель данных, контракт API, приём событий с авторизацией и дедупликацией, минимальный симулятор устройств.

**Готово:**
- Инфраструктура: PostgreSQL+PostGIS, Redis, MinIO в Docker Compose
- Модель данных — все 10 сущностей из §8.1 ТЗ, миграция Alembic
- REST API: приём событий (дедуп), заявки на помощь, выгрузка препятствий
- Авторизация устройств по Bearer-токену
- Симулятор: виртуальное устройство идёт по графу улиц и шлёт события

**Ещё не начато** (по плану — недели 3–11):
- Агентский харнесс и модуль управления контекстом (ядро проекта, §9–10)
- Агенты: аналитик, помощник, маршрутизатор (§11)
- Голосовой контур STT/TTS, WebRTC-сессии с волонтёром
- Веб-интерфейс волонтёра/администратора, Telegram-бот
- Полноценный симулятор нагрузки (20–50 пользователей, обрывы связи, ground truth)
- Бенчмарк политик управления контекстом

## Архитектура (текущий срез)

```
┌──────────────────┐
│ Симулятор         │  виртуальные устройства, графовое перемещение
│ simulator/         │  (сегодня — синтетическая сетка вместо OSM, см. ниже)
└─────────┬──────────┘
          │ HTTPS + Bearer-токен
          ▼
┌───────────────────────────────────────────────────────────┐
│                      backend/ (FastAPI)                    │
│                                                              │
│  app/api/v1/          — роуты                               │
│    events.py           приём событий, дедупликация           │
│    assistance.py       создание заявки на помощь             │
│    hazards.py          выгрузка препятствий по bbox/since     │
│    snapshot.py         приём полнокадрового снимка (заглушка) │
│    realtime.py         WS /dialog, /signaling (заглушки)      │
│                                                              │
│  app/api/deps.py       — проверка Bearer-токена устройства    │
│  app/core/             — конфиг (pydantic-settings), сессия БД │
│  app/dao/              — DAO поверх моделей (см. ниже)         │
│  app/ioc.py            — DI-провайдеры Dishka (сессия, DAO)    │
│  app/models/           — SQLAlchemy 2.0 + GeoAlchemy2          │
│  app/schemas/          — pydantic-контракты API                │
│  app/scripts/          — provision_device.py (выдача токена)   │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ PostgreSQL 16 + PostGIS · Redis · MinIO             │    │
│  └────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────┘
```

Агентский харнесс, модуль контекста, голосовой контур, веб и Telegram-бот на этой схеме отсутствуют — их ещё нет в коде.

## Структура репозитория

```
navigation-agents/
├── docker-compose.yml       # Postgres+PostGIS, Redis, MinIO
├── .env.example             # переменные окружения (копируется в backend/.env)
│
├── backend/
│   ├── pyproject.toml
│   ├── alembic/              # миграции; env.py игнорирует служебные
│   │                          # таблицы postgis/tiger/topology при autogenerate
│   └── app/
│       ├── main.py           # точка входа FastAPI
│       ├── core/
│       │   ├── config.py     # Settings (pydantic-settings, читает .env)
│       │   ├── database.py   # async engine + get_db() dependency
│       │   └── security.py   # генерация/хеширование токена устройства
│       ├── models/           # SQLAlchemy-модели, см. раздел «Модель данных»
│       ├── dao/               # DAO: по одному классу на агрегат (Device, User,
│       │                       # Event, Hazard, AssistanceRequest), инкапсулируют SQL
│       ├── ioc.py             # Dishka: Provider с сессией (scope=REQUEST) и DAO
│       ├── schemas/          # pydantic-схемы запросов/ответов API
│       ├── api/
│       │   ├── deps.py       # get_current_device — проверка Bearer-токена (DAO через Dishka)
│       │   └── v1/           # роуты (route_class=DishkaRoute) + агрегирующий router.py
│       └── scripts/
│           └── provision_device.py  # создаёт user+device+token в обход API
│
└── simulator/
    ├── pyproject.toml
    └── simulator/
        ├── graph.py   # граф улиц (сегодня — синтетическая сетка)
        ├── device.py  # VirtualDevice: идёт по графу, шлёт события
        └── main.py    # CLI-обёртка
```

## Модель данных (§8.1 ТЗ)

| Таблица | Назначение |
|---|---|
| `users` | Аккаунт: роль (`blind_user`/`volunteer`/`admin`), язык, preferences (jsonb) |
| `devices` | Устройство: владелец, хеш токена, `revoked_at` для отзыва |
| `events` | Сигнал от устройства: геометрия (PostGIS `Geography(Point)`), детекции (jsonb), медиа-ссылки. Уникальность `(device_id, client_event_id)` — основа дедупликации |
| `hazards` | Препятствие на карте: тип, геометрия, `confidence`, статус жизненного цикла (§8.2) |
| `hazard_events` | Связь препятствия с подтверждающими/опровергающими событиями |
| `assistance_requests` | Заявка на живую помощь: геометрия, статус, назначенный волонтёр |
| `volunteers` | Профиль волонтёра: языки, районы, статус доступности |
| `sessions` | Видеосессия пользователя с волонтёром |
| `user_memories` | Долговременная память пользователя (§10.1) |
| `dialog_turns` | Эпизодическая память — история диалога (§10.1) |

Геометрия хранится как `Geography(Point, SRID=4326)` через GeoAlchemy2; GIST-индексы создаются автоматически при `create_table`, поэтому в миграциях Alembic такие индексы не дублируются вручную (`alembic/env.py` также отфильтровывает служебные таблицы postgis/tiger geocoder — иначе autogenerate пытается их удалить).

## DAO-слой и DI (Dishka)

Роуты не работают с `AsyncSession`/SQLAlchemy напрямую — SQL-запросы вынесены в DAO-классы (`app/dao/`, по одному на агрегат: `DeviceDAO`, `UserDAO`, `EventDAO`, `HazardDAO`, `AssistanceDAO`), каждый принимает `AsyncSession` в конструкторе. Сборка зависимостей — через [Dishka](https://github.com/reagento/dishka):

- `app/ioc.py` — единственный `Provider` со `scope=REQUEST`: отдаёт `AsyncSession` (одна на запрос, из `async_session_factory`) и DAO поверх неё (`provide(DeviceDAO)` и т.д. — Dishka сама резолвит `__init__`).
- `app/main.py` — `setup_dishka(build_container(), app)` вешает на FastAPI middleware, который кладёт контейнер в `request.state.dishka_container`.
- Роутеры создаются с `APIRouter(route_class=DishkaRoute)` — это автоматически оборачивает каждый обработчик в `@inject`, и параметр `FromDishka[EventDAO]` резолвится из контейнера запроса.
- `get_current_device` (`app/api/deps.py`) — не эндпоинт, а вложенная FastAPI-зависимость (`Depends(...)`), поэтому `DishkaRoute` её не подхватывает автоматически — она размечена `@inject` отдельно.

## API (§7 ТЗ)

Все запросы, кроме `/health`, требуют `Authorization: Bearer <token>` — токен выдаётся не через API, а скриптом `provision_device.py` (в ТЗ сам процесс регистрации не специфицирован).

| Метод | Путь | Статус | Описание |
|---|---|---|---|
| `POST` | `/api/v1/events` | ✅ работает | Пакетная отправка событий, дедуп по `(device_id, client_event_id)` через `ON CONFLICT DO NOTHING` |
| `POST` | `/api/v1/events/{id}/media` | ⚠️ заглушка | Принимает файлы, сохраняет на диск (`backend/data/media/`); перенос в MinIO — следующий шаг |
| `POST` | `/api/v1/assistance` | ✅ работает | Создаёт заявку; сборка сводки и подбор волонтёра (агент-маршрутизатор) — неделя 8 |
| `GET` | `/api/v1/hazards?bbox=&since=` | ✅ работает | Фильтр по bbox (`ST_MakeEnvelope`) и времени создания |
| `POST` | `/api/v1/snapshot` | ⚠️ заглушка | Приём полнокадрового снимка, без привязки к сессии |
| `WS` | `/api/v1/dialog` | ⚠️ заглушка | Закрывается с кодом 1013 — агент-помощник ещё не реализован |
| `WS` | `/api/v1/signaling` | ⚠️ заглушка | Закрывается с кодом 1013 — WebRTC-сигналинг ещё не реализован |

## Быстрый старт

```bash
# 1. Поднять инфраструктуру
docker compose up -d

# 2. Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp ../.env.example .env   # при необходимости поправить порты
alembic upgrade head
uvicorn app.main:app --reload --port 8010

# 3. Выдать токен тестовому устройству (в отдельном терминале, venv активен)
python -m app.scripts.provision_device
# → печатает device_id и token

# 4. Симулятор (в отдельном терминале)
cd ../simulator
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
python -m simulator.main --base-url http://localhost:8010 \
    --device-id <device_id> --token <token> --steps 10
```

Порт PostgreSQL в docker-compose — **5433**, а не стандартный 5432: на хосте уже мог быть занят локальный Postgres.

## Симулятор: почему сетка, а не OSM

`simulator/graph.py` строит синтетическую сетку улиц вместо реального графа OSM. Overpass API (`overpass-api.de`) недоступен из текущего окружения разработки — возвращает `406` независимо от метода и заголовков, похоже на блокировку по IP дата-центра, при этом обычный интернет работает. Интерфейс намеренно узкий (`networkx.Graph` с атрибутами `lat`/`lon` на узлах), чтобы заменить `build_demo_graph()` на `osmnx.graph_from_place(...)` без изменений в `device.py`/`main.py`.

## Дальнейшие шаги (по §19 ТЗ)

| Недели | Блок |
|---|---|
| 3–4 | Агентский харнесс, модуль управления контекстом, 4 политики вытеснения, юнит-тесты, трассировка |
| 5–6 | Агент-аналитик, достоверность и устаревание препятствий, размытие лиц |
| 7 | STT/TTS, голосовой цикл, роутинг, агент-помощник |
| 8 | Агент-маршрутизатор, WebRTC-сессия, Telegram-бот |
| 9 | Веб: карта, модерация, дашборд, отладочный экран агентов |
| 10 | Бенчмарк, прогон политик, таблицы и графики |
| 11 | Сквозной прогон на реальном устройстве, презентация, документация |
