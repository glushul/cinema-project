from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from database import db_manager
from models import User, UserSubscription, PaymentHistory, PaymentStatus, PaymentMethod

class BaseSubscriptionProcessor(ABC):
    """Абстрактный класс с фиксированным алгоритмом (Шаблонный метод)"""
    
    def process_subscription(self, user_id: int, plan: str, amount: float, duration_days: int, payment_method: str) -> dict:
        # 0. ПРОВЕРКА: Это активный пользователь?
        if self._is_active_user(user_id):
            return {"status": "failed", "message": "Такого пользователя не существует"}
        
        # 1. ПРОВЕРКА: Уже есть активная подписка?
        if self._has_active_subscription(user_id):
            return {"status": "failed", "message": "У пользователя уже есть активная подписка"}

        # 2. Проверка платежа
        if not self._verify_payment(amount):
            return {"status": "failed", "message": "Ошибка оплаты"}

        # 3. Активация подписки
        sub_id = self._activate_plan(user_id, plan, duration_days)

        # 4. Сохранение записи об оплате в БД
        self._save_payment_record(user_id, sub_id, amount, payment_method)

        # 5. Отправка подтверждения
        self._send_confirmation(user_id)
        
        return {"status": "success", "subscription_id": sub_id}

    @abstractmethod
    def _verify_payment(self, amount: float) -> bool: pass

    def _is_active_user(self, user_id: int) -> bool:
        """Проверяет, есть ли у пользователя активная подписка"""
        db = db_manager.get_session()
        active_us = db.query(User).filter(
            User.id == user_id
        ).first()
        return active_us is None
    
    def _has_active_subscription(self, user_id: int) -> bool:
        """Проверяет, есть ли у пользователя активная подписка"""
        db = db_manager.get_session()
        active_sub = db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.is_active == 1
        ).first()
        return active_sub is not None

    def _activate_plan(self, user_id: int, plan: str, duration_days: int) -> int:
        db = db_manager.get_session()
        sub = UserSubscription(
            user_id=user_id,
            plan=plan,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=duration_days),
            is_active=1
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        return sub.id

    def _save_payment_record(self, user_id: int, subscription_id: int, amount: float, method: str):
        db = db_manager.get_session()
        method_enum = PaymentMethod.CARD if method == "card" else PaymentMethod.SBP
        payment = PaymentHistory(
            user_id=user_id,
            subscription_id=subscription_id,
            amount=amount,
            payment_date=datetime.utcnow(),
            method=method_enum,
            status=PaymentStatus.SUCCESS
        )
        db.add(payment)
        db.commit()

    def _send_confirmation(self, user_id: int):
        print(f" Уведомление отправлено пользователю #{user_id}")


class BasicSubscriptionProcessor(BaseSubscriptionProcessor):
    def _verify_payment(self, amount: float) -> bool:
        if amount < 299.0: return False
        print(f"[Base] Оплата {amount}₽ принята")
        return True

class PremiumSubscriptionProcessor(BaseSubscriptionProcessor):
    def _verify_payment(self, amount: float) -> bool:
        if amount < 599.0: return False
        print(f"[Premium] Оплата {amount}₽ принята")
        return True