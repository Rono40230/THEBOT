"""
Support & Resistance Indicator
Détection automatique des niveaux de support et résistance dynamiques
Basé sur les swing highs/lows et la validation des niveaux
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from ...base.indicator import BaseIndicator
from ...base.types import IndicatorResult, MarketData, Signal, SignalDirection


class SRLevel:
    """Représente un niveau de support ou résistance"""

    def __init__(
        self,
        price: float,
        level_type: str,
        strength: int = 1,
        first_touch: datetime = None,
        last_touch: datetime = None,
    ):
        self.price = price
        self.level_type = level_type  # 'support' ou 'resistance'
        self.strength = strength  # Nombre de fois touché
        self.first_touch = first_touch or datetime.now()
        self.last_touch = last_touch or datetime.now()
        self.is_active = True
        self.breaks = 0  # Nombre de cassures

    def update_touch(self, timestamp: datetime):
        """Met à jour lors d'un nouveau touch"""
        self.strength += 1
        self.last_touch = timestamp

    def check_break(self, price: float, timestamp: datetime) -> bool:
        """Vérifie si le niveau a été cassé"""
        tolerance = self.price * 0.001  # 0.1% de tolérance

        if self.level_type == "support" and price < (self.price - tolerance):
            self.breaks += 1
            self.is_active = False
            return True
        elif self.level_type == "resistance" and price > (self.price + tolerance):
            self.breaks += 1
            self.is_active = False
            return True
        return False


class SupportResistanceConfig:
    """Configuration pour Support/Resistance"""

    def __init__(self):
        self.lookback_period = 50  # Périodes pour recherche de swing points
        self.min_strength = 2  # Force minimale d'un niveau
        self.touch_tolerance = 0.002  # 0.2% de tolérance pour touch
        self.max_levels = 10  # Nombre max de niveaux actifs
        self.min_distance = 0.005  # Distance minimale entre niveaux (0.5%)
        self.enabled = True


class SupportResistanceIndicator(BaseIndicator):
    """
    Indicateur Support & Resistance avec détection automatique
    """

    def __init__(self, config: SupportResistanceConfig = None):
        super().__init__()
        self.config = config or SupportResistanceConfig()

        # Historique des données
        self._price_history: List[MarketData] = []

        # Niveaux détectés
        self._support_levels: List[SRLevel] = []
        self._resistance_levels: List[SRLevel] = []

        # Swing points
        self._swing_highs: List[Tuple[datetime, float]] = []
        self._swing_lows: List[Tuple[datetime, float]] = []

        # État
        self._current_result: Optional[IndicatorResult] = None

    @property
    def name(self) -> str:
        return "Support/Resistance"

    def get_required_periods(self) -> int:
        return self.config.lookback_period

    @property
    def is_ready(self) -> bool:
        return len(self._price_history) >= self.get_required_periods()

    @property
    def current_value(self) -> Optional[Dict]:
        if not self.is_ready:
            return None
        return {
            "support_levels": [
                {
                    "price": level.price,
                    "strength": level.strength,
                    "type": level.level_type,
                    "active": level.is_active,
                }
                for level in self._support_levels
                if level.is_active
            ],
            "resistance_levels": [
                {
                    "price": level.price,
                    "strength": level.strength,
                    "type": level.level_type,
                    "active": level.is_active,
                }
                for level in self._resistance_levels
                if level.is_active
            ],
        }

    @property
    def data_count(self) -> int:
        return len(self._price_history)

    def add_data(self, market_data: MarketData) -> Optional[IndicatorResult]:
        """Ajoute des données et calcule les niveaux S/R"""
        self._price_history.append(market_data)

        # Limiter l'historique
        if len(self._price_history) > self.config.lookback_period * 2:
            self._price_history.pop(0)

        if not self.is_ready:
            return None

        # Détecter les swing points
        self._detect_swing_points()

        # Mettre à jour les niveaux
        self._update_levels()

        # Vérifier les touches et cassures
        self._check_touches_and_breaks(market_data)

        # Créer le résultat
        result = IndicatorResult(
            value=self.current_value,
            timestamp=market_data.timestamp,
            indicator_name=self.name,
            metadata={
                "support_count": len([l for l in self._support_levels if l.is_active]),
                "resistance_count": len(
                    [l for l in self._resistance_levels if l.is_active]
                ),
                "total_levels": len(self._support_levels)
                + len(self._resistance_levels),
            },
        )

        self._current_result = result
        return result

    def _detect_swing_points(self):
        """Détecte les swing highs et lows"""
        if len(self._price_history) < 5:
            return

        # Analyser les derniers points pour swing detection
        window = min(10, len(self._price_history))
        recent_data = self._price_history[-window:]

        for i in range(2, len(recent_data) - 2):
            current = recent_data[i]

            # Swing High detection
            if (
                current.high > recent_data[i - 1].high
                and current.high > recent_data[i - 2].high
                and current.high > recent_data[i + 1].high
                and current.high > recent_data[i + 2].high
            ):

                swing_point = (current.timestamp, current.high)
                if swing_point not in self._swing_highs:
                    self._swing_highs.append(swing_point)

            # Swing Low detection
            if (
                current.low < recent_data[i - 1].low
                and current.low < recent_data[i - 2].low
                and current.low < recent_data[i + 1].low
                and current.low < recent_data[i + 2].low
            ):

                swing_point = (current.timestamp, current.low)
                if swing_point not in self._swing_lows:
                    self._swing_lows.append(swing_point)

        # Limiter le nombre de swing points
        self._swing_highs = self._swing_highs[-20:]
        self._swing_lows = self._swing_lows[-20:]

    def _update_levels(self):
        """Met à jour les niveaux S/R basés sur les swing points"""
        current_price = self._price_history[-1].close

        # Créer des niveaux candidats depuis les swing points
        candidate_resistances = []
        candidate_supports = []

        # Résistances depuis swing highs
        for timestamp, price in self._swing_highs:
            if price > current_price:  # Au-dessus du prix actuel
                candidate_resistances.append((price, timestamp))

        # Supports depuis swing lows
        for timestamp, price in self._swing_lows:
            if price < current_price:  # En-dessous du prix actuel
                candidate_supports.append((price, timestamp))

        # Grouper les niveaux proches
        self._group_and_create_levels(candidate_resistances, "resistance")
        self._group_and_create_levels(candidate_supports, "support")

        # Nettoyer les niveaux obsolètes
        self._cleanup_levels()

    def _group_and_create_levels(
        self, candidates: List[Tuple[float, datetime]], level_type: str
    ):
        """Groupe les niveaux proches et crée des niveaux S/R"""
        if not candidates:
            return

        # Trier par prix
        candidates.sort(key=lambda x: x[0])

        # Grouper les niveaux proches
        grouped_levels = []
        current_group = [candidates[0]]

        for i in range(1, len(candidates)):
            price_diff = (
                abs(candidates[i][0] - current_group[-1][0]) / current_group[-1][0]
            )

            if price_diff <= self.config.min_distance:
                current_group.append(candidates[i])
            else:
                if len(current_group) >= self.config.min_strength:
                    grouped_levels.append(current_group)
                current_group = [candidates[i]]

        # Ajouter le dernier groupe
        if len(current_group) >= self.config.min_strength:
            grouped_levels.append(current_group)

        # Créer les niveaux
        levels_list = (
            self._resistance_levels
            if level_type == "resistance"
            else self._support_levels
        )

        for group in grouped_levels:
            avg_price = sum(price for price, _ in group) / len(group)
            strength = len(group)
            first_touch = min(timestamp for _, timestamp in group)
            last_touch = max(timestamp for _, timestamp in group)

            # Vérifier si le niveau existe déjà
            existing_level = None
            for level in levels_list:
                if abs(level.price - avg_price) / avg_price <= self.config.min_distance:
                    existing_level = level
                    break

            if existing_level:
                existing_level.strength = max(existing_level.strength, strength)
                existing_level.last_touch = last_touch
            else:
                new_level = SRLevel(
                    price=avg_price,
                    level_type=level_type,
                    strength=strength,
                    first_touch=first_touch,
                    last_touch=last_touch,
                )
                levels_list.append(new_level)

    def _check_touches_and_breaks(self, market_data: MarketData):
        """Vérifie les touches et cassures des niveaux"""
        current_price = market_data.close
        tolerance = current_price * self.config.touch_tolerance

        # Vérifier tous les niveaux actifs
        all_levels = self._support_levels + self._resistance_levels

        for level in all_levels:
            if not level.is_active:
                continue

            # Vérifier touch
            if abs(current_price - level.price) <= tolerance:
                level.update_touch(market_data.timestamp)

            # Vérifier break
            level.check_break(current_price, market_data.timestamp)

    def _cleanup_levels(self):
        """Nettoie les niveaux obsolètes et limite le nombre"""
        current_time = datetime.now()
        max_age = timedelta(hours=24)  # Niveaux valides 24h

        # Filtrer par âge et activité
        self._support_levels = [
            level
            for level in self._support_levels
            if level.is_active and (current_time - level.last_touch) <= max_age
        ]

        self._resistance_levels = [
            level
            for level in self._resistance_levels
            if level.is_active and (current_time - level.last_touch) <= max_age
        ]

        # Limiter le nombre et garder les plus forts
        self._support_levels.sort(key=lambda x: x.strength, reverse=True)
        self._support_levels = self._support_levels[: self.config.max_levels // 2]

        self._resistance_levels.sort(key=lambda x: x.strength, reverse=True)
        self._resistance_levels = self._resistance_levels[: self.config.max_levels // 2]

    def generate_signal(self, current_result: IndicatorResult) -> Optional[Signal]:
        """Génère des signaux basés sur les niveaux S/R"""
        if not self.is_ready or not current_result.value:
            return None

        current_price = self._price_history[-1].close
        support_levels = current_result.value["support_levels"]
        resistance_levels = current_result.value["resistance_levels"]

        # Trouver le support/résistance le plus proche
        closest_support = None
        closest_resistance = None

        for level in support_levels:
            if not closest_support or abs(current_price - level["price"]) < abs(
                current_price - closest_support["price"]
            ):
                closest_support = level

        for level in resistance_levels:
            if not closest_resistance or abs(current_price - level["price"]) < abs(
                current_price - closest_resistance["price"]
            ):
                closest_resistance = level

        # Générer signal selon proximité
        distance_threshold = current_price * 0.01  # 1%

        if (
            closest_support
            and abs(current_price - closest_support["price"]) <= distance_threshold
        ):
            return Signal(
                direction=SignalDirection.LONG,
                strength=min(closest_support["strength"] / 5.0, 1.0),
                message=f"Prix proche support fort à {closest_support['price']:.4f} (Force: {closest_support['strength']})",
                indicator_name=self.name,
                timestamp=datetime.now(),
                metadata={
                    "level_type": "support",
                    "level_price": closest_support["price"],
                },
            )

        if (
            closest_resistance
            and abs(current_price - closest_resistance["price"]) <= distance_threshold
        ):
            return Signal(
                direction=SignalDirection.SHORT,
                strength=min(closest_resistance["strength"] / 5.0, 1.0),
                message=f"Prix proche résistance forte à {closest_resistance['price']:.4f} (Force: {closest_resistance['strength']})",
                indicator_name=self.name,
                timestamp=datetime.now(),
                metadata={
                    "level_type": "resistance",
                    "level_price": closest_resistance["price"],
                },
            )

        return None

    def get_levels_for_chart(self) -> Dict[str, List[Dict]]:
        """Retourne les niveaux formatés pour l'affichage graphique"""
        return {
            "support_levels": [
                {
                    "y": level.price,
                    "strength": level.strength,
                    "label": f"S: {level.price:.4f} ({level.strength}x)",
                    "color": "green",
                    "line_width": min(level.strength, 5),
                }
                for level in self._support_levels
                if level.is_active
            ],
            "resistance_levels": [
                {
                    "y": level.price,
                    "strength": level.strength,
                    "label": f"R: {level.price:.4f} ({level.strength}x)",
                    "color": "red",
                    "line_width": min(level.strength, 5),
                }
                for level in self._resistance_levels
                if level.is_active
            ],
        }

    def reset(self) -> None:
        """Remet à zéro l'indicateur"""
        self._price_history.clear()
        self._support_levels.clear()
        self._resistance_levels.clear()
        self._swing_highs.clear()
        self._swing_lows.clear()
        self._current_result = None
