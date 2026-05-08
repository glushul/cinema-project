from fastapi import APIRouter
from database import db_manager
from models import (
    PLAN_CONFIG, User, Content, Genre, Review, 
    UserSubscription, 
    PaymentHistory, WatchHistory, Collection,
    UserRole, ContentType, PaymentMethod, PaymentStatus
)
from datetime import datetime, timedelta

router = APIRouter(prefix="/seed", tags=["Заполнение БД"])

@router.get("/")
def seed_database():
    """Заполняет базу данных тестовыми данными (20+ записей)"""
    db = db_manager.get_session()
    
    genres_data = ["Фантастика", "Боевик", "Драма", "Комедия", "Ужасы"]
    genres = []
    for g_name in genres_data:
        genre = Genre(name=g_name)
        genres.append(genre)
    db.add_all(genres)
    db.commit()
    for g in genres:
        db.refresh(g)

    users_data = [
        {"name": "Алексей Админов", "email": "admin@cinema.ru", "role": UserRole.ADMIN},
        {"name": "Иван Петров", "email": "ivan@uni.ru", "role": UserRole.USER},
        {"name": "Мария Сидорова", "email": "maria@cinema.ru", "role": UserRole.USER},
        {"name": "Дмитрий Кинокритик", "email": "critic@cinema.ru", "role": UserRole.USER},
        {"name": "Анна Смирнова", "email": "anna@cinema.ru", "role": UserRole.USER},
    ]
    users = []
    for i, u_data in enumerate(users_data):
        user = User(
            name=u_data["name"], 
            email=u_data["email"], 
            password_hash=f"hash{i+1}", 
            role=u_data["role"]
        )
        users.append(user)
    db.add_all(users)
    db.commit()
    for u in users:
        db.refresh(u)

    contents_data = [
        {"title": "Дюна: Часть вторая", "desc": "Эпическое продолжение саги о Поло Атрейдесе", "year": 2024, "dur": 166, "rating": 8.8, "type": ContentType.FILM, "views": 50000, "genres": [0, 1]},
        {"title": "Во все тяжкие", "desc": "Учитель химии становится наркобароном", "year": 2008, "dur": 45, "rating": 9.5, "type": ContentType.SERIES, "views": 120000, "genres": [2]},
        {"title": "Аватар", "desc": "Приключения на планете Пандора", "year": 2009, "dur": 162, "rating": 7.8, "type": ContentType.FILM, "views": 300000, "genres": [0, 1]},
        {"title": "Офис", "desc": "Псевдодокументальный сериал о жизни офиса", "year": 2005, "dur": 22, "rating": 9.0, "type": ContentType.SERIES, "views": 200000, "genres": [3]},
        {"title": "Начало", "desc": "Кража секретов через сны", "year": 2010, "dur": 148, "rating": 8.8, "type": ContentType.FILM, "views": 180000, "genres": [0, 1]},
        {"title": "Очень странные дела", "desc": "Дети против монстров из параллельного мира", "year": 2016, "dur": 50, "rating": 8.7, "type": ContentType.SERIES, "views": 250000, "genres": [0, 4]},
        {"title": "Крёстный отец", "desc": "Классика о мафиозной семье Корлеоне", "year": 1972, "dur": 175, "rating": 9.2, "type": ContentType.FILM, "views": 150000, "genres": [2]},
        {"title": "Унесённые призраками", "desc": "Шедевр аниме от Хаяо Миядзаки", "year": 2001, "dur": 125, "rating": 8.6, "type": ContentType.ANIME, "views": 130000, "genres": [0, 3]},
        {"title": "Тёмный рыцарь", "desc": "Бэтмен против Джокера", "year": 2008, "dur": 152, "rating": 9.0, "type": ContentType.FILM, "views": 220000, "genres": [0, 1]},
        {"title": "Рик и Морти", "desc": "Приключения учёного и его внука", "year": 2013, "dur": 23, "rating": 9.1, "type": ContentType.CARTOON, "views": 190000, "genres": [0, 3]},
    ]
    
    contents = []
    for c_data in contents_data:
        content = Content(
            title=c_data["title"],
            description=c_data["desc"],
            release_year=c_data["year"],
            duration=c_data["dur"],
            rating=c_data["rating"],
            type=c_data["type"],
            views_count=c_data["views"]
        )
        # Привязываем жанры
        for g_idx in c_data["genres"]:
            content.genres.append(genres[g_idx])
        contents.append(content)
    
    db.add_all(contents)
    db.commit()
    for c in contents:
        db.refresh(c)

    reviews_data = [
        {"user_idx": 1, "content_idx": 0, "text": "Невероятная визуальная составляющая!", "rating": 10},
        {"user_idx": 2, "content_idx": 0, "text": "Лучшее продолжение, которое я видел", "rating": 9},
        {"user_idx": 1, "content_idx": 1, "text": "Шедевр телевидения, все 5 сезонов идеальны", "rating": 10},
        {"user_idx": 3, "content_idx": 4, "text": "Нолан снова удивил, фильм заставляет думать", "rating": 9},
        {"user_idx": 2, "content_idx": 5, "text": "Ностальгия и страх в одном флаконе", "rating": 8},
        {"user_idx": 4, "content_idx": 6, "text": "Классика кинематографа, обязательно к просмотру", "rating": 10},
        {"user_idx": 1, "content_idx": 8, "text": "Хит Леджер легенда, лучший Джокер", "rating": 10},
        {"user_idx": 3, "content_idx": 9, "text": "Остроумно, умно и очень смешно", "rating": 9},
    ]
    
    reviews = []
    for r_data in reviews_data:
        review = Review(
            text=r_data["text"],
            rating=r_data["rating"],
            user_id=users[r_data["user_idx"]].id,
            content_id=contents[r_data["content_idx"]].id
        )
        reviews.append(review)
    
    db.add_all(reviews)
    db.commit()

    watch_history_data = [
        {"user_idx": 1, "content_idx": 0, "progress": 100},
        {"user_idx": 1, "content_idx": 4, "progress": 100},
        {"user_idx": 1, "content_idx": 8, "progress": 100},
        {"user_idx": 2, "content_idx": 1, "progress": 85},
        {"user_idx": 2, "content_idx": 3, "progress": 60},
        {"user_idx": 3, "content_idx": 5, "progress": 100},
        {"user_idx": 3, "content_idx": 7, "progress": 100},
        {"user_idx": 4, "content_idx": 6, "progress": 100},
        {"user_idx": 4, "content_idx": 2, "progress": 45},
        {"user_idx": 1, "content_idx": 9, "progress": 30},
    ]
    
    watch_histories = []
    for wh_data in watch_history_data:
        wh = WatchHistory(
            user_id=users[wh_data["user_idx"]].id,
            content_id=contents[wh_data["content_idx"]].id,
            progress=wh_data["progress"]
        )
        watch_histories.append(wh)
    
    db.add_all(watch_histories)
    db.commit()

    collections_data = [
        {"user_idx": 1, "name": "Избранное", "desc": "Лучшие фильмы всех времён", "personal": 1},
        {"user_idx": 2, "name": "Посмотреть позже", "desc": "Список на выходные", "personal": 1},
        {"user_idx": 3, "name": "Научная фантастика", "desc": "Вся фантастика в одном месте", "personal": 0},
    ]
    
    collections = []
    for c_data in collections_data:
        collection = Collection(
            user_id=users[c_data["user_idx"]].id,
            name=c_data["name"],
            description=c_data["desc"],
            is_personal=c_data["personal"]
        )
        collections.append(collection)
    
    db.add_all(collections)
    db.commit()
    for c in collections:
        db.refresh(c)

    collections[0].contents.append(contents[0])  # Дюна 2
    collections[0].contents.append(contents[8])  # Тёмный рыцарь
    collections[1].contents.append(contents[1])  # Во все тяжкие
    collections[2].contents.append(contents[0])  # Дюна 2
    collections[2].contents.append(contents[2])  # Аватар
    collections[2].contents.append(contents[5])  # Очень странные дела
    
    db.commit()

    total_records = (
        len(genres) +           # 5
        len(users) +            # 5
        len(contents) +         # 10
        len(reviews) +          # 8
        len(watch_histories) +  # 10
        len(collections)        # 3
    )
    
    return {
        "status": "success", 
        "message": f"База данных заполнена: {total_records} записей!",
        "details": {
            "жанры": len(genres),
            "пользователи": len(users),
            "контент": len(contents),
            "отзывы": len(reviews),
            "история_просмотров": len(watch_histories),
            "коллекции": len(collections)
        }
    }
