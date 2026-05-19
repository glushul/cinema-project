from fastapi import APIRouter

from services.processes import (
    ActivateSubscriptionCommand,
    BasicRecommendationTemplate,
    ConsoleObserver,
    NotificationObserver,
    OldPaymentSystem,
    PaymentAdapter,
    PremiumRecommendationTemplate,
    SubscriptionSubject,
)

router = APIRouter(
    prefix="/processes",
    tags=["Processes"]
)

subject = SubscriptionSubject()

#подключение наблюдателей, п3
subject.attach(ConsoleObserver())
subject.attach(NotificationObserver())

adapter = PaymentAdapter(OldPaymentSystem())


@router.post("/activate/{user_id}")
def activate_subscription(user_id: int, amount: float = 599):

    command = ActivateSubscriptionCommand(
        user_id=user_id,
        amount=amount,
        adapter=adapter,
        subject=subject
    )

    return command.execute()


@router.get("/recommendations/basic/{user_id}")
def basic_recommendations(user_id: int):

    template = BasicRecommendationTemplate()
    #использование, п5
    return template.generate(user_id)


@router.get("/recommendations/premium/{user_id}")
def premium_recommendations(user_id: int):

    template = PremiumRecommendationTemplate()

    return template.generate(user_id)