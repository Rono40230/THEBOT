"""
State Manager - Gestionnaire d'état unifié THEBOT
Centralisation de tous les stores Dash pour une gestion cohérente de l'état
"""

import logging
from typing import Any, Dict, List, Optional

import dash
from dash import dcc, html

from ..core.theme_constants import UIColors

logger = logging.getLogger(__name__)


class StateManager:
    """
    Gestionnaire centralisé pour tous les stores d'état de l'application
    Pattern Singleton pour assurer la cohérence des données
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._stores: Dict[str, dcc.Store] = {}
        self._store_configs: Dict[str, Dict[str, Any]] = {}
        self._initialized = True

        # Configuration des stores par défaut
        self._setup_default_stores()

    def _setup_default_stores(self):
        """Configure tous les stores par défaut de l'application"""

        # Store pour les alertes de prix
        self.register_store(
            "alerts-store",
            initial_data=[],
            description="Stockage des alertes de prix configurées"
        )

        # Store pour les données temps réel
        self.register_store(
            "realtime-data-store",
            initial_data={},
            description="Données de marché en temps réel"
        )

        # Stores pour les actualités crypto
        self.register_store(
            "crypto-news-store",
            initial_data=[],
            description="Articles d'actualités crypto"
        )

        self.register_store(
            "crypto-sentiment-store",
            initial_data={},
            description="Analyse de sentiment des actualités crypto"
        )

        # Stores pour les actualités économiques
        self.register_store(
            "economic-news-store",
            initial_data=[],
            description="Articles d'actualités économiques"
        )

        self.register_store(
            "economic-sentiment-store",
            initial_data={},
            description="Analyse de sentiment des actualités économiques"
        )

        # Store pour la configuration des indicateurs
        self.register_store(
            "indicators-config-store",
            initial_data={},
            description="Configuration des indicateurs techniques"
        )

        # Store pour la configuration IA
        self.register_store(
            "ai-config-store",
            initial_data={},
            description="Configuration des moteurs IA"
        )

        # Store pour les préférences utilisateur
        self.register_store(
            "user-preferences-store",
            initial_data={},
            description="Préférences utilisateur personnalisées"
        )

        # Store pour le layout du dashboard
        self.register_store(
            "dashboard-layout-store",
            initial_data={},
            description="Configuration du layout du dashboard"
        )

    def register_store(
        self,
        store_id: str,
        initial_data: Any = None,
        description: str = "",
        storage_type: str = "memory"
    ) -> None:
        """
        Enregistre un nouveau store dans le gestionnaire d'état

        Args:
            store_id: Identifiant unique du store
            initial_data: Données initiales du store
            description: Description du store pour la documentation
            storage_type: Type de stockage ('memory', 'local', 'session')
        """
        if store_id in self._stores:
            logger.warning(f"Store {store_id} déjà enregistré, remplacement...")

        # Créer le composant dcc.Store
        store = dcc.Store(
            id=store_id,
            data=initial_data,
            storage_type=storage_type
        )

        # Stocker la configuration
        self._store_configs[store_id] = {
            "description": description,
            "initial_data": initial_data,
            "storage_type": storage_type,
            "component": store
        }

        self._stores[store_id] = store
        logger.debug(f"Store {store_id} enregistré: {description}")

    def get_store(self, store_id: str) -> Optional[dcc.Store]:
        """Récupère un store par son ID"""
        return self._stores.get(store_id)

    def get_store_component(self, store_id: str) -> Optional[dcc.Store]:
        """Alias pour get_store - retourne le composant Dash"""
        return self.get_store(store_id)

    def get_all_stores(self) -> List[dcc.Store]:
        """Retourne tous les stores enregistrés"""
        return list(self._stores.values())

    def get_store_data(self, store_id: str) -> Any:
        """Récupère les données actuelles d'un store"""
        config = self._store_configs.get(store_id)
        return config.get("initial_data") if config else None

    def update_store_data(self, store_id: str, data: Any) -> bool:
        """
        Met à jour les données d'un store (utilisé principalement pour les tests)

        Note: En production, les données sont mises à jour via les callbacks Dash
        """
        if store_id not in self._store_configs:
            logger.error(f"Store {store_id} non trouvé")
            return False

        self._store_configs[store_id]["initial_data"] = data
        logger.debug(f"Données du store {store_id} mises à jour")
        return True

    def get_stores_info(self) -> Dict[str, Dict[str, Any]]:
        """Retourne les informations sur tous les stores (pour debugging)"""
        return {
            store_id: {
                "description": config["description"],
                "storage_type": config["storage_type"],
                "has_data": config["initial_data"] is not None
            }
            for store_id, config in self._store_configs.items()
        }

    def create_hidden_stores_container(self) -> html.Div:
        """
        Crée un conteneur caché contenant tous les stores
        À intégrer dans le layout principal de l'application
        """
        stores = self.get_all_stores()

        return html.Div(
            stores,
            style={"display": "none"},  # Stores cachés
            id="global-state-container"
        )

    def reset_store(self, store_id: str) -> bool:
        """Remet un store à ses données initiales"""
        if store_id not in self._store_configs:
            return False

        config = self._store_configs[store_id]
        initial_data = config.get("initial_data")
        return self.update_store_data(store_id, initial_data)


# Instance globale du gestionnaire d'état
global_state_manager = StateManager()


def get_global_state_manager() -> StateManager:
    """Retourne l'instance globale du gestionnaire d'état"""
    return global_state_manager


def get_store(store_id: str) -> Optional[dcc.Store]:
    """Fonction utilitaire pour récupérer un store rapidement"""
    return global_state_manager.get_store(store_id)


def get_all_stores() -> List[dcc.Store]:
    """Fonction utilitaire pour récupérer tous les stores"""
    return global_state_manager.get_all_stores()</content>
<parameter name="filePath">/home/rono/THEBOT/dash_modules/core/state_manager.py