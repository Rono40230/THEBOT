"""
IA Hybride Smart - Combine gratuit + payant optimisé
Phase 6 - Intelligence Artificielle Optimisée Budget
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SmartAIEngine:
    """
    Moteur IA Hybride Smart :
    1. IA LOCALE (gratuite) pour 90% des analyses
    2. IA PAYANTE (OpenAI/Claude) pour cas complexes uniquement
    3. Optimisation coûts intelligente
    4. Fallback automatique si budget épuisé
    """

    def __init__(self):
        # Configuration budget
        self.monthly_budget_euro = 10  # Budget conservateur 10€/mois
        self.daily_budget_euro = self.monthly_budget_euro / 30
        self.current_monthly_spend = 0
        self.current_daily_spend = 0

        # Configuration services
        self.openai_available = False  # Nécessite clé API
        self.claude_available = False  # Nécessite clé API
        self.local_ai_always_available = True

        # Stratégie d'usage IA payante (seulement cas critiques)
        self.paid_ai_triggers = {
            "high_volatility": True,  # Volatilité > 5%
            "major_news_event": True,  # News majeures (NFP, FOMC, etc.)
            "unusual_volume": True,  # Volume > 200% moyenne
            "conflicting_signals": True,  # Signaux contradictoires
            "user_request_premium": False,  # Demande explicite utilisateur
        }

        # Historique usage
        self.daily_usage_log = []

        logger.info("🧠 IA Hybride Smart initialisée - Budget: 10€/mois")

    def _should_use_paid_ai(self, context: Dict) -> tuple[bool, str]:
        """Détermine si utiliser IA payante selon contexte"""

        # Vérifier budget quotidien
        if self.current_daily_spend >= self.daily_budget_euro:
            return False, "Budget quotidien épuisé"

        # Vérifier budget mensuel
        if self.current_monthly_spend >= self.monthly_budget_euro:
            return False, "Budget mensuel épuisé"

        # Analyser contexte pour justifier coût
        triggers_activated = []

        # Volatilité élevée
        volatility = context.get("volatility_24h", 0)
        if volatility > 5 and self.paid_ai_triggers["high_volatility"]:
            triggers_activated.append("high_volatility")

        # Événement majeur
        if (
            context.get("major_news_event", False)
            and self.paid_ai_triggers["major_news_event"]
        ):
            triggers_activated.append("major_news_event")

        # Volume inhabituel
        volume_ratio = context.get("volume_vs_average", 1)
        if volume_ratio > 2 and self.paid_ai_triggers["unusual_volume"]:
            triggers_activated.append("unusual_volume")

        # Signaux contradictoires
        if (
            context.get("conflicting_signals", False)
            and self.paid_ai_triggers["conflicting_signals"]
        ):
            triggers_activated.append("conflicting_signals")

        # Décision
        if triggers_activated:
            estimated_cost = self._estimate_request_cost(context)
            if estimated_cost <= (self.daily_budget_euro - self.current_daily_spend):
                return True, f"Triggers: {', '.join(triggers_activated)}"

        return False, "Pas de justification pour IA payante"

    def _estimate_request_cost(self, context: Dict) -> float:
        """Estimer coût requête IA payante"""
        # Estimation conservative basée sur longueur prompt
        prompt_length = len(str(context.get("prompt", "")))
        estimated_tokens = max(100, prompt_length + 200)  # Input + output

        # Prix OpenAI GPT-3.5-turbo (plus économique)
        cost_per_1k_tokens = 0.002  # $0.002/1K tokens
        estimated_cost_usd = (estimated_tokens / 1000) * cost_per_1k_tokens
        estimated_cost_eur = estimated_cost_usd * 0.92  # Conversion approximative

        return round(estimated_cost_eur, 4)

    def _log_ai_usage(self, service: str, cost: float, context: str):
        """Logger utilisation IA"""
        usage_entry = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "cost_eur": cost,
            "context": context,
            "daily_spend_after": round(self.current_daily_spend + cost, 4),
            "monthly_spend_after": round(self.current_monthly_spend + cost, 4),
        }

        self.daily_usage_log.append(usage_entry)
        self.current_daily_spend += cost
        self.current_monthly_spend += cost

        logger.info(
            f"💰 IA usage: {service} - {cost}€ - Total jour: {self.current_daily_spend:.3f}€"
        )

    def analyze_market_comprehensive(
        self,
        symbol: str,
        market_data: Dict,
        news_data: List[Dict],
        context: Dict = None,
    ) -> Dict:
        """Analyse marché complète avec stratégie hybride intelligente"""

        if context is None:
            context = {}

        # Enrichir contexte avec métriques
        enhanced_context = self._enrich_context(symbol, market_data, news_data, context)

        # Décider stratégie IA
        use_paid_ai, decision_reason = self._should_use_paid_ai(enhanced_context)

        # ÉTAPE 1: Analyse locale TOUJOURS (gratuite)
        from .local_ai_engine import local_ai_engine

        local_sentiment = local_ai_engine.analyze_market_sentiment(news_data)
        local_technical = local_ai_engine.analyze_technical_pattern(
            market_data.get("price_data", {}), market_data.get("indicators", {})
        )
        local_insight = local_ai_engine.generate_trading_insight(
            symbol, {"technical_analysis": local_technical}, local_sentiment
        )

        analysis_result = {
            "symbol": symbol,
            "local_analysis": {
                "sentiment": local_sentiment,
                "technical": local_technical,
                "insight": local_insight,
            },
            "enhanced_analysis": None,
            "strategy": "local_only" if not use_paid_ai else "hybrid",
            "decision_reason": decision_reason,
            "cost_breakdown": {"local": 0.0, "paid": 0.0, "total": 0.0},
        }

        # ÉTAPE 2: IA payante SI justifiée
        if use_paid_ai and (self.openai_available or self.claude_available):
            try:
                enhanced_analysis = self._call_paid_ai(enhanced_context, local_insight)

                if enhanced_analysis:
                    cost = self._estimate_request_cost(enhanced_context)
                    self._log_ai_usage("paid_ai", cost, decision_reason)

                    analysis_result["enhanced_analysis"] = enhanced_analysis
                    analysis_result["cost_breakdown"]["paid"] = cost
                    analysis_result["cost_breakdown"]["total"] = cost

                    # Combiner analyses locale + payante
                    analysis_result["combined_insight"] = self._combine_analyses(
                        local_insight, enhanced_analysis
                    )

            except Exception as e:
                logger.error(f"Erreur IA payante, fallback local: {e}")
                analysis_result["enhanced_analysis"] = {
                    "error": str(e),
                    "fallback": "local_only",
                }

        # Finaliser résultat
        analysis_result["timestamp"] = datetime.now().isoformat()
        analysis_result["budget_status"] = self._get_budget_status()

        return analysis_result

    def _enrich_context(
        self, symbol: str, market_data: Dict, news_data: List[Dict], base_context: Dict
    ) -> Dict:
        """Enrichir contexte avec métriques pour décision IA"""

        enriched = base_context.copy()

        # Calculer volatilité
        price_data = market_data.get("price_data", {})
        high_24h = price_data.get("high", 0)
        low_24h = price_data.get("low", 0)
        current = price_data.get("close", 0)

        if current > 0:
            enriched["volatility_24h"] = round(
                ((high_24h - low_24h) / current) * 100, 2
            )

        # Volume ratio
        volume = price_data.get("volume", 0)
        avg_volume = market_data.get("indicators", {}).get("avg_volume", volume)
        if avg_volume > 0:
            enriched["volume_vs_average"] = round(volume / avg_volume, 2)

        # News significance
        enriched["news_count"] = len(news_data)
        enriched["major_news_event"] = any(
            keyword in (article.get("title", "") or "").lower()
            for article in news_data
            for keyword in ["fed", "fomc", "nfp", "cpi", "gdp", "ecb", "bce"]
        )

        # Signaux contradictoires (sentiment vs technique)
        local_sentiment_score = 50  # Par défaut neutre
        technical_score = market_data.get("indicators", {}).get("trend_score", 50)

        enriched["conflicting_signals"] = (
            abs(local_sentiment_score - technical_score) > 30
        )

        enriched["symbol"] = symbol
        enriched["analysis_complexity"] = (
            "high"
            if enriched.get("major_news_event") or enriched.get("volatility_24h", 0) > 3
            else "normal"
        )

        return enriched

    def _call_paid_ai(self, context: Dict, local_insight: Dict) -> Optional[Dict]:
        """Appeler IA payante (simulé pour l'instant)"""
        # TODO: Implémenter vraies APIs OpenAI/Claude quand clés disponibles

        # Simulation IA premium
        enhanced_insights = [
            "Analyse macro-économique suggère correlation forte avec DXY",
            "Patterns institutionnels détectés sur flux ordres",
            "Résistance psychologique majeure à surveiller",
            "Confluence Fibonacci + niveaux volume profile critique",
        ]

        return {
            "enhanced_insights": enhanced_insights,
            "confidence_boost": 15,  # +15% confidence vs local
            "additional_signals": [
                "macro_correlation",
                "institutional_flow",
                "psychological_levels",
            ],
            "premium_recommendation": "Position avec sizing réduit + monitoring accru",
            "source": "Premium AI (Simulated)",
            "note": "Simulation - vraies APIs non configurées",
        }

    def _combine_analyses(self, local: Dict, enhanced: Dict) -> Dict:
        """Combiner analyses locale et premium"""

        # Boost confidence avec IA premium
        original_confidence = local.get("confidence", 50)
        enhanced_confidence = min(
            95, original_confidence + enhanced.get("confidence_boost", 0)
        )

        # Combiner recommandations
        local_rec = local.get("recommendation", "HOLD")
        enhanced_rec = enhanced.get("premium_recommendation", local_rec)

        return {
            "recommendation": local_rec,
            "enhanced_recommendation": enhanced_rec,
            "confidence": enhanced_confidence,
            "original_confidence": original_confidence,
            "combined_insights": local.get("explanation", "")
            + " | "
            + enhanced.get("enhanced_insights", [""])[0],
            "premium_signals": enhanced.get("additional_signals", []),
            "analysis_quality": "premium",
        }

    def _get_budget_status(self) -> Dict:
        """Status budget IA"""
        return {
            "daily_spend": round(self.current_daily_spend, 3),
            "daily_budget": round(self.daily_budget_euro, 3),
            "daily_remaining": round(
                self.daily_budget_euro - self.current_daily_spend, 3
            ),
            "monthly_spend": round(self.current_monthly_spend, 2),
            "monthly_budget": self.monthly_budget_euro,
            "monthly_remaining": round(
                self.monthly_budget_euro - self.current_monthly_spend, 2
            ),
            "usage_level": (
                "conservative"
                if self.current_daily_spend < self.daily_budget_euro * 0.5
                else "active"
            ),
        }

    def get_strategy_summary(self) -> Dict:
        """Résumé stratégie IA hybride"""
        return {
            "name": "Smart Hybrid AI",
            "description": "IA locale gratuite + IA premium pour cas critiques",
            "budget": f"{self.monthly_budget_euro}€/mois",
            "cost_optimization": {
                "local_ai_usage": "90% des analyses (gratuit)",
                "paid_ai_usage": "10% cas critiques seulement",
                "triggers": list(self.paid_ai_triggers.keys()),
                "estimated_savings": "80% vs full premium usage",
            },
            "quality": {
                "baseline": "IA locale performante pour 90% cas",
                "premium": "IA payante pour analyses complexes",
                "fallback": "Local toujours disponible si budget épuisé",
            },
            "current_status": self._get_budget_status(),
        }


# Instance globale
smart_ai_engine = SmartAIEngine()
