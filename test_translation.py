#!/usr/bin/env python3
"""
Test de traduction et boutons RSS
"""

from dash_modules.ai_engine.smart_ai_manager import SmartAIManager

def test_translation():
    """Tester la fonction de traduction"""
    print("🧪 Test de traduction français")
    
    # Initialiser AI Manager
    smart_ai = SmartAIManager()
    smart_ai.initialize_engines()
    
    # Textes à traduire (exemples anglais typiques)
    test_texts = [
        "Bitcoin price surges to new highs",
        "Stock market shows strong growth this week",
        "Federal Reserve raises interest rates",
        "Technology stocks face pressure from inflation",
        "Cryptocurrency market sees volatility"
    ]
    
    print("\n📖 Traductions test :")
    for text in test_texts:
        translated = smart_ai.translate_to_french(text)
        print(f"   EN: {text}")
        print(f"   FR: {translated}")
        print()
    
    print("✅ Test de traduction terminé")

if __name__ == "__main__":
    test_translation()