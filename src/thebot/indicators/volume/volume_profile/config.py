"""
Configuration du Volume Profile avec POC (Point of Control)
Paramètres pour l'analyse de la distribution du volume par prix
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class VolumeProfileType(Enum):
    """Types de Volume Profile"""

    FIXED_RANGE = "fixed_range"  # Période fixe
    SESSION = "session"  # Par session trading
    VISIBLE_RANGE = "visible_range"  # Zone visible graphique
    CUSTOM = "custom"  # Personnalisé


class ValueAreaMethod(Enum):
    """Méthodes de calcul Value Area"""

    PERCENTAGE = "percentage"  # 70% du volume
    CUSTOM_PCT = "custom_percent"  # Pourcentage personnalisé
    STANDARD_DEV = "standard_dev"  # Écart-type


@dataclass
class VolumeProfileConfig:
    """Configuration Volume Profile + POC"""

    # === PARAMÈTRES DE BASE ===
    profile_type: VolumeProfileType = VolumeProfileType.SESSION
    bins_count: int = 100  # Nombre de niveaux de prix
    value_area_percent: float = 70.0  # % pour Value Area

    # === PÉRIODE ET TIMEFRAME ===
    lookback_periods: int = 100  # Nombre de bougies à analyser
    session_start: str = "00:00"  # Début session
    session_end: str = "23:59"  # Fin session

    # === POC ET VALUE AREA ===
    poc_sensitivity: float = 1.0  # Sensibilité détection POC
    value_area_method: ValueAreaMethod = ValueAreaMethod.PERCENTAGE
    min_volume_threshold: float = 0.01  # Volume minimum % pour niveau

    # === NIVEAUX SUPPORT/RÉSISTANCE ===
    high_volume_threshold: float = 80.0  # % pour High Volume Node
    low_volume_threshold: float = 20.0  # % pour Low Volume Node
    support_resistance_strength: float = 0.7  # Force S/R basé volume

    # === VISUALISATION ===
    show_poc: bool = True  # Afficher POC
    show_value_area: bool = True  # Afficher Value Area
    show_high_volume_nodes: bool = True  # Afficher HVN
    show_low_volume_nodes: bool = False  # Afficher LVN
    show_volume_histogram: bool = True  # Histogramme

    # === COULEURS ET STYLES ===
    poc_color: str = "#FF6B35"  # Orange pour POC
    value_area_color: str = "#4ECDC4"  # Teal pour Value Area
    high_volume_color: str = "#45B7D1"  # Bleu pour HVN
    low_volume_color: str = "#96CEB4"  # Vert clair pour LVN
    histogram_color: str = "#FECA57"  # Jaune pour histogramme

    # === OPACITÉ ET ÉPAISSEUR ===
    poc_line_width: float = 3.0
    value_area_opacity: float = 0.2
    histogram_opacity: float = 0.6
    nodes_line_width: float = 2.0

    # === ALERTES ET SIGNAUX ===
    enable_poc_alerts: bool = True  # Alertes POC
    enable_value_area_alerts: bool = True  # Alertes Value Area
    poc_proximity_percent: float = 0.5  # % proximité pour alerte
    value_area_break_alert: bool = True  # Alerte cassure Value Area

    # === CALCULS AVANCÉS ===
    volume_delta_analysis: bool = False  # Analyse delta buy/sell
    time_weighted_volume: bool = True  # Volume pondéré temps
    normalize_by_range: bool = True  # Normaliser par range prix

    def get_trading_style_config(self, style: str) -> Dict[str, Any]:
        """Retourne config optimisée selon style de trading"""
        configs = {
            "scalping": {
                "bins_count": 50,
                "lookback_periods": 50,
                "value_area_percent": 60.0,
                "poc_sensitivity": 1.5,
                "high_volume_threshold": 75.0,
                "show_low_volume_nodes": True,
                "histogram_opacity": 0.8,
            },
            "day_trading": {
                "bins_count": 100,
                "lookback_periods": 100,
                "value_area_percent": 70.0,
                "poc_sensitivity": 1.0,
                "high_volume_threshold": 80.0,
                "show_low_volume_nodes": False,
                "histogram_opacity": 0.6,
            },
            "swing_trading": {
                "bins_count": 75,
                "lookback_periods": 200,
                "value_area_percent": 75.0,
                "poc_sensitivity": 0.8,
                "high_volume_threshold": 85.0,
                "show_low_volume_nodes": False,
                "histogram_opacity": 0.5,
            },
            "position_trading": {
                "bins_count": 50,
                "lookback_periods": 500,
                "value_area_percent": 80.0,
                "poc_sensitivity": 0.5,
                "high_volume_threshold": 90.0,
                "show_low_volume_nodes": False,
                "histogram_opacity": 0.4,
            },
        }

        return configs.get(style, configs["day_trading"])

    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire"""
        return {
            "profile_type": self.profile_type.value,
            "bins_count": self.bins_count,
            "value_area_percent": self.value_area_percent,
            "lookback_periods": self.lookback_periods,
            "session_start": self.session_start,
            "session_end": self.session_end,
            "poc_sensitivity": self.poc_sensitivity,
            "value_area_method": self.value_area_method.value,
            "min_volume_threshold": self.min_volume_threshold,
            "high_volume_threshold": self.high_volume_threshold,
            "low_volume_threshold": self.low_volume_threshold,
            "support_resistance_strength": self.support_resistance_strength,
            "show_poc": self.show_poc,
            "show_value_area": self.show_value_area,
            "show_high_volume_nodes": self.show_high_volume_nodes,
            "show_low_volume_nodes": self.show_low_volume_nodes,
            "show_volume_histogram": self.show_volume_histogram,
            "poc_color": self.poc_color,
            "value_area_color": self.value_area_color,
            "high_volume_color": self.high_volume_color,
            "low_volume_color": self.low_volume_color,
            "histogram_color": self.histogram_color,
            "poc_line_width": self.poc_line_width,
            "value_area_opacity": self.value_area_opacity,
            "histogram_opacity": self.histogram_opacity,
            "nodes_line_width": self.nodes_line_width,
            "enable_poc_alerts": self.enable_poc_alerts,
            "enable_value_area_alerts": self.enable_value_area_alerts,
            "poc_proximity_percent": self.poc_proximity_percent,
            "value_area_break_alert": self.value_area_break_alert,
            "volume_delta_analysis": self.volume_delta_analysis,
            "time_weighted_volume": self.time_weighted_volume,
            "normalize_by_range": self.normalize_by_range,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VolumeProfileConfig":
        """Création depuis dictionnaire"""
        config = cls()

        # Mise à jour des attributs
        for key, value in data.items():
            if hasattr(config, key):
                if key == "profile_type":
                    setattr(config, key, VolumeProfileType(value))
                elif key == "value_area_method":
                    setattr(config, key, ValueAreaMethod(value))
                else:
                    setattr(config, key, value)

        return config
