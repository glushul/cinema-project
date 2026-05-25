from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from models import (
    User, Content, Genre, Review,
    UserSubscription, PaymentHistory,
    WatchHistory, Collection, TicketPurchase
)


# --- Аутентификация ---

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        if form["username"] == "admin" and form["password"] == "secret":
            request.session.update({"token": "admin"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return "token" in request.session


# --- Вьюхи ---

class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-users"
    column_list = [
        User.id,
        User.name,
        User.email,
        User.role,
        User.registration_date,
    ]
    column_searchable_list = [User.name, User.email]
    column_sortable_list = [User.registration_date, User.role]
    can_create = False
    can_delete = True
    can_edit = True


class ContentAdmin(ModelView, model=Content):
    name = "Контент"
    name_plural = "Каталог"
    icon = "fa-solid fa-film"
    column_list = [
        Content.id,
        Content.title,
        Content.type,
        Content.release_year,
        Content.rating,
        Content.views_count,
        Content.duration,
    ]
    column_searchable_list = [Content.title]
    column_sortable_list = [Content.rating, Content.release_year, Content.views_count]
    can_create = True
    can_edit = True
    can_delete = True


class GenreAdmin(ModelView, model=Genre):
    name = "Жанр"
    name_plural = "Жанры"
    icon = "fa-solid fa-tag"
    column_list = [Genre.id, Genre.name]
    column_searchable_list = [Genre.name]
    can_create = True
    can_edit = True
    can_delete = True


class ReviewAdmin(ModelView, model=Review):
    name = "Отзыв"
    name_plural = "Отзывы"
    icon = "fa-solid fa-star"
    column_list = [
        Review.id,
        Review.user_id,
        Review.content_id,
        Review.rating,
        Review.date,
    ]
    column_sortable_list = [Review.date, Review.rating]
    can_create = False
    can_edit = False
    can_delete = True  # модерация


class UserSubscriptionAdmin(ModelView, model=UserSubscription):
    name = "Подписка"
    name_plural = "Подписки"
    icon = "fa-solid fa-credit-card"
    column_list = [
        UserSubscription.id,
        UserSubscription.user_id,
        UserSubscription.plan,
        UserSubscription.is_active,
        UserSubscription.start_date,
        UserSubscription.end_date,
    ]
    column_searchable_list = [UserSubscription.user_id]
    column_sortable_list = [UserSubscription.start_date, UserSubscription.plan]
    can_create = False
    can_edit = True
    can_delete = True


class PaymentHistoryAdmin(ModelView, model=PaymentHistory):
    name = "Платёж"
    name_plural = "История платежей"
    icon = "fa-solid fa-receipt"
    column_list = [
        PaymentHistory.id,
        PaymentHistory.user_id,
        PaymentHistory.subscription_id,
        PaymentHistory.amount,
        PaymentHistory.method,
        PaymentHistory.status,
        PaymentHistory.payment_date,
    ]
    column_sortable_list = [PaymentHistory.payment_date, PaymentHistory.amount]
    can_create = False
    can_edit = False  
    can_delete = False


class WatchHistoryAdmin(ModelView, model=WatchHistory):
    name = "Просмотр"
    name_plural = "История просмотров"
    icon = "fa-solid fa-clock-rotate-left"
    column_list = [
        WatchHistory.id,
        WatchHistory.user_id,
        WatchHistory.content_id,
        WatchHistory.progress,
        WatchHistory.watch_date,
    ]
    column_sortable_list = [WatchHistory.watch_date, WatchHistory.progress]
    can_create = False
    can_edit = False
    can_delete = True


class CollectionAdmin(ModelView, model=Collection):
    name = "Коллекция"
    name_plural = "Коллекции"
    icon = "fa-solid fa-folder"
    column_list = [
        Collection.id,
        Collection.user_id,
        Collection.name,
        Collection.is_personal,
    ]
    column_searchable_list = [Collection.name]
    can_create = False
    can_edit = True
    can_delete = True

class TicketPurchaseAdmin(ModelView, model=TicketPurchase):
    name = "Билет"
    name_plural = "Купленные билеты"
    icon = "fa-solid fa-ticket"
    column_list = [
        TicketPurchase.id,
        TicketPurchase.user_id,
        TicketPurchase.movie_id,
        TicketPurchase.quantity,
        TicketPurchase.amount,
        TicketPurchase.payment_method,
        TicketPurchase.cinema_type,
        TicketPurchase.booking_code,
        TicketPurchase.purchase_date,
    ]
    column_sortable_list = [TicketPurchase.purchase_date, TicketPurchase.amount]
    can_create = False
    can_edit = False
    can_delete = False

# --- Фабричная функция ---

def create_admin(app, engine) -> Admin:
    admin = Admin(app, engine, title="Кинотеатр")

    admin.add_view(UserAdmin)
    admin.add_view(ContentAdmin)
    admin.add_view(GenreAdmin)
    admin.add_view(ReviewAdmin)
    admin.add_view(UserSubscriptionAdmin)
    admin.add_view(PaymentHistoryAdmin)
    admin.add_view(WatchHistoryAdmin)
    admin.add_view(CollectionAdmin)
    admin.add_view(TicketPurchaseAdmin)

    return admin
