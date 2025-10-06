"""
Configuration pour l'analyse des Order Blocks (Blocs d'Ordres)
Analyse Smart Money des zones institutionnelles
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class OrderBlockType(Enum):
    """Types d'Order Blocks"""
    BULLISH = "bullish"
    BEARISH = "bearish"


class OrderBlockStatus(Enum):
    """Statut des Order Blocks"""
    ACTIVE = "active"
    TESTED = "tested"
    BROKEN = "broken"
    EXPIRED = "expired"


class OrderBlockStrength(Enum):
    """Force des Order Blocks"""
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


@dataclass
class OrderBlockConfig:
    """Configuration complète pour l'analyse des Order Blocks"""
    
    # Paramètres de base
    min_body_size: float = 0.002  # Taille minimum du corps de bougie (0.2%)
    max_wick_ratio: float = 0.3   # Ratio wick/body maximum (30%)
    min_impulse_strength: float = 0.005  # Force minimum de l'impulsion (0.5%)
    lookback_period: int = 50     # Période de recherche des patterns
    
    # Validation et filtres
    volume_confirmation: bool = True  # Confirmation par le volume
    volume_multiplier: float = 1.5    # Multiplicateur volume moyen
    atr_filter: bool = True           # Filtrage par ATR
    atr_multiplier: float = 2.0       # Multiplicateur ATR pour validation
    
    # Gestion temporelle
    max_age_bars: int = 200          # Âge maximum en barres
    retest_proximity: float = 0.001   # Proximité pour considérer un retest (0.1%)
    break_confirmation: float = 0.002 # Confirmation de cassure (0.2%)
    
    # Détection avancée
    require_impulse_break: bool = True   # Exiger cassure du high/low précédent
    min_impulse_bars: int = 3           # Nombre minimum de barres pour l'impulsion
    max_impulse_bars: int = 20          # Nombre maximum de barres pour l'impulsion
    consolidation_bars: int = 5        # Barres de consolidation avant impulsion
    
    # Scoring et force
    strength_volume_weight: float = 0.3    # Poids du volume dans le score
    strength_size_weight: float = 0.2      # Poids de la taille dans le score
    strength_impulse_weight: float = 0.3   # Poids de l'impulsion dans le score
    strength_age_weight: float = 0.2       # Poids de l'âge dans le score
    
    # Seuils de force
    weak_threshold: float = 0.3        # Seuil faible
    medium_threshold: float = 0.5      # Seuil moyen
    strong_threshold: float = 0.7      # Seuil fort
    very_strong_threshold: float = 0.85 # Seuil très fort
    
    # Zones et confluence
    confluence_distance: float = 0.005   # Distance pour confluence (0.5%)
    merge_overlapping: bool = True       # Fusionner les blocs qui se chevauchent
    overlap_threshold: float = 0.7       # Seuil de chevauchement (70%)
    
    # Affichage et interface
    show_labels: bool = True             # Afficher les labels
    show_strength: bool = True           # Afficher la force
    show_retest_count: bool = True       # Afficher le nombre de retests
    max_blocks_display: int = 20         # Nombre maximum de blocs affichés
    
    # Couleurs et style
    bullish_color: str = "#00FF88"       # Couleur bullish
    bearish_color: str = "#FF4444"       # Couleur bearish
    opacity_active: float = 0.3          # Opacité blocs actifs
    opacity_tested: float = 0.2          # Opacité blocs testés
    opacity_broken: float = 0.1          # Opacité blocs cassés
    
    # Alertes et signaux
    alert_on_formation: bool = True      # Alertes formation nouveaux blocs
    alert_on_retest: bool = True         # Alertes sur retests
    alert_on_break: bool = True          # Alertes sur cassures
    signal_proximity: float = 0.002      # Proximité pour signaux (0.2%)


def get_style_config(trading_style: str) -> OrderBlockConfig:
    """
    Retourne la configuration Order Blocks selon le style de trading
    
    Args:
        trading_style: Style de trading (scalping, day_trading, swing_trading, position_trading)
    
    Returns:
        Configuration Order Blocks optimisée
    """
    
    if trading_style == "scalping":
        return OrderBlockConfig(
            # Scalping: Blocs plus sensibles, réaction rapide
            min_body_size=0.001,          # 0.1% minimum
            max_wick_ratio=0.4,           # Plus tolérant sur les wicks
            min_impulse_strength=0.003,   # Impulsions plus petites
            lookback_period=30,           # Période plus courte
            volume_confirmation=False,     # Pas de confirmation volume
            max_age_bars=100,             # Expiration plus rapide
            require_impulse_break=False,   # Moins strict
            min_impulse_bars=2,           # Impulsions plus courtes
            max_blocks_display=15,        # Moins de blocs
            opacity_active=0.25,          # Plus transparent
        )
    
    elif trading_style == "day_trading":
        return OrderBlockConfig(
            # Day Trading: Configuration équilibrée
            min_body_size=0.002,          # 0.2% minimum
            max_wick_ratio=0.3,           # Standard
            min_impulse_strength=0.005,   # Force standard
            lookback_period=50,           # Période standard
            volume_confirmation=True,      # Confirmation volume
            max_age_bars=200,             # Âge standard
            require_impulse_break=True,    # Standard
            min_impulse_bars=3,           # Standard
            max_blocks_display=20,        # Standard
            opacity_active=0.3,           # Standard
        )
    
    elif trading_style == "swing_trading":
        return OrderBlockConfig(
            # Swing Trading: Blocs de qualité, plus patients
            min_body_size=0.003,          # 0.3% minimum
            max_wick_ratio=0.25,          # Plus strict sur les wicks
            min_impulse_strength=0.008,   # Impulsions plus fortes
            lookback_period=100,          # Période plus longue
            volume_confirmation=True,      # Confirmation volume
            volume_multiplier=2.0,        # Volume plus strict
            max_age_bars=500,             # Plus longue durée de vie
            require_impulse_break=True,    # Strict
            min_impulse_bars=5,           # Impulsions plus longues
            max_blocks_display=25,        # Plus de blocs
            opacity_active=0.35,          # Plus visible
        )
    
    elif trading_style == "position_trading":
        return OrderBlockConfig(
            # Position Trading: Blocs majeurs seulement
            min_body_size=0.005,          # 0.5% minimum
            max_wick_ratio=0.2,           # Très strict
            min_impulse_strength=0.015,   # Impulsions très fortes
            lookback_period=200,          # Période très longue
            volume_confirmation=True,      # Obligatoire
            volume_multiplier=3.0,        # Volume très strict
            max_age_bars=1000,            # Très longue durée de vie
            require_impulse_break=True,    # Très strict
            min_impulse_bars=8,           # Impulsions longues
            max_blocks_display=30,        # Beaucoup de blocs
            opacity_active=0.4,           # Très visible
            strong_threshold=0.6,         # Seuils plus élevés
            very_strong_threshold=0.8,    # Très sélectif
        )
    
    else:
        # Configuration par défaut (day trading)
        return OrderBlockConfig()


# Paramètres par défaut pour l'interface
DEFAULT_PARAMETERS = {
    'min_body_size': 0.002,
    'max_wick_ratio': 0.3,
    'min_impulse_strength': 0.005,
    'lookback_period': 50,
    'volume_confirmation': True,
    'max_age_bars': 200,
    'show_labels': True,
    'max_blocks_display': 20,
    'bullish_color': '#00FF88',
    'bearish_color': '#FF4444',
    'opacity_active': 0.3
}


def create_style_configs() -> Dict[str, OrderBlockConfig]:
    """
    Crée les configurations Order Blocks pour tous les styles de trading
    
    Returns:
        Dictionnaire avec les configurations par style
    """
    
    configs = {}
    
    # Scalping - Réactif et nombreux signaux
    configs['scalping'] = OrderBlockConfig(
        # Base - Scalping: Très réactif
        lookback_period=10,
        volume_multiplier=1.2,
        weak_threshold=0.3,
        min_impulse_strength=0.003,
        min_body_size=0.001,
        max_age_bars=30,
        # Détection - Permissive
        volume_confirmation=False,
        require_impulse_break=False,
        # Visualisation - Compact
        show_labels=False,
        show_strength=True,
        show_retest_count=False,
        bullish_color='#27AE60',
        bearish_color='#E74C3C',
        opacity_active=0.15,
        max_blocks_display=8
    )
    
    # Day Trading - Équilibré
    configs['day_trading'] = OrderBlockConfig(
        # Base - Day Trading: Équilibré
        lookback_period=20,
        volume_multiplier=1.5,
        medium_threshold=0.6,
        min_impulse_strength=0.005,
        min_body_size=0.002,
        max_age_bars=100,
        # Détection - Équilibrée
        volume_confirmation=True,
        require_impulse_break=True,
        # Visualisation - Standard
        show_labels=True,
        show_strength=True,
        show_retest_count=True,
        bullish_color='#2E8B57',
        bearish_color='#DC143C',
        opacity_active=0.30,
        max_blocks_display=15
    )
    
    # Swing Trading - Focus qualité
    configs['swing_trading'] = OrderBlockConfig(
        # Base - Swing Trading: Focus qualité
        lookback_period=50,
        volume_multiplier=2.0,
        strong_threshold=0.7,
        min_impulse_strength=0.008,
        min_body_size=0.005,
        max_age_bars=200,
        # Détection - Stricte
        volume_confirmation=True,
        require_impulse_break=True,
        # Visualisation - Détaillée
        show_labels=True,
        show_strength=True,
        show_retest_count=True,
        bullish_color='#1F5F3F',
        bearish_color='#8B0000',
        opacity_active=0.35,
        max_blocks_display=12
    )
    
    # Position Trading - Majeurs seulement
    configs['position_trading'] = OrderBlockConfig(
        # Base - Position Trading: Majeurs seulement
        lookback_period=100,
        volume_multiplier=3.0,
        very_strong_threshold=0.8,
        min_impulse_strength=0.010,
        min_body_size=0.010,
        max_age_bars=500,
        # Détection - Très stricte
        volume_confirmation=True,
        require_impulse_break=True,
        # Visualisation - Conservatrice
        show_labels=True,
        show_strength=True,
        show_retest_count=True,
        bullish_color='#0F3F1F',
        bearish_color='#4B0000',
        opacity_active=0.40,
        max_blocks_display=8
    )
    
    return configs