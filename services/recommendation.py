import math
from models import Content

class RecommendationEngine:
    """Математическая модель ранжирования контента"""
    def calculate_score(self, content: Content) -> float:
        r = content.rating / 10.0 if content.rating else 0
        p = math.log(content.views_count + 1) / 5.0
        age = 2026 - content.release_year if content.release_year else 50
        n = max(0, (10 - age)) / 10.0
        return round((0.4 * r) + (0.4 * p) + (0.2 * n), 2)
    
    def get_ranked(self, items: list[Content]) -> list[tuple[Content, float]]:
        scored = [(c, self.calculate_score(c)) for c in items]
        sorted_scored = sorted(scored, key=lambda x: x[1], reverse=True)
        return [content for content, score in sorted_scored]