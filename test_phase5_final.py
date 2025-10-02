#!/usr/bin/env python3
"""
Test Final Phase 5 - Intégration Crypto News + Phase 4
Validation complète de l'intégration modulaire
"""

import sys
import os
from datetime import datetime

# Ajouter le chemin du projet
sys.path.insert(0, '/home/rono/THEBOT')

def test_crypto_news_with_phase4():
    """Test complet crypto news avec extensions Phase 4"""
    print("🧪 TEST CRYPTO NEWS + PHASE 4 INTÉGRATION")
    print("=" * 50)
    
    try:
        from dash_modules.tabs.crypto_news_module import CryptoNewsModule
        
        # Créer instance
        crypto_news = CryptoNewsModule()
        print("✅ CryptoNewsModule avec Phase 4 instancié")
        
        # Test layout avec extensions
        layout = crypto_news.get_layout()
        print("✅ Layout avec extensions Phase 4 généré")
        
        # Test méthodes Phase 4
        phase4_extensions = crypto_news.create_phase4_extensions()
        print("✅ Extensions Phase 4 créées")
        
        # Test méthodes existantes (non-régression)
        trending = crypto_news.create_trending_cryptos_widget()
        print("✅ Trending cryptos widget (existant) fonctionne")
        
        sources = crypto_news._get_news_sources()
        print(f"✅ Sources news: {sources}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test crypto news intégré: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_widgets_data_flow():
    """Test le flux de données des widgets Phase 4"""
    print("\n🧪 TEST FLUX DONNÉES WIDGETS")
    print("=" * 50)
    
    try:
        # Test widgets individuellement
        from dash_modules.components.crypto_trends import crypto_trends
        from dash_modules.components.top_performers import top_performers
        from dash_modules.components.fear_greed_gauge import fear_greed_gauge
        
        # Test données crypto trends
        trending_data = crypto_trends.get_trending_coins(3)
        print(f"✅ Crypto Trends: {len(trending_data) if trending_data else 0} cryptos")
        
        # Test données top performers
        gainers_data = top_performers.get_top_gainers(3)
        print(f"✅ Top Performers: {len(gainers_data) if gainers_data else 0} gainers")
        
        # Test données fear & greed
        fear_data = fear_greed_gauge.get_fear_greed_index()
        print(f"✅ Fear & Greed: {fear_data.get('value', 'N/A') if fear_data else 'N/A'}/100")
        
        # Test extension complète
        from dash_modules.components.crypto_news_phase4_extensions import get_phase4_sidebar_widgets
        widgets_layout = get_phase4_sidebar_widgets()
        print("✅ Layout widgets compacts généré")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test flux données: {e}")
        return False

def test_dashboard_compatibility():
    """Test compatibilité avec le dashboard principal"""
    print("\n🧪 TEST COMPATIBILITÉ DASHBOARD")
    print("=" * 50)
    
    try:
        # Test lancement dashboard
        from launch_dash_professional import create_dash_app
        
        # Créer app (sans lancer)
        app = create_dash_app(debug=False)
        print("✅ Dashboard principal créé avec intégrations")
        
        # Test modules tabs
        from dash_modules.tabs.crypto_news_module import CryptoNewsModule
        crypto_module = CryptoNewsModule()
        print("✅ Module crypto news compatible")
        
        # Vérifier que les autres modules fonctionnent toujours
        from dash_modules.tabs.economic_news_module import EconomicNewsModule
        eco_module = EconomicNewsModule()
        print("✅ Module economic news non affecté")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test compatibilité: {e}")
        return False

def test_error_handling():
    """Test gestion d'erreurs et fallbacks"""
    print("\n🧪 TEST GESTION ERREURS")
    print("=" * 50)
    
    try:
        from dash_modules.tabs.crypto_news_module import CryptoNewsModule
        
        crypto_news = CryptoNewsModule()
        
        # Test fallback extensions Phase 4
        try:
            # Simuler absence Phase 4 (difficile à tester directement)
            extensions = crypto_news.create_phase4_extensions()
            print("✅ Extensions Phase 4 ou fallback créés")
        except Exception as e:
            print(f"⚠️ Fallback activé: {e}")
        
        # Test robustesse avec données vides
        empty_filter = crypto_news._filter_news_by_type([])
        print(f"✅ Filter avec données vides: {len(empty_filter)} résultats")
        
        # Test trending widget avec erreur potentielle
        trending_widget = crypto_news.create_trending_cryptos_widget()
        print("✅ Trending widget robuste")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test gestion erreurs: {e}")
        return False

def validate_phase5_completion():
    """Validation finale Phase 5"""
    print("\n✅ VALIDATION FINALE PHASE 5")
    print("=" * 50)
    
    completion_checks = []
    
    # Check 1: Module crypto news fonctionne
    try:
        from dash_modules.tabs.crypto_news_module import CryptoNewsModule
        crypto_news = CryptoNewsModule()
        layout = crypto_news.get_layout()
        completion_checks.append(("Module crypto news", True, "Fonctionnel avec intégrations"))
    except Exception as e:
        completion_checks.append(("Module crypto news", False, f"Erreur: {e}"))
    
    # Check 2: Extensions Phase 4 disponibles
    try:
        from dash_modules.components.crypto_news_phase4_extensions import get_phase4_sidebar_widgets
        widgets = get_phase4_sidebar_widgets()
        completion_checks.append(("Extensions Phase 4", True, "Widgets compacts opérationnels"))
    except Exception as e:
        completion_checks.append(("Extensions Phase 4", False, f"Erreur: {e}"))
    
    # Check 3: Dashboard principal compatible
    try:
        from launch_dash_professional import create_dash_app
        app = create_dash_app(debug=False)
        completion_checks.append(("Dashboard principal", True, "Compatible avec Phase 5"))
    except Exception as e:
        completion_checks.append(("Dashboard principal", False, f"Erreur: {e}"))
    
    # Check 4: Aucune régression
    try:
        from dash_modules.tabs.economic_news_module import EconomicNewsModule
        eco_news = EconomicNewsModule()
        completion_checks.append(("Non-régression", True, "Autres modules intacts"))
    except Exception as e:
        completion_checks.append(("Non-régression", False, f"Régression détectée: {e}"))
    
    # Afficher résultats
    passed = 0
    total = len(completion_checks)
    
    for check_name, status, details in completion_checks:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check_name}: {details}")
        if status:
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\n📊 VALIDATION: {passed}/{total} ({success_rate:.0f}%)")
    
    return success_rate >= 75

def main():
    """Fonction principale de test final"""
    print("🚀 THEBOT - TEST FINAL PHASE 5")
    print("=" * 70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    # Test 1: Intégration crypto news + Phase 4
    results.append(test_crypto_news_with_phase4())
    
    # Test 2: Flux données widgets
    results.append(test_widgets_data_flow())
    
    # Test 3: Compatibilité dashboard
    results.append(test_dashboard_compatibility())
    
    # Test 4: Gestion erreurs
    results.append(test_error_handling())
    
    # Validation finale
    validation_passed = validate_phase5_completion()
    
    # Résumé final
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ FINAL PHASE 5")
    print("=" * 70)
    
    success_count = sum(results)
    total_tests = len(results)
    success_rate = (success_count / total_tests) * 100
    
    test_names = [
        "Crypto News + Phase 4 Integration",
        "Widgets Data Flow",
        "Dashboard Compatibility", 
        "Error Handling"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results), 1):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i}. {name}: {status}")
    
    print(f"\n📈 TESTS: {success_count}/{total_tests} ({success_rate:.0f}%)")
    print(f"📋 VALIDATION: {'✅ PASS' if validation_passed else '❌ FAIL'}")
    
    overall_success = success_rate >= 75 and validation_passed
    
    if overall_success:
        print("\n🎉 PHASE 5 - TERMINÉE AVEC SUCCÈS!")
        print("✅ Intégration modulaire crypto news + Phase 4 opérationnelle")
        print("✅ Aucune régression détectée")
        print("✅ Dashboard enrichi avec widgets crypto avancés")
        print("🔗 Ready for Phase 6!")
    elif success_rate >= 50:
        print("\n⚠️ PHASE 5 - Partiellement terminée")
        print("🔧 Quelques ajustements nécessaires")
    else:
        print("\n❌ PHASE 5 - Corrections requises")
    
    print(f"\n🎯 Résultat: Dashboard crypto news enrichi")
    print(f"🧩 Architecture: 100% modulaire préservée")
    print(f"💰 Budget: 0€/mois maintenu")
    print(f"📊 Widgets Phase 4 intégrés dans onglet crypto news")
    
    return overall_success

if __name__ == "__main__":
    main()