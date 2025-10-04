#!/usr/bin/env python3
"""
Test Modal IA Trading - THEBOT
Vérification du fonctionnement du modal IA
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

# Test d'import du modal IA
try:
    from dash_modules.components.ai_trading_modal import ai_trading_modal, generate_ai_analysis
    print("✅ Modal IA importé avec succès")
    
    # Test de création du modal
    modal = ai_trading_modal.create_modal()
    print("✅ Modal IA créé avec succès")
    
    # Test de génération d'analyse
    analysis = generate_ai_analysis("BTCUSDT", "1h")
    print("✅ Analyse IA générée avec succès")
    print(f"📊 Analyse pour {analysis['symbol']}:")
    print(f"   - Recommandation: {analysis['trading_recommendation']['recommendation']}")
    print(f"   - Confiance: {analysis['trading_recommendation']['confidence']}%")
    print(f"   - Sentiment: {analysis['sentiment_analysis']['sentiment']}")
    
    # Test CSS
    css = ai_trading_modal.get_custom_css()
    print("✅ CSS personnalisé récupéré")
    
    print("\n🎉 Tous les tests du modal IA sont PASSÉS!")
    
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
except Exception as e:
    print(f"❌ Erreur test: {e}")