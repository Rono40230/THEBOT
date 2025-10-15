"""
Modèle de base pour tous les modèles THEBOT
Utilise SQLAlchemy avec configuration SQLite
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration de la base de données
DATABASE_URL = "sqlite:///./thebot.db"

# Création du moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Nécessaire pour SQLite
    echo=False  # Désactiver les logs SQL en production
)

# Création de la session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base déclarative pour tous les modèles
Base = declarative_base()


class BaseModel(Base):
    """
    Modèle de base avec champs communs à toutes les tables.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'BaseModel':
        """Crée un objet à partir d'un dictionnaire"""
        # Exclure les champs auto-générés
        filtered_data = {k: v for k, v in data.items() if k not in ['id', 'created_at', 'updated_at']}
        return cls(**filtered_data)


def get_db():
    """
    Générateur de session de base de données.
    À utiliser avec FastAPI ou dans un context manager.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Crée toutes les tables définies dans les modèles.
    À appeler au démarrage de l'application.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Supprime toutes les tables (utilisé pour les tests ou reset).
    """
    Base.metadata.drop_all(bind=engine)

def get_db_session():
    """
    Fonction utilitaire pour obtenir une session de base de données.
    Retourne un context manager pour la session.
    """
    return SessionLocal()
