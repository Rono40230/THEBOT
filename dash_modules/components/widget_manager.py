from src.thebot.core.logger import logger
"""
Widget Manager - Phase 3 THEBOT
Gestionnaire des widgets du dashboard avec persistence et personnalisation
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class WidgetManager:
    """
    Gestionnaire des widgets du dashboard avec sauvegarde et restauration
    """

    def __init__(self, config_dir: str = "dashboard_configs"):
        self.config_dir = config_dir
        self.ensure_config_dir()

        # Configuration par défaut des widgets
        self.default_widgets = {
            "market_overview": {
                "enabled": True,
                "position": {"x": 0, "y": 0, "w": 12, "h": 6},
                "settings": {
                    "auto_refresh": True,
                    "refresh_interval": 30,
                    "show_percentage": True,
                },
            },
            "news_feed": {
                "enabled": True,
                "position": {"x": 0, "y": 6, "w": 6, "h": 8},
                "settings": {
                    "auto_refresh": True,
                    "refresh_interval": 60,
                    "categories": ["crypto", "economic", "market"],
                    "max_articles": 10,
                },
            },
            "price_charts": {
                "enabled": True,
                "position": {"x": 6, "y": 6, "w": 6, "h": 8},
                "settings": {
                    "default_symbol": "BTCUSDT",
                    "default_timeframe": "1h",
                    "show_volume": True,
                    "show_indicators": False,
                },
            },
            "alerts": {
                "enabled": True,
                "position": {"x": 0, "y": 14, "w": 12, "h": 4},
                "settings": {
                    "sound_enabled": True,
                    "popup_enabled": True,
                    "email_enabled": False,
                },
            },
        }

        # Layouts prédéfinis
        self.predefined_layouts = {
            "default": {
                "name": "Layout par défaut",
                "description": "Configuration équilibrée pour tous usages",
                "widgets": self.default_widgets,
            },
            "trading": {
                "name": "Focus Trading",
                "description": "Optimisé pour le trading actif",
                "widgets": {
                    "price_charts": {
                        "enabled": True,
                        "position": {"x": 0, "y": 0, "w": 8, "h": 10},
                        "settings": {
                            "default_symbol": "BTCUSDT",
                            "default_timeframe": "15m",
                            "show_volume": True,
                            "show_indicators": True,
                        },
                    },
                    "market_overview": {
                        "enabled": True,
                        "position": {"x": 8, "y": 0, "w": 4, "h": 6},
                        "settings": {
                            "auto_refresh": True,
                            "refresh_interval": 15,
                            "show_percentage": True,
                        },
                    },
                    "alerts": {
                        "enabled": True,
                        "position": {"x": 8, "y": 6, "w": 4, "h": 4},
                        "settings": {"sound_enabled": True, "popup_enabled": True},
                    },
                    "news_feed": {
                        "enabled": True,
                        "position": {"x": 0, "y": 10, "w": 12, "h": 4},
                        "settings": {"categories": ["crypto"], "max_articles": 5},
                    },
                },
            },
            "news": {
                "name": "Focus News",
                "description": "Optimisé pour le suivi des actualités",
                "widgets": {
                    "news_feed": {
                        "enabled": True,
                        "position": {"x": 0, "y": 0, "w": 8, "h": 12},
                        "settings": {
                            "auto_refresh": True,
                            "refresh_interval": 30,
                            "categories": ["crypto", "economic", "market"],
                            "max_articles": 20,
                        },
                    },
                    "market_overview": {
                        "enabled": True,
                        "position": {"x": 8, "y": 0, "w": 4, "h": 6},
                        "settings": {"auto_refresh": True, "refresh_interval": 60},
                    },
                    "price_charts": {
                        "enabled": True,
                        "position": {"x": 8, "y": 6, "w": 4, "h": 6},
                        "settings": {"default_timeframe": "1d", "show_volume": False},
                    },
                },
            },
            "mobile": {
                "name": "Vue Mobile",
                "description": "Optimisé pour les écrans mobiles",
                "widgets": {
                    "market_overview": {
                        "enabled": True,
                        "position": {"x": 0, "y": 0, "w": 12, "h": 4},
                        "settings": {"refresh_interval": 30},
                    },
                    "price_charts": {
                        "enabled": True,
                        "position": {"x": 0, "y": 4, "w": 12, "h": 6},
                        "settings": {"default_timeframe": "1h"},
                    },
                    "news_feed": {
                        "enabled": True,
                        "position": {"x": 0, "y": 10, "w": 12, "h": 6},
                        "settings": {"max_articles": 5, "categories": ["crypto"]},
                    },
                },
            },
        }

    def ensure_config_dir(self):
        """Assure que le répertoire de configuration existe"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            logger.info(f"📁 Répertoire configuration créé: {self.config_dir}")

    def save_layout(
        self, layout_name: str, widgets_config: Dict, user_id: str = "default"
    ) -> bool:
        """Sauvegarde un layout personnalisé"""
        try:
            layout_data = {
                "name": layout_name,
                "created_at": datetime.now().isoformat(),
                "user_id": user_id,
                "widgets": widgets_config,
                "metadata": {"version": "3.0", "auto_generated": False},
            }

            filename = f"{user_id}_{layout_name}.json"
            filepath = os.path.join(self.config_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(layout_data, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Layout sauvegardé: {layout_name} pour {user_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde layout {layout_name}: {e}")
            return False

    def load_layout(self, layout_name: str, user_id: str = "default") -> Optional[Dict]:
        """Charge un layout sauvegardé"""
        try:
            # Vérifier layouts prédéfinis d'abord
            if layout_name in self.predefined_layouts:
                logger.info(f"📖 Layout prédéfini chargé: {layout_name}")
                return self.predefined_layouts[layout_name]["widgets"]

            # Chercher dans les layouts personnalisés
            filename = f"{user_id}_{layout_name}.json"
            filepath = os.path.join(self.config_dir, filename)

            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    layout_data = json.load(f)

                logger.info(f"📖 Layout personnalisé chargé: {layout_name}")
                return layout_data.get("widgets", self.default_widgets)

            logger.warning(
                f"⚠️ Layout non trouvé: {layout_name}, utilisation par défaut"
            )
            return self.default_widgets

        except Exception as e:
            logger.error(f"❌ Erreur chargement layout {layout_name}: {e}")
            return self.default_widgets

    def get_available_layouts(self, user_id: str = "default") -> List[Dict]:
        """Retourne la liste des layouts disponibles"""
        layouts = []

        # Ajouter layouts prédéfinis
        for layout_id, layout_info in self.predefined_layouts.items():
            layouts.append(
                {
                    "id": layout_id,
                    "name": layout_info["name"],
                    "description": layout_info["description"],
                    "type": "predefined",
                    "editable": False,
                }
            )

        # Ajouter layouts personnalisés
        try:
            for filename in os.listdir(self.config_dir):
                if filename.startswith(f"{user_id}_") and filename.endswith(".json"):
                    filepath = os.path.join(self.config_dir, filename)

                    with open(filepath, "r", encoding="utf-8") as f:
                        layout_data = json.load(f)

                    layout_id = filename.replace(f"{user_id}_", "").replace(".json", "")
                    layouts.append(
                        {
                            "id": layout_id,
                            "name": layout_data.get("name", layout_id),
                            "description": f"Layout personnalisé créé le {layout_data.get('created_at', 'N/A')[:10]}",
                            "type": "custom",
                            "editable": True,
                        }
                    )

        except Exception as e:
            logger.error(f"❌ Erreur listage layouts: {e}")

        return layouts

    def delete_layout(self, layout_name: str, user_id: str = "default") -> bool:
        """Supprime un layout personnalisé"""
        try:
            filename = f"{user_id}_{layout_name}.json"
            filepath = os.path.join(self.config_dir, filename)

            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"🗑️ Layout supprimé: {layout_name}")
                return True
            else:
                logger.warning(f"⚠️ Layout non trouvé pour suppression: {layout_name}")
                return False

        except Exception as e:
            logger.error(f"❌ Erreur suppression layout {layout_name}: {e}")
            return False

    def get_widget_settings(
        self, widget_id: str, layout_name: str = "default", user_id: str = "default"
    ) -> Dict:
        """Récupère les paramètres d'un widget spécifique"""
        layout = self.load_layout(layout_name, user_id)

        if widget_id in layout:
            return layout[widget_id].get("settings", {})

        # Fallback vers les paramètres par défaut
        if widget_id in self.default_widgets:
            return self.default_widgets[widget_id].get("settings", {})

        return {}

    def update_widget_settings(
        self,
        widget_id: str,
        new_settings: Dict,
        layout_name: str = "default",
        user_id: str = "default",
    ) -> bool:
        """Met à jour les paramètres d'un widget"""
        try:
            layout = self.load_layout(layout_name, user_id)

            if widget_id in layout:
                layout[widget_id]["settings"].update(new_settings)
                return self.save_layout(layout_name, layout, user_id)

            logger.warning(f"⚠️ Widget {widget_id} non trouvé dans layout {layout_name}")
            return False

        except Exception as e:
            logger.error(f"❌ Erreur mise à jour widget {widget_id}: {e}")
            return False

    def validate_layout(self, widgets_config: Dict) -> Dict:
        """Valide et corrige un layout si nécessaire"""
        validated = {}

        for widget_id, config in widgets_config.items():
            # Vérifier structure minimale
            if isinstance(config, dict):
                validated_widget = {
                    "enabled": config.get("enabled", True),
                    "position": config.get(
                        "position", {"x": 0, "y": 0, "w": 6, "h": 4}
                    ),
                    "settings": config.get("settings", {}),
                }

                # Valider position
                pos = validated_widget["position"]
                pos["x"] = max(0, min(pos.get("x", 0), 11))  # 0-11
                pos["y"] = max(0, pos.get("y", 0))
                pos["w"] = max(1, min(pos.get("w", 6), 12))  # 1-12
                pos["h"] = max(1, pos.get("h", 4))

                # Vérifier que le widget ne dépasse pas
                if pos["x"] + pos["w"] > 12:
                    pos["w"] = 12 - pos["x"]

                validated[widget_id] = validated_widget

        return validated

    def export_layout(
        self, layout_name: str, user_id: str = "default"
    ) -> Optional[str]:
        """Exporte un layout au format JSON"""
        try:
            layout = self.load_layout(layout_name, user_id)

            export_data = {
                "layout_name": layout_name,
                "exported_at": datetime.now().isoformat(),
                "version": "3.0",
                "widgets": layout,
            }

            return json.dumps(export_data, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"❌ Erreur export layout {layout_name}: {e}")
            return None

    def import_layout(
        self, layout_json: str, new_name: str, user_id: str = "default"
    ) -> bool:
        """Importe un layout depuis JSON"""
        try:
            layout_data = json.loads(layout_json)

            if "widgets" in layout_data:
                validated_widgets = self.validate_layout(layout_data["widgets"])
                return self.save_layout(new_name, validated_widgets, user_id)

            logger.error("❌ Format JSON invalide: clé 'widgets' manquante")
            return False

        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur parsing JSON: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur import layout: {e}")
            return False


# Instance globale
widget_manager = WidgetManager()
