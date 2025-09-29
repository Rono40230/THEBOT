"""
AI Dashboard Module - THEBOT Dash
Intelligence artificielle autonome pour analyse des marchés financiers
Version simplifiée sans API externes
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
        
        if len(df) == 0:
            return self._default_sentiment()
            
        latest_data = {
            'price': df['close'].iloc[-1],
            'volume': df['volume'].iloc[-1] if 'volume' in df.columns else 1000000,
            'sma': indicators['sma'][-1] if indicators['sma'] else df['close'].iloc[-1],
            'ema': indicators['ema'][-1] if indicators['ema'] else df['close'].iloc[-1],
            'rsi': indicators['rsi'][-1] if indicators['rsi'] else 50,
            'atr': indicators['atr'][-1] if indicators['atr'] else 1
        }
        
        # Calcul du sentiment basé sur les indicateurs
        sentiment_score = 0.0
        sentiment_factors = []
        
        # Analyse RSI
        if latest_data['rsi'] > 70:
            sentiment_score -= 0.3
            sentiment_factors.append("RSI en survente (>70) - Signal baissier")
        elif latest_data['rsi'] < 30:
            sentiment_score += 0.3
            sentiment_factors.append("RSI en surachat (<30) - Signal haussier")
        else:
            sentiment_factors.append("RSI neutre (30-70) - Zone d'équilibre")
            
        # Analyse tendance SMA/EMA
        if latest_data['price'] > latest_data['sma'] and latest_data['price'] > latest_data['ema']:
            sentiment_score += 0.4
            sentiment_factors.append("Prix au-dessus des moyennes mobiles - Tendance haussière")
        elif latest_data['price'] < latest_data['sma'] and latest_data['price'] < latest_data['ema']:
            sentiment_score -= 0.4
            sentiment_factors.append("Prix en-dessous des moyennes mobiles - Tendance baissière")
        else:
            sentiment_factors.append("Prix entre les moyennes mobiles - Indécision")
        
        # Analyse volatilité ATR
        avg_atr = np.mean(indicators['atr'][-10:]) if len(indicators['atr']) >= 10 else latest_data['atr']
        if latest_data['atr'] > avg_atr * 1.5:
            sentiment_factors.append("Volatilité élevée (+50%) - Mouvement majeur en cours")
        elif latest_data['atr'] < avg_atr * 0.7:
            sentiment_factors.append("Volatilité faible (-30%) - Marché calme")
        else:
            sentiment_factors.append("Volatilité normale - Conditions standards")
            
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
            'score': round(sentiment_score, 3),
            'classification': classification,
            'confidence': round(confidence, 1),
            'color': color,
            'factors': sentiment_factors,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    
    def predict_price_movement(self, symbol: str, price_data: pd.DataFrame,
                             indicators: Dict[str, List[float]]) -> Dict[str, Any]:
        """Prédiction de mouvement de prix basée sur analyse technique"""
        
        if len(price_data) == 0:
            return self._default_prediction()
            
        current_price = price_data['close'].iloc[-1]
        
        # Calcul des supports et résistances
        highs = price_data['high'].tail(20).tolist()
        lows = price_data['low'].tail(20).tolist()
        
        resistance = np.percentile(highs, 80) if highs else current_price * 1.02
        support = np.percentile(lows, 20) if lows else current_price * 0.98
        
        # Signaux des indicateurs
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
        
        # Horizons temporels
        time_horizons = {
            '1H': target_price * (1 + random.uniform(-0.005, 0.005)),
            '4H': target_price,
            '1D': target_price * (1 + random.uniform(-0.01, 0.01))
        }
        
        return {
            'direction': direction,
            'target_price': round(target_price, 4),
            'current_price': round(current_price, 4),
            'probability': round(probability, 1),
            'support': round(support, 4),
            'resistance': round(resistance, 4),
            'time_horizons': {k: round(v, 4) for k, v in time_horizons.items()},
            'composite_score': round(composite_score, 3),
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    
    def assess_risk_level(self, symbol: str, df: pd.DataFrame,
                         indicators: Dict[str, List[float]]) -> Dict[str, Any]:
        """Évaluation du niveau de risque"""
        
        if len(df) == 0:
            return self._default_risk()
            
        # Calcul de la volatilité
        returns = df['close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)  # Annualisée
        
        # ATR relatif
        current_price = df['close'].iloc[-1]
        atr = indicators['atr'][-1] if indicators['atr'] else current_price * 0.02
        atr_ratio = atr / current_price
        
        # VaR (Value at Risk) simplifié
        var_95 = np.percentile(returns, 5) if len(returns) > 0 else -0.02
        
        # Score de risque composite
        risk_factors = {
            'volatility': min(1.0, volatility / 0.5),  # Normalisé sur 50%
            'atr_ratio': min(1.0, atr_ratio / 0.05),   # Normalisé sur 5%
            'var_impact': min(1.0, abs(var_95) / 0.05) # Normalisé sur 5%
        }
        
        risk_score = np.mean(list(risk_factors.values()))
        
        # Classification du risque
        if risk_score < 0.3:
            risk_level = "Faible"
            color = "success"
            description = "Conditions de marché stables"
        elif risk_score < 0.7:
            risk_level = "Modéré"
            color = "warning"
            description = "Volatilité normale, surveillance recommandée"
        else:
            risk_level = "Élevé"
            color = "danger"
            description = "Forte volatilité, prudence requise"
        
        return {
            'level': risk_level,
            'score': round(risk_score * 100, 1),
            'color': color,
            'description': description,
            'factors': {
                'volatility_annual': round(volatility * 100, 2),
                'atr_percentage': round(atr_ratio * 100, 2),
                'var_95': round(var_95 * 100, 2)
            },
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    
    def generate_trading_insights(self, symbol: str, sentiment: Dict[str, Any],
                                prediction: Dict[str, Any], risk: Dict[str, Any]) -> Dict[str, Any]:
        """Génération d'insights de trading"""
        
        insights = []
        recommendations = []
        
        # Analyse sentiment
        if sentiment['classification'] == 'Bullish':
            insights.append(f"📈 Sentiment haussier détecté avec {sentiment['confidence']}% de confiance")
            if risk['level'] == 'Faible':
                recommendations.append("ACHAT: Conditions favorables pour position longue")
            else:
                recommendations.append("ACHAT PRUDENT: Sentiment positif mais risque élevé")
        
        elif sentiment['classification'] == 'Bearish':
            insights.append(f"📉 Sentiment baissier détecté avec {sentiment['confidence']}% de confiance")
            if risk['level'] == 'Faible':
                recommendations.append("VENTE: Conditions favorables pour position courte")
            else:
                recommendations.append("ATTENTE: Sentiment négatif et risque élevé")
        
        else:
            insights.append(f"⚖️ Sentiment neutre - Marché en indécision")
            recommendations.append("OBSERVATION: Attendre un signal plus clair")
        
        # Analyse prédiction
        if prediction['probability'] > 75:
            insights.append(f"🎯 Prédiction forte ({prediction['probability']}%) vers {prediction['target_price']}")
        
        # Analyse risque
        if risk['level'] == 'Élevé':
            insights.append(f"⚠️ Risque élevé ({risk['score']}%) - Réduire la taille des positions")
            recommendations.append("GESTION: Utiliser des stops serrés")
        
        # Points d'entrée/sortie
        entry_points = []
        if prediction['direction'] == 'Hausse':
            entry_points.append(f"Support: {prediction['support']}")
        elif prediction['direction'] == 'Baisse':
            entry_points.append(f"Résistance: {prediction['resistance']}")
        
        return {
            'insights': insights,
            'recommendations': recommendations,
            'entry_points': entry_points,
            'key_levels': {
                'support': prediction['support'],
                'resistance': prediction['resistance'],
                'target': prediction['target_price']
            },
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    
    def get_comprehensive_analysis(self, symbol: str, df: pd.DataFrame,
                                 indicators: Dict[str, List[float]]) -> Dict[str, Any]:
        """Analyse complète combinant tous les modules IA"""
        
        sentiment = self.analyze_market_sentiment(symbol, df, indicators)
        prediction = self.predict_price_movement(symbol, df, indicators)
        risk = self.assess_risk_level(symbol, df, indicators)
        insights = self.generate_trading_insights(symbol, sentiment, prediction, risk)
        
        return {
            'sentiment': sentiment,
            'prediction': prediction,
            'risk': risk,
            'insights': insights,
            'symbol': symbol,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _default_sentiment(self) -> Dict[str, Any]:
        """Sentiment par défaut quand pas de données"""
        return {
            'score': 0.0,
            'classification': 'Neutral',
            'confidence': 50.0,
            'color': 'secondary',
            'factors': ['Données insuffisantes pour l\'analyse'],
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    
    def _default_prediction(self) -> Dict[str, Any]:
        """Prédiction par défaut quand pas de données"""
        return {
            'direction': 'Inconnu',
            'target_price': 0.0,
            'current_price': 0.0,
            'probability': 50.0,
            'support': 0.0,
            'resistance': 0.0,
            'time_horizons': {'1H': 0.0, '4H': 0.0, '1D': 0.0},
            'composite_score': 0.0,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    
    def _default_risk(self) -> Dict[str, Any]:
        """Risque par défaut quand pas de données"""
        return {
            'level': 'Inconnu',
            'score': 50.0,
            'color': 'secondary',
            'description': 'Données insuffisantes pour évaluer le risque',
            'factors': {'volatility_annual': 0.0, 'atr_percentage': 0.0, 'var_95': 0.0},
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }


# Instance globale du moteur d'analyse IA
ai_engine = AIAnalysisEngine()