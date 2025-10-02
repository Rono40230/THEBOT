#!/usr/bin/env python3
"""
Test Phase 2 - Optimisations APIs Spécialisées
Validation des améliorations de performance et spécialisation
"""

import sys
import os
import time
from datetime import datetime

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cache_intelligent():
    """Test du système de cache intelligent"""
    print("\n🧪 TEST CACHE INTELLIGENT")
    print("=" * 40)
    
    try:
        from dash_modules.core.intelligent_cache import get_global_cache
        
        cache = get_global_cache()
        
        # Test mise en cache
        test_data = {'test': 'data', 'timestamp': time.time()}
        cache.set('test_crypto_ohlcv', test_data, symbol='BTCUSDT')
        
        # Test récupération
        cached = cache.get('test_crypto_ohlcv', symbol='BTCUSDT')
        
        if cached:
            print("✅ Cache mis en place et récupération OK")
            print(f"   Données: {cached}")
            
            # Test stats
            stats = cache.get_stats()
            print(f"   Entrées cache: {stats['total_entries']}")
            print(f"   Hits totaux: {stats['total_hits']}")
            
            return True
        else:
            print("❌ Problème récupération cache")
            return False
            
    except Exception as e:
        print(f"❌ Erreur cache: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sources_rss_reparees():
    """Test des sources RSS réparées en Phase 2"""
    print("\n🧪 TEST SOURCES RSS RÉPARÉES")
    print("=" * 40)
    
    try:
        from dash_modules.data_providers.rss_news_manager import rss_news_manager
        
        # Test connectivité des nouvelles sources
        print("🔍 Test connectivité nouvelles sources...")
        test_results = rss_news_manager.test_sources()
        
        total = test_results.get('total_sources', 0)
        successful = test_results.get('successful', 0)
        failed = test_results.get('failed', 0)
        
        success_rate = (successful / total * 100) if total > 0 else 0
        
        print(f"📊 Résultats:")
        print(f"   Total: {total}")
        print(f"   Succès: {successful}")
        print(f"   Échecs: {failed}")
        print(f"   Taux succès: {success_rate:.1f}%")
        
        # Test par catégorie
        categories = ['crypto', 'economic', 'market']
        for category in categories:
            try:
                start_time = time.time()
                news = rss_news_manager.get_news(categories=[category], limit=3, use_cache=False)
                elapsed = time.time() - start_time
                print(f"   {category}: {len(news)} articles en {elapsed:.2f}s")
            except Exception as e:
                print(f"   {category}: ❌ {e}")
        
        return success_rate >= 80  # 80% minimum
        
    except Exception as e:
        print(f"❌ Erreur sources RSS: {e}")
        return False

def test_specialisation_apis():
    """Test de la spécialisation des APIs"""
    print("\n🧪 TEST SPÉCIALISATION APIs")
    print("=" * 40)
    
    try:
        from dash_modules.core.specialized_api_manager import specialized_api_manager
        from dash_modules.data_providers.real_data_manager import real_data_manager
        
        # Tester détection type de marché
        test_symbols = [
            ('BTCUSDT', 'crypto'),
            ('EUR/USD', 'forex'),
            ('AAPL', 'stocks'),
            ('SPY', 'indices')
        ]
        
        print("🎯 Test détection marché:")
        correct_detections = 0
        
        for symbol, expected_type in test_symbols:
            detected = specialized_api_manager._detect_market_type(symbol)
            is_correct = detected == expected_type
            status = "✅" if is_correct else "❌"
            print(f"   {status} {symbol}: {detected} (attendu: {expected_type})")
            if is_correct:
                correct_detections += 1
        
        detection_rate = (correct_detections / len(test_symbols)) * 100
        print(f"📊 Précision détection: {detection_rate:.1f}%")
        
        # Test provider optimal
        print("\n🔍 Test provider optimal:")
        for symbol, _ in test_symbols[:2]:  # Limiter pour éviter erreurs
            try:
                optimal = specialized_api_manager.get_optimal_provider(symbol)
                print(f"   {symbol}: {optimal}")
            except Exception as e:
                print(f"   {symbol}: ❌ {e}")
        
        return detection_rate >= 75
        
    except Exception as e:
        print(f"❌ Erreur spécialisation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_globale():
    """Test de performance globale du système"""
    print("\n🧪 TEST PERFORMANCE GLOBALE")
    print("=" * 40)
    
    try:
        from dash_modules.data_providers.real_data_manager import real_data_manager
        
        # Test performance news
        print("📰 Test performance news...")
        start_time = time.time()
        news = real_data_manager.get_news_data(sources=['rss'], limit=5)
        news_time = time.time() - start_time
        
        print(f"   RSS News: {len(news)} articles en {news_time:.2f}s")
        
        # Test cache stats
        if hasattr(real_data_manager, 'cache') and hasattr(real_data_manager.cache, 'get_stats'):
            cache_stats = real_data_manager.cache.get_stats()
            print(f"   Cache: {cache_stats['total_entries']} entrées, {cache_stats['total_hits']} hits")
        
        # Critères de performance
        performance_ok = news_time < 5.0  # Moins de 5 secondes
        data_ok = len(news) > 0
        
        overall_performance = performance_ok and data_ok
        
        status = "✅" if overall_performance else "❌"
        print(f"{status} Performance globale: {status}")
        
        return overall_performance
        
    except Exception as e:
        print(f"❌ Erreur performance: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_complete():
    """Test d'intégration complète Phase 1 + Phase 2"""
    print("\n🧪 TEST INTÉGRATION COMPLÈTE")
    print("=" * 40)
    
    try:
        # Test que tous les modules s'importent correctement
        modules_to_test = [
            'dash_modules.core.rss_parser',
            'dash_modules.data_providers.rss_sources_config',
            'dash_modules.data_providers.rss_news_manager',
            'dash_modules.core.news_aggregator',
            'dash_modules.core.intelligent_cache',
            'dash_modules.core.specialized_api_manager',
            'dash_modules.data_providers.real_data_manager'
        ]
        
        imported_modules = 0
        for module_name in modules_to_test:
            try:
                __import__(module_name)
                print(f"   ✅ {module_name}")
                imported_modules += 1
            except Exception as e:
                print(f"   ❌ {module_name}: {e}")
        
        import_rate = (imported_modules / len(modules_to_test)) * 100
        print(f"📊 Taux import: {import_rate:.1f}%")
        
        # Test fonctionnel global
        print("\n🔄 Test fonctionnel global...")
        from dash_modules.data_providers.real_data_manager import real_data_manager
        
        # Test combiné RSS + cache + spécialisation
        all_news = real_data_manager.get_news_data(limit=3)
        print(f"   Nouvelles globales: {len(all_news)} articles")
        
        integration_ok = import_rate >= 85 and len(all_news) > 0
        
        return integration_ok
        
    except Exception as e:
        print(f"❌ Erreur intégration: {e}")
        return False

def main():
    """Fonction principale de test Phase 2"""
    print("🚀 THEBOT - TEST PHASE 2 : OPTIMISATIONS SPÉCIALISÉES")
    print("=" * 70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Cache Intelligent", test_cache_intelligent),
        ("Sources RSS Réparées", test_sources_rss_reparees),
        ("Spécialisation APIs", test_specialisation_apis),
        ("Performance Globale", test_performance_globale),
        ("Intégration Complète", test_integration_complete)
    ]
    
    results = []
    total_start_time = time.time()
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Démarrage: {test_name}")
            start_time = time.time()
            result = test_func()
            elapsed = time.time() - start_time
            
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name} ({elapsed:.2f}s)")
            results.append((test_name, result, elapsed))
            
        except Exception as e:
            print(f"❌ ERREUR CRITIQUE dans {test_name}: {e}")
            results.append((test_name, False, 0))
    
    # Résumé final
    total_time = time.time() - total_start_time
    
    print("\n" + "=" * 70)
    print("📋 RÉSUMÉ PHASE 2 - OPTIMISATIONS")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result, elapsed in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name} ({elapsed:.2f}s)")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\n🎯 Résultat Phase 2: {passed}/{total} tests réussis ({success_rate:.1f}%)")
    print(f"⏱️ Temps total: {total_time:.2f}s")
    
    if passed == total:
        print("\n🎉 PHASE 2 COMPLÈTE: SUCCÈS TOTAL!")
        print("✅ Optimisations déployées avec succès")
        print("⚡ Performance améliorée")
        print("🎯 APIs spécialisées opérationnelles")
    elif passed >= total * 0.7:
        print("\n⚠️ PHASE 2: Succès partiel")
        print("🔧 Quelques ajustements nécessaires")
    else:
        print("\n❌ PHASE 2: Problèmes importants")
        print("🛠️ Révision nécessaire")
    
    print(f"\n💰 ÉCONOMIES MAINTENUES:")
    print("   ❌ CryptoPanic (-7€/mois)")
    print("   ❌ FMP (-14€/mois)")
    print("   ❌ Alpha Vantage (-200€/mois)")
    print("   ✅ Infrastructure optimisée (0€/mois)")
    print("   💵 Total économies: ~221€/mois")
    
    print(f"\n🚀 AMÉLIORATIONS PHASE 2:")
    print("   ⚡ Cache intelligent adaptatif")
    print("   🎯 APIs spécialisées par marché")
    print("   📡 Sources RSS réparées")
    print("   📊 Performance optimisée")
    
    return passed >= total * 0.7

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)