from abc import ABC, abstractmethod

from models import Content


class IFilter(ABC):
    @abstractmethod
    def apply(self, data: list[Content]) -> list[Content]:
        """Применяет условие к списку фильмов"""
        pass

class NoFilter(IFilter):
    def apply(self, data: list[Content]) -> list[Content]:
        return data

class FilterDecorator(IFilter):
    def __init__(self, wrapped: IFilter):
        self._wrapped = wrapped

    def apply(self, data: list[Content]) -> list[Content]:
        return self._wrapped.apply(data)

class GenreFilterDecorator(FilterDecorator):
    def __init__(self, wrapped: IFilter, genre_name: str):
        super().__init__(wrapped)
        self.genre_name = genre_name

    def apply(self, data: list[Content]) -> list[Content]:
        previous_result = super().apply(data)
        
        return [
            c for c in previous_result 
            if any(g.name == self.genre_name for g in c.genres)
        ]

class RatingFilterDecorator(FilterDecorator):
    def __init__(self, wrapped: IFilter, min_rating: float):
        super().__init__(wrapped)
        self.min_rating = min_rating

    def apply(self, data: list[Content]) -> list[Content]:
        previous_result = super().apply(data)
        return [c for c in previous_result if c.rating >= self.min_rating]

class YearFilterDecorator(FilterDecorator):
    def __init__(self, wrapped: IFilter, min_year: int):
        super().__init__(wrapped)
        self.min_year = min_year

    def apply(self, data: list[Content]) -> list[Content]:
        previous_result = super().apply(data)
        return [c for c in previous_result if (c.release_year and c.release_year >= self.min_year)]