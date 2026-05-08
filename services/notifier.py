from abc import ABC, abstractmethod


class INotifier(ABC):
    @abstractmethod
    def send(self, user_id: int, message: str): pass

class EmailNotifier(INotifier):
    def send(self, user_id: int, message: str):
        print(f"📧 [Email] User {user_id}: {message}")

class PushNotifier(INotifier):
    def send(self, user_id: int, message: str):
        print(f"📱 [Push] User {user_id}: {message}")

class NotifierFactory(ABC):
    @abstractmethod
    def create(self) -> INotifier: pass

class EmailNotifierFactory(NotifierFactory):
    def create(self) -> INotifier: return EmailNotifier()

class PushNotifierFactory(NotifierFactory):
    def create(self) -> INotifier: return PushNotifier()