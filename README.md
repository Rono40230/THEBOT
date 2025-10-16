# 🤖 THEBOT - Trading Analysis Platform

Plateforme d'analyse de trading avancée avec intelligence artificielle, support multi-marchés et observabilité complète.

## ✨ Fonctionnalités

### 📊 Analyse de Marché
- **Multi-marchés** : Crypto, Forex, Actions, Indices
- **Temps réel** : Données en direct via WebSocket
- **Indicateurs** : Plus de 50 indicateurs techniques
- **IA Trading** : Conseils basés sur l'intelligence artificielle

### 📰 Agrégation de News
- **RSS Feeds** : Sources financières mondiales
- **Filtrage IA** : Analyse de sentiment automatique
- **Pagination** : Chargement optimisé des articles
- **Cache intelligent** : Performance maximale

### 🚨 Alertes & Notifications
- **Prix** : Alertes personnalisables sur les seuils
- **Tendance** : Détection automatique des renversements
- **Email/SMS** : Notifications multi-canaux
- **Dashboard** : Interface intuitive de gestion

### 🔒 Sécurité & Performance
- **Rate Limiting** : Protection contre les abus
- **Validation** : Données sécurisées avec Pydantic
- **Lazy Loading** : Démarrage ultra-rapide
- **Health Checks** : Monitoring temps réel

---

## 🚀 Installation

### Prérequis
- Python 3.11+
- pip
- Git

### Installation Rapide
```bash
# Cloner le repository
git clone https://github.com/Rono40230/THEBOT.git
cd THEBOT

# Installation des dépendances
pip install -r requirements.txt

# Configuration des API keys
cp api_config.example.json api_config.json
# Éditer api_config.json avec vos clés API

# Lancement
python launch_dash_professional.py
```

### Installation Avancée
```bash
# Avec environnement virtuel
python -m venv thebot_env
source thebot_env/bin/activate  # Linux/Mac
# thebot_env\Scripts\activate   # Windows

pip install -r requirements.txt
```

---

## 🧪 Tests & Qualité

### Exécution des Tests
```bash
# Tests unitaires
pytest tests/unit/ -v

# Tests d'intégration
pytest tests/integration/ -v

# Tests complets avec coverage
pytest --cov=dash_modules --cov-report=html

# Tests de performance
pytest tests/integration/test_phase4_integration.py::TestPhase4Performance -v
```

### Qualité du Code
```bash
# Formatage
black .

# Linting
flake8 .

# Type checking
mypy dash_modules/core/
```

---

## 🚀 Déploiement

### CI/CD Automatisé
THEBOT utilise GitHub Actions pour :
- ✅ Tests automatisés sur chaque commit
- ✅ Analyse de sécurité (Bandit, Safety)
- ✅ Contrôle qualité (Black, Flake8, MyPy)
- ✅ Déploiements multi-environnements

### Environnements
- **Development** : Tests continus
- **Staging** : Validation pré-production
- **Production** : Déploiement automatisé

### Backup Automatique
```bash
# Configuration
./scripts/backup_database.py --setup

# Exécution manuelle
./scripts/backup_database.py --run

# Installation automatique
./scripts/setup_backup_cron.sh
```

---

## 📊 Architecture

### Structure MVC
```
dash_modules/
├── components/     # Vues (UI Components)
├── callbacks/      # Contrôleurs (Business Logic)
├── core/          # Services & Utilitaires
├── data_providers/ # APIs & Data Sources
└── ai_engine/     # Intelligence Artificielle
```

### Composants Clés
- **LazyModuleLoader** : Chargement paresseux des modules
- **MetricsCollector** : Métriques temps réel
- **HealthChecker** : Vérifications de santé
- **StructuredLogger** : Logging JSON structuré
- **OptimizedRSSPaginator** : Pagination RSS optimisée
- **WebSocketPool** : Pool de connexions WebSocket

---

## 🔧 Configuration

### Variables d'Environnement
```bash
# API Keys
export BINANCE_API_KEY="your_key"
export COINBASE_API_KEY="your_key"
export TWELVE_DATA_API_KEY="your_key"

# Database
export DATABASE_URL="sqlite:///data/thebot.db"

# Security
export SECRET_KEY="your_secret_key"
export JWT_SECRET="your_jwt_secret"
```

### Fichiers de Configuration
- `api_config.json` : Configuration des APIs
- `backup_config.json` : Configuration des sauvegardes
- `pyproject.toml` : Configuration Python

---

## 📈 Monitoring & Observabilité

### Métriques Temps Réel
- Latence des requêtes
- Taux de succès/erreur
- Utilisation cache
- Performance modules

### Health Checks
- État des services externes
- Utilisation système (CPU/RAM)
- Connectivité base de données
- Statut des APIs

### Logging Structuré
- Format JSON pour ELK stack
- Niveaux configurables
- Rotation automatique
- Performance logging

---

## 🤝 Contribution

### Processus de Développement
1. Fork le repository
2. Créer une branche feature
3. Commits atomiques avec messages clairs
4. Pull Request avec description détaillée
5. Tests automatisés passent
6. Code review et merge

### Standards de Code
- **Black** pour le formatage
- **Flake8** pour le linting
- **MyPy** pour les types
- **pytest** pour les tests
- **pre-commit** hooks

---

## 📝 License

MIT License - voir [LICENSE](LICENSE) pour plus de détails.

---

## 🆘 Support

### Documentation
- [Guide d'Installation](docs/installation.md)
- [API Reference](docs/api.md)
- [Troubleshooting](docs/troubleshooting.md)

### Issues & Bugs
- [GitHub Issues](https://github.com/Rono40230/THEBOT/issues)
- Labels appropriées pour triage rapide
- Templates pour bug reports/features

### Communauté
- Discord pour discussions temps réel
- GitHub Discussions pour questions générales
- Documentation collaborative

---

## 🎯 Roadmap

### ✅ Phase 5 Terminée
- Tests unitaires complets
- CI/CD pipeline automatisé
- Backup automatique
- Infrastructure production-ready

### 🔄 Phase 6 : Finalisation
- Tests end-to-end
- Documentation complète
- Déploiement production
- Monitoring production

---

**THEBOT - Trading Intelligence Made Simple 🤖📈**
