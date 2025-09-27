# 🏠 THEBOT - Installation dans /home/rono/THEBOT/

## 🎯 **PROCÉDURE EXACTE POUR VOTRE PC**

### **1️⃣ Clonage dans le Répertoire Spécifié**

```bash
# Aller dans votre répertoire home
cd /home/rono

# Cloner THEBOT directement dans /home/rono/THEBOT/
git clone https://github.com/Rono40230/THEBOT.git

# Vérifier que le dossier est créé correctement
ls -la /home/rono/THEBOT/

# Aller dans le dossier
cd /home/rono/THEBOT
```

### **2️⃣ Première Installation & Lancement**

```bash
# Dans /home/rono/THEBOT/
./run_thebot.sh
# → Choisir option 3 (Réinstallation complète)
# → Attendre l'installation automatique des dépendances
# → Puis choisir option 1 (Application Desktop Native)
```

### **3️⃣ Utilisation Quotidienne**

```bash
# Toujours aller dans le bon répertoire
cd /home/rono/THEBOT

# Lancer THEBOT
./run_thebot.sh
# → Choisir option 1 (Application Native)
```

---

## 🛠️ **SCRIPTS ADAPTÉS POUR VOTRE CHEMIN**

Je vais créer un script personnalisé qui utilise automatiquement `/home/rono/THEBOT/` :

### **Script de Lancement Personnalisé**

```bash
#!/bin/bash
# Script personnalisé pour /home/rono/THEBOT/

THEBOT_PATH="/home/rono/THEBOT"

# Vérifier que le dossier existe
if [ ! -d "$THEBOT_PATH" ]; then
    echo "❌ THEBOT non trouvé dans $THEBOT_PATH"
    echo "Clonez d'abord avec:"
    echo "cd /home/rono && git clone https://github.com/Rono40230/THEBOT.git"
    exit 1
fi

# Aller dans le bon répertoire
cd "$THEBOT_PATH"

# Lancer THEBOT
echo "🚀 Lancement THEBOT depuis $THEBOT_PATH"
./run_thebot.sh
```

---

## 📁 **STRUCTURE FINALE SUR VOTRE PC**

Après clonage, vous aurez :

```
/home/rono/THEBOT/
├── 🚀 run_thebot.sh              # Lancement principal
├── 🖥️ launch_native.sh          # App native seulement
├── 📊 jupyter_dashboard.ipynb    # Dashboard alternatif  
├── 📖 README.md                  # Documentation
├── 🏗️ src/thebot/              # Code source
│   ├── indicators/              # 4 indicateurs validés
│   │   ├── basic/sma/          # Simple Moving Average
│   │   ├── basic/ema/          # Exponential Moving Average
│   │   ├── volatility/atr/     # Average True Range
│   │   └── oscillators/rsi/    # Relative Strength Index
│   └── gui/native_app.py       # Application native PyQt6
├── 🧪 tests/                    # 61 tests validés
├── 📋 requirements.txt          # Dépendances Python
├── 🐧 launch_fedora.sh          # Installation complète Fedora
├── 🖱️ start.sh                  # Démarrage rapide
└── 📖 Documentation/            # Guides complets
```

---

## 🚀 **COMMANDES RACCOURCIES POUR VOTRE PC**

### **Installation (Une seule fois)**
```bash
cd /home/rono
git clone https://github.com/Rono40230/THEBOT.git
cd /home/rono/THEBOT
./run_thebot.sh  # Option 3 puis Option 1
```

### **Utilisation Quotidienne**
```bash
cd /home/rono/THEBOT && ./run_thebot.sh  # Option 1
```

### **Mise à Jour Future**
```bash
cd /home/rono/THEBOT
git pull origin main
./run_thebot.sh
```

---

## 📱 **RACCOURCI DESKTOP PERSONNALISÉ**

Créer un raccourci qui utilise directement `/home/rono/THEBOT/` :

```bash
# Créer le fichier desktop
cat > ~/.local/share/applications/thebot-rono.desktop << EOF
[Desktop Entry]
Name=THEBOT Trading Platform
Comment=Plateforme d'Analyse Trading - Installation Rono
Exec=/home/rono/THEBOT/run_thebot.sh
Path=/home/rono/THEBOT
Icon=applications-office
Terminal=true
Type=Application
Categories=Office;Finance;
StartupNotify=true
EOF

# Rendre exécutable
chmod +x ~/.local/share/applications/thebot-rono.desktop

echo "✅ Raccourci créé ! THEBOT apparaît dans vos applications."
```

---

## 🔧 **ALIAS BASH POUR FACILITER L'USAGE**

Ajouter à votre `~/.bashrc` :

```bash
# Ajouter ces lignes à la fin de /home/rono/.bashrc
echo '
# THEBOT Trading Platform
alias thebot="cd /home/rono/THEBOT && ./run_thebot.sh"
alias thebot-native="cd /home/rono/THEBOT && ./launch_native.sh"
alias thebot-update="cd /home/rono/THEBOT && git pull origin main"
' >> ~/.bashrc

# Recharger le bash
source ~/.bashrc
```

**Maintenant vous pouvez lancer THEBOT avec juste :**
```bash
thebot          # Lancement avec menu
thebot-native   # App native directe
thebot-update   # Mise à jour
```

---

## 📊 **ENVIRONNEMENT VIRTUEL DANS /home/rono/THEBOT/**

L'environnement virtuel sera créé dans :
```
/home/rono/THEBOT/venv_thebot/
```

Tout sera contenu dans votre dossier THEBOT, rien ailleurs sur le système.

---

## ✅ **VALIDATION INSTALLATION**

Après installation, vérifiez :

```bash
cd /home/rono/THEBOT

# Vérifier structure
ls -la

# Vérifier environnement virtuel
ls -la venv_thebot/

# Tester les indicateurs
python -m pytest tests/unit/indicators/ -v

# Lancer l'application
./run_thebot.sh
```

---

## 🎯 **AVANTAGES DE CETTE ORGANISATION**

- ✅ **Chemin fixe** : Toujours `/home/rono/THEBOT/`
- ✅ **Isolation complète** : Tout dans un dossier
- ✅ **Raccourcis personnalisés** adaptés à votre chemin
- ✅ **Mise à jour facile** avec git pull
- ✅ **Sauvegarde simple** : juste sauvegarder le dossier
- ✅ **Alias bash** pour utilisation rapide

**THEBOT sera parfaitement organisé dans `/home/rono/THEBOT/` ! 🚀**