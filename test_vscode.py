#!/usr/bin/env python3
"""
THEBOT - Test Simple Direct
Fichier de test à exécuter dans VS Code
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_simple():
    """Test ultra-simple des indicateurs"""
    print("🚀 THEBOT - Test VS Code")
    print("=" * 30)
    
    # Test des imports
    try:
        from thebot.indicators.basic.sma import SMAIndicator
        print("✅ Import SMA OK")
        
        from thebot.indicators.basic.ema import EMAIndicator
        print("✅ Import EMA OK")
        
        from thebot.indicators.volatility.atr import ATRIndicator
        print("✅ Import ATR OK")
        
        from thebot.indicators.oscillators.rsi import RSIIndicator
        print("✅ Import RSI OK")
        
        print()
        print("🎉 TOUS LES IMPORTS RÉUSSIS !")
        print("✅ THEBOT est correctement installé")
        print("📊 Architecture ultra-modulaire opérationnelle")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_unit_tests():
    """Lancer les tests unitaires"""
    print("\n🧪 LANCEMENT DES TESTS UNITAIRES")
    print("=" * 35)
    
    import subprocess
    
    try:
        # Lancer pytest avec l'interpréteur Python courant
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/unit/indicators/', 
            '-v', '--tb=short'
        ], capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        if result.returncode == 0:
            print("✅ TOUS LES TESTS PASSENT !")
        else:
            print(f"⚠️ Code de retour: {result.returncode}")
            
    except Exception as e:
        print(f"❌ Erreur tests: {e}")

if __name__ == "__main__":
    print("🤖 THEBOT - Test Direct VS Code")
    print("=" * 40)
    
    # Test imports
    if test_simple():
        print("\n" + "="*40)
        
        # Demander si lancer les tests
        response = input("Lancer les tests unitaires ? [y/N]: ")
        if response.lower() in ['y', 'yes', 'o', 'oui']:
            run_unit_tests()
    
    print("\n🎯 Test terminé !")
    input("Appuyez sur Entrée pour quitter...")