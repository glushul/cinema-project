from services.observer import (
    TicketPurchaseSubject,
    EmailNotificationObserver,
    PurchaseHistoryObserver,
    SalesStatsObserver,
)
from services.strategies import PaymentContext, CardPaymentStrategy, SBPPaymentStrategy
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/tickets", tags=["tickets"])

TICKET_PRICE = 350.0

ticket_subject = TicketPurchaseSubject()
ticket_subject.attach(EmailNotificationObserver())
ticket_subject.attach(PurchaseHistoryObserver())
ticket_subject.attach(SalesStatsObserver())

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

@router.post("/buy")
def buy_ticket(data: TicketRequest):
    if data.quantity < 1 or data.quantity > 10:
        raise HTTPException(400, detail="Количество билетов: от 1 до 10")

    payment_strategy = PAYMENT_STRATEGIES.get(data.payment_method)
    if not payment_strategy:
        raise HTTPException(400, detail=f"Неизвестный способ оплаты: {data.payment_method}")

    amount = TICKET_PRICE * data.quantity

    payment_ctx = PaymentContext(payment_strategy)
    paid = payment_ctx.execute(amount)
    if not paid:
        raise HTTPException(402, detail="Оплата не прошла")

    # Наблюдатель: оповещаем всех после успешной оплаты
    ticket_subject.complete_purchase({
        "user_id": data.user_id,
        "movie_id": data.movie_id,
        "movie_title": data.movie_title,
        "quantity": data.quantity,
        "total": amount,
        "payment_method": data.payment_method,
    })

    return {
        "status": "success",
        "quantity": data.quantity,
        "total": amount,
        "message": f"Куплено {data.quantity} билет(ов) на сумму {amount:.0f} ₽"
    }