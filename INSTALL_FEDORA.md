# 🚀 Installation et Lancement THEBOT sur Fedora

## Installation Rapide

### 1️⃣ Cloner le Projet
```bash
git clone https://github.com/Rono40230/THEBOT.git
cd THEBOT
```

### 2️⃣ Lancer le Script d'Installation
```bash
./launch_fedora.sh
```

### 3️⃣ Choisir Option 2 (Installation Complète)
Le script va automatiquement :
- ✅ Vérifier Fedora et Python 3.11+
- ✅ Installer les dépendances système (`dnf install`)
- ✅ Créer l'environnement virtuel Python
- ✅ Installer tous les packages Python requis
- ✅ Lancer les tests de validation
- ✅ Démarrer le Dashboard Jupyter
- ✅ Ouvrir Firefox automatiquement

## Utilisation Quotidienne

### Lancement Rapide
```bash
./launch_fedora.sh      # Menu interactif
# OU
./launch_fedora.sh start    # Direct au Dashboard
```

### Tests de Validation
```bash
./launch_fedora.sh test     # Valider tous les indicateurs
```

### Voir l'État du Système
```bash
./launch_fedora.sh status   # Info sur les indicateurs disponibles
```

## Structure du Dashboard

Une fois lancé, vous aurez accès à :

### 📊 **Dashboard Jupyter Interactif**
- **URL** : `http://localhost:8888`
- **Fichier** : `jupyter_dashboard.ipynb`
- **Interface** : Widgets interactifs + Graphiques Plotly

### 🎯 **Indicateurs Disponibles**
- **SMA** : Simple Moving Average (15 tests ✅)
- **EMA** : Exponential Moving Average (15 tests ✅) 
- **ATR** : Average True Range (17 tests ✅)
- **RSI** : Relative Strength Index (14 tests ✅)

### 📈 **Marchés Supportés**
- **Crypto** : BTCUSDT, ETHUSD
- **Forex** : EURUSD, GBPUSD

## Dépendances Système Fedora

Le script installe automatiquement :

```bash
sudo dnf install -y \
    python3-pip \
    python3-venv \
    python3-devel \
    gcc \
    gcc-c++ \
    make \
    git \
    nodejs \
    npm
```

## Dépendances Python

Installées automatiquement dans l'environnement virtuel :
- pandas, numpy, scipy (analyse de données)
- plotly (graphiques interactifs) 
- jupyter, ipywidgets (interface dashboard)
- pytest (tests de validation)
- loguru (logs avancés)

## Résolution de Problèmes

### Python < 3.11
```bash
sudo dnf install python3.11 python3.11-pip python3.11-venv
# Puis modifier le script pour utiliser python3.11
```

### Ports occupés
```bash
# Si le port 8888 est occupé
jupyter lab --port=8889
```

### Permissions
```bash
# Ne PAS lancer en root (sauf pour dnf install)
./launch_fedora.sh   # En utilisateur normal
```

### Jupyter n'ouvre pas le navigateur
Ouvrir manuellement : `http://localhost:8888/lab/tree/jupyter_dashboard.ipynb`

## Architecture Ultra-Modulaire

Chaque indicateur suit le pattern :
```
src/thebot/indicators/[category]/[name]/
├── config.py      # Configuration et validation
├── calculator.py  # Logique de calcul pure  
└── __init__.py    # Orchestration et API
```

Parfait pour ajouter les 21 autres indicateurs de NonoBot ! 🎯

## Support

Le script gère automatiquement :
- ✅ Détection de Fedora
- ✅ Vérification Python 3.11+
- ✅ Installation dépendances système  
- ✅ Environnement virtuel isolé
- ✅ Tests complets (55 tests)
- ✅ Ouverture automatique navigateur
- ✅ Menu interactif convivial

**Enjoy trading avec THEBOT ! 🤖📊**