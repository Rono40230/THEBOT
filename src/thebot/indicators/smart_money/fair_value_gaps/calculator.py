# src/thebot/indicators/smart_money/fair_value_gaps/calculator.py

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from .config import FVGConfig


class FVGType(Enum):
    """Type de Fair Value Gap."""

    BULLISH = "bullish"  # Gap créé par mouvement haussier
    BEARISH = "bearish"  # Gap créé par mouvement baissier


class FVGStatus(Enum):
    """Statut d'un Fair Value Gap."""

    ACTIVE = "active"  # Gap non comblé
    PARTIALLY_FILLED = "partially_filled"  # Gap partiellement comblé
    FILLED = "filled"  # Gap entièrement comblé
    EXPIRED = "expired"  # Gap expiré (trop ancien)


@dataclass
class FairValueGap:
    """
    Représente un Fair Value Gap détecté.

    Un FVG est une zone où le prix a bougé si rapidement qu'il a laissé
    un "vide" dans le carnet d'ordres, créant un déséquilibre qui attire
    souvent le prix pour être comblé.
    """

    # === IDENTIFICATION ===
    id: str  # Identifiant unique
    type: FVGType  # Bullish ou Bearish
    status: FVGStatus  # Statut actuel

    # === DONNÉES TEMPORELLES ===
    creation_time: datetime  # Moment de création
    creation_index: int  # Index de la bougie de création
    last_update: datetime  # Dernière mise à jour

    # === DONNÉES SPATIALES ===
    top: float  # Prix haut de la zone
    bottom: float  # Prix bas de la zone
    size: float  # Taille du gap en %
    mid_point: float  # Point milieu du gap

    # === DONNÉES DE VALIDATION ===
    volume_confirmation: bool  # Confirmé par volume élevé
    creation_volume: float  # Volume lors de la création
    volume_ratio: float  # Ratio volume vs moyenne

    # === DONNÉES DE REMPLISSAGE ===
    fill_percentage: float = 0.0  # % de remplissage (0-100)
    first_touch_time: Optional[datetime] = None  # Premier contact
    fill_time: Optional[datetime] = None  # Moment du remplissage complet

    # === MÉTADONNÉES ===
    strength: float = 0.0  # Force du gap (0-1)
    age_in_candles: int = 0  # Age en nombre de bougies
    touches: int = 0  # Nombre de contacts

    def __post_init__(self):
        """Calculs automatiques après initialisation."""
        self.size = abs(self.top - self.bottom)
        self.mid_point = (self.top + self.bottom) / 2

    def update_status(self, current_price: float, current_time: datetime, max_age: int):
        """Met à jour le statut du gap selon le prix actuel."""
        self.last_update = current_time
        self.age_in_candles += 1

        # Vérifier expiration
        if self.age_in_candles > max_age:
            self.status = FVGStatus.EXPIRED
            return

        # Calculer le remplissage
        if self.type == FVGType.BULLISH:
            # Pour gap bullish, remplissage quand prix descend dans la zone
            if current_price <= self.top:
                if self.first_touch_time is None:
                    self.first_touch_time = current_time
                self.touches += 1

                if current_price <= self.bottom:
                    # Gap entièrement comblé
                    self.fill_percentage = 100.0
                    self.status = FVGStatus.FILLED
                    if self.fill_time is None:
                        self.fill_time = current_time
                else:
                    # Gap partiellement comblé
                    self.fill_percentage = (
                        (self.top - current_price) / self.size
                    ) * 100
                    self.status = FVGStatus.PARTIALLY_FILLED
        else:
            # Pour gap bearish, remplissage quand prix monte dans la zone
            if current_price >= self.bottom:
                if self.first_touch_time is None:
                    self.first_touch_time = current_time
                self.touches += 1

                if current_price >= self.top:
                    # Gap entièrement comblé
                    self.fill_percentage = 100.0
                    self.status = FVGStatus.FILLED
                    if self.fill_time is None:
                        self.fill_time = current_time
                else:
                    # Gap partiellement comblé
                    self.fill_percentage = (
                        (current_price - self.bottom) / self.size
                    ) * 100
                    self.status = FVGStatus.PARTIALLY_FILLED

    def calculate_strength(self, avg_volume: float) -> float:
        """Calcule la force du gap basée sur plusieurs facteurs."""
        strength = 0.0

        # Force basée sur la taille (max 40%)
        size_strength = min(self.size * 100, 2.0) / 2.0 * 0.4
        strength += size_strength

        # Force basée sur le volume (max 30%)
        if self.volume_confirmation and avg_volume > 0:
            volume_strength = min(self.volume_ratio, 3.0) / 3.0 * 0.3
            strength += volume_strength

        # Force basée sur l'âge (max 20%) - plus récent = plus fort
        age_strength = max(0, (50 - self.age_in_candles) / 50) * 0.2
        strength += age_strength

        # Force basée sur le nombre de touches (max 10%) - moins de touches = plus fort
        touch_strength = max(0, (5 - self.touches) / 5) * 0.1
        strength += touch_strength

        self.strength = min(strength, 1.0)
        return self.strength

    def is_active(self) -> bool:
        """Vérifie si le gap est encore actif."""
        return self.status in [FVGStatus.ACTIVE, FVGStatus.PARTIALLY_FILLED]

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le gap en dictionnaire."""
        return {
            "id": self.id,
            "type": self.type.value,
            "status": self.status.value,
            "creation_time": self.creation_time.isoformat(),
            "creation_index": self.creation_index,
            "top": self.top,
            "bottom": self.bottom,
            "size": self.size,
            "mid_point": self.mid_point,
            "volume_confirmation": self.volume_confirmation,
            "creation_volume": self.creation_volume,
            "volume_ratio": self.volume_ratio,
            "fill_percentage": self.fill_percentage,
            "first_touch_time": (
                self.first_touch_time.isoformat() if self.first_touch_time else None
            ),
            "fill_time": self.fill_time.isoformat() if self.fill_time else None,
            "strength": self.strength,
            "age_in_candles": self.age_in_candles,
            "touches": self.touches,
        }


class FVGCalculationError(Exception):
    """Erreur lors du calcul des Fair Value Gaps."""

    pass


class FVGCalculator:
    """
    Calculateur pour la détection des Fair Value Gaps.

    Analyse les données de marché pour identifier les zones de déséquilibre
    créées par des mouvements institutionnels rapides.
    """

    def __init__(self, config: FVGConfig):
        """
        Initialise le calculateur FVG.

        Args:
            config: Configuration FVG
        """
        self.config = config
        self.gaps: List[FairValueGap] = []
        self.data_history: List[Dict[str, Any]] = []
        self.volume_history: List[float] = []
        self._gap_counter = 0

    def calculate_gaps(self, data: pd.DataFrame) -> List[FairValueGap]:
        """
        Calcule les Fair Value Gaps à partir d'un DataFrame.

        Args:
            data: DataFrame avec colonnes OHLCV et index datetime

        Returns:
            Liste des gaps détectés
        """
        try:
            # Réinitialiser pour nouveau calcul
            self.gaps = []
            self.data_history = []
            self.volume_history = []
            self._gap_counter = 0

            # Convertir DataFrame en format dict pour traitement
            for idx, row in data.iterrows():
                candle_data = {
                    "timestamp": (
                        idx
                        if hasattr(idx, "to_pydatetime")
                        else datetime.now(timezone.utc)
                    ),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row.get("volume", 0)),
                }

                # Ajouter à l'historique et détecter gaps
                self.add_data(candle_data)

            return self.gaps.copy()

        except Exception as e:
            raise FVGCalculationError(f"Erreur calcul FVG: {str(e)}")

    def calculate_statistics(self, gaps: List[FairValueGap]) -> Dict[str, Any]:
        """
        Calcule les statistiques des gaps.

        Args:
            gaps: Liste des gaps à analyser

        Returns:
            Dictionnaire avec statistiques
        """
        if not gaps:
            return {
                "total_gaps": 0,
                "active_gaps": 0,
                "filled_gaps": 0,
                "bullish_gaps": 0,
                "bearish_gaps": 0,
                "avg_strength": 0,
                "avg_size": 0,
                "fill_rate": 0,
            }

        active_gaps = [g for g in gaps if g.is_active()]
        filled_gaps = [g for g in gaps if g.status == FVGStatus.FILLED]
        bullish_gaps = [g for g in gaps if g.type == FVGType.BULLISH]
        bearish_gaps = [g for g in gaps if g.type == FVGType.BEARISH]

        return {
            "total_gaps": len(gaps),
            "active_gaps": len(active_gaps),
            "filled_gaps": len(filled_gaps),
            "bullish_gaps": len(bullish_gaps),
            "bearish_gaps": len(bearish_gaps),
            "avg_strength": sum(g.strength for g in gaps) / len(gaps),
            "avg_size": sum(g.size for g in gaps) / len(gaps),
            "fill_rate": len(filled_gaps) / len(gaps) * 100 if gaps else 0,
        }

    def update_gaps_status(
        self, gaps: List[FairValueGap], data: pd.DataFrame
    ) -> List[FairValueGap]:
        """
        Met à jour le statut des gaps existants.

        Args:
            gaps: Gaps existants à mettre à jour
            data: Nouvelles données de marché

        Returns:
            Gaps avec statuts mis à jour
        """
        if not gaps or data.empty:
            return gaps

        # Utiliser le dernier prix pour mise à jour
        last_candle = data.iloc[-1]
        current_price = float(last_candle["close"])
        current_time = (
            data.index[-1]
            if hasattr(data.index[-1], "to_pydatetime")
            else datetime.now(timezone.utc)
        )

        # Calculer volume moyen pour strength
        avg_volume = float(data["volume"].mean()) if "volume" in data.columns else 1000

        # Mettre à jour chaque gap
        for gap in gaps:
            if gap.is_active():
                gap.update_status(current_price, current_time, self.config.max_gap_age)
                gap.calculate_strength(avg_volume)

        return gaps

    def add_data(self, data: Dict[str, Any]) -> None:
        """
        Ajoute de nouvelles données de marché.

        Args:
            data: Données OHLCV avec timestamp
        """
        self.data_history.append(data)
        self.volume_history.append(data.get("volume", 0))

        # Limiter l'historique pour la performance
        max_history = max(self.config.max_gap_age * 2, 200)
        if len(self.data_history) > max_history:
            self.data_history.pop(0)
            self.volume_history.pop(0)

        # Mettre à jour les gaps existants
        self._update_existing_gaps(data)

        # Détecter de nouveaux gaps
        if len(self.data_history) >= 3:  # Besoin de 3 bougies minimum
            self._detect_new_gaps()

    def _update_existing_gaps(self, current_data: Dict[str, Any]) -> None:
        """Met à jour tous les gaps existants."""
        current_price = current_data.get("close", 0)
        current_time = current_data.get("timestamp", datetime.now(timezone.utc))

        for gap in self.gaps:
            if gap.is_active():
                gap.update_status(current_price, current_time, self.config.max_gap_age)
                gap.calculate_strength(self._get_average_volume())

    def _detect_new_gaps(self) -> None:
        """Détecte de nouveaux Fair Value Gaps."""
        if len(self.data_history) < 3:
            return

        # Prendre les 3 dernières bougies
        candle1 = self.data_history[-3]  # Bougie 1 (la plus ancienne)
        candle2 = self.data_history[-2]  # Bougie 2 (milieu)
        candle3 = self.data_history[-1]  # Bougie 3 (la plus récente)

        # Détecter gap bullish: high[1] < low[3]
        if candle1["high"] < candle3["low"]:
            gap = self._create_bullish_gap(candle1, candle2, candle3)
            if gap and self._validate_gap(gap, candle2):
                self.gaps.append(gap)

        # Détecter gap bearish: low[1] > high[3]
        elif candle1["low"] > candle3["high"]:
            gap = self._create_bearish_gap(candle1, candle2, candle3)
            if gap and self._validate_gap(gap, candle2):
                self.gaps.append(gap)

    def _create_bullish_gap(
        self, candle1: Dict, candle2: Dict, candle3: Dict
    ) -> Optional[FairValueGap]:
        """Crée un gap bullish entre candle1.high et candle3.low."""
        top = candle3["low"]
        bottom = candle1["high"]
        size_percent = ((top - bottom) / bottom) * 100

        # Vérifier la taille minimale
        if size_percent < self.config.gap_threshold:
            return None

        self._gap_counter += 1
        gap_id = f"FVG_BULL_{self._gap_counter}"
        creation_time = candle2.get("timestamp", datetime.now(timezone.utc))

        return FairValueGap(
            id=gap_id,
            type=FVGType.BULLISH,
            status=FVGStatus.ACTIVE,
            creation_time=creation_time,
            creation_index=len(self.data_history) - 2,
            last_update=creation_time,  # Initialement même que creation_time
            top=top,
            bottom=bottom,
            size=size_percent,
            mid_point=(top + bottom) / 2,
            volume_confirmation=False,  # Sera validé plus tard
            creation_volume=candle2.get("volume", 0),
            volume_ratio=0.0,  # Sera calculé plus tard
        )

    def _create_bearish_gap(
        self, candle1: Dict, candle2: Dict, candle3: Dict
    ) -> Optional[FairValueGap]:
        """Crée un gap bearish entre candle1.low et candle3.high."""
        top = candle1["low"]
        bottom = candle3["high"]
        size_percent = ((top - bottom) / bottom) * 100

        # Vérifier la taille minimale
        if size_percent < self.config.gap_threshold:
            return None

        self._gap_counter += 1
        gap_id = f"FVG_BEAR_{self._gap_counter}"
        creation_time = candle2.get("timestamp", datetime.now(timezone.utc))

        return FairValueGap(
            id=gap_id,
            type=FVGType.BEARISH,
            status=FVGStatus.ACTIVE,
            creation_time=creation_time,
            creation_index=len(self.data_history) - 2,
            last_update=creation_time,  # Initialement même que creation_time
            top=top,
            bottom=bottom,
            size=size_percent,
            mid_point=(top + bottom) / 2,
            volume_confirmation=False,  # Sera validé plus tard
            creation_volume=candle2.get("volume", 0),
            volume_ratio=0.0,  # Sera calculé plus tard
        )

    def _validate_gap(self, gap: FairValueGap, creation_candle: Dict) -> bool:
        """Valide un gap selon les critères de configuration."""

        # 1. Vérifier la taille minimale
        if gap.size < self.config.min_gap_size:
            return False

        # 2. Vérifier la taille du corps de bougie
        body_size = abs(creation_candle["close"] - creation_candle["open"])
        candle_range = creation_candle["high"] - creation_candle["low"]
        if candle_range > 0:
            body_ratio = body_size / candle_range
            if body_ratio < self.config.min_candle_body:
                return False

        # 3. Vérifier le ratio des wicks
        upper_wick = creation_candle["high"] - max(
            creation_candle["open"], creation_candle["close"]
        )
        lower_wick = (
            min(creation_candle["open"], creation_candle["close"])
            - creation_candle["low"]
        )
        if body_size > 0:
            wick_ratio = (upper_wick + lower_wick) / body_size
            if wick_ratio > self.config.max_wick_ratio:
                return False

        # 4. Vérifier la confirmation par volume
        if self.config.volume_confirmation:
            avg_volume = self._get_average_volume()
            if avg_volume > 0:
                volume_ratio = gap.creation_volume / avg_volume
                gap.volume_ratio = volume_ratio
                gap.volume_confirmation = volume_ratio >= self.config.volume_multiplier
            else:
                gap.volume_confirmation = False
        else:
            gap.volume_confirmation = True

        return True

    def _get_average_volume(self, period: int = 20) -> float:
        """Calcule le volume moyen sur une période."""
        if not self.volume_history:
            return 0.0

        recent_volumes = self.volume_history[-period:]
        return sum(recent_volumes) / len(recent_volumes) if recent_volumes else 0.0

    def get_active_gaps(self) -> List[FairValueGap]:
        """Retourne tous les gaps actifs."""
        return [gap for gap in self.gaps if gap.is_active()]

    def get_gaps_by_status(self, status: FVGStatus) -> List[FairValueGap]:
        """Retourne tous les gaps d'un statut donné."""
        return [gap for gap in self.gaps if gap.status == status]

    def get_gaps_near_price(
        self, price: float, tolerance: float = 0.5
    ) -> List[FairValueGap]:
        """Retourne les gaps proches du prix actuel."""
        near_gaps = []
        for gap in self.get_active_gaps():
            distance_to_gap = min(
                abs(price - gap.top) / price * 100,
                abs(price - gap.bottom) / price * 100,
                abs(price - gap.mid_point) / price * 100,
            )
            if distance_to_gap <= tolerance:
                near_gaps.append(gap)
        return near_gaps

    def calculate_gap_statistics(self) -> Dict[str, Any]:
        """Calcule des statistiques sur les gaps détectés."""
        active_gaps = self.get_active_gaps()
        filled_gaps = self.get_gaps_by_status(FVGStatus.FILLED)

        return {
            "total_gaps": len(self.gaps),
            "active_gaps": len(active_gaps),
            "filled_gaps": len(filled_gaps),
            "fill_rate": len(filled_gaps) / len(self.gaps) * 100 if self.gaps else 0,
            "avg_gap_size": (
                np.mean([gap.size for gap in self.gaps]) if self.gaps else 0
            ),
            "avg_fill_time": self._calculate_avg_fill_time(),
            "strongest_gaps": sorted(
                active_gaps, key=lambda g: g.strength, reverse=True
            )[:5],
        }

    def _calculate_avg_fill_time(self) -> Optional[float]:
        """Calcule le temps moyen de remplissage des gaps en heures."""
        filled_gaps = [
            gap for gap in self.gaps if gap.fill_time and gap.first_touch_time
        ]
        if not filled_gaps:
            return None

        fill_times = []
        for gap in filled_gaps:
            duration = gap.fill_time - gap.first_touch_time
            fill_times.append(duration.total_seconds() / 3600)  # Convertir en heures

        return np.mean(fill_times)

    def reset(self) -> None:
        """Remet à zéro le calculateur."""
        self.gaps.clear()
        self.data_history.clear()
        self.volume_history.clear()
        self._gap_counter = 0

    def export_gaps(self) -> List[Dict[str, Any]]:
        """Exporte tous les gaps au format dictionnaire."""
        return [gap.to_dict() for gap in self.gaps]
