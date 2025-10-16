from .core.logger import logger
"""
Indicator Factory - Point d'entrée unifié pour tous les indicateurs
Centralise l'accès aux calculateurs THEBOT avec cache intelligent
"""

import logging
from typing import Any, Dict, Optional, Type, Union, List
from functools import lru_cache
import pandas as pd
import numpy as np

from .base.indicator import BaseIndicator
from .basic.sma.calculator import SMACalculator
from .basic.ema.calculator import EMACalculator
from .oscillators.rsi.calculator import RSICalculator
from .volatility.atr.calculator import ATRCalculator
from .momentum.macd.calculator import MACDCalculator
from .momentum.breakout.calculator import BreakoutCalculator
from .momentum.squeeze.calculator import SqueezeCalculator
from .trend.supertrend.calculator import SuperTrendCalculator
from .volume.obv.calculator import OBVCalculator
from .volume.volume_profile.calculator import VolumeProfileCalculator
from .structural.fibonacci import FibonacciIndicator
from .structural.pivot_points import PivotPointsIndicator
from .structural.support_resistance import SupportResistanceIndicator

logger = logging.getLogger(__name__)


class IndicatorFactory:
    """
    Factory centralisée pour tous les indicateurs techniques.
    Utilise le cache LRU pour optimiser les performances.
    """

    # Mapping des noms d'indicateurs vers leurs classes
    INDICATOR_CLASSES = {
        # Indicateurs de base
        'sma': SMACalculator,
        'ema': EMACalculator,
        
        # Oscillators
        'rsi': RSICalculator,
        
        # Volatility
        'atr': ATRCalculator,
        
        # Momentum
        'macd': MACDCalculator,
        'breakout': BreakoutCalculator,
        'squeeze': SqueezeCalculator,
        
        # Trend
        'supertrend': SuperTrendCalculator,
        
        # Volume
        'obv': OBVCalculator,
        'volume_profile': VolumeProfileCalculator,
        
        # Structural
        'fibonacci': FibonacciIndicator,
        'pivot_points': PivotPointsIndicator,
        'support_resistance': SupportResistanceIndicator,
    }

    def __init__(self):
        self._cache = {}
        logger.info("IndicatorFactory initialisé avec %d indicateurs", len(self.INDICATOR_CLASSES))

    @lru_cache(maxsize=128)
    def _get_calculator_class(self, name: str) -> Type:
        """Récupère la classe calculateur avec cache"""
        if name not in self.INDICATOR_CLASSES:
            available = list(self.INDICATOR_CLASSES.keys())
            raise ValueError(f"Indicateur '{name}' inconnu. Disponibles: {available}")

        return self.INDICATOR_CLASSES[name]

    def create_calculator(self, name: str, **config_params) -> Any:
        """
        Crée une instance de calculateur pour l'indicateur demandé.

        Args:
            name: Nom de l'indicateur ('sma', 'ema', 'rsi', etc.)
            **config_params: Paramètres de configuration spécifiques

        Returns:
            Instance du calculateur configuré

        Raises:
            ValueError: Si l'indicateur n'existe pas
        """
        calculator_class = self._get_calculator_class(name)

        # Créer la configuration appropriée
        config_class = self._get_config_class(name)
        config = config_class(**config_params)

        calculator = calculator_class(config)
        logger.debug("Calculateur %s créé avec config: %s", name, config_params)

        return calculator

    def _get_config_class(self, name: str) -> Type:
        """Récupère la classe de configuration pour un indicateur"""
        # Import dynamique des configs
        config_module = f"thebot.indicators.{self._get_category(name)}.{name}.config"
        config_class_name = f"{name.upper()}Config"

        try:
            import importlib
            module = importlib.import_module(config_module)
            return getattr(module, config_class_name)
        except (ImportError, AttributeError) as e:
            logger.warning("Config non trouvée pour %s, utilisation config par défaut: %s", name, e)
            # Retourner une config basique
            from .base.config import BaseIndicatorConfig
            return BaseIndicatorConfig

    def _get_category(self, name: str) -> str:
        """Détermine la catégorie d'un indicateur"""
        categories = {
            # Basic
            'sma': 'basic',
            'ema': 'basic',
            
            # Oscillators
            'rsi': 'oscillators',
            
            # Volatility
            'atr': 'volatility',
            
            # Momentum
            'macd': 'momentum',
            'breakout': 'momentum',
            'squeeze': 'momentum',
            
            # Trend
            'supertrend': 'trend',
            
            # Volume
            'obv': 'volume',
            'volume_profile': 'volume',
            
            # Structural
            'fibonacci': 'structural',
            'pivot_points': 'structural',
            'support_resistance': 'structural',
        }
        return categories.get(name, 'basic')

    # === MÉTHODES DE CALCUL HAUT NIVEAU (API COMPATIBLE) ===

    def calculate_sma(self, data: Union[pd.Series, list], period: int = 20) -> Union[pd.Series, list]:
        """Calcule SMA - Compatible avec l'API existante"""
        # Utiliser pandas pour cohérence avec l'API existante
        if isinstance(data, pd.Series):
            result = data.rolling(window=period).mean()
            return result.tolist() if isinstance(data, list) else result
        else:
            series = pd.Series(data)
            result = series.rolling(window=period).mean()
            return result.tolist()

    def calculate_ema(self, data: Union[pd.Series, list], period: int = 21) -> Union[pd.Series, list]:
        """Calcule EMA - Compatible avec l'API existante"""
        # Utiliser pandas pour cohérence avec l'API existante
        if isinstance(data, pd.Series):
            result = data.ewm(span=period, adjust=False).mean()
            return result.tolist() if isinstance(data, list) else result
        else:
            series = pd.Series(data)
            result = series.ewm(span=period, adjust=False).mean()
            return result.tolist()

    def calculate_rsi(self, data: Union[pd.Series, list], period: int = 14) -> Union[pd.Series, list]:
        """Calcule RSI - Compatible avec l'API existante"""
        calculator = self.create_calculator('rsi', period=period)

        # Vérifier si le calculateur a une méthode calculate_batch
        if hasattr(calculator, 'calculate_batch'):
            if isinstance(data, pd.Series):
                return calculator.calculate_batch(data.tolist())
            else:
                return calculator.calculate_batch(data)
        else:
            # Fallback: utiliser add_data_point itérativement
            return self._calculate_rsi_fallback(data, period)

    def calculate_atr(self, data: Union[pd.DataFrame, Dict, tuple], period: int = 14) -> Union[pd.Series, list]:
        """Calcule ATR - Compatible avec l'API existante"""
        # Gérer différents formats d'entrée
        if isinstance(data, tuple) and len(data) == 3:
            # Format (highs, lows, closes)
            highs, lows, closes = data
            high_series = pd.Series(highs)
            low_series = pd.Series(lows)
            close_series = pd.Series(closes)
        elif isinstance(data, pd.DataFrame):
            # Format DataFrame
            high_series = data["high"]
            low_series = data["low"]
            close_series = data["close"]
        elif isinstance(data, dict):
            # Format dict
            high_series = pd.Series(data.get('high', []))
            low_series = pd.Series(data.get('low', []))
            close_series = pd.Series(data.get('close', []))
        else:
            raise ValueError("Format de données ATR non supporté")

        # Calcul ATR
        if len(close_series) < period + 1:
            return [0.0] * len(close_series) if isinstance(data, (tuple, dict)) else pd.Series([0.0] * len(data), index=data.index)

        prev_close = close_series.shift(1)
        tr1 = high_series - low_series
        tr2 = np.abs(high_series - prev_close)
        tr3 = np.abs(low_series - prev_close)
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()

        result = atr.fillna(0)
        return result.tolist() if isinstance(data, (tuple, dict)) else result

    def calculate_macd(self, data: Union[pd.Series, list], fast_period: int = 12,
                       slow_period: int = 26, signal_period: int = 9) -> Dict[str, Union[pd.Series, list]]:
        """Calcule MACD - Compatible avec l'API existante"""
        calculator = self.create_calculator('macd',
                                          fast_period=fast_period,
                                          slow_period=slow_period,
                                          signal_period=signal_period)

        if isinstance(data, pd.Series):
            return calculator.calculate_batch(data.tolist())
        else:
            return calculator.calculate_batch(data)

    # === MÉTHODES UTILITAIRES ===

    def list_available_indicators(self) -> list:
        """Retourne la liste des indicateurs disponibles"""
        return list(self.INDICATOR_CLASSES.keys())

    def clear_cache(self):
        """Vide le cache des calculateurs"""
        self._cache.clear()
        self._get_calculator_class.cache_clear()
        logger.info("Cache IndicatorFactory vidé")

    def _calculate_rsi_fallback(self, data: Union[pd.Series, list], period: int) -> list:
        """Fallback RSI calculation using pandas (compatible avec l'API existante)"""
        if isinstance(data, pd.Series):
            prices = data
        else:
            prices = pd.Series(data)

        # Calcul RSI avec pandas (comme dans technical_indicators.py)
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.fillna(50).tolist()  # Valeur neutre pour les NaN
        except:
            return [50.0] * len(prices)


    # === MÉTHODES DE CALCUL DIRECT ===
    # Ces méthodes utilisent les calculateurs pour un accès simplifié

    def calculate_sma(self, data: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calcule SMA directement"""
        from .basic.sma.calculator import SMACalculator
        prices = data['close'].tolist()
        if hasattr(SMACalculator, 'calculate_batch'):
            result = SMACalculator.calculate_batch(prices, period)
            # Pad with NaN for initial values
            padding = [np.nan] * (period - 1)
            full_result = padding + result
        else:
            # Fallback: calcul manuel
            full_result = []
            for i in range(len(prices)):
                if i < period - 1:
                    full_result.append(np.nan)
                else:
                    window = prices[i-period+1:i+1]
                    full_result.append(sum(window) / period)
        return pd.Series(full_result, index=data.index)

    def calculate_ema(self, data: pd.DataFrame, period: int = 21) -> pd.Series:
        """Calcule EMA directement"""
        from .basic.ema.calculator import EMACalculator
        prices = data['close'].tolist()
        if hasattr(EMACalculator, 'calculate_batch'):
            result = EMACalculator.calculate_batch(prices, period)
            # Pad with NaN for initial values
            padding = [np.nan] * (period - 1)
            full_result = padding + result
        else:
            # Fallback: calcul manuel EMA
            full_result = []
            multiplier = 2 / (period + 1)
            ema = None
            for price in prices:
                if ema is None:
                    ema = price
                else:
                    ema = (price * multiplier) + (ema * (1 - multiplier))
                full_result.append(ema)
        return pd.Series(full_result, index=data.index)

    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calcule RSI directement"""
        from .oscillators.rsi.calculator import RSICalculator
        prices = data['close'].tolist()
        if hasattr(RSICalculator, 'calculate_batch'):
            result = RSICalculator.calculate_batch(prices, period)
            # RSI needs more padding
            padding = [50.0] * (period)  # RSI typically starts with 50
            full_result = padding + result
        else:
            # Fallback: calcul manuel RSI
            full_result = []
            for i in range(len(prices)):
                if i < period:
                    full_result.append(50.0)  # Valeur neutre
                else:
                    gains = []
                    losses = []
                    for j in range(i-period+1, i+1):
                        change = prices[j] - prices[j-1]
                        if change > 0:
                            gains.append(change)
                            losses.append(0)
                        else:
                            gains.append(0)
                            losses.append(abs(change))
                    
                    avg_gain = sum(gains) / period
                    avg_loss = sum(losses) / period
                    
                    if avg_loss == 0:
                        rsi = 100
                    else:
                        rs = avg_gain / avg_loss
                        rsi = 100 - (100 / (1 + rs))
                    full_result.append(rsi)
        return pd.Series(full_result, index=data.index)

    def calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calcule ATR directement"""
        from .volatility.atr.calculator import ATRCalculator
        high = data['high'].tolist()
        low = data['low'].tolist()
        close = data['close'].tolist()
        result = ATRCalculator.calculate_batch(high, low, close, period)
        # Pad with NaN for initial values
        padding = [np.nan] * (period - 1)
        full_result = padding + result
        return pd.Series(full_result, index=data.index)

    def calculate_macd(self, data: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict:
        """Calcule MACD directement"""
        from .momentum.macd.calculator import MACDCalculator
        prices = data['close'].tolist()
        result = MACDCalculator.calculate_batch(prices, fast_period, slow_period, signal_period)
        # Pad with NaN for initial values
        padding_length = max(fast_period, slow_period, signal_period) - 1
        return {
            'macd': pd.Series([np.nan] * padding_length + result['macd'], index=data.index),
            'signal': pd.Series([np.nan] * padding_length + result['signal'], index=data.index),
            'histogram': pd.Series([np.nan] * padding_length + result['histogram'], index=data.index)
        }

    def calculate_supertrend(self, data: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> pd.DataFrame:
        """Calcule SuperTrend directement"""
        # Fallback simple pour l'instant - à implémenter avec calculate_batch quand disponible
        supertrend_values = []
        direction_values = []
        
        for i in range(len(data)):
            if i < period:
                supertrend_values.append(data['close'].iloc[i])
                direction_values.append(0)
            else:
                # Logique SuperTrend simplifiée
                atr_window = data['high'].iloc[i-period:i+1] - data['low'].iloc[i-period:i+1]
                atr = atr_window.mean()
                hl2 = (data['high'].iloc[i] + data['low'].iloc[i]) / 2
                supertrend_values.append(hl2 - atr * multiplier)
                direction_values.append(1)  # Simplifié
        
        return pd.DataFrame({
            'supertrend': supertrend_values,
            'direction': direction_values
        }, index=data.index)

    def calculate_breakout(self, data: pd.DataFrame, period: int = 20, breakout_threshold: float = 2.0) -> pd.Series:
        """Calcule Breakout directement"""
        # Fallback simple
        breakout_signals = []
        for i in range(len(data)):
            if i < period:
                breakout_signals.append(0)
            else:
                recent_high = data['high'].iloc[i-period:i].max()
                recent_low = data['low'].iloc[i-period:i].min()
                current_close = data['close'].iloc[i]
                
                if current_close > recent_high * (1 + breakout_threshold/100):
                    breakout_signals.append(1)  # Breakout up
                elif current_close < recent_low * (1 - breakout_threshold/100):
                    breakout_signals.append(-1)  # Breakout down
                else:
                    breakout_signals.append(0)  # No breakout
        
        return pd.Series(breakout_signals, index=data.index)

    def calculate_squeeze(self, data: pd.DataFrame, bb_period: int = 20, kc_period: int = 20,
                          bb_multiplier: float = 2.0, kc_multiplier: float = 1.5) -> pd.Series:
        """Calcule Squeeze directement"""
        # Fallback simple - Squeeze Momentum simplifié
        squeeze_values = []
        for i in range(len(data)):
            if i < max(bb_period, kc_period):
                squeeze_values.append(0)
            else:
                # Bollinger Bands
                bb_sma = data['close'].iloc[i-bb_period:i].mean()
                bb_std = data['close'].iloc[i-bb_period:i].std()
                bb_upper = bb_sma + bb_std * bb_multiplier
                bb_lower = bb_sma - bb_std * bb_multiplier
                
                # Keltner Channels (simplifié)
                kc_sma = data['close'].iloc[i-kc_period:i].mean()
                kc_atr = (data['high'].iloc[i-kc_period:i] - data['low'].iloc[i-kc_period:i]).mean()
                kc_upper = kc_sma + kc_atr * kc_multiplier
                kc_lower = kc_sma - kc_atr * kc_multiplier
                
                # Squeeze condition
                squeeze = 1 if (bb_upper < kc_upper and bb_lower > kc_lower) else 0
                squeeze_values.append(squeeze)
        
        return pd.Series(squeeze_values, index=data.index)

    def calculate_obv(self, data: pd.DataFrame) -> pd.Series:
        """Calcule OBV directement"""
        # Fallback simple
        obv_values = [0]  # Start with 0
        for i in range(1, len(data)):
            if data['close'].iloc[i] > data['close'].iloc[i-1]:
                obv_values.append(obv_values[-1] + data['volume'].iloc[i])
            elif data['close'].iloc[i] < data['close'].iloc[i-1]:
                obv_values.append(obv_values[-1] - data['volume'].iloc[i])
            else:
                obv_values.append(obv_values[-1])
        
        return pd.Series(obv_values, index=data.index)

    def calculate_volume_profile(self, data: pd.DataFrame, bins: int = 50) -> Dict:
        """Calcule Volume Profile directement"""
        # Fallback simple
        price_min, price_max = data['low'].min(), data['high'].max()
        price_range = price_max - price_min
        bin_size = price_range / bins
        
        volume_profile = []
        price_levels = []
        
        for i in range(bins):
            level_min = price_min + i * bin_size
            level_max = price_min + (i + 1) * bin_size
            
            # Volume dans cette tranche de prix
            mask = (data['high'] >= level_min) & (data['low'] <= level_max)
            level_volume = data.loc[mask, 'volume'].sum()
            
            volume_profile.append(level_volume)
            price_levels.append((level_min + level_max) / 2)
        
        return {
            'volume_profile': volume_profile,
            'price_levels': price_levels
        }

    def calculate_fibonacci(self, high: float, low: float) -> Dict[str, float]:
        """Calcule niveaux Fibonacci directement"""
        diff = high - low
        return {
            "0.0": low,
            "0.236": low + diff * 0.236,
            "0.382": low + diff * 0.382,
            "0.5": low + diff * 0.5,
            "0.618": low + diff * 0.618,
            "0.786": low + diff * 0.786,
            "1.0": high
        }

    def calculate_pivot_points(self, high: float, low: float, close: float) -> Dict[str, float]:
        """Calcule Pivot Points directement"""
        pivot = (high + low + close) / 3
        return {
            "pivot": pivot,
            "r1": 2 * pivot - low,
            "r2": pivot + (high - low),
            "r3": high + 2 * (pivot - low),
            "s1": 2 * pivot - high,
            "s2": pivot - (high - low),
            "s3": low - 2 * (high - pivot)
        }

    def calculate_support_resistance(self, data: pd.DataFrame, lookback: int = 50) -> Dict[str, List[float]]:
        """Calcule Support et Résistance directement"""
        recent_data = data.tail(lookback)
        
        # Support: minima locaux
        supports = []
        for i in range(2, len(recent_data)-2):
            if (recent_data['low'].iloc[i] < recent_data['low'].iloc[i-1] and 
                recent_data['low'].iloc[i] < recent_data['low'].iloc[i-2] and
                recent_data['low'].iloc[i] < recent_data['low'].iloc[i+1] and 
                recent_data['low'].iloc[i] < recent_data['low'].iloc[i+2]):
                supports.append(recent_data['low'].iloc[i])
        
        # Résistance: maxima locaux
        resistances = []
        for i in range(2, len(recent_data)-2):
            if (recent_data['high'].iloc[i] > recent_data['high'].iloc[i-1] and 
                recent_data['high'].iloc[i] > recent_data['high'].iloc[i-2] and
                recent_data['high'].iloc[i] > recent_data['high'].iloc[i+1] and 
                recent_data['high'].iloc[i] > recent_data['high'].iloc[i+2]):
                resistances.append(recent_data['high'].iloc[i])
        
        return {
            "supports": sorted(list(set(supports)))[-3:],  # Top 3 supports
            "resistances": sorted(list(set(resistances)))[-3:]  # Top 3 resistances
        }


# Instance globale singleton
_indicator_factory = None

def get_indicator_factory() -> IndicatorFactory:
    """Retourne l'instance globale de la factory"""
    global _indicator_factory
    if _indicator_factory is None:
        _indicator_factory = IndicatorFactory()
    return _indicator_factory