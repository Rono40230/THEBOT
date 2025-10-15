#!/bin/bash
# Script de configuration de l'environnement de développement THEBOT
# Optimisé pour isolation et reproductibilité

set -e

echo "🚀 Configuration de l'environnement de développement THEBOT..."

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 n'est pas installé"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $PYTHON_VERSION détecté"

# Supprimer l'ancien environnement virtuel s'il existe
if [ -d ".venv" ]; then
    echo "🗑️ Suppression de l'ancien environnement virtuel..."
    rm -rf .venv
fi

# Créer un nouvel environnement virtuel
echo "🏗️ Création de l'environnement virtuel isolé..."
python3 -m venv .venv

# Activer l'environnement virtuel
source .venv/bin/activate

# Mettre à jour pip
echo "⬆️ Mise à jour de pip..."
pip install --upgrade pip

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# Installer les outils de développement
echo "🔧 Installation des outils de développement..."
pip install black isort mypy pytest-cov

echo "✅ Environnement de développement configuré avec succès!"
echo ""
echo "📋 Commandes utiles:"
echo "  source .venv/bin/activate    # Activer l'environnement"
echo "  deactivate                   # Désactiver l'environnement"
echo "  python launch_dash_professional.py  # Lancer l'application"
echo "  pytest                       # Lancer les tests"
