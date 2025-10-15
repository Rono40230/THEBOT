"""
Tests pour SmartAIEngine - Moteur IA hybride intelligent
Phase 2 - Expansion couverture de test THEBOT
"""

import pytest
from unittest.mock import patch, MagicMock
from dash_modules.ai_engine.smart_ai_engine import SmartAIEngine


class TestSmartAIEngine:
    """Tests pour le moteur IA hybride"""

    def setup_method(self):
        """Initialisation avant chaque test"""
        self.engine = SmartAIEngine()

    def test_initialization(self):
        """Test initialisation du moteur IA hybride"""
        assert self.engine.monthly_budget_euro == 10
        assert self.engine.daily_budget_euro == 10 / 30
        assert self.engine.current_monthly_spend == 0
        assert self.engine.current_daily_spend == 0
        assert self.engine.openai_available is False
        assert self.engine.claude_available is False
        assert self.engine.local_ai_always_available is True
        assert isinstance(self.engine.paid_ai_triggers, dict)
        assert isinstance(self.engine.daily_usage_log, list)

    def test_should_use_paid_ai_budget_exhausted_daily(self):
        """Test décision IA payante - budget quotidien épuisé"""
        self.engine.current_daily_spend = self.engine.daily_budget_euro

        use_paid, reason = self.engine._should_use_paid_ai({})

        assert use_paid is False
        assert "Budget quotidien épuisé" in reason

    def test_should_use_paid_ai_budget_exhausted_monthly(self):
        """Test décision IA payante - budget mensuel épuisé"""
        self.engine.current_monthly_spend = self.engine.monthly_budget_euro

        use_paid, reason = self.engine._should_use_paid_ai({})

        assert use_paid is False
        assert "Budget mensuel épuisé" in reason

    def test_should_use_paid_ai_high_volatility(self):
        """Test décision IA payante - haute volatilité"""
        context = {"volatility_24h": 6}  # > 5%

        use_paid, reason = self.engine._should_use_paid_ai(context)

        assert use_paid is True
        assert "high_volatility" in reason

    def test_should_use_paid_ai_major_news_event(self):
        """Test décision IA payante - événement majeur"""
        context = {"major_news_event": True}

        use_paid, reason = self.engine._should_use_paid_ai(context)

        assert use_paid is True
        assert "major_news_event" in reason

    def test_should_use_paid_ai_unusual_volume(self):
        """Test décision IA payante - volume inhabituel"""
        context = {"volume_vs_average": 2.5}  # > 2

        use_paid, reason = self.engine._should_use_paid_ai(context)

        assert use_paid is True
        assert "unusual_volume" in reason

    def test_should_use_paid_ai_conflicting_signals(self):
        """Test décision IA payante - signaux contradictoires"""
        context = {"conflicting_signals": True}

        use_paid, reason = self.engine._should_use_paid_ai(context)

        assert use_paid is True
        assert "conflicting_signals" in reason

    def test_should_use_paid_ai_no_triggers(self):
        """Test décision IA payante - aucun trigger activé"""
        context = {"volatility_24h": 2, "major_news_event": False}

        use_paid, reason = self.engine._should_use_paid_ai(context)

        assert use_paid is False
        assert "Pas de justification" in reason

    def test_estimate_request_cost(self):
        """Test estimation coût requête"""
        context = {"prompt": "Test prompt de 20 caractères"}

        cost = self.engine._estimate_request_cost(context)

        assert isinstance(cost, float)
        assert cost > 0
        assert cost < 1  # Devrait être petit pour prompt court

    def test_log_ai_usage(self):
        """Test logging utilisation IA"""
        initial_daily = self.engine.current_daily_spend
        initial_monthly = self.engine.current_monthly_spend

        self.engine._log_ai_usage("test_service", 0.5, "test_context")

        assert self.engine.current_daily_spend == initial_daily + 0.5
        assert self.engine.current_monthly_spend == initial_monthly + 0.5
        assert len(self.engine.daily_usage_log) == 1

        log_entry = self.engine.daily_usage_log[0]
        assert log_entry["service"] == "test_service"
        assert log_entry["cost_eur"] == 0.5
        assert log_entry["context"] == "test_context"

    @patch('dash_modules.ai_engine.local_ai_engine')
    def test_analyze_market_comprehensive_local_only(self, mock_local_ai):
        """Test analyse complète - stratégie locale seulement"""
        # Mock local AI responses
        mock_local_ai.analyze_market_sentiment.return_value = {
            "sentiment": "bullish", "confidence": 70, "score": 65
        }
        mock_local_ai.analyze_technical_pattern.return_value = {
            "pattern": "uptrend", "confidence": 75, "score": 70
        }
        mock_local_ai.generate_trading_insight.return_value = {
            "recommendation": "BUY", "confidence": 72, "symbol": "AAPL"
        }

        symbol = "AAPL"
        market_data = {"price_data": {"close": 150}, "indicators": {}}
        news_data = [{"title": "Stock rises strongly with bullish momentum"}]

        result = self.engine.analyze_market_comprehensive(symbol, market_data, news_data)

        assert result["symbol"] == symbol
        assert result["strategy"] == "local_only"
        assert result["enhanced_analysis"] is None
        assert result["cost_breakdown"]["total"] == 0.0
        assert "budget_status" in result

    @patch('dash_modules.ai_engine.local_ai_engine')
    def test_analyze_market_comprehensive_hybrid_paid_ai(self, mock_local_ai):
        """Test analyse complète - stratégie hybride avec IA payante"""
        # Setup pour trigger IA payante
        self.engine.openai_available = True

        # Mock local AI responses
        mock_local_ai.analyze_market_sentiment.return_value = {
            "sentiment": "bullish", "confidence": 70, "score": 65
        }
        mock_local_ai.analyze_technical_pattern.return_value = {
            "pattern": "uptrend", "confidence": 75, "score": 70
        }
        mock_local_ai.generate_trading_insight.return_value = {
            "recommendation": "BUY", "confidence": 72, "symbol": "AAPL"
        }

        symbol = "AAPL"
        market_data = {"price_data": {"close": 150, "high": 160, "low": 140}, "indicators": {}}
        news_data = [{"title": "Fed meeting today"}]
        context = {"major_news_event": True}

        result = self.engine.analyze_market_comprehensive(symbol, market_data, news_data, context)

        assert result["strategy"] == "hybrid"
        assert result["enhanced_analysis"] is not None
        assert result["cost_breakdown"]["paid"] > 0
        assert result["cost_breakdown"]["total"] > 0
        assert "combined_insight" in result

    def test_enrich_context_volatility(self):
        """Test enrichissement contexte - volatilité"""
        symbol = "AAPL"
        market_data = {
            "price_data": {"close": 100, "high": 110, "low": 90},
            "indicators": {}
        }
        news_data = []
        base_context = {}

        enriched = self.engine._enrich_context(symbol, market_data, news_data, base_context)

        assert enriched["volatility_24h"] == 20.0  # ((110-90)/100)*100
        assert enriched["symbol"] == symbol

    def test_enrich_context_volume_ratio(self):
        """Test enrichissement contexte - ratio volume"""
        symbol = "AAPL"
        market_data = {
            "price_data": {"volume": 1000000},
            "indicators": {"avg_volume": 500000}
        }
        news_data = []
        base_context = {}

        enriched = self.engine._enrich_context(symbol, market_data, news_data, base_context)

        assert enriched["volume_vs_average"] == 2.0

    def test_enrich_context_major_news_event(self):
        """Test enrichissement contexte - événement majeur"""
        symbol = "AAPL"
        market_data = {"price_data": {}, "indicators": {}}
        news_data = [{"title": "Fed announces interest rate decision"}]
        base_context = {}

        enriched = self.engine._enrich_context(symbol, market_data, news_data, base_context)

        assert enriched["major_news_event"] is True
        assert enriched["news_count"] == 1

    def test_enrich_context_analysis_complexity(self):
        """Test enrichissement contexte - complexité analyse"""
        symbol = "AAPL"
        market_data = {
            "price_data": {"close": 100, "high": 106, "low": 94},
            "indicators": {}
        }
        news_data = [{"title": "Fed meeting"}]
        base_context = {}

        enriched = self.engine._enrich_context(symbol, market_data, news_data, base_context)

        assert enriched["analysis_complexity"] == "high"

    def test_call_paid_ai_simulation(self):
        """Test appel IA payante (simulation)"""
        context = {"test": "data"}
        local_insight = {"recommendation": "BUY"}

        result = self.engine._call_paid_ai(context, local_insight)

        assert "enhanced_insights" in result
        assert "confidence_boost" in result
        assert result["confidence_boost"] == 15
        assert "additional_signals" in result
        assert result["source"] == "Premium AI (Simulated)"
        assert "note" in result

    def test_combine_analyses(self):
        """Test combinaison analyses locale et premium"""
        local = {
            "recommendation": "BUY",
            "confidence": 70,
            "explanation": "Signal technique positif"
        }
        enhanced = {
            "confidence_boost": 15,
            "enhanced_insights": ["Analyse macro favorable"],
            "additional_signals": ["macro_correlation"],
            "premium_recommendation": "BUY avec prudence"
        }

        combined = self.engine._combine_analyses(local, enhanced)

        assert combined["recommendation"] == "BUY"
        assert combined["confidence"] == 85  # 70 + 15
        assert combined["original_confidence"] == 70
        assert "Signal technique positif" in combined["combined_insights"]
        assert combined["premium_signals"] == ["macro_correlation"]
        assert combined["analysis_quality"] == "premium"

    def test_get_budget_status(self):
        """Test récupération status budget"""
        # Ajouter quelques dépenses
        self.engine.current_daily_spend = 0.5
        self.engine.current_monthly_spend = 2.5

        status = self.engine._get_budget_status()

        assert status["daily_spend"] == 0.5
        assert status["monthly_spend"] == 2.5
        assert status["daily_remaining"] == pytest.approx(self.engine.daily_budget_euro - 0.5, abs=0.001)
        assert status["monthly_remaining"] == self.engine.monthly_budget_euro - 2.5
        assert "usage_level" in status

    def test_get_strategy_summary(self):
        """Test résumé stratégie IA hybride"""
        summary = self.engine.get_strategy_summary()

        assert summary["name"] == "Smart Hybrid AI"
        assert "budget" in summary
        assert "cost_optimization" in summary
        assert "quality" in summary
        assert "current_status" in summary

        cost_opt = summary["cost_optimization"]
        assert "90% des analyses" in cost_opt["local_ai_usage"]
        assert "10% cas critiques" in cost_opt["paid_ai_usage"]
        assert "80% vs full premium" in cost_opt["estimated_savings"]

    def test_budget_usage_level_conservative(self):
        """Test niveau usage budget - conservatif"""
        self.engine.current_daily_spend = self.engine.daily_budget_euro * 0.3  # 30%

        status = self.engine._get_budget_status()

        assert status["usage_level"] == "conservative"

    def test_budget_usage_level_active(self):
        """Test niveau usage budget - actif"""
        self.engine.current_daily_spend = self.engine.daily_budget_euro * 0.7  # 70%

        status = self.engine._get_budget_status()

        assert status["usage_level"] == "active"

    @patch('dash_modules.ai_engine.local_ai_engine')
    def test_analyze_market_comprehensive_paid_ai_error_fallback(self, mock_local_ai):
        """Test analyse complète - erreur IA payante avec fallback"""
        # Setup pour trigger IA payante mais simuler erreur
        self.engine.openai_available = True

        # Mock local AI
        mock_local_ai.analyze_market_sentiment.return_value = {
            "sentiment": "neutral", "confidence": 50, "score": 50
        }
        mock_local_ai.analyze_technical_pattern.return_value = {
            "pattern": "sideways", "confidence": 60, "score": 55
        }
        mock_local_ai.generate_trading_insight.return_value = {
            "recommendation": "HOLD", "confidence": 55, "symbol": "TEST"
        }

        # Mock pour faire échouer l'IA payante
        with patch.object(self.engine, '_call_paid_ai', side_effect=Exception("API Error")):
            symbol = "TEST"
            market_data = {"price_data": {"close": 100, "high": 110, "low": 90}, "indicators": {}}
            news_data = [{"title": "Fed meeting"}]
            context = {"major_news_event": True}

            result = self.engine.analyze_market_comprehensive(symbol, market_data, news_data, context)

            assert result["strategy"] == "hybrid"
            assert result["enhanced_analysis"]["error"] == "API Error"
            assert result["enhanced_analysis"]["fallback"] == "local_only"