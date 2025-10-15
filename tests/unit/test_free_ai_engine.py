"""
Tests pour Free AI Engine - Moteur IA utilisant APIs gratuites
Tests se concentrant sur les fonctionnalités sans appels réseau réels (mocks)
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from dash_modules.ai_engine.free_ai_engine import FreeAIEngine, free_ai_engine


class TestFreeAIEngine:
    """Tests pour FreeAIEngine"""

    def test_initialization(self):
        """Test d'initialisation du moteur IA gratuit"""
        engine = FreeAIEngine()

        assert engine.huggingface_available is True
        assert engine.openai_free_available is False
        assert engine.gemini_available is False
        assert engine.local_fallback is True
        assert isinstance(engine.request_history, list)
        assert engine.daily_limit == 100

    def test_check_rate_limit(self):
        """Test vérification des limites de taux"""
        engine = FreeAIEngine()

        # Sans historique, devrait passer
        assert engine._check_rate_limit() is True

        # Ajouter des requêtes pour atteindre la limite
        for _ in range(100):
            engine._add_request_to_history()

        # Devrait être limité
        assert engine._check_rate_limit() is False

    def test_add_request_to_history(self):
        """Test ajout de requête à l'historique"""
        engine = FreeAIEngine()

        initial_count = len(engine.request_history)
        engine._add_request_to_history()

        assert len(engine.request_history) == initial_count + 1
        assert isinstance(engine.request_history[-1], datetime)

    @patch('requests.post')
    def test_analyze_with_huggingface_success(self, mock_post):
        """Test analyse HuggingFace réussie"""
        engine = FreeAIEngine()

        # Mock réponse réussie
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "label": "POSITIVE",  # Positive
                "score": 0.85
            }
        ]
        mock_post.return_value = mock_response

        result = engine.analyze_with_huggingface("Great market performance!")

        assert result["sentiment"] == "bullish"
        assert result["confidence"] == 85.0
        assert result["source"] == "HuggingFace (Free)"
        assert result["model"] == "twitter-roberta-base-sentiment"
        assert "raw_result" in result

    @patch('requests.post')
    def test_analyze_with_huggingface_negative(self, mock_post):
        """Test analyse HuggingFace avec sentiment négatif"""
        engine = FreeAIEngine()

        # Mock réponse négative
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "label": "NEGATIVE",  # Negative
                "score": 0.92
            }
        ]
        mock_post.return_value = mock_response

        result = engine.analyze_with_huggingface("Market crash incoming!")

        assert result["sentiment"] == "bearish"
        assert result["confidence"] == 92.0

    @patch('requests.post')
    def test_analyze_with_huggingface_api_error(self, mock_post):
        """Test analyse HuggingFace avec erreur API"""
        engine = FreeAIEngine()

        # Mock erreur API
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        result = engine.analyze_with_huggingface("Test text")

        # Devrait utiliser le fallback local
        assert "sentiment" in result
        assert "confidence" in result
        # Le fallback peut retourner différents formats selon l'implémentation

    @patch('requests.post')
    def test_analyze_with_huggingface_rate_limit(self, mock_post):
        """Test analyse HuggingFace avec rate limit dépassé"""
        engine = FreeAIEngine()

        # Atteindre la limite de taux
        for _ in range(100):
            engine._add_request_to_history()

        result = engine.analyze_with_huggingface("Test text")

        # Devrait utiliser le fallback local
        assert "sentiment" in result
        assert "confidence" in result

    def test_analyze_with_free_llm(self):
        """Test analyse avec LLM gratuit"""
        engine = FreeAIEngine()

        result = engine.analyze_with_free_llm("Analyze market conditions")

        assert isinstance(result, dict)
        assert "analysis" in result
        assert "recommendation" in result
        assert "confidence" in result
        assert result["source"] == "Local LLM Simulation (Free)"
        assert isinstance(result["analysis"], list)

    def test_local_llm_simulation_market(self):
        """Test simulation LLM pour analyse marché"""
        engine = FreeAIEngine()

        result = engine._local_llm_simulation("market analysis", "")

        assert "analysis" in result
        assert "recommendation" in result
        assert result["confidence"] == 75
        assert len(result["analysis"]) > 0
        assert isinstance(result["recommendation"], str)

    def test_local_llm_simulation_crypto(self):
        """Test simulation LLM pour crypto"""
        engine = FreeAIEngine()

        result = engine._local_llm_simulation("bitcoin analysis", "")

        assert "analysis" in result
        assert "recommendation" in result
        assert len(result["analysis"]) > 0
        assert isinstance(result["recommendation"], str)

    def test_local_fallback_analysis(self):
        """Test fallback vers analyse locale"""
        engine = FreeAIEngine()

        # Tester que la fonction fonctionne (elle importe et utilise local_ai_engine)
        result = engine._local_fallback_analysis("Test news", "sentiment-analysis")

        # Vérifier que le résultat a la structure attendue
        assert isinstance(result, dict)
        assert "sentiment" in result
        assert "confidence" in result
        # Le résultat exact dépend de ce que retourne local_ai_engine

    def test_get_daily_usage(self):
        """Test récupération utilisation quotidienne"""
        engine = FreeAIEngine()

        # Sans historique
        usage = engine.get_daily_usage()
        assert usage["requests_today"] == 0
        assert usage["daily_limit"] == 100
        assert usage["remaining"] == 100
        assert usage["percentage_used"] == 0.0

        # Ajouter quelques requêtes
        for _ in range(5):
            engine._add_request_to_history()

        usage = engine.get_daily_usage()
        assert usage["requests_today"] == 5
        assert usage["remaining"] == 95
        assert usage["percentage_used"] == 5.0

    def test_get_available_services(self):
        """Test récupération services disponibles"""
        engine = FreeAIEngine()

        services = engine.get_available_services()

        assert "huggingface" in services
        assert "local_fallback" in services
        assert "openai_free" in services
        assert "gemini_free" in services

        # Vérifier structure HuggingFace
        hf = services["huggingface"]
        assert hf["available"] is True
        assert hf["cost"] == "FREE"
        assert "limits" in hf
        assert "models" in hf

        # Vérifier local fallback
        local = services["local_fallback"]
        assert local["available"] is True
        assert local["cost"] == "FREE"
        assert local["limits"] == "Unlimited"

    @patch('dash_modules.ai_engine.local_ai_engine')
    def test_comprehensive_analysis(self, mock_local):
        """Test analyse complète"""
        engine = FreeAIEngine()

        # Mock les méthodes locales
        mock_local.analyze_market_sentiment.return_value = {
            "sentiment": "bullish",
            "confidence": 75
        }
        mock_local.analyze_technical_pattern.return_value = {
            "pattern": "bullish_flag",
            "strength": 80
        }
        mock_local.generate_trading_insight.return_value = {
            "signal": "BUY",
            "confidence": 70
        }

        market_data = {"price_data": {}, "indicators": {}}
        news_data = [{"title": "Market up", "description": "Positive news"}]

        result = engine.comprehensive_analysis("BTCUSDT", market_data, news_data)

        assert result["symbol"] == "BTCUSDT"
        assert "sentiment_analysis" in result
        assert "technical_analysis" in result
        assert "trading_insight" in result
        assert "usage_stats" in result
        assert result["total_cost"] == "FREE"
        assert "timestamp" in result

    def test_global_instance(self):
        """Test de l'instance globale"""
        assert isinstance(free_ai_engine, FreeAIEngine)
        assert hasattr(free_ai_engine, 'huggingface_available')
        assert hasattr(free_ai_engine, 'request_history')