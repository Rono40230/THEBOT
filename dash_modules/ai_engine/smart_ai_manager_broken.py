#!/usr/bin/env python3
"""
Smart AI Manager - Gestionnaire Intelligent des IA
Sélection automatique de la meilleure IA selon le contexte
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import os

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
            'local': {'speed': 89000, 'accuracy': 65, 'cost': 0},
            'huggingface': {'speed': 50, 'accuracy': 80, 'cost': 0},
            'premium': {'speed': 5, 'accuracy': 90, 'cost': 10}
        }
        
        logger.info("🧠 Smart AI Manager initialisé")
    
    def _load_user_preferences(self) -> Dict:
        """Charger préférences utilisateur depuis config"""
        default_prefs = {
            'ai_mode': 'auto',  # auto, manual, hybrid
            'max_cost_per_month': 0,  # Budget mensuel IA
            'priority_speed': True,   # Privilégier vitesse
            'priority_accuracy': False,  # Privilégier précision
            'huggingface_enabled': True,
            'premium_enabled': False,
            'fallback_always_local': True
        }
        
        try:
            config_path = os.path.join(os.getcwd(), 'dashboard_configs', 'ai_preferences.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    prefs = json.load(f)
                    return {**default_prefs, **prefs}
        except Exception as e:
            logger.warning(f"Erreur chargement préférences IA: {e}")
        
        return default_prefs
    
    def _save_user_preferences(self):
        """Sauvegarder préférences utilisateur"""
        try:
            config_dir = os.path.join(os.getcwd(), 'dashboard_configs')
            os.makedirs(config_dir, exist_ok=True)
            
            config_path = os.path.join(config_dir, 'ai_preferences.json')
            with open(config_path, 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
        except Exception as e:
            logger.error(f"Erreur sauvegarde préférences: {e}")
    
    def initialize_engines(self):
        """Initialiser les moteurs IA disponibles"""
        try:
            from .local_ai_engine import LocalAIEngine
            from .free_ai_engine import FreeAIEngine
            from .smart_ai_engine import SmartAIEngine
            
            self.local_ai = LocalAIEngine()
            self.free_ai = FreeAIEngine()
            self.smart_ai = SmartAIEngine()
            
            logger.info("✅ Tous les moteurs IA initialisés")
        except Exception as e:
            logger.error(f"Erreur initialisation moteurs IA: {e}")
    
    def choose_best_ai(self, task_type: str, priority: str = "auto", complexity: str = "medium") -> str:
        """
        Choisir automatiquement la meilleure IA selon le contexte
        
        Args:
            task_type: 'sentiment', 'technical', 'trading', 'realtime'
            priority: 'speed', 'accuracy', 'cost', 'auto'
            complexity: 'simple', 'medium', 'complex'
        
        Returns:
            str: 'local', 'huggingface', 'premium'
        """
        
        # Mode manuel : utiliser choix utilisateur
        if self.user_preferences['ai_mode'] == 'manual':
            return 'local'  # Valeur par défaut
        
        # Vérifier budgets et quotas
        can_use_huggingface = self._check_huggingface_quota()
        can_use_premium = self._check_premium_budget()
        
        # Logique de sélection intelligente
        if task_type == "sentiment" and can_use_huggingface:
            # HuggingFace excelle en sentiment
            return "huggingface"
        
        elif task_type == "realtime" or priority == "speed":
            # Local imbattable en vitesse
            return "local"
        
        elif complexity == "complex" and can_use_premium and priority == "accuracy":
            # Premium pour analyses complexes
            return "premium"
        
        elif task_type == "technical":
            # Local optimal pour technique
            return "local"
        
        else:
            # Fallback intelligent
            if can_use_huggingface and complexity != "simple":
                return "huggingface"
            else:
                return "local"
    
    def _check_huggingface_quota(self) -> bool:
        """Vérifier si quota HuggingFace disponible"""
        if not self.free_ai:
            return False
        
        return self.free_ai._check_rate_limit()
    
    def _check_premium_budget(self) -> bool:
        """Vérifier si budget premium disponible"""
        return self.user_preferences['max_cost_per_month'] > 0 and self.user_preferences['premium_enabled']
    
    def analyze_with_best_ai(self, data: Dict, task_type: str = "sentiment") -> Dict:
        """
        Analyser avec la meilleure IA automatiquement sélectionnée
        """
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
            result['metadata'] = {
                'ai_used': selected_ai,
                'execution_time_ms': round(execution_time, 2),
                'task_type': task_type,
                'auto_selected': True
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"Erreur avec {selected_ai}, fallback local: {e}")
            # Fallback vers local en cas d'erreur
            return self._analyze_with_local(data, task_type)\n    \n    def _analyze_with_huggingface(self, data: Dict, task_type: str) -> Dict:\n        \"\"\"Analyser avec HuggingFace\"\"\"\n        if task_type == \"sentiment\":\n            news_text = \" \".join(data.get('news_articles', []))\n            return self.free_ai.analyze_with_huggingface(news_text)\n        else:\n            # Fallback local pour autres tâches\n            return self._analyze_with_local(data, task_type)\n    \n    def _analyze_with_premium(self, data: Dict, task_type: str) -> Dict:\n        \"\"\"Analyser avec IA Premium\"\"\"\n        # TODO: Implémenter quand Smart AI sera configurée\n        return self._analyze_with_local(data, task_type)\n    \n    def _analyze_with_local(self, data: Dict, task_type: str) -> Dict:\n        \"\"\"Analyser avec IA Locale\"\"\"\n        if task_type == \"sentiment\":\n            return self.local_ai.analyze_sentiment(data.get('news_articles', []))\n        elif task_type == \"technical\":\n            return self.local_ai.analyze_technical_pattern_simple(\n                data.get('price_data', []), \n                data.get('indicators', {})\n            )\n        else:\n            return {'error': 'Type de tâche non supporté'}\n    \n    def get_ai_status(self) -> Dict:\n        \"\"\"Obtenir status de tous les moteurs IA\"\"\"\n        return {\n            'local': {\n                'available': self.local_ai is not None,\n                'performance': self.performance_metrics['local'],\n                'quota': 'Illimité'\n            },\n            'huggingface': {\n                'available': self._check_huggingface_quota(),\n                'performance': self.performance_metrics['huggingface'],\n                'quota': f\"{100 - len(self.free_ai.request_history) if self.free_ai else 0}/100 aujourd'hui\"\n            },\n            'premium': {\n                'available': self._check_premium_budget(),\n                'performance': self.performance_metrics['premium'],\n                'quota': f\"Budget: {self.user_preferences['max_cost_per_month']}€/mois\"\n            },\n            'current_selection': self.user_preferences['ai_mode'],\n            'recommendations': self._get_recommendations()\n        }\n    \n    def _get_recommendations(self) -> List[str]:\n        \"\"\"Obtenir recommandations d'optimisation IA\"\"\"\n        recommendations = []\n        \n        if not self.user_preferences['huggingface_enabled']:\n            recommendations.append(\"💡 Activez HuggingFace pour une meilleure analyse de sentiment (gratuit)\")\n        \n        if self.user_preferences['max_cost_per_month'] == 0:\n            recommendations.append(\"💰 Considérez un budget premium (5-10€) pour analyses avancées\")\n        \n        if self.user_preferences['ai_mode'] == 'manual':\n            recommendations.append(\"🧠 Passez en mode 'auto' pour optimisation intelligente\")\n        \n        return recommendations\n    \n    def update_preferences(self, new_prefs: Dict):\n        \"\"\"Mettre à jour préférences utilisateur\"\"\"\n        self.user_preferences.update(new_prefs)\n        self._save_user_preferences()\n        logger.info(f\"Préférences IA mises à jour: {new_prefs}\")\n    \n    def get_usage_stats(self) -> Dict:\n        \"\"\"Statistiques d'utilisation des IA\"\"\"\n        return {\n            'today_huggingface_calls': len(self.free_ai.request_history) if self.free_ai else 0,\n            'remaining_free_calls': max(0, 100 - len(self.free_ai.request_history)) if self.free_ai else 0,\n            'estimated_monthly_cost': 0,  # Calculé selon usage premium\n            'performance_summary': {\n                'fastest': 'local',\n                'most_accurate': 'premium',\n                'best_value': 'huggingface'\n            }\n        }\n\n# Instance globale\nsmart_ai_manager = SmartAIManager()