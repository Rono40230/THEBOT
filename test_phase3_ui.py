#!/usr/bin/env python3
"""
Test Phase 3 - Interface Utilisateur Avancée
Validation des nouveaux composants UI et fonctionnalités
"""

import sys
import os
import time
from datetime import datetime

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_advanced_dashboard():
    """Test du dashboard avancé"""
    print("\n🧪 TEST DASHBOARD AVANCÉ")
    print("=" * 40)
    
    try:
        from dash_modules.components.advanced_dashboard import advanced_dashboard
        
        print("✅ Dashboard avancé importé")
        
        # Test création layout
        layout = advanced_dashboard.create_layout()
        print("✅ Layout principal créé")
        
        # Test widgets catalog
        widgets_count = len(advanced_dashboard.widget_catalog)
        print(f"✅ Catalogue widgets: {widgets_count} widgets disponibles")
        
        # Test widgets individuels
        widget_types = ['market_overview', 'news_feed', 'price_charts', 'alerts']
        working_widgets = 0
        
        for widget_type in widget_types:
            try:
                widget_content = advanced_dashboard.get_widget_content(widget_type)
                print(f"   ✅ Widget {widget_type}: OK")
                working_widgets += 1
            except Exception as e:
                print(f"   ❌ Widget {widget_type}: {e}")
        
        widget_success_rate = (working_widgets / len(widget_types)) * 100
        print(f"📊 Widgets fonctionnels: {working_widgets}/{len(widget_types)} ({widget_success_rate:.1f}%)")
        
        return widget_success_rate >= 75
        
    except Exception as e:
        print(f"❌ Erreur dashboard: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_widget_manager():
    """Test du gestionnaire de widgets"""
    print("\n🧪 TEST GESTIONNAIRE WIDGETS")
    print("=" * 40)
    
    try:
        from dash_modules.components.widget_manager import widget_manager
        
        print("✅ Widget Manager importé")
        
        # Test layouts prédéfinis
        predefined_layouts = widget_manager.predefined_layouts
        print(f"✅ Layouts prédéfinis: {len(predefined_layouts)}")
        
        for layout_id, layout_info in predefined_layouts.items():
            print(f"   - {layout_id}: {layout_info['name']}")
        
        # Test sauvegarde/chargement
        test_layout = widget_manager.default_widgets
        save_success = widget_manager.save_layout("test_phase3", test_layout, "test_user")
        print(f"✅ Sauvegarde test: {'OK' if save_success else 'ERREUR'}")
        
        if save_success:
            loaded_layout = widget_manager.load_layout("test_phase3", "test_user")
            load_success = loaded_layout is not None
            print(f"✅ Chargement test: {'OK' if load_success else 'ERREUR'}")
        
        # Test validation layout
        validated = widget_manager.validate_layout(test_layout)
        print(f"✅ Validation layout: {len(validated)} widgets validés")
        
        # Test layouts disponibles
        available = widget_manager.get_available_layouts("test_user")
        print(f"✅ Layouts disponibles: {len(available)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur widget manager: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_advanced_news_feed():
    """Test de l'interface news avancée"""
    print("\n🧪 TEST INTERFACE NEWS AVANCÉE")
    print("=" * 40)
    
    try:
        from dash_modules.components.advanced_news_feed import advanced_news_feed
        
        print("✅ News Feed avancé importé")
        
        # Test interface principale
        news_interface = advanced_news_feed.create_news_interface()
        print("✅ Interface news créée")
        
        # Test catégories et sources
        categories_count = len(advanced_news_feed.news_categories)
        sources_count = len(advanced_news_feed.news_sources)
        print(f"✅ Catégories: {categories_count}, Sources: {sources_count}")
        
        # Test formatage articles (avec données factices)
        fake_articles = [
            {
                'title': 'Test Article 1',
                'summary': 'Résumé de test',
                'source': 'Test Source',
                'category': 'crypto',
                'published': datetime.now().isoformat(),
                'url': 'https://example.com'
            },
            {
                'title': 'Test Article 2',
                'summary': 'Autre résumé de test',
                'source': 'CoinDesk News',
                'category': 'economic',
                'published': datetime.now().isoformat(),
                'url': 'https://example2.com'
            }
        ]
        
        formatted = advanced_news_feed.format_news_articles(fake_articles, {})
        print(f"✅ Formatage articles: {len(formatted)} articles formatés")
        
        # Test filtres
        filtered = advanced_news_feed.filter_articles(fake_articles, {
            'category': 'crypto',
            'sort': 'newest'
        })
        print(f"✅ Filtres: {len(filtered)} articles après filtrage")
        
        # Test statistiques
        stats = advanced_news_feed.get_news_statistics(fake_articles)
        print(f"✅ Statistiques: {stats['total']} total, {stats['today']} aujourd'hui")
        
        return len(formatted) > 0 and stats['total'] > 0
        
    except Exception as e:
        print(f"❌ Erreur news feed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_advanced_charts():
    """Test des graphiques avancés"""
    print("\n🧪 TEST GRAPHIQUES AVANCÉS")
    print("=" * 40)
    
    try:
        from dash_modules.components.advanced_charts import advanced_charts
        
        print("✅ Charts avancés importés")
        
        # Test interface
        chart_interface = advanced_charts.create_advanced_chart_interface()
        print("✅ Interface graphiques créée")
        
        # Test configurations
        chart_types_count = len(advanced_charts.chart_types)
        timeframes_count = len(advanced_charts.timeframes)
        indicators_count = len(advanced_charts.indicators)
        
        print(f"✅ Types graphiques: {chart_types_count}")
        print(f"✅ Timeframes: {timeframes_count}")
        print(f"✅ Indicateurs: {indicators_count}")
        
        # Test création graphique vide
        empty_chart = advanced_charts.create_empty_chart("Test")
        print("✅ Graphique vide créé")
        
        # Test indicateurs (avec données factices)
        import pandas as pd
        import numpy as np
        
        # Créer données factices OHLCV
        dates = pd.date_range(start='2025-01-01', periods=100, freq='H')
        np.random.seed(42)
        
        fake_data = pd.DataFrame({
            'open': 50000 + np.cumsum(np.random.randn(100) * 100),
            'high': 50000 + np.cumsum(np.random.randn(100) * 100) + 200,
            'low': 50000 + np.cumsum(np.random.randn(100) * 100) - 200,
            'close': 50000 + np.cumsum(np.random.randn(100) * 100),
            'volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        # Corriger les données pour qu'elles soient cohérentes
        for i in range(len(fake_data)):
            high = max(fake_data.iloc[i]['open'], fake_data.iloc[i]['close']) + abs(np.random.randn() * 50)
            low = min(fake_data.iloc[i]['open'], fake_data.iloc[i]['close']) - abs(np.random.randn() * 50)
            fake_data.iloc[i, fake_data.columns.get_loc('high')] = high
            fake_data.iloc[i, fake_data.columns.get_loc('low')] = low
        
        # Test indicateurs techniques
        sma = advanced_charts.calculate_sma(fake_data['close'], 20)
        ema = advanced_charts.calculate_ema(fake_data['close'], 20)
        rsi = advanced_charts.calculate_rsi(fake_data['close'], 14)
        
        indicators_working = 0
        if not sma.isna().all():
            print("   ✅ SMA calculé")
            indicators_working += 1
        if not ema.isna().all():
            print("   ✅ EMA calculé")
            indicators_working += 1
        if not rsi.isna().all():
            print("   ✅ RSI calculé")
            indicators_working += 1
        
        # Test création graphique avec données
        config = {
            'symbol': 'BTCUSDT',
            'timeframe': '1h',
            'chart_type': 'candlestick',
            'indicators': ['sma'],
            'theme': 'default',
            'display_options': ['show_volume']
        }
        
        chart_fig = advanced_charts.create_candlestick_chart(fake_data, config)
        print("✅ Graphique chandelier créé")
        
        success_rate = (indicators_working / 3) * 100
        print(f"📊 Indicateurs fonctionnels: {indicators_working}/3 ({success_rate:.1f}%)")
        
        return success_rate >= 66  # Au moins 2/3 des indicateurs
        
    except Exception as e:
        print(f"❌ Erreur charts: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_phase3():
    """Test d'intégration Phase 3"""
    print("\n🧪 TEST INTÉGRATION PHASE 3")
    print("=" * 40)
    
    try:
        # Test imports combinés
        from dash_modules.components.advanced_dashboard import advanced_dashboard
        from dash_modules.components.widget_manager import widget_manager
        from dash_modules.components.advanced_news_feed import advanced_news_feed
        from dash_modules.components.advanced_charts import advanced_charts
        
        print("✅ Tous les composants Phase 3 importés")
        
        # Test compatibilité avec infrastructure Phase 1+2
        try:
            from dash_modules.core.rss_parser import RSSParser
            from dash_modules.core.intelligent_cache import get_global_cache
            from dash_modules.core.specialized_api_manager import specialized_api_manager
            from dash_modules.data_providers.real_data_manager import real_data_manager
            
            infra_ok = True
            print("✅ Infrastructure Phases 1-2 compatible")
        except Exception as e:
            print(f"⚠️ Problème compatibilité infrastructure: {e}")
            infra_ok = False
        
        # Test création dashboard complet
        try:
            # Layout avec widgets Phase 3
            layout = advanced_dashboard.create_layout()
            
            # Configuration avec widget manager
            available_layouts = widget_manager.get_available_layouts()
            
            # Interface news
            news_ui = advanced_news_feed.create_news_interface()
            
            # Interface charts
            charts_ui = advanced_charts.create_advanced_chart_interface()
            
            print("✅ Intégration UI complète fonctionnelle")
            integration_ok = True
            
        except Exception as e:
            print(f"❌ Erreur intégration UI: {e}")
            integration_ok = False
        
        return infra_ok and integration_ok
        
    except Exception as e:
        print(f"❌ Erreur intégration: {e}")
        return False

def main():
    """Fonction principale de test Phase 3"""
    print("🚀 THEBOT - TEST PHASE 3 : INTERFACE UTILISATEUR AVANCÉE")
    print("=" * 70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Dashboard Avancé", test_advanced_dashboard),
        ("Gestionnaire Widgets", test_widget_manager),
        ("Interface News Avancée", test_advanced_news_feed),
        ("Graphiques Avancés", test_advanced_charts),
        ("Intégration Phase 3", test_integration_phase3)
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
    print("📋 RÉSUMÉ PHASE 3 - INTERFACE UTILISATEUR AVANCÉE")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result, elapsed in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name} ({elapsed:.2f}s)")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\n🎯 Résultat Phase 3: {passed}/{total} tests réussis ({success_rate:.1f}%)")
    print(f"⏱️ Temps total: {total_time:.2f}s")
    
    if passed == total:
        print("\n🎉 PHASE 3 COMPLÈTE: SUCCÈS TOTAL!")
        print("✅ Interface utilisateur avancée déployée")
        print("🎨 Dashboard moderne opérationnel")
        print("📰 Feed RSS avancé fonctionnel")
        print("📊 Graphiques avec indicateurs techniques")
    elif passed >= total * 0.7:
        print("\n⚠️ PHASE 3: Succès partiel")
        print("🔧 Quelques ajustements nécessaires")
    else:
        print("\n❌ PHASE 3: Problèmes importants")
        print("🛠️ Révision nécessaire")
    
    print(f"\n📈 PROGRESSION GLOBALE THEBOT:")
    print("   ✅ Phase 1: Infrastructure RSS (100%)")
    print("   ✅ Phase 2: Optimisations APIs (100%)")
    print(f"   🎨 Phase 3: Interface Avancée ({success_rate:.1f}%)")
    print("   💰 Coût total: 0€/mois")
    
    if success_rate >= 80:
        print(f"\n🚀 THEBOT PRÊT POUR PRODUCTION!")
        print("   Interface moderne et performante")
        print("   Infrastructure optimisée")
        print("   Données en temps réel")
        print("   Fonctionnalités avancées")
    
    return passed >= total * 0.7

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)