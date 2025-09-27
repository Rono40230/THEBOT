#!/bin/bash
# =============================================================================
# THEBOT - Guide de Démarrage Express pour Rono
# Installation directe dans /home/rono/THEBOT/
# =============================================================================

echo "🚀 THEBOT - Installation Express pour Rono"
echo "==========================================="
echo

# Étape 1 : Clonage direct
echo "📥 ÉTAPE 1 : Clonage dans /home/rono/THEBOT/"
echo "cd /home/rono"
echo "git clone https://github.com/Rono40230/THEBOT.git"
echo

# Étape 2 : Installation
echo "🔧 ÉTAPE 2 : Installation & Premier Lancement"
echo "cd /home/rono/THEBOT"
echo "./run_thebot.sh"
echo "# → Choisir option 3 (Installation complète)"
echo "# → Puis option 1 (Application Native)"
echo

# Étape 3 : Usage quotidien
echo "⚡ ÉTAPE 3 : Usage Quotidien"
echo "cd /home/rono/THEBOT && ./run_thebot.sh"
echo

# Bonus : Alias
echo "💡 BONUS : Alias pour faciliter l'usage"
echo "echo 'alias thebot=\"cd /home/rono/THEBOT && ./run_thebot.sh\"' >> ~/.bashrc"
echo "source ~/.bashrc"
echo "# Puis juste: thebot"
echo

# Raccourci desktop
echo "🖱️  BONUS : Raccourci Desktop"
echo "cat > ~/.local/share/applications/thebot.desktop << EOF"
echo "[Desktop Entry]"
echo "Name=THEBOT Trading"
echo "Exec=/home/rono/THEBOT/run_thebot.sh"
echo "Path=/home/rono/THEBOT"
echo "Icon=applications-office"
echo "Terminal=true"
echo "Type=Application"
echo "Categories=Office;Finance;"
echo "EOF"
echo "chmod +x ~/.local/share/applications/thebot.desktop"
echo

echo "✅ THEBOT sera installé dans /home/rono/THEBOT/ et prêt à utiliser !"
echo "🎯 Interface native desktop + 4 indicateurs validés (61 tests ✅)"