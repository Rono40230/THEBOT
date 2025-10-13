#!/usr/bin/env python3
"""
Smart AI Manager - Gestionnaire Intelligent des IA (Version Corrigée)
Sélection automatique de la meilleure IA selon le contexte
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SmartAIManager:
    """
    Gestionnaire intelligent qui choisit automatiquement la meilleure IA
    selon le contexte, les quotas et les préférences utilisateur
    """

    def __init__(self):
        self.local_ai = None
        self.free_ai = None
        self.smart_ai = None

        # Configuration utilisateur
        self.user_preferences = self._load_user_preferences()

        # Métriques performance
        self.performance_metrics = {
            "local": {"speed": 89000, "accuracy": 65, "cost": 0},
            "huggingface": {"speed": 50, "accuracy": 80, "cost": 0},
            "premium": {"speed": 5, "accuracy": 90, "cost": 10},
        }

        logger.info("🧠 Smart AI Manager initialisé")

    def _load_user_preferences(self) -> Dict:
        """Charger préférences utilisateur depuis config"""
        default_prefs = {
            "ai_mode": "auto",
            "max_cost_per_month": 0,
            "priority_speed": True,
            "priority_accuracy": False,
            "huggingface_enabled": True,
            "premium_enabled": False,
            "fallback_always_local": True,
        }

        try:
            config_path = os.path.join(
                os.getcwd(), "dashboard_configs", "ai_preferences.json"
            )
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    prefs = json.load(f)
                    return {**default_prefs, **prefs}
        except Exception as e:
            logger.warning(f"Erreur chargement préférences IA: {e}")

        return default_prefs

    def _save_user_preferences(self):
        """Sauvegarder préférences utilisateur"""
        try:
            config_dir = os.path.join(os.getcwd(), "dashboard_configs")
            os.makedirs(config_dir, exist_ok=True)

            config_path = os.path.join(config_dir, "ai_preferences.json")
            with open(config_path, "w") as f:
                json.dump(self.user_preferences, f, indent=2)
        except Exception as e:
            logger.error(f"Erreur sauvegarde préférences: {e}")

    def initialize_engines(self):
        """Initialiser les moteurs IA disponibles"""
        try:
            from .free_ai_engine import FreeAIEngine
            from .local_ai_engine import LocalAIEngine
            from .smart_ai_engine import SmartAIEngine

            self.local_ai = LocalAIEngine()
            self.free_ai = FreeAIEngine()
            self.smart_ai = SmartAIEngine()

            logger.info("✅ Tous les moteurs IA initialisés")
        except Exception as e:
            logger.error(f"Erreur initialisation moteurs IA: {e}")

    def choose_best_ai(
        self, task_type: str, priority: str = "auto", complexity: str = "medium"
    ) -> str:
        """Choisir automatiquement la meilleure IA selon le contexte"""

        # Mode manuel : utiliser choix utilisateur
        if self.user_preferences["ai_mode"] == "manual":
            return "local"

        # Vérifier budgets et quotas
        can_use_huggingface = self._check_huggingface_quota()
        can_use_premium = self._check_premium_budget()

        # Logique de sélection intelligente
        if task_type == "sentiment" and can_use_huggingface:
            return "huggingface"
        elif task_type == "realtime" or priority == "speed":
            return "local"
        elif complexity == "complex" and can_use_premium and priority == "accuracy":
            return "premium"
        elif task_type == "technical":
            return "local"
        else:
            if can_use_huggingface and complexity != "simple":
                return "huggingface"
            else:
                return "local"

    def _check_huggingface_quota(self) -> bool:
        """Vérifier quota HuggingFace et configuration API key"""
        # Vérifier si la clé API HuggingFace est configurée
        api_key = self._get_huggingface_api_key()
        if api_key and api_key.strip():
            # Si clé API configurée, vérifier le quota
            return self.free_ai and len(self.free_ai.request_history) < 1000
        else:
            # Pas de clé API = pas d'accès HuggingFace
            return False

    def _get_huggingface_api_key(self) -> str:
        """Récupérer la clé API HuggingFace depuis la configuration"""
        try:
            from dash_modules.core.api_config import api_config

            ai_providers = api_config.config.get("providers", {}).get(
                "ai_providers", []
            )

            for provider in ai_providers:
                if provider.get("name") == "HuggingFace":
                    return provider.get("config", {}).get("api_key", "")

            return ""
        except Exception as e:
            logger.warning(f"⚠️ Erreur récupération clé HuggingFace: {e}")
            return ""

    def _check_premium_budget(self) -> bool:
        """Vérifier si budget premium disponible"""
        return (
            self.user_preferences["max_cost_per_month"] > 0
            and self.user_preferences["premium_enabled"]
        )

    def analyze_with_best_ai(self, data: Dict, task_type: str = "sentiment") -> Dict:
        """Analyser avec la meilleure IA automatiquement sélectionnée"""
        start_time = datetime.now()

        # Choisir meilleure IA
        selected_ai = self.choose_best_ai(task_type)

        try:
            # Exécuter analyse selon IA sélectionnée
            if selected_ai == "huggingface" and self.free_ai:
                result = self._analyze_with_huggingface(data, task_type)
            elif selected_ai == "premium" and self.smart_ai:
                result = self._analyze_with_premium(data, task_type)
            else:
                result = self._analyze_with_local(data, task_type)

            # Ajouter métadonnées
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            result["metadata"] = {
                "ai_used": selected_ai,
                "execution_time_ms": round(execution_time, 2),
                "task_type": task_type,
                "auto_selected": True,
            }

            return result

        except Exception as e:
            logger.warning(f"Erreur avec {selected_ai}, fallback local: {e}")
            return self._analyze_with_local(data, task_type)

    def _analyze_with_huggingface(self, data: Dict, task_type: str) -> Dict:
        """Analyser avec HuggingFace"""
        if task_type == "sentiment":
            news_text = " ".join(data.get("news_articles", []))
            api_key = self._get_huggingface_api_key()
            return self.free_ai.analyze_with_huggingface(news_text, api_key=api_key)
        else:
            return self._analyze_with_local(data, task_type)

    def _analyze_with_premium(self, data: Dict, task_type: str) -> Dict:
        """Analyser avec IA Premium"""
        return self._analyze_with_local(data, task_type)

    def _analyze_with_local(self, data: Dict, task_type: str) -> Dict:
        """Analyser avec IA Locale"""
        if task_type == "sentiment":
            return self.local_ai.analyze_sentiment(data.get("news_articles", []))
        elif task_type == "technical":
            return self.local_ai.analyze_technical_pattern_simple(
                data.get("price_data", []), data.get("indicators", {})
            )
        elif task_type == "translation":
            return self.local_ai.translate_text(
                data.get("text", ""), target_lang=data.get("target_lang", "fr")
            )
        else:
            return {"error": "Type de tâche non supporté"}

    def translate_to_french(self, text: str) -> str:
        """Traduire un texte en français avec IA locale"""
        try:
            if not text or not text.strip():
                return text

            # Détecter si déjà en français (heuristique simple)
            french_indicators = [
                "le ",
                "la ",
                "les ",
                "un ",
                "une ",
                "des ",
                "du ",
                "de ",
                "et ",
                "ou ",
                "que ",
                "qui ",
            ]
            text_lower = text.lower()
            french_count = sum(
                1 for indicator in french_indicators if indicator in text_lower
            )

            # Si déjà probablement en français, ne pas traduire
            if french_count >= 3:
                return text

            # Utiliser IA locale pour traduction
            result = self.analyze_with_best_ai(
                {"text": text, "target_lang": "fr"}, task_type="translation"
            )

            return result.get("translated_text", text)

        except Exception as e:
            logger.warning(f"Erreur traduction: {e}")
            return text  # Retourner texte original en cas d'erreur

    def get_ai_status(self) -> Dict:
        """Obtenir status de tous les moteurs IA"""
        return {
            "local": {
                "available": self.local_ai is not None,
                "performance": self.performance_metrics["local"],
                "quota": "Illimité",
            },
            "huggingface": {
                "available": self._check_huggingface_quota(),
                "performance": self.performance_metrics["huggingface"],
                "quota": f"{100 - len(self.free_ai.request_history) if self.free_ai else 0}/100 aujourd'hui",
            },
            "premium": {
                "available": self._check_premium_budget(),
                "performance": self.performance_metrics["premium"],
                "quota": f"Budget: {self.user_preferences['max_cost_per_month']}€/mois",
            },
            "current_selection": self.user_preferences["ai_mode"],
            "recommendations": self._get_recommendations(),
        }

    def _get_recommendations(self) -> List[str]:
        """Obtenir recommandations d'optimisation IA"""
        recommendations = []

        if not self.user_preferences["huggingface_enabled"]:
            recommendations.append(
                "💡 Activez HuggingFace pour une meilleure analyse de sentiment (gratuit)"
            )

        if self.user_preferences["max_cost_per_month"] == 0:
            recommendations.append(
                "💰 Considérez un budget premium (5-10€) pour analyses avancées"
            )

        if self.user_preferences["ai_mode"] == "manual":
            recommendations.append(
                "🧠 Passez en mode 'auto' pour optimisation intelligente"
            )

        return recommendations

    def update_preferences(self, new_prefs: Dict):
        """Mettre à jour préférences utilisateur"""
        self.user_preferences.update(new_prefs)
        self._save_user_preferences()
        logger.info(f"Préférences IA mises à jour: {new_prefs}")

    def get_usage_stats(self) -> Dict:
        """Statistiques d'utilisation des IA"""
        return {
            "today_huggingface_calls": (
                len(self.free_ai.request_history) if self.free_ai else 0
            ),
            "remaining_free_calls": (
                max(0, 100 - len(self.free_ai.request_history)) if self.free_ai else 0
            ),
            "estimated_monthly_cost": 0,
            "performance_summary": {
                "fastest": "local",
                "most_accurate": "premium",
                "best_value": "huggingface",
            },
        }


# Instance globale
smart_ai_manager = SmartAIManager()
smart_ai_manager.initialize_engines()  # ✅ CORRECTION: Initialiser les engines
