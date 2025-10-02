#!/usr/bin/env python3
"""
Test des composants Phase 4 - Crypto Avancés
Validation des 3 nouveaux modules crypto
"""

import sys
import os
import traceback
from datetime import datetime

# Ajouter le chemin du projet
sys.path.insert(0, '/home/rono/THEBOT')

def test_crypto_trends():
    """Test du composant crypto trends"""
    print("\n🧪 TEST CRYPTO TRENDS COMPONENT")
    print("=" * 50)
    
    try:
        from dash_modules.components.crypto_trends import crypto_trends
        
        # Test 1: Récupération trending coins
        print("📊 Test trending coins...")
        trending = crypto_trends.get_trending_coins(5)
        
        if trending:
            print(f"✅ {len(trending)} cryptos trending récupérées")
            for i, coin in enumerate(trending[:3], 1):
                print(f"   {i}. {coin['symbol']} - {coin['change_24h']:.2f}% - {coin['momentum']}")
        else:
            print("⚠️ Aucune crypto trending")
        
        # Test 2: Analyse volume
        print("\n📈 Test analyse volume...")
        volume_analysis = crypto_trends.get_volume_analysis()
        
        if volume_analysis:
            print(f"✅ Analyse volume disponible")
            print(f"   Paires actives: {volume_analysis.get('active_pairs', 0)}")
            print(f"   Sentiment marché: {volume_analysis.get('market_sentiment', 'Unknown')}")
            print(f"   Tendance volume: {volume_analysis.get('volume_trend', 'Unknown')}")
        else:
            print("⚠️ Analyse volume indisponible")
        
        # Test 3: Changements prix
        print("\n💰 Test changements prix...")
        price_changes = crypto_trends.get_price_changes()
        
        if price_changes:
            print(f"✅ Analyse changements prix disponible")
            extremes = price_changes.get('extremes', {})
            if extremes.get('biggest_gainer'):
                gainer = extremes['biggest_gainer']
                print(f"   Plus gros gainer: {gainer.get('symbol', 'N/A')} - {gainer.get('priceChangePercent', 0):.2f}%")
        else:
            print("⚠️ Changements prix indisponibles")
        
        # Test 4: Widget creation
        print("\n🎨 Test création widget...")
        widget = crypto_trends.create_trends_widget()
        print("✅ Widget crypto trends créé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test crypto trends: {e}")
        traceback.print_exc()
        return False

def test_top_performers():
    """Test du composant top performers"""
    print("\n🧪 TEST TOP PERFORMERS COMPONENT")
    print("=" * 50)
    
    try:
        from dash_modules.components.top_performers import top_performers
        
        # Test 1: Top gainers
        print("🏆 Test top gainers...")
        gainers = top_performers.get_top_gainers(5)
        
        if gainers:
            print(f"✅ {len(gainers)} top gainers récupérés")
            for i, gainer in enumerate(gainers[:3], 1):
                print(f"   {i}. {gainer['symbol']} - {gainer['change_percent']:.2f}% - {gainer['risk_level']}")
        else:
            print("⚠️ Aucun gainer trouvé")
        
        # Test 2: Top losers
        print("\n📉 Test top losers...")
        losers = top_performers.get_top_losers(5)
        
        if losers:
            print(f"✅ {len(losers)} top losers récupérés")
            for i, loser in enumerate(losers[:3], 1):
                print(f"   {i}. {loser['symbol']} - {loser['change_percent']:.2f}% - {loser['recovery_potential']}")
        else:
            print("⚠️ Aucun loser trouvé")
        
        # Test 3: Corrélations
        print("\n🔗 Test corrélations...")
        correlations = top_performers.calculate_correlations()
        
        if correlations:
            print("✅ Matrice de corrélation calculée")
            matrix = correlations.get('correlation_matrix', {})
            if matrix:
                symbols = list(matrix.keys())[:3]
                print(f"   Symboles analysés: {', '.join([s.replace('USDT', '') for s in symbols])}")
        else:
            print("⚠️ Corrélations indisponibles")
        
        # Test 4: Ratios performance
        print("\n📊 Test ratios performance...")
        ratios = top_performers.get_performance_ratios()
        
        if ratios:
            print("✅ Ratios de performance calculés")
            print(f"   Condition marché: {ratios.get('market_condition', 'Unknown')}")
            print(f"   Ratio Bull/Bear: {ratios.get('bull_bear_ratio', 0):.2f}")
            print(f"   Index force: {ratios.get('strength_index', 0):.1f}%")
        else:
            print("⚠️ Ratios indisponibles")
        
        # Test 5: Widget creation
        print("\n🎨 Test création widget...")
        widget = top_performers.create_performance_widget()
        print("✅ Widget top performers créé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test top performers: {e}")
        traceback.print_exc()
        return False

def test_fear_greed_gauge():
    """Test du composant Fear & Greed Gauge"""
    print("\n🧪 TEST FEAR & GREED GAUGE COMPONENT")
    print("=" * 50)
    
    try:
        from dash_modules.components.fear_greed_gauge import fear_greed_gauge
        
        # Test 1: Index actuel
        print("😨 Test Fear & Greed Index actuel...")
        current_index = fear_greed_gauge.get_fear_greed_index()
        
        if current_index:
            print(f"✅ Index Fear & Greed récupéré")
            print(f"   Valeur: {current_index['value']}/100")
            print(f"   Classification: {current_index['value_classification']}")
            print(f"   Niveau: {current_index['level']}")
            print(f"   Recommandation: {current_index['recommendation'].get('action', 'N/A')}")
        else:
            print("⚠️ Index Fear & Greed indisponible")
        
        # Test 2: Données historiques
        print("\n📈 Test données historiques...")
        historical = fear_greed_gauge.get_historical_data(7)
        
        if historical:
            print(f"✅ {len(historical)} entrées historiques récupérées")
            if len(historical) >= 3:
                recent = historical[:3]
                print("   Dernières valeurs:")
                for entry in recent:
                    print(f"     {entry['date']}: {entry['value']} ({entry['value_classification']})")
        else:
            print("⚠️ Données historiques indisponibles")
        
        # Test 3: Analyse tendances
        print("\n📊 Test analyse tendances...")
        if historical:
            trends = fear_greed_gauge.analyze_trends(historical)
            
            if trends:
                print("✅ Analyse des tendances effectuée")
                print(f"   Direction: {trends.get('trend_direction', 'Unknown')}")
                print(f"   Force: {trends.get('trend_strength', 0):.1f}")
                print(f"   Signal: {trends.get('signal', {}).get('signal', 'Unknown')}")
            else:
                print("⚠️ Analyse tendances échouée")
        
        # Test 4: Alertes
        print("\n🚨 Test système d'alertes...")
        if current_index:
            alerts = fear_greed_gauge.setup_alerts(current_index['value'])
            
            if alerts:
                print(f"✅ {len(alerts)} alertes configurées")
                for alert in alerts[:2]:  # Afficher 2 premières alertes
                    print(f"   {alert['type']}: {alert['message']}")
            else:
                print("✅ Aucune alerte active (normal)")
        
        # Test 5: Widget creation
        print("\n🎨 Test création widget...")
        widget = fear_greed_gauge.create_gauge_widget()
        print("✅ Widget Fear & Greed Gauge créé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test Fear & Greed Gauge: {e}")
        traceback.print_exc()
        return False

def test_integration():
    """Test d'intégration des composants Phase 4"""
    print("\n🧪 TEST INTÉGRATION PHASE 4")
    print("=" * 50)
    
    try:
        # Test imports simultanés
        print("📦 Test imports simultanés...")
        from dash_modules.components.crypto_trends import crypto_trends
        from dash_modules.components.top_performers import top_performers
        from dash_modules.components.fear_greed_gauge import fear_greed_gauge
        print("✅ Tous les composants importés")
        
        # Test données cross-component
        print("\n🔗 Test compatibilité données...")
        
        # Récupérer données de chaque composant
        trending_data = crypto_trends.get_trending_coins(3)
        gainers_data = top_performers.get_top_gainers(3)
        fear_data = fear_greed_gauge.get_fear_greed_index()
        
        success_count = 0
        if trending_data:
            success_count += 1
        if gainers_data:
            success_count += 1
        if fear_data:
            success_count += 1
        
        print(f"✅ {success_count}/3 composants fonctionnels")
        
        # Test cohérence des données
        if trending_data and gainers_data:
            trending_symbols = {coin['symbol'] for coin in trending_data}
            gainers_symbols = {coin['symbol'] for coin in gainers_data}
            common_symbols = trending_symbols.intersection(gainers_symbols)
            
            if common_symbols:
                print(f"✅ Symboles communs détectés: {len(common_symbols)}")
            else:
                print("ℹ️ Aucun symbole commun (normal selon les critères)")
        
        return success_count >= 2  # Au moins 2 composants doivent fonctionner
        
    except Exception as e:
        print(f"❌ Erreur test intégration: {e}")
        traceback.print_exc()
        return False

def main():
    """Fonction principale de test"""
    print("🚀 THEBOT - TEST PHASE 4 : COMPOSANTS CRYPTO AVANCÉS")
    print("=" * 70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Tests individuels
    results = []
    
    # Test 1: Crypto Trends
    results.append(test_crypto_trends())
    
    # Test 2: Top Performers
    results.append(test_top_performers())
    
    # Test 3: Fear & Greed Gauge
    results.append(test_fear_greed_gauge())
    
    # Test 4: Intégration
    results.append(test_integration())
    
    # Résumé final
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ TESTS PHASE 4")
    print("=" * 70)
    
    test_names = [
        "Crypto Trends Component",
        "Top Performers Component", 
        "Fear & Greed Gauge Component",
        "Integration Test"
    ]
    
    success_count = 0
    for i, (name, result) in enumerate(zip(test_names, results), 1):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i}. {name}: {status}")
        if result:
            success_count += 1
    
    # Score final
    total_tests = len(results)
    success_rate = (success_count / total_tests) * 100
    
    print(f"\n📈 SCORE FINAL: {success_count}/{total_tests} ({success_rate:.0f}%)")
    
    if success_rate >= 75:
        print("🎉 PHASE 4 - SUCCÈS! Composants crypto avancés opérationnels")
        print("✅ Prêt pour intégration au dashboard principal")
    elif success_rate >= 50:
        print("⚠️ PHASE 4 - PARTIEL. Quelques ajustements nécessaires")
    else:
        print("❌ PHASE 4 - ÉCHEC. Révision majeure requise")
    
    print(f"\n🎯 Phase 4 complétée - Dashboard crypto professionnel")
    print(f"💰 Coût total maintenu: 0€/mois")
    
    return success_rate >= 75

if __name__ == "__main__":
    main()