# 🏠 THEBOT - Installation sur PC Fedora Personnel

## 🎯 **PROCÉDURE COMPLÈTE POUR VOTRE PC**

### **1️⃣ Clonage depuis GitHub**

```bash
# Aller dans votre dossier personnel
cd ~

# Créer dossier pour vos projets (optionnel)
mkdir -p ~/Projets
cd ~/Projets

# Cloner THEBOT depuis votre dépôt GitHub
git clone https://github.com/Rono40230/THEBOT.git

# Aller dans le dossier
cd THEBOT

# Vérifier que tout est là
ls -la
```

### **2️⃣ Lancement Ultra-Rapide**

```bash
# Première installation (automatique)
./run_thebot.sh
# → Choisir option 3 (Réinstallation complète)
# → Attendre l'installation automatique
# → Puis choisir option 1 (Application Native)
```

### **3️⃣ Utilisation Quotidienne**

```bash
cd ~/Projets/THEBOT
./run_thebot.sh
# → Choisir option 1 (Application Desktop Native)
```

---

## 🛠️ **DÉPENDANCES SYSTÈME FEDORA**

Le script installe automatiquement, mais si besoin manuel :

```bash
# Dépendances de base
sudo dnf install -y \
    python3 python3-pip python3-venv python3-devel \
    gcc gcc-c++ make git \
    qt6-qtbase-devel qt6-qttools-devel

# Optionnel : pour PyQt6
pip install PyQt6 PyQt6-tools PyQt6-Charts
```

---

## 📁 **STRUCTURE SUR VOTRE PC**

Après clonage, vous aurez :

```
~/Projets/THEBOT/
├── 🚀 run_thebot.sh              # Lancement principal
├── 📊 jupyter_dashboard.ipynb    # Dashboard alternatif
├── 📖 README.md                  # Documentation
├── 🏗️ src/thebot/              # Code source
│   ├── indicators/              # 4 indicateurs validés
│   └── gui/native_app.py        # Application native
├── 🧪 tests/                    # Tests (61/61 ✅)
├── 📋 requirements.txt          # Dépendances Python
└── 📖 GUIDE_LANCEMENT_PC.md     # Ce guide
```

---

## 🎯 **UTILISATION RECOMMANDÉE**

### **Interface Native (Recommandée)**
- Application desktop professionnelle
- Graphiques temps réel
- Signaux automatiques
- Export données
- Thème sombre

### **Dashboard Jupyter (Alternative)**  
- Interface web dans navigateur
- Widgets interactifs
- Développement/expérimentation

---

## 📱 **Créer un Raccourci Desktop**

```bash
# Créer fichier .desktop
cat > ~/.local/share/applications/thebot.desktop << EOF
[Desktop Entry]
Name=THEBOT Trading Platform
Comment=Plateforme d'Analyse Trading Crypto/Forex
Exec=/home/$(whoami)/Projets/THEBOT/run_thebot.sh
Icon=applications-office
Terminal=true
Type=Application
Categories=Office;Finance;
EOF

# Rendre exécutable
chmod +x ~/.local/share/applications/thebot.desktop

# Maintenant THEBOT apparaît dans vos applications !
```

---

## 🔄 **Mise à Jour Future**

```bash
cd ~/Projets/THEBOT
git pull origin main    # Récupérer dernières mises à jour
./run_thebot.sh         # Relancer
```

---

## ✅ **VALIDATION INSTALLATION**

Après installation, vous devriez avoir :
- ✅ Application native qui se lance
- ✅ 4 indicateurs fonctionnels (SMA, EMA, ATR, RSI)
- ✅ Graphiques temps réel
- ✅ 61/61 tests qui passent
- ✅ Export données JSON

---

## 🆘 **SUPPORT/PROBLÈMES**

### **Erreur Python**
```bash
# Vérifier version
python3 --version    # Doit être >= 3.11

# Reinstaller si nécessaire
sudo dnf install python3.11
```

### **Erreur PyQt6**
```bash
# Installation manuelle
pip install PyQt6 PyQt6-tools PyQt6-Charts
```

### **Permissions**
```bash
# Rendre scripts exécutables
chmod +x *.sh
```

---

## 🎉 **FÉLICITATIONS !**

Vous avez maintenant THEBOT sur votre PC Fedora avec :
- 🖥️ Application desktop native professionnelle
- 📊 4 indicateurs techniques validés 
- 🚀 Architecture ultra-modulaire extensible
- 🎯 Support crypto/forex exclusif

**Enjoy trading ! 🤖📈**