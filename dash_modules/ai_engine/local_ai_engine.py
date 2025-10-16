from src.thebot.core.logger import logger
"""
IA Locale Gratuite - Solution Open Source pour THEBOT
Phase 6 - Intelligence Artificielle 100% Gratuite
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalAIEngine:
    """
    Moteur IA local gratuit utilisant :
    - Analyse statistique avancée
    - Modèles ML légers (scikit-learn)
    - Patterns recognition algorithmique
    - Sentiment analysis basique
    """

    def __init__(self):
        self.models_available = True
        self.sentiment_patterns = self._load_sentiment_patterns()
        self.technical_patterns = self._load_technical_patterns()

        logger.info("🤖 IA Locale initialisée - 100% GRATUITE")

    def _load_sentiment_patterns(self) -> Dict:
        """Charger patterns de sentiment prédéfinis"""
        return {
            "bullish_keywords": [
                "bull",
                "bullish",
                "rise",
                "rising",
                "up",
                "gain",
                "gains",
                "profit",
                "profits",
                "positive",
                "growth",
                "increase",
                "rally",
                "surge",
                "pump",
                "moon",
                "breakout",
                "support",
            ],
            "bearish_keywords": [
                "bear",
                "bearish",
                "fall",
                "falling",
                "down",
                "loss",
                "losses",
                "negative",
                "decline",
                "decrease",
                "crash",
                "dump",
                "resistance",
                "breakdown",
                "correction",
                "dip",
                "sell-off",
            ],
            "neutral_keywords": [
                "stable",
                "sideways",
                "consolidation",
                "range",
                "holding",
                "waiting",
                "uncertain",
                "mixed",
                "flat",
            ],
        }

    def _load_technical_patterns(self) -> Dict:
        """Charger patterns techniques algorithmiques"""
        return {
            "trend_patterns": {
                "strong_uptrend": {
                    "sma_above": True,
                    "rsi_range": (40, 70),
                    "volume_increase": True,
                },
                "strong_downtrend": {
                    "sma_below": True,
                    "rsi_range": (30, 60),
                    "volume_increase": True,
                },
                "sideways": {
                    "sma_neutral": True,
                    "rsi_range": (40, 60),
                    "volume_normal": True,
                },
            },
            "reversal_patterns": {
                "oversold_bounce": {"rsi_below": 30, "support_touch": True},
                "overbought_decline": {"rsi_above": 70, "resistance_touch": True},
            },
        }

    def analyze_sentiment(
        self, news_articles: List[str], market_type: str = "general"
    ) -> Dict:
        """Wrapper pour compatibilité - analyse sentiment à partir de textes simples"""
        # Convertir textes en format dict pour analyze_market_sentiment
        news_data = []
        for article in news_articles:
            news_data.append({"title": article, "description": "", "content": article})

        result = self.analyze_market_sentiment(news_data)

        # Adapter pour marché spécifique
        if market_type == "stocks":
            # Ajuster pour stocks (focus sur earnings, fundamentals)
            if (
                "earnings" in " ".join(news_articles).lower()
                or "profit" in " ".join(news_articles).lower()
            ):
                result["confidence"] = min(95, result["confidence"] + 5)
        elif market_type == "crypto":
            # Ajuster pour crypto (focus sur adoption, technology)
            if (
                "adoption" in " ".join(news_articles).lower()
                or "blockchain" in " ".join(news_articles).lower()
            ):
                result["confidence"] = min(95, result["confidence"] + 5)
        elif market_type == "forex":
            # Ajuster pour forex (focus sur économie, banques centrales)
            if (
                "fed" in " ".join(news_articles).lower()
                or "central bank" in " ".join(news_articles).lower()
            ):
                result["confidence"] = min(95, result["confidence"] + 5)

        return result

    def analyze_technical_pattern_simple(
        self, price_data: List[float], indicators: Dict
    ) -> Dict:
        """Wrapper pour compatibilité - analyse technique avec liste de prix simple"""
        if not price_data:
            return {"pattern": "unknown", "confidence": 50, "signals": []}

        # Convertir en format dict attendu
        price_dict = {
            "close": price_data[-1] if price_data else 0,
            "volume": indicators.get("volume", 1000000),
        }

        return self.analyze_technical_pattern(price_dict, indicators)

    def generate_trading_insight_enhanced(
        self,
        symbol: str,
        technical_data: Dict,
        sentiment_data: Dict,
        market_type: str = "general",
    ) -> Dict:
        """Wrapper pour compatibilité avec amélioration par type de marché"""

        result = self.generate_trading_insight(symbol, technical_data, sentiment_data)

        # Personnalisation par type de marché
        if market_type == "stocks":
            result["action"] = result["recommendation"]  # Alias pour compatibilité
            if result["recommendation"] == "BUY":
                result["explanation"] = (
                    f"📈 {symbol}: Analyse technique positive + sentiment earnings favorable. Position long recommandée."
                )
            elif result["recommendation"] == "SELL":
                result["explanation"] = (
                    f"📉 {symbol}: Signaux techniques baissiers + sentiment négatif. Réduction position conseillée."
                )
            else:
                result["explanation"] = (
                    f"⚖️ {symbol}: Signaux mixtes. Maintien position actuelle recommandé."
                )

        elif market_type == "crypto":
            result["action"] = result["recommendation"]
            if result["recommendation"] == "BUY":
                result["explanation"] = (
                    f"🚀 {symbol}: Momentum haussier confirmé + sentiment crypto positif. Accumulation."
                )
            elif result["recommendation"] == "SELL":
                result["explanation"] = (
                    f"🔴 {symbol}: Faiblesse technique + sentiment bearish. Prise de profits."
                )
            else:
                result["explanation"] = (
                    f"🎯 {symbol}: Consolidation. Attendre confirmation directionnelle."
                )

        elif market_type == "forex":
            result["action"] = result["recommendation"]
            if result["recommendation"] == "BUY":
                result["explanation"] = (
                    f"💰 {symbol}: Fondamentaux économiques solides + technique haussier. Long bias."
                )
            elif result["recommendation"] == "SELL":
                result["explanation"] = (
                    f"📉 {symbol}: Pression économique + signaux techniques négatifs. Short bias."
                )
            else:
                result["explanation"] = (
                    f"⚡ {symbol}: Attente données économiques. Position neutre."
                )

        return result

    def analyze_market_sentiment(self, news_data: List[Dict]) -> Dict:
        """Analyser sentiment marché via patterns keywords"""
        if not news_data:
            return {"sentiment": "neutral", "confidence": 0, "score": 50}

        bullish_count = 0
        bearish_count = 0
        total_articles = len(news_data)

        for article in news_data:
            title = (article.get("title", "") or "").lower()
            description = (article.get("description", "") or "").lower()
            content = f"{title} {description}"

            # Compter keywords bullish
            bullish_score = sum(
                1
                for keyword in self.sentiment_patterns["bullish_keywords"]
                if keyword in content
            )

            # Compter keywords bearish
            bearish_score = sum(
                1
                for keyword in self.sentiment_patterns["bearish_keywords"]
                if keyword in content
            )

            if bullish_score > bearish_score:
                bullish_count += 1
            elif bearish_score > bullish_score:
                bearish_count += 1

        # Calculer sentiment global
        if bullish_count > bearish_count:
            sentiment = "bullish"
            confidence = min(90, (bullish_count / total_articles) * 100)
            score = 50 + (confidence / 2)
        elif bearish_count > bullish_count:
            sentiment = "bearish"
            confidence = min(90, (bearish_count / total_articles) * 100)
            score = 50 - (confidence / 2)
        else:
            sentiment = "neutral"
            confidence = 60
            score = 50

        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 1),
            "score": round(score, 1),
            "analysis": {
                "bullish_articles": bullish_count,
                "bearish_articles": bearish_count,
                "neutral_articles": total_articles - bullish_count - bearish_count,
                "total_articles": total_articles,
            },
        }

    def analyze_technical_pattern(self, price_data: Dict, indicators: Dict) -> Dict:
        """Analyser pattern technique via règles algorithmiques"""
        try:
            current_price = price_data.get("close", 0)
            sma_20 = indicators.get("sma_20", current_price)
            rsi = indicators.get("rsi", 50)
            volume = price_data.get("volume", 0)
            avg_volume = indicators.get("avg_volume", volume)

            # Analyse trend
            trend_score = 0
            trend_signals = []

            if current_price > sma_20:
                trend_score += 25
                trend_signals.append("Prix au-dessus SMA 20")

            if 40 <= rsi <= 70:
                trend_score += 25
                trend_signals.append("RSI dans zone saine")
            elif rsi > 70:
                trend_score -= 10
                trend_signals.append("RSI surachat possible")
            elif rsi < 30:
                trend_score += 15
                trend_signals.append("RSI survente - rebond possible")

            if volume > avg_volume * 1.2:
                trend_score += 15
                trend_signals.append("Volume supérieur à la moyenne")

            # Déterminer pattern
            if trend_score >= 60:
                pattern = "strong_uptrend"
                confidence = min(95, trend_score)
            elif trend_score <= 20:
                pattern = "strong_downtrend"
                confidence = min(95, 100 - trend_score)
            else:
                pattern = "sideways"
                confidence = 65

            return {
                "pattern": pattern,
                "confidence": confidence,
                "score": trend_score,
                "signals": trend_signals,
                "technical_analysis": {
                    "price_vs_sma": "above" if current_price > sma_20 else "below",
                    "rsi_level": rsi,
                    "volume_status": "high" if volume > avg_volume * 1.2 else "normal",
                },
            }

        except Exception as e:
            logger.error(f"Erreur analyse technique: {e}")
            return {"pattern": "unknown", "confidence": 50, "signals": []}

    def translate_text(self, text: str, target_lang: str = "fr") -> Dict:
        """Traduire texte en français via dictionnaire local simple"""
        try:
            if not text or not text.strip():
                return {"translated_text": text, "confidence": 0}

            # Dictionnaire de traduction simple anglais -> français
            translations = {
                # Mots économiques/financiers courants
                "stock": "action",
                "stocks": "actions",
                "market": "marché",
                "markets": "marchés",
                "price": "prix",
                "prices": "prix",
                "trading": "trading",
                "trader": "trader",
                "investment": "investissement",
                "investor": "investisseur",
                "buy": "acheter",
                "sell": "vendre",
                "growth": "croissance",
                "profit": "profit",
                "loss": "perte",
                "earnings": "bénéfices",
                "revenue": "revenus",
                "company": "entreprise",
                "economic": "économique",
                "economy": "économie",
                "bank": "banque",
                "interest": "intérêt",
                "rate": "taux",
                "federal": "fédéral",
                "central": "central",
                "inflation": "inflation",
                "recession": "récession",
                "recovery": "reprise",
                "currency": "devise",
                "dollar": "dollar",
                "euro": "euro",
                "bitcoin": "bitcoin",
                "crypto": "crypto",
                "cryptocurrency": "cryptomonnaie",
                "blockchain": "blockchain",
                "technology": "technologie",
                "tech": "tech",
                "artificial": "artificiel",
                "intelligence": "intelligence",
                "data": "données",
                "analysis": "analyse",
                "report": "rapport",
                "news": "nouvelles",
                "update": "mise à jour",
                "forecast": "prévision",
                "outlook": "perspectives",
                "target": "objectif",
                # Mots de liaison et temps
                "and": "et",
                "or": "ou",
                "but": "mais",
                "with": "avec",
                "from": "de",
                "to": "à",
                "for": "pour",
                "in": "dans",
                "on": "sur",
                "at": "à",
                "up": "hausse",
                "down": "baisse",
                "higher": "plus haut",
                "lower": "plus bas",
                "increase": "augmentation",
                "decrease": "diminution",
                "rise": "hausse",
                "fall": "chute",
                "strong": "fort",
                "weak": "faible",
                "stable": "stable",
                "volatile": "volatil",
                "risk": "risque",
                "opportunity": "opportunité",
                # Temps
                "today": "aujourd'hui",
                "yesterday": "hier",
                "tomorrow": "demain",
                "week": "semaine",
                "month": "mois",
                "year": "année",
                "quarter": "trimestre",
                "morning": "matin",
                "afternoon": "après-midi",
                "evening": "soir",
                # Adjectifs courants
                "good": "bon",
                "bad": "mauvais",
                "new": "nouveau",
                "old": "ancien",
                "big": "grand",
                "small": "petit",
                "high": "élevé",
                "low": "bas",
                "positive": "positif",
                "negative": "négatif",
                "neutral": "neutre",
            }

            # Traduction mot par mot (simple)
            words = text.split()
            translated_words = []

            for word in words:
                # Nettoyer le mot (enlever ponctuation)
                clean_word = word.lower().strip('.,!?;:"()[]{}')

                # Chercher traduction
                if clean_word in translations:
                    # Garder la casse originale
                    if word[0].isupper() and len(word) > 1:
                        translated = translations[clean_word].capitalize()
                    else:
                        translated = translations[clean_word]

                    # Rajouter ponctuation
                    punctuation = "".join(c for c in word if not c.isalnum())
                    translated_words.append(translated + punctuation)
                else:
                    # Garder mot original si pas de traduction
                    translated_words.append(word)

            translated_text = " ".join(translated_words)

            # Calculer confiance basée sur % de mots traduits
            translated_count = sum(
                1
                for word in words
                if word.lower().strip('.,!?;:"()[]{}') in translations
            )
            confidence = min(90, (translated_count / len(words)) * 100) if words else 0

            return {
                "translated_text": translated_text,
                "confidence": round(confidence, 1),
                "original_text": text,
                "words_translated": translated_count,
                "total_words": len(words),
            }

        except Exception as e:
            logger.error(f"Erreur traduction: {e}")
            return {"translated_text": text, "confidence": 0}

    def generate_trading_insight(
        self,
        symbol: str,
        market_data: Dict,
        news_sentiment: Dict,
        market_type: str = "general",
    ) -> Dict:
        """Générer insight trading combiné technique + sentiment"""
        try:
            technical = market_data.get("technical_analysis", {})
            sentiment = news_sentiment

            # Score combiné
            technical_score = technical.get("score", 50)
            sentiment_score = sentiment.get("score", 50)

            # Pondération : 60% technique, 40% sentiment
            combined_score = (technical_score * 0.6) + (sentiment_score * 0.4)

            # Génération recommendation
            if combined_score >= 70:
                recommendation = "BUY"
                strength = "Strong"
                color = "success"
            elif combined_score >= 60:
                recommendation = "BUY"
                strength = "Moderate"
                color = "success"
            elif combined_score <= 30:
                recommendation = "SELL"
                strength = "Strong"
                color = "danger"
            elif combined_score <= 40:
                recommendation = "SELL"
                strength = "Moderate"
                color = "danger"
            else:
                recommendation = "HOLD"
                strength = "Neutral"
                color = "warning"

            # Génération explication selon type de marché
            explanations = []
            if market_type == "stocks":
                if technical_score > 60:
                    explanations.append("📈 Momentum haussier confirmé")
                elif technical_score < 40:
                    explanations.append("📉 Signaux techniques baissiers")

                if sentiment_score > 60:
                    explanations.append("💰 Sentiment earnings positif")
                elif sentiment_score < 40:
                    explanations.append("📉 Sentiment fondamentaux négatif")
            else:
                if technical_score > 60:
                    explanations.append("📈 Signaux techniques positifs")
                elif technical_score < 40:
                    explanations.append("📉 Signaux techniques négatifs")

                if sentiment_score > 60:
                    explanations.append("📰 Sentiment marché positif")
                elif sentiment_score < 40:
                    explanations.append("📰 Sentiment marché négatif")

            return {
                "symbol": symbol,
                "recommendation": recommendation,
                "action": recommendation,  # Alias pour compatibilité
                "strength": strength,
                "confidence": round(abs(combined_score - 50) + 50, 1),
                "combined_score": round(combined_score, 1),
                "color": color,
                "explanation": (
                    " | ".join(explanations) if explanations else "Analyse neutre"
                ),
                "breakdown": {
                    "technical_score": round(technical_score, 1),
                    "sentiment_score": round(sentiment_score, 1),
                    "weighting": "60% technique + 40% sentiment",
                },
                "timestamp": datetime.now().isoformat(),
                "source": "Local AI Engine (Free)",
            }

        except Exception as e:
            logger.error(f"Erreur génération insight: {e}")
            return {
                "symbol": symbol,
                "recommendation": "HOLD",
                "action": "HOLD",
                "confidence": 50,
                "explanation": "Erreur analyse - position neutre recommandée",
            }

    def analyze_market_context(self, all_markets_data: Dict) -> Dict:
        """Analyser contexte marché global"""
        try:
            bullish_markets = 0
            bearish_markets = 0
            total_markets = len(all_markets_data)

            for market, data in all_markets_data.items():
                sentiment_score = data.get("sentiment_score", 50)
                if sentiment_score > 55:
                    bullish_markets += 1
                elif sentiment_score < 45:
                    bearish_markets += 1

            # Déterminer tendance globale
            if bullish_markets > bearish_markets * 1.5:
                global_sentiment = "Risk-On"
                market_mood = "Optimistic"
            elif bearish_markets > bullish_markets * 1.5:
                global_sentiment = "Risk-Off"
                market_mood = "Pessimistic"
            else:
                global_sentiment = "Mixed"
                market_mood = "Cautious"

            return {
                "global_sentiment": global_sentiment,
                "market_mood": market_mood,
                "bullish_markets": bullish_markets,
                "bearish_markets": bearish_markets,
                "neutral_markets": total_markets - bullish_markets - bearish_markets,
                "analysis": f"{bullish_markets}/{total_markets} marchés bullish",
                "recommendation": f"Contexte {global_sentiment} - Approche {market_mood.lower()}",
            }

        except Exception as e:
            logger.error(f"Erreur analyse contexte: {e}")
            return {"global_sentiment": "Unknown", "market_mood": "Neutral"}

    def is_available(self) -> bool:
        """Toujours disponible car local et gratuit"""
        return True

    def get_status(self) -> Dict:
        """Status du moteur IA local"""
        return {
            "name": "Local AI Engine",
            "status": "active",
            "cost": "FREE",
            "capabilities": [
                "Sentiment Analysis (Keywords)",
                "Technical Pattern Recognition",
                "Trading Insights Generation",
                "Market Context Analysis",
            ],
            "limitations": [
                "Basé sur règles algorithmiques",
                "Pas de ML avancé (transformers)",
                "Analyse simple mais efficace",
            ],
            "advantages": [
                "100% Gratuit",
                "Pas de limites API",
                "Données privées (local)",
                "Réponse instantanée",
            ],
        }


# Instance globale
local_ai_engine = LocalAIEngine()
