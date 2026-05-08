from datetime import datetime

from fastapi import APIRouter, Query
from database import db_manager
from models import Content
from services.recommendation import RecommendationEngine
from services.strategies import SortingContext, ByRatingStrategy, ByYearStrategy
from services.filter import (
    NoFilter, 
    GenreFilterDecorator, 
    RatingFilterDecorator, 
    YearFilterDecorator
)


router = APIRouter(prefix="/catalog", tags=["Каталог и Подписки"])

@router.get("/")
def browse_catalog(sort_by: str = Query("rating", enum=["rating", "year"])):    
    """Фильтрация/Сортировка контента (Strategy) + Мат. модель"""
    db = db_manager.get_session()
    contents = db.query(Content).all()
    
    engine = RecommendationEngine()
    ranked = engine.get_ranked(contents)

    strategy = ByRatingStrategy() if sort_by == "rating" else ByYearStrategy()
    context = SortingContext(strategy)
    sorted_contents = context.apply(ranked)
    
    return [{"title": c.title, "year": c.release_year} for c in sorted_contents]

@router.get("/filtered")
def get_filtered_catalog(
    genre: str = Query(None, description="Жанр (например: Фантастика)"),
    min_rating: float = Query(None, description="Минимальный рейтинг"),
    min_year: int = Query(None, description="Фильмы не старше этого года")
):
    """
    Демонстрация Декоратора: Динамическая фильтрация каталога.
    Мы 'надеваем' фильтры друг на друга в зависимости от параметров запроса.
    """
    
    db = db_manager.get_session()
    all_content = db.query(Content).all()
    
    chain = NoFilter()
    
    if genre:
        chain = GenreFilterDecorator(chain, genre_name=genre)
        
    if min_rating:
        chain = RatingFilterDecorator(chain, min_rating=min_rating)
        
    if min_year:
        chain = YearFilterDecorator(chain, min_year=min_year)
        
    result = chain.apply(all_content)
    
    return {"count": len(result), "movies": [c.title for c in result]}