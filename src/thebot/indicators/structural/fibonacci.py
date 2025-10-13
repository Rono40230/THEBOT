"""
Fibonacci Retracement & Extension Indicator
Calcul automatique des niveaux de Fibonacci basés sur les swing highs/lows
Support pour retracements et extensions avec visualisation
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ...base.indicator import BaseIndicator
from ...base.types import IndicatorResult, MarketData, Signal, SignalDirection


class FibonacciLevel:
    """Représente un niveau de Fibonacci"""

    def __init__(
        self,
        price: float,
        ratio: float,
        level_type: str,
        swing_high: float,
        swing_low: float,
    ):
        self.price = price
        self.ratio = ratio  # 0.236, 0.382, 0.5, 0.618, 0.786, etc.
        self.level_type = level_type  # 'retracement' ou 'extension'
        self.swing_high = swing_high
        self.swing_low = swing_low
        self.touches = 0
        self.is_active = True

    def check_touch(self, current_price: float, tolerance: float = 0.001) -> bool:
        """Vérifie si le prix touche ce niveau"""
        price_tolerance = self.price * tolerance
        if abs(current_price - self.price) <= price_tolerance:
            self.touches += 1
            return True
        return False


class FibonacciConfig:
    """Configuration pour Fibonacci"""

    def __init__(self):
        # Ratios de retracement
        self.retracement_levels = [0.236, 0.382, 0.5, 0.618, 0.786]

        # Ratios d'extension
        self.extension_levels = [1.272, 1.414, 1.618, 2.0, 2.618]

        # Configuration
        self.lookback_period = 100  # Périodes pour trouver swings
        self.min_swing_size = 0.02  # Taille minimale du swing (2%)
        self.touch_tolerance = 0.002  # Tolérance pour touch (0.2%)
        self.max_age_hours = 48  # Durée de vie des niveaux (heures)
        self.enabled = True


class FibonacciIndicator(BaseIndicator):
    """
    Indicateur Fibonacci avec détection automatique des swings
    Calcule retracements et extensions basés sur les mouvements significatifs
    """

    def __init__(self, config: FibonacciConfig = None):
        super().__init__()
        self.config = config or FibonacciConfig()

        # Historique des données
        self._price_history: List[MarketData] = []

        # Swings détectés
        self._significant_swings: List[Tuple[datetime, float, float, str]] = (
            []
        )  # (time, high, low, direction)

        # Niveaux Fibonacci actifs
        self._fibonacci_levels: List[FibonacciLevel] = []

        # État
        self._current_result: Optional[IndicatorResult] = None
        self._last_calculation = None

    @property
    def name(self) -> str:
        return "Fibonacci"

    def get_required_periods(self) -> int:
        return self.config.lookback_period // 2

    @property
    def is_ready(self) -> bool:
        return len(self._price_history) >= self.get_required_periods()

    @property
    def current_value(self) -> Optional[Dict]:
        if not self.is_ready:
            return None
        return {
            "retracement_levels": [
                {
                    "price": level.price,
                    "ratio": level.ratio,
                    "type": level.level_type,
                    "touches": level.touches,
                    "swing_high": level.swing_high,
                    "swing_low": level.swing_low,
                }
                for level in self._fibonacci_levels
                if level.level_type == "retracement" and level.is_active
            ],
            "extension_levels": [
                {
                    "price": level.price,
                    "ratio": level.ratio,
                    "type": level.level_type,
                    "touches": level.touches,
                    "swing_high": level.swing_high,
                    "swing_low": level.swing_low,
                }
                for level in self._fibonacci_levels
                if level.level_type == "extension" and level.is_active
            ],
            "active_swings": len(self._significant_swings),
        }

    @property
    def data_count(self) -> int:
        return len(self._price_history)

    def add_data(self, market_data: MarketData) -> Optional[IndicatorResult]:
        """Ajoute des données et calcule les niveaux de Fibonacci"""
        self._price_history.append(market_data)

        # Limiter l'historique
        if len(self._price_history) > self.config.lookback_period:
            self._price_history.pop(0)

        if not self.is_ready:
            return None

        # Détecter les swings significatifs
        self._detect_significant_swings()

        # Calculer les niveaux Fibonacci
        self._calculate_fibonacci_levels()

        # Vérifier les touches
        self._check_level_touches(market_data.close)

        # Nettoyer les anciens niveaux
        self._cleanup_old_levels()

        # Créer le résultat
        result = IndicatorResult(
            value=self.current_value,
            timestamp=market_data.timestamp,
            indicator_name=self.name,
            metadata={
                "total_levels": len(self._fibonacci_levels),
                "retracement_count": len(
                    [l for l in self._fibonacci_levels if l.level_type == "retracement"]
                ),
                "extension_count": len(
                    [l for l in self._fibonacci_levels if l.level_type == "extension"]
                ),
                "active_swings": len(self._significant_swings),
            },
        )

        self._current_result = result
        self._last_calculation = market_data.timestamp
        return result

    def _detect_significant_swings(self):
        """Détecte les swings significatifs pour le calcul de Fibonacci"""
        if len(self._price_history) < 20:
            return

        # Analyser les dernières données pour détecter de nouveaux swings
        window_size = min(50, len(self._price_history))
        recent_data = self._price_history[-window_size:]

        # Trouver les extremums locaux
        highs = []
        lows = []

        for i in range(5, len(recent_data) - 5):
            current = recent_data[i]

            # Local high
            if all(
                current.high >= recent_data[j].high
                for j in range(i - 5, i + 6)
                if j != i
            ):
                highs.append((current.timestamp, current.high))

            # Local low
            if all(
                current.low <= recent_data[j].low for j in range(i - 5, i + 6) if j != i
            ):
                lows.append((current.timestamp, current.low))

        # Créer des swings significatifs
        self._create_significant_swings(highs, lows)

    def _create_significant_swings(self, highs: List[Tuple], lows: List[Tuple]):
        """Crée des swings significatifs basés sur la taille minimale"""
        all_points = [(t, p, "high") for t, p in highs] + [
            (t, p, "low") for t, p in lows
        ]
        all_points.sort(key=lambda x: x[0])  # Trier par temps

        current_swing = None

        for i in range(len(all_points) - 1):
            current_point = all_points[i]
            next_point = all_points[i + 1]

            # Calculer la taille du mouvement
            if (
                current_point[2] != next_point[2]
            ):  # Types différents (high -> low ou low -> high)
                move_size = abs(next_point[1] - current_point[1]) / current_point[1]

                if move_size >= self.config.min_swing_size:
                    # Swing significatif détecté
                    if current_point[2] == "high" and next_point[2] == "low":
                        # Mouvement baissier
                        swing = (
                            current_point[0],
                            current_point[1],
                            next_point[1],
                            "bearish",
                        )
                    else:
                        # Mouvement haussier
                        swing = (
                            current_point[0],
                            next_point[1],
                            current_point[1],
                            "bullish",
                        )

                    # Éviter les doublons
                    if swing not in self._significant_swings:
                        self._significant_swings.append(swing)

        # Limiter le nombre de swings
        self._significant_swings = self._significant_swings[-10:]

    def _calculate_fibonacci_levels(self):
        """Calcule les niveaux de Fibonacci pour tous les swings actifs"""
        if not self._significant_swings:
            return

        current_price = self._price_history[-1].close
        new_levels = []

        for swing_time, swing_high, swing_low, direction in self._significant_swings[
            -3:
        ]:  # 3 derniers swings
            swing_size = swing_high - swing_low

            # Calculer les retracements
            for ratio in self.config.retracement_levels:
                if direction == "bullish":
                    # Pour un mouvement haussier, retracement depuis le high
                    fib_price = swing_high - (swing_size * ratio)
                else:
                    # Pour un mouvement baissier, retracement depuis le low
                    fib_price = swing_low + (swing_size * ratio)

                level = FibonacciLevel(
                    price=fib_price,
                    ratio=ratio,
                    level_type="retracement",
                    swing_high=swing_high,
                    swing_low=swing_low,
                )
                new_levels.append(level)

            # Calculer les extensions
            for ratio in self.config.extension_levels:
                if direction == "bullish":
                    # Extension au-dessus du high
                    fib_price = swing_high + (swing_size * (ratio - 1.0))
                else:
                    # Extension en-dessous du low
                    fib_price = swing_low - (swing_size * (ratio - 1.0))

                level = FibonacciLevel(
                    price=fib_price,
                    ratio=ratio,
                    level_type="extension",
                    swing_high=swing_high,
                    swing_low=swing_low,
                )
                new_levels.append(level)

        # Remplacer les anciens niveaux
        self._fibonacci_levels = new_levels

    def _check_level_touches(self, current_price: float):
        """Vérifie les touches des niveaux Fibonacci"""
        for level in self._fibonacci_levels:
            if level.is_active:
                level.check_touch(current_price, self.config.touch_tolerance)

    def _cleanup_old_levels(self):
        """Nettoie les niveaux obsolètes"""
        if not self._last_calculation:
            return

        current_time = datetime.now()
        max_age = timedelta(hours=self.config.max_age_hours)

        # Filtrer par âge
        cutoff_time = current_time - max_age
        self._significant_swings = [
            swing for swing in self._significant_swings if swing[0] >= cutoff_time
        ]

        # Les niveaux sont recalculés à chaque fois, pas besoin de les nettoyer individuellement

    def generate_signal(self, current_result: IndicatorResult) -> Optional[Signal]:
        """Génère des signaux basés sur les niveaux de Fibonacci"""
        if not self.is_ready or not current_result.value:
            return None

        current_price = self._price_history[-1].close
        retracement_levels = current_result.value["retracement_levels"]
        extension_levels = current_result.value["extension_levels"]

        # Trouver le niveau le plus proche
        all_levels = retracement_levels + extension_levels
        if not all_levels:
            return None

        closest_level = min(all_levels, key=lambda x: abs(current_price - x["price"]))
        distance = abs(current_price - closest_level["price"]) / current_price

        # Signal si très proche d'un niveau important
        if distance <= 0.005:  # 0.5%
            # Déterminer la force du signal selon le ratio
            key_levels = [0.382, 0.5, 0.618, 1.272, 1.618]
            is_key_level = any(
                abs(closest_level["ratio"] - key) < 0.01 for key in key_levels
            )

            if is_key_level:
                # Déterminer la direction selon le type et la position
                if closest_level["type"] == "retracement":
                    # Les retracements sont souvent des zones de rebond
                    direction = (
                        SignalDirection.LONG
                        if current_price < closest_level["price"]
                        else SignalDirection.SHORT
                    )
                else:
                    # Les extensions sont des objectifs
                    direction = SignalDirection.NEUTRAL

                strength = 0.8 if is_key_level else 0.5
                if closest_level["touches"] > 0:
                    strength += 0.2  # Bonus si le niveau a déjà été testé

                return Signal(
                    direction=direction,
                    strength=min(strength, 1.0),
                    message=f"Prix proche Fib {closest_level['ratio']:.1%} à {closest_level['price']:.4f} ({closest_level['touches']} touches)",
                    indicator_name=self.name,
                    timestamp=datetime.now(),
                    metadata={
                        "fib_ratio": closest_level["ratio"],
                        "level_type": closest_level["type"],
                        "level_price": closest_level["price"],
                        "touches": closest_level["touches"],
                    },
                )

        return None

    def get_levels_for_chart(self) -> Dict[str, List[Dict]]:
        """Retourne les niveaux formatés pour l'affichage graphique"""
        fib_colors = {
            0.236: "#FFE4B5",  # Moccasin
            0.382: "#FFA500",  # Orange
            0.5: "#FF6347",  # Tomato
            0.618: "#DC143C",  # Crimson
            0.786: "#8B0000",  # DarkRed
            1.272: "#9370DB",  # MediumPurple
            1.414: "#8A2BE2",  # BlueViolet
            1.618: "#4B0082",  # Indigo
            2.0: "#2F4F4F",  # DarkSlateGray
            2.618: "#000080",  # Navy
        }

        return {
            "retracement_levels": [
                {
                    "y": level.price,
                    "ratio": level.ratio,
                    "label": f"Fib {level.ratio:.1%}: {level.price:.4f}",
                    "color": fib_colors.get(level.ratio, "#888888"),
                    "line_width": 3 if level.touches > 0 else 1,
                    "line_dash": (
                        "solid" if level.ratio in [0.382, 0.5, 0.618] else "dash"
                    ),
                }
                for level in self._fibonacci_levels
                if level.level_type == "retracement" and level.is_active
            ],
            "extension_levels": [
                {
                    "y": level.price,
                    "ratio": level.ratio,
                    "label": f"Ext {level.ratio:.1%}: {level.price:.4f}",
                    "color": fib_colors.get(level.ratio, "#888888"),
                    "line_width": 2,
                    "line_dash": "dot",
                }
                for level in self._fibonacci_levels
                if level.level_type == "extension" and level.is_active
            ],
        }

    def reset(self) -> None:
        """Remet à zéro l'indicateur"""
        self._price_history.clear()
        self._significant_swings.clear()
        self._fibonacci_levels.clear()
        self._current_result = None
        self._last_calculation = None
