# 🔧 CORRECTION INSTALLATION THEBOT

## ❌ **PROBLÈME DÉTECTÉ**
```
ModuleNotFoundError: No module named 'matplotlib'
```

## ✅ **SOLUTION RAPIDE - 2 OPTIONS**

### **🚀 OPTION 1 - CORRECTION AUTOMATIQUE**
```bash
cd /home/rono/THEBOT
curl -O https://raw.githubusercontent.com/Rono40230/THEBOT/main/fix_install.sh
chmod +x fix_install.sh
./fix_install.sh
```

### **🛠️ OPTION 2 - CORRECTION MANUELLE**
```bash
cd /home/rono/THEBOT

# Activer environnement virtuel
source venv_thebot/bin/activate

# Installer dépendances manquantes
pip install matplotlib PyQt6 plotly ipywidgets

# Mettre à jour requirements
pip install -r requirements.txt

# Réinstaller THEBOT
pip install -e .

# Tester l'application
./run_thebot.sh  # Option 1
```

---

## 🎯 **APRÈS CORRECTION**

Vous pourrez lancer :
```bash
cd /home/rono/THEBOT
./run_thebot.sh
# → Option 1 (Application Native) 
# → Application PyQt6 se lance sans erreur
```

---

## 🔍 **CAUSE DU PROBLÈME**

L'application native importait `matplotlib` même quand PyQt6 est disponible. 
**Correction appliquée :** Import conditionnel pour éviter l'erreur.

---

## ✅ **VALIDATION**

Après correction, ces commandes doivent fonctionner :
```bash
cd /home/rono/THEBOT
python -c "import matplotlib.pyplot as plt; print('✅ matplotlib OK')"
python -c "from src.thebot.gui.native_app import create_native_app; print('✅ App native OK')"
./run_thebot.sh  # → Option 1 → Application se lance
```

**La correction est poussée sur GitHub, votre prochaine installation sera automatiquement corrigée ! 🚀**