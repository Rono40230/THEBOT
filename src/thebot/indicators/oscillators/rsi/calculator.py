"""
Calculateur RSI (Relative Strength Index)
Module ultra-modulaire - Responsabilité unique : Logique pure de calcul RSI
"""

from decimal import Decimal
from typing import Optional
from collections import deque

from thebot.core.types import MarketData, IndicatorResult
from thebot.indicators.oscillators.rsi.config import RSIConfig


class RSICalculator:
    """
    Calculateur pur pour RSI - Aucune dépendance externe
    Implémente l'algorithme classique de Wilder :
    RSI = 100 - (100 / (1 + RS))
    où RS = Moyenne des gains / Moyenne des pertes
    """
    
    def __init__(self, config: RSIConfig):
        self.config = config
        self.alpha = config.get_smoothing_alpha()
        
        # État interne RSI
        self._previous_close: Optional[Decimal] = None
        self._avg_gain: Optional[Decimal] = None
        self._avg_loss: Optional[Decimal] = None
        self._current_rsi: Optional[Decimal] = None
        self._data_count = 0
        
        # Pour SMA initial (premières périodes)
        self._initial_gains: deque = deque()
        self._initial_losses: deque = deque()
        self._is_initialized = False
        
        # Historique pour analyse (si activé)
        if config.store_history:
            self._history: deque = deque(maxlen=min(config.period * 3, 200))
        else:
            self._history = None
    
    def add_data_point(self, market_data: MarketData) -> Optional[IndicatorResult]:
        """
        Ajoute un point de données et calcule RSI
        
        Args:
            market_data: Données de marché
            
        Returns:
            IndicatorResult si calculable, None sinon
        """
        current_close = market_data.close
        self._data_count += 1
        
        # Premier point : pas de RSI calculable
        if self._previous_close is None:
            self._previous_close = current_close
            return None
        
        # Calculer le changement de prix
        price_change = current_close - self._previous_close
        gain = max(price_change, Decimal('0'))
        loss = abs(min(price_change, Decimal('0')))
        
        # Phase d'initialisation (premières périodes)
        if not self._is_initialized:
            rsi = self._calculate_initial_rsi(gain, loss)
        else:
            rsi = self._calculate_smoothed_rsi(gain, loss)
        
        # Stocker dans l'historique si activé
        if self._history is not None and rsi is not None:
            self._history.append({
                'timestamp': market_data.timestamp,
                'price': current_close,
                'rsi': rsi,
                'gain': gain,
                'loss': loss,
                'price_change': price_change
            })
        
        # Mettre à jour état
        self._previous_close = current_close
        self._current_rsi = rsi
        
        if rsi is not None:
            return IndicatorResult(
                value=rsi,
                timestamp=market_data.timestamp,
                indicator_name="RSI",
                metadata={
                    'period': self.config.period,
                    'price_change': float(price_change),
                    'gain': float(gain),
                    'loss': float(loss),
                    'avg_gain': float(self._avg_gain) if self._avg_gain else None,
                    'avg_loss': float(self._avg_loss) if self._avg_loss else None,
                    'data_count': self._data_count
                }
            )
        
        return None
    
    def _calculate_initial_rsi(self, gain: Decimal, loss: Decimal) -> Optional[Decimal]:
        """Calcule RSI pendant la phase d'initialisation"""
        self._initial_gains.append(gain)
        self._initial_losses.append(loss)
        
        # Attendre d'avoir assez de données
        if len(self._initial_gains) < self.config.period:
            return None
        
        # Calcul des moyennes initiales
        if self.config.smoothing_method == "sma":
            self._avg_gain = sum(self._initial_gains) / len(self._initial_gains)
            self._avg_loss = sum(self._initial_losses) / len(self._initial_losses)
        else:  # EMA - démarrage avec SMA puis passage à EMA
            self._avg_gain = sum(self._initial_gains) / len(self._initial_gains)
            self._avg_loss = sum(self._initial_losses) / len(self._initial_losses)
        
        self._is_initialized = True
        return self._calculate_rsi_from_averages()
    
    def _calculate_smoothed_rsi(self, gain: Decimal, loss: Decimal) -> Optional[Decimal]:
        """Calcule RSI avec moyennes lissées"""
        if self._avg_gain is None or self._avg_loss is None:
            return None
        
        if self.config.smoothing_method == "ema":
            # Lissage exponentiel (méthode de Wilder)
            # Wilder utilise alpha = 1/period au lieu de 2/(period+1)
            wilder_alpha = Decimal('1') / Decimal(str(self.config.period))
            self._avg_gain = wilder_alpha * gain + (Decimal('1') - wilder_alpha) * self._avg_gain
            self._avg_loss = wilder_alpha * loss + (Decimal('1') - wilder_alpha) * self._avg_loss
        else:  # SMA - recalcul complet (moins efficace)
            # Ajouter nouvelle valeur et maintenir la taille
            self._initial_gains.append(gain)
            self._initial_losses.append(loss)
            self._avg_gain = sum(self._initial_gains) / len(self._initial_gains)
            self._avg_loss = sum(self._initial_losses) / len(self._initial_losses)
        
        return self._calculate_rsi_from_averages()
    
    def _calculate_rsi_from_averages(self) -> Optional[Decimal]:
        """Calcule RSI à partir des moyennes"""
        if self._avg_gain is None or self._avg_loss is None:
            return None
        
        # Éviter division par zéro
        if self._avg_loss == 0:
            return Decimal('100')  # RSI maximum si pas de pertes
        
        # RSI = 100 - (100 / (1 + RS))
        # où RS = avg_gain / avg_loss
        rs = self._avg_gain / self._avg_loss
        rsi = Decimal('100') - (Decimal('100') / (Decimal('1') + rs))
        
        # S'assurer que RSI est dans [0, 100]
        return max(Decimal('0'), min(Decimal('100'), rsi))
    
    def get_current_value(self) -> Optional[Decimal]:
        """Valeur RSI actuelle"""
        return self._current_rsi
    
    def is_ready(self) -> bool:
        """Indicateur prêt"""
        return self._is_initialized and self._current_rsi is not None
    
    def get_data_count(self) -> int:
        """Nombre de points de données traités"""
        return self._data_count
    
    def reset(self) -> None:
        """Remet à zéro l'état du calculateur"""
        self._previous_close = None
        self._avg_gain = None
        self._avg_loss = None
        self._current_rsi = None
        self._data_count = 0
        self._initial_gains.clear()
        self._initial_losses.clear()
        self._is_initialized = False
        if self._history is not None:
            self._history.clear()
    
    def get_momentum_strength(self) -> Optional[str]:
        """
        Détermine la force du momentum basé sur RSI
        
        Returns:
            "strong_bullish", "bullish", "neutral", "bearish", "strong_bearish"
        """
        if not self._current_rsi:
            return None
        
        rsi = self._current_rsi
        
        if rsi >= self.config.extreme_overbought:
            return "strong_bullish"
        elif rsi >= self.config.overbought_level:
            return "bullish"
        elif rsi <= self.config.extreme_oversold:
            return "strong_bearish"
        elif rsi <= self.config.oversold_level:
            return "bearish"
        else:
            return "neutral"
    
    def get_divergence_data(self, periods: int = 5) -> Optional[dict]:
        """
        Analyse les données pour détecter des divergences
        
        Args:
            periods: Nombre de périodes pour analyser
            
        Returns:
            Dictionnaire avec données de divergence ou None
        """
        if self._history is None or len(self._history) < periods:
            return None
        
        recent_data = list(self._history)[-periods:]
        
        # Tendances prix et RSI
        price_start = recent_data[0]['price']
        price_end = recent_data[-1]['price']
        rsi_start = recent_data[0]['rsi']
        rsi_end = recent_data[-1]['rsi']
        
        price_trend = "up" if price_end > price_start else "down"
        rsi_trend = "up" if rsi_end > rsi_start else "down"
        
        # Détection divergence
        divergence = None
        if price_trend == "up" and rsi_trend == "down":
            divergence = "bearish"  # Prix monte, RSI baisse
        elif price_trend == "down" and rsi_trend == "up":
            divergence = "bullish"  # Prix baisse, RSI monte
        
        return {
            'price_trend': price_trend,
            'rsi_trend': rsi_trend,
            'divergence': divergence,
            'price_change': float(price_end - price_start),
            'rsi_change': float(rsi_end - rsi_start)
        }
    
    def get_volatility_adjusted_levels(self) -> dict:
        """
        Calcule des niveaux RSI ajustés selon la volatilité
        
        Returns:
            Dictionnaire avec niveaux ajustés
        """
        if not self._history or len(self._history) < 20:
            return {
                'overbought': float(self.config.overbought_level),
                'oversold': float(self.config.oversold_level)
            }
        
        # Calculer volatilité RSI
        recent_rsi = [point['rsi'] for point in list(self._history)[-20:]]
        rsi_mean = sum(recent_rsi) / len(recent_rsi)
        rsi_variance = sum((rsi - rsi_mean) ** 2 for rsi in recent_rsi) / len(recent_rsi)
        rsi_std = rsi_variance.sqrt()
        
        # Ajuster niveaux selon volatilité
        volatility_factor = min(Decimal('1.5'), max(Decimal('0.5'), rsi_std / Decimal('10')))
        
        adjusted_overbought = self.config.overbought_level + (Decimal('10') * volatility_factor)
        adjusted_oversold = self.config.oversold_level - (Decimal('10') * volatility_factor)
        
        # S'assurer des limites
        adjusted_overbought = min(Decimal('95'), adjusted_overbought)
        adjusted_oversold = max(Decimal('5'), adjusted_oversold)
        
        return {
            'overbought': float(adjusted_overbought),
            'oversold': float(adjusted_oversold),
            'volatility_factor': float(volatility_factor),
            'rsi_std': float(rsi_std)
        }