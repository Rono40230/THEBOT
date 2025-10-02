#!/usr/bin/env python3
"""
Test HuggingFace Configuration
"""

from dash_modules.core.api_config import api_config
from dash_modules.ai_engine.smart_ai_manager import SmartAIManager

def test_huggingface_config():
    """Tester la configuration HuggingFace"""
    print("🧪 Test de la configuration HuggingFace")
    
    # 1. Vérifier que HuggingFace est dans la config
    ai_providers = api_config.config.get("providers", {}).get("ai_providers", [])
    hf_provider = None
    
    for provider in ai_providers:
        if provider.get("name") == "HuggingFace":
            hf_provider = provider
            break
    
    if hf_provider:
        print("✅ HuggingFace trouvé dans la configuration")
        print(f"   Status: {hf_provider.get('status')}")
        print(f"   API Key: {'Configurée' if hf_provider.get('config', {}).get('api_key') else 'Non configurée'}")
        print(f"   Description: {hf_provider.get('description')}")
    else:
        print("❌ HuggingFace non trouvé dans la configuration")
        return
    
    # 2. Tester Smart AI Manager
    smart_ai = SmartAIManager()
    smart_ai.initialize_engines()
    
    # 3. Tester récupération clé API
    api_key = smart_ai._get_huggingface_api_key()
    print(f"🔑 Clé API récupérée: {'Oui' if api_key else 'Non'}")
    
    # 4. Tester quota check
    can_use_hf = smart_ai._check_huggingface_quota()
    print(f"📊 Peut utiliser HuggingFace: {'Oui' if can_use_hf else 'Non'}")
    
    # 5. Tester sélection AI
    best_ai = smart_ai.choose_best_ai("sentiment")
    print(f"🧠 Meilleure IA pour sentiment: {best_ai}")
    
    print("\n📋 Résumé des capacités IA:")
    capabilities = smart_ai.get_ai_capabilities()
    for ai_type, info in capabilities.items():
        print(f"   {ai_type}: {'Disponible' if info['available'] else 'Indisponible'}")

if __name__ == "__main__":
    test_huggingface_config()