#!/bin/bash
# =============================================================================
# THEBOT - Démarrage Quotidien Rapide
# Lancement direct sans menu pour usage quotidien
# =============================================================================

# Configuration
THEBOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$THEBOT_DIR/venv_thebot"

# Couleurs
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}🚀 THEBOT - Démarrage Quotidien Rapide${NC}"

# Activation environnement virtuel
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
    echo -e "${GREEN}✅ Environnement virtuel activé${NC}"
else
    echo -e "${YELLOW}⚠️  Environnement virtuel non trouvé. Lancez d'abord: ./launch_fedora.sh${NC}"
    exit 1
fi

# Vérification du dashboard
if [ ! -f "$THEBOT_DIR/jupyter_dashboard.ipynb" ]; then
    echo -e "${YELLOW}⚠️  Dashboard non trouvé !${NC}"
    exit 1
fi

# Aller au répertoire
cd "$THEBOT_DIR"

echo -e "${CYAN}📊 Ouverture du Dashboard THEBOT...${NC}"
echo -e "${CYAN}   URL: http://localhost:8888${NC}"
echo -e "${CYAN}   Ctrl+C pour arrêter${NC}"

# Lancement direct avec ouverture navigateur
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser 2>/dev/null &

# Attendre démarrage
sleep 3

# Ouvrir navigateur
if command -v firefox &> /dev/null; then
    firefox "http://localhost:8888/lab/tree/jupyter_dashboard.ipynb" 2>/dev/null &
elif command -v google-chrome &> /dev/null; then
    google-chrome "http://localhost:8888/lab/tree/jupyter_dashboard.ipynb" 2>/dev/null &
fi

# Attendre arrêt
wait