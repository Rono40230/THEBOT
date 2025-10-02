#!/usr/bin/env python3
"""
Test simple HuggingFace Configuration
"""
import json
import sys
import os

def test_config_file():
    """Tester le fichier de configuration"""
    print("🧪 Test de la configuration HuggingFace dans api_config.json")
    
    config_file = "/home/rono/THEBOT/api_config.json"
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        ai_providers = config.get("providers", {}).get("ai_providers", [])
        
        print(f"📊 Nombre de providers AI: {len(ai_providers)}")
        
        for provider in ai_providers:
            name = provider.get("name", "Unknown")
            status = provider.get("status", "unknown")
            api_key = provider.get("config", {}).get("api_key", "")
            
            print(f"   {name}: {status} - API Key: {'Configurée' if api_key else 'Non configurée'}")
            
            if name == "HuggingFace":
                print("✅ HuggingFace trouvé dans la configuration!")
                print(f"      Description: {provider.get('description', 'N/A')}")
                print(f"      Models: {provider.get('models', [])}")
                print(f"      Rate Limit: {provider.get('rate_limit', 'N/A')}")
                print(f"      Priority: {provider.get('priority', 'N/A')}")
                return True
        
        print("❌ HuggingFace non trouvé dans ai_providers")
        return False
        
    except FileNotFoundError:
        print(f"❌ Fichier de configuration non trouvé: {config_file}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    success = test_config_file()
    sys.exit(0 if success else 1)