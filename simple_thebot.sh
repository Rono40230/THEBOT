#!/bin/bash
# THEBOT - Script Minimal qui Marche

cd /home/rono/THEBOT
source venv_thebot/bin/activate

echo "🚀 THEBOT - Lancement Minimal"
echo "==============================="
echo

echo "1) 📊 Lancer Dashboard Jupyter"
echo "2) 🧪 Tester les Indicateurs"  
echo "3) ❌ Quitter"
echo

read -p "Votre choix [1-3]: " choice

case $choice in
    1)
        echo "📊 Lancement Jupyter..."
        python -m jupyter lab --no-browser --ip=0.0.0.0 --port=8888
        ;;
    2)
        echo "🧪 Test des indicateurs..."
        python -m pytest tests/unit/indicators/ -v
        ;;
    3)
        echo "Au revoir !"
        exit 0
        ;;
    *)
        echo "Choix invalide"
        ;;
esac