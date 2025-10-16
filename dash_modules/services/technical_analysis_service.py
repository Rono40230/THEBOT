from src.thebot.core.logger import logger
"""
Technical Analysis Service - Logique métier pour les analyses techniques
Calcule les indicateurs techniques et analyses de marché
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class TechnicalAnalysisService:
    """
    Service de logique métier pour les analyses techniques
    Calcule les indicateurs techniques et fournit des analyses de marché
    """

    def __init__(self):
        pass

    def calculate_moving_averages(self, prices: List[float], periods: List[int] = None) -> Dict[str, List[float]]:
        """
        Calcule les moyennes mobiles

        Args:
            prices: Liste des prix
            periods: Périodes pour les moyennes mobiles (défaut: [20, 50, 200])

        Returns:
            Dictionnaire des moyennes mobiles par période
        """
        if periods is None:
            periods = [20, 50, 200]

        try:
            result = {}
            prices_array = np.array(prices)

            for period in periods:
                if len(prices) >= period:
                    ma = np.convolve(prices_array, np.ones(period), 'valid') / period
                    result[f"SMA_{period}"] = ma.tolist()
                else:
                    result[f"SMA_{period}"] = []

            return result

        except Exception as e:
            logger.error(f"Erreur calcul moyennes mobiles: {e}")
            return {}

    def calculate_rsi(self, prices: List[float], period: int = 14) -> List[float]:
        """
        Calcule l'indice de force relative (RSI)

        Args:
            prices: Liste des prix
            period: Période du RSI (défaut: 14)

        Returns:
            Liste des valeurs RSI
        """
        try:
            if len(prices) < period + 1:
                return []

            prices_array = np.array(prices)
            deltas = np.diff(prices_array)

            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)

            avg_gains = np.convolve(gains, np.ones(period), 'valid') / period
            avg_losses = np.convolve(losses, np.ones(period), 'valid') / period

            rs = avg_gains / avg_losses
            rsi = 100 - (100 / (1 + rs))

            return rsi.tolist()

        except Exception as e:
            logger.error(f"Erreur calcul RSI: {e}")
            return []

    def analyze_trend(self, prices: List[float]) -> Dict[str, Any]:
        """
        Analyse la tendance générale

        Args:
            prices: Liste des prix

        Returns:
            Analyse de tendance
        """
        try:
            if len(prices) < 20:
                return {"trend": "insufficient_data", "strength": 0, "description": "Données insuffisantes"}

            # Calculer les moyennes mobiles
            sma_20 = self.calculate_moving_averages(prices, [20])["SMA_20"]
            sma_50 = self.calculate_moving_averages(prices, [50])["SMA_50"]

            if not sma_20 or not sma_50:
                return {"trend": "insufficient_data", "strength": 0, "description": "Données insuffisantes"}

            # Analyser la tendance
            current_price = prices[-1]
            sma_20_current = sma_20[-1] if sma_20 else current_price
            sma_50_current = sma_50[-1] if sma_50 else current_price

            # Logique de tendance
            if current_price > sma_20_current and sma_20_current > sma_50_current:
                trend = "bullish"
                strength = min(100, ((current_price - sma_50_current) / sma_50_current) * 100)
                description = "Tendance haussière forte"
            elif current_price > sma_20_current:
                trend = "bullish"
                strength = min(100, ((current_price - sma_20_current) / sma_20_current) * 100)
                description = "Tendance haussière modérée"
            elif current_price < sma_20_current and sma_20_current < sma_50_current:
                trend = "bearish"
                strength = min(100, ((sma_50_current - current_price) / sma_50_current) * 100)
                description = "Tendance baissière forte"
            elif current_price < sma_20_current:
                trend = "bearish"
                strength = min(100, ((sma_20_current - current_price) / sma_20_current) * 100)
                description = "Tendance baissière modérée"
            else:
                trend = "sideways"
                strength = 0
                description = "Tendance latérale"

            return {
                "trend": trend,
                "strength": round(strength, 2),
                "description": description,
                "current_price": current_price,
                "sma_20": sma_20_current,
                "sma_50": sma_50_current
            }

        except Exception as e:
            logger.error(f"Erreur analyse tendance: {e}")
            return {"trend": "error", "strength": 0, "description": "Erreur d'analyse"}

    def get_technical_summary(self, symbol: str, prices: List[float]) -> Dict[str, Any]:
        """
        Fournit un résumé technique complet

        Args:
            symbol: Symbole de l'actif
            prices: Liste des prix

        Returns:
            Résumé technique complet
        """
        try:
            if len(prices) < 50:
                return {"error": "Données insuffisantes pour l'analyse technique"}

            # Calculer tous les indicateurs
            moving_averages = self.calculate_moving_averages(prices)
            rsi = self.calculate_rsi(prices)
            trend = self.analyze_trend(prices)

            return {
                "symbol": symbol,
                "trend_analysis": trend,
                "indicators": {
                    "moving_averages": moving_averages,
                    "rsi": rsi[-1] if rsi else None,
                },
                "current_price": prices[-1],
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Erreur résumé technique pour {symbol}: {e}")
            return {"error": f"Erreur d'analyse technique: {str(e)}"}


# Instance globale du service
technical_analysis_service = TechnicalAnalysisService()
