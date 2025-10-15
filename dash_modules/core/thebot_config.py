"""
Configuration centralisée THEBOT
Fichier de configuration unifié remplaçant api_config.json et autres configs
"""

# Configuration THEBOT v3.0.0
THEBOT_CONFIG = {
    # === APPLICATION ===
    "app": {
        "name": "THEBOT",
        "version": "3.0.0",
        "debug": False,
        "host": "0.0.0.0",
        "port": 8050,
        "theme": "dark",
        "auto_refresh_interval": 30,  # secondes
        "max_concurrent_requests": 10
    },

    # === PROVIDERS API ===
    "providers": {
        "binance": {
            "enabled": True,
            "base_url": "https://api.binance.com/api/v3",
            "rate_limit": 1200,  # requêtes/minute
            "timeout": 10,
            "retry_attempts": 3,
            "retry_delay": 1.0
        },
        "coingecko": {
            "enabled": True,
            "base_url": "https://api.coingecko.com/api/v3",
            "rate_limit": 25,  # requêtes/minute
            "timeout": 10,
            "retry_attempts": 3,
            "retry_delay": 1.0,
            "api_key": None  # À définir via variable d'environnement
        },
        "twelve_data": {
            "enabled": False,
            "base_url": "https://api.twelve-data.com",
            "rate_limit": 100,  # requêtes/minute
            "timeout": 10,
            "retry_attempts": 3,
            "retry_delay": 1.0,
            "api_key": None  # À définir via variable d'environnement
        },
        "yahoo_finance": {
            "enabled": True,
            "timeout": 10,
            "retry_attempts": 3,
            "retry_delay": 1.0
        },
        "rss_news": {
            "enabled": True,
            "max_workers": 5,
            "timeout": 10,
            "retry_attempts": 2,
            "retry_delay": 0.5,
            "max_articles_per_feed": 50,
            "update_interval": 300  # 5 minutes
        },
        "economic_calendar": {
            "enabled": True,
            "timeout": 15,
            "retry_attempts": 3,
            "retry_delay": 1.0,
            "update_interval": 3600  # 1 heure
        }
    },

    # === CACHE ===
    "cache": {
        "enabled": True,
        "default_ttl": 300,  # 5 minutes
        "ttl_by_type": {
            "crypto_price": 60,      # 1 minute
            "crypto_data": 300,      # 5 minutes
            "news": 600,             # 10 minutes
            "economic_events": 1800, # 30 minutes
            "fear_greed": 3600,      # 1 heure
            "market_status": 300     # 5 minutes
        },
        "max_size": 1000,  # nombre maximum d'éléments
        "cleanup_interval": 3600,  # nettoyage toutes les heures
        "stats_enabled": True
    },

    # === BASE DE DONNÉES ===
    "database": {
        "type": "json",  # json, sqlite, postgresql
        "path": "dashboard_configs",
        "backup_enabled": True,
        "backup_interval": 86400,  # 24 heures
        "max_backups": 7,
        "compression": False
    },

    # === INTELLIGENCE ARTIFICIELLE ===
    "ai": {
        "default_provider": "free",
        "providers": {
            "free": {
                "enabled": True,
                "model": "gpt-2",
                "max_tokens": 500,
                "temperature": 0.7
            },
            "openai": {
                "enabled": False,
                "model": "gpt-3.5-turbo",
                "max_tokens": 1000,
                "temperature": 0.7,
                "api_key": None
            },
            "anthropic": {
                "enabled": False,
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1000,
                "temperature": 0.7,
                "api_key": None
            }
        },
        "budget_limit": 10.0,  # €/mois
        "timeout": 30,
        "cache_responses": True,
        "response_cache_ttl": 3600  # 1 heure
    },

    # === INTERFACE UTILISATEUR ===
    "ui": {
        "theme": "dark",
        "colors": {
            "primary": "#00d4aa",
            "secondary": "#6c757d",
            "success": "#28a745",
            "danger": "#dc3545",
            "warning": "#ffc107",
            "info": "#17a2b8",
            "light": "#f8f9fa",
            "dark": "#343a40",
            "bullish": "#00d4aa",
            "bearish": "#ff6b6b",
            "neutral": "#6c757d"
        },
        "responsive_breakpoints": {
            "xs": 576,
            "sm": 768,
            "md": 992,
            "lg": 1200,
            "xl": 1400
        },
        "chart_defaults": {
            "height": 400,
            "mobile_height": 300,
            "background_color": "rgba(0,0,0,0)",
            "grid_color": "rgba(255,255,255,0.1)",
            "text_color": "#ffffff"
        },
        "animations": {
            "enabled": True,
            "duration": 300,  # ms
            "easing": "ease-in-out"
        }
    },

    # === LOGGING ===
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file_enabled": True,
        "file_path": "logs/thebot.log",
        "max_file_size": 10485760,  # 10MB
        "backup_count": 5,
        "console_enabled": True,
        "console_level": "WARNING"
    },

    # === PERFORMANCE ===
    "performance": {
        "max_workers": 5,
        "request_timeout": 10,
        "connection_pool_size": 10,
        "lazy_loading": True,
        "preload_critical_data": True,
        "memory_monitoring": True,
        "cpu_monitoring": False
    },

    # === SÉCURITÉ ===
    "security": {
        "api_key_validation": True,
        "rate_limiting": True,
        "cors_enabled": False,
        "cors_origins": ["http://localhost:8050"],
        "session_timeout": 3600,  # 1 heure
        "max_request_size": 1048576  # 1MB
    },

    # === MONITORING ===
    "monitoring": {
        "enabled": True,
        "metrics_interval": 60,  # secondes
        "health_check_endpoint": "/health",
        "performance_metrics": True,
        "error_tracking": True,
        "alerts_enabled": False
    },

    # === DÉVELOPPEMENT ===
    "development": {
        "hot_reload": False,
        "debug_toolbar": False,
        "profile_enabled": False,
        "test_mode": False,
        "mock_data": False
    }
}

# === CONFIGURATION LÉGACY ===
# Pour compatibilité avec l'ancien api_config.json
LEGACY_API_CONFIG = {
    "binance": {
        "url": "https://api.binance.com/api/v3",
        "rate_limit": 1200,
        "timeout": 10
    },
    "coingecko": {
        "url": "https://api.coingecko.com/api/v3",
        "rate_limit": 25,
        "timeout": 10
    },
    "twelve_data": {
        "url": "https://api.twelve-data.com",
        "rate_limit": 100,
        "timeout": 10
    }
}