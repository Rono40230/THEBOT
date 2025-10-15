"""
Dependency Injection Container - Conteneur d'injection de dépendances THEBOT
Système d'injection automatique pour découpler les composants et faciliter les tests
"""

import logging
from typing import Any, Callable, Dict, Optional, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')


class DependencyContainer:
    """
    Conteneur d'injection de dépendances simple et léger
    Pattern Singleton pour assurer la cohérence des dépendances
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DependencyContainer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, Any] = {}
        self._initialized = True

        # Enregistrer les dépendances par défaut
        self._register_default_dependencies()

    def _register_default_dependencies(self):
        """Enregistre les dépendances par défaut de l'application"""

        # Services métier (lazy loading)
        from ..services import (
            AlertService, MarketDataService, NewsService,
            UserPreferencesService, DashboardService
        )

        self.register_lazy_singleton("alert_service", AlertService)
        self.register_lazy_singleton("market_data_service", MarketDataService)
        self.register_lazy_singleton("news_service", NewsService)
        self.register_lazy_singleton("user_preferences_service", UserPreferencesService)
        self.register_lazy_singleton("dashboard_service", DashboardService)

        # Providers (lazy loading)
        from ..data_providers.provider_manager import ProviderManager
        self.register_lazy_singleton("provider_manager", ProviderManager)

        # Cache intelligent
        from .intelligent_cache import get_global_cache
        self.register_singleton("cache", get_global_cache())

        # State manager
        from .state_manager import get_global_state_manager
        self.register_singleton("state_manager", get_global_state_manager())

        logger.debug("Dépendances par défaut enregistrées")

    def register_singleton(self, name: str, instance: Any) -> None:
        """
        Enregistre une instance singleton (même instance retournée à chaque résolution)
        """
        self._services[name] = instance
        logger.debug(f"Singleton enregistré: {name}")

    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        """
        Enregistre une factory (nouvelle instance créée à chaque résolution)
        """
        self._factories[name] = factory
        logger.debug(f"Factory enregistrée: {name}")

    def register_lazy_singleton(self, name: str, cls: Type[T], *args, **kwargs) -> None:
        """
        Enregistre un singleton lazy (instance créée seulement au premier accès)
        """
        def factory():
            if name not in self._singletons:
                self._singletons[name] = cls(*args, **kwargs)
            return self._singletons[name]

        self._factories[name] = factory
        logger.debug(f"Lazy singleton enregistré: {name}")

    def resolve(self, name: str) -> Any:
        """
        Résout une dépendance par son nom
        """
        # Vérifier d'abord les singletons
        if name in self._services:
            return self._services[name]

        # Vérifier les factories
        if name in self._factories:
            return self._factories[name]()

        raise ValueError(f"Dépendance non trouvée: {name}")

    def has_dependency(self, name: str) -> bool:
        """Vérifie si une dépendance est enregistrée"""
        return name in self._services or name in self._factories

    def clear(self) -> None:
        """Vide le conteneur (principalement pour les tests)"""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        logger.debug("Conteneur d'injection vidé")

    def get_registered_dependencies(self) -> Dict[str, str]:
        """Retourne la liste des dépendances enregistrées (pour debugging)"""
        result = {}

        for name in self._services:
            result[name] = "singleton"

        for name in self._factories:
            if name in self._singletons:
                result[name] = "lazy_singleton"
            else:
                result[name] = "factory"

        return result


# Instance globale du conteneur
global_container = DependencyContainer()


def get_global_container() -> DependencyContainer:
    """Retourne l'instance globale du conteneur d'injection"""
    return global_container


def inject(name: str) -> Any:
    """Fonction utilitaire pour injecter une dépendance rapidement"""
    return global_container.resolve(name)


def register_dependency(name: str, instance: Any = None, factory: Callable = None, lazy_singleton: Type = None) -> None:
    """
    Fonction utilitaire pour enregistrer une dépendance
    """
    if instance is not None:
        global_container.register_singleton(name, instance)
    elif factory is not None:
        global_container.register_factory(name, factory)
    elif lazy_singleton is not None:
        global_container.register_lazy_singleton(name, lazy_singleton)
    else:
        raise ValueError("Doit spécifier instance, factory, ou lazy_singleton")


# Décorateur pour injection automatique
def inject_dependencies(*dependency_names: str):
    """
    Décorateur pour injecter automatiquement des dépendances dans une classe
    """
    def decorator(cls):
        original_init = cls.__init__

        def new_init(self, *args, **kwargs):
            # Injecter les dépendances
            for dep_name in dependency_names:
                if not hasattr(self, dep_name):
                    setattr(self, dep_name, inject(dep_name))

            # Appeler l'init original
            original_init(self, *args, **kwargs)

        cls.__init__ = new_init
        return cls

    return decorator</content>
<parameter name="filePath">/home/rono/THEBOT/dash_modules/core/dependency_container.py