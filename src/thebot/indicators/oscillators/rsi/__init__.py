"""
Indicateur RSI (Relative Strength Index) - Orchestration
Module ultra-modulaire - Responsabilité unique : Interface et signaux RSI
"""

from decimal import Decimal
from typing import Any, Dict, Optional

from thebot.core.types import (
    IndicatorResult,
    MarketData,
    Signal,
    SignalDirection,
    SignalStrength,
)
from thebot.indicators.base.indicator import BaseIndicator
from thebot.indicators.oscillators.rsi.calculator import RSICalculator
from thebot.indicators.oscillators.rsi.config import RSIConfig


class RSIIndicator(BaseIndicator):
    """
    Indicateur RSI complet avec génération de signaux
    Orchestration entre configuration, calcul et signalisation
    """

    def __init__(self, config: RSIConfig):
        super().__init__()
        self.config = config
        self.calculator = RSICalculator(config)

        # État pour génération de signaux
        self._previous_result: Optional[IndicatorResult] = None
        self._current_result: Optional[IndicatorResult] = None
        self._signal_history: list = []  # Historique des signaux

    @property
    def name(self) -> str:
        return f"RSI({self.config.period})"

    def get_required_periods(self) -> int:
        """Périodes requises pour RSI stable"""
        return self.config.period + 1  # +1 pour calculer changement prix

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
        Ajoute des données et calcule RSI

        Args:
            market_data: Données de marché

        Returns:
            IndicatorResult ou None
        """
        # Calculer RSI
        result = self.calculator.add_data_point(market_data)

        if result:
            # Mettre à jour l'état pour signaux
            self._previous_result = self._current_result
            self._current_result = result

        return result

    def generate_signal(self, current_result: IndicatorResult) -> Optional[Signal]:
        """
        Génère des signaux basés sur RSI

        Types de signaux RSI :
        1. RSI < 30 = Oversold (BUY signal)
        2. RSI > 70 = Overbought (SELL signal)
        3. RSI < 20 = Extreme oversold (STRONG BUY)
        4. RSI > 80 = Extreme overbought (STRONG SELL)
        5. Divergences RSI vs Prix

        Args:
            current_result: Résultat RSI actuel

        Returns:
            Signal ou None
        """
        if not self.config.enable_signals:
            return None

        current_rsi = current_result.value
        signal_direction = None
        signal_strength = SignalStrength.WEAK
        signal_type = "level"

        # Signaux basés sur les niveaux
        if current_rsi <= self.config.extreme_oversold:
            signal_direction = SignalDirection.BUY
            signal_strength = SignalStrength.STRONG
            signal_type = "extreme_oversold"

        elif current_rsi <= self.config.oversold_level:
            signal_direction = SignalDirection.BUY
            signal_strength = SignalStrength.MEDIUM
            signal_type = "oversold"

        elif current_rsi >= self.config.extreme_overbought:
            signal_direction = SignalDirection.SELL
            signal_strength = SignalStrength.STRONG
            signal_type = "extreme_overbought"

        elif current_rsi >= self.config.overbought_level:
            signal_direction = SignalDirection.SELL
            signal_strength = SignalStrength.MEDIUM
            signal_type = "overbought"

        # Détection de divergences
        divergence_data = self.calculator.get_divergence_data()
        if divergence_data and divergence_data["divergence"]:
            if signal_direction is None:  # Pas de signal de niveau
                if divergence_data["divergence"] == "bullish":
                    signal_direction = SignalDirection.BUY
                    signal_strength = SignalStrength.MEDIUM
                    signal_type = "bullish_divergence"
                elif divergence_data["divergence"] == "bearish":
                    signal_direction = SignalDirection.SELL
                    signal_strength = SignalStrength.MEDIUM
                    signal_type = "bearish_divergence"
            else:
                # Renforcer signal existant avec divergence
                if signal_strength == SignalStrength.WEAK:
                    signal_strength = SignalStrength.MEDIUM
                elif signal_strength == SignalStrength.MEDIUM:
                    signal_strength = SignalStrength.STRONG

        # Générer signal si pertinent
        if signal_direction:
            # Calculer confiance basée sur distance des niveaux
            if (
                current_rsi <= self.config.extreme_oversold
                or current_rsi >= self.config.extreme_overbought
            ):
                confidence = 0.9
            elif (
                current_rsi <= self.config.oversold_level
                or current_rsi >= self.config.overbought_level
            ):
                confidence = 0.7
            else:
                confidence = 0.5  # Signaux de divergence

            # Ajuster confiance selon momentum
            momentum = self.calculator.get_momentum_strength()
            if momentum in ["strong_bullish", "strong_bearish"]:
                confidence = min(0.95, confidence + 0.1)

            signal = Signal(
                direction=signal_direction,
                strength=signal_strength,
                price=current_result.metadata.get(
                    "price", Decimal("0")
                ),  # Prix depuis metadata si dispo
                timestamp=current_result.timestamp,
                source=self.name,
                confidence=confidence,
                metadata={
                    "indicator": self.name,
                    "rsi_value": float(current_rsi),
                    "signal_type": signal_type,
                    "momentum": momentum,
                    "divergence_data": divergence_data,
                    "levels": {
                        "oversold": float(self.config.oversold_level),
                        "overbought": float(self.config.overbought_level),
                    },
                },
            )

            # Stocker dans historique
            self._signal_history.append(
                {
                    "timestamp": signal.timestamp,
                    "signal": signal_type,
                    "direction": signal.direction.value,
                    "rsi": float(current_rsi),
                }
            )

            # Garder seulement les 50 derniers signaux
            if len(self._signal_history) > 50:
                self._signal_history.pop(0)

            return signal

        return None

    def get_rsi_zone(self) -> str:
        """
        Détermine la zone RSI actuelle

        Returns:
            "extreme_overbought", "overbought", "neutral", "oversold", "extreme_oversold"
        """
        if not self.current_value:
            return "unknown"

        rsi = self.current_value

        if rsi >= self.config.extreme_overbought:
            return "extreme_overbought"
        elif rsi >= self.config.overbought_level:
            return "overbought"
        elif rsi <= self.config.extreme_oversold:
            return "extreme_oversold"
        elif rsi <= self.config.oversold_level:
            return "oversold"
        else:
            return "neutral"

    def get_rsi_trend(self, periods: int = 3) -> Optional[str]:
        """
        Détermine la tendance RSI

        Args:
            periods: Nombre de périodes pour analyse

        Returns:
            "rising", "falling", "sideways"
        """
        if not hasattr(self.calculator, "_history") or not self.calculator._history:
            return None

        history = self.calculator._history
        if len(history) < periods:
            return None

        recent_rsi = [point["rsi"] for point in list(history)[-periods:]]

        # Calculer pente simple
        first_half = sum(recent_rsi[: periods // 2]) / (periods // 2)
        second_half = sum(recent_rsi[periods // 2 :]) / (len(recent_rsi) - periods // 2)

        change = second_half - first_half

        if change > 2:  # RSI monte de plus de 2 points
            return "rising"
        elif change < -2:  # RSI baisse de plus de 2 points
            return "falling"
        else:
            return "sideways"

    def get_signal_quality(self) -> dict:
        """
        Évalue la qualité des signaux RSI récents

        Returns:
            Dictionnaire avec statistiques de qualité
        """
        if not self._signal_history:
            return {"quality": "unknown", "signal_count": 0}

        recent_signals = self._signal_history[-10:]  # 10 derniers signaux

        # Types de signaux
        signal_types = [s["signal"] for s in recent_signals]
        type_counts = {}
        for sig_type in signal_types:
            type_counts[sig_type] = type_counts.get(sig_type, 0) + 1

        # Qualité basée sur diversité et niveaux extrêmes
        extreme_signals = sum(1 for s in signal_types if "extreme" in s)
        total_signals = len(recent_signals)

        if total_signals == 0:
            quality = "unknown"
        elif extreme_signals / total_signals > 0.6:
            quality = "high"  # Beaucoup de signaux extrêmes
        elif extreme_signals / total_signals > 0.3:
            quality = "medium"
        else:
            quality = "low"  # Peu de signaux extrêmes

        return {
            "quality": quality,
            "signal_count": total_signals,
            "extreme_ratio": (
                extreme_signals / total_signals if total_signals > 0 else 0
            ),
            "signal_distribution": type_counts,
        }

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
        if self.current_value:
            base_metadata.update(
                {
                    "current_value": float(self.current_value),
                    "rsi_zone": self.get_rsi_zone(),
                    "rsi_trend": self.get_rsi_trend(),
                    "momentum_strength": self.calculator.get_momentum_strength(),
                    "signal_quality": self.get_signal_quality(),
                    "volatility_adjusted_levels": self.calculator.get_volatility_adjusted_levels(),
                }
            )

        return base_metadata

    def reset(self) -> None:
        """Remet à zéro l'indicateur"""
        self.calculator.reset()
        self._previous_result = None
        self._current_result = None
        self._signal_history.clear()
