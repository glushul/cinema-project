import hashlib

from fastapi import APIRouter
from pydantic import BaseModel

from database import db_manager
from models import User, UserRole


router = APIRouter(prefix="/auth", tags=["Авторизация"])


class AuthRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(AuthRequest):
    name: str


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def serialize_user(user: User) -> dict:
    active_subscription = next(
        (subscription for subscription in user.subscriptions if subscription.is_active == 1),
        None,
    )
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.value if user.role else "user",
        "subscription": {
            "id": active_subscription.id,
            "plan": active_subscription.plan,
            "end_date": active_subscription.end_date.isoformat() if active_subscription.end_date else None,
        } if active_subscription else None,
    }


@router.post("/register")
def register(payload: RegisterRequest):
    db = db_manager.get_session()
    email = payload.email.strip().lower()
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return {"status": "failed", "message": "Пользователь с таким email уже существует"}

    user = User(
        name=payload.name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
        role=UserRole.USER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"status": "success", "user": serialize_user(user)}


@router.post("/login")
def login(payload: AuthRequest):
    db = db_manager.get_session()
    user = db.query(User).filter(User.email == payload.email.strip().lower()).first()
    if not user:
        return {"status": "failed", "message": "Пользователь не найден"}

    password_hash = hash_password(payload.password)
    if user.password_hash not in {password_hash, payload.password}:
        return {"status": "failed", "message": "Неверный пароль"}

    return {"status": "success", "user": serialize_user(user)}


@router.get("/me/{user_id}")
def get_current_user(user_id: int):
    db = db_manager.get_session()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"status": "failed", "message": "Пользователь не найден"}

    return {"status": "success", "user": serialize_user(user)}
