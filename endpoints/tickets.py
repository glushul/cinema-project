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
from database import db_manager

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

import uuid
from models import TicketPurchase, PaymentMethod

@router.post("/buy")
def buy_ticket(data: TicketRequest):
    if data.quantity < 1 or data.quantity > 10:
        raise HTTPException(400, detail="Количество билетов: от 1 до 10")

    try:
        # Абстрактная фабрика
        factory = CinemaFactoryRegistry.get(data.cinema_type)
        # Фабричный метод
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

    # сохраняем покупку в БД
    booking_code = f"TKT-{uuid.uuid4().hex[:8].upper()}"
    db = db_manager.get_session()
    ticket = TicketPurchase(
        user_id=data.user_id,
        movie_id=data.movie_id,
        quantity=data.quantity,
        amount=amount,
        payment_method=PaymentMethod(data.payment_method),
        cinema_type=data.cinema_type,
        booking_code=booking_code,
    )
    db.add(ticket)
    db.commit()

    # Наблюдатель оповещает после успешной оплаты
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
        "booking_code": booking_code,
    })

    return {
        "status": "success",
        "quantity": data.quantity,
        "total": amount,
        "booking_code": booking_code,
        "message": f"Куплено {data.quantity} билет(ов) на сумму {amount:.0f} ₽",
    }

@router.get("/history/{user_id}")
def get_ticket_history(user_id: int):
    db = db_manager.get_session()
    tickets = db.query(TicketPurchase).filter(
        TicketPurchase.user_id == user_id
    ).order_by(TicketPurchase.purchase_date.desc()).all()

    return {
        "status": "success",
        "tickets": [
            {
                "id": t.id,
                "movie_id": t.movie_id,
                "quantity": t.quantity,
                "amount": t.amount,
                "payment_method": t.payment_method.value,
                "cinema_type": t.cinema_type,
                "booking_code": t.booking_code,
                "purchase_date": t.purchase_date.isoformat(),
            }
            for t in tickets
        ]
    }