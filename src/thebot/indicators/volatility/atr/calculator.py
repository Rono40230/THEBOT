"""
Calculateur ATR (Average True Range)
Module ultra-modulaire - Responsabilité unique : Logique pure de calcul ATR
"""

from collections import deque
from decimal import Decimal
from typing import List, Optional

from thebot.core.types import IndicatorResult, MarketData
from thebot.indicators.volatility.atr.config import ATRConfig


class ATRCalculator:
    """
    Calculateur pur pour ATR - Aucune dépendance externe
    Implémente True Range puis moyenne mobile du TR
    """

    def __init__(self, config: ATRConfig):
        self.config = config
        self.alpha = config.get_smoothing_alpha()  # None si SMA

        # État interne pour ATR
        self._previous_close: Optional[Decimal] = None
        self._true_ranges: deque = (
            deque(maxlen=config.period) if config.smoothing_method == "sma" else None
        )
        self._current_atr: Optional[Decimal] = None
        self._is_initialized = False
        self._data_count = 0

        # Historique pour analyse (si activé)
        if config.store_history:
            self._history: deque = deque(maxlen=min(config.period * 2, 100))
        else:
            self._history = None

    def add_data_point(self, market_data: MarketData) -> Optional[IndicatorResult]:
        """
        Ajoute un point de données et calcule ATR

        Args:
            market_data: Données de marché

        Returns:
            IndicatorResult si calculable, None sinon
        """
        current_high = market_data.high
        current_low = market_data.low
        current_close = market_data.close

        # Calculer True Range
        if self._previous_close is None:
            # Premier point : TR = High - Low
            true_range = current_high - current_low
        else:
            # TR = max(High-Low, |High-PrevClose|, |Low-PrevClose|)
            hl_range = current_high - current_low
            hc_range = abs(current_high - self._previous_close)
            lc_range = abs(current_low - self._previous_close)
            true_range = max(hl_range, hc_range, lc_range)

        self._data_count += 1

        # Calculer ATR selon la méthode
        if self.config.smoothing_method == "sma":
            atr = self._calculate_sma_atr(true_range)
        else:  # EMA
            atr = self._calculate_ema_atr(true_range)

        # Stocker dans l'historique si activé
        if self._history is not None:
            self._history.append(
                {
                    "timestamp": market_data.timestamp,
                    "true_range": true_range,
                    "atr": atr,
                    "high": current_high,
                    "low": current_low,
                    "close": current_close,
                }
            )

        # Mettre à jour état
        self._previous_close = current_close
        self._current_atr = atr

        if atr is not None:
            return IndicatorResult(
                value=atr,
                timestamp=market_data.timestamp,
                indicator_name="ATR",
                metadata={
                    "period": self.config.period,
                    "smoothing_method": self.config.smoothing_method,
                    "true_range": float(true_range),
                    "data_count": self._data_count,
                },
            )

        return None

    def _calculate_sma_atr(self, true_range: Decimal) -> Optional[Decimal]:
        """Calcule ATR avec moyenne mobile simple"""
        self._true_ranges.append(true_range)

        if len(self._true_ranges) >= self.config.period:
            self._is_initialized = True
            return sum(self._true_ranges) / len(self._true_ranges)

        return None

    def _calculate_ema_atr(self, true_range: Decimal) -> Optional[Decimal]:
        """Calcule ATR avec moyenne mobile exponentielle"""
        if not self._is_initialized:
            # Premier point EMA
            self._current_atr = true_range
            self._is_initialized = True
            return self._current_atr

        # ATR_EMA = α × TR + (1-α) × ATR_précédent
        self._current_atr = (
            self.alpha * true_range + (Decimal("1") - self.alpha) * self._current_atr
        )
        return self._current_atr

    def get_current_value(self) -> Optional[Decimal]:
        """Valeur ATR actuelle"""
        return self._current_atr

    def is_ready(self) -> bool:
        """Indicateur prêt"""
        if self.config.smoothing_method == "sma":
            return len(self._true_ranges or []) >= self.config.period
        else:
            return self._is_initialized

    def get_data_count(self) -> int:
        """Nombre de points de données traités"""
        return self._data_count

    def reset(self) -> None:
        """Remet à zéro l'état du calculateur"""
        self._previous_close = None
        self._current_atr = None
        self._is_initialized = False
        self._data_count = 0
        if self._true_ranges is not None:
            self._true_ranges.clear()
        if self._history is not None:
            self._history.clear()

    def get_volatility_percentile(self, periods: int = 20) -> Optional[Decimal]:
        """
        Calcule le percentile de volatilité actuel

        Args:
            periods: Nombre de périodes pour comparaison

        Returns:
            Percentile (0-100) ou None
        """
        if self._history is None or len(self._history) < 5 or not self._current_atr:
            return None

        # Utiliser les données disponibles (minimum 5)
        available_periods = min(periods, len(self._history))
        recent_atrs = [
            point["atr"]
            for point in list(self._history)[-available_periods:]
            if point["atr"] is not None
        ]

        if len(recent_atrs) < 3:  # Minimum 3 points pour percentile
            return None

        # Calculer percentile
        sorted_atrs = sorted(recent_atrs)
        current_rank = sum(1 for atr in sorted_atrs if atr <= self._current_atr)
        percentile = (current_rank / len(sorted_atrs)) * 100

        return Decimal(str(round(percentile, 2)))

    def get_normalized_atr(self, price: Decimal) -> Optional[Decimal]:
        """
        Normalise ATR par rapport au prix (ATR en %)

        Args:
            price: Prix de référence

        Returns:
            ATR normalisé en pourcentage ou None
        """
        if not self._current_atr or price == 0:
            return None

        return (self._current_atr / price) * 100

    def get_recent_trend(self, periods: int = 5) -> Optional[str]:
        """
        Détermine la tendance de volatilité

        Args:
            periods: Nombre de périodes pour analyse

        Returns:
            "increasing", "decreasing" ou "stable"
        """
        if self._history is None or len(self._history) < periods:
            return None

        recent_atrs = [
            point["atr"]
            for point in list(self._history)[-periods:]
            if point["atr"] is not None
        ]
        if len(recent_atrs) < periods:
            return None

        # Pente simple
        first_half = sum(recent_atrs[: periods // 2]) / (periods // 2)
        second_half = sum(recent_atrs[periods // 2 :]) / (
            len(recent_atrs) - periods // 2
        )

        change = (second_half - first_half) / first_half

        if change > Decimal("0.1"):  # 10% increase
            return "increasing"
        elif change < Decimal("-0.1"):  # 10% decrease
            return "decreasing"
        else:
            return "stable"
