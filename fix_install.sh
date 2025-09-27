#!/bin/bash
# =============================================================================
# THEBOT - Fix Installation (Correction Dépendances Manquantes)
# Pour corriger l'erreur matplotlib sur installation existante
# =============================================================================

THEBOT_PATH="/home/rono/THEBOT"

# Couleurs
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}🔧 THEBOT - Correction Installation${NC}"
echo

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "$THEBOT_PATH/run_thebot.sh" ]; then
    echo -e "${RED}❌ THEBOT non trouvé dans $THEBOT_PATH${NC}"
    echo "Assurez-vous d'avoir cloné THEBOT dans /home/rono/THEBOT/"
    exit 1
fi

cd "$THEBOT_PATH"

# Activer environnement virtuel
if [ -d "venv_thebot" ]; then
    echo -e "${CYAN}🐍 Activation environnement virtuel...${NC}"
    source venv_thebot/bin/activate
else
    echo -e "${YELLOW}⚠️  Environnement virtuel non trouvé, création...${NC}"
    python3 -m venv venv_thebot
    source venv_thebot/bin/activate
fi

# Installation des dépendances manquantes
echo -e "${CYAN}📦 Installation des dépendances manquantes...${NC}"

# Mise à jour pip
pip install --upgrade pip

# Dépendances critiques pour l'application native
echo -e "${CYAN}🔧 Installation matplotlib et dépendances GUI...${NC}"
pip install matplotlib>=3.7.0
pip install PyQt6 PyQt6-tools PyQt6-Charts
pip install plotly>=5.15.0
pip install ipywidgets>=8.0.0

# Dépendances complètes depuis requirements.txt
if [ -f "requirements.txt" ]; then
    echo -e "${CYAN}📋 Installation depuis requirements.txt...${NC}"
    pip install -r requirements.txt
fi

# Installation THEBOT en mode développement
echo -e "${CYAN}🔧 Installation THEBOT...${NC}"
pip install -e .

# Test des imports critiques
echo -e "${CYAN}🧪 Test des imports...${NC}"

python3 -c "
try:
    import matplotlib.pyplot as plt
    print('✅ matplotlib: OK')
except ImportError as e:
    print('❌ matplotlib: ERREUR -', e)

try:
    import PyQt6
    print('✅ PyQt6: OK')
except ImportError:
    print('⚠️  PyQt6: Non disponible (version Tkinter sera utilisée)')

try:
    from src.thebot.gui.native_app import create_native_app
    print('✅ Application native: OK')
except Exception as e:
    print('❌ Application native: ERREUR -', e)

try:
    from thebot.indicators.basic.sma import SMAIndicator
    print('✅ Indicateurs THEBOT: OK')
except Exception as e:
    print('❌ Indicateurs THEBOT: ERREUR -', e)
"

echo
echo -e "${GREEN}✅ Correction terminée !${NC}"
echo
echo -e "${CYAN}🚀 Essayez maintenant:${NC}"
echo "cd $THEBOT_PATH"
echo "./run_thebot.sh"
echo "# → Choisir option 1 (Application Native)"