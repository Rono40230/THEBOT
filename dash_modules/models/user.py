"""
Modèles utilisateur THEBOT
Préparé pour l'authentification future
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text

from .base import BaseModel


class User(BaseModel):
    """
    Modèle utilisateur pour l'authentification future.
    Actuellement utilisé pour stocker les préférences utilisateur.
    """
    __tablename__ = "users"

    # Informations de base (pour futur système d'authentification)
    username = Column(String(50), unique=True, nullable=True, index=True)
    email = Column(String(100), unique=True, nullable=True, index=True)

    # État du compte
    is_active = Column(Integer, default=1, nullable=False)
    is_admin = Column(Integer, default=0, nullable=False)

    # Métadonnées
    last_login = Column(DateTime, nullable=True)
    preferences_id = Column(Integer, nullable=True)  # Clé étrangère vers UserPreferences

    def __repr__(self) -> str:
        return f"<User(username='{self.username}', email='{self.email}')>"


class UserPreferences(BaseModel):
    """
    Préférences utilisateur pour la personnalisation de l'interface.
    """
    __tablename__ = "user_preferences"

    user_id = Column(Integer, nullable=True, index=True)  # Peut être null pour utilisateur anonyme

    # Préférences d'affichage
    theme = Column(String(20), default="dark", nullable=False)  # light, dark
    language = Column(String(10), default="fr", nullable=False)
    timezone = Column(String(50), default="Europe/Paris", nullable=False)

    # Préférences de données
    default_provider = Column(String(50), default="binance", nullable=False)
    refresh_interval = Column(Integer, default=30, nullable=False)  # secondes
    max_news_items = Column(Integer, default=50, nullable=False)

    # Préférences d'alertes
    email_notifications = Column(Integer, default=0, nullable=False)  # 0=désactivé, 1=activé
    sound_notifications = Column(Integer, default=1, nullable=False)

    # Symboles favoris (séparés par des virgules)
    favorite_symbols = Column(String(1000), nullable=True)

    # Layout personnalisé (JSON)
    dashboard_layout = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<UserPreferences(user_id={self.user_id}, theme='{self.theme}')>"

    @property
    def favorite_symbols_list(self) -> list:
        """Retourne la liste des symboles favoris"""
        if not self.favorite_symbols:
            return []
        return [s.strip() for s in self.favorite_symbols.split(',') if s.strip()]

    @favorite_symbols_list.setter
    def favorite_symbols_list(self, symbols: list) -> None:
        """Définit les symboles favoris à partir d'une liste"""
        self.favorite_symbols = ','.join(symbols) if symbols else None

    @classmethod
    def get_default_preferences(cls) -> 'UserPreferences':
        """Retourne les préférences par défaut pour un nouvel utilisateur"""
        return cls(
            theme="dark",
            language="fr",
            timezone="Europe/Paris",
            default_provider="binance",
            refresh_interval=30,
            max_news_items=50,
            email_notifications=0,
            sound_notifications=1
        )
