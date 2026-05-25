from abc import ABC, abstractmethod
from enum import Enum


#Наблюдатель, п3
class Observer(ABC):
    @abstractmethod
    def update(self, event: str, data: dict):
        pass

#Конкретные наблюдатели
class ConsoleObserver(Observer):
    def update(self, event: str, data: dict):
        print(f"[EVENT]: {event}")
        print(f"[DATA]: {data}")


class NotificationObserver(Observer):
    def update(self, event: str, data: dict):
        print(f"Уведомление отправлено: {event}")

#За ним наблюдают
class SubscriptionSubject:
    def __init__(self):
        self.observers = []

    def attach(self, observer: Observer):
        self.observers.append(observer)

    def notify(self, event: str, data: dict):
        for observer in self.observers:
            observer.update(event, data)


# Старая платежная система, п2
class OldPaymentSystem:
    def make_payment(self, value: int):
        return {
            "status": "success",
            "payment_id": f"OLD-{value}"
        }

# # Адаптер платежной системы, п2
class PaymentAdapter:
    def __init__(self, old_system: OldPaymentSystem):
        self.old_system = old_system

    def pay(self, amount: float):
        result = self.old_system.make_payment(int(amount))

        return {
            "success": result["status"] == "success",
            "transaction": result["payment_id"]
        }


class SubscriptionState(Enum):
    CREATED = "created"
    VALIDATED = "validated"
    PAID = "paid"
    ACTIVE = "active"
    FAILED = "failed"


class SubscriptionStateMachine:
    def __init__(self):
        self.state = SubscriptionState.CREATED

    def validate(self):
        self.state = SubscriptionState.VALIDATED

    def pay(self, success=True):
        if success:
            self.state = SubscriptionState.PAID
        else:
            self.state = SubscriptionState.FAILED

    def activate(self):
        if self.state == SubscriptionState.PAID:
            self.state = SubscriptionState.ACTIVE


class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

#Интерфейс команды, п4
class ActivateSubscriptionCommand(Command):
    def __init__(
        self,
        user_id: int,
        amount: float,
        adapter: PaymentAdapter,
        subject: SubscriptionSubject
    ):
        self.user_id = user_id
        self.amount = amount
        self.adapter = adapter
        self.subject = subject
    #выполнение команды, п4
    def execute(self):
        machine = SubscriptionStateMachine()
        #тут уведомления, п3
        self.subject.notify(
            "subscription_created",
            {
                "user_id": self.user_id,
                "state": machine.state.value
            }
        )

        machine.validate()
        #использование адаптера из пункта 2
        payment_result = self.adapter.pay(self.amount)

        if payment_result["success"]:
            machine.pay(True)
            machine.activate()

            self.subject.notify(
                "subscription_activated",
                {
                    "user_id": self.user_id,
                    "state": machine.state.value,
                    "transaction": payment_result["transaction"]
                }
            )

            return {
                "message": "Подписка активирована",
                "state": machine.state.value,
                "transaction": payment_result["transaction"]
            }

        machine.pay(False)

        self.subject.notify(
            "subscription_failed",
            {
                "user_id": self.user_id
            }
        )

        return {
            "message": "Ошибка оплаты",
            "state": machine.state.value
        }
# Базовый шаблон, п5
class BaseRecommendationTemplate(ABC):
    #шаблонный метод, п5
    def generate(self, user_id: int):
        data = self.get_data(user_id)
        prepared = self.prepare(data)
        return self.build_response(prepared)

    def prepare(self, data):
        return data

    @abstractmethod
    def get_data(self, user_id: int):
        pass

    @abstractmethod
    def build_response(self, data):
        pass


class BasicRecommendationTemplate(BaseRecommendationTemplate):

    def get_data(self, user_id: int):
        return {
            "user_id": user_id,
            "recommendations": [
                "Интерстеллар",
                "Начало"
            ]
        }

    def build_response(self, data):
        return {
            "type": "basic",
            "data": data
        }


class PremiumRecommendationTemplate(BaseRecommendationTemplate):

    def get_data(self, user_id: int):
        return {
            "user_id": user_id,
            "recommendations": [
                "Дюна",
                "Бегущий по лезвию 2049",
                "Матрица"
            ]
        }

    def build_response(self, data):
        return {
            "type": "premium",
            "data": data,
            "extra": "AI recommendations enabled"
        }