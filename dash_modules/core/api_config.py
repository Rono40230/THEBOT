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
                    "forex": [
                        {
                            "name": "Alpha Vantage",
                            "type": "forex",
                            "status": "inactive",
                            "api_key_required": True,
                            "description": "Professional forex and currency data",
                            "data_types": ["fx_rates", "historical", "intraday"],
                            "rate_limit": "5 calls/minute (free)",
                            "cost": "Free tier: 5 calls/min, Pro: $49.99/month",
                            "priority": 1,
                            "endpoints": {
                                "base_url": "https://www.alphavantage.co/query",
                                "fx_daily": "function=FX_DAILY",
                                "fx_intraday": "function=FX_INTRADAY"
                            },
                            "config": {
                                "api_key": ""
                            }
                        }
                    ],
                    "stocks": [
                        {
                            "name": "Alpha Vantage",
                            "type": "stocks",
                            "status": "inactive",
                            "api_key_required": True,
                            "description": "Global equity market data",
                            "data_types": ["stocks", "etfs", "historical", "real_time"],
                            "rate_limit": "5 calls/minute (free)",
                            "cost": "Free tier: 5 calls/min, Pro: $49.99/month",
                            "priority": 1,
                            "endpoints": {
                                "base_url": "https://www.alphavantage.co/query",
                                "daily": "function=TIME_SERIES_DAILY",
                                "intraday": "function=TIME_SERIES_INTRADAY"
                            },
                            "config": {
                                "api_key": ""
                            }
                        }
                    ],
                    "news": [
                        {
                            "name": "Alpha Vantage News",
                            "type": "news",
                            "status": "inactive",
                            "api_key_required": True,
                            "description": "Economic news and sentiment analysis",
                            "data_types": ["news", "sentiment", "economic_events"],
                            "rate_limit": "5 calls/minute (free)",
                            "cost": "Free tier: 5 calls/min, Pro: $49.99/month",
                            "priority": 1,
                            "endpoints": {
                                "base_url": "https://www.alphavantage.co/query",
                                "news": "function=NEWS_SENTIMENT"
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
        """Create the API configuration modal"""
        return html.Div([
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle([
                    html.I(className="fas fa-key me-2"),
                    "🔑 API Keys Configuration"
                ])),
                dbc.ModalBody([
                    dbc.Tabs([
                        dbc.Tab(
                            label="📊 Data Sources",
                            tab_id="data-sources-tab",
                            children=[self._create_data_sources_panel()]
                        ),
                        dbc.Tab(
                            label="🧠 AI Providers", 
                            tab_id="ai-providers-tab",
                            children=[self._create_ai_providers_panel()]
                        ),
                        dbc.Tab(
                            label="⚙️ Advanced",
                            tab_id="advanced-tab", 
                            children=[self._create_advanced_panel()]
                        ),
                        dbc.Tab(
                            label="📋 Presets",
                            tab_id="presets-tab",
                            children=[self._create_presets_panel()]
                        )
                    ], id="api-config-tabs", active_tab="data-sources-tab")
                ]),
                dbc.ModalFooter([
                    dbc.Button("Test All Connections", color="info", className="me-2", id="test-all-btn"),
                    dbc.Button("Save Configuration", color="success", className="me-2", id="save-config-btn"),
                    dbc.Button("Close", color="secondary", id="close-config-btn")
                ])
            ], id="api-config-modal", size="xl", is_open=False)
        ])
    
    def _create_data_sources_panel(self) -> html.Div:
        """Create data sources configuration panel"""
        return html.Div([
            html.H5("Data Sources Configuration", className="mb-3"),
            
            # Crypto Section
            self._create_provider_section("crypto", "💰 Cryptocurrency Data", "crypto-providers"),
            html.Hr(),
            
            # Forex Section  
            self._create_provider_section("forex", "💱 Forex Data", "forex-providers"),
            html.Hr(),
            
            # Stocks Section
            self._create_provider_section("stocks", "📊 Stocks Data", "stocks-providers"),
            html.Hr(),
            
            # News Section
            self._create_provider_section("news", "📰 Economic News", "news-providers")
        ])
    
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