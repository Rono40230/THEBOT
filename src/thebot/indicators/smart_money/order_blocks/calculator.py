"""
Calculateur pour l'analyse des Order Blocks (Blocs d'Ordres)
Détection Smart Money des zones institutionnelles
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from .config import (
    OrderBlockConfig,
    OrderBlockStatus,
    OrderBlockStrength,
    OrderBlockType,
    get_style_config,
)


@dataclass
class OrderBlock:
    """Représente un Order Block détecté"""

    # Identification
    id: str
    type: OrderBlockType
    status: OrderBlockStatus

    # Position et taille
    top: float
    bottom: float
    left_time: datetime
    right_time: Optional[datetime]

    # Informations de formation
    formation_bar: int
    impulse_start: int
    impulse_end: int
    impulse_strength: float

    # Métriques de qualité
    body_size: float
    wick_ratio: float
    volume_ratio: float
    strength_score: float
    strength_level: OrderBlockStrength

    # Historique des interactions
    retest_count: int = 0
    last_retest_time: Optional[datetime] = None
    break_time: Optional[datetime] = None

    # Données additionnelles
    confluence_zones: List[str] = None
    notes: str = ""

    def __post_init__(self):
        if self.confluence_zones is None:
            self.confluence_zones = []

    @property
    def size(self) -> float:
        """Taille du bloc en points"""
        return abs(self.top - self.bottom)

    @property
    def size_percentage(self) -> float:
        """Taille du bloc en pourcentage"""
        mid_price = (self.top + self.bottom) / 2
        return (self.size / mid_price) * 100 if mid_price > 0 else 0

    @property
    def mid_price(self) -> float:
        """Prix milieu du bloc"""
        return (self.top + self.bottom) / 2

    @property
    def is_active(self) -> bool:
        """Vérifie si le bloc est actif"""
        return self.status == OrderBlockStatus.ACTIVE

    @property
    def age_bars(self) -> int:
        """Âge du bloc en barres"""
        if self.right_time and self.left_time:
            return int(
                (self.right_time - self.left_time).total_seconds() / 3600
            )  # Approximation
        return 0


class OrderBlockCalculator:
    """Calculateur principal pour les Order Blocks"""

    def __init__(self, config: OrderBlockConfig):
        self.config = config
        self.blocks: List[OrderBlock] = []
        self.last_update = None

    def analyze_blocks(self, data: pd.DataFrame) -> List[OrderBlock]:
        """
        Analyse les données pour détecter les Order Blocks

        Args:
            data: DataFrame avec colonnes OHLCV

        Returns:
            Liste des Order Blocks détectés
        """
        if len(data) < self.config.lookback_period:
            return []

        # Préparation des données
        df = data.copy()
        df = self._prepare_data(df)

        # Détection des Order Blocks
        new_blocks = []

        # Recherche des patterns de formation
        for i in range(
            self.config.lookback_period, len(df) - self.config.min_impulse_bars
        ):
            # Détecter Order Block bullish
            bullish_block = self._detect_bullish_block(df, i)
            if bullish_block:
                new_blocks.append(bullish_block)

            # Détecter Order Block bearish
            bearish_block = self._detect_bearish_block(df, i)
            if bearish_block:
                new_blocks.append(bearish_block)

        # Mise à jour des blocs existants
        self._update_existing_blocks(df)

        # Fusion des nouveaux blocs
        self.blocks.extend(new_blocks)

        # Nettoyage et optimisation
        self._cleanup_blocks()
        self._merge_overlapping_blocks()

        self.last_update = datetime.now()
        return self.blocks

    def _prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prépare les données avec les indicateurs nécessaires"""

        # ATR pour la validation
        df["tr"] = np.maximum(
            df["high"] - df["low"],
            np.maximum(
                abs(df["high"] - df["close"].shift(1)),
                abs(df["low"] - df["close"].shift(1)),
            ),
        )
        df["atr"] = df["tr"].rolling(window=14).mean()

        # Volume moyen
        df["volume_ma"] = df["volume"].rolling(window=20).mean()

        # Taille des corps de bougie
        df["body_size"] = abs(df["close"] - df["open"]) / df["open"]

        # Ratio wick
        df["upper_wick"] = df["high"] - np.maximum(df["open"], df["close"])
        df["lower_wick"] = np.minimum(df["open"], df["close"]) - df["low"]
        df["total_wick"] = df["upper_wick"] + df["lower_wick"]
        df["body_abs"] = abs(df["close"] - df["open"])
        df["wick_ratio"] = df["total_wick"] / (
            df["body_abs"] + 0.0001
        )  # Éviter division par 0

        return df

    def _detect_bullish_block(self, df: pd.DataFrame, idx: int) -> Optional[OrderBlock]:
        """Détecte un Order Block bullish"""

        # 1. Vérifier qu'on a une bougie baissière (dernier ordre vendeur)
        current_bar = df.iloc[idx]
        if current_bar["close"] >= current_bar["open"]:
            return None

        # 2. Vérifier la taille du corps
        body_size = current_bar["body_size"]
        if body_size < self.config.min_body_size:
            return None

        # 3. Vérifier le ratio wick
        wick_ratio = current_bar["wick_ratio"]
        if wick_ratio > self.config.max_wick_ratio:
            return None

        # 4. Chercher l'impulsion haussière qui suit
        impulse_start = idx + 1
        impulse_end = min(idx + self.config.max_impulse_bars, len(df) - 1)

        impulse_data = df.iloc[impulse_start : impulse_end + 1]
        if len(impulse_data) < self.config.min_impulse_bars:
            return None

        # 5. Vérifier la force de l'impulsion
        impulse_low = impulse_data["low"].min()
        impulse_high = impulse_data["high"].max()

        # L'impulsion doit casser le high de la bougie Order Block
        if impulse_high <= current_bar["high"]:
            return None

        # Calculer la force de l'impulsion
        impulse_strength = (impulse_high - current_bar["high"]) / current_bar["high"]
        if impulse_strength < self.config.min_impulse_strength:
            return None

        # 6. Validation volume (si activée)
        if self.config.volume_confirmation:
            avg_volume = df["volume_ma"].iloc[idx]
            if current_bar["volume"] < avg_volume * self.config.volume_multiplier:
                return None

        # 7. Créer l'Order Block
        block_id = f"OB_BULL_{idx}_{datetime.now().strftime('%H%M%S')}"

        # Définir les limites du bloc
        block_top = current_bar["high"]
        block_bottom = current_bar["low"]

        # Calculer les métriques de qualité
        volume_ratio = (
            current_bar["volume"] / df["volume_ma"].iloc[idx]
            if df["volume_ma"].iloc[idx] > 0
            else 1.0
        )
        strength_score = self._calculate_strength_score(
            body_size, wick_ratio, volume_ratio, impulse_strength
        )
        strength_level = self._get_strength_level(strength_score)

        return OrderBlock(
            id=block_id,
            type=OrderBlockType.BULLISH,
            status=OrderBlockStatus.ACTIVE,
            top=block_top,
            bottom=block_bottom,
            left_time=df.index[idx],
            right_time=None,
            formation_bar=idx,
            impulse_start=impulse_start,
            impulse_end=impulse_end,
            impulse_strength=impulse_strength,
            body_size=body_size,
            wick_ratio=wick_ratio,
            volume_ratio=volume_ratio,
            strength_score=strength_score,
            strength_level=strength_level,
        )

    def _detect_bearish_block(self, df: pd.DataFrame, idx: int) -> Optional[OrderBlock]:
        """Détecte un Order Block bearish"""

        # 1. Vérifier qu'on a une bougie haussière (dernier ordre acheteur)
        current_bar = df.iloc[idx]
        if current_bar["close"] <= current_bar["open"]:
            return None

        # 2. Vérifier la taille du corps
        body_size = current_bar["body_size"]
        if body_size < self.config.min_body_size:
            return None

        # 3. Vérifier le ratio wick
        wick_ratio = current_bar["wick_ratio"]
        if wick_ratio > self.config.max_wick_ratio:
            return None

        # 4. Chercher l'impulsion baissière qui suit
        impulse_start = idx + 1
        impulse_end = min(idx + self.config.max_impulse_bars, len(df) - 1)

        impulse_data = df.iloc[impulse_start : impulse_end + 1]
        if len(impulse_data) < self.config.min_impulse_bars:
            return None

        # 5. Vérifier la force de l'impulsion
        impulse_low = impulse_data["low"].min()
        impulse_high = impulse_data["high"].max()

        # L'impulsion doit casser le low de la bougie Order Block
        if impulse_low >= current_bar["low"]:
            return None

        # Calculer la force de l'impulsion
        impulse_strength = (current_bar["low"] - impulse_low) / current_bar["low"]
        if impulse_strength < self.config.min_impulse_strength:
            return None

        # 6. Validation volume (si activée)
        if self.config.volume_confirmation:
            avg_volume = df["volume_ma"].iloc[idx]
            if current_bar["volume"] < avg_volume * self.config.volume_multiplier:
                return None

        # 7. Créer l'Order Block
        block_id = f"OB_BEAR_{idx}_{datetime.now().strftime('%H%M%S')}"

        # Définir les limites du bloc
        block_top = current_bar["high"]
        block_bottom = current_bar["low"]

        # Calculer les métriques de qualité
        volume_ratio = (
            current_bar["volume"] / df["volume_ma"].iloc[idx]
            if df["volume_ma"].iloc[idx] > 0
            else 1.0
        )
        strength_score = self._calculate_strength_score(
            body_size, wick_ratio, volume_ratio, impulse_strength
        )
        strength_level = self._get_strength_level(strength_score)

        return OrderBlock(
            id=block_id,
            type=OrderBlockType.BEARISH,
            status=OrderBlockStatus.ACTIVE,
            top=block_top,
            bottom=block_bottom,
            left_time=df.index[idx],
            right_time=None,
            formation_bar=idx,
            impulse_start=impulse_start,
            impulse_end=impulse_end,
            impulse_strength=impulse_strength,
            body_size=body_size,
            wick_ratio=wick_ratio,
            volume_ratio=volume_ratio,
            strength_score=strength_score,
            strength_level=strength_level,
        )

    def _calculate_strength_score(
        self,
        body_size: float,
        wick_ratio: float,
        volume_ratio: float,
        impulse_strength: float,
    ) -> float:
        """Calcule le score de force d'un Order Block"""

        # Normaliser les composants
        body_score = min(body_size / 0.01, 1.0)  # Normaliser à 1% max
        wick_score = max(0, 1.0 - wick_ratio / 0.5)  # Moins de wick = mieux
        volume_score = min(volume_ratio / 3.0, 1.0)  # Normaliser à 3x max
        impulse_score = min(impulse_strength / 0.02, 1.0)  # Normaliser à 2% max

        # Score pondéré
        total_score = (
            body_score * self.config.strength_size_weight
            + wick_score * 0.1  # Poids faible pour wick
            + volume_score * self.config.strength_volume_weight
            + impulse_score * self.config.strength_impulse_weight
        )

        return min(total_score, 1.0)

    def _get_strength_level(self, score: float) -> OrderBlockStrength:
        """Détermine le niveau de force basé sur le score"""

        if score >= self.config.very_strong_threshold:
            return OrderBlockStrength.VERY_STRONG
        elif score >= self.config.strong_threshold:
            return OrderBlockStrength.STRONG
        elif score >= self.config.medium_threshold:
            return OrderBlockStrength.MEDIUM
        else:
            return OrderBlockStrength.WEAK

    def _update_existing_blocks(self, df: pd.DataFrame):
        """Met à jour le statut des blocs existants"""

        if not self.blocks:
            return

        current_time = df.index[-1]
        current_price = df["close"].iloc[-1]

        for block in self.blocks:
            if block.status == OrderBlockStatus.BROKEN:
                continue

            # Vérifier l'âge
            if block.age_bars > self.config.max_age_bars:
                block.status = OrderBlockStatus.EXPIRED
                continue

            # Vérifier les retests
            if self._is_price_in_block(current_price, block):
                block.retest_count += 1
                block.last_retest_time = current_time
                block.status = OrderBlockStatus.TESTED

            # Vérifier les cassures
            elif self._is_block_broken(current_price, block):
                block.status = OrderBlockStatus.BROKEN
                block.break_time = current_time

    def _is_price_in_block(self, price: float, block: OrderBlock) -> bool:
        """Vérifie si le prix est dans la zone du bloc"""
        return block.bottom <= price <= block.top

    def _is_block_broken(self, price: float, block: OrderBlock) -> bool:
        """Vérifie si le bloc est cassé"""
        if block.type == OrderBlockType.BULLISH:
            return price < (block.bottom - block.size * self.config.break_confirmation)
        else:
            return price > (block.top + block.size * self.config.break_confirmation)

    def _cleanup_blocks(self):
        """Nettoie les blocs expirés et limite le nombre affiché"""

        # Supprimer les blocs expirés anciens
        self.blocks = [
            b
            for b in self.blocks
            if b.status != OrderBlockStatus.EXPIRED or b.age_bars < 100
        ]

        # Limiter le nombre de blocs affichés
        if len(self.blocks) > self.config.max_blocks_display:
            # Garder les plus forts et les plus récents
            self.blocks.sort(
                key=lambda x: (x.strength_score, -x.formation_bar), reverse=True
            )
            self.blocks = self.blocks[: self.config.max_blocks_display]

    def _merge_overlapping_blocks(self):
        """Fusionne les blocs qui se chevauchent"""

        if not self.config.merge_overlapping:
            return

        merged = []
        for block in self.blocks:
            overlapping = None

            for existing in merged:
                if existing.type == block.type and self._blocks_overlap(
                    existing, block
                ):
                    overlapping = existing
                    break

            if overlapping:
                # Fusionner avec le bloc existant
                overlapping.top = max(overlapping.top, block.top)
                overlapping.bottom = min(overlapping.bottom, block.bottom)
                overlapping.strength_score = max(
                    overlapping.strength_score, block.strength_score
                )
                overlapping.retest_count += block.retest_count
            else:
                merged.append(block)

        self.blocks = merged

    def _blocks_overlap(self, block1: OrderBlock, block2: OrderBlock) -> bool:
        """Vérifie si deux blocs se chevauchent"""

        overlap_size = max(
            0, min(block1.top, block2.top) - max(block1.bottom, block2.bottom)
        )
        block1_size = block1.top - block1.bottom

        if block1_size <= 0:
            return False

        overlap_ratio = overlap_size / block1_size
        return overlap_ratio >= self.config.overlap_threshold

    def get_active_blocks(self) -> List[OrderBlock]:
        """Retourne les blocs actifs"""
        return [b for b in self.blocks if b.status == OrderBlockStatus.ACTIVE]

    def get_strong_blocks(
        self, min_strength: OrderBlockStrength = OrderBlockStrength.STRONG
    ) -> List[OrderBlock]:
        """Retourne les blocs forts"""
        strength_order = {
            OrderBlockStrength.WEAK: 0,
            OrderBlockStrength.MEDIUM: 1,
            OrderBlockStrength.STRONG: 2,
            OrderBlockStrength.VERY_STRONG: 3,
        }

        min_level = strength_order[min_strength]
        return [b for b in self.blocks if strength_order[b.strength_level] >= min_level]

    def get_trading_signals(self, current_price: float) -> Dict[str, Any]:
        """Génère des signaux de trading basés sur les Order Blocks"""

        signals = {
            "signal": "neutral",
            "strength": 0.0,
            "blocks_nearby": [],
            "recommendation": "",
            "risk_level": "medium",
        }

        # Chercher les blocs proches
        nearby_blocks = []
        for block in self.get_active_blocks():
            distance = abs(current_price - block.mid_price) / current_price
            if distance <= self.config.signal_proximity:
                nearby_blocks.append((block, distance))

        if not nearby_blocks:
            return signals

        # Trier par distance
        nearby_blocks.sort(key=lambda x: x[1])
        closest_block, distance = nearby_blocks[0]

        signals["blocks_nearby"] = [b[0].id for b in nearby_blocks]

        # Générer le signal
        if closest_block.type == OrderBlockType.BULLISH:
            if (
                current_price <= closest_block.top
                and current_price >= closest_block.bottom
            ):
                signals["signal"] = "buy"
                signals["strength"] = closest_block.strength_score
                signals["recommendation"] = (
                    f"Achat sur Order Block bullish (force: {closest_block.strength_level.value})"
                )

        elif closest_block.type == OrderBlockType.BEARISH:
            if (
                current_price <= closest_block.top
                and current_price >= closest_block.bottom
            ):
                signals["signal"] = "sell"
                signals["strength"] = closest_block.strength_score
                signals["recommendation"] = (
                    f"Vente sur Order Block bearish (force: {closest_block.strength_level.value})"
                )

        # Ajuster le niveau de risque
        if closest_block.strength_level in [
            OrderBlockStrength.STRONG,
            OrderBlockStrength.VERY_STRONG,
        ]:
            signals["risk_level"] = "low"
        elif closest_block.strength_level == OrderBlockStrength.WEAK:
            signals["risk_level"] = "high"

        return signals

    def export_blocks_data(self) -> List[Dict[str, Any]]:
        """Exporte les données des blocs pour analyse"""

        export_data = []
        for block in self.blocks:
            export_data.append(
                {
                    "id": block.id,
                    "type": block.type.value,
                    "status": block.status.value,
                    "top": block.top,
                    "bottom": block.bottom,
                    "left_time": (
                        block.left_time.isoformat() if block.left_time else None
                    ),
                    "formation_bar": block.formation_bar,
                    "impulse_strength": block.impulse_strength,
                    "body_size": block.body_size,
                    "strength_score": block.strength_score,
                    "strength_level": block.strength_level.value,
                    "retest_count": block.retest_count,
                    "size_percentage": block.size_percentage,
                }
            )

        return export_data


def analyze_market_structure(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyse la structure de marché pour détecter les Order Blocks

    Args:
        data: DataFrame OHLCV

    Returns:
        Dictionnaire avec l'analyse de structure
    """

    if len(data) < 20:
        return {
            "trend": "neutral",
            "swing_highs": [],
            "swing_lows": [],
            "structure_breaks": [],
        }

    # Calcul des swing points basique
    SWING_HIGH_PERIOD = 10
    SWING_LOW_PERIOD = 10

    swing_highs = []
    swing_lows = []

    for i in range(SWING_HIGH_PERIOD, len(data) - SWING_HIGH_PERIOD):
        # Swing High
        if all(
            data["high"].iloc[i] >= data["high"].iloc[i - j]
            for j in range(1, high_period + 1)
        ) and all(
            data["high"].iloc[i] >= data["high"].iloc[i + j]
            for j in range(1, high_period + 1)
        ):
            swing_highs.append(
                {"index": i, "time": data.index[i], "price": data["high"].iloc[i]}
            )

        # Swing Low
        if all(
            data["low"].iloc[i] <= data["low"].iloc[i - j]
            for j in range(1, SWING_LOW_PERIOD + 1)
        ) and all(
            data["low"].iloc[i] <= data["low"].iloc[i + j]
            for j in range(1, SWING_LOW_PERIOD + 1)
        ):
            swing_lows.append(
                {"index": i, "time": data.index[i], "price": data["low"].iloc[i]}
            )

    # Détermination de la tendance basique
    if len(swing_highs) >= 2 and len(swing_lows) >= 2:
        recent_highs = swing_highs[-2:]
        recent_lows = swing_lows[-2:]

        if (
            recent_highs[-1]["price"] > recent_highs[-2]["price"]
            and recent_lows[-1]["price"] > recent_lows[-2]["price"]
        ):
            trend = "bullish"
        elif (
            recent_highs[-1]["price"] < recent_highs[-2]["price"]
            and recent_lows[-1]["price"] < recent_lows[-2]["price"]
        ):
            trend = "bearish"
        else:
            trend = "neutral"
    else:
        trend = "neutral"

    return {
        "trend": trend,
        "swing_highs": swing_highs,
        "swing_lows": swing_lows,
        "structure_breaks": [],  # Simplification pour ce test
    }


def find_order_block_signals(
    blocks: List[OrderBlock], current_price: float
) -> Dict[str, Any]:
    """
    Trouve les signaux de trading basés sur les Order Blocks

    Args:
        blocks: Liste des Order Blocks
        current_price: Prix actuel

    Returns:
        Dictionnaire avec les signaux
    """

    if not blocks:
        return {
            "signal": "neutral",
            "strength": 0.0,
            "nearest_block": None,
            "distance": None,
        }

    # Filtre les blocs actifs
    active_blocks = [b for b in blocks if b.status == OrderBlockStatus.ACTIVE]

    if not active_blocks:
        return {
            "signal": "neutral",
            "strength": 0.0,
            "nearest_block": None,
            "distance": None,
        }

    # Trouve le bloc le plus proche
    nearest_block = None
    min_distance = float("inf")

    for block in active_blocks:
        # Distance au bloc (milieu)
        distance_to_block = abs(current_price - block.mid_price) / current_price

        if distance_to_block < min_distance:
            min_distance = distance_to_block
            nearest_block = block

    # Génère les signaux
    signal = "neutral"
    strength = 0.0

    if nearest_block and min_distance < 0.01:  # Moins de 1% de distance
        if (
            nearest_block.type == OrderBlockType.BULLISH
            and current_price <= nearest_block.top
        ):
            signal = "buy"
            strength = nearest_block.strength_score * (
                1 - min_distance * 10
            )  # Plus proche = plus fort
        elif (
            nearest_block.type == OrderBlockType.BEARISH
            and current_price >= nearest_block.bottom
        ):
            signal = "sell"
            strength = nearest_block.strength_score * (1 - min_distance * 10)

    return {
        "signal": signal,
        "strength": max(0, min(1, strength)),
        "nearest_block": nearest_block,
        "distance": min_distance,
    }
