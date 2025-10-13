"""
Calculateur EMA (Exponential Moving Average)
Module ultra-modulaire - Responsabilité unique : Logique pure de calcul EMA
"""

from collections import deque
from decimal import Decimal
from typing import List, Optional

from thebot.core.types import IndicatorResult, MarketData
from thebot.indicators.basic.ema.config import EMAConfig


class EMACalculator:
    """
    Calculateur pur pour EMA - Aucune dépendance externe
    Implémente l'algorithme : EMA = α × Prix + (1-α) × EMA_précédent
    """

    def __init__(self, config: EMAConfig):
        self.config = config
        self.alpha = config.get_alpha()
        self.one_minus_alpha = config.get_one_minus_alpha()

        # État interne minimal
        self._current_ema: Optional[Decimal] = None
        self._is_initialized = False
        self._data_count = 0

        # Historique pour analyse de tendance (si activé)
        if config.store_history:
            self._history: deque = deque(maxlen=min(config.period * 2, 100))
        else:
            self._history = None

    def add_data_point(self, market_data: MarketData) -> Optional[IndicatorResult]:
        """
        Ajoute un point de données et calcule EMA

        Args:
            market_data: Données de marché

        Returns:
            IndicatorResult si calculable, None sinon
        """
        price = market_data.close
        self._data_count += 1

        if not self._is_initialized:
            # Premier point : EMA = prix
            self._current_ema = price
            self._is_initialized = True
        else:
            # EMA = α × prix_actuel + (1-α) × EMA_précédent
            self._current_ema = (
                self.alpha * price + self.one_minus_alpha * self._current_ema
            )

        # Stocker dans l'historique si activé
        if self._history is not None:
            self._history.append(
                {
                    "timestamp": market_data.timestamp,
                    "price": price,
                    "ema": self._current_ema,
                }
            )

        # Retourner le résultat
        return IndicatorResult(
            value=self._current_ema,
            timestamp=market_data.timestamp,
            indicator_name="EMA",
            metadata={
                "period": self.config.period,
                "alpha": float(self.alpha),
                "data_count": self._data_count,
            },
        )

    def get_current_value(self) -> Optional[Decimal]:
        """Valeur EMA actuelle"""
        return self._current_ema

    def is_ready(self) -> bool:
        """Indicateur prêt (EMA calculable dès le premier point)"""
        return self._is_initialized

    def get_data_count(self) -> int:
        """Nombre de points de données traités"""
        return self._data_count

    def reset(self) -> None:
        """Remet à zéro l'état du calculateur"""
        self._current_ema = None
        self._is_initialized = False
        self._data_count = 0
        if self._history is not None:
            self._history.clear()

    def get_trend_slope(self, periods: int = 3) -> Optional[Decimal]:
        """
        Calcule la pente de tendance sur les N dernières périodes

        Args:
            periods: Nombre de périodes pour calculer la pente

        Returns:
            Pente (positive=haussier, négative=baissier) ou None
        """
        if self._history is None or len(self._history) < periods:
            return None

        recent_values = list(self._history)[-periods:]
        if len(recent_values) < 2:
            return None

        # Régression linéaire simple
        n = len(recent_values)
        sum_x = sum(range(n))
        sum_y = sum(point["ema"] for point in recent_values)
        sum_xy = sum(i * point["ema"] for i, point in enumerate(recent_values))
        sum_x2 = sum(i * i for i in range(n))

        # Pente = (n*sum_xy - sum_x*sum_y) / (n*sum_x2 - sum_x²)
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return Decimal("0")

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope

    def get_volatility(self, periods: int = 10) -> Optional[Decimal]:
        """
        Calcule la volatilité basée sur les variations EMA

        Args:
            periods: Nombre de périodes pour la volatilité

        Returns:
            Écart-type des variations ou None
        """
        if self._history is None or len(self._history) < periods:
            return None

        recent_values = [point["ema"] for point in list(self._history)[-periods:]]
        if len(recent_values) < 2:
            return None

        # Calcul des variations
        changes = [
            recent_values[i] - recent_values[i - 1]
            for i in range(1, len(recent_values))
        ]

        if not changes:
            return Decimal("0")

        # Moyenne des variations
        mean_change = sum(changes) / len(changes)

        # Variance
        variance = sum((change - mean_change) ** 2 for change in changes) / len(changes)

        # Écart-type
        return variance.sqrt()

    def get_smoothness_factor(self) -> Decimal:
        """
        Retourne le facteur de lissage actuel
        Plus alpha est élevé, plus l'EMA réagit rapidement
        """
        return self.alpha

    def compare_with_sma_equivalent(self, sma_values: List[Decimal]) -> dict:
        """
        Compare l'EMA avec une SMA équivalente pour analyse

        Args:
            sma_values: Liste des valeurs SMA de même période

        Returns:
            Dictionnaire avec statistiques de comparaison
        """
        if not self._history or not sma_values:
            return {}

        ema_values = [point["ema"] for point in self._history]
        min_len = min(len(ema_values), len(sma_values))

        if min_len == 0:
            return {}

        ema_subset = ema_values[-min_len:]
        sma_subset = sma_values[-min_len:]

        # Calcul des différences
        differences = [ema - sma for ema, sma in zip(ema_subset, sma_subset)]

        return {
            "mean_difference": sum(differences) / len(differences),
            "max_difference": max(differences),
            "min_difference": min(differences),
            "ema_leads_sma": sum(1 for d in differences if d > 0) / len(differences),
        }
