#!/usr/bin/env python3
"""
THEBOT - Launcher Script
Script de lancement rapide pour toutes les interfaces
"""

import sys
import os
import subprocess

def print_banner():
    """Afficher la bannière THEBOT"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         🤖 THEBOT TRADING PLATFORM                            ║
║                        Interface Selection Menu                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Choose your preferred interface:
    """)

def main():
    """Menu principal de sélection d'interface"""
    
    print_banner()
    
    options = {
        "1": {
            "name": "🚀 Ultra-Modern Native (RECOMMENDED)",
            "description": "Desktop native with CustomTkinter, 4 indicators (SMA, EMA, RSI, ATR)",
            "script": "launch_ultra_modern_native.py",
            "features": "✅ All 4 Indicators ✅ Modern UI ✅ Real-time ✅ Native Desktop"
        },
        "2": {
            "name": "🌐 Professional Web Dashboard",
            "description": "Dash Plotly web interface (opens in browser)",
            "script": "launch_dash_professional.py",
            "features": "✅ Professional Charts ✅ AI Dashboard ✅ Backtesting ✅ Economic Calendar"
        },
        "3": {
            "name": "🔧 Simple Native (Basic)",
            "description": "Simple Tkinter interface with all indicators",
            "script": "launch_simple_native.py",
            "features": "✅ All 4 Indicators ✅ Simple UI ✅ THEBOT Core Integration"
        },
        "4": {
            "name": "⚙️ Quick Test",
            "description": "Quick indicator validation test",
            "script": "quick_test.py",
            "features": "✅ Indicators Test ✅ Validation ✅ Quick Check"
        }
    }
    
    # Afficher les options
    for key, option in options.items():
        print(f"[{key}] {option['name']}")
        print(f"    {option['description']}")
        print(f"    {option['features']}")
        print()
    
    # Choix utilisateur
    while True:
        choice = input("Enter your choice (1-4) or 'q' to quit: ").strip().lower()
        
        if choice == 'q':
            print("🛑 Exiting THEBOT Launcher")
            return
            
        if choice in options:
            option = options[choice]
            script = option['script']
            
            print(f"\n🚀 Launching {option['name']}...")
            print(f"📄 Running: {script}")
            
            # Vérifier que le script existe
            if not os.path.exists(script):
                print(f"❌ Error: {script} not found!")
                continue
            
            # Lancer le script
            try:
                # Activer l'environnement virtuel et lancer
                cmd = f"source .venv/bin/activate && python {script}"
                subprocess.run(cmd, shell=True, check=True)
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Error launching {script}: {e}")
                print(f"💡 Try running manually: python {script}")
                
            except KeyboardInterrupt:
                print(f"\n🛑 {option['name']} stopped by user")
                
        else:
            print("❌ Invalid choice. Please select 1-4 or 'q'")


if __name__ == "__main__":
    main()