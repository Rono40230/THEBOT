#!/usr/bin/env python3
"""
Test RSS Infrastructure Simple - Phase 1 Validation
Tests uniquement l'infrastructure RSS sans dépendances complexes
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
    print("🧪 TEST RSS Parser")
    print("="*60)
    
    try:
        from dash_modules.core.rss_parser import RSSParser
        
        parser = RSSParser()
        print("✅ RSSParser importé et initialisé")
        
        # Test avec un flux RSS qui fonctionne
        test_url = "https://www.coindesk.com/arc/outboundfeeds/rss/"
        print(f"📡 Test parsing: {test_url}")
        
        articles = parser.parse_feed(test_url, max_entries=5)
        
        if articles:
            print(f"✅ Parser RSS OK: {len(articles)} articles récupérés")
            for i, article in enumerate(articles[:3], 1):
                print(f"   {i}. {article.get('title', 'N/A')[:60]}...")
                print(f"      Source: {article.get('source', 'N/A')}")
                print(f"      Catégorie: {article.get('category', 'N/A')}")
        else:
            print("⚠️ Aucun article récupéré")
        
        return len(articles) > 0
        
    except Exception as e:
        print(f"❌ Erreur RSS Parser: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rss_sources_config():
    """Test de la configuration des sources RSS"""
    print("\n" + "="*60)
    print("🧪 TEST Configuration Sources RSS")
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
                print(f"     - {source['name']}: {source['url']}")
        
        return len(active_sources) > 0
        
    except Exception as e:
        print(f"❌ Erreur Sources Config: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rss_news_manager():
    """Test du gestionnaire RSS"""
    print("\n" + "="*60)
    print("🧪 TEST RSS News Manager")
    print("="*60)
    
    try:
        from dash_modules.data_providers.rss_news_manager import rss_news_manager
        
        print("✅ RSSNewsManager importé")
        
        # Test récupération nouvelles crypto (plus fiable)
        print("🪙 Test nouvelles crypto...")
        crypto_news = rss_news_manager.get_news(
            categories=['crypto'], 
            limit=5,
            use_cache=False  # Pas de cache pour le test
        )
        
        if crypto_news:
            print(f"✅ Nouvelles crypto: {len(crypto_news)} articles")
            for i, article in enumerate(crypto_news[:3], 1):
                print(f"   {i}. {article.get('title', 'N/A')[:50]}...")
                print(f"      RSS Source: {article.get('rss_source_name', 'N/A')}")
        else:
            print("⚠️ Aucune nouvelle crypto")
        
        # Stats cache
        cache_stats = rss_news_manager.get_cache_stats()
        print(f"💾 Cache: {cache_stats.get('total_entries', 0)} entrées")
        
        return len(crypto_news) > 0
        
    except Exception as e:
        print(f"❌ Erreur RSS News Manager: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_news_aggregator():
    """Test de l'agrégateur de nouvelles"""
    print("\n" + "="*60)
    print("🧪 TEST News Aggregator")
    print("="*60)
    
    try:
        from dash_modules.core.news_aggregator import news_aggregator
        
        print("✅ NewsAggregator importé")
        
        # Test agrégation RSS seulement pour éviter les dépendances
        print("🔄 Test agrégation RSS...")
        rss_news = news_aggregator.get_aggregated_news(
            categories=['crypto'],
            limit=5,
            include_rss=True,
            include_apis=False  # Éviter les APIs pour le test
        )
        
        if rss_news:
            print(f"✅ Agrégation RSS OK: {len(rss_news)} articles")
            
            # Analyser les sources
            rss_count = len([a for a in rss_news if a.get('provider') == 'rss'])
            
            print(f"   📡 RSS: {rss_count} articles")
            
            # Exemples
            for i, article in enumerate(rss_news[:3], 1):
                provider = "RSS" if article.get('provider') == 'rss' else "API"
                print(f"   {i}. [{provider}] {article.get('title', 'N/A')[:45]}...")
        else:
            print("⚠️ Aucun article agrégé")
        
        return len(rss_news) > 0
        
    except Exception as e:
        print(f"❌ Erreur News Aggregator: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rss_connectivity():
    """Test de connectivité des sources RSS crypto"""
    print("\n" + "="*60)
    print("🧪 TEST Connectivité Sources RSS")
    print("="*60)
    
    try:
        from dash_modules.data_providers.rss_news_manager import rss_news_manager
        
        print("🌐 Test connectivité sources crypto...")
        
        # Test spécifique crypto (plus fiable)
        test_results = rss_news_manager.test_sources(['crypto'])
        
        total = test_results.get('total_sources', 0)
        successful = test_results.get('successful', 0)
        failed = test_results.get('failed', 0)
        
        print(f"   Total: {total}, Succès: {successful}, Échecs: {failed}")
        
        if test_results.get('details'):
            for detail in test_results['details'][:5]:  # Limiter l'affichage
                status_icon = "✅" if detail['status'] == 'OK' else "❌"
                response_time = detail.get('response_time', 0)
                print(f"   {status_icon} {detail['name']}: {detail['status']} ({response_time}s)")
        
        return successful > 0
        
    except Exception as e:
        print(f"❌ Erreur test connectivité: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale de test"""
    setup_logging()
    
    print("🚀 THEBOT - Test Infrastructure RSS Simple (Phase 1)")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("RSS Parser", test_rss_parser),
        ("RSS Sources Config", test_rss_sources_config),
        ("RSS News Manager", test_rss_news_manager),
        ("News Aggregator", test_news_aggregator),
        ("RSS Connectivité", test_rss_connectivity)
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
    print("📋 RÉSUMÉ DES TESTS RSS")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Résultat RSS: {passed}/{total} tests réussis ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 INFRASTRUCTURE RSS: SUCCÈS COMPLET!")
        print("✅ RSS opérationnel - Prêt pour intégration")
    elif passed >= total * 0.6:
        print("⚠️ INFRASTRUCTURE RSS: Partiellement fonctionnelle")
        print("🔧 Quelques ajustements nécessaires")
    else:
        print("❌ INFRASTRUCTURE RSS: Problèmes majeurs")
        print("🛠️ Révision nécessaire")
    
    print(f"\n💰 APIs payantes supprimées:")
    print("   ❌ CryptoPanic (-7€/mois)")
    print("   ❌ FMP (-14€/mois)")  
    print("   ❌ Alpha Vantage (-200€/mois)")
    print("   ✅ RSS Infrastructure (0€/mois)")
    print(f"   💵 Économies: ~221€/mois")
    
    return passed >= total * 0.6

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)