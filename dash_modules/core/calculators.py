"""
Calculators Module - THEBOT Dash  
Calculs d'indicateurs techniques optimisés
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any

# Imports THEBOT avec gestion d'erreur
try:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
    
    from thebot.indicators.basic.sma.config import SMAConfig
    from thebot.indicators.basic.sma.calculator import SMACalculator
    from thebot.indicators.basic.ema.config import EMAConfig
    from thebot.indicators.basic.ema.calculator import EMACalculator
    from thebot.indicators.oscillators.rsi.config import RSIConfig
    from thebot.indicators.oscillators.rsi.calculator import RSICalculator
    from thebot.indicators.volatility.atr.config import ATRConfig
    from thebot.indicators.volatility.atr.calculator import ATRCalculator
    
    THEBOT_AVAILABLE = True
    print("✅ Calculateurs THEBOT chargés dans module")
    
except ImportError as e:
    print(f"⚠️ Calculateurs THEBOT indisponibles: {e}")
    THEBOT_AVAILABLE = False


class TechnicalCalculators:
    """Calculateurs d'indicateurs techniques optimisés"""
    
    def __init__(self):
        self.thebot_available = THEBOT_AVAILABLE
        
    def calculate_sma(self, prices: List[float], period: int = 20) -> List[float]:
        """Calculer Simple Moving Average"""
        
        if self.thebot_available and len(prices) >= period:
            try:
                # Tentative avec calculateur THEBOT
                if hasattr(SMACalculator, 'calculate_batch'):
                    return SMACalculator.calculate_batch(prices, period)
                else:
                    print("Info SMA: Utilisation fallback pandas")
            except Exception as e:
                print(f"Info SMA: Fallback pandas - {e}")
        
        # Fallback pandas (très fiable)
        return pd.Series(prices).rolling(window=period).mean().fillna(0).tolist()
    
    def calculate_ema(self, prices: List[float], period: int = 12) -> List[float]:
        """Calculer Exponential Moving Average"""
        
        # Calcul EMA optimisé avec pandas
        return pd.Series(prices).ewm(span=period).mean().fillna(0).tolist()
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> List[float]:
        """Calculer Relative Strength Index"""
        
        if len(prices) < period + 1:
            return [50.0] * len(prices)
        
        # Calcul RSI optimisé avec pandas
        series = pd.Series(prices)
        delta = series.diff()
        
        # Gains et pertes
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Moyennes mobiles des gains et pertes
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # RSI calculation
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.fillna(50).tolist()
    
    def calculate_atr(self, highs: List[float], lows: List[float], 
                     closes: List[float], period: int = 14) -> List[float]:
        """Calculer Average True Range"""
        
        if len(closes) < period + 1:
            return [0.0] * len(closes)
        
        # Conversion en séries pandas
        high_series = pd.Series(highs)
        low_series = pd.Series(lows)
        close_series = pd.Series(closes)
        
        # Previous close
        prev_close = close_series.shift(1)
        
        # True Range components
        tr1 = high_series - low_series  # High - Low
        tr2 = abs(high_series - prev_close)  # High - Previous Close
        tr3 = abs(low_series - prev_close)  # Low - Previous Close
        
        # True Range = max des 3 composants
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # ATR = moyenne mobile du True Range
        atr = true_range.rolling(window=period).mean()
        
        return atr.fillna(0).tolist()
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, 
                                 std_dev: float = 2.0) -> Dict[str, List[float]]:
        """Calculer Bollinger Bands"""
        
        series = pd.Series(prices)
        sma = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'upper': upper_band.fillna(0).tolist(),
            'middle': sma.fillna(0).tolist(), 
            'lower': lower_band.fillna(0).tolist()
        }
    

    
    def calculate_stochastic(self, highs: List[float], lows: List[float], 
                           closes: List[float], k_period: int = 14, 
                           d_period: int = 3) -> Dict[str, List[float]]:
        """Calculer Stochastic Oscillator"""
        
        high_series = pd.Series(highs)
        low_series = pd.Series(lows)
        close_series = pd.Series(closes)
        
        # %K calculation
        lowest_low = low_series.rolling(window=k_period).min()
        highest_high = high_series.rolling(window=k_period).max()
        
        k_percent = 100 * ((close_series - lowest_low) / (highest_high - lowest_low))
        
        # %D calculation (moving average of %K)
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            'k': k_percent.fillna(50).tolist(),
            'd': d_percent.fillna(50).tolist()
        }


# Instance globale
calculator = TechnicalCalculators()