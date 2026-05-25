__package__ = "strategies"

from abc import ABC, abstractmethod
from models import Content

# Стратегии сортировки каталога
class SortingStrategy(ABC):
    @abstractmethod
    def sort(self, items: list[Content]) -> list[Content]: pass

class ByRatingStrategy(SortingStrategy):
    def sort(self, items: list[Content]) -> list[Content]:
        return sorted(items, key=lambda x: x.rating or 0, reverse=True)

class ByYearStrategy(SortingStrategy):
    def sort(self, items: list[Content]) -> list[Content]:
        return sorted(items, key=lambda x: x.release_year or 0, reverse=True)

class SortingContext:
    def __init__(self, strategy: SortingStrategy):
        self._strategy = strategy
    def apply(self, items: list[Content]) -> list[Content]:
        return self._strategy.sort(items)


# Стратегии оплаты
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> bool: pass

class CardPaymentStrategy(PaymentStrategy):
    def pay(self, amount: float) -> bool:
        print(f"Оплата картой: {amount}₽")
        return True

class SBPPaymentStrategy(PaymentStrategy):
    def pay(self, amount: float) -> bool:
        print(f"Оплата через СБП: {amount}₽")
        return True

class PaymentContext:
    def __init__(self, strategy: PaymentStrategy):
        self._strategy = strategy
    def execute(self, amount: float) -> bool:
        return self._strategy.pay(amount)
    
class PaymentStrategyFactory:
    @staticmethod
    def create(payment_method: str) -> PaymentStrategy:
        strategies = {
            "card": CardPaymentStrategy(),
            "sbp": SBPPaymentStrategy(),
        }
        strategy = strategies.get(payment_method)
        if not strategy:
            raise ValueError(f"Неизвестный способ оплаты: {payment_method}")
        return strategy    
