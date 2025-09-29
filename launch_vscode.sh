#!/bin/bash
# THEBOT - Lancement VS Code Optimisé

echo "🚀 THEBOT - VS Code Launch"
echo "=========================="

cd /home/rono/THEBOT

# Ouvrir VS Code dans le dossier THEBOT
echo "📂 Ouverture de VS Code..."
code .

echo ""
echo "🎯 ACTIONS À FAIRE DANS VS CODE :"
echo ""
echo "1️⃣ OUVRIR LE TERMINAL INTÉGRÉ (Ctrl+\`)"
echo "   source venv_thebot/bin/activate"
echo ""
echo "2️⃣ LANCER LES TESTS :"
echo "   python test_vscode.py"
echo ""
echo "3️⃣ OU TESTS UNITAIRES :"
echo "   python -m pytest tests/unit/indicators/ -v"
echo ""
echo "4️⃣ OU OUVRIR JUPYTER :"
echo "   Ouvrir 'jupyter_dashboard.ipynb' et cliquer 'Run All'"
echo ""
echo "✅ VS Code lancé ! Suivez les instructions ci-dessus."