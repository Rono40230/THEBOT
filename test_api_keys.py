#!/usr/bin/env python3
"""
Test de la sauvegarde des clés API
"""

import json
import os
import time

def test_api_key_saving():
    """Test pour vérifier la sauvegarde des clés API"""
    
    # Vérifier si le fichier de configuration existe
    config_file = "/home/rono/THEBOT/api_config.json"
    
    if os.path.exists(config_file):
        print("📄 Fichier de configuration trouvé")
        
        # Afficher la date de modification
        mod_time = os.path.getmtime(config_file)
        mod_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mod_time))
        print(f"📅 Dernière modification: {mod_date}")
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Vérifier les clés API sauvegardées
        print("\n🔍 Clés API actuellement sauvegardées:")
        
        total_keys = 0
        configured_keys = 0
        
        for section_name, providers in config.get("providers", {}).get("data_sources", {}).items():
            if providers:  # Si la section n'est pas vide
                print(f"\n📁 Section: {section_name}")
                for provider in providers:
                    api_key = provider.get("config", {}).get("api_key", "")
                    if provider.get("api_key_required", False):
                        total_keys += 1
                        if api_key:
                            configured_keys += 1
                            status = "✅ CONFIGURÉE"
                            key_preview = f"{api_key[:8]}{'*' * 8}..."
                        else:
                            status = "❌ MANQUANTE"
                            key_preview = "Vide"
                        print(f"  🔑 {provider['name']}: {status} ({key_preview})")
                    else:
                        print(f"  ℹ️  {provider['name']}: Pas de clé requise")
        
        print(f"\n📊 Résumé: {configured_keys}/{total_keys} clés configurées")
        
        if configured_keys > 0:
            print("🎉 Des clés API ont été sauvegardées avec succès!")
        else:
            print("⚠️  Aucune clé API n'est encore configurée")
            
    else:
        print("❌ Aucun fichier de configuration trouvé")
        print("💡 Les clés seront sauvegardées après la première utilisation")

def monitor_config_changes():
    """Surveiller les changements du fichier de configuration"""
    config_file = "/home/rono/THEBOT/api_config.json"
    
    print(f"\n👀 Surveillance du fichier: {config_file}")
    print("⏱️  Vérification toutes les 2 secondes... (Ctrl+C pour arrêter)")
    
    last_mod_time = 0
    if os.path.exists(config_file):
        last_mod_time = os.path.getmtime(config_file)
    
    try:
        while True:
            time.sleep(2)
            if os.path.exists(config_file):
                current_mod_time = os.path.getmtime(config_file)
                if current_mod_time != last_mod_time:
                    print(f"\n🔄 Fichier modifié à {time.strftime('%H:%M:%S')}")
                    test_api_key_saving()
                    last_mod_time = current_mod_time
            else:
                if last_mod_time != 0:
                    print("\n❌ Fichier de configuration supprimé")
                    last_mod_time = 0
    except KeyboardInterrupt:
        print("\n⏹️  Surveillance arrêtée")

if __name__ == "__main__":
    print("🧪 Test de sauvegarde des clés API")
    print("=" * 50)
    
    # Test initial
    test_api_key_saving()
    
    # Demander si on veut surveiller les changements
    print("\n" + "=" * 50)
    choice = input("📊 Voulez-vous surveiller les changements en temps réel? (o/n): ").lower().strip()
    
    if choice in ['o', 'oui', 'y', 'yes']:
        monitor_config_changes()
    else:
        print("✅ Test terminé")