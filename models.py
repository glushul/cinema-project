from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Table
from sqlalchemy.orm import relationship
from database import Base
import enum
from datetime import datetime


class ContentType(enum.Enum):
    FILM = "film"
    SERIES = "series"
    CARTOON = "cartoon"
    ANIME = "anime"

class PaymentMethod(enum.Enum):
    CARD = "card"
    SBP = "sbp"

class PaymentStatus(enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"

class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"
    
PLAN_CONFIG = {
    "BASE": {"price": 299.0, "days": 30},
    "PREMIUM": {"price": 599.0, "days": 30},
}

# ASSOCIATION TABLES (Связи Many-to-Many)

# Связь Фильм <-> Жанр
content_genre_table = Table(
    'content_genre', Base.metadata,
    Column('content_id', Integer, ForeignKey('contents.id'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id'), primary_key=True)
)

# Связь Коллекция <-> Контент 
collection_content_table = Table(
    'collection_content', Base.metadata,
    Column('collection_id', Integer, ForeignKey('collections.id'), primary_key=True),
    Column('content_id', Integer, ForeignKey('contents.id'), primary_key=True)
)

# MAIN MODELS

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    role = Column(Enum(UserRole), default=UserRole.USER)

    # Связи
    reviews = relationship("Review", back_populates="user")
    watch_history = relationship("WatchHistory", back_populates="user")
    payments = relationship("PaymentHistory", back_populates="user")
    subscriptions = relationship("UserSubscription", back_populates="user")

class Genre(Base):
    __tablename__ = "genres"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

class Content(Base):
    __tablename__ = "contents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String) 
    release_year = Column(Integer)
    duration = Column(Integer)
    rating = Column(Float, default=0.0)
    type = Column(Enum(ContentType), default=ContentType.FILM)
    views_count = Column(Integer, default=0) 
    video_url = Column(String) 

    genres = relationship("Genre", secondary=content_genre_table, backref="contents")
    reviews = relationship("Review", back_populates="content")
    watch_history = relationship("WatchHistory", back_populates="content")

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    rating = Column(Integer) # 1-10
    date = Column(DateTime, default=datetime.utcnow)
    
    user_id = Column(Integer, ForeignKey('users.id'))
    content_id = Column(Integer, ForeignKey('contents.id'))
    
    user = relationship("User", back_populates="reviews")
    content = relationship("Content", back_populates="reviews")


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    plan = Column(String, default="BASE")  
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    is_active = Column(Integer, default=1) # 1 = True, 0 = False

    user = relationship("User", back_populates="subscriptions")
    payments = relationship("PaymentHistory", back_populates="subscription", cascade="all, delete-orphan")

    @property
    def price(self) -> float:
        return PLAN_CONFIG.get(self.plan, {}).get("price", 0.0)
        
    @property
    def duration_days(self) -> int:
        return PLAN_CONFIG.get(self.plan, {}).get("days", 30)

class PaymentHistory(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    subscription_id = Column(Integer, ForeignKey('user_subscriptions.id'))
    amount = Column(Float)
    payment_date = Column(DateTime, default=datetime.utcnow)
    method = Column(Enum(PaymentMethod), default=PaymentMethod.CARD)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)

    user = relationship("User", back_populates="payments")
    subscription = relationship("UserSubscription", back_populates="payments")

class WatchHistory(Base):
    __tablename__ = "watch_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    content_id = Column(Integer, ForeignKey('contents.id'))
    watch_date = Column(DateTime, default=datetime.utcnow)
    progress = Column(Integer, default=0) # 0-100%

    user = relationship("User", back_populates="watch_history")
    content = relationship("Content", back_populates="watch_history")

class Collection(Base):
    __tablename__ = "collections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String, nullable=False)
    description = Column(String)
    is_personal = Column(Integer, default=1)

    contents = relationship("Content", secondary=collection_content_table, backref="collections")
