python -m venv venv
.\venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy pydantic
uvicorn main:app --reload

-endpoints-
catalog.py:
    - browse_catalog: "http://127.0.0.1:8000/catalog/?sort_by=year", "http://127.0.0.1:8000/catalog/?sort_by=rating" (сначала сортирует по результату подсчета по мат. модели, потом по заданной сортировке)
    - get_filtered_catalog: "http://127.0.0.1:8000/catalog/filtered?genre=Фантастика&min_year=2006&min_rating=9", "http://127.0.0.1:8000/catalog/filtered?min_year=2006&min_rating=9", "http://127.0.0.1:8000/catalog/filtered?min_year=2006" (фильтрация в каталоге по трем параметрам)
seed.py - seed_database: "http://127.0.0.1:8000/seed"
subscription.py - POST "http://127.0.0.1:8000/subscription/activate/2?payment_method=card&plan=PREMIUM"

-services-
Математическая модель - recommendation.py (считает рейтинг фильма по рейтингу пользователей, кол-во просмотров и году: RecommendationEngine, calculate_score(), get_ranked())
Шаблонный метод - subsription.py (оформляет подписку пользователю: BaseSubscriptionProcessor, BasicSubscriptionProcessor, PremiumSubscriptionProcessor)
Абстрактная Фабрика - notifier.py (уведомления: INotifier, EmailNotifierFactory, PushNotifierFactory)
Декоратор - filter.py (фильтры каталога: GenreFilterDecorator, RatingFilterDecorator, YearFilterDecorator)
Стратегии - strategirs.py (стратегия оплаты PaymentStrategy и стратегия сортировки SortingStrategy)