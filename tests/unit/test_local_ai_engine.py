"""
Tests pour LocalAIEngine - Moteur IA local gratuit
Phase 2 - Expansion couverture de test THEBOT
"""

import pytest
from unittest.mock import patch, MagicMock
from dash_modules.ai_engine.local_ai_engine import LocalAIEngine


class TestLocalAIEngine:
    """Tests pour le moteur IA local"""

    def setup_method(self):
        """Initialisation avant chaque test"""
        self.engine = LocalAIEngine()

    def test_initialization(self):
        """Test initialisation du moteur IA local"""
        assert self.engine.models_available is True
        assert isinstance(self.engine.sentiment_patterns, dict)
        assert isinstance(self.engine.technical_patterns, dict)
        assert "bullish_keywords" in self.engine.sentiment_patterns
        assert "bearish_keywords" in self.engine.sentiment_patterns
        assert "trend_patterns" in self.engine.technical_patterns

    def test_load_sentiment_patterns(self):
        """Test chargement patterns sentiment"""
        patterns = self.engine._load_sentiment_patterns()

        assert "bullish_keywords" in patterns
        assert "bearish_keywords" in patterns
        assert "neutral_keywords" in patterns

        # Vérifier présence mots-clés importants
        assert "bull" in patterns["bullish_keywords"]
        assert "bear" in patterns["bearish_keywords"]
        assert "stable" in patterns["neutral_keywords"]

    def test_load_technical_patterns(self):
        """Test chargement patterns techniques"""
        patterns = self.engine._load_technical_patterns()

        assert "trend_patterns" in patterns
        assert "reversal_patterns" in patterns

        # Vérifier structure patterns
        assert "strong_uptrend" in patterns["trend_patterns"]
        assert "oversold_bounce" in patterns["reversal_patterns"]

    def test_analyze_market_sentiment_empty(self):
        """Test analyse sentiment avec données vides"""
        result = self.engine.analyze_market_sentiment([])

        assert result["sentiment"] == "neutral"
        assert result["confidence"] == 0
        assert result["score"] == 50

    def test_analyze_market_sentiment_bullish(self):
        """Test analyse sentiment bullish"""
        news_data = [
            {"title": "Stock rises strongly", "description": "Bull market continues"},
            {"title": "Profits increase", "description": "Growth momentum"},
        ]

        result = self.engine.analyze_market_sentiment(news_data)

        assert result["sentiment"] == "bullish"
        assert result["confidence"] > 0
        assert result["score"] > 50
        assert result["analysis"]["bullish_articles"] > 0

    def test_analyze_market_sentiment_bearish(self):
        """Test analyse sentiment bearish"""
        news_data = [
            {"title": "Market falls sharply", "description": "Bear pressure increases"},
            {"title": "Losses reported", "description": "Decline continues"},
        ]

        result = self.engine.analyze_market_sentiment(news_data)

        assert result["sentiment"] == "bearish"
        assert result["confidence"] > 0
        assert result["score"] < 50
        assert result["analysis"]["bearish_articles"] > 0

    def test_analyze_market_sentiment_neutral(self):
        """Test analyse sentiment neutre"""
        news_data = [
            {"title": "Market stable", "description": "Sideways movement"},
            {"title": "Consolidation phase", "description": "Waiting for direction"},
        ]

        result = self.engine.analyze_market_sentiment(news_data)

        assert result["sentiment"] == "neutral"
        assert result["confidence"] == 60
        assert result["score"] == 50

    def test_analyze_sentiment_wrapper(self):
        """Test wrapper analyze_sentiment"""
        news_articles = ["Stock rises strongly", "Profits increase"]

        result = self.engine.analyze_sentiment(news_articles)

        assert "sentiment" in result
        assert "confidence" in result
        assert "score" in result

    def test_analyze_sentiment_stocks_market_type(self):
        """Test analyse sentiment avec type marché stocks"""
        news_articles = ["Company reports earnings growth", "Profits increase significantly"]

        result = self.engine.analyze_sentiment(news_articles, "stocks")

        assert result["confidence"] >= 60  # Bonus confiance pour earnings

    def test_analyze_sentiment_crypto_market_type(self):
        """Test analyse sentiment avec type marché crypto"""
        news_articles = ["Blockchain adoption increases", "Crypto technology advances"]

        result = self.engine.analyze_sentiment(news_articles, "crypto")

        assert result["confidence"] >= 50  # Bonus confiance pour adoption (ajusté)

    def test_analyze_technical_pattern_simple_empty(self):
        """Test analyse technique simple avec données vides"""
        result = self.engine.analyze_technical_pattern_simple([], {})

        assert result["pattern"] == "unknown"
        assert result["confidence"] == 50
        assert result["signals"] == []

    def test_analyze_technical_pattern_uptrend(self):
        """Test analyse pattern technique uptrend"""
        price_data = [100, 105, 110, 115]
        indicators = {
            "sma_20": 100,
            "rsi": 65,
            "volume": 1000000,
            "avg_volume": 800000
        }

        result = self.engine.analyze_technical_pattern_simple(price_data, indicators)

        assert result["pattern"] in ["strong_uptrend", "sideways"]
        assert result["confidence"] > 50
        assert len(result["signals"]) > 0

    def test_analyze_technical_pattern_downtrend(self):
        """Test analyse pattern technique downtrend"""
        price_data = [115, 110, 105, 100]
        indicators = {
            "sma_20": 120,
            "rsi": 25,
            "volume": 1000000,
            "avg_volume": 800000
        }

        result = self.engine.analyze_technical_pattern_simple(price_data, indicators)

        assert result["pattern"] in ["strong_downtrend", "sideways"]
        assert result["confidence"] > 50
        assert len(result["signals"]) > 0

    def test_analyze_technical_pattern_full(self):
        """Test analyse technique complète"""
        price_data = {"close": 105, "volume": 1000000}
        indicators = {
            "sma_20": 100,
            "rsi": 65,
            "avg_volume": 800000
        }

        result = self.engine.analyze_technical_pattern(price_data, indicators)

        assert "pattern" in result
        assert "confidence" in result
        assert "score" in result
        assert "signals" in result
        assert "technical_analysis" in result

    def test_translate_text_empty(self):
        """Test traduction texte vide"""
        result = self.engine.translate_text("")

        assert result["translated_text"] == ""
        assert result["confidence"] == 0

    def test_translate_text_simple(self):
        """Test traduction texte simple"""
        result = self.engine.translate_text("Stock market trading")

        assert "marché" in result["translated_text"].lower()
        assert "trading" in result["translated_text"].lower()
        assert result["confidence"] > 0
        assert result["words_translated"] > 0

    def test_translate_text_no_translation(self):
        """Test traduction avec mots non traduits"""
        result = self.engine.translate_text("xyzabc unknownword")

        assert result["translated_text"] == "xyzabc unknownword"
        assert result["confidence"] == 0
        assert result["words_translated"] == 0

    def test_generate_trading_insight_buy(self):
        """Test génération insight BUY"""
        symbol = "AAPL"
        market_data = {
            "technical_analysis": {
                "score": 80,
                "pattern": "strong_uptrend"
            }
        }
        news_sentiment = {
            "score": 70,
            "sentiment": "bullish"
        }

        result = self.engine.generate_trading_insight(symbol, market_data, news_sentiment)

        assert result["symbol"] == symbol
        assert result["recommendation"] == "BUY"
        assert result["combined_score"] > 70
        assert result["confidence"] > 50

    def test_generate_trading_insight_sell(self):
        """Test génération insight SELL"""
        symbol = "TSLA"
        market_data = {
            "technical_analysis": {
                "score": 20,
                "pattern": "strong_downtrend"
            }
        }
        news_sentiment = {
            "score": 30,
            "sentiment": "bearish"
        }

        result = self.engine.generate_trading_insight(symbol, market_data, news_sentiment)

        assert result["symbol"] == symbol
        assert result["recommendation"] == "SELL"
        assert result["combined_score"] < 40
        assert result["confidence"] > 50

    def test_generate_trading_insight_hold(self):
        """Test génération insight HOLD"""
        symbol = "GOOGL"
        market_data = {
            "technical_analysis": {
                "score": 55,
                "pattern": "sideways"
            }
        }
        news_sentiment = {
            "score": 45,
            "sentiment": "neutral"
        }

        result = self.engine.generate_trading_insight(symbol, market_data, news_sentiment)

        assert result["symbol"] == symbol
        assert result["recommendation"] == "HOLD"
        assert 40 <= result["combined_score"] <= 60

    def test_generate_trading_insight_enhanced_stocks(self):
        """Test insight amélioré pour stocks"""
        symbol = "MSFT"
        technical_data = {"technical_analysis": {"score": 80}}
        sentiment_data = {"score": 70}

        result = self.engine.generate_trading_insight_enhanced(
            symbol, technical_data, sentiment_data, "stocks"
        )

        assert result["action"] == "BUY"
        assert "earnings" in result["explanation"].lower() or "📈" in result["explanation"]

    def test_generate_trading_insight_enhanced_crypto(self):
        """Test insight amélioré pour crypto"""
        symbol = "BTC"
        technical_data = {"technical_analysis": {"score": 80}}
        sentiment_data = {"score": 70}

        result = self.engine.generate_trading_insight_enhanced(
            symbol, technical_data, sentiment_data, "crypto"
        )

        assert result["action"] == "BUY"
        assert "🚀" in result["explanation"] or "momentum" in result["explanation"].lower()

    def test_analyze_market_context_bullish(self):
        """Test analyse contexte marché bullish"""
        all_markets_data = {
            "stocks": {"sentiment_score": 70},
            "crypto": {"sentiment_score": 65},
            "forex": {"sentiment_score": 60},
        }

        result = self.engine.analyze_market_context(all_markets_data)

        assert result["global_sentiment"] == "Risk-On"
        assert result["market_mood"] == "Optimistic"
        assert result["bullish_markets"] >= 2

    def test_analyze_market_context_bearish(self):
        """Test analyse contexte marché bearish"""
        all_markets_data = {
            "stocks": {"sentiment_score": 30},
            "crypto": {"sentiment_score": 35},
            "forex": {"sentiment_score": 40},
        }

        result = self.engine.analyze_market_context(all_markets_data)

        assert result["global_sentiment"] == "Risk-Off"
        assert result["market_mood"] == "Pessimistic"
        assert result["bearish_markets"] >= 2

    def test_analyze_market_context_mixed(self):
        """Test analyse contexte marché mixte"""
        all_markets_data = {
            "stocks": {"sentiment_score": 60},
            "crypto": {"sentiment_score": 40},
            "forex": {"sentiment_score": 50},
        }

        result = self.engine.analyze_market_context(all_markets_data)

        assert result["global_sentiment"] == "Mixed"
        assert result["market_mood"] == "Cautious"

    def test_is_available(self):
        """Test disponibilité du moteur"""
        assert self.engine.is_available() is True

    def test_get_status(self):
        """Test récupération status"""
        status = self.engine.get_status()

        assert status["name"] == "Local AI Engine"
        assert status["status"] == "active"
        assert status["cost"] == "FREE"
        assert "Sentiment Analysis (Keywords)" in status["capabilities"]
        assert "100% Gratuit" in status["advantages"]

    def test_error_handling_technical_pattern(self):
        """Test gestion erreurs analyse technique"""
        # Données invalides pour provoquer erreur
        price_data = None
        indicators = None

        result = self.engine.analyze_technical_pattern(price_data, indicators)

        assert result["pattern"] == "unknown"
        assert result["confidence"] == 50
        assert result["signals"] == []

    def test_error_handling_trading_insight(self):
        """Test gestion erreurs génération insight"""
        # Données invalides
        result = self.engine.generate_trading_insight("TEST", None, None)

        assert result["recommendation"] == "HOLD"
        assert result["confidence"] == 50
        assert "Erreur analyse" in result["explanation"]

    def test_error_handling_market_context(self):
        """Test gestion erreurs analyse contexte"""
        # Données invalides
        result = self.engine.analyze_market_context(None)

        assert result["global_sentiment"] == "Unknown"
        assert result["market_mood"] == "Neutral"