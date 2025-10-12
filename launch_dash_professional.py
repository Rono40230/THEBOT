"""
THEBOT Launcher - Architecture MVC Ultra-Léger
Point d'entrée principal de l'application THEBOT conforme .clinerules
"""

import dash
import dash_bootstrap_components as dbc
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

# Imports des modules MVC
from dash_modules.core.base_module import BaseModule
from dash_modules.core.data_manager import data_manager, DataManager
from dash_modules.core.layout_manager import layout_manager, LayoutManager
from dash_modules.core.launcher_callbacks import LauncherCallbacks

# Import des modules métier
from dash_modules.tabs.crypto_module import CryptoModule
from dash_modules.tabs.forex_module import ForexModule
from dash_modules.tabs.stocks_module import StocksModule
from dash_modules.tabs.economic_news_module import EconomicNewsModule
from dash_modules.tabs.crypto_news_module import CryptoNewsModule
from dash_modules.tabs.announcements_calendar import AnnouncementsCalendarModule
from dash_modules.tabs.strategies_module import StrategiesModule

# Import style trading manager
from dash_modules.core.style_trading import trading_style_manager

# Import calculateurs THEBOT
from dash_modules.core.calculators import TechnicalCalculators

# Instance partagée des calculateurs
shared_calculators = TechnicalCalculators()

# Configuration du logging conforme .clinerules
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class THEBOTApp:
    """
    Application THEBOT avec architecture MVC ultra-moderne
    
    Responsabilités selon .clinerules :
    - Single Responsibility : Orchestration uniquement
    - Type hints obligatoires
    - Logging structuré
    - Architecture MVC stricte
    """
    
    def __init__(self, debug: bool = False, port: int = 8050) -> None:
        """
        Initialise l'application THEBOT
        
        Args:
            debug: Mode debug Dash
            port: Port d'écoute
        """
        self.debug = debug
        self.port = port
        self.current_tab = "economic_news"
        
        # Configuration Dash
        self.app = self._create_dash_app()
        
        # Managers MVC
        self.data_manager = data_manager
        self.layout_manager = layout_manager
        
        # Modules métier
        self.modules: Dict[str, BaseModule] = {}
        
        # Callbacks handler
        self.callbacks_handler: Optional[LauncherCallbacks] = None
        
        logger.info("🚀 THEBOTApp initialisé")
        
        # Initialisation complète
        self._initialize()
    
    def _create_dash_app(self) -> dash.Dash:
        """
        Crée l'instance Dash avec configuration optimale
        
        Returns:
            dash.Dash: Application Dash configurée
        """
        try:
            app = dash.Dash(
                __name__,
                external_stylesheets=[
                    dbc.themes.CYBORG,  # Thème dark moderne
                    dbc.icons.FONT_AWESOME,  # Icônes
                    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
                ],
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"},
                    {"name": "description", "content": "THEBOT - Trading Intelligence Platform"},
                    {"name": "theme-color", "content": "#212529"}
                ],
                suppress_callback_exceptions=True,
                update_title=None  # Pas de "Updating..." dans le titre
            )
            
            app.title = "THEBOT - Trading Intelligence Platform"
            logger.info("✅ Application Dash créée")
            return app
            
        except Exception as e:
            logger.error(f"❌ Erreur création Dash: {e}")
            raise
    
    def _initialize(self) -> None:
        """Initialise tous les composants de l'application"""
        try:
            self._init_modules()
            self._setup_layout()
            self._setup_callbacks()
            logger.info("✅ Application THEBOT initialisée")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation: {e}")
            raise
    
    def _init_modules(self) -> None:
        """Initialise tous les modules métier"""
        try:
            logger.info("🔄 Initialisation des modules...")
            
            # Modules avec calculateurs partagés
            self.modules = {
                'crypto': CryptoModule(),
                'forex': ForexModule(calculators=shared_calculators),
                'stocks': StocksModule(calculators=shared_calculators),
                'economic_news': EconomicNewsModule(calculators=shared_calculators),
                'crypto_news': CryptoNewsModule(calculators=shared_calculators),
                'announcements_calendar': AnnouncementsCalendarModule(calculators=shared_calculators),
                'strategies': StrategiesModule(calculators=shared_calculators)
            }
            
            # Configuration des callbacks pour chaque module
            for module_name, module in self.modules.items():
                if hasattr(module, 'setup_callbacks'):
                    try:
                        module.setup_callbacks(self.app)
                        logger.info(f"✅ Callbacks {module_name} configurés")
                    except Exception as e:
                        logger.error(f"❌ Erreur callbacks {module_name}: {e}")
            
            logger.info(f"✅ {len(self.modules)} modules initialisés")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation modules: {e}")
            raise
    
    def _setup_layout(self) -> None:
        """Configure le layout principal via LayoutManager"""
        try:
            # Récupérer les données par défaut
            all_symbols = self.data_manager.get_all_binance_symbols()
            default_data = self._get_default_data()
            
            # Créer le layout via le LayoutManager avec les modules
            self.app.layout = self.layout_manager.get_main_layout(all_symbols, default_data, self.modules)
            
            logger.info("✅ Layout configuré via LayoutManager")
            
        except Exception as e:
            logger.error(f"❌ Erreur setup layout: {e}")
            raise
    
    def _setup_callbacks(self) -> None:
        """Configure les callbacks via LauncherCallbacks"""
        try:
            self.callbacks_handler = LauncherCallbacks(
                app=self.app,
                modules=self.modules,
                layout_manager=self.layout_manager,
                data_manager=self.data_manager
            )
            
            self.callbacks_handler.register_all_callbacks()
            logger.info("✅ Callbacks configurés via LauncherCallbacks")
            
        except Exception as e:
            logger.error(f"❌ Erreur setup callbacks: {e}")
            raise
    
    def _get_default_data(self) -> Dict[str, Any]:
        """
        Retourne les données par défaut pour l'application
        
        Returns:
            Dict: Données par défaut
        """
        try:
            # Charger données par défaut BTCUSDT
            default_symbol = 'BTCUSDT'
            df = self.data_manager.load_symbol_data(default_symbol)
            
            if df is not None and not df.empty:
                return {
                    'market_data': {
                        'symbol': default_symbol,
                        'data': df.to_json(date_format='iso'),
                        'timestamp': datetime.now().isoformat()
                    },
                    'settings': {
                        'default_symbol': default_symbol,
                        'default_timeframe': '1h',
                        'theme': 'dark',
                        'risk_profile': 'moderate'
                    }
                }
            
            return {
                'market_data': {},
                'settings': {
                    'default_symbol': 'BTCUSDT',
                    'default_timeframe': '1h',
                    'theme': 'dark',
                    'risk_profile': 'moderate'
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur données par défaut: {e}")
            return {'market_data': {}, 'settings': {}}
    
    def get_module_info(self) -> Dict[str, Any]:
        """
        Retourne les informations des modules
        
        Returns:
            Dict: Informations détaillées de tous les modules
        """
        info = {
            'total_modules': len(self.modules),
            'modules': {}
        }
        
        for name, module in self.modules.items():
            if hasattr(module, 'get_module_info'):
                info['modules'][name] = module.get_module_info()
            else:
                info['modules'][name] = {
                    'name': name,
                    'class': module.__class__.__name__,
                    'initialized': True
                }
        
        return info
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Retourne les informations du cache
        
        Returns:
            Dict: Informations du cache de données
        """
        return self.data_manager.get_cache_info()
    
    def clear_cache(self) -> None:
        """Vide le cache de données"""
        self.data_manager.clear_cache()
        logger.info("🗑️ Cache vidé")
    
    def run(self, host: str = '0.0.0.0') -> None:
        """
        Lance l'application THEBOT
        
        Args:
            host: Adresse d'écoute
        """
        try:
            logger.info(f"🚀 Lancement THEBOT sur http://{host}:{self.port}")
            logger.info(f"🔧 Mode debug: {self.debug}")
            
            # Afficher les informations des modules
            module_info = self.get_module_info()
            logger.info(f"📊 Modules chargés: {module_info['total_modules']}")
            
            # Lancer l'application
            self.app.run(
                debug=self.debug,
                host=host,
                port=self.port,
                dev_tools_hot_reload=self.debug,
                dev_tools_ui=self.debug
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur lancement application: {e}")
            raise
    
    def shutdown(self) -> None:
        """Arrêt propre de l'application"""
        try:
            self.clear_cache()
            logger.info("🛑 Application THEBOT arrêtée proprement")
        except Exception as e:
            logger.error(f"❌ Erreur arrêt: {e}")

def main() -> None:
    """Point d'entrée principal"""
    try:
        # Configuration depuis les arguments ou environnement
        import sys
        debug = '--debug' in sys.argv or '-d' in sys.argv
        port = 8050
        
        # Récupérer le port depuis les arguments
        for i, arg in enumerate(sys.argv):
            if arg in ['--port', '-p'] and i + 1 < len(sys.argv):
                try:
                    port = int(sys.argv[i + 1])
                except ValueError:
                    logger.warning(f"Port invalide: {sys.argv[i + 1]}, utilisation du port par défaut 8050")
        
        # Créer et lancer l'application
        app = THEBOTApp(debug=debug, port=port)
        app.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        sys.exit(1)

def create_dash_app(debug: bool = False, port: int = 8050) -> dash.Dash:
    """
    Crée une instance Dash pour usage externe
    
    Args:
        debug: Mode debug
        port: Port d'écoute
        
    Returns:
        dash.Dash: Instance Dash configurée
    """
    app_instance = THEBOTApp(debug=debug, port=port)
    return app_instance.app

# Point d'entrée
if __name__ == "__main__":
    main()

# Export conforme .clinerules
__all__ = ['THEBOTApp', 'main', 'create_dash_app']