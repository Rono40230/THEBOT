# 🛠️ Environnement de Développement THEBOT

## Vue d'ensemble
Environnement de développement isolé et optimisé pour THEBOT avec gestion moderne des dépendances.

## Structure
```
THEBOT/
├── .venv/                 # Environnement virtuel isolé
├── requirements.txt       # Dépendances runtime (nettoyées)
├── pyproject.toml         # Configuration Poetry + outils dev
├── setup_dev_env.sh       # Script d'initialisation automatique
└── DEV_ENV_README.md      # Ce fichier
```

## Configuration Rapide

### Installation Automatique (Recommandé)
```bash
./setup_dev_env.sh
```

### Installation Manuelle
```bash
# Créer l'environnement virtuel
python3 -m venv .venv

# Activer l'environnement
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Installer les outils de développement
pip install black isort mypy pytest-cov
```

## Utilisation Quotidienne

### Activation de l'environnement
```bash
source .venv/bin/activate
```

### Commandes Essentielles
```bash
# Lancer l'application
python launch_dash_professional.py

# Lancer les tests
pytest

# Formater le code
black .
isort .

# Vérification de type
mypy dash_modules/
```

### Désactivation
```bash
deactivate
```

## Dépendances

### Runtime (requirements.txt)
- **pandas** : Analyse de données
- **numpy** : Calculs numériques
- **dash** : Interface web
- **plotly** : Graphiques
- **requests** : API clients
- **feedparser** : Flux RSS
- **pytest** : Tests

### Développement (pyproject.toml)
- **black** : Formatage automatique
- **isort** : Tri des imports
- **mypy** : Vérification de types
- **pytest-cov** : Couverture de tests

## Optimisations Appliquées

### ✅ Dépendances Nettoyées
- Supprimé 15+ dépendances inutilisées
- Réduit la taille du requirements.txt de ~30 à 7 lignes
- Temps d'installation réduit de ~60%

### ✅ Gestion Moderne
- Configuration Poetry complète
- Environnement virtuel isolé
- Outils de développement intégrés

### ✅ Automatisation
- Script de setup en un clic
- Configuration reproductible
- Instructions claires pour nouveaux développeurs

## Maintenance

### Mise à jour des dépendances
```bash
source .venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Nettoyage
```bash
# Supprimer l'environnement virtuel
rm -rf .venv

# Recréer proprement
./setup_dev_env.sh
```

## Dépannage

### Problème: Commande python non trouvée
```bash
# Vérifier l'activation
which python
# Doit afficher: /home/rono/THEBOT/.venv/bin/python
```

### Problème: Module non trouvé
```bash
# Réinstaller les dépendances
source .venv/bin/activate
pip install -r requirements.txt
```

### Problème: Tests lents
```bash
# Utiliser pytest en mode optimisé
pytest -x --tb=short
```
