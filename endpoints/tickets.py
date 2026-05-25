from services.observer import (
    TicketPurchaseSubject,
    EmailNotificationObserver,
    PurchaseHistoryObserver,
    SalesStatsObserver,
)
from services.strategies import PaymentContext, CardPaymentStrategy, SBPPaymentStrategy, PaymentStrategyFactory
from services.abstract_factory import CinemaFactoryRegistry
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/tickets", tags=["tickets"])

TICKET_PRICE = 350.0


PAYMENT_STRATEGIES = {
    "card": CardPaymentStrategy(),
    "sbp": SBPPaymentStrategy(),
}

class TicketRequest(BaseModel):
    movie_id: int
    movie_title: str
    user_id: int
    quantity: int
    payment_method: str
    cinema_type: str

@router.post("/buy")
def buy_ticket(data: TicketRequest):
    if data.quantity < 1 or data.quantity > 10:
        raise HTTPException(400, detail="Количество билетов: от 1 до 10")

    try:
        # Абстрактная фабрика выдаёт нужное семейство объектов
        factory = CinemaFactoryRegistry.get(data.cinema_type)
        
        # Фабричный метод создаёт нужную стратегию
        strategy = factory.create_payment_strategy(data.payment_method)

        observers = factory.create_observers()
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

    amount = TICKET_PRICE * data.quantity

    # Стратегия выполняет оплату
    payment_ctx = PaymentContext(strategy)
    paid = payment_ctx.execute(amount)
    if not paid:
        raise HTTPException(402, detail="Оплата не прошла")

    # Наблюдатель: оповещаем всех после успешной оплаты
    subject = TicketPurchaseSubject()
    for observer in observers:
        subject.attach(observer)

    subject.complete_purchase({
        "user_id": data.user_id,
        "movie_id": data.movie_id,
        "movie_title": data.movie_title,
        "quantity": data.quantity,
        "total": amount,
        "payment_method": data.payment_method,
        "cinema_type": data.cinema_type,
    })

    return {
        "status": "success",
        "quantity": data.quantity,
        "total": amount,
        "cinema_type": data.cinema_type,
        "message": f"Куплено {data.quantity} билет(ов) на сумму {amount:.0f} ₽"
    }