#!/bin/bash
# =============================================================================
# THEBOT - Lancement Jupyter Sans Token
# Dashboard sans authentification pour usage local
# =============================================================================

THEBOT_PATH="/home/rono/THEBOT"

# Couleurs
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}📊 THEBOT - Dashboard Jupyter (Sans Token)${NC}"

# Aller dans le bon répertoire
cd "$THEBOT_PATH" || exit 1

# Activer environnement virtuel
source venv_thebot/bin/activate

# Vérifier que le dashboard existe
if [ ! -f "jupyter_dashboard.ipynb" ]; then
    echo "❌ Dashboard non trouvé !"
    exit 1
fi

echo -e "${GREEN}🚀 Lancement Dashboard THEBOT...${NC}"
echo -e "${CYAN}   URL: http://localhost:8888${NC}"
echo -e "${CYAN}   Dashboard: jupyter_dashboard.ipynb${NC}"
echo -e "${CYAN}   Appuyez sur Ctrl+C pour arrêter${NC}"
echo

# Lancer Jupyter sans token ni mot de passe
jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --NotebookApp.token='' \
    --NotebookApp.password='' \
    --NotebookApp.open_browser=False \
    --allow-root 2>/dev/null &

# Attendre que Jupyter démarre
sleep 3

# Ouvrir automatiquement le navigateur
echo -e "${GREEN}🌐 Ouverture automatique du navigateur...${NC}"

if command -v firefox &> /dev/null; then
    firefox "http://localhost:8888/lab/tree/jupyter_dashboard.ipynb" 2>/dev/null &
elif command -v google-chrome &> /dev/null; then
    google-chrome "http://localhost:8888/lab/tree/jupyter_dashboard.ipynb" 2>/dev/null &
elif command -v chromium-browser &> /dev/null; then
    chromium-browser "http://localhost:8888/lab/tree/jupyter_dashboard.ipynb" 2>/dev/null &
else
    echo -e "${CYAN}💡 Ouvrez manuellement: http://localhost:8888/lab/tree/jupyter_dashboard.ipynb${NC}"
fi

# Attendre l'arrêt
wait