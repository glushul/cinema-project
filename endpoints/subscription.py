from fastapi import APIRouter, Query
from database import db_manager
from models import PaymentHistory, PaymentStatus, PaymentMethod, PLAN_CONFIG
from services.subscription import PremiumSubscriptionProcessor, BasicSubscriptionProcessor
from services.notifier import EmailNotifierFactory, PushNotifierFactory
from services.strategies import CardPaymentStrategy, SBPPaymentStrategy, PaymentContext
from datetime import datetime

router = APIRouter(prefix="/subscription", tags=["Подписки"])

@router.post("/activate/{user_id}")
def subscribe(
    user_id: int, 
    plan: str = Query("PREMIUM", enum=["BASE", "PREMIUM"], description="Тип тарифа"),
    payment_method: str = Query("card", enum=["card", "sbp"])
):
    """Оформление подписки (Template Method + Strategy + Factory + DB)"""

    if plan not in PLAN_CONFIG:
        return {"error": f"Тариф '{plan}' не найден в системе"}
        
    config = PLAN_CONFIG[plan]
    amount = config["price"]
    duration_days = config["days"]

    pay_strategy = CardPaymentStrategy() if payment_method == "card" else SBPPaymentStrategy()
    pay_ctx = PaymentContext(pay_strategy)
    
    if not pay_ctx.execute(amount):
        return {"error": "Payment failed"}
        
    processor = PremiumSubscriptionProcessor() if plan == "PREMIUM" else BasicSubscriptionProcessor()
    result = processor.process_subscription(
        user_id=user_id, 
        plan=plan, 
        amount=amount, 
        duration_days=duration_days,
        payment_method=payment_method
    )
    
    if result.get("status") == "success":
        
        notifier_factory = EmailNotifierFactory() if plan == "PREMIUM" else PushNotifierFactory()
        notifier = notifier_factory.create()
        notifier.send(user_id, f"Подписка {plan} активирована!")
        
        return {
            "message": "Подписка успешно оформлена и оплачена",
            "plan": plan,
            "amount": amount,
            "subscription_id": result["subscription_id"]
        }
        
    return {"error": "Failed to activate subscription"}