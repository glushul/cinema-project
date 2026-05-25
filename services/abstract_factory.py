# services/abstract_factory.py

from abc import ABC, abstractmethod
from services.strategies import (
    PaymentStrategy,
    CardPaymentStrategy,
    SBPPaymentStrategy,
)
from services.observer import (
    Observer,
    EmailNotificationObserver,
    PurchaseHistoryObserver,
    SalesStatsObserver,
)


# --- Абстрактная фабрика ---
class TicketPurchaseFactory(ABC):
    @abstractmethod
    def create_payment_strategy(self, method: str) -> PaymentStrategy:
        pass

    @abstractmethod
    def create_observers(self) -> list[Observer]:
        pass


# Премиум кинотеатр 
class PremiumCinemaFactory(TicketPurchaseFactory):
    """
    Премиум: поддерживает карту и СБП,
    уведомляет по email + пишет историю + обновляет статистику
    """
    def create_payment_strategy(self, method: str) -> PaymentStrategy:
        strategies = {
            "card": CardPaymentStrategy(),
            "sbp": SBPPaymentStrategy(),
        }
        strategy = strategies.get(method)
        if not strategy:
            raise ValueError(f"Премиум кинотеатр не поддерживает способ оплаты: {method}")
        return strategy

    def create_observers(self) -> list[Observer]:
        return [
            EmailNotificationObserver(),
            PurchaseHistoryObserver(),
            SalesStatsObserver(),
        ]


# Стандартный кинотеатр 
class StandardCinemaFactory(TicketPurchaseFactory):
    """
    Стандарт: только карта,
    только история — без email и статистики
    """
    def create_payment_strategy(self, method: str) -> PaymentStrategy:
        if method != "card":
            raise ValueError("Стандартный кинотеатр принимает только карту")
        return CardPaymentStrategy()

    def create_observers(self) -> list[Observer]:
        return [
            PurchaseHistoryObserver(),
        ]



class CinemaFactoryRegistry:
    _factories = {
        "premium": PremiumCinemaFactory(),
        "standard": StandardCinemaFactory(),
    }

    @classmethod
    def get(cls, cinema_type: str) -> TicketPurchaseFactory:
        factory = cls._factories.get(cinema_type)
        if not factory:
            raise ValueError(f"Неизвестный тип кинотеатра: {cinema_type}")
        return factory