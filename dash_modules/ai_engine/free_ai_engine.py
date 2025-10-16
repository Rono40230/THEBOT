from src.thebot.core.logger import logger
"""
IA Gratuite Publique - APIs avec tiers gratuits
Phase 6 - Intelligence Artificielle Gratuite Limitée
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class FreeAIEngine:
    """
    Moteur IA utilisant APIs gratuites :
    - Hugging Face (gratuit avec limites)
    - OpenAI Free Tier (limité)
    - Google Gemini (gratuit avec quotas)
    - Fallback vers IA locale
    """

    def __init__(self):
        self.huggingface_available = True
        self.openai_free_available = False  # Nécessite clé
        self.gemini_available = False  # Nécessite clé
        self.local_fallback = True

        # Rate limiting
        self.request_history = []
        self.daily_limit = 100  # Limite conservative

        logger.info("🤖 IA Publique Gratuite initialisée")

    def _check_rate_limit(self) -> bool:
        """Vérifier limites de rate"""
        now = datetime.now()
        # Nettoyer historique > 24h
        self.request_history = [
            req_time
            for req_time in self.request_history
            if now - req_time < timedelta(hours=24)
        ]

        return len(self.request_history) < self.daily_limit

    def _add_request_to_history(self):
        """Ajouter requête à l'historique"""
        self.request_history.append(datetime.now())

    def analyze_with_huggingface(
        self, text: str, task: str = "sentiment-analysis", api_key: str = None
    ) -> Dict:
        """Analyser avec Hugging Face (GRATUIT avec limites, meilleur avec API key)"""
        if not self._check_rate_limit():
            logger.warning("Rate limit atteint - fallback vers IA locale")
            return self._local_fallback_analysis(text, task)

        try:
            # API Hugging Face
            API_URL = f"https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"

            headers = {"Content-Type": "application/json"}

            # Ajouter clé API si disponible
            if api_key and api_key.strip():
                headers["Authorization"] = f"Bearer {api_key.strip()}"
                logger.info("🔑 Utilisation clé API HuggingFace")
            else:
                logger.info("🆓 Utilisation API HuggingFace publique")

            payload = {"inputs": text[:512]}  # Limite longueur

            response = requests.post(API_URL, headers=headers, json=payload, timeout=10)

            if response.status_code == 200:
                self._add_request_to_history()
                result = response.json()

                # Parser résultat HuggingFace
                if isinstance(result, list) and len(result) > 0:
                    sentiment_data = result[0]

                    # Mapper vers notre format
                    label = sentiment_data.get("label", "NEUTRAL")
                    score = sentiment_data.get("score", 0.5)

                    if "POSITIVE" in label.upper():
                        sentiment = "bullish"
                        confidence = score * 100
                    elif "NEGATIVE" in label.upper():
                        sentiment = "bearish"
                        confidence = score * 100
                    else:
                        sentiment = "neutral"
                        confidence = 60

                    return {
                        "sentiment": sentiment,
                        "confidence": round(confidence, 1),
                        "score": round(
                            (
                                50 + (score * 50)
                                if sentiment == "bullish"
                                else 50 - (score * 50)
                            ),
                            1,
                        ),
                        "source": "HuggingFace (Free)",
                        "model": "twitter-roberta-base-sentiment",
                        "raw_result": sentiment_data,
                    }

            logger.warning(f"HuggingFace API erreur: {response.status_code}")
            return self._local_fallback_analysis(text, task)

        except Exception as e:
            logger.error(f"Erreur HuggingFace: {e}")
            return self._local_fallback_analysis(text, task)

    def analyze_with_free_llm(self, prompt: str, context: str = "") -> Dict:
        """Analyser avec LLM gratuit (si disponible)"""
        # Pour l'instant, fallback vers analyse locale
        # TODO: Intégrer Ollama local si installé
        logger.info("LLM gratuit non configuré - utilisation IA locale")
        return self._local_llm_simulation(prompt, context)

    def _local_llm_simulation(self, prompt: str, context: str) -> Dict:
        """Simulation LLM locale avec règles business"""
        try:
            # Analyser le prompt pour détecter l'intention
            prompt_lower = prompt.lower()

            # Simulation analyse marché
            if "market" in prompt_lower or "analysis" in prompt_lower:
                insights = [
                    "Analyse basée sur indicateurs techniques et sentiment news",
                    "Signaux multiples détectés - confluence recommandée",
                    "Contexte macro à surveiller pour confirmations",
                    "Gestion risque prioritaire dans environnement volatile",
                ]

                recommendation = "Position prudente recommandée avec stop-loss ajustés"

            # Simulation sentiment crypto
            elif "crypto" in prompt_lower or "bitcoin" in prompt_lower:
                insights = [
                    "Momentum crypto dépendant corrélations macro",
                    "Niveaux techniques clés à surveiller",
                    "Volume et sentiment réseaux sociaux importants",
                    "Événements réglementaires comme catalyseurs",
                ]

                recommendation = "Approche graduelle avec DCA sur supports"

            else:
                insights = [
                    "Analyse multi-factorielle recommandée",
                    "Confluence signaux techniques prioritaire",
                    "Sentiment marché à intégrer dans décisions",
                ]

                recommendation = "Position neutre jusqu'à clarification tendance"

            return {
                "analysis": insights,
                "recommendation": recommendation,
                "confidence": 75,
                "source": "Local LLM Simulation (Free)",
                "timestamp": datetime.now().isoformat(),
                "note": "Analyse basée sur règles business prédéfinies",
            }

        except Exception as e:
            logger.error(f"Erreur simulation LLM: {e}")
            return {
                "analysis": ["Erreur analyse - position neutre recommandée"],
                "recommendation": "HOLD - Attendre clarification marché",
                "confidence": 50,
            }

    def _local_fallback_analysis(self, text: str, task: str) -> Dict:
        """Fallback vers analyse locale simple"""
        from .local_ai_engine import local_ai_engine

        if task == "sentiment-analysis":
            # Simuler format news pour analyse locale
            fake_news = [{"title": text, "description": ""}]
            return local_ai_engine.analyze_market_sentiment(fake_news)

        return {"sentiment": "neutral", "confidence": 50, "source": "Local Fallback"}

    def get_daily_usage(self) -> Dict:
        """Obtenir utilisation quotidienne"""
        now = datetime.now()
        today_requests = [
            req_time
            for req_time in self.request_history
            if now.date() == req_time.date()
        ]

        return {
            "requests_today": len(today_requests),
            "daily_limit": self.daily_limit,
            "remaining": max(0, self.daily_limit - len(today_requests)),
            "percentage_used": round((len(today_requests) / self.daily_limit) * 100, 1),
        }

    def get_available_services(self) -> Dict:
        """Services IA disponibles"""
        return {
            "huggingface": {
                "available": self.huggingface_available,
                "cost": "FREE",
                "limits": "Inference API - rate limited",
                "models": ["sentiment-analysis", "text-classification"],
            },
            "local_fallback": {
                "available": self.local_fallback,
                "cost": "FREE",
                "limits": "Unlimited",
                "capabilities": ["sentiment", "technical-analysis", "insights"],
            },
            "openai_free": {
                "available": self.openai_free_available,
                "cost": "FREE (trial)",
                "limits": "Requires API key + limited credits",
                "note": "Non configuré actuellement",
            },
            "gemini_free": {
                "available": self.gemini_available,
                "cost": "FREE (quota)",
                "limits": "Requires API key + quotas",
                "note": "Non configuré actuellement",
            },
        }

    def comprehensive_analysis(
        self, symbol: str, market_data: Dict, news_data: List[Dict]
    ) -> Dict:
        """Analyse complète combinant tous les services gratuits"""
        try:
            # Analyse sentiment via HuggingFace si possible
            news_text = " ".join(
                [
                    f"{article.get('title', '')} {article.get('description', '')}"
                    for article in news_data[:3]  # Limiter pour éviter rate limit
                ]
            )

            if news_text.strip():
                sentiment_analysis = self.analyze_with_huggingface(news_text)
            else:
                # Fallback local
                from .local_ai_engine import local_ai_engine

                sentiment_analysis = local_ai_engine.analyze_market_sentiment(news_data)

            # Analyse technique locale (toujours gratuite)
            from .local_ai_engine import local_ai_engine

            technical_analysis = local_ai_engine.analyze_technical_pattern(
                market_data.get("price_data", {}), market_data.get("indicators", {})
            )

            # Insight combiné
            trading_insight = local_ai_engine.generate_trading_insight(
                symbol, {"technical_analysis": technical_analysis}, sentiment_analysis
            )

            # Usage stats
            usage_stats = self.get_daily_usage()

            return {
                "symbol": symbol,
                "sentiment_analysis": sentiment_analysis,
                "technical_analysis": technical_analysis,
                "trading_insight": trading_insight,
                "usage_stats": usage_stats,
                "services_used": {
                    "sentiment": sentiment_analysis.get("source", "Unknown"),
                    "technical": "Local AI Engine",
                    "insights": "Local AI Engine",
                },
                "total_cost": "FREE",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Erreur analyse complète: {e}")
            return {
                "symbol": symbol,
                "error": str(e),
                "fallback": "Local analysis only",
                "total_cost": "FREE",
            }


# Instance globale
free_ai_engine = FreeAIEngine()
