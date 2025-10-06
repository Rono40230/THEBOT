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