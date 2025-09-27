#!/bin/bash
# =============================================================================
# THEBOT - Lancement Ultra-Rapide sur PC Fedora
# Script tout-en-un pour votre usage quotidien
# =============================================================================

THEBOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$THEBOT_DIR"

# Couleurs
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}🚀 THEBOT - Lancement PC Fedora${NC}"
echo

# Fonction d'installation automatique
auto_install() {
    echo -e "${CYAN}Installation automatique...${NC}"
    
    # Dépendances système
    sudo dnf install -y python3-pip python3-venv python3-devel gcc gcc-c++ make git || true
    
    # Environnement virtuel
    if [ ! -d "venv_thebot" ]; then
        python3 -m venv venv_thebot
    fi
    
    source venv_thebot/bin/activate
    
    # Dépendances Python
    pip install --upgrade pip
    pip install -r requirements.txt || true
    pip install -e . || true
    pip install PyQt6 PyQt6-tools PyQt6-Charts || true
    pip install matplotlib plotly ipywidgets || true  # Dépendances critiques
    
    echo -e "${GREEN}✅ Installation terminée !${NC}"
}

# Fonction de lancement natif
launch_native() {
    echo -e "${GREEN}🖥️  Lancement application native...${NC}"
    source venv_thebot/bin/activate
    python src/thebot/gui/native_app.py
}

# Fonction de lancement Jupyter
launch_jupyter() {
    echo -e "${GREEN}📊 Lancement Dashboard Jupyter...${NC}"
    source venv_thebot/bin/activate
    jupyter lab --ip=0.0.0.0 --port=8888 --no-browser 2>/dev/null &
    sleep 3
    
    # Ouvrir navigateur
    if command -v firefox &> /dev/null; then
        firefox "http://localhost:8888/lab/tree/jupyter_dashboard.ipynb" 2>/dev/null &
    elif command -v google-chrome &> /dev/null; then
        google-chrome "http://localhost:8888/lab/tree/jupyter_dashboard.ipynb" 2>/dev/null &
    else
        echo "Ouvrez: http://localhost:8888/lab/tree/jupyter_dashboard.ipynb"
    fi
    
    wait
}

# Détection automatique
if [ ! -d "venv_thebot" ] || [ ! -f "src/thebot/gui/native_app.py" ]; then
    echo -e "${YELLOW}⚠️  Première installation détectée${NC}"
    auto_install
fi

# Menu simple
echo "Que voulez-vous lancer ?"
echo "1) 🖥️  Application Desktop Native (PyQt6)"
echo "2) 📊 Dashboard Jupyter (Navigateur)"
echo "3) ⚙️  Réinstallation complète"
echo

read -p "Votre choix [1-3]: " choice

case $choice in
    1)
        launch_native
        ;;
    2)
        launch_jupyter
        ;;
    3)
        auto_install
        echo "Relancez le script pour utiliser THEBOT"
        ;;
    *)
        echo -e "${GREEN}Lancement par défaut: Application Native${NC}"
        launch_native
        ;;
esac