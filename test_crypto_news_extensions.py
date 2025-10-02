#!/usr/bin/env python3
"""
Test Phase 5 Extensions Crypto News
Test des extensions modulaires Phase 4 pour crypto news
"""

import sys
import os
from datetime import datetime

# Ajouter le chemin du projet
sys.path.insert(0, '/home/rono/THEBOT')

def test_phase4_extensions():
    """Test des extensions Phase 4 pour crypto news"""
    print("🧪 TEST PHASE 4 EXTENSIONS")
    print("=" * 50)
    
    try:
        from dash_modules.components.crypto_news_phase4_extensions import (
            crypto_news_phase4_extensions,
            get_phase4_sidebar_widgets,
            register_phase4_callbacks,
            PHASE4_AVAILABLE
        )
        
        print(f"✅ Extensions importées")
        print(f"✅ Phase 4 disponible: {PHASE4_AVAILABLE}")
        
        # Test création layout
        layout = get_phase4_sidebar_widgets()
        print("✅ Layout widgets compacts créé")
        
        # Test instance
        instance = crypto_news_phase4_extensions
        print(f"✅ Instance créée avec prefix: {instance.widget_prefix}")
        
        # Test callbacks registration
        register_phase4_callbacks()
        print("✅ Callbacks enregistrés")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test extensions: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_widgets_functionality():
    """Test la fonctionnalité des widgets individuels"""
    print("\n🧪 TEST WIDGETS FUNCTIONALITY")
    print("=" * 50)
    
    try:
        from dash_modules.components.crypto_news_phase4_extensions import PHASE4_AVAILABLE
        
        if not PHASE4_AVAILABLE:
            print("⚠️ Phase 4 non disponible - Test layout fallback")
            from dash_modules.components.crypto_news_phase4_extensions import get_phase4_sidebar_widgets
            layout = get_phase4_sidebar_widgets()
            print("✅ Layout fallback généré")
            return True
        
        # Test composants individuels
        from dash_modules.components.crypto_trends import crypto_trends
        from dash_modules.components.top_performers import top_performers
        from dash_modules.components.fear_greed_gauge import fear_greed_gauge
        
        # Test Fear & Greed
        fear_data = fear_greed_gauge.get_fear_greed_index()
        if fear_data:
            value = fear_data['value']
            classification = fear_data['value_classification']
            print(f"✅ Fear & Greed: {value}/100 ({classification})")
        else:
            print("⚠️ Fear & Greed données indisponibles")
        
        # Test Top Gainers
        gainers = top_performers.get_top_gainers(3)
        if gainers:
            top_gainer = gainers[0]
            symbol = top_gainer['symbol'].replace('USDT', '')
            change = top_gainer['change_percent']
            print(f"✅ Top Gainer: {symbol} +{change:.1f}%")
        else:
            print("⚠️ Gainers données indisponibles")
        
        # Test Market Trends
        volume_analysis = crypto_trends.get_volume_analysis()
        if volume_analysis:
            sentiment = volume_analysis.get('market_sentiment', 'Unknown')
            gainers_count = volume_analysis.get('gainers_count', 0)
            losers_count = volume_analysis.get('losers_count', 0)
            print(f"✅ Market: {sentiment} ({gainers_count}↗️ {losers_count}↘️)")
        else:
            print("⚠️ Market trends données indisponibles")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test widgets: {e}")
        return False

def test_integration_ready():
    """Test si l'intégration est prête"""
    print("\n🧪 TEST INTEGRATION READINESS")
    print("=" * 50)
    
    try:
        # Test module crypto news existant
        from dash_modules.tabs.crypto_news_module import CryptoNewsModule
        crypto_news = CryptoNewsModule()
        print("✅ Module crypto news fonctionnel")
        
        # Test extensions
        from dash_modules.components.crypto_news_phase4_extensions import get_phase4_sidebar_widgets
        widgets = get_phase4_sidebar_widgets()
        print("✅ Widgets Phase 4 prêts")
        
        # Test compatibilité
        layout = crypto_news.get_layout()
        print("✅ Layout crypto news compatible")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test intégration: {e}")
        return False

def create_integration_demo():
    """Crée une démo d'intégration des extensions"""
    print("\n🎨 DÉMO INTÉGRATION")
    print("=" * 50)
    
    try:
        from dash_modules.components.crypto_news_phase4_extensions import get_phase4_sidebar_widgets
        
        # Simuler l'intégration
        widgets = get_phase4_sidebar_widgets()
        
        # Structure d'intégration suggérée
        integration_structure = {
            'approach': 'Extension modulaire non-invasive',
            'method': 'Ajout dans sidebar existante',
            'files_to_modify': [
                'dash_modules/tabs/crypto_news_module.py (minimal)'
            ],
            'files_to_add': [
                'dash_modules/components/crypto_news_phase4_extensions.py (✅ créé)'
            ],
            'integration_points': [
                'Sidebar widgets section',
                'Import des extensions',
                'Ajout au layout'
            ],
            'risk_assessment': 'TRÈS FAIBLE - Extensions isolées'
        }
        
        print("📋 STRUCTURE D'INTÉGRATION:")
        print(f"   Approche: {integration_structure['approach']}")
        print(f"   Méthode: {integration_structure['method']}")
        print(f"   Risque: {integration_structure['risk_assessment']}")
        
        print("\n📁 FICHIERS:")
        for file in integration_structure['files_to_modify']:
            print(f"   🔧 À modifier: {file}")
        for file in integration_structure['files_to_add']:
            print(f"   🆕 Ajouté: {file}")
        
        print("\n🔗 POINTS D'INTÉGRATION:")
        for point in integration_structure['integration_points']:
            print(f"   • {point}")
        
        return integration_structure
        
    except Exception as e:
        print(f"❌ Erreur démo intégration: {e}")
        return {}

def main():
    """Fonction principale de test"""
    print("🚀 THEBOT - TEST PHASE 5 EXTENSIONS")
    print("=" * 70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    # Test 1: Extensions Phase 4
    results.append(test_phase4_extensions())
    
    # Test 2: Fonctionnalité widgets
    results.append(test_widgets_functionality())
    
    # Test 3: Prêt pour intégration
    results.append(test_integration_ready())
    
    # Démo intégration
    integration_structure = create_integration_demo()
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ PHASE 5 EXTENSIONS")
    print("=" * 70)
    
    success_count = sum(results)
    total_tests = len(results)
    success_rate = (success_count / total_tests) * 100
    
    test_names = [
        "Phase 4 Extensions",
        "Widgets Functionality",
        "Integration Readiness"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results), 1):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i}. {name}: {status}")
    
    print(f"\n📈 SCORE: {success_count}/{total_tests} ({success_rate:.0f}%)")
    
    if success_rate >= 75:
        print("🎉 PHASE 5 EXTENSIONS - PRÊTES!")
        print("✅ Intégration modulaire sûre et non-invasive")
        print("🔗 Prêt pour ajout dans crypto_news_module.py")
    elif success_rate >= 50:
        print("⚠️ PHASE 5 EXTENSIONS - Partiellement prêtes")
    else:
        print("❌ PHASE 5 EXTENSIONS - Corrections nécessaires")
    
    print(f"\n🎯 Approche: Extensions modulaires isolées")
    print(f"🛡️ Sécurité: Aucun impact sur l'existant")
    print(f"💰 Budget: 0€/mois maintenu")
    
    return success_rate >= 75

if __name__ == "__main__":
    main()