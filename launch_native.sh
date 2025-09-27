#!/bin/bash
# =============================================================================
# THEBOT - Lancement Application Native Desktop
# Interface PyQt6 professionnelle pour Fedora
# =============================================================================

set -e

# Couleurs
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

THEBOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$THEBOT_DIR/venv_thebot"

echo -e "${CYAN}🤖 THEBOT - Application Native Desktop${NC}"
echo -e "${CYAN}   Interface PyQt6 Professionnelle${NC}"
echo

# Vérification environnement virtuel
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}⚠️  Environnement virtuel non trouvé !${NC}"
    echo "Lancez d'abord: ./launch_fedora.sh (option 2)"
    exit 1
fi

# Activation
source "$VENV_DIR/bin/activate"

# Vérification PyQt6
echo -e "${CYAN}Vérification des dépendances...${NC}"

if python -c "import PyQt6" 2>/dev/null; then
    echo -e "${GREEN}✅ PyQt6 détecté${NC}"
    HAS_PYQT6=true
else
    echo -e "${YELLOW}⚠️  PyQt6 non trouvé${NC}"
    HAS_PYQT6=false
fi

# Menu de choix
echo
echo "Options disponibles:"
echo "1) 🚀 Application Native PyQt6 (Recommandée)"
echo "2) 📊 Dashboard Jupyter (Navigateur)" 
echo "3) 💾 Installer PyQt6"
echo "4) ❌ Quitter"
echo

read -p "Votre choix [1-4]: " choice

case $choice in
    1)
        if [ "$HAS_PYQT6" = true ]; then
            echo -e "${GREEN}🚀 Lancement de l'application native...${NC}"
            cd "$THEBOT_DIR"
            python src/thebot/gui/native_app.py
        else
            echo -e "${RED}❌ PyQt6 requis ! Choisissez option 3 d'abord.${NC}"
            exit 1
        fi
        ;;
    2)
        echo -e "${CYAN}📊 Lancement du Dashboard Jupyter...${NC}"
        ./start.sh
        ;;
    3)
        echo -e "${CYAN}💾 Installation de PyQt6...${NC}"
        pip install PyQt6 PyQt6-tools
        echo -e "${GREEN}✅ PyQt6 installé ! Relancez l'option 1.${NC}"
        ;;
    4)
        echo -e "${GREEN}Au revoir ! 👋${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Choix invalide !${NC}"
        exit 1
        ;;
esac