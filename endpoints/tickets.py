from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from strategy_service import PaymentContext, CardPaymentStrategy, SBPPaymentStrategy

router = APIRouter(prefix="/tickets", tags=["tickets"])

TICKET_PRICE = 350.0  

PAYMENT_STRATEGIES = {
    "card": CardPaymentStrategy(),
    "sbp": SBPPaymentStrategy(),
}

class TicketRequest(BaseModel):
    movie_id: int
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

    return {
        "status": "success",
        "movie_id": data.movie_id,
        "quantity": data.quantity,
        "total": amount,
        "payment_method": data.payment_method,
        "message": f"Куплено {data.quantity} билет(ов) на сумму {amount:.0f} ₽"
    }