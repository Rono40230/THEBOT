"""
Module de gestion des styles de trading avec paramètres pré-configurés.
Fournit des configurations optimales pour différents styles de trading.
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class IndicatorConfig:
    """Configuration d'un indicateur spécifique"""
    enabled: bool
    parameters: Dict[str, Any]
    visual: Dict[str, Any]


class TradingStyleManager:
    """Gestionnaire des styles de trading avec paramètres optimisés"""
    
    TRADING_STYLES = {
        "scalping": {
            "name": "⚡ Scalping (1-5min)",
            "description": "Trading ultra-rapide avec nombreux signaux",
            "timeframes": ["1m", "5m"],
            "characteristics": "Signaux fréquents, faible risque par trade"
        },
        "day_trading": {
            "name": "🌅 Day Trading (15min-4h)",
            "description": "Trading intraday avec positions fermées en fin de journée",
            "timeframes": ["15m", "1h", "4h"],
            "characteristics": "Équilibre entre fréquence et qualité des signaux"
        },
        "swing_trading": {
            "name": "📈 Swing Trading (4h-1D)",
            "description": "Trading de mouvements sur plusieurs jours/semaines",
            "timeframes": ["4h", "1d"],
            "characteristics": "Signaux de qualité, positions tenues plusieurs jours"
        },
        "position_trading": {
            "name": "🏔️ Position Trading (1D-1W)",
            "description": "Trading de tendances long terme",
            "timeframes": ["1d", "1w"],
            "characteristics": "Peu de signaux mais très fiables"
        },
        "manuel": {
            "name": "🎯 Configuration Manuelle",
            "description": "Paramètres personnalisés selon vos préférences",
            "timeframes": ["Tous"],
            "characteristics": "Contrôle total des paramètres"
        }
    }
    
    def __init__(self):
        """Initialise le gestionnaire de styles"""
        self.current_style = "day_trading"
        
    def get_style_list(self) -> Dict[str, str]:
        """Retourne la liste des styles pour les composants UI"""
        return {key: config["name"] for key, config in self.TRADING_STYLES.items()}
    
    def get_style_info(self, style: str) -> Dict[str, str]:
        """Retourne les informations détaillées d'un style"""
        return self.TRADING_STYLES.get(style, {})
    
    def get_scalping_config(self) -> Dict[str, IndicatorConfig]:
        """Configuration optimisée pour le scalping"""
        return {
            # Moyennes Mobiles - Très réactives
            "sma": IndicatorConfig(
                enabled=True,
                parameters={"period": 9, "color": "#2E86C1"},
                visual={"line_width": 2, "line_style": "solid"}
            ),
            "ema": IndicatorConfig(
                enabled=True,
                parameters={"period": 5, "color": "#E74C3C"},
                visual={"line_width": 2, "line_style": "solid"}
            ),
            
            # Niveaux - Focus sur niveaux courts
            "support_resistance": IndicatorConfig(
                enabled=True,
                parameters={"strength": 2, "lookback": 20},
                visual={"support_color": "#27AE60", "resistance_color": "#E74C3C", "line_width": 1, "line_style": "solid"}
            ),
            "fibonacci": IndicatorConfig(
                enabled=False,  # Moins utile en scalping
                parameters={"swing_points": 10},
                visual={"colors": ["#F39C12", "#E67E22", "#D35400", "#C0392B", "#8E44AD"], "line_width": 1, "line_style": "dashed"}
            ),
            "pivot_points": IndicatorConfig(
                enabled=True,
                parameters={"method": "standard", "period": "daily"},
                visual={"pivot_color": "#8E44AD", "resistance_colors": ["#E74C3C", "#C0392B", "#922B21"], 
                       "support_colors": ["#27AE60", "#1E8449", "#145A32"], "line_width": 1, "line_style": "dot"}
            ),
            
            # Oscillateurs - Très sensibles
            "rsi": IndicatorConfig(
                enabled=True,
                parameters={"period": 7, "overbought": 75, "oversold": 25},
                visual={"line_color": "#8E44AD", "overbought_color": "#E74C3C", "oversold_color": "#27AE60"}
            ),
            "atr": IndicatorConfig(
                enabled=True,
                parameters={"period": 7, "multiplier": 1.0},
                visual={"line_color": "#F39C12"}
            ),
            "macd": IndicatorConfig(
                enabled=True,
                parameters={"fast": 8, "slow": 21, "signal": 5},
                visual={"macd_color": "#2196F3", "signal_color": "#FF5722", "histogram": True}
            ),
            
            # Smart Money - Fair Value Gaps (Scalping)
            "fvg": IndicatorConfig(
                enabled=True,
                parameters={
                    # Base - Scalping: Réactif, nombreux gaps
                    "min_gap_size": 0.001,  # 0.1% minimum
                    "volume_confirmation": False,  # Pas de confirmation volume (trop restrictif)
                    "overlap_threshold": 0.8,  # 80% overlap pour invalidation
                    "max_distance": 50,  # Distance max en pips
                    # Détection - Sensible
                    "body_rejection": 0.3,  # 30% rejection minimum
                    "wick_ratio": 0.6,  # 60% wick vs body
                    "momentum_filter": True,  # Filtrage momentum
                    "trend_alignment": False,  # Pas d'alignement tendance
                    # Affichage - Compact
                    "show_labels": False,  # Pas de labels (encombrement)
                    "show_stats": True,  # Stats importantes
                    "zones_opacity": 0.15,  # Transparence élevée
                    "max_zones": 10  # Max 10 zones affichées
                },
                visual={"bullish_color": "#27AE60", "bearish_color": "#E74C3C", "opacity": 0.15}
            ),
            
            # Smart Money - Order Blocks (Scalping)
            "order_blocks": IndicatorConfig(
                enabled=True,
                parameters={
                    # Base - Scalping: ULTRA permissif pour crypto volatil
                    "lookback_period": 5,  # Très court
                    "strong_threshold": 0.05,  # 5% seulement
                    "weak_threshold": 0.02,  # 2% ultra-bas
                    "max_age_bars": 20,  # Courte durée
                    # Détection - ULTRA permissive
                    "min_body_size": 0.0001,  # 0.01% minimum
                    "volume_confirmation": False,  # Désactivé
                    "min_impulse_strength": 0.01,  # 1% seulement
                    "max_wick_ratio": 3.0,  # Très permissif wicks
                    "min_impulse_bars": 1,  # 1 barre suffit
                    "max_impulse_bars": 5,  # Recherche courte
                    "volume_multiplier": 0.1,  # 10% volume moyen
                    # Affichage - Compact
                    "show_labels": False,
                    "show_retest_count": True,
                    "opacity_active": 0.25,
                    "opacity_broken": 0.1
                },
                visual={"bullish_color": "#2ECC71", "bearish_color": "#E67E22", "opacity": 0.25}
            ),
            
            # Momentum - Squeeze Momentum (Scalping)
            "squeeze_momentum": IndicatorConfig(
                enabled=True,
                parameters={
                    # BB/KC - Ultra sensible
                    "bb_period": 10,  # Court
                    "bb_deviation": 1.5,  # Moins strict
                    "kc_period": 10,  # Court
                    "kc_atr_period": 5,  # Ultra court
                    "kc_multiplier": 1.0,  # Sensible
                    # Momentum - Réactif
                    "momentum_period": 5,  # Très court
                    "momentum_ma_period": 3,  # Ultra court
                    # Alertes - Fréquentes
                    "squeeze_alert": True,
                    "momentum_alert": True,
                    "min_squeeze_bars": 1  # Immédiat
                },
                visual={"squeeze_color": "#FF9800", "momentum_color": "#2196F3", "line_width": 1}
            ),
            
            # Patterns - Candle Patterns (Scalping)
            "candle_patterns": IndicatorConfig(
                enabled=True,
                parameters={
                    # Détection - Très permissive
                    "doji_threshold": 0.05,  # 5% body
                    "hammer_ratio": 1.5,  # 1.5x wick
                    "body_size_min": 0.01,  # 1% minimum
                    # Engulfing - Sensible
                    "engulfing_body_ratio": 0.8,  # 80% engulfing
                    "engulfing_volume_confirm": False,  # Pas de volume
                    # Affichage - Compact
                    "show_labels": False,  # Pas d'encombrement
                    "show_stats": True,
                    "max_patterns": 5  # Limité
                },
                visual={"bullish_color": "#4CAF50", "bearish_color": "#F44336", "opacity": 0.7}
            ),
            
            # Breakout - Breakout Detector (Scalping)
            "breakout_detector": IndicatorConfig(
                enabled=True,
                parameters={
                    # Support/Resistance - Court terme
                    "sr_period": 10,  # Très court
                    "sr_strength": 1,  # Permissif
                    "price_precision": 4,  # Précision élevée
                    # Volume - Sensible
                    "volume_threshold": 0.3,  # 30% volume moyen
                    "volume_ma_period": 5,  # Court
                    # Breakout - Réactif
                    "breakout_threshold": 0.02,  # 2% breakout
                    "confirmation_bars": 1,  # Confirmation rapide
                    "max_age_levels": 20  # Niveaux récents
                },
                visual={"support_color": "#00BCD4", "resistance_color": "#FF5722", "breakout_color": "#FFEB3B"}
            ),
            
            # Volume Analysis - Volume Profile (Scalping)
            "volume_profile": IndicatorConfig(
                enabled=True,
                parameters={
                    # Base - Scalping: Analyse courte, réactive
                    "profile_type": "session",  # Par session
                    "bins_count": 50,  # Moins de niveaux, plus lisible
                    "lookback_periods": 50,  # Période courte
                    "value_area_percent": 60.0,  # Value Area plus étroite
                    # POC - Sensible
                    "poc_sensitivity": 1.5,  # Très sensible
                    "high_volume_threshold": 75.0,  # 75% pour HVN
                    "low_volume_threshold": 25.0,  # Montrer LVN
                    "support_resistance_strength": 0.8,  # Force S/R
                    # Visualisation - Scalping
                    "show_poc": True,
                    "show_value_area": True,
                    "show_high_volume_nodes": True,
                    "show_low_volume_nodes": True,  # Utile scalping
                    "show_volume_histogram": True,
                    # Alertes - Fréquentes
                    "enable_poc_alerts": True,
                    "enable_value_area_alerts": True,
                    "poc_proximity_percent": 0.3,  # 0.3% alerte POC
                    "value_area_break_alert": True,
                    # Opacité - Visible
                    "histogram_opacity": 0.8,  # Très visible
                    "value_area_opacity": 0.3
                },
                visual={"poc_color": "#FF6B35", "value_area_color": "#4ECDC4", "histogram_color": "#FECA57"}
            )
        }
    
    def get_day_trading_config(self) -> Dict[str, IndicatorConfig]:
        """Configuration optimisée pour le day trading"""
        return {
            # Moyennes Mobiles - Standard
            "sma": IndicatorConfig(
                enabled=True,
                parameters={"period": 20, "color": "#2E86C1"},
                visual={"line_width": 2, "line_style": "solid"}
            ),
            "ema": IndicatorConfig(
                enabled=True,
                parameters={"period": 12, "color": "#E74C3C"},
                visual={"line_width": 2, "line_style": "solid"}
            ),
            
            # Niveaux - Équilibrés
            "support_resistance": IndicatorConfig(
                enabled=True,
                parameters={"strength": 3, "lookback": 50},
                visual={"support_color": "#27AE60", "resistance_color": "#E74C3C", "line_width": 2, "line_style": "solid"}
            ),
            "fibonacci": IndicatorConfig(
                enabled=True,
                parameters={"swing_points": 20},
                visual={"colors": ["#F39C12", "#E67E22", "#D35400", "#C0392B", "#8E44AD"], "line_width": 1, "line_style": "dashed"}
            ),
            "pivot_points": IndicatorConfig(
                enabled=True,
                parameters={"method": "standard", "period": "daily"},
                visual={"pivot_color": "#8E44AD", "resistance_colors": ["#E74C3C", "#C0392B", "#922B21"], 
                       "support_colors": ["#27AE60", "#1E8449", "#145A32"], "line_width": 2, "line_style": "solid"}
            ),
            
            # Oscillateurs - Standard
            "rsi": IndicatorConfig(
                enabled=True,
                parameters={"period": 14, "overbought": 70, "oversold": 30},
                visual={"line_color": "#8E44AD", "overbought_color": "#E74C3C", "oversold_color": "#27AE60"}
            ),
            "atr": IndicatorConfig(
                enabled=True,
                parameters={"period": 14, "multiplier": 2.0},
                visual={"line_color": "#F39C12"}
            ),
            "macd": IndicatorConfig(
                enabled=True,
                parameters={"fast": 12, "slow": 26, "signal": 9},
                visual={"macd_color": "#2196F3", "signal_color": "#FF5722", "histogram": True}
            ),
            
            # Smart Money - Fair Value Gaps (Day Trading)
            "fvg": IndicatorConfig(
                enabled=True,
                parameters={
                    # Base - Day Trading: Équilibré
                    "min_gap_size": 0.002,  # 0.2% minimum
                    "volume_confirmation": True,  # Confirmation volume
                    "overlap_threshold": 0.7,  # 70% overlap pour invalidation
                    "max_distance": 100,  # Distance max en pips
                    # Détection - Standard
                    "body_rejection": 0.5,  # 50% rejection minimum
                    "wick_ratio": 0.5,  # 50% wick vs body
                    "momentum_filter": True,  # Filtrage momentum
                    "trend_alignment": True,  # Alignement tendance
                    # Affichage - Équilibré
                    "show_labels": True,  # Labels utiles
                    "show_stats": True,  # Stats importantes
                    "zones_opacity": 0.2,  # Transparence modérée
                    "max_zones": 15  # Max 15 zones affichées
                },
                visual={"bullish_color": "#27AE60", "bearish_color": "#E74C3C", "opacity": 0.2}
            ),
            
                        # Smart Money - Order Blocks (Day Trading)
            "order_blocks": IndicatorConfig(
                enabled=True,
                parameters={
                    # Base - Day Trading: Permissif pour crypto
                    "lookback_period": 10,  # Court
                    "strong_threshold": 0.1,  # 10% permissif
                    "weak_threshold": 0.05,  # 5% très bas
                    "max_age_bars": 50,  # Durée raisonnable
                    # Détection - Permissive
                    "min_body_size": 0.0003,  # 0.03% minimum
                    "volume_confirmation": False,  # Désactivé
                    "min_impulse_strength": 0.03,  # 3% impulse
                    "max_wick_ratio": 2.0,  # Permissif wicks
                    "min_impulse_bars": 1,
                    "max_impulse_bars": 8,
                    "volume_multiplier": 0.2,  # 20% volume moyen
                    # Affichage
                    "show_labels": True,
                    "show_retest_count": True,
                    "opacity_active": 0.3,
                    "opacity_broken": 0.15
                },
                visual={"bullish_color": "#27AE60", "bearish_color": "#E74C3C", "opacity": 0.3}
            ),
            
            # Momentum - Squeeze Momentum (Day Trading)
            "squeeze_momentum": IndicatorConfig(
                enabled=True,
                parameters={
                    # BB/KC - Standard
                    "bb_period": 20,  # Standard
                    "bb_deviation": 2.0,  # Standard
                    "kc_period": 20,  # Standard
                    "kc_atr_period": 10,  # Standard
                    "kc_multiplier": 1.5,  # Standard
                    # Momentum - Équilibré
                    "momentum_period": 12,  # Standard
                    "momentum_ma_period": 6,  # Standard
                    # Alertes - Équilibrées
                    "squeeze_alert": True,
                    "momentum_alert": True,
                    "min_squeeze_bars": 3  # Confirmation
                },
                visual={"squeeze_color": "#FF9800", "momentum_color": "#2196F3", "line_width": 2}
            ),
            
            # Patterns - Candle Patterns (Day Trading)
            "candle_patterns": IndicatorConfig(
                enabled=True,
                parameters={
                    # Détection - Standard
                    "doji_threshold": 0.1,  # 10% body
                    "hammer_ratio": 2.0,  # 2x wick
                    "body_size_min": 0.02,  # 2% minimum
                    # Engulfing - Standard
                    "engulfing_body_ratio": 1.0,  # 100% engulfing
                    "engulfing_volume_confirm": True,  # Avec volume
                    # Affichage - Complet
                    "show_labels": True,  # Labels utiles
                    "show_stats": True,
                    "max_patterns": 8  # Plus de patterns
                },
                visual={"bullish_color": "#4CAF50", "bearish_color": "#F44336", "opacity": 0.8}
            ),
            
            # Breakout - Breakout Detector (Day Trading)
            "breakout_detector": IndicatorConfig(
                enabled=True,
                parameters={
                    # Support/Resistance - Standard
                    "sr_period": 20,  # Standard
                    "sr_strength": 2,  # Standard
                    "price_precision": 4,  # Précision
                    # Volume - Confirmation
                    "volume_threshold": 0.5,  # 50% volume moyen
                    "volume_ma_period": 10,  # Standard
                    # Breakout - Confirmé
                    "breakout_threshold": 0.03,  # 3% breakout
                    "confirmation_bars": 2,  # Confirmation
                    "max_age_levels": 50  # Niveaux plus longs
                },
                visual={"support_color": "#00BCD4", "resistance_color": "#FF5722", "breakout_color": "#FFEB3B"}
            ),
            
            # Volume Analysis - Volume Profile (Day Trading)
            "volume_profile": IndicatorConfig(
                enabled=True,
                parameters={
                    # Base - Day Trading: Standard professionnel
                    "profile_type": "session",  # Par session
                    "bins_count": 100,  # Standard
                    "lookback_periods": 100,  # Période équilibrée
                    "value_area_percent": 70.0,  # Value Area standard
                    # POC - Standard
                    "poc_sensitivity": 1.0,  # Standard
                    "high_volume_threshold": 80.0,  # 80% pour HVN
                    "low_volume_threshold": 20.0,  # Pas de LVN
                    "support_resistance_strength": 1.0,  # Force S/R standard
                    # Visualisation - Complète
                    "show_poc": True,
                    "show_value_area": True,
                    "show_high_volume_nodes": True,
                    "show_low_volume_nodes": False,  # Pas utile day trading
                    "show_volume_histogram": True,
                    # Alertes - Équilibrées
                    "enable_poc_alerts": True,
                    "enable_value_area_alerts": True,
                    "poc_proximity_percent": 0.5,  # 0.5% alerte POC
                    "value_area_break_alert": True,
                    # Opacité - Équilibrée
                    "histogram_opacity": 0.6,  # Visible
                    "value_area_opacity": 0.2
                },
                visual={"poc_color": "#FF6B35", "value_area_color": "#4ECDC4", "histogram_color": "#FECA57"}
            )
        }
    
    def get_swing_trading_config(self) -> Dict[str, IndicatorConfig]:
        """Configuration optimisée pour le swing trading"""
        return {
            # Moyennes Mobiles - Plus longues
            "sma": IndicatorConfig(
                enabled=True,
                parameters={"period": 50, "color": "#2E86C1"},
                visual={"line_width": 3, "line_style": "solid"}
            ),
            "ema": IndicatorConfig(
                enabled=True,
                parameters={"period": 21, "color": "#E74C3C"},
                visual={"line_width": 3, "line_style": "solid"}
            ),
            
            # Niveaux - Plus robustes
            "support_resistance": IndicatorConfig(
                enabled=True,
                parameters={"strength": 4, "lookback": 100},
                visual={"support_color": "#27AE60", "resistance_color": "#E74C3C", "line_width": 3, "line_style": "solid"}
            ),
            "fibonacci": IndicatorConfig(
                enabled=True,
                parameters={"swing_points": 30},
                visual={"colors": ["#F39C12", "#E67E22", "#D35400", "#C0392B", "#8E44AD"], "line_width": 2, "line_style": "solid"}
            ),
            "pivot_points": IndicatorConfig(
                enabled=True,
                parameters={"method": "fibonacci", "period": "weekly"},
                visual={"pivot_color": "#8E44AD", "resistance_colors": ["#E74C3C", "#C0392B", "#922B21"], 
                       "support_colors": ["#27AE60", "#1E8449", "#145A32"], "line_width": 2, "line_style": "solid"}
            ),
            
            # Oscillateurs - Moins sensibles
            "rsi": IndicatorConfig(
                enabled=True,
                parameters={"period": 21, "overbought": 65, "oversold": 35},
                visual={"line_color": "#8E44AD", "overbought_color": "#E74C3C", "oversold_color": "#27AE60"}
            ),
            "atr": IndicatorConfig(
                enabled=True,
                parameters={"period": 21, "multiplier": 3.0},
                visual={"line_color": "#F39C12"}
            ),
            "macd": IndicatorConfig(
                enabled=True,
                parameters={"fast": 12, "slow": 30, "signal": 12},
                visual={"macd_color": "#2196F3", "signal_color": "#FF5722", "histogram": True}
            ),
            
            # Smart Money - Fair Value Gaps (Swing Trading)
            "fvg": IndicatorConfig(
                enabled=True,
                parameters={
                    # Base - Swing Trading: Qualité prioritaire
                    "min_gap_size": 0.005,  # 0.5% minimum
                    "volume_confirmation": True,  # Confirmation volume obligatoire
                    "overlap_threshold": 0.6,  # 60% overlap pour invalidation
                    "max_distance": 200,  # Distance max en pips
                    # Détection - Strict
                    "body_rejection": 0.7,  # 70% rejection minimum
                    "wick_ratio": 0.4,  # 40% wick vs body
                    "momentum_filter": True,  # Filtrage momentum
                    "trend_alignment": True,  # Alignement tendance obligatoire
                    # Affichage - Qualité
                    "show_labels": True,  # Labels importantes
                    "show_stats": True,  # Stats importantes
                    "zones_opacity": 0.25,  # Transparence faible
                    "max_zones": 20  # Max 20 zones affichées
                },
                visual={"bullish_color": "#27AE60", "bearish_color": "#E74C3C", "opacity": 0.25}
            ),
            
            # Smart Money - Order Blocks (Swing Trading)
            "order_blocks": IndicatorConfig(
                enabled=True,
                parameters={
                    # Base - Swing: Sélectif mais réaliste pour crypto
                    "lookback_period": 25,  # Adapté au swing crypto
                    "strong_threshold": 0.4,  # Réaliste pour crypto
                    "weak_threshold": 0.2,  # Seuil faible adapté
                    "max_age_bars": 150,  # Durée de vie raisonnable
                    # Détection - Équilibrée pour crypto
                    "min_body_size": 0.002,  # 0.2% minimum
                    "volume_confirmation": False,  # Simplifié
                    "min_impulse_strength": 0.15,  # 15% impulse
                    "max_wick_ratio": 0.8,  # Plus permissif
                    "min_impulse_bars": 2,  # Minimum 2 barres
                    "max_impulse_bars": 15,  # Recherche étendue
                    "volume_multiplier": 0.7,  # 70% volume moyen
                    # Affichage - Détaillé
                    "show_labels": True,  # Labels complets
                    "show_retest_count": True,  # Historique retests
                    "opacity_active": 0.4,  # Plus visible
                    "opacity_broken": 0.2   # Visible même cassés
                },
                visual={"bullish_color": "#27AE60", "bearish_color": "#E74C3C", "opacity": 0.4}
            ),
            
            # Momentum - Squeeze Momentum (Swing Trading)
            "squeeze_momentum": IndicatorConfig(
                enabled=True,
                parameters={
                    # BB/KC - Plus longs
                    "bb_period": 30,  # Plus long
                    "bb_deviation": 2.5,  # Plus strict
                    "kc_period": 30,  # Plus long
                    "kc_atr_period": 20,  # Plus long
                    "kc_multiplier": 2.0,  # Moins sensible
                    # Momentum - Moins réactif
                    "momentum_period": 20,  # Plus long
                    "momentum_ma_period": 10,  # Plus long
                    # Alertes - Sélectives
                    "squeeze_alert": True,
                    "momentum_alert": True,
                    "min_squeeze_bars": 5  # Plus de confirmation
                },
                visual={"squeeze_color": "#FF9800", "momentum_color": "#2196F3", "line_width": 3}
            ),
            
            # Patterns - Candle Patterns (Swing Trading)
            "candle_patterns": IndicatorConfig(
                enabled=True,
                parameters={
                    # Détection - Plus stricte
                    "doji_threshold": 0.15,  # 15% body
                    "hammer_ratio": 2.5,  # 2.5x wick
                    "body_size_min": 0.03,  # 3% minimum
                    # Engulfing - Strict
                    "engulfing_body_ratio": 1.2,  # 120% engulfing
                    "engulfing_volume_confirm": True,  # Avec volume
                    # Affichage - Sélectif
                    "show_labels": True,  # Labels complets
                    "show_stats": True,
                    "max_patterns": 12  # Plus de patterns
                },
                visual={"bullish_color": "#4CAF50", "bearish_color": "#F44336", "opacity": 0.9}
            ),
            
            # Breakout - Breakout Detector (Swing Trading)
            "breakout_detector": IndicatorConfig(
                enabled=True,
                parameters={
                    # Support/Resistance - Long terme
                    "sr_period": 50,  # Plus long
                    "sr_strength": 3,  # Plus strict
                    "price_precision": 4,  # Précision
                    # Volume - Confirmation forte
                    "volume_threshold": 0.8,  # 80% volume moyen
                    "volume_ma_period": 20,  # Plus long
                    # Breakout - Confirmé
                    "breakout_threshold": 0.05,  # 5% breakout
                    "confirmation_bars": 3,  # Plus de confirmation
                    "max_age_levels": 100  # Niveaux très longs
                },
                visual={"support_color": "#00BCD4", "resistance_color": "#FF5722", "breakout_color": "#FFEB3B"}
            ),
            
            # Volume Analysis - Volume Profile (Swing Trading)
            "volume_profile": IndicatorConfig(
                enabled=True,
                parameters={
                    # Base - Swing Trading: Long terme, sélectif
                    "profile_type": "session",  # Par session
                    "bins_count": 75,  # Moins de niveaux
                    "lookback_periods": 200,  # Période longue
                    "value_area_percent": 75.0,  # Value Area plus large
                    # POC - Moins sensible
                    "poc_sensitivity": 0.8,  # Moins réactif
                    "high_volume_threshold": 85.0,  # 85% pour HVN
                    "low_volume_threshold": 15.0,  # Pas de LVN
                    "support_resistance_strength": 1.2,  # Force S/R plus forte
                    # Visualisation - Sélective
                    "show_poc": True,
                    "show_value_area": True,
                    "show_high_volume_nodes": True,
                    "show_low_volume_nodes": False,  # Pas utile swing
                    "show_volume_histogram": True,
                    # Alertes - Sélectives
                    "enable_poc_alerts": True,
                    "enable_value_area_alerts": True,
                    "poc_proximity_percent": 0.8,  # 0.8% alerte POC
                    "value_area_break_alert": True,
                    # Opacité - Modérée
                    "histogram_opacity": 0.5,  # Moins visible
                    "value_area_opacity": 0.2
                },
                visual={"poc_color": "#FF6B35", "value_area_color": "#4ECDC4", "histogram_color": "#FECA57"}
            )
        }
    
    def get_position_trading_config(self) -> Dict[str, IndicatorConfig]:
        """Configuration optimisée pour le position trading"""
        return {
            # Moyennes Mobiles - Très longues
            "sma": IndicatorConfig(
                enabled=True,
                parameters={"period": 100, "color": "#2E86C1"},
                visual={"line_width": 4, "line_style": "solid"}
            ),
            "ema": IndicatorConfig(
                enabled=True,
                parameters={"period": 50, "color": "#E74C3C"},
                visual={"line_width": 4, "line_style": "solid"}
            ),
            
            # Niveaux - Très robustes
            "support_resistance": IndicatorConfig(
                enabled=True,
                parameters={"strength": 6, "lookback": 200},
                visual={"support_color": "#27AE60", "resistance_color": "#E74C3C", "line_width": 4, "line_style": "solid"}
            ),
            "fibonacci": IndicatorConfig(
                enabled=True,
                parameters={"swing_points": 50},
                visual={"colors": ["#F39C12", "#E67E22", "#D35400", "#C0392B", "#8E44AD"], "line_width": 3, "line_style": "solid"}
            ),
            "pivot_points": IndicatorConfig(
                enabled=True,
                parameters={"method": "camarilla", "period": "monthly"},
                visual={"pivot_color": "#8E44AD", "resistance_colors": ["#E74C3C", "#C0392B", "#922B21"], 
                       "support_colors": ["#27AE60", "#1E8449", "#145A32"], "line_width": 3, "line_style": "solid"}
            ),
            
            # Oscillateurs - Très stables
            "rsi": IndicatorConfig(
                enabled=True,
                parameters={"period": 30, "overbought": 60, "oversold": 40},
                visual={"line_color": "#8E44AD", "overbought_color": "#E74C3C", "oversold_color": "#27AE60"}
            ),
            "atr": IndicatorConfig(
                enabled=True,
                parameters={"period": 30, "multiplier": 4.0},
                visual={"line_color": "#F39C12"}
            ),
            "macd": IndicatorConfig(
                enabled=True,
                parameters={"fast": 15, "slow": 35, "signal": 15},
                visual={"macd_color": "#2196F3", "signal_color": "#FF5722", "histogram": True}
            ),
            
            # Smart Money - Fair Value Gaps (Position Trading)
            "fvg": IndicatorConfig(
                enabled=True,
                parameters={
                    # Base - Position Trading: Gaps majeurs seulement
                    "min_gap_size": 0.01,  # 1% minimum (très strict)
                    "volume_confirmation": True,  # Confirmation volume obligatoire
                    "overlap_threshold": 0.5,  # 50% overlap pour invalidation
                    "max_distance": 500,  # Distance max en pips (large)
                    # Détection - Très strict
                    "body_rejection": 0.8,  # 80% rejection minimum
                    "wick_ratio": 0.3,  # 30% wick vs body
                    "momentum_filter": True,  # Filtrage momentum
                    "trend_alignment": True,  # Alignement tendance obligatoire
                    # Affichage - Minimaliste
                    "show_labels": True,  # Labels importantes
                    "show_stats": True,  # Stats importantes
                    "zones_opacity": 0.3,  # Transparence faible
                    "max_zones": 25  # Max 25 zones affichées
                },
                visual={"bullish_color": "#27AE60", "bearish_color": "#E74C3C", "opacity": 0.3}
            ),
            
            # Smart Money - Order Blocks (Position Trading)
            "order_blocks": IndicatorConfig(
                enabled=True,
                parameters={
                    # Base - Position: Sélectif mais détectable en crypto
                    "lookback_period": 40,  # Long mais raisonnable
                    "strong_threshold": 0.5,  # Élevé mais atteignable
                    "weak_threshold": 0.25,  # Seuil faible réaliste
                    "max_age_bars": 300,  # Longue durée de vie
                    # Détection - Sélective mais réaliste
                    "min_body_size": 0.003,  # 0.3% minimum
                    "volume_confirmation": False,  # Simplifié
                    "min_impulse_strength": 0.2,  # 20% impulse
                    "max_wick_ratio": 0.6,  # Sélectif mais pas impossible
                    "min_impulse_bars": 2,  # Minimum 2 barres
                    "max_impulse_bars": 20,  # Recherche longue
                    "volume_multiplier": 0.8,  # 80% volume moyen
                    # Affichage - Permanent
                    "show_labels": True,  # Toutes les infos
                    "show_retest_count": True,  # Historique complet
                    "opacity_active": 0.5,  # Très visible
                    "opacity_broken": 0.3   # Reste visible longtemps
                },
                visual={"bullish_color": "#27AE60", "bearish_color": "#E74C3C", "opacity": 0.5}
            ),
            
            # Momentum - Squeeze Momentum (Position Trading)
            "squeeze_momentum": IndicatorConfig(
                enabled=True,
                parameters={
                    # BB/KC - Très longs
                    "bb_period": 50,  # Très long
                    "bb_deviation": 3.0,  # Très strict
                    "kc_period": 50,  # Très long
                    "kc_atr_period": 30,  # Très long
                    "kc_multiplier": 2.5,  # Peu sensible
                    # Momentum - Stable
                    "momentum_period": 30,  # Très long
                    "momentum_ma_period": 15,  # Très long
                    # Alertes - Rares mais fiables
                    "squeeze_alert": True,
                    "momentum_alert": True,
                    "min_squeeze_bars": 10  # Beaucoup de confirmation
                },
                visual={"squeeze_color": "#FF9800", "momentum_color": "#2196F3", "line_width": 4}
            ),
            
            # Patterns - Candle Patterns (Position Trading)
            "candle_patterns": IndicatorConfig(
                enabled=True,
                parameters={
                    # Détection - Très stricte
                    "doji_threshold": 0.2,  # 20% body
                    "hammer_ratio": 3.0,  # 3x wick
                    "body_size_min": 0.05,  # 5% minimum
                    # Engulfing - Très strict
                    "engulfing_body_ratio": 1.5,  # 150% engulfing
                    "engulfing_volume_confirm": True,  # Volume obligatoire
                    # Affichage - Sélectif
                    "show_labels": True,  # Labels complets
                    "show_stats": True,
                    "max_patterns": 15  # Patterns majeurs
                },
                visual={"bullish_color": "#4CAF50", "bearish_color": "#F44336", "opacity": 1.0}
            ),
            
            # Breakout - Breakout Detector (Position Trading)
            "breakout_detector": IndicatorConfig(
                enabled=True,
                parameters={
                    # Support/Resistance - Très long terme
                    "sr_period": 100,  # Très long
                    "sr_strength": 4,  # Très strict
                    "price_precision": 4,  # Précision
                    # Volume - Confirmation massive
                    "volume_threshold": 1.2,  # 120% volume moyen
                    "volume_ma_period": 50,  # Très long
                    # Breakout - Majeur
                    "breakout_threshold": 0.08,  # 8% breakout
                    "confirmation_bars": 5,  # Beaucoup de confirmation
                    "max_age_levels": 200  # Niveaux historiques
                },
                visual={"support_color": "#00BCD4", "resistance_color": "#FF5722", "breakout_color": "#FFEB3B"}
            ),
            
            # Volume Analysis - Volume Profile (Position Trading)
            "volume_profile": IndicatorConfig(
                enabled=True,
                parameters={
                    # Base - Position Trading: Très long terme, ultra-sélectif
                    "profile_type": "session",  # Par session
                    "bins_count": 50,  # Peu de niveaux, major seulement
                    "lookback_periods": 500,  # Période très longue
                    "value_area_percent": 80.0,  # Value Area très large
                    # POC - Très stable
                    "poc_sensitivity": 0.5,  # Peu réactif
                    "high_volume_threshold": 90.0,  # 90% pour HVN
                    "low_volume_threshold": 10.0,  # Pas de LVN
                    "support_resistance_strength": 1.5,  # Force S/R maximale
                    # Visualisation - Majeure seulement
                    "show_poc": True,
                    "show_value_area": True,
                    "show_high_volume_nodes": True,
                    "show_low_volume_nodes": False,  # Pas utile position
                    "show_volume_histogram": True,
                    # Alertes - Rares mais importantes
                    "enable_poc_alerts": True,
                    "enable_value_area_alerts": True,
                    "poc_proximity_percent": 1.0,  # 1% alerte POC
                    "value_area_break_alert": True,
                    # Opacité - Discrète
                    "histogram_opacity": 0.4,  # Moins visible
                    "value_area_opacity": 0.15
                },
                visual={"poc_color": "#FF6B35", "value_area_color": "#4ECDC4", "histogram_color": "#FECA57"}
            )
        }
    
    def get_style_config(self, style: str) -> Dict[str, IndicatorConfig]:
        """Retourne la configuration pour un style donné"""
        configs = {
            "scalping": self.get_scalping_config,
            "day_trading": self.get_day_trading_config,
            "swing_trading": self.get_swing_trading_config,
            "position_trading": self.get_position_trading_config
        }
        
        if style in configs:
            return configs[style]()
        else:
            # Style manuel - retourne la config day trading par défaut
            return self.get_day_trading_config()
    
    def apply_style(self, style: str) -> Dict[str, Any]:
        """Applique un style et retourne la configuration complète"""
        self.current_style = style
        
        if style == "manuel":
            # Ne change rien, garde les paramètres actuels
            return {}
        
        config = self.get_style_config(style)
        
        # Convertit la configuration en format utilisable par la modal
        modal_config = {}
        for indicator, indicator_config in config.items():
            modal_config[indicator] = {
                "enabled": indicator_config.enabled,
                **indicator_config.parameters,
                **indicator_config.visual
            }
        
        return modal_config
    
    def get_style_recommendations(self, style: str) -> Dict[str, str]:
        """Retourne les recommandations d'usage pour un style"""
        recommendations = {
            "scalping": {
                "timeframe": "Utilisez des timeframes 1-5 minutes",
                "risk": "Risque faible par trade mais nombreuses positions",
                "indicators": "Indicateurs très réactifs pour signaux rapides",
                "tips": "Concentrez-vous sur les pivots et RSI pour les entrées"
            },
            "day_trading": {
                "timeframe": "Privilégiez 15min à 4h selon la volatilité",
                "risk": "Équilibrez risque et fréquence des trades",
                "indicators": "Configuration standard optimisée",
                "tips": "Combinez supports/résistances avec RSI pour confirmation"
            },
            "swing_trading": {
                "timeframe": "Analysez en 4h et 1D pour les tendances",
                "risk": "Positions tenues plusieurs jours, stops plus larges",
                "indicators": "Paramètres moins sensibles, signaux de qualité",
                "tips": "Fibonacci très utile pour les objectifs de prix"
            },
            "position_trading": {
                "timeframe": "Timeframes journaliers et hebdomadaires",
                "risk": "Risque plus élevé mais positions très sélectives",
                "indicators": "Indicateurs stables pour tendances long terme",
                "tips": "Focalisez sur les niveaux majeurs et moyennes longues"
            },
            "manuel": {
                "timeframe": "Adaptez selon votre stratégie",
                "risk": "Gérez selon vos règles de money management",
                "indicators": "Personnalisez tous les paramètres",
                "tips": "Testez vos configurations sur historique"
            }
        }
        
        return recommendations.get(style, {})


# Instance globale du gestionnaire
trading_style_manager = TradingStyleManager()