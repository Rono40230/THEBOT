"""
Indicateur ATR (Average True Range) - Orchestration
Module ultra-modulaire - Responsabilité unique : Interface et signaux de volatilité
"""

from decimal import Decimal
from typing import Any, Dict, Optional

from ....core.types import (
    IndicatorResult,
    MarketData,
    Signal,
    SignalDirection,
    SignalStrength,
)
from ...base.indicator import BaseIndicator
from .calculator import ATRCalculator
from .config import ATRConfig


class ATRIndicator(BaseIndicator):
    """
    Indicateur ATR complet avec génération de signaux de volatilité
    Orchestration entre configuration, calcul et signalisation
    """

    def __init__(self, config: ATRConfig):
        super().__init__()
        self.config = config
        self.calculator = ATRCalculator(config)

        # État pour génération de signaux
        self._previous_result: Optional[IndicatorResult] = None
        self._current_result: Optional[IndicatorResult] = None
        self._price_history: list = []  # Prix de clôture

    @property
    def name(self) -> str:
        return f"ATR({self.config.period})"

    def get_required_periods(self) -> int:
        """Périodes requises pour ATR stable"""
        return self.config.period

    @property
    def is_ready(self) -> bool:
        return self.calculator.is_ready()

    @property
    def current_value(self) -> Optional[Decimal]:
        return self.calculator.get_current_value()

    @property
    def data_count(self) -> int:
        return self.calculator.get_data_count()

    def add_data(self, market_data: MarketData) -> Optional[IndicatorResult]:
        """
        Ajoute des données et calcule ATR

        Args:
            market_data: Données de marché

        Returns:
            IndicatorResult ou None
        """
        # Stocker prix pour signaux
        self._price_history.append(market_data.close)
        if len(self._price_history) > 100:
            self._price_history.pop(0)

        # Calculer ATR
        result = self.calculator.add_data_point(market_data)

        if result:
            # Mettre à jour l'état pour signaux
            self._previous_result = self._current_result
            self._current_result = result

        return result

    def generate_signal(self, current_result: IndicatorResult) -> Optional[Signal]:
        """
        Génère des signaux basés sur la volatilité ATR

        Types de signaux ATR :
        1. Volatilité faible = Consolidation (attendre breakout)
        2. Volatilité élevée = Mouvement fort (prudence)
        3. ATR croissant = Volatilité augmente
        4. ATR décroissant = Marché se calme

        Args:
            current_result: Résultat ATR actuel

        Returns:
            Signal ou None
        """
        if not self.config.enable_signals or not self._price_history:
            return None

        current_atr = current_result.value
        current_price = self._price_history[-1]

        # Normaliser ATR par rapport au prix
        normalized_atr = self.calculator.get_normalized_atr(current_price)
        if normalized_atr is None:
            return None

        signal_direction = None
        signal_strength = SignalStrength.WEAK
        signal_type = "volatility"

        # Détection niveau de volatilité
        if normalized_atr < self.config.volatility_threshold_low:
            # Volatilité faible = Consolidation
            signal_direction = SignalDirection.NEUTRAL
            signal_type = "low_volatility"
            signal_strength = SignalStrength.MEDIUM

        elif normalized_atr > self.config.volatility_threshold_high:
            # Volatilité élevée = Mouvement fort
            signal_direction = SignalDirection.NEUTRAL  # Pas de direction, juste info
            signal_type = "high_volatility"
            signal_strength = SignalStrength.STRONG

        # Tendance de volatilité si on a assez d'historique
        volatility_trend = self.calculator.get_recent_trend()
        if volatility_trend == "increasing" and signal_direction is None:
            signal_direction = SignalDirection.NEUTRAL
            signal_type = "volatility_increasing"
            signal_strength = SignalStrength.MEDIUM

        elif volatility_trend == "decreasing" and signal_direction is None:
            signal_direction = SignalDirection.NEUTRAL
            signal_type = "volatility_decreasing"
            signal_strength = SignalStrength.WEAK

        # Générer signal si pertinent
        if signal_direction:
            percentile = self.calculator.get_volatility_percentile()
            confidence = min(
                0.8, 0.5 + abs(normalized_atr - Decimal("1.0")) / Decimal("2.0")
            )

            return Signal(
                direction=signal_direction,
                strength=signal_strength,
                price=current_price,
                timestamp=current_result.timestamp,
                source=self.name,
                confidence=float(confidence),
                metadata={
                    "indicator": self.name,
                    "atr_value": float(current_atr),
                    "normalized_atr": float(normalized_atr),
                    "signal_type": signal_type,
                    "volatility_trend": volatility_trend,
                    "volatility_percentile": float(percentile) if percentile else None,
                },
            )

        return None

    def get_volatility_regime(self) -> str:
        """
        Détermine le régime de volatilité actuel

        Returns:
            "low", "normal", "high" ou "extreme"
        """
        if not self.current_value or not self._price_history:
            return "unknown"

        current_price = self._price_history[-1]
        normalized_atr = self.calculator.get_normalized_atr(current_price)

        if normalized_atr is None:
            return "unknown"

        if normalized_atr < self.config.volatility_threshold_low:
            return "low"
        elif normalized_atr < self.config.volatility_threshold_high:
            return "normal"
        elif normalized_atr < self.config.volatility_threshold_high * Decimal("2"):
            return "high"
        else:
            return "extreme"

    def get_breakout_threshold(
        self, multiplier: Decimal = Decimal("1.5")
    ) -> Optional[Decimal]:
        """
        Calcule le seuil de breakout basé sur ATR

        Args:
            multiplier: Multiplicateur ATR pour breakout

        Returns:
            Seuil de breakout ou None
        """
        if not self.current_value:
            return None

        return self.current_value * multiplier

    def get_stop_loss_distance(
        self, multiplier: Decimal = Decimal("2.0")
    ) -> Optional[Decimal]:
        """
        Calcule distance stop-loss basée sur ATR

        Args:
            multiplier: Multiplicateur ATR pour stop-loss

        Returns:
            Distance stop-loss ou None
        """
        if not self.current_value:
            return None

        return self.current_value * multiplier

    def get_position_size_factor(self) -> Optional[Decimal]:
        """
        Facteur de dimensionnement de position basé sur volatilité

        Returns:
            Facteur (0.1 = 10% taille normale, 1.0 = taille normale)
        """
        if not self._price_history or not self.current_value:
            return None

        current_price = self._price_history[-1]
        normalized_atr = self.calculator.get_normalized_atr(current_price)

        if normalized_atr is None:
            return Decimal("1.0")

        # Réduire taille si volatilité élevée
        if normalized_atr > self.config.volatility_threshold_high:
            return Decimal("0.5")  # Réduire de moitié
        elif normalized_atr < self.config.volatility_threshold_low:
            return Decimal("1.2")  # Augmenter légèrement
        else:
            return Decimal("1.0")  # Taille normale

    def get_metadata(self) -> Dict[str, Any]:
        """Métadonnées complètes de l'indicateur"""
        base_metadata = {
            "name": self.name,
            "config": self.config.to_dict(),
            "data_points": self.data_count,
            "is_ready": self.is_ready,
            "required_periods": self.get_required_periods(),
        }

        # Ajout métadonnées calculées si disponibles
        if self.current_value and self._price_history:
            current_price = self._price_history[-1]
            normalized_atr = self.calculator.get_normalized_atr(current_price)

            base_metadata.update(
                {
                    "current_value": float(self.current_value),
                    "normalized_atr": float(normalized_atr) if normalized_atr else None,
                    "volatility_regime": self.get_volatility_regime(),
                    "breakout_threshold": float(self.get_breakout_threshold() or 0),
                    "stop_loss_distance": float(self.get_stop_loss_distance() or 0),
                    "position_size_factor": float(self.get_position_size_factor() or 1),
                    "volatility_percentile": float(
                        self.calculator.get_volatility_percentile() or 0
                    ),
                }
            )

        return base_metadata

    def reset(self) -> None:
        """Remet à zéro l'indicateur"""
        self.calculator.reset()
        self._previous_result = None
        self._current_result = None
        self._price_history.clear()
