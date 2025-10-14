"""
Indicator Factory - Point d'entrée unifié pour tous les indicateurs
Centralise l'accès aux calculateurs THEBOT avec cache intelligent
"""

import logging
from typing import Any, Dict, Optional, Type, Union
from functools import lru_cache
import pandas as pd
import numpy as np

from .base.indicator import BaseIndicator
from .basic.sma.calculator import SMACalculator
from .basic.ema.calculator import EMACalculator
from .oscillators.rsi.calculator import RSICalculator
from .volatility.atr.calculator import ATRCalculator
from .momentum.macd.calculator import MACDCalculator

logger = logging.getLogger(__name__)


class IndicatorFactory:
    """
    Factory centralisée pour tous les indicateurs techniques.
    Utilise le cache LRU pour optimiser les performances.
    """

    # Mapping des noms d'indicateurs vers leurs classes
    INDICATOR_CLASSES = {
        'sma': SMACalculator,
        'ema': EMACalculator,
        'rsi': RSICalculator,
        'atr': ATRCalculator,
        'macd': MACDCalculator,
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
            'sma': 'basic',
            'ema': 'basic',
            'rsi': 'oscillators',
            'atr': 'volatility',
            'macd': 'momentum',
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


# Instance globale singleton
_indicator_factory = None

def get_indicator_factory() -> IndicatorFactory:
    """Retourne l'instance globale de la factory"""
    global _indicator_factory
    if _indicator_factory is None:
        _indicator_factory = IndicatorFactory()
    return _indicator_factory