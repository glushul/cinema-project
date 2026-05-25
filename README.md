# КИНОБРО

## Установка и запуск

### 1. Клонируй репозиторий и перейди в папку

### 2. Создай и активируй виртуальное окружение
```bash
python -m venv venv
.\venv\Scripts\activate 
```

### 3. Установи зависимости
```bash
pip install fastapi uvicorn sqlalchemy pydantic sqladmin
```

### 4. Запусти сервер
```bash
uvicorn main:app --reload
```

### 5. Проверь работу
- 🌐 **API Docs**: http://127.0.0.1:8000/docs
- 📦 **Заполнить БД**: `GET /seed`

> ⚠️ **Важно**: Сначала вызови `GET /seed`, чтобы заполнить базу тестовыми данными (53 записи: фильмы, пользователи, тарифы).

---

## Эндпоинты API

### Каталог и рекомендации

| Метод | Эндпоинт | Описание | Пример |
|-------|----------|----------|--------|
| `GET` | `/catalog/` | Список фильмов, отсортированный по **математической модели** + заданной сортировке | [`?sort_by=year`](http://127.0.0.1:8000/catalog/?sort_by=year) <br> [`?sort_by=rating`](http://127.0.0.1:8000/catalog/?sort_by=rating) |
| `GET` | `/catalog/filtered` | Фильтрация каталога по параметрам | [`?genre=Фантастика&min_year=2006&min_rating=9`](http://127.0.0.1:8000/catalog/filtered?genre=Фантастика&min_year=2006&min_rating=9) <br> [`?min_year=2006&min_rating=9`](http://127.0.0.1:8000/catalog/filtered?min_year=2006&min_rating=9) <br> [`?min_year=2006`](http://127.0.0.1:8000/catalog/filtered?min_year=2006) |

### Подписки

| Метод | Эндпоинт | Описание | Пример |
|-------|----------|----------|--------|
| `POST` | `/subscription/activate/{user_id}` | Оформление подписки (план + способ оплаты) | [`/activate/2?plan=PREMIUM&payment_method=card`](http://127.0.0.1:8000/subscription/activate/2?plan=PREMIUM&payment_method=card) |

### Утилиты

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/seed` | Заполнение БД тестовыми данными |

---

## Реализация паттернов

### Математическая модель
**Файл:** `services/recommendations.py`  
**Класс:** `RecommendationEngine`  
**Формула:**  
```
Score = 0.4·R + 0.4·P + 0.2·N

где:
  R = rating / 10.0                    # Нормализованный рейтинг
  P = log(views_count + 1) / 5.0       # Популярность (логарифмическая)
  N = max(0, 10 - (2026 - release_year)) / 10.0  # Новизна
```

### Паттерны проектирования

| Паттерн | Файл | Классы | Назначение |
|---------|------|--------|------------|
| **🔄 Template Method** | `services/processes.py` | `BaseSubscriptionProcessor`, `BasicSubscriptionProcessor`, `PremiumSubscriptionProcessor` | Фиксирует алгоритм оформления подписки; наследники переопределяют шаги валидации и проверки оплаты |
| **⚙️ Strategy** | `services/strategies.py` | `PaymentStrategy`, `CardPaymentStrategy`, `SBPPaymentStrategy`, `PaymentContext`, `SortingStrategy`, `ByRatingStrategy`, `ByYearStrategy`, `SortingContext`, `PaymentStrategyFactory` | Динамический выбор способа оплаты и алгоритма сортировки каталога; фабричный метод инкапсулирует создание стратегии по строковому ключу |
| **👁️ Observer** | `services/observer.py` | `Observer`, `TicketPurchaseSubject`, `EmailNotificationObserver`, `PurchaseHistoryObserver`, `SalesStatsObserver` | Оповещение связанных систем после покупки билета: email-уведомление, запись в историю, обновление статистики |
| **🏭 Factory Method** | `services/strategies.py` | `PaymentStrategyFactory` | Централизованное создание стратегии оплаты по типу; роутер не зависит от конкретных классов стратегий |
| **🏗️ Abstract Factory** | `services/abstract_factory.py` | `TicketPurchaseFactory`, `PremiumCinemaFactory`, `StandardCinemaFactory`, `CinemaFactoryRegistry` | Создание семейства объектов (стратегия оплаты + набор наблюдателей) в зависимости от типа кинотеатра; Premium даёт полный набор, Standard — урезанный |
| **📋 Command** | `services/processes.py` | `Command`, `ActivateSubscriptionCommand` | Инкапсуляция операции активации подписки с поддержкой отмены через `undo()`: при отмене возвращает деньги и удаляет подписку из БД |
| **🎭 Decorator** | `services/filters.py` | `GenreFilterDecorator`, `RatingFilterDecorator`, `YearFilterDecorator` | Динамическое наложение фильтров на каталог без изменения базового объекта |
