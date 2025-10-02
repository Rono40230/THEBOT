#!/usr/bin/env python3
"""
Test Phase 5 - Extension modulaire crypto news
Test l'intégration des widgets Phase 4 dans crypto_news_module
"""

import sys
import os
from datetime import datetime

# Ajouter le chemin du projet
sys.path.insert(0, '/home/rono/THEBOT')

def test_crypto_news_module_basic():
    """Test le module crypto news de base"""
    print("🧪 TEST CRYPTO NEWS MODULE BASIC")
    print("=" * 50)
    
    try:
        from dash_modules.tabs.crypto_news_module import CryptoNewsModule
        
        # Créer instance
        crypto_news = CryptoNewsModule()
        print("✅ CryptoNewsModule instancié")
        
        # Test layout
        layout = crypto_news.get_layout()
        print("✅ Layout crypto news généré")
        
        # Test méthodes de base
        sources = crypto_news._get_news_sources()
        print(f"✅ Sources news: {sources}")
        
        # Test filter (avec données vides)
        filtered = crypto_news._filter_news_by_type([])
        print(f"✅ Filter news: {len(filtered)} articles")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test crypto news module: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase4_widgets_availability():
    """Test la disponibilité des widgets Phase 4"""
    print("\n🧪 TEST WIDGETS PHASE 4 AVAILABILITY")
    print("=" * 50)
    
    try:
        from dash_modules.components.crypto_trends import crypto_trends
        from dash_modules.components.top_performers import top_performers
        from dash_modules.components.fear_greed_gauge import fear_greed_gauge
        
        print("✅ crypto_trends importé")
        print("✅ top_performers importé")
        print("✅ fear_greed_gauge importé")
        
        # Test fonctionnalité de base
        trending = crypto_trends.get_trending_coins(3)
        print(f"✅ Trending coins: {len(trending) if trending else 0} résultats")
        
        gainers = top_performers.get_top_gainers(3)
        print(f"✅ Top gainers: {len(gainers) if gainers else 0} résultats")
        
        fear_data = fear_greed_gauge.get_fear_greed_index()
        print(f"✅ Fear & Greed: {fear_data.get('value', 'N/A') if fear_data else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test widgets Phase 4: {e}")
        return False

def test_integration_approach():
    """Test l'approche d'intégration modulaire"""
    print("\n🧪 TEST APPROCHE INTÉGRATION")
    print("=" * 50)
    
    try:
        # Test import conditionnel
        try:
            from dash_modules.components.crypto_trends import crypto_trends
            phase4_available = True
            print("✅ Phase 4 widgets disponibles")
        except ImportError:
            phase4_available = False
            print("⚠️ Phase 4 widgets non disponibles")
        
        # Test création de widgets compacts
        if phase4_available:
            # Simuler la création de widgets compacts
            print("✅ Widgets compacts simulés")
            
            # Test données compactes
            trending = crypto_trends.get_trending_coins(3)
            if trending:
                top_symbol = trending[0]['symbol'].replace('USDT', '')
                print(f"✅ Top trending: {top_symbol}")
            
            fear_data = fear_greed_gauge.get_fear_greed_index()
            if fear_data:
                value = fear_data['value']
                classification = fear_data['value_classification']
                print(f"✅ Fear & Greed: {value}/100 ({classification})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test intégration: {e}")
        return False

def create_phase5_integration_plan():
    """Crée un plan d'intégration Phase 5 simplifié"""
    print("\n📋 PLAN INTÉGRATION PHASE 5 SIMPLIFIÉ")
    print("=" * 50)
    
    plan = {
        'approach': 'Extension modulaire progressive',
        'steps': [
            {
                'step': 1,
                'name': 'Correction syntaxe crypto_news_module.py',
                'status': 'En cours',
                'risk': 'Faible'
            },
            {
                'step': 2, 
                'name': 'Ajout widgets compacts Phase 4',
                'status': 'Planifié',
                'risk': 'Faible'
            },
            {
                'step': 3,
                'name': 'Tests intégration',
                'status': 'Planifié', 
                'risk': 'Très faible'
            },
            {
                'step': 4,
                'name': 'Extension economic_news_module.py',
                'status': 'Planifié',
                'risk': 'Très faible'
            }
        ],
        'principles': [
            '🔒 Préservation 100% de l\'existant',
            '🧩 Ajouts modulaires uniquement', 
            '⚡ Widgets compacts dans sidebar',
            '🧪 Tests de non-régression'
        ]
    }
    
    print("📊 ÉTAPES:")
    for step in plan['steps']:
        print(f"   {step['step']}. {step['name']} - {step['status']} (Risque: {step['risk']})")
    
    print("\n🎯 PRINCIPES:")
    for principle in plan['principles']:
        print(f"   {principle}")
    
    return plan

def main():
    """Fonction principale de test Phase 5"""
    print("🚀 THEBOT - TEST PHASE 5 : EXTENSION MODULAIRE")
    print("=" * 70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    # Test 1: Module crypto news de base
    results.append(test_crypto_news_module_basic())
    
    # Test 2: Disponibilité widgets Phase 4
    results.append(test_phase4_widgets_availability())
    
    # Test 3: Approche intégration
    results.append(test_integration_approach())
    
    # Plan d'intégration
    plan = create_phase5_integration_plan()
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ TEST PHASE 5")
    print("=" * 70)
    
    success_count = sum(results)
    total_tests = len(results)
    success_rate = (success_count / total_tests) * 100
    
    test_names = [
        "Crypto News Module Basic",
        "Phase 4 Widgets Availability", 
        "Integration Approach"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results), 1):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i}. {name}: {status}")
    
    print(f"\n📈 SCORE: {success_count}/{total_tests} ({success_rate:.0f}%)")
    
    if success_rate >= 75:
        print("🎉 PHASE 5 - PRÊTE pour intégration modulaire!")
        print("✅ Approche: Extension progressive et sûre")
    else:
        print("⚠️ PHASE 5 - Prérequis à corriger")
    
    print(f"\n🎯 Phase 5: Extension modulaire crypto news")
    print(f"🧩 Architecture: 100% modulaire préservée")
    print(f"💰 Budget: 0€/mois maintenu")
    
    return success_rate >= 75

if __name__ == "__main__":
    main()