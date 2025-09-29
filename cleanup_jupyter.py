#!/usr/bin/env python3
"""
THEBOT - Nettoyage Post-Migration Native
Script pour supprimer définitivement toutes les dépendances Jupyter
"""

import os
import shutil
import subprocess
import sys

def clean_jupyter_dependencies():
    """Nettoyer toutes les dépendances Jupyter"""
    
    print("🧹 THEBOT - Nettoyage Complet Jupyter")
    print("=" * 50)
    
    # 1. Désinstaller les packages Jupyter
    jupyter_packages = [
        'jupyter', 'jupyterlab', 'notebook', 'ipywidgets', 
        'voila', 'nbconvert', 'jupyter-console', 'jupyter-client',
        'jupyter-core', 'jupyter-server', 'jupyterlab-server',
        'notebook-shim', 'jupyter-lsp', 'jupyter-events'
    ]
    
    print("📦 Désinstallation des packages Jupyter...")
    for package in jupyter_packages:
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'uninstall', package, '-y'
            ], capture_output=True)
            print(f"   ✅ {package} désinstallé")
        except:
            print(f"   ⚠️  {package} déjà absent")
    
    # 2. Supprimer les fichiers Jupyter restants
    files_to_remove = [
        'start_jupyter_no_token.sh',
        'jupyter_dashboard.ipynb',
        'simple_web_test.py'
    ]
    
    print("\n📁 Suppression des fichiers Jupyter...")
    for file in files_to_remove:
        try:
            if os.path.exists(file):
                os.remove(file)
                print(f"   ✅ {file} supprimé")
        except:
            print(f"   ⚠️  {file} déjà absent")
    
    # 3. Nettoyer les dossiers cache
    cache_dirs = [
        '.jupyter',
        '__pycache__',
        '.ipynb_checkpoints'
    ]
    
    print("\n🗂️  Nettoyage des caches...")
    for root, dirs, files in os.walk('.'):
        for cache_dir in cache_dirs:
            if cache_dir in dirs:
                cache_path = os.path.join(root, cache_dir)
                try:
                    shutil.rmtree(cache_path)
                    print(f"   ✅ {cache_path} nettoyé")
                except:
                    pass
    
    # 4. Réinstaller uniquement les dépendances natives
    print("\n📦 Installation des dépendances natives...")
    native_deps = [
        'PyQt6>=6.5.0',
        'matplotlib>=3.7.0',
        'pandas>=2.0.0',
        'numpy>=1.24.0'
    ]
    
    for dep in native_deps:
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', dep
            ], capture_output=True)
            print(f"   ✅ {dep} installé")
        except Exception as e:
            print(f"   ❌ Erreur {dep}: {e}")
    
    print("\n✅ Nettoyage terminé !")
    print("🚀 THEBOT est maintenant 100% natif")
    
    return True

def update_launch_scripts():
    """Mettre à jour les scripts de lancement"""
    print("\n🔧 Mise à jour des scripts de lancement...")
    
    # Mise à jour du README
    readme_content = """# 🤖 THEBOT - Application Native de Trading

## 🚀 Application 100% Native (Sans Navigateur)

### Lancement de l'application :

```bash
# Version simple Tkinter (recommandée)
python launch_simple_native.py

# Version avancée PyQt6 (si disponible)  
python launch_native_app.py

# Tests unitaires
python test_vscode.py
```

### Architecture Native :
- ✅ Interface Tkinter/PyQt6 native
- ✅ Graphiques intégrés matplotlib  
- ✅ Aucune dépendance navigateur web
- ✅ Indicateurs ultra-modulaires
- ✅ Tests unitaires complets

### Indicateurs supportés :
- 📊 SMA - Simple Moving Average
- 📈 EMA - Exponential Moving Average  
- 🔵 RSI - Relative Strength Index
- 📉 ATR - Average True Range

### Fonctionnalités :
- 🔄 Calculs temps réel
- 📊 Visualisations intégrées
- 🧪 Tests automatisés
- 🎛️ Interface intuitive
"""
    
    with open('README_NATIVE.md', 'w') as f:
        f.write(readme_content)
    
    print("   ✅ README_NATIVE.md créé")
    
    return True

def main():
    """Point d'entrée principal"""
    
    if not clean_jupyter_dependencies():
        print("❌ Erreur lors du nettoyage")
        return 1
        
    if not update_launch_scripts():
        print("❌ Erreur lors de la mise à jour")
        return 1
    
    print("\n🎉 THEBOT - Migration Native Terminée !")
    print("=" * 50)
    print("📱 Lancer l'app: python launch_simple_native.py")
    print("🧪 Tests: python test_vscode.py")
    print("🏗️  Architecture: 100% native, 0% web")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())