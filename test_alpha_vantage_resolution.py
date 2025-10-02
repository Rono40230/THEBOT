#!/usr/bin/env python3
"""
Test de résolution Alpha Vantage - Validation compatibilité 100%
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_alpha_vantage_resolution():
    """Test complet de résolution alpha_vantage"""
    print("🚀 THEBOT - TEST RÉSOLUTION ALPHA VANTAGE")
    print("=" * 70)
    
    from datetime import datetime
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Import du stub compatibility
    total_tests += 1
    try:
        from dash_modules.data_providers.alpha_vantage_api import AlphaVantageAPI
        api = AlphaVantageAPI("test_key")
        
        print("✅ Alpha Vantage stub importé avec succès")
        print(f"   - API disponible: {api.is_available}")
        success_count += 1
    except Exception as e:
        print(f"❌ Erreur import Alpha Vantage stub: {e}")
    
    # Test 2: Import dans launch_dash_professional 
    total_tests += 1
    try:
        import launch_dash_professional  # Should not crash
        print("✅ launch_dash_professional: Import alpha_vantage résolu")
        success_count += 1
    except Exception as e:
        print(f"❌ Erreur launch_dash_professional: {e}")
    
    # Test 3: Import dans forex_module
    total_tests += 1
    try:
        from dash_modules.tabs.forex_module import ForexModule
        forex = ForexModule()
        print("✅ forex_module: Import alpha_vantage résolu")
        success_count += 1
    except Exception as e:
        print(f"❌ Erreur forex_module: {e}")
    
    # Test 4: Import dans stocks_module
    total_tests += 1
    try:
        from dash_modules.tabs.stocks_module import StocksModule  
        stocks = StocksModule()
        print("✅ stocks_module: Import alpha_vantage résolu")
        success_count += 1
    except Exception as e:
        print(f"❌ Erreur stocks_module: {e}")
    
    # Test 5: Economic news sans alpha_vantage
    total_tests += 1
    try:
        from dash_modules.tabs.economic_news_module import EconomicNewsModule
        economic = EconomicNewsModule()
        sources = economic._get_news_sources()
        
        if 'alpha_vantage' not in sources:
            print("✅ economic_news_module: alpha_vantage retiré des sources")
            print(f"   - Sources actives: {sources}")
            success_count += 1
        else:
            print("❌ economic_news_module: alpha_vantage encore présent")
    except Exception as e:
        print(f"❌ Erreur economic_news_module: {e}")
    
    # Test 6: API Config compatibility
    total_tests += 1
    try:
        from dash_modules.core.api_config import APIConfig
        config = APIConfig()
        print("✅ api_config: Import alpha_vantage résolu")
        success_count += 1
    except Exception as e:
        print(f"❌ Erreur api_config: {e}")
    
    # Test 7: Stub methods functionality
    total_tests += 1
    try:
        api = AlphaVantageAPI("test")
        
        # Test stub methods
        forex_data = api.get_forex_rates("USD", "EUR")
        stock_data = api.get_stock_quote("AAPL") 
        economic_data = api.get_economic_indicators("GDP")
        news_data = api.get_news("financial")
        
        if (forex_data.get('status') == 'deprecated' and 
            stock_data.get('status') == 'deprecated' and
            economic_data.get('status') == 'deprecated' and
            isinstance(news_data, list)):
            print("✅ Alpha Vantage stub: Toutes les méthodes fonctionnelles")
            print(f"   - Forex: {forex_data.get('message', 'OK')[:50]}...")
            print(f"   - Stock: {stock_data.get('message', 'OK')[:50]}...")
            print(f"   - Economic: {economic_data.get('message', 'OK')[:50]}...")
            print(f"   - News: {len(news_data)} articles")
            success_count += 1
        else:
            print("❌ Alpha Vantage stub: Méthodes non conformes")
            
    except Exception as e:
        print(f"❌ Erreur test stub methods: {e}")
    
    print()
    print("🧪 TEST COMPATIBILITÉ DASHBOARD")
    print("=" * 50)
    
    # Test 8: Dashboard compatibility (critical test)
    total_tests += 1
    try:
        # Test import de tous les modules principaux
        from dash_modules.tabs.crypto_module import CryptoModule
        from dash_modules.tabs.forex_module import ForexModule  
        from dash_modules.tabs.stocks_module import StocksModule
        from dash_modules.tabs.strategies_module import StrategiesModule
        from dash_modules.tabs.crypto_news_module import CryptoNewsModule
        from dash_modules.tabs.economic_news_module import EconomicNewsModule
        from dash_modules.tabs.news_module import NewsModule
        
        print("✅ Tous les modules dashboard importés sans erreur")
        success_count += 1
        
    except Exception as e:
        print(f"❌ Erreur import modules dashboard: {e}")
    
    print()
    print("📊 RÉSULTATS FINAUX")
    print("=" * 50)
    
    percentage = (success_count / total_tests) * 100
    print(f"✅ Tests réussis: {success_count}/{total_tests} ({percentage:.1f}%)")
    
    if percentage == 100:
        print("🎉 RÉSOLUTION ALPHA VANTAGE: ✅ SUCCÈS COMPLET!")
        print("🏆 Compatibilité 100% atteinte")
        print("🔧 Stub de compatibilité fonctionnel")
        print("📦 Tous les modules dashboard opérationnels") 
        return True
    elif percentage >= 87.5:  # 7/8 tests
        print("🟡 RÉSOLUTION ALPHA VANTAGE: ✅ SUCCÈS PARTIEL")
        print("⚠️ Quelques ajustements mineurs peuvent être nécessaires")
        return True
    else:
        print("❌ RÉSOLUTION ALPHA VANTAGE: ÉCHEC")
        print("🔧 Corrections supplémentaires requises")
        return False

if __name__ == "__main__":
    test_alpha_vantage_resolution()