from fastapi import APIRouter, Query
from database import db_manager
from models import PaymentHistory, PaymentStatus, PaymentMethod, PLAN_CONFIG, UserSubscription
from services.subscription import PremiumSubscriptionProcessor, BasicSubscriptionProcessor
from services.notifier import EmailNotifierFactory, PushNotifierFactory
from services.strategies import CardPaymentStrategy, SBPPaymentStrategy, PaymentContext
from datetime import datetime

router = APIRouter(prefix="/subscription", tags=["Подписки"])

@router.get("/user/{user_id}")
def get_user_subscription(user_id: int):
    db = db_manager.get_session()
    subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == user_id,
        UserSubscription.is_active == 1
    ).first()

    if not subscription:
        return {"status": "empty", "subscription": None}

    return {
        "status": "success",
        "subscription": {
            "id": subscription.id,
            "plan": subscription.plan,
            "price": subscription.price,
            "start_date": subscription.start_date.isoformat() if subscription.start_date else None,
            "end_date": subscription.end_date.isoformat() if subscription.end_date else None,
        }
    }

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
        
    return {"error": result.get("message", "Failed to activate subscription")}


@router.post("/cancel/{user_id}")
def cancel_subscription(user_id: int):
    db = db_manager.get_session()
    subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == user_id,
        UserSubscription.is_active == 1
    ).first()

    if not subscription:
        return {"status": "failed", "message": "Активная подписка не найдена"}

    subscription_id = subscription.id
    db.query(PaymentHistory).filter(
        PaymentHistory.subscription_id == subscription_id
    ).delete(synchronize_session=False)
    db.delete(subscription)
    db.commit()

    return {
        "status": "success",
        "message": "Подписка удалена",
        "deleted_subscription_id": subscription_id
    }
