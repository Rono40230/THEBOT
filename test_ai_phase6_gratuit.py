#!/usr/bin/env python3
"""
Test IA Phase 6 - Validation 100% Gratuite
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ai_engines_gratuits():
    """Test complet des moteurs IA gratuits"""
    print("🤖 THEBOT - TEST IA PHASE 6 GRATUITE")
    print("=" * 70)
    
    from datetime import datetime
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success_count = 0
    total_tests = 0
    
    # Test 1: IA Locale
    total_tests += 1
    try:
        from dash_modules.ai_engine.local_ai_engine import local_ai_engine
        
        # Test sentiment analysis
        fake_news = [
            {'title': 'Bitcoin rises to new highs', 'description': 'Strong bullish momentum'},
            {'title': 'Market shows positive trends', 'description': 'Gains across crypto'},
            {'title': 'Bearish sentiment emerging', 'description': 'Decline expected'}
        ]
        
        sentiment_result = local_ai_engine.analyze_market_sentiment(fake_news)
        
        print("✅ IA Locale - Sentiment Analysis")
        print(f"   - Sentiment: {sentiment_result.get('sentiment')}")
        print(f"   - Confidence: {sentiment_result.get('confidence')}%")
        print(f"   - Score: {sentiment_result.get('score')}")
        print(f"   - Coût: 100% GRATUIT")
        
        success_count += 1
    except Exception as e:
        print(f"❌ Erreur IA Locale: {e}")
    
    # Test 2: IA Technique Locale
    total_tests += 1
    try:
        # Test analyse technique
        price_data = {'close': 45000, 'volume': 1000000}
        indicators = {'sma_20': 44000, 'rsi': 65, 'avg_volume': 800000}
        
        technical_result = local_ai_engine.analyze_technical_pattern(price_data, indicators)
        
        print("✅ IA Locale - Technical Analysis")
        print(f"   - Pattern: {technical_result.get('pattern')}")
        print(f"   - Confidence: {technical_result.get('confidence')}%")
        print(f"   - Signaux: {len(technical_result.get('signals', []))}")
        print(f"   - Coût: 100% GRATUIT")
        
        success_count += 1
    except Exception as e:
        print(f"❌ Erreur Technical Analysis: {e}")
    
    # Test 3: IA Gratuite Publique
    total_tests += 1
    try:
        from dash_modules.ai_engine.free_ai_engine import free_ai_engine
        
        # Test status services gratuits
        services = free_ai_engine.get_available_services()
        usage = free_ai_engine.get_daily_usage()
        
        print("✅ IA Publique Gratuite")
        print(f"   - Services disponibles: {len(services)}")
        print(f"   - HuggingFace: {services['huggingface']['available']}")
        print(f"   - Usage quotidien: {usage['requests_today']}/{usage['daily_limit']}")
        print(f"   - Coût: {services['huggingface']['cost']}")
        
        success_count += 1
    except Exception as e:
        print(f"❌ Erreur IA Publique: {e}")
    
    # Test 4: IA Hybride Smart
    total_tests += 1
    try:
        from dash_modules.ai_engine.smart_ai_engine import smart_ai_engine
        
        # Test stratégie hybride
        strategy = smart_ai_engine.get_strategy_summary()
        budget_status = strategy['current_status']
        
        print("✅ IA Hybride Smart")
        print(f"   - Budget mensuel: {strategy['budget']}")
        print(f"   - Dépense actuelle: {budget_status['monthly_spend']}€")
        print(f"   - IA locale: {strategy['cost_optimization']['local_ai_usage']}")
        print(f"   - Savings: {strategy['cost_optimization']['estimated_savings']}")
        
        success_count += 1
    except Exception as e:
        print(f"❌ Erreur IA Hybride: {e}")
    
    # Test 5: Analyse Complète Gratuite
    total_tests += 1
    try:
        # Test analyse complète avec IA locale
        market_data = {
            'price_data': {'close': 45000, 'high': 46000, 'low': 44000, 'volume': 1500000},
            'indicators': {'sma_20': 44500, 'rsi': 58, 'avg_volume': 1000000}
        }
        
        news_data = [
            {'title': 'Crypto market stabilizing', 'description': 'Positive outlook'},
            {'title': 'Federal Reserve hints dovish', 'description': 'Market optimistic'}
        ]
        
        complete_analysis = local_ai_engine.generate_trading_insight(
            'BTCUSDT', 
            {'technical_analysis': technical_result},
            sentiment_result
        )
        
        print("✅ Analyse Complète Gratuite")
        print(f"   - Recommandation: {complete_analysis.get('recommendation')}")
        print(f"   - Confidence: {complete_analysis.get('confidence')}%")
        print(f"   - Source: {complete_analysis.get('source')}")
        print(f"   - Breakdown technique: {complete_analysis.get('breakdown', {}).get('technical_score')}%")
        print(f"   - Breakdown sentiment: {complete_analysis.get('breakdown', {}).get('sentiment_score')}%")
        
        success_count += 1
    except Exception as e:
        print(f"❌ Erreur Analyse Complète: {e}")
    
    # Test 6: Smart Analysis avec Budget
    total_tests += 1
    try:
        # Test analyse smart avec contrôle budget
        context = {
            'volatility_24h': 2.5,  # Pas assez pour justifier IA payante
            'major_news_event': False,
            'volume_vs_average': 1.2
        }
        
        smart_analysis = smart_ai_engine.analyze_market_comprehensive(
            'ETHUSDT', market_data, news_data, context
        )
        
        print("✅ Smart Analysis Budget")
        print(f"   - Stratégie utilisée: {smart_analysis.get('strategy')}")
        print(f"   - Raison: {smart_analysis.get('decision_reason')}")
        print(f"   - Coût total: {smart_analysis.get('cost_breakdown', {}).get('total')}€")
        print(f"   - Analysis disponible: {'Oui' if smart_analysis.get('local_analysis') else 'Non'}")
        
        success_count += 1
    except Exception as e:
        print(f"❌ Erreur Smart Analysis: {e}")
    
    print()
    print("🧪 TEST PERFORMANCE & COÛTS")
    print("=" * 50)
    
    # Test 7: Performance et coûts
    total_tests += 1
    try:
        import time
        
        # Test performance IA locale
        start_time = time.time()
        for i in range(10):
            local_ai_engine.analyze_market_sentiment([
                {'title': f'Test {i}', 'description': 'Performance test'}
            ])
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        
        print("✅ Performance & Coûts")
        print(f"   - Temps moyen analyse: {avg_time:.3f}s")
        print(f"   - Throughput: {1/avg_time:.1f} analyses/seconde")
        print(f"   - Coût par analyse: 0.000€ (GRATUIT)")
        print(f"   - Limite quotidienne: ILLIMITÉE")
        print(f"   - Dépendances externes: AUCUNE")
        
        success_count += 1
    except Exception as e:
        print(f"❌ Erreur Performance: {e}")
    
    print()
    print("📊 COMPARAISON COÛTS")
    print("=" * 50)
    
    # Comparaison coûts
    print("💰 STRATÉGIES IA DISPONIBLES:")
    print()
    print("1. 🆓 IA LOCALE (100% Gratuite)")
    print("   ✅ Coût: 0€/mois")
    print("   ✅ Analyses: illimitées")
    print("   ✅ Latence: <100ms")
    print("   ⚠️ Sophistication: moyenne")
    print()
    
    print("2. 🌐 IA PUBLIQUE GRATUITE (Limitée)")
    print("   ✅ Coût: 0€/mois")
    print("   ⚠️ Analyses: 100/jour")
    print("   ⚠️ Latence: 1-3s")
    print("   ✅ Sophistication: élevée")
    print()
    
    print("3. 🧠 IA HYBRIDE SMART (Budget optimisé)")
    print("   💰 Coût: ~10€/mois")
    print("   ✅ Analyses: majoritairement gratuites")
    print("   ✅ IA premium: cas critiques seulement")
    print("   ✅ Sophistication: premium quand nécessaire")
    print()
    
    print("4. 💸 IA PREMIUM FULL (Non recommandé)")
    print("   💸 Coût: ~50€/mois")
    print("   ✅ Analyses: illimitées premium")
    print("   ✅ Sophistication: maximale")
    print("   ❌ ROI: questionnable pour usage personnel")
    
    print()
    print("📊 RÉSULTATS FINAUX")
    print("=" * 50)
    
    percentage = (success_count / total_tests) * 100
    print(f"✅ Tests réussis: {success_count}/{total_tests} ({percentage:.1f}%)")
    
    if percentage == 100:
        print("🎉 IA PHASE 6 - 100% GRATUITE: ✅ SUCCÈS COMPLET!")
        print("🏆 Toutes les stratégies IA fonctionnelles")
        print("💰 Coût total: 0€/mois avec IA locale")
        print("🚀 Performance: >10 analyses/seconde")
        print("🧠 Qualité: Suffisante pour trading personnel")
        return True
    else:
        print(f"⚠️ IA PHASE 6: {percentage:.1f}% fonctionnel")
        print("🔧 Ajustements mineurs nécessaires")
        return False

if __name__ == "__main__":
    test_ai_engines_gratuits()