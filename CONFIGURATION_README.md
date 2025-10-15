# Configuration Unifiée THEBOT v3.0.0

## Vue d'ensemble

THEBOT utilise désormais un système de configuration unifié et centralisé qui remplace l'ancien système fragmenté (api_config.json, configurations éparpillées).

## Architecture

### Fichiers de configuration

- **`dash_modules/core/thebot_config.py`** - Configuration centralisée par défaut
- **`dash_modules/core/config_manager.py`** - Gestionnaire de configuration singleton
- **`dash_modules/core/api_config.py`** - Couche de compatibilité avec l'ancien système
- **`.env`** - Variables d'environnement sensibles (clés API)
- **`.env.example`** - Template des variables d'environnement

### Hiérarchie de configuration

1. **Configuration par défaut** (`thebot_config.py`)
2. **Variables d'environnement** (`.env`)
3. **Fichiers locaux** (pour surcharge)
4. **Configuration runtime** (modifications en cours d'exécution)

## Utilisation

### Accès à la configuration

```python
from dash_modules.core.config_manager import get_global_config, get_config_value

# Instance globale
config = get_global_config()

# Récupération de valeurs
app_name = config.get('app.name')
debug_mode = config.get('app.debug', False)
api_key = config.get('providers.coingecko.api_key')

# Fonction utilitaire
port = get_config_value('app.port', 8050)
```

### Modification de la configuration

```python
from dash_modules.core.config_manager import set_config_value

# Définition de valeurs
set_config_value('app.debug', True)
set_config_value('providers.twelve_data.api_key', 'your_key_here')
```

## Sections de configuration

### Application (`app`)
```python
app: {
    "name": "THEBOT",
    "version": "3.0.0",
    "debug": False,
    "host": "0.0.0.0",
    "port": 8050,
    "theme": "dark"
}
```

### Providers API (`providers`)
```python
providers: {
    "binance": {
        "enabled": True,
        "base_url": "https://api.binance.com/api/v3",
        "rate_limit": 1200,
        "timeout": 10
    },
    "coingecko": {
        "enabled": True,
        "base_url": "https://api.coingecko.com/api/v3",
        "rate_limit": 25,
        "timeout": 10,
        "api_key": None
    }
    # ... autres providers
}
```

### Cache (`cache`)
```python
cache: {
    "enabled": True,
    "default_ttl": 300,
    "ttl_by_type": {
        "crypto_price": 60,
        "crypto_data": 300,
        "news": 600,
        "economic_events": 1800
    },
    "max_size": 1000
}
```

### Intelligence Artificielle (`ai`)
```python
ai: {
    "default_provider": "free",
    "budget_limit": 10.0,
    "providers": {
        "free": {"enabled": True, "model": "gpt-2"},
        "openai": {"enabled": False, "model": "gpt-3.5-turbo"},
        "anthropic": {"enabled": False, "model": "claude-3-haiku-20240307"}
    }
}
```

## Variables d'environnement

Créer un fichier `.env` à la racine du projet :

```bash
# API Keys
COINGECKO_API_KEY=votre_clé_coingecko
TWELVE_DATA_API_KEY=votre_clé_twelve_data
OPENAI_API_KEY=votre_clé_openai
ANTHROPIC_API_KEY=votre_clé_anthropic

# Application
THEBOT_DEBUG=false
THEBOT_PORT=8050
THEBOT_HOST=0.0.0.0
```

## Migration depuis l'ancien système

### Script de migration automatique

```bash
python migrate_config.py
```

Ce script :
- Sauvegarde l'ancien `api_config.json`
- Migre les clés API vers `.env`
- Met à jour les références dans le code
- Renomme l'ancien fichier en `.obsolete`

### Compatibilité descendante

L'ancien système `api_config` est maintenu pour compatibilité :

```python
from dash_modules.core.api_config import api_config

# Ancienne méthode (toujours fonctionnelle)
provider = api_config.get_provider("crypto", "coingecko")
```

## Bonnes pratiques

### 1. Utiliser les variables d'environnement
- Pour les clés API sensibles
- Pour la configuration spécifique à l'environnement (dev/prod)

### 2. Validation des configurations
```python
config = get_global_config()
if not config.get('providers.coingecko.api_key'):
    logger.warning("Clé API CoinGecko manquante")
```

### 3. Cache intelligent
Le système utilise différents TTL selon le type de données :
- Prix crypto : 1 minute
- Données crypto : 5 minutes
- Actualités : 10 minutes
- Événements économiques : 30 minutes

### 4. Monitoring et logging
```python
logging.getLogger('dash_modules.core.config_manager')
```

## Dépannage

### Configuration non chargée
```python
from dash_modules.core.config_manager import get_global_config
config = get_global_config()
print(config.get_all_config())  # Debug complet
```

### Variables d'environnement ignorées
Installer `python-dotenv` :
```bash
pip install python-dotenv
```

### Erreurs de compatibilité
Vérifier que les imports utilisent le nouveau système :
```python
# ✅ Correct
from dash_modules.core.config_manager import get_global_config

# ❌ Obsolète (mais fonctionnel)
from dash_modules.core.api_config import api_config
```

## Évolution future

- Support pour configuration à distance (base de données)
- Validation automatique des schémas
- Interface web de configuration
- Profils de configuration (dev, staging, prod)