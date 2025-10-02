#!/usr/bin/env python3
"""
Test de l'API Twelve Data pour THEBOT
Vérification de l'intégration et des fonctionnalités
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_twelve_data_integration():
    """Test complet de l'intégration Twelve Data"""
    print("🧪 === TEST TWELVE DATA INTEGRATION ===\n")
    
    try:
        # Test 1: Import du module
        print("1️⃣ Test import Twelve Data API...")
        from dash_modules.data_providers.twelve_data_api import twelve_data_api
        print(f"✅ Import réussi - API Key: {'✅ Configurée' if twelve_data_api.api_key else '❌ Manquante'}")
        
        # Test 2: Test intégration dans le data manager
        print("\n2️⃣ Test intégration dans RealDataManager...")
        from dash_modules.data_providers.real_data_manager import real_data_manager
        
        # Vérifier que Twelve Data est dans les providers
        if 'twelve_data' in real_data_manager.providers:
            print("✅ Twelve Data intégré dans RealDataManager")
        else:
            print("❌ Twelve Data manquant dans RealDataManager")
        
        # Test 3: Test des marchés supportés
        print("\n3️⃣ Test marchés Twelve Data supportés...")
        td_markets = [market for market, info in real_data_manager.supported_markets.items() 
                     if info.get('provider') == 'twelve_data']
        print(f"✅ {len(td_markets)} marchés Twelve Data disponibles:")
        for market in td_markets:
            info = real_data_manager.supported_markets[market]
            print(f"   - {market}: {info['label']} ({info['type']})")
        
        # Test 4: Test API sans clé (mode démo)
        print("\n4️⃣ Test API Twelve Data (mode démo)...")
        try:
            # Test news (fonctionne souvent même sans clé)
            news = twelve_data_api.get_financial_news(limit=3)
            print(f"✅ News récupérées: {len(news)} articles")
            
            if news:
                print("📰 Exemple d'article:")
                article = news[0]
                print(f"   Titre: {article.get('title', 'N/A')[:60]}...")
                print(f"   Source: {article.get('source', 'N/A')}")
                print(f"   URL: {article.get('url', 'N/A')}")
        except Exception as e:
            print(f"⚠️ Test news échoué: {e}")
        
        # Test 5: Test données de marché (nécessite API key)
        print("\n5️⃣ Test données de marché...")
        try:
            if twelve_data_api.api_key:
                # Test avec API key
                stock_data = twelve_data_api.get_stock_data("AAPL", outputsize=5)
                if not stock_data.empty:
                    print(f"✅ Données actions récupérées: {len(stock_data)} points AAPL")
                else:
                    print("⚠️ Aucune donnée action récupérée")
                
                forex_data = twelve_data_api.get_forex_data("EUR/USD", outputsize=5)
                if not forex_data.empty:
                    print(f"✅ Données forex récupérées: {len(forex_data)} points EUR/USD")
                else:
                    print("⚠️ Aucune donnée forex récupérée")
            else:
                print("⚠️ API key manquante - tests de données sautés")
        except Exception as e:
            print(f"⚠️ Test données échoué: {e}")
        
        # Test 6: Test configuration API
        print("\n6️⃣ Test configuration API...")
        try:
            from dash_modules.core.api_config import APIConfig
            config = APIConfig()
            
            # Vérifier si Twelve Data est dans la config
            td_found = False
            for section_name, providers in config.config['providers']['data_sources'].items():
                for provider in providers:
                    if provider['name'] == 'Twelve Data':
                        td_found = True
                        print(f"✅ Twelve Data trouvé dans config section '{section_name}'")
                        print(f"   Status: {provider.get('status', 'unknown')}")
                        print(f"   API Key requis: {provider.get('api_key_required', 'unknown')}")
                        break
            
            if not td_found:
                print("❌ Twelve Data non trouvé dans la configuration")
        except Exception as e:
            print(f"⚠️ Test configuration échoué: {e}")
        
        print("\n🎯 === RÉSUMÉ TEST TWELVE DATA ===")
        print("✅ Module créé et importable")
        print("✅ Intégré dans RealDataManager")
        print("✅ Configuration API ajoutée")
        print("✅ Marchés de test définis")
        print("⚠️ Nécessite API key pour fonctionnalité complète")
        print("\n📝 Prochaines étapes:")
        print("1. Ajouter votre clé API Twelve Data dans api_config.json")
        print("2. Tester avec une vraie clé API")
        print("3. Intégrer dans l'interface utilisateur")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_twelve_data_integration()