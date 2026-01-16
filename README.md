# Organizations Directory REST API

REST API приложение для справочника Организаций, Зданий и Деятельности.

## Технологический стек

- **FastAPI** - веб-фреймворк для создания API
- **Pydantic** - валидация данных и настройки
- **SQLAlchemy** - ORM для работы с базой данных
- **Alembic** - миграции базы данных
- **PostgreSQL** - реляционная база данных
- **Docker & Docker Compose** - контейнеризация приложения

## Структура базы данных

### Таблицы:

1. **buildings** - Здания
   - id, address, latitude, longitude

2. **activities** - Виды деятельности (древовидная структура, макс. 3 уровня)
   - id, name, parent_id, level

3. **organizations** - Организации
   - id, name, building_id

4. **phone_numbers** - Телефонные номера организаций
   - id, number, organization_id

5. **organization_activity** - Связь организаций и видов деятельности (many-to-many)

## Быстрый старт

### Предварительные требования

- Docker
- Docker Compose

### Разворачивание приложения

1. **Клонировать проект** (если он в репозитории) или перейти в директорию проекта:
   ```bash
   cd /REST-API-Application
   ```

2. **Запустить приложение с помощью Docker Compose:**
   ```bash
   docker-compose up --build
   ```

   Эта команда:
   - Создаст и запустит контейнер PostgreSQL
   - Создаст и запустит контейнер приложения
   - Применит миграции базы данных
   - Заполнит базу тестовыми данными
   - Запустит API сервер на порту 8000

3. **Проверить статус:**
   ```bash
   docker-compose ps
   ```

4. **Приложение будет доступно по адресу:**
   - API: http://localhost:8000
   - Swagger UI документация: http://localhost:8000/docs
   - ReDoc документация: http://localhost:8000/redoc

### Остановка приложения

```bash
docker-compose down
```

Для удаления данных и volumes:
```bash
docker-compose down -v
```

## API Аутентификация

Все API endpoints защищены с помощью API ключа. Ключ должен быть передан в заголовке запроса, так же не забудте заполнить .env:

```
X-API-Key: test-api-key-123456
```

**Тестовый API ключ:** `test-api-key-123456`

## API Endpoints

### Организации

#### 1. Получить список всех организаций
```http
GET /organizations/
Header: X-API-Key: test-api-key-123456
```

#### 2. Получить информацию об организации по ID
```http
GET /organizations/{organization_id}
Header: X-API-Key: test-api-key-123456
```

#### 3. Получить организации в конкретном здании
```http
GET /organizations/building/{building_id}
Header: X-API-Key: test-api-key-123456
```

#### 4. Получить организации по виду деятельности
```http
GET /organizations/activity/{activity_id}?include_children=true
Header: X-API-Key: test-api-key-123456
```

**Параметры:**
- `include_children` (bool, по умолчанию true) - включить организации из дочерних видов деятельности

**Пример:** Поиск по виду деятельности "Еда" вернет все организации с видами деятельности: Еда, Мясная продукция, Молочная продукция, Хлебобулочные изделия.

#### 5. Поиск организаций по названию
```http
GET /organizations/search/by-name?name=Рога
Header: X-API-Key: test-api-key-123456
```

#### 6. Поиск организаций по геолокации

**Поиск в радиусе:**
```http
POST /organizations/search/by-location
Header: X-API-Key: test-api-key-123456
Content-Type: application/json

{
  "latitude": 55.751244,
  "longitude": 37.618423,
  "radius": 5.0
}
```

**Поиск в прямоугольной области:**
```http
POST /organizations/search/by-location
Header: X-API-Key: test-api-key-123456
Content-Type: application/json

{
  "latitude": 55.751244,
  "longitude": 37.618423,
  "min_latitude": 55.74,
  "max_latitude": 55.76,
  "min_longitude": 37.60,
  "max_longitude": 37.64
}
```

### Здания

#### 1. Получить список всех зданий
```http
GET /buildings/
Header: X-API-Key: test-api-key-123456
```

#### 2. Получить здание по ID
```http
GET /buildings/{building_id}
Header: X-API-Key: test-api-key-123456
```

### Виды деятельности

#### 1. Получить список всех видов деятельности
```http
GET /activities/
Header: X-API-Key: test-api-key-123456
```

#### 2. Получить дерево видов деятельности
```http
GET /activities/tree
Header: X-API-Key: test-api-key-123456
```

#### 3. Получить вид деятельности по ID
```http
GET /activities/{activity_id}
Header: X-API-Key: test-api-key-123456
```

## Примеры использования

### cURL

```bash
# Получить список организаций
curl -X GET "http://localhost:8000/organizations/" \
  -H "X-API-Key: test-api-key-123456"

# Поиск по названию
curl -X GET "http://localhost:8000/organizations/search/by-name?name=Рога" \
  -H "X-API-Key: test-api-key-123456"

# Поиск по геолокации (радиус)
curl -X POST "http://localhost:8000/organizations/search/by-location" \
  -H "X-API-Key: test-api-key-123456" \
  -H "Content-Type: application/json" \
  -d '{"latitude": 55.751244, "longitude": 37.618423, "radius": 5.0}'
```


## Структура проекта

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # Основное приложение FastAPI
│   ├── models.py            # SQLAlchemy модели
│   ├── schemas.py           # Pydantic схемы
│   ├── database.py          # Настройка подключения к БД
│   ├── config.py            # Конфигурация приложения
│   └── auth.py              # API ключ аутентификация
├── alembic/
│   ├── versions/
│   │   └── 001_initial_migration.py
│   ├── env.py
│   └── script.py.mako
├── alembic.ini              # Конфигурация Alembic
├── docker-compose.yml       # Docker Compose конфигурация
├── Dockerfile               # Docker образ приложения
├── requirements.txt         # Python зависимости
├── seed_data.py            # Скрипт для заполнения тестовыми данными
├── .env                     # Переменные окружения (не в git)
├── .env.example             # Пример переменных окружения
└── README.md               # Документация
```



## Особенности реализации

- **API ключ аутентификация** - все endpoints защищены
- **Древовидная структура деятельностей** - максимум 3 уровня вложенности
- **Рекурсивный поиск** - поиск по виду деятельности включает все дочерние виды
- **Геолокационный поиск** - поддержка поиска по радиусу и прямоугольной области
- **Автоматические миграции** - Alembic для версионирования схемы БД
- **Docker контейнеризация** - простое разворачивание на любой платформе
- **Swagger/ReDoc документация** - автоматически генерируемая документация API

## Логи и отладка

Просмотр логов приложения:
```bash
docker-compose logs -f app
```

Просмотр логов базы данных:
```bash
docker-compose logs -f db
```

## Тестирование

Проект включает **34 автоматических теста **

### Запуск тестов

```bash
# Установить зависимости
pip install -r requirements-test.txt

# Запустить все тесты
pytest

# С покрытием кода
pytest --cov=app --cov-report=html

# Или использовать готовый скрипт
./run_tests.sh
```

### Структура тестов

- `tests/test_auth.py` - 6 тестов API Key аутентификации
- `tests/test_organizations.py` - 15 тестов организаций
- `tests/test_buildings.py` - 5 тестов зданий
- `tests/test_activities.py` - 8 тестов видов деятельности

### Покрытие кода

- **app/auth.py**: 100%
- **app/models.py**: 100%
- **app/schemas.py**: 100%
- **app/config.py**: 100%
- **app/main.py**: 98%
- **ИТОГО: 97%**

### CI/CD

Проект настроен с автоматическим CI/CD через GitHub Actions (`.github/workflows/ci.yml`):

**3 параллельных job:**
1. **Test** - Unit тесты с PostgreSQL, линтинг (flake8), покрытие кода
2. **Docker Build** - Сборка и тестирование Docker образов
3. **Integration Test** - Интеграционные тесты полного стека

**Автозапуск при:** Push/PR в ветки `main` или `develop`

## Лицензия

MIT

## Автор

Pavel Ershov
Разработано для тестового задания
