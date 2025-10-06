"""
Calculateur pour l'indicateur MACD (Moving Average Convergence Divergence)
Module ultra-modulaire - Responsabilité unique : Calculs MACD
"""

import pandas as pd
import numpy as np
from decimal import Decimal
from typing import Dict, Tuple, Optional
import logging

from .config import MACDConfig

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Erreur de validation des données"""
    pass

class CalculationError(Exception):
    """Erreur de calcul"""
    pass


class MACDCalculator:
    """Calculateur MACD selon la formule standard de Gerald Appel"""
    
    def __init__(self, config: MACDConfig):
        """
        Initialise le calculateur avec validation.
        
        Args:
            config: Configuration validée MACD
            
        Raises:
            ValidationError: Si configuration invalide
        """
        self.config = config
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Calcule MACD, Signal et Histogramme.
        
        Args:
            data: DataFrame avec colonnes OHLCV
            
        Returns:
            Dict avec clés 'macd', 'signal', 'histogram'
            
        Raises:
            CalculationError: Si calcul échoue
            ValidationError: Si données invalides
        """
        try:
            self._validate_data(data)
            
            # Extraction prix selon source
            prices = self._extract_prices(data)
            
            # Calcul EMAs
            ema_fast = self._calculate_ema(prices, self.config.fast_period)
            ema_slow = self._calculate_ema(prices, self.config.slow_period)
            
            # Ligne MACD (différence des EMAs)
            macd_line = ema_fast - ema_slow
            
            # Ligne Signal (EMA du MACD)
            signal_line = self._calculate_ema(macd_line, self.config.signal_period)
            
            # Histogramme (MACD - Signal)
            histogram = macd_line - signal_line
            
            logger.debug(f"MACD calculé: {len(macd_line)} points")
            
            return {
                'macd': macd_line,
                'signal': signal_line,
                'histogram': histogram
            }
            
        except Exception as e:
            raise CalculationError(f"Erreur calcul MACD: {str(e)}") from e
    
    def calculate_signals(self, macd_data: Dict[str, pd.Series]) -> pd.DataFrame:
        """
        Calcule les signaux de trading (crossovers).
        
        Args:
            macd_data: Résultat de calculate()
            
        Returns:
            DataFrame avec colonnes 'signal_type', 'strength'
        """
        try:
            macd = macd_data['macd']
            signal = macd_data['signal']
            histogram = macd_data['histogram']
            
            signals = pd.DataFrame(index=macd.index)
            signals['signal_type'] = 'hold'
            signals['strength'] = 0.0
            
            # Détection crossovers
            for i in range(1, len(macd)):
                prev_macd, curr_macd = macd.iloc[i-1], macd.iloc[i]
                prev_signal, curr_signal = signal.iloc[i-1], signal.iloc[i]
                
                # Crossover bullish (MACD croise au-dessus Signal)
                if prev_macd <= prev_signal and curr_macd > curr_signal:
                    signals.iloc[i, signals.columns.get_loc('signal_type')] = 'buy'
                    signals.iloc[i, signals.columns.get_loc('strength')] = min(abs(histogram.iloc[i]) * 100, 1.0)
                
                # Crossover bearish (MACD croise en-dessous Signal)
                elif prev_macd >= prev_signal and curr_macd < curr_signal:
                    signals.iloc[i, signals.columns.get_loc('signal_type')] = 'sell'
                    signals.iloc[i, signals.columns.get_loc('strength')] = min(abs(histogram.iloc[i]) * 100, 1.0)
            
            return signals
            
        except Exception as e:
            raise CalculationError(f"Erreur calcul signaux MACD: {str(e)}") from e
    
    def _validate_data(self, data: pd.DataFrame):
        """Valide les données d'entrée"""
        if data.empty:
            raise ValidationError("DataFrame vide")
        
        required_cols = ['open', 'high', 'low', 'close']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise ValidationError(f"Colonnes manquantes: {missing_cols}")
        
        min_periods = max(self.config.slow_period, self.config.signal_period) + 10
        if len(data) < min_periods:
            raise ValidationError(f"Données insuffisantes: {len(data)} < {min_periods} requis")
    
    def _extract_prices(self, data: pd.DataFrame) -> pd.Series:
        """Extrait les prix selon la source configurée"""
        if self.config.source == "close":
            return data['close']
        elif self.config.source == "typical":
            return (data['high'] + data['low'] + data['close']) / 3
        elif self.config.source == "weighted":
            return (data['high'] + data['low'] + 2*data['close']) / 4
        else:
            return data[self.config.source]
    
    def _calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Calcule EMA avec la formule standard.
        
        Args:
            prices: Série de prix
            period: Période EMA
            
        Returns:
            Série EMA
        """
        # Utiliser pandas ewm pour calcul optimisé
        return prices.ewm(span=period, adjust=False).mean()
    
    def get_calculation_info(self) -> Dict[str, any]:
        """Retourne les informations de calcul"""
        return {
            "indicator": "MACD",
            "fast_period": self.config.fast_period,
            "slow_period": self.config.slow_period,
            "signal_period": self.config.signal_period,
            "source": getattr(self.config, 'source', 'close'),
            "min_periods_required": max(self.config.slow_period, self.config.signal_period) + 10,
            "formula": f"MACD = EMA({self.config.fast_period}) - EMA({self.config.slow_period}), Signal = EMA(MACD, {self.config.signal_period})"
        }