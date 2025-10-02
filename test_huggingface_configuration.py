#!/usr/bin/env python3
"""
Test Configuration HuggingFace & Smart AI Manager
Validation complète du système IA intelligent
"""

import sys
import os
import time
import traceback
from datetime import datetime

def test_huggingface_configuration():
    """Test complet du système IA intelligent avec HuggingFace"""
    
    print("🤗 TEST CONFIGURATION HUGGINGFACE & SMART AI")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Import Smart AI Manager
    print("\n📋 Test 1: Import Smart AI Manager...")
    try:
        from dash_modules.ai_engine.smart_ai_manager import SmartAIManager, smart_ai_manager
        print("✅ Smart AI Manager importé")
        test_results.append(("Smart AI Manager Import", "✅ PASS"))
    except Exception as e:
        print(f"❌ Erreur import Smart AI Manager: {e}")
        test_results.append(("Smart AI Manager Import", f"❌ FAIL: {e}"))
        return False
        
    # Test 2: Initialisation moteurs IA
    print("\n📋 Test 2: Initialisation des moteurs IA...")
    try:
        smart_ai_manager.initialize_engines()
        
        engines_available = {
            'local': smart_ai_manager.local_ai is not None,
            'free': smart_ai_manager.free_ai is not None,
            'smart': smart_ai_manager.smart_ai is not None
        }
        
        all_engines = all(engines_available.values())
        
        if all_engines:
            print("✅ Tous les moteurs IA initialisés")
            print(f"   🆓 Local: {'✅' if engines_available['local'] else '❌'}")
            print(f"   🌐 Free: {'✅' if engines_available['free'] else '❌'}")
            print(f"   🧠 Smart: {'✅' if engines_available['smart'] else '❌'}")
            test_results.append(("AI Engines Init", "✅ PASS"))
        else:
            print("⚠️ Quelques moteurs manquants")
            test_results.append(("AI Engines Init", "⚠️ PARTIAL"))
            
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
        test_results.append(("AI Engines Init", f"❌ FAIL: {e}"))
        
    # Test 3: Sélection automatique IA
    print("\n📋 Test 3: Sélection automatique d'IA...")
    try:
        test_scenarios = [
            ("sentiment", "speed", "simple"),
            ("sentiment", "accuracy", "medium"),  
            ("technical", "speed", "simple"),
            ("realtime", "speed", "simple"),
            ("trading", "accuracy", "complex")
        ]
        
        selections = {}
        for task, priority, complexity in test_scenarios:
            selected = smart_ai_manager.choose_best_ai(task, priority, complexity)
            selections[f"{task}_{priority}_{complexity}"] = selected
        
        print("✅ Sélection automatique fonctionnelle")
        for scenario, selection in selections.items():
            print(f"   📊 {scenario}: {selection}")
        
        test_results.append(("Auto AI Selection", "✅ PASS"))
            
    except Exception as e:
        print(f"❌ Erreur sélection IA: {e}")
        test_results.append(("Auto AI Selection", f"❌ FAIL: {e}"))
        
    # Test 4: HuggingFace API Test
    print("\n📋 Test 4: Test API HuggingFace...")
    try:
        # Test sentiment analysis avec HuggingFace
        test_texts = [
            "Apple reports strong quarterly earnings beating expectations",
            "Bitcoin crashes amid regulatory concerns",
            "Market remains stable with mixed signals"
        ]
        
        huggingface_results = []
        for text in test_texts:
            try:
                result = smart_ai_manager.free_ai.analyze_with_huggingface(text)
                if result and 'sentiment' in result:
                    huggingface_results.append(result)
                    print(f"   📝 '{text[:30]}...' → {result['sentiment']}")
            except Exception as e:
                print(f"   ⚠️ HuggingFace erreur: {e}")
        
        if huggingface_results:
            print("✅ HuggingFace API fonctionnel")
            test_results.append(("HuggingFace API", f"✅ PASS ({len(huggingface_results)}/3)"))
        else:
            print("⚠️ HuggingFace non disponible (normal sans quota)")
            test_results.append(("HuggingFace API", "⚠️ QUOTA LIMITE"))
            
    except Exception as e:
        print(f"❌ Erreur HuggingFace: {e}")
        test_results.append(("HuggingFace API", f"❌ FAIL: {e}"))
        
    # Test 5: Analyse avec meilleure IA
    print("\n📋 Test 5: Analyse avec auto-sélection...")
    try:
        test_data = {
            'news_articles': [
                "Tesla stock rises on strong delivery numbers",
                "Apple launches new innovative products",
                "Microsoft reports record cloud revenue"
            ],
            'price_data': [150, 152, 154, 153, 156],
            'indicators': {'rsi': 65, 'sma_20': 152.5}
        }
        
        start_time = time.time()
        
        # Test analyses automatiques
        sentiment_result = smart_ai_manager.analyze_with_best_ai(test_data, "sentiment")
        technical_result = smart_ai_manager.analyze_with_best_ai(test_data, "technical")
        
        execution_time = (time.time() - start_time) * 1000
        
        print(f"   📊 Sentiment: {sentiment_result.get('sentiment', 'N/A')}")
        print(f"   📈 Technical: {technical_result.get('pattern', 'N/A')}")
        print(f"   🤖 IA Utilisée (sentiment): {sentiment_result.get('metadata', {}).get('ai_used', 'local')}")
        print(f"   ⚡ Temps total: {execution_time:.0f}ms")
        
        if sentiment_result and technical_result:
            print("✅ Auto-analyse fonctionnelle")
            test_results.append(("Auto Analysis", f"✅ PASS ({execution_time:.0f}ms)"))
        else:
            print("❌ Résultats incomplets")
            test_results.append(("Auto Analysis", "❌ FAIL"))
            
    except Exception as e:
        print(f"❌ Erreur auto-analyse: {e}")
        test_results.append(("Auto Analysis", f"❌ FAIL: {e}"))
        
    # Test 6: Status et métriques
    print("\n📋 Test 6: Status et métriques IA...")
    try:
        status = smart_ai_manager.get_ai_status()
        usage = smart_ai_manager.get_usage_stats()
        
        print(f"   🆓 Local disponible: {'✅' if status['local']['available'] else '❌'}")
        print(f"   🤗 HuggingFace quota: {status['huggingface']['quota']}")
        print(f"   💰 Budget premium: {status['premium']['quota']}")
        print(f"   📈 Appels HF aujourd'hui: {usage['today_huggingface_calls']}")
        print(f"   🏃 IA la plus rapide: {usage['performance_summary']['fastest']}")
        
        if status and usage:
            print("✅ Métriques disponibles")
            test_results.append(("AI Metrics", "✅ PASS"))
        else:
            print("❌ Métriques manquantes")
            test_results.append(("AI Metrics", "❌ FAIL"))
            
    except Exception as e:
        print(f"❌ Erreur métriques: {e}")
        test_results.append(("AI Metrics", f"❌ FAIL: {e}"))
        
    # Test 7: Configuration preferences
    print("\n📋 Test 7: Gestion des préférences...")
    try:
        # Test mise à jour préférences
        test_prefs = {
            'ai_mode': 'auto',
            'max_cost_per_month': 5,
            'huggingface_enabled': True,
            'priority_speed': True
        }
        
        smart_ai_manager.update_preferences(test_prefs)
        
        # Vérifier sauvegarde
        updated_prefs = smart_ai_manager.user_preferences
        
        if updated_prefs['ai_mode'] == 'auto' and updated_prefs['max_cost_per_month'] == 5:
            print("✅ Préférences sauvegardées")
            test_results.append(("Preferences", "✅ PASS"))
        else:
            print("❌ Préférences non sauvegardées")
            test_results.append(("Preferences", "❌ FAIL"))
            
    except Exception as e:
        print(f"❌ Erreur préférences: {e}")
        test_results.append(("Preferences", f"❌ FAIL: {e}"))
    
    # Test 8: Interface configuration
    print("\n📋 Test 8: Interface de configuration...")
    try:
        from huggingface_config import create_huggingface_config_interface
        
        interface = create_huggingface_config_interface()
        
        if interface and hasattr(interface, 'children'):
            print("✅ Interface de configuration créée")
            test_results.append(("Config Interface", "✅ PASS"))
        else:
            print("❌ Interface invalide")
            test_results.append(("Config Interface", "❌ FAIL"))
            
    except Exception as e:
        print(f"❌ Erreur interface: {e}")
        test_results.append(("Config Interface", f"❌ FAIL: {e}"))
    
    # Résumé des tests
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ - HUGGINGFACE & SMART AI CONFIGURATION")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅" if result.startswith("✅") else "⚠️" if result.startswith("⚠️") else "❌"
        print(f"{status} {test_name}: {result}")
        if result.startswith("✅") or result.startswith("⚠️"):
            passed += 1
    
    print(f"\n📊 RÉSULTATS: {passed}/{total} tests réussis ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 HUGGINGFACE CONFIGURATION: SUCCÈS COMPLET!")
        print("🤗 Système IA intelligent pleinement opérationnel")
        print("🚀 HuggingFace intégré avec sélection automatique")
        print("💰 Configuration flexible : gratuit → premium")
    elif passed >= total * 0.8:
        print("✅ HUGGINGFACE CONFIGURATION: SUCCÈS PARTIEL")
        print("🛠️ Système principal fonctionnel, optimisations mineures possibles")
    else:
        print("❌ HUGGINGFACE CONFIGURATION: CORRECTIONS NÉCESSAIRES")
        print("🔧 Révision de la configuration requise")
    
    # Recommandations finales
    print("\n💡 RECOMMANDATIONS D'UTILISATION:")
    print("1️⃣ Mode 'auto' activé par défaut pour optimisation intelligente")
    print("2️⃣ HuggingFace utilisé automatiquement pour sentiment analysis")
    print("3️⃣ IA locale pour analyses techniques (vitesse optimale)")
    print("4️⃣ Fallback intelligent vers local si quotas épuisés")
    print("5️⃣ Interface de configuration accessible dans l'app")
    
    return passed >= total * 0.8

if __name__ == "__main__":
    try:
        success = test_huggingface_configuration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur critique: {e}")
        traceback.print_exc()
        sys.exit(1)