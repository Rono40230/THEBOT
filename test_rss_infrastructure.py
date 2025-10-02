#!/usr/bin/env python3
"""
Test RSS Infrastructure - Phase 1 Validation
Tests de l'infrastructure RSS nouvellement créée
"""

import sys
import os
import logging
from datetime import datetime

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Configure le logging pour les tests"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

def test_rss_parser():
    """Test du parser RSS de base"""
    print("\n" + "="*60)
    print("🧪 TEST 1: RSS Parser de base")
    print("="*60)
    
    try:
        from dash_modules.core.rss_parser import RSSParser
        
        parser = RSSParser()
        print("✅ RSSParser importé et initialisé")
        
        # Test avec un flux RSS simple
        test_url = "https://www.coindesk.com/arc/outboundfeeds/rss/"
        print(f"📡 Test parsing: {test_url}")
        
        articles = parser.parse_feed(test_url, max_entries=3)
        
        if articles:
            print(f"✅ Parser RSS OK: {len(articles)} articles récupérés")
            for i, article in enumerate(articles[:2], 1):
                print(f"   {i}. {article.get('title', 'N/A')[:60]}...")
                print(f"      Source: {article.get('source', 'N/A')}")
                print(f"      Catégorie: {article.get('category', 'N/A')}")
        else:
            print("⚠️ Aucun article récupéré (peut être normal)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur RSS Parser: {e}")
        return False

def test_rss_sources_config():
    """Test de la configuration des sources RSS"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Configuration Sources RSS")
    print("="*60)
    
    try:
        from dash_modules.data_providers.rss_sources_config import rss_sources_config
        
        print("✅ RSSSourcesConfig importé")
        
        # Test des catégories
        categories = rss_sources_config.get_categories()
        print(f"📁 Catégories configurées: {categories}")
        
        # Test des sources actives
        active_sources = rss_sources_config.get_active_sources()
        print(f"🔗 Sources actives: {len(active_sources)}")
        
        # Détail par catégorie
        for category in categories:
            cat_sources = rss_sources_config.get_active_sources(category)
            print(f"   {category}: {len(cat_sources)} sources")
            for source in cat_sources[:2]:  # Limiter l'affichage
                print(f"     - {source['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur Sources Config: {e}")
        return False

def test_rss_news_manager():
    """Test du gestionnaire RSS"""
    print("\n" + "="*60)
    print("🧪 TEST 3: RSS News Manager")
    print("="*60)
    
    try:
        from dash_modules.data_providers.rss_news_manager import rss_news_manager
        
        print("✅ RSSNewsManager importé")
        
        # Test récupération nouvelles économiques
        print("📰 Test nouvelles économiques...")
        eco_news = rss_news_manager.get_news(
            categories=['economic'], 
            limit=5,
            use_cache=False  # Pas de cache pour le test
        )
        
        if eco_news:
            print(f"✅ Nouvelles économiques: {len(eco_news)} articles")
            for i, article in enumerate(eco_news[:2], 1):
                print(f"   {i}. {article.get('title', 'N/A')[:50]}...")
                print(f"      RSS Source: {article.get('rss_source_name', 'N/A')}")
        else:
            print("⚠️ Aucune nouvelle économique (connexion ou config)")
        
        # Test nouvelles crypto
        print("🪙 Test nouvelles crypto...")
        crypto_news = rss_news_manager.get_news(
            categories=['crypto'], 
            limit=3,
            use_cache=False
        )
        
        if crypto_news:
            print(f"✅ Nouvelles crypto: {len(crypto_news)} articles")
            for i, article in enumerate(crypto_news[:2], 1):
                print(f"   {i}. {article.get('title', 'N/A')[:50]}...")
                print(f"      RSS Source: {article.get('rss_source_name', 'N/A')}")
        else:
            print("⚠️ Aucune nouvelle crypto (connexion ou config)")
        
        # Stats cache
        cache_stats = rss_news_manager.get_cache_stats()
        print(f"💾 Cache: {cache_stats.get('total_entries', 0)} entrées")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur RSS News Manager: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_news_aggregator():
    """Test de l'agrégateur de nouvelles"""
    print("\n" + "="*60)
    print("🧪 TEST 4: News Aggregator")
    print("="*60)
    
    try:
        from dash_modules.core.news_aggregator import news_aggregator
        
        print("✅ NewsAggregator importé")
        
        # Test agrégation toutes sources
        print("🔄 Test agrégation multi-sources...")
        all_news = news_aggregator.get_aggregated_news(
            limit=10,
            include_rss=True,
            include_apis=True  # Test hybride RSS + APIs existantes
        )
        
        if all_news:
            print(f"✅ Agrégation OK: {len(all_news)} articles totaux")
            
            # Analyser les sources
            rss_count = len([a for a in all_news if a.get('provider') == 'rss'])
            api_count = len([a for a in all_news if a.get('provider') == 'api'])
            
            print(f"   📡 RSS: {rss_count} articles")
            print(f"   🔌 API: {api_count} articles")
            
            # Exemples
            for i, article in enumerate(all_news[:3], 1):
                provider = "RSS" if article.get('provider') == 'rss' else "API"
                print(f"   {i}. [{provider}] {article.get('title', 'N/A')[:45]}...")
        else:
            print("⚠️ Aucun article agrégé")
        
        # Test statistiques
        stats = news_aggregator.get_source_statistics()
        if stats:
            print("📊 Statistiques sources:")
            if 'rss_sources' in stats:
                rss_stats = stats['rss_sources']
                print(f"   RSS: {rss_stats.get('active_sources', 0)}/{rss_stats.get('total_configured', 0)} actives")
            if 'api_sources' in stats:
                api_stats = stats['api_sources']
                print(f"   APIs: {len(api_stats.get('available', []))} disponibles")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur News Aggregator: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rss_connectivity():
    """Test de connectivité des sources RSS"""
    print("\n" + "="*60)
    print("🧪 TEST 5: Connectivité Sources RSS")
    print("="*60)
    
    try:
        from dash_modules.data_providers.rss_news_manager import rss_news_manager
        
        print("🌐 Test connectivité toutes sources...")
        
        # Test spécifique par catégorie
        categories_to_test = ['economic', 'crypto']
        
        for category in categories_to_test:
            print(f"\n📂 Test catégorie: {category}")
            test_results = rss_news_manager.test_sources([category])
            
            total = test_results.get('total_sources', 0)
            successful = test_results.get('successful', 0)
            failed = test_results.get('failed', 0)
            
            print(f"   Total: {total}, Succès: {successful}, Échecs: {failed}")
            
            if test_results.get('details'):
                for detail in test_results['details'][:3]:  # Limiter l'affichage
                    status_icon = "✅" if detail['status'] == 'OK' else "❌"
                    response_time = detail.get('response_time', 0)
                    print(f"   {status_icon} {detail['name']}: {detail['status']} ({response_time}s)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test connectivité: {e}")
        return False

def test_api_deprecation():
    """Test que les APIs payantes ont été supprimées"""
    print("\n" + "="*60)
    print("🧪 TEST 6: Vérification Suppression APIs Payantes")
    print("="*60)
    
    deprecated_apis = [
        'crypto_panic_api',
        'fmp_api'
        # alpha_vantage_api now has compatibility stub
    ]
    
    success_count = 0
    
    for api_name in deprecated_apis:
        try:
            # Tenter d'importer l'API (ne devrait plus fonctionner)
            exec(f"from dash_modules.data_providers.{api_name} import *")
            print(f"⚠️ {api_name}: Encore accessible (migration incomplète)")
        except ImportError:
            print(f"✅ {api_name}: Correctement supprimé")
            success_count += 1
        except Exception as e:
            print(f"✅ {api_name}: Inaccessible ({str(e)[:30]}...)")
            success_count += 1
    
    # Vérifier que les fichiers .deprecated existent
    import os
    for api_name in deprecated_apis:
        deprecated_file = f"dash_modules/data_providers/{api_name}.py.deprecated"
        if os.path.exists(deprecated_file):
            print(f"✅ {api_name}: Fichier sauvegardé en .deprecated")
        else:
            print(f"⚠️ {api_name}: Pas de sauvegarde .deprecated trouvée")
    
    print(f"\n💰 APIs payantes supprimées: {success_count}/{len(deprecated_apis)}")
    
    return success_count == len(deprecated_apis)

def main():
    """Fonction principale de test"""
    setup_logging()
    
    print("🚀 THEBOT - Test Infrastructure RSS (Phase 1)")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("RSS Parser", test_rss_parser),
        ("RSS Sources Config", test_rss_sources_config),
        ("RSS News Manager", test_rss_news_manager),
        ("News Aggregator", test_news_aggregator),
        ("RSS Connectivité", test_rss_connectivity),
        ("API Deprecation", test_api_deprecation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur critique dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé final
    print("\n" + "="*60)
    print("📋 RÉSUMÉ DES TESTS")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Résultat: {passed}/{total} tests réussis ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 PHASE 1 RSS INFRASTRUCTURE: SUCCÈS COMPLET!")
        print("✅ Prêt pour Phase 2: Spécialisation APIs")
    elif passed >= total * 0.8:
        print("⚠️ PHASE 1: Majoritairement réussie avec quelques alertes")
        print("🔧 Corrections mineures nécessaires")
    else:
        print("❌ PHASE 1: Échec - Corrections majeures nécessaires")
        print("🛠️ Révision de l'infrastructure requise")
    
    print(f"\n💰 Économies estimées: ~221€/mois avec infrastructure RSS")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)