"""
Modèles pour les actualités THEBOT
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text

from .base import BaseModel


class NewsArticle(BaseModel):
    """
    Articles d'actualité et informations financières.
    """
    __tablename__ = "news_articles"

    title = Column(String(500), nullable=False, index=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    url = Column(String(1000), nullable=False, unique=True)

    # Source et provenance
    source = Column(String(100), nullable=False, index=True)  # RSS feed name, API provider
    provider = Column(String(50), nullable=False)  # rss, crypto_panic, news_api, etc.
    author = Column(String(200), nullable=True)

    # Classification
    category = Column(String(50), nullable=True)  # crypto, stocks, forex, economy, etc.
    tags = Column(String(500), nullable=True)  # Mots-clés séparés par des virgules

    # Symboles mentionnés
    symbols = Column(String(500), nullable=True)  # BTC,ETH,AAPL,GOOGL séparés par des virgules

    # Métadonnées temporelles
    published_at = Column(DateTime, nullable=False, index=True)
    crawled_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # État et qualité
    is_processed = Column(Integer, default=0, nullable=False)  # 0=non traité, 1=traité
    sentiment_score = Column(Integer, nullable=True)  # -1=négatif, 0=neutre, 1=positif
    relevance_score = Column(Integer, default=0)  # Score de pertinence (0-100)

    # Contenu enrichi
    image_url = Column(String(1000), nullable=True)
    language = Column(String(10), default="en", nullable=False)

    def __repr__(self) -> str:
        return f"<NewsArticle(title='{self.title[:50]}...', source='{self.source}')>"

    @property
    def symbols_list(self) -> list:
        """Retourne la liste des symboles sous forme de liste"""
        if not self.symbols:
            return []
        return [s.strip() for s in self.symbols.split(',') if s.strip()]

    @symbols_list.setter
    def symbols_list(self, symbols: list) -> None:
        """Définit les symboles à partir d'une liste"""
        self.symbols = ','.join(symbols) if symbols else None

    @property
    def tags_list(self) -> list:
        """Retourne la liste des tags sous forme de liste"""
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    @tags_list.setter
    def tags_list(self, tags: list) -> None:
        """Définit les tags à partir d'une liste"""
        self.tags = ','.join(tags) if tags else None

    @property
    def age_hours(self) -> float:
        """Retourne l'âge de l'article en heures"""
        if not self.published_at:
            return 0.0
        delta = datetime.utcnow() - self.published_at
        return delta.total_seconds() / 3600

    @classmethod
    def from_rss_item(cls, rss_item: dict, source: str, provider: str = "rss") -> 'NewsArticle':
        """
        Crée un article à partir d'un item RSS.

        Args:
            rss_item: Dictionnaire contenant les données RSS
            source: Nom de la source RSS
            provider: Nom du provider (défaut: rss)

        Returns:
            Instance de NewsArticle
        """
        return cls(
            title=rss_item.get('title', ''),
            summary=rss_item.get('summary', ''),
            content=rss_item.get('content', ''),
            url=rss_item.get('link', ''),
            source=source,
            provider=provider,
            author=rss_item.get('author'),
            published_at=rss_item.get('published_parsed'),
            tags=rss_item.get('tags'),
            category=rss_item.get('category')
        )
