"""
API Configuration Module for THEBOT
Manages API keys and data provider settings
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback
import hashlib

class APIConfig:
    """Manages API configuration and data providers"""
    
    def __init__(self, config_file: str = "api_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        default_config = {
            "providers": {
                "data_sources": {
                    "crypto": [
                        {
                            "name": "Binance",
                            "type": "crypto",
                            "status": "active",
                            "api_key_required": False,
                            "description": "Real-time cryptocurrency data",
                            "data_types": ["prices", "volume", "historical"],
                            "rate_limit": "1200 calls/minute",
                            "cost": "Free",
                            "priority": 1,
                            "endpoints": {
                                "base_url": "https://api.binance.com",
                                "klines": "/api/v3/klines",
                                "ticker": "/api/v3/ticker/24hr"
                            },
                            "config": {}
                        }
                    ],
                    "forex": [],
                    "stocks": [],
                    "news": [
                        {
                            "name": "Alpha Vantage",
                            "type": "multi",
                            "status": "inactive",
                            "api_key_required": True,
                            "description": "Professional financial data provider - Forex, Stocks, News & Analysis",
                            "data_types": ["fx_rates", "stocks", "etfs", "news", "sentiment", "historical", "real_time"],
                            "rate_limit": "5 calls/minute (free)",
                            "cost": "Free tier: 5 calls/min, Pro: $49.99/month",
                            "priority": 1,
                            "endpoints": {
                                "base_url": "https://www.alphavantage.co/query",
                                "fx_daily": "function=FX_DAILY",
                                "stocks_daily": "function=TIME_SERIES_DAILY",
                                "news": "function=NEWS_SENTIMENT"
                            },
                            "config": {
                                "api_key": ""
                            }
                        },
                        {
                            "name": "CryptoPanic",
                            "type": "news",
                            "status": "active",
                            "api_key_required": True,
                            "description": "Cryptocurrency and blockchain news aggregator",
                            "data_types": ["crypto_news", "sentiment", "social_media"],
                            "rate_limit": "1000 calls/day (free)",
                            "cost": "Free: 1000 calls/day, Pro: $7/month",
                            "priority": 2,
                            "endpoints": {
                                "base_url": "https://cryptopanic.com/api/v1",
                                "posts": "/posts/"
                            },
                            "config": {
                                "api_key": ""
                            }
                        },
                        {
                            "name": "CoinGecko",
                            "type": "news",
                            "status": "active", 
                            "api_key_required": True,
                            "description": "Cryptocurrency data and news provider",
                            "data_types": ["crypto_prices", "market_data", "news"],
                            "rate_limit": "30 calls/minute (free)",
                            "cost": "Free: 30 calls/min, Pro: $199/month",
                            "priority": 3,
                            "endpoints": {
                                "base_url": "https://api.coingecko.com/api/v3",
                                "news": "/news"
                            },
                            "config": {
                                "api_key": ""
                            }
                        },
                        {
                            "name": "Yahoo Finance",
                            "type": "news",
                            "status": "active",
                            "api_key_required": False,
                            "description": "Free financial news and market data",
                            "data_types": ["financial_news", "market_data", "earnings"],
                            "rate_limit": "Variable (rate limited)",
                            "cost": "Free",
                            "priority": 4,
                            "endpoints": {
                                "base_url": "https://feeds.finance.yahoo.com",
                                "rss": "/rss/2.0/headline"
                            },
                            "config": {}
                        },
                        {
                            "name": "FMP",
                            "type": "news",
                            "status": "inactive",
                            "api_key_required": True,
                            "description": "Financial Modeling Prep - Professional financial data",
                            "data_types": ["financial_news", "company_news", "market_analysis"],
                            "rate_limit": "250 calls/day (free)",
                            "cost": "Free: 250 calls/day, Pro: $14/month",
                            "priority": 5,
                            "endpoints": {
                                "base_url": "https://financialmodelingprep.com/api/v3",
                                "news": "/stock_news"
                            },
                            "config": {
                                "api_key": ""
                            }
                        }
                    ]
                },
                "ai_providers": [
                    {
                        "name": "OpenAI GPT",
                        "type": "ai",
                        "status": "inactive",
                        "api_key_required": True,
                        "description": "Advanced AI analysis and insights",
                        "capabilities": ["analysis", "predictions", "explanations"],
                        "models": ["gpt-4", "gpt-3.5-turbo"],
                        "rate_limit": "3000 tokens/minute",
                        "cost": "$0.03/1K tokens (GPT-4)",
                        "priority": 1,
                        "config": {
                            "api_key": "",
                            "model": "gpt-4",
                            "max_tokens": 1000,
                            "temperature": 0.7
                        }
                    },
                    {
                        "name": "Anthropic Claude",
                        "type": "ai",
                        "status": "inactive",
                        "api_key_required": True,
                        "description": "Claude AI for market analysis",
                        "capabilities": ["analysis", "reasoning", "explanations"],
                        "models": ["claude-3-opus", "claude-3-sonnet"],
                        "rate_limit": "4000 tokens/minute",
                        "cost": "$15/million tokens",
                        "priority": 2,
                        "config": {
                            "api_key": "",
                            "model": "claude-3-sonnet",
                            "max_tokens": 1000
                        }
                    }
                ]
            },
            "settings": {
                "auto_fallback": True,
                "health_monitoring": True,
                "cost_tracking": True,
                "last_updated": datetime.now().isoformat()
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return self._merge_configs(default_config, loaded_config)
            except Exception as e:
                print(f"⚠️ Error loading config: {e}")
                
        return default_config
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Merge loaded config with defaults"""
        result = default.copy()
        for key, value in loaded.items():
            if isinstance(value, dict) and key in result:
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self):
        """Save configuration to file"""
        try:
            # Update timestamp
            self.config["settings"]["last_updated"] = datetime.now().isoformat()
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print("✅ Configuration saved successfully")
            return True
        except Exception as e:
            print(f"❌ Error saving config: {e}")
            return False
    
    def get_provider(self, data_type: str, provider_name: str) -> Optional[Dict]:
        """Get specific provider configuration"""
        providers = self.config["providers"]["data_sources"].get(data_type, [])
        for provider in providers:
            if provider["name"] == provider_name:
                return provider
        return None
    
    def get_active_providers(self, data_type: str) -> List[Dict]:
        """Get active providers for a data type"""
        providers = self.config["providers"]["data_sources"].get(data_type, [])
        return [p for p in providers if p["status"] == "active"]
    
    def set_api_key(self, provider_name: str, data_type: str, api_key: str) -> bool:
        """Set API key for a provider"""
        provider = self.get_provider(data_type, provider_name)
        if provider:
            provider["config"]["api_key"] = api_key
            provider["status"] = "active" if api_key else "inactive"
            return self.save_config()
        return False
    
    def test_provider(self, provider_name: str, data_type: str) -> Dict:
        """Test provider connection"""
        provider = self.get_provider(data_type, provider_name)
        if not provider:
            return {"success": False, "error": "Provider not found"}
        
        if provider["name"] == "Alpha Vantage":
            from .alpha_vantage_api import AlphaVantageAPI
            api = AlphaVantageAPI(provider["config"].get("api_key"))
            return api.test_connection()
        elif provider["name"] == "Binance":
            # Binance doesn't require API key for public data
            return {"success": True, "message": "Binance public API available"}
        else:
            return {"success": False, "error": "Provider test not implemented"}
    
    def add_custom_provider(self, provider_config: Dict) -> bool:
        """Add a custom data provider"""
        data_type = provider_config.get("type")
        if data_type not in self.config["providers"]["data_sources"]:
            self.config["providers"]["data_sources"][data_type] = []
        
        self.config["providers"]["data_sources"][data_type].append(provider_config)
        return self.save_config()
    
    def remove_provider(self, provider_name: str, data_type: str) -> bool:
        """Remove a data provider"""
        providers = self.config["providers"]["data_sources"].get(data_type, [])
        self.config["providers"]["data_sources"][data_type] = [
            p for p in providers if p["name"] != provider_name
        ]
        return self.save_config()
    
    def get_api_config_modal(self) -> html.Div:
        """Create the simplified API configuration modal"""
        return html.Div([
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle([
                    html.I(className="fas fa-key me-2"),
                    "🔑 Configuration des Fournisseurs de Données"
                ])),
                dbc.ModalBody([
                    self._create_unified_providers_panel()
                ]),
                dbc.ModalFooter([
                    dbc.Button("Tester les Connexions", color="info", className="me-2", id="test-all-btn"),
                    dbc.Button("Enregistrer", color="success", className="me-2", id="save-config-btn"),
                    dbc.Button("Fermer", color="secondary", id="close-config-btn")
                ])
            ], id="api-config-modal", size="xl", is_open=False)
        ])
    
    def _create_unified_providers_panel(self) -> html.Div:
        """Create unified providers configuration panel"""
        
        # Récupérer tous les providers de toutes les catégories
        all_providers = []
        categories = {
            "crypto": {"icon": "💰", "name": "Crypto"},
            "forex": {"icon": "💱", "name": "Forex"}, 
            "stocks": {"icon": "📊", "name": "Actions"},
            "news": {"icon": "📰", "name": "News"}
        }
        
        for data_type, type_info in categories.items():
            providers = self.config["providers"]["data_sources"].get(data_type, [])
            for provider in providers:
                provider_copy = provider.copy()
                provider_copy["data_type"] = data_type
                provider_copy["type_info"] = type_info
                all_providers.append(provider_copy)
        
        # Supprimer les doublons basés sur le nom
        unique_providers = {}
        for provider in all_providers:
            name = provider["name"]
            if name not in unique_providers:
                unique_providers[name] = provider
            else:
                # Fusionner les types de données
                existing = unique_providers[name]
                existing["data_types"] = list(set(existing["data_types"] + provider["data_types"]))
        
        provider_cards = []
        for provider_name, provider in unique_providers.items():
            status_color = "success" if provider["status"] == "active" else "secondary"
            status_icon = "🟢" if provider["status"] == "active" else "🔴"
            status_text = "ACTIF" if provider["status"] == "active" else "INACTIF"
            
            # Déterminer si une API key est requise
            needs_api_key = provider.get("api_key_required", False)
            
            card = dbc.Card([
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col([
                            html.H6([
                                f"{provider['type_info']['icon']} {provider_name}",
                            ], className="mb-0")
                        ], width=8),
                        dbc.Col([
                            dbc.Badge(
                                f"{status_icon} {status_text}",
                                color=status_color,
                                className="float-end"
                            )
                        ], width=4)
                    ])
                ]),
                dbc.CardBody([
                    # Description
                    html.P(provider["description"], className="text-muted small mb-2"),
                    
                    # Informations techniques en ligne
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.Strong("Types: ", className="small"),
                                html.Span(", ".join(provider["data_types"]), className="small")
                            ])
                        ], width=6),
                        dbc.Col([
                            html.Div([
                                html.Strong("Limites: ", className="small"),
                                html.Span(provider["rate_limit"], className="small")
                            ])
                        ], width=6)
                    ], className="mb-2"),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.Strong("Coût: ", className="small"),
                                html.Span(provider["cost"], className="small")
                            ])
                        ], width=12)
                    ], className="mb-3"),
                    
                    # Champ API Key seulement pour CryptoPanic et CoinGecko
                    html.Div([
                        dbc.Label("Clé API:", className="small fw-bold"),
                        dbc.InputGroup([
                            dbc.Input(
                                type="password",
                                placeholder="Entrez votre clé API...",
                                value=provider["config"].get("api_key", ""),
                                id=f"api-key-{provider_name.lower().replace(' ', '-')}"
                            ),
                            dbc.Button(
                                "Tester",
                                color="outline-primary",
                                size="sm",
                                id=f"test-{provider_name.lower().replace(' ', '-')}"
                            )
                        ])
                    ], className="mb-3") if needs_api_key else html.Div(),
                    
                    # Boutons d'action (sans bouton supprimer)
                    dbc.ButtonGroup([
                        dbc.Button(
                            "Activer" if provider["status"] == "inactive" else "Désactiver",
                            size="sm", 
                            color="success" if provider["status"] == "inactive" else "warning",
                            outline=True,
                            id=f"toggle-{provider_name.lower().replace(' ', '-')}"
                        ),
                        dbc.Button("Configurer", size="sm", color="primary", outline=True)
                    ], size="sm")
                ])
            ], className="mb-3")
            
            provider_cards.append(card)
        
        return html.Div([
            html.Div([
                html.H5("🔧 Fournisseurs de Données", className="text-primary mb-3"),
                html.P("Configuration des sources de données et clés API", className="text-muted small mb-4")
            ]),
            html.Div(provider_cards)
        ])

    def _create_data_sources_panel(self) -> html.Div:
        """Legacy method - redirects to unified panel"""
        return self._create_unified_providers_panel()
    
    def _create_provider_section(self, data_type: str, title: str, section_id: str) -> html.Div:
        """Create a section for specific provider type"""
        providers = self.config["providers"]["data_sources"].get(data_type, [])
        
        provider_cards = []
        for provider in providers:
            status_color = "success" if provider["status"] == "active" else "warning"
            status_icon = "✅" if provider["status"] == "active" else "⚠️"
            
            card = dbc.Card([
                dbc.CardHeader([
                    html.H6([
                        f"{status_icon} {provider['name']}",
                        dbc.Badge(
                            provider["status"].title(),
                            color=status_color,
                            className="ms-2"
                        )
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    html.P(provider["description"], className="text-muted small"),
                    
                    html.Div([
                        html.Strong("Data Types: "),
                        html.Span(", ".join(provider["data_types"]))
                    ], className="small mb-2"),
                    
                    html.Div([
                        html.Strong("Rate Limit: "),
                        html.Span(provider["rate_limit"])
                    ], className="small mb-2"),
                    
                    html.Div([
                        html.Strong("Cost: "),
                        html.Span(provider["cost"])
                    ], className="small mb-3"),
                    
                    # API Key input if required
                    html.Div([
                        dbc.Label("API Key:", className="small fw-bold"),
                        dbc.InputGroup([
                            dbc.Input(
                                type="password",
                                placeholder="Enter API key..." if provider["api_key_required"] else "No API key required",
                                value=provider["config"].get("api_key", ""),
                                disabled=not provider["api_key_required"],
                                id=f"api-key-{data_type}-{provider['name'].lower().replace(' ', '-')}"
                            ),
                            dbc.Button(
                                "Test",
                                color="outline-secondary",
                                size="sm",
                                id=f"test-{data_type}-{provider['name'].lower().replace(' ', '-')}"
                            )
                        ])
                    ], className="mb-2") if provider["api_key_required"] else html.Div(),
                    
                    dbc.ButtonGroup([
                        dbc.Button("Configure", size="sm", color="primary", outline=True),
                        dbc.Button(
                            "Remove" if len(providers) > 1 else "Disable", 
                            size="sm", 
                            color="danger", 
                            outline=True
                        )
                    ], size="sm")
                ])
            ], className="mb-3")
            
            provider_cards.append(card)
        
        return html.Div([
            html.H6(title, className="text-primary"),
            html.Div(provider_cards),
            dbc.Button(
                f"+ Add {data_type.title()} Provider",
                size="sm",
                color="success",
                outline=True,
                className="mt-2"
            )
        ])
    
    def _create_ai_providers_panel(self) -> html.Div:
        """Create AI providers configuration panel"""
        return html.Div([
            html.H5("AI Providers Configuration", className="mb-3"),
            html.P("Configure AI services for market analysis and insights.", className="text-muted"),
            
            # AI providers cards will be generated here
            html.Div(id="ai-providers-content")
        ])
    
    def _create_advanced_panel(self) -> html.Div:
        """Create advanced settings panel"""
        return html.Div([
            html.H5("Advanced Settings", className="mb-3"),
            
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Switch(
                                id="auto-fallback-switch",
                                label="Auto Fallback",
                                value=self.config["settings"].get("auto_fallback", True)
                            ),
                            html.Small("Automatically switch to backup providers if primary fails", className="text-muted")
                        ], width=6),
                        
                        dbc.Col([
                            dbc.Switch(
                                id="health-monitoring-switch", 
                                label="Health Monitoring",
                                value=self.config["settings"].get("health_monitoring", True)
                            ),
                            html.Small("Monitor API health and performance", className="text-muted")
                        ], width=6)
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Switch(
                                id="cost-tracking-switch",
                                label="Cost Tracking", 
                                value=self.config["settings"].get("cost_tracking", True)
                            ),
                            html.Small("Track API usage and costs", className="text-muted")
                        ], width=6)
                    ])
                ])
            ])
        ])
    
    def _create_presets_panel(self) -> html.Div:
        """Create configuration presets panel"""
        return html.Div([
            html.H5("Configuration Presets", className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🆓 Free Tier"),
                        dbc.CardBody([
                            html.P("Basic configuration using free APIs", className="small"),
                            html.Ul([
                                html.Li("Binance (Crypto) - Free"),
                                html.Li("Alpha Vantage Free (Forex/Stocks) - 5 calls/min"),
                                html.Li("Basic AI analysis")
                            ], className="small"),
                            dbc.Button("Apply Free Preset", color="success", size="sm")
                        ])
                    ])
                ], width=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("💼 Professional"),
                        dbc.CardBody([
                            html.P("Enhanced APIs for professional trading", className="small"),
                            html.Ul([
                                html.Li("Binance Pro (Crypto)"),
                                html.Li("Alpha Vantage Pro (Forex/Stocks)"),
                                html.Li("OpenAI GPT-4 (AI Analysis)")
                            ], className="small"),
                            dbc.Button("Apply Pro Preset", color="primary", size="sm")
                        ])
                    ])
                ], width=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🚀 Enterprise"),
                        dbc.CardBody([
                            html.P("Full-featured enterprise setup", className="small"),
                            html.Ul([
                                html.Li("Multiple data providers"),
                                html.Li("Redundancy & failover"),
                                html.Li("Advanced AI models")
                            ], className="small"),
                            dbc.Button("Apply Enterprise Preset", color="warning", size="sm")
                        ])
                    ])
                ], width=4)
            ])
        ])


# Global instance
api_config = APIConfig()