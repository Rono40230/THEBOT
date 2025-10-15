"""
Modèles pour les alertes THEBOT
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from .base import BaseModel


class Alert(BaseModel):
    """
    Alertes générales du système THEBOT.
    """
    __tablename__ = "alerts"

    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), nullable=False, default="info")  # info, warning, error, success
    category = Column(String(50), nullable=False)  # market, news, system, user

    # Contexte de l'alerte
    symbol = Column(String(20), nullable=True, index=True)
    provider = Column(String(50), nullable=True)

    # État et gestion
    is_read = Column(Integer, default=0, nullable=False)  # 0=non lu, 1=lu
    is_active = Column(Integer, default=1, nullable=False)  # 0=archivée, 1=active

    # Métadonnées
    priority = Column(String(20), default="normal")  # low, normal, high, critical
    expires_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, type='{self.type}', title='{self.title[:30]}...')>"

    @property
    def is_expired(self) -> bool:
        """Vérifie si l'alerte a expiré"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


class PriceAlert(BaseModel):
    """
    Alertes de prix spécifiques pour les symboles.
    """
    __tablename__ = "price_alerts"

    symbol = Column(String(20), nullable=False, index=True)
    provider = Column(String(50), nullable=False)

    # Conditions d'alerte
    condition_type = Column(String(20), nullable=False)  # above, below, between, change_percent
    target_price = Column(Float, nullable=True)
    target_price_min = Column(Float, nullable=True)  # Pour condition 'between'
    target_price_max = Column(Float, nullable=True)  # Pour condition 'between'
    change_percent = Column(Float, nullable=True)    # Pour condition 'change_percent'

    # État
    is_active = Column(Integer, default=1, nullable=False)
    is_triggered = Column(Integer, default=0, nullable=False)
    triggered_at = Column(DateTime, nullable=True)

    # Métadonnées
    name = Column(String(100), nullable=True)  # Nom personnalisé de l'alerte
    description = Column(Text, nullable=True)
    notification_method = Column(String(50), default="dashboard")  # dashboard, email, sms

    # Prix de référence (pour calculer les changements)
    reference_price = Column(Float, nullable=True)
    reference_timestamp = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<PriceAlert(symbol='{self.symbol}', condition='{self.condition_type}', target={self.target_price})>"

    def check_condition(self, current_price: float) -> bool:
        """
        Vérifie si la condition d'alerte est remplie.

        Args:
            current_price: Prix actuel du symbole

        Returns:
            True si l'alerte doit se déclencher
        """
        if not self.is_active or self.is_triggered:
            return False

        if self.condition_type == "above" and self.target_price is not None:
            return current_price >= self.target_price
        elif self.condition_type == "below" and self.target_price is not None:
            return current_price <= self.target_price
        elif self.condition_type == "between" and self.target_price_min is not None and self.target_price_max is not None:
            return self.target_price_min <= current_price <= self.target_price_max
        elif self.condition_type == "change_percent" and self.change_percent is not None and self.reference_price is not None:
            change = ((current_price - self.reference_price) / self.reference_price) * 100
            return abs(change) >= abs(self.change_percent)

        return False

    def trigger(self) -> None:
        """Marque l'alerte comme déclenchée"""
        self.is_triggered = 1
        self.triggered_at = datetime.utcnow()
