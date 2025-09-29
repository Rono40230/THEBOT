"""
AI Dashboard Module - THEBOT Dash
Intelligence artificielle pour analyse contextuelle des marchés financiers
Version autonome sans API externes
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import math
import random
from ..core.config import dash_config


class AIAnalysisEngine:
    """Moteur d'analyse IA autonome pour THEBOT"""
    
    def __init__(self):
        """Initialisation du moteur d'analyse IA"""
        self.analysis_history = {}
        self.market_sentiment_cache = {}
        self.prediction_models = self._initialize_models()
    
    def _initialize_models(self) -> Dict[str, Any]:
        """Initialisation des modèles de prédiction intégrés"""
        return {
            'trend_model': {'weights': np.random.random(10), 'bias': 0.1},
            'volatility_model': {'alpha': 0.2, 'beta': 0.8},
            'momentum_model': {'lookback': 14, 'threshold': 0.7},
            'risk_model': {'var_confidence': 0.95, 'stress_factor': 1.5}
        }
    
    def analyze_market_sentiment(self, symbol: str, df: pd.DataFrame, 
                               indicators: Dict[str, List[float]]) -> Dict[str, Any]:
        """Analyse du sentiment de marché basée sur les indicateurs techniques"""
        
        latest_data = {
            'price': df['close'].iloc[-1] if len(df) > 0 else 100,
            'volume': df['volume'].iloc[-1] if len(df) > 0 else 1000000,
            'sma': indicators['sma'][-1] if indicators['sma'] else 0,
            'ema': indicators['ema'][-1] if indicators['ema'] else 0,
            'rsi': indicators['rsi'][-1] if indicators['rsi'] else 50,
            'atr': indicators['atr'][-1] if indicators['atr'] else 1
        }
        
        # Calcul du sentiment basé sur les indicateurs
        sentiment_score = 0.0
        sentiment_factors = []
        
        # Analyse RSI
        if latest_data['rsi'] > 70:
            sentiment_score -= 0.3
            sentiment_factors.append("RSI en survente - Signal baissier")
        elif latest_data['rsi'] < 30:
            sentiment_score += 0.3
            sentiment_factors.append("RSI en surachat - Signal haussier")
        else:
            sentiment_factors.append("RSI neutre - Zone d'équilibre")
            
        # Analyse tendance SMA/EMA
        if latest_data['price'] > latest_data['sma'] and latest_data['price'] > latest_data['ema']:
            sentiment_score += 0.4
            sentiment_factors.append("Prix au-dessus des moyennes mobiles - Tendance haussière")
        elif latest_data['price'] < latest_data['sma'] and latest_data['price'] < latest_data['ema']:
            sentiment_score -= 0.4
            sentiment_factors.append("Prix en-dessous des moyennes mobiles - Tendance baissière")
        
        # Analyse volatilité ATR
        avg_atr = np.mean(indicators['atr'][-10:]) if len(indicators['atr']) >= 10 else latest_data['atr']
        if latest_data['atr'] > avg_atr * 1.5:
            sentiment_factors.append("Volatilité élevée - Mouvement majeur en cours")
        elif latest_data['atr'] < avg_atr * 0.7:
            sentiment_factors.append("Volatilité faible - Marché calme")
            
        # Normalisation du score
        sentiment_score = max(-1.0, min(1.0, sentiment_score))
        
        # Classification
        if sentiment_score >= 0.3:
            classification = "Bullish"
            color = "success"
        elif sentiment_score <= -0.3:
            classification = "Bearish"
            color = "danger"
        else:
            classification = "Neutral"
            color = "warning"
            
        confidence = min(95, max(50, abs(sentiment_score) * 100 + random.randint(10, 20)))
        
        return {
            'score': sentiment_score,
            'classification': classification,
            'confidence': confidence,
            'color': color,
            'factors': sentiment_factors,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    
    def predict_price_movement(self, symbol: str, price_data: pd.DataFrame,
                             indicators: Dict[str, List[float]]) -> Dict[str, Any]:
    def predict_price_movement(self, symbol: str, price_data: pd.DataFrame,
                             indicators: Dict[str, List[float]]) -> Dict[str, Any]:
        """Prédiction de mouvement de prix basée sur analyse technique"""
        
        current_price = price_data['close'].iloc[-1] if len(price_data) > 0 else 100
        
        # Calcul des supports et résistances
        highs = price_data['high'].tail(20).tolist()
        lows = price_data['low'].tail(20).tolist()
        
        resistance = np.percentile(highs, 80) if highs else current_price * 1.02
        support = np.percentile(lows, 20) if lows else current_price * 0.98
        
        # Prédiction basée sur les indicateurs
        sma_signal = 0
        ema_signal = 0
        rsi_signal = 0
        
        if indicators['sma']:
            sma_signal = 1 if current_price > indicators['sma'][-1] else -1
            
        if indicators['ema']:
            ema_signal = 1 if current_price > indicators['ema'][-1] else -1
            
        if indicators['rsi']:
            rsi_val = indicators['rsi'][-1]
            if rsi_val < 30:
                rsi_signal = 1  # Oversold - buy signal
            elif rsi_val > 70:
                rsi_signal = -1  # Overbought - sell signal
        
        # Score composite
        composite_score = (sma_signal + ema_signal + rsi_signal) / 3
        
        # Prédiction de prix
        volatility = indicators['atr'][-1] if indicators['atr'] else current_price * 0.02
        
        if composite_score > 0.3:
            direction = "Hausse"
            target_price = current_price + (volatility * random.uniform(1.5, 2.5))
            probability = min(85, 60 + abs(composite_score) * 20)
        elif composite_score < -0.3:
            direction = "Baisse"
            target_price = current_price - (volatility * random.uniform(1.5, 2.5))
            probability = min(85, 60 + abs(composite_score) * 20)
        else:
            direction = "Consolidation"
            target_price = current_price * (1 + random.uniform(-0.01, 0.01))
            probability = random.randint(55, 70)
        
        # Horizon temporel
        time_horizons = {
            '1H': target_price * (1 + random.uniform(-0.005, 0.005)),
            '4H': target_price,
            '1D': target_price * (1 + random.uniform(-0.01, 0.01))
        }
        
        return {
            'direction': direction,
            'target_price': round(target_price, 4),
            'current_price': round(current_price, 4),
            'probability': probability,
            'support': round(support, 4),
            'resistance': round(resistance, 4),
            'time_horizons': {k: round(v, 4) for k, v in time_horizons.items()},
            'composite_score': round(composite_score, 3),
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        
        # Tendance basée sur moyennes mobiles
        trend_strength = 0
        if sma_values and ema_values:
            sma_current = sma_values[-1]
            ema_current = ema_values[-1]
            
            if current_price > sma_current and current_price > ema_current:
                trend_strength = 1  # Haussier
            elif current_price < sma_current and current_price < ema_current:
                trend_strength = -1  # Baissier
            else:
                trend_strength = 0  # Neutre
        
        # Calcul de la prédiction
        if atr_values:
            atr_current = atr_values[-1]
            volatility_factor = atr_current / current_price
        else:
            volatility_factor = 0.02  # 2% par défaut
            
        # Prédiction basée sur la tendance et volatilité
        if trend_strength > 0:
            prediction_pct = np.random.uniform(0.5, 2.5) * (1 + volatility_factor * 10)
            direction = "Bullish"
        elif trend_strength < 0:
            prediction_pct = -np.random.uniform(0.5, 2.5) * (1 + volatility_factor * 10)
            direction = "Bearish"
        else:
            prediction_pct = np.random.uniform(-1.0, 1.0)
            direction = "Sideways"
            
        target_price = current_price * (1 + prediction_pct / 100)
        
        return {
            'direction': direction,
            'target_price': round(target_price, 4),
            'change_percent': round(prediction_pct, 2),
            'timeframe': '24h',
            'confidence': round(65 + abs(trend_strength) * 15, 1),
            'volatility': round(volatility_factor * 100, 2)
        }
        
    def assess_risk_level(self, symbol: str, price_data: pd.DataFrame,
                         indicators: Dict[str, List[float]]) -> Dict[str, Any]:
        """Évaluation du niveau de risque avec IA"""
        
        # Calcul de volatilité récente
        recent_prices = price_data['close'].tail(20)
        volatility = recent_prices.std() / recent_prices.mean()
        
        # ATR pour mesure de volatilité
        atr_values = indicators.get('atr', [])
        if atr_values:
            atr_current = atr_values[-1]
            current_price = price_data['close'].iloc[-1]
            atr_percentage = (atr_current / current_price) * 100
        else:
            atr_percentage = volatility * 100
            
        # Classification du risque
        if atr_percentage > 3.0:
            risk_level = "High"
            risk_score = min(95, 60 + atr_percentage * 10)
            description = "Forte volatilité détectée. Trading risqué."
        elif atr_percentage > 1.5:
            risk_level = "Medium"
            risk_score = 40 + atr_percentage * 10
            description = "Volatilité modérée. Prudence recommandée."
        else:
            risk_level = "Low"
            risk_score = max(15, 20 + atr_percentage * 10)
            description = "Faible volatilité. Conditions favorables."
            
        return {
            'risk_level': risk_level,
            'risk_score': round(risk_score, 1),
            'description': description,
            'volatility_percent': round(atr_percentage, 2),
            'recommendation': self._get_risk_recommendation(risk_level)
        }
        
    def _get_risk_recommendation(self, risk_level: str) -> str:
        """Recommandations basées sur le niveau de risque"""
        recommendations = {
            'Low': "Position sizing normal. Conditions stables pour trading.",
            'Medium': "Réduire la taille des positions. Surveiller de près.",
            'High': "Position sizing minimal. Éviter le trading ou hedger."
        }
        return recommendations.get(risk_level, "Analyser les conditions avant trading.")
        
    def generate_trading_insights(self, symbol: str, price_data: pd.DataFrame,
                                indicators: Dict[str, List[float]]) -> List[str]:
        """Génération d'insights de trading intelligents"""
        
        insights = []
        
        # Analyse RSI
        rsi_values = indicators.get('rsi', [])
        if rsi_values:
            rsi_current = rsi_values[-1]
            if rsi_current > 75:
                insights.append(f"⚠️ RSI extrême à {rsi_current:.1f} - Signal de vente fort")
            elif rsi_current < 25:
                insights.append(f"🚀 RSI extrême à {rsi_current:.1f} - Opportunité d'achat")
            elif rsi_current > 65:
                insights.append(f"📈 RSI élevé à {rsi_current:.1f} - Momentum haussier mais prudence")
            elif rsi_current < 35:
                insights.append(f"📉 RSI faible à {rsi_current:.1f} - Pression vendeuse mais rebond possible")
        
        # Analyse moyennes mobiles
        sma_values = indicators.get('sma', [])
        ema_values = indicators.get('ema', [])
        current_price = price_data['close'].iloc[-1]
        
        if sma_values and ema_values:
            sma_current = sma_values[-1]
            ema_current = ema_values[-1]
            
            if current_price > sma_current and current_price > ema_current:
                insights.append("🟢 Prix au-dessus SMA et EMA - Tendance haussière confirmée")
            elif current_price < sma_current and current_price < ema_current:
                insights.append("🔴 Prix sous SMA et EMA - Tendance baissière confirmée")
            else:
                insights.append("🟡 Prix entre moyennes mobiles - Zone d'indécision")
                
        # Analyse ATR pour volatilité
        atr_values = indicators.get('atr', [])
        if atr_values:
            atr_current = atr_values[-1]
            atr_percentage = (atr_current / current_price) * 100
            if atr_percentage > 2.5:
                insights.append(f"⚡ ATR élevé ({atr_percentage:.1f}%) - Forte volatilité attendue")
            elif atr_percentage < 1.0:
                insights.append(f"😴 ATR faible ({atr_percentage:.1f}%) - Marché peu volatil")
                
        # Analyse de volume (si disponible)
        if 'volume' in price_data.columns:
            recent_volume = price_data['volume'].tail(5).mean()
            avg_volume = price_data['volume'].mean()
            
            if recent_volume > avg_volume * 1.5:
                insights.append("📊 Volume anormalement élevé - Mouvement significatif possible")
            elif recent_volume < avg_volume * 0.5:
                insights.append("📊 Volume faible - Manque de conviction du marché")
        
        # Si pas d'insights spéciaux, ajouter insight générique
        if not insights:
            insights.append("📊 Conditions de marché normales - Surveiller les signaux clés")
            
        return insights[:3]  # Limiter à 3 insights max
    
    def get_comprehensive_analysis(self, symbol: str, price_data: pd.DataFrame,
                                 indicators: Dict[str, List[float]]) -> Dict[str, Any]:
        """Analyse complète combinant tous les modules IA"""
        
        return {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'sentiment': self.analyze_market_sentiment(symbol, price_data, indicators),
            'prediction': self.predict_price_movement(symbol, price_data, indicators),
            'risk_assessment': self.assess_risk_level(symbol, price_data, indicators),
            'insights': self.generate_trading_insights(symbol, price_data, indicators),
            'ai_status': 'simulation_mode'  # Production: 'openai_active' ou 'claude_active'
        }


# Instance globale
ai_engine = AIAnalysisEngine()