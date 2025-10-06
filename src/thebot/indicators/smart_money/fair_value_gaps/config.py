# src/thebot/indicators/smart_money/fair_value_gaps/config.py

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum

class TradingStyle(Enum):
    """Styles de trading avec paramètres optimisés."""
    SCALPING = "scalping"
    DAY_TRADING = "day_trading"
    SWING_TRADING = "swing_trading"
    POSITION_TRADING = "position_trading"

@dataclass
class FVGConfig:
    """
    Configuration pour l'indicateur Fair Value Gaps (FVG).
    
    Les Fair Value Gaps sont des zones de déséquilibre créées par des mouvements 
    institutionnels rapides, laissant des "vides" dans le carnet d'ordres qui 
    attirent souvent le prix pour être "comblés".
    """
    
    # === PARAMÈTRES DE DÉTECTION ===
    gap_threshold: float = 0.1  # % minimum pour considérer un gap (0.1% = 10 pips)
    min_gap_size: float = 0.05  # % taille minimale du gap pour être valide
    max_gap_age: int = 100      # Nombre max de bougies avant expiration du gap
    
    # === PARAMÈTRES DE VALIDATION ===
    volume_confirmation: bool = True     # Confirmer avec volume élevé
    volume_multiplier: float = 1.5       # Volume doit être X fois la moyenne
    immediate_fill_threshold: float = 0.3 # % de remplissage immédiat accepté
    
    # === PARAMÈTRES DE DÉTECTION AVANCÉE ===
    confluence_detection: bool = True    # Détecter zones de confluence
    confluence_distance: float = 0.5     # Distance max (%) pour confluence
    structural_break_confirmation: bool = False # Confirmer avec cassure structure
    price_action_filter: bool = False    # Filtrer selon patterns de bougies
    
    # === PARAMÈTRES DE FILTRAGE ===
    min_candle_body: float = 0.02  # % taille minimale du corps de bougie
    max_wick_ratio: float = 0.4    # Ratio max wick/body pour éviter les faux gaps
    session_filter: bool = True    # Filtrer selon sessions de marché actives
    news_filter: bool = False      # Éviter gaps créés par actualités
    weekend_gaps: bool = True      # Inclure gaps de weekend
    
    # === PARAMÈTRES DE RETEST ===
    retest_sensitivity: float = 0.1      # Sensibilité détection retests (%)
    max_retest_count: int = 3            # Nombre max de retests avant invalidation
    retest_timeframe: int = 20           # Délai max pour premier retest (bougies)
    
    # === PARAMÈTRES VISUELS ===
    bullish_gap_color: str = "#4CAF50"      # Vert pour gaps haussiers
    bearish_gap_color: str = "#F44336"      # Rouge pour gaps baissiers  
    filled_gap_color: str = "#9E9E9E"       # Gris pour gaps comblés
    gap_opacity: float = 0.3                # Transparence des zones
    show_gap_labels: bool = True            # Afficher labels avec infos
    show_fill_percentage: bool = True       # Afficher % de remplissage
    
    # === PARAMÈTRES VISUELS AVANCÉS ===
    dynamic_opacity: bool = True            # Opacité variable selon âge
    strength_line_width: bool = True        # Épaisseur selon force
    age_color_transition: bool = False      # Transition couleur selon âge
    show_distance_to_price: bool = True     # Afficher distance au prix actuel
    max_gaps_display: int = 20              # Limite affichage pour performance
    
    # === PARAMÈTRES D'ALERTES ===
    auto_alerts: bool = False               # Générer alertes automatiques
    alert_distance: float = 0.2             # Distance (%) pour alerte
    
    # === PARAMÈTRES TECHNIQUES OPTIONNELS ===
    rsi_confirmation: bool = False          # Confirmation RSI optionnelle
    rsi_overbought: float = 70             # Seuil RSI surachat
    rsi_oversold: float = 30               # Seuil RSI survente
    fibonacci_levels: bool = True           # Prioriser niveaux Fibonacci
    
    # === PARAMÈTRES TRADING STYLES ===
    style_multiplier: float = 1.0  # Multiplicateur selon style trading
    
    def __post_init__(self):
        """Validation de la configuration après initialisation."""
        if self.gap_threshold <= 0:
            raise ValueError("gap_threshold doit être positif")
        if self.min_gap_size >= self.gap_threshold:
            raise ValueError("min_gap_size doit être inférieur à gap_threshold")
        if self.max_gap_age <= 0:
            raise ValueError("max_gap_age doit être positif")
        if not 0 <= self.gap_opacity <= 1:
            raise ValueError("gap_opacity doit être entre 0 et 1")

    @classmethod
    def for_scalping(cls) -> 'FVGConfig':
        """Configuration optimisée pour le scalping (très réactive)."""
        return cls(
            gap_threshold=0.05,         # Gaps plus petits détectés
            min_gap_size=0.02,          # Taille minimale réduite
            max_gap_age=50,             # Expiration rapide
            volume_multiplier=1.2,      # Volume confirmation moins stricte
            immediate_fill_threshold=0.5, # Plus tolérant au remplissage immédiat
            style_multiplier=0.5
        )
    
    @classmethod 
    def for_day_trading(cls) -> 'FVGConfig':
        """Configuration équilibrée pour le day trading (standard)."""
        return cls(
            gap_threshold=0.1,          # Standard
            min_gap_size=0.05,          # Standard
            max_gap_age=100,            # Standard
            volume_multiplier=1.5,      # Confirmation modérée
            immediate_fill_threshold=0.3, # Standard
            style_multiplier=1.0
        )
    
    @classmethod
    def for_swing_trading(cls) -> 'FVGConfig':
        """Configuration pour swing trading (gaps significatifs)."""
        return cls(
            gap_threshold=0.2,          # Gaps plus importants
            min_gap_size=0.1,           # Taille minimale plus grande
            max_gap_age=200,            # Durée de vie plus longue
            volume_multiplier=2.0,      # Confirmation stricte
            immediate_fill_threshold=0.1, # Très peu de remplissage immédiat
            style_multiplier=1.5
        )
    
    @classmethod
    def for_position_trading(cls) -> 'FVGConfig':
        """Configuration pour position trading (gaps majeurs uniquement)."""
        return cls(
            gap_threshold=0.3,          # Gaps très significatifs
            min_gap_size=0.15,          # Grande taille minimale
            max_gap_age=500,            # Très longue durée de vie
            volume_multiplier=3.0,      # Confirmation très stricte
            immediate_fill_threshold=0.05, # Presque aucun remplissage immédiat
            style_multiplier=2.0
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convertir la configuration en dictionnaire."""
        return {
            'gap_threshold': self.gap_threshold,
            'min_gap_size': self.min_gap_size,
            'max_gap_age': self.max_gap_age,
            'volume_confirmation': self.volume_confirmation,
            'volume_multiplier': self.volume_multiplier,
            'immediate_fill_threshold': self.immediate_fill_threshold,
            'min_candle_body': self.min_candle_body,
            'max_wick_ratio': self.max_wick_ratio,
            'session_filter': self.session_filter,
            'bullish_gap_color': self.bullish_gap_color,
            'bearish_gap_color': self.bearish_gap_color,
            'filled_gap_color': self.filled_gap_color,
            'gap_opacity': self.gap_opacity,
            'show_gap_labels': self.show_gap_labels,
            'show_fill_percentage': self.show_fill_percentage,
            'style_multiplier': self.style_multiplier
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'FVGConfig':
        """Créer une configuration depuis un dictionnaire."""
        return cls(**config_dict)

    def validate(self) -> bool:
        """Valider la configuration."""
        try:
            self.__post_init__()
            return True
        except ValueError:
            return False

# === FONCTIONS UTILITAIRES ===

def get_trading_style_preset(style: TradingStyle) -> FVGConfig:
    """
    Retourne une configuration FVG optimisée pour un style de trading.
    
    Args:
        style: Style de trading (enum TradingStyle)
        
    Returns:
        Configuration FVG optimisée
    """
    presets = {
        TradingStyle.SCALPING: FVGConfig(
            gap_threshold=0.05,
            min_gap_size=0.02,
            max_gap_age=20,
            volume_confirmation=True,
            volume_multiplier=1.2,
            immediate_fill_threshold=0.5,
            confluence_detection=True,
            confluence_distance=0.3,
            retest_sensitivity=0.05,
            max_retest_count=5,
            session_filter=True,
            news_filter=True,
            dynamic_opacity=True,
            strength_line_width=True,
            max_gaps_display=15,
            auto_alerts=True,
            alert_distance=0.1,
            gap_opacity=0.4,
            show_gap_labels=True,
            style_multiplier=0.5
        ),
        TradingStyle.DAY_TRADING: FVGConfig(
            gap_threshold=0.1,
            min_gap_size=0.05,
            max_gap_age=50,
            volume_confirmation=True,
            volume_multiplier=1.5,
            immediate_fill_threshold=0.3,
            confluence_detection=True,
            confluence_distance=0.5,
            structural_break_confirmation=False,
            retest_sensitivity=0.1,
            max_retest_count=3,
            session_filter=True,
            news_filter=False,
            dynamic_opacity=True,
            strength_line_width=True,
            max_gaps_display=20,
            auto_alerts=False,
            alert_distance=0.2,
            fibonacci_levels=True,
            gap_opacity=0.3,
            show_gap_labels=True,
            style_multiplier=1.0
        ),
        TradingStyle.SWING_TRADING: FVGConfig(
            gap_threshold=0.2,
            min_gap_size=0.1,
            max_gap_age=100,
            volume_confirmation=True,
            volume_multiplier=2.0,
            immediate_fill_threshold=0.1,
            confluence_detection=True,
            confluence_distance=0.8,
            structural_break_confirmation=True,
            price_action_filter=True,
            retest_sensitivity=0.15,
            max_retest_count=2,
            session_filter=False,
            weekend_gaps=False,
            rsi_confirmation=True,
            fibonacci_levels=True,
            dynamic_opacity=True,
            max_gaps_display=25,
            gap_opacity=0.25,
            show_gap_labels=False,
            style_multiplier=2.0
        ),
        TradingStyle.POSITION_TRADING: FVGConfig(
            gap_threshold=0.5,
            min_gap_size=0.25,
            max_gap_age=200,
            volume_confirmation=False,
            volume_multiplier=3.0,
            immediate_fill_threshold=0.05,
            confluence_detection=True,
            confluence_distance=1.0,
            structural_break_confirmation=True,
            price_action_filter=True,
            retest_sensitivity=0.2,
            max_retest_count=1,
            session_filter=False,
            weekend_gaps=True,
            news_filter=False,
            rsi_confirmation=True,
            fibonacci_levels=True,
            dynamic_opacity=False,
            max_gaps_display=10,
            gap_opacity=0.2,
            show_gap_labels=False,
            style_multiplier=4.0
        )
    }
    
    return presets.get(style, presets[TradingStyle.DAY_TRADING])

def validate_fvg_parameters(**kwargs) -> Dict[str, Any]:
    """
    Valide et normalise les paramètres FVG.
    
    Args:
        **kwargs: Paramètres à valider
        
    Returns:
        Paramètres validés et normalisés
    """
    validated = {}
    
    # Gap threshold
    gap_threshold = kwargs.get('gap_threshold', 0.1)
    if not 0.01 <= gap_threshold <= 2.0:
        raise ValueError(f"gap_threshold doit être entre 0.01 et 2.0, reçu: {gap_threshold}")
    validated['gap_threshold'] = gap_threshold
    
    # Max gap age
    max_gap_age = kwargs.get('max_gap_age', 50)
    if not 5 <= max_gap_age <= 500:
        raise ValueError(f"max_gap_age doit être entre 5 et 500, reçu: {max_gap_age}")
    validated['max_gap_age'] = max_gap_age
    
    # Volume confirmation
    validated['volume_confirmation'] = bool(kwargs.get('volume_confirmation', True))
    
    # Gap opacity
    gap_opacity = kwargs.get('gap_opacity', 0.3)
    if not 0.1 <= gap_opacity <= 1.0:
        raise ValueError(f"gap_opacity doit être entre 0.1 et 1.0, reçu: {gap_opacity}")
    validated['gap_opacity'] = gap_opacity
    
    return validated