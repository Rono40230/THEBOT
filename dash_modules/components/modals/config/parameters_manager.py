from src.thebot.core.logger import logger
"""
📊 PARAMETERS MANAGER - Gestion Unifiée Configuration
====================================================

Centralise TOUS les paramètres des indicateurs en JSON standardisé.
Remplace les multiples variables dispersées par un système unifié.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class ParametersManager:
    """Gestionnaire unifié pour tous les paramètres des indicateurs"""

    def __init__(self):
        self.config_file = Path("dashboard_configs/indicators_config.json")
        self.default_config = self._get_default_config()
        self.config = self._load_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut pour tous les indicateurs"""
        return {
            # === INDICATEURS DE BASE ===
            "basic_indicators": {
                "sma": {
                    "enabled": True,  # ✅ ACTIVÉ PAR DÉFAUT
                    "period": 20,
                    "min_value": 5,
                    "max_value": 200,
                    "color": "#2196F3",
                },
                "ema": {
                    "enabled": True,  # ✅ ACTIVÉ PAR DÉFAUT
                    "period": 12,
                    "min_value": 5,
                    "max_value": 200,
                    "color": "#FF9800",
                },
                "rsi": {
                    "enabled": True,  # ✅ ACTIVÉ PAR DÉFAUT
                    "period": 14,
                    "min_value": 2,
                    "max_value": 50,
                    "overbought": 70,
                    "oversold": 30,
                    "color": "#9C27B0",
                },
                "atr": {
                    "enabled": True,  # ✅ ACTIVÉ PAR DÉFAUT
                    "period": 14,
                    "min_value": 5,
                    "max_value": 50,
                    "multiplier": 2.0,
                    "color": "#4CAF50",
                },
                "macd": {
                    "enabled": True,  # ✅ ACTIVÉ PAR DÉFAUT
                    "fast_period": 12,
                    "slow_period": 26,
                    "signal_period": 9,
                    "color_macd": "#2196F3",
                    "color_signal": "#FF5722",
                    "color_histogram": "#FFC107",
                },
            },
            # === INDICATEURS AVANCÉS ===
            "advanced_indicators": {
                "support_resistance": {
                    "enabled": False,  # ❌ DÉSACTIVÉ PAR DÉFAUT
                    "strength": 2,
                    "lookback": 50,
                    "min_strength": 1,
                    "max_strength": 5,
                    "min_lookback": 10,
                    "max_lookback": 200,
                },
                "fibonacci": {
                    "enabled": False,  # ❌ DÉSACTIVÉ PAR DÉFAUT
                    "swing_period": 20,
                    "line_width": 1,
                    "min_swing": 5,
                    "max_swing": 100,
                    "levels": [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0],
                },
                "pivot_points": {
                    "enabled": False,  # ❌ DÉSACTIVÉ PAR DÉFAUT
                    "method": "traditional",  # traditional, fibonacci, camarilla
                    "show_r3": True,
                    "show_r2": True,
                    "show_r1": True,
                    "show_pp": True,
                    "show_s1": True,
                    "show_s2": True,
                    "show_s3": True,
                },
            },
            # === STYLES DE TRADING ===
            "trading_styles": {
                "current_style": "day_trading",  # 🎯 DAY TRADING PAR DÉFAUT
                "styles": {
                    "scalping": {
                        "timeframe": "1m",
                        "indicators": {
                            "ema": {"period": 8},
                            "rsi": {"period": 7, "overbought": 80, "oversold": 20},
                            "atr": {"period": 7, "multiplier": 1.5},
                        },
                    },
                    "day_trading": {
                        "timeframe": "15m",
                        "indicators": {
                            "sma": {"period": 20},
                            "ema": {"period": 12},
                            "rsi": {"period": 14, "overbought": 70, "oversold": 30},
                            "atr": {"period": 14, "multiplier": 2.0},
                        },
                    },
                    "swing_trading": {
                        "timeframe": "4h",
                        "indicators": {
                            "sma": {"period": 50},
                            "ema": {"period": 21},
                            "rsi": {"period": 21, "overbought": 65, "oversold": 35},
                            "atr": {"period": 21, "multiplier": 2.5},
                        },
                    },
                    "position_trading": {
                        "timeframe": "1d",
                        "indicators": {
                            "sma": {"period": 100},
                            "ema": {"period": 50},
                            "rsi": {"period": 30, "overbought": 60, "oversold": 40},
                            "atr": {"period": 30, "multiplier": 3.0},
                        },
                    },
                },
            },
        }

    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration depuis le fichier JSON"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)

                # Merge avec config par défaut pour nouveaux paramètres
                return self._merge_configs(self.default_config, config)
            else:
                # Créer le fichier avec config par défaut
                self._save_config(self.default_config)
                return self.default_config.copy()

        except Exception as e:
            logger.info(f"⚠️ Erreur loading config: {e}")
            return self.default_config.copy()

    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Fusionne la config chargée avec les valeurs par défaut"""
        result = default.copy()

        def deep_merge(base_dict, update_dict):
            for key, value in update_dict.items():
                if (
                    key in base_dict
                    and isinstance(base_dict[key], dict)
                    and isinstance(value, dict)
                ):
                    deep_merge(base_dict[key], value)
                else:
                    base_dict[key] = value

        deep_merge(result, loaded)
        return result

    def _save_config(self, config: Dict[str, Any]):
        """Sauvegarde la configuration dans le fichier JSON"""
        try:
            # Créer le dossier si nécessaire
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.info(f"⚠️ Erreur saving config: {e}")

    def get_indicator_config(self, category: str, indicator: str) -> Dict[str, Any]:
        """Récupère la configuration d'un indicateur spécifique"""
        try:
            return self.config[category][indicator].copy()
        except KeyError:
            logger.info(f"⚠️ Config not found: {category}.{indicator}")
            return {}

    def update_indicator_config(
        self, category: str, indicator: str, key: str, value: Any
    ):
        """Met à jour un paramètre spécifique d'un indicateur"""
        try:
            if category not in self.config:
                self.config[category] = {}
            if indicator not in self.config[category]:
                self.config[category][indicator] = {}

            self.config[category][indicator][key] = value
            self._save_config(self.config)

            logger.info(f"✅ Config updated: {category}.{indicator}.{key} = {value}")

        except Exception as e:
            logger.info(f"⚠️ Erreur updating config: {e}")

    def get_all_basic_indicators(self) -> Dict[str, Any]:
        """Récupère tous les indicateurs de base"""
        return self.config.get("basic_indicators", {})

    def get_all_advanced_indicators(self) -> Dict[str, Any]:
        """Récupère tous les indicateurs avancés"""
        return self.config.get("advanced_indicators", {})

    def get_current_trading_style(self) -> str:
        """Récupère le style de trading actuel"""
        return self.config.get("trading_styles", {}).get("current_style", "day_trading")

    def apply_trading_style(self, style_name: str):
        """Applique un style de trading (met à jour tous les indicateurs)"""
        try:
            styles = self.config.get("trading_styles", {}).get("styles", {})
            if style_name not in styles:
                logger.info(f"⚠️ Style non trouvé: {style_name}")
                return

            style_config = styles[style_name]

            # Mettre à jour le style actuel
            self.config["trading_styles"]["current_style"] = style_name

            # Appliquer les paramètres du style aux indicateurs
            for indicator, params in style_config.get("indicators", {}).items():
                if indicator in self.config["basic_indicators"]:
                    for key, value in params.items():
                        self.config["basic_indicators"][indicator][key] = value

            self._save_config(self.config)
            logger.info(f"✅ Style appliqué: {style_name}")

        except Exception as e:
            logger.info(f"⚠️ Erreur applying style: {e}")

    def reset_to_defaults(self):
        """Remet à zéro tous les paramètres aux valeurs par défaut"""
        self.config = self.default_config.copy()
        self._save_config(self.config)
        logger.info("✅ Configuration reset to defaults")

    def export_config(self, filepath: str):
        """Exporte la configuration actuelle vers un fichier"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Configuration exported to: {filepath}")
        except Exception as e:
            logger.info(f"⚠️ Erreur exporting config: {e}")

    def import_config(self, filepath: str):
        """Importe une configuration depuis un fichier"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                imported_config = json.load(f)

            self.config = self._merge_configs(self.default_config, imported_config)
            self._save_config(self.config)
            logger.info(f"✅ Configuration imported from: {filepath}")

        except Exception as e:
            logger.info(f"⚠️ Erreur importing config: {e}")


# Instance globale
parameters_manager = ParametersManager()
