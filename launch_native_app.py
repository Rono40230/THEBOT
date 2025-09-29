#!/usr/bin/env python3
"""
THEBOT - Lanceur Application Native
Point d'entrée principal pour l'application PyQt6
"""

import sys
import os

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Lancer l'application native THEBOT"""
    print("🚀 THEBOT - Lancement Application Native")
    print("=" * 50)
    
    try:
        # Vérifier PyQt6
        try:
            from PyQt6.QtWidgets import QApplication
            print("✅ PyQt6 disponible")
        except ImportError:
            print("❌ PyQt6 non installé")
            print("📦 Installation requise: pip install PyQt6 PyQt6-tools")
            return 1
            
        # Vérifier les modules THEBOT
        try:
            from thebot.indicators.basic.sma import SMAIndicator
            from thebot.indicators.basic.ema import EMAIndicator
            from thebot.indicators.volatility.atr import ATRIndicator
            from thebot.indicators.oscillators.rsi import RSIIndicator
            print("✅ Modules THEBOT chargés")
        except ImportError as e:
            print(f"❌ Erreur import THEBOT: {e}")
            return 1
            
        # Lancer l'interface PyQt6
        from thebot.gui.pyqt import main as pyqt_main
        print("🖥️  Lancement interface native...")
        
        pyqt_main()
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
        return 0
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())