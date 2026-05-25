from abc import ABC, abstractmethod
from datetime import datetime

#Наблюдатель, п3
class Observer(ABC):
    @abstractmethod
    def update(self, event: str, data: dict):
        pass

#Конкретные наблюдатели
class EmailNotificationObserver(Observer):
    """Отправляет письмо с подтверждением покупки"""
    def update(self, event: str, data: dict):
        if event == "ticket_purchased":
            print(
                f"[EMAIL] Отправка на {data.get('user_email', 'user@example.com')}: "
                f"куплено {data['quantity']} билет(ов) на «{data['movie_title']}», "
                f"сумма: {data['total']} ₽"
            )

class PurchaseHistoryObserver(Observer):
    """Записывает покупку в историю пользователя"""
    def update(self, event: str, data: dict):
        if event == "ticket_purchased":
            print(
                f"[HISTORY] user_id={data['user_id']} | "
                f"movie_id={data['movie_id']} | "
                f"qty={data['quantity']} | "
                f"total={data['total']} ₽ | "
                f"at={datetime.now().isoformat()}"
            )

class SalesStatsObserver(Observer):
    """Обновляет статистику продаж"""
    def update(self, event: str, data: dict):
        if event == "ticket_purchased":
            print(
                f"[STATS] +{data['quantity']} билетов на фильм id={data['movie_id']} "
                f"(способ оплаты: {data['payment_method']})"
            )

class ConsoleObserver(Observer):
    """Для отладки — печатает любое событие"""
    def update(self, event: str, data: dict):
        print(f"[EVENT]: {event}")
        print(f"[DATA]: {data}")


class TicketPurchaseSubject:
    def __init__(self):
        self._observers: list[Observer] = []

    def attach(self, observer: Observer):
        self._observers.append(observer)

    def detach(self, observer: Observer):
        self._observers.remove(observer)

    def notify(self, event: str, data: dict):
        for observer in self._observers:
            observer.update(event, data)

    def complete_purchase(self, purchase_data: dict):
        """Вызывается после успешной оплаты"""
        self.notify("ticket_purchased", purchase_data)