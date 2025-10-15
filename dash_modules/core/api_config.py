"""
API Config - Compatibilité avec l'ancien système
Fichier de transition pour maintenir la compatibilité pendant la migration
"""

from .config_manager import get_global_config

# Instance globale pour compatibilité


def get_provider(category: str, default_provider: str = None):
    """
    Fonction de compatibilité pour récupérer un provider
    Utilise maintenant le nouveau système de configuration
    """
    config = get_global_config()

    # Mapping des catégories vers les providers dans la nouvelle config
    provider_mapping = {
        "crypto": "coingecko",
        "stocks": "twelve_data",
        "forex": "twelve_data",
        "news": "rss_news",
        "economic": "economic_calendar"
    }

    provider_name = provider_mapping.get(category, category)

    if config.get(f"providers.{provider_name}.enabled"):
        return provider_name
    elif default_provider:
        return default_provider

    return None


# Classe de compatibilité pour les anciens appels
class APIConfigCompat:
    """Classe de compatibilité avec l'ancien APIConfig"""

    def __init__(self):
        self.config = get_global_config().get_all_config()

    def get_provider(self, category: str, default_provider: str = None):
        """Méthode de compatibilité"""
        return get_provider(category, default_provider)

    def get(self, key: str, default=None):
        """Récupère une valeur de configuration"""
        return get_global_config().get(key, default)

    def set(self, key: str, value):
        """Définit une valeur de configuration"""
        get_global_config().set(key, value)


# Instance globale pour compatibilité


    def get_api_config_modal(self):
        """
        Retourne le modal de configuration des APIs
        Méthode utilisée par le layout manager pour afficher le modal de config
        """
        import dash_bootstrap_components as dbc
        from dash import html
        
        return dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Configuration des APIs")),
                dbc.ModalBody([
                    html.P("Configuration des clés API pour THEBOT", className="mb-3"),
                    html.Div([
                        html.Label("Clé API Binance:", className="form-label"),
                        dbc.Input(
                            type="password",
                            id="binance-api-key",
                            placeholder="Entrez votre clé API Binance",
                            className="mb-2"
                        ),
                        html.Label("Clé API Twelve Data:", className="form-label"),
                        dbc.Input(
                            type="password", 
                            id="twelve-data-api-key",
                            placeholder="Entrez votre clé API Twelve Data",
                            className="mb-2"
                        ),
                        html.Label("Clé API CoinGecko:", className="form-label"),
                        dbc.Input(
                            type="password",
                            id="coingecko-api-key", 
                            placeholder="Entrez votre clé API CoinGecko",
                            className="mb-2"
                        ),
                    ])
                ]),
                dbc.ModalFooter([
                    dbc.Button("Annuler", id="cancel-api-config", className="ms-auto"),
                    dbc.Button("Sauvegarder", id="save-api-config", color="primary"),
                ]),
            ],
            id="api-config-modal",
            size="lg",
            is_open=False,
        )


# Instance globale pour compatibilité

# Alias pour compatibilité
api_config = APIConfigCompat()
APIConfig = APIConfigCompat
