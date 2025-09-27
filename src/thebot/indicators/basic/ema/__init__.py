"""
Indicateur EMA (Exponential Moving Average) - Orchestration
Module ultra-modulaire - Responsabilité unique : Interface et signaux
"""

from decimal import Decimal
from typing import Optional, Dict, Any, List

from thebot.core.types import MarketData, IndicatorResult, Signal, SignalDirection, SignalStrength
from thebot.indicators.base.indicator import BaseIndicator
from thebot.indicators.basic.ema.config import EMAConfig
from thebot.indicators.basic.ema.calculator import EMACalculator


class EMAIndicator(BaseIndicator):
    """
    Indicateur EMA complet avec génération de signaux
    Orchestration entre configuration, calcul et signalisation
    """
    
    def __init__(self, config: EMAConfig):
        super().__init__()
        self.config = config
        self.calculator = EMACalculator(config)
        
        # État pour génération de signaux
        self._previous_result: Optional[IndicatorResult] = None
        self._current_result: Optional[IndicatorResult] = None
        
        # Historique prix pour comparaisons
        self._price_history: List[Decimal] = []
    
    @property
    def name(self) -> str:
        return f"EMA"
    
    def get_required_periods(self) -> int:
        """EMA calculable dès le premier point mais plus stable après 'period' points"""
        return 1  # Calculable immédiatement
    
    def get_stable_periods(self) -> int:
        """Périodes nécessaires pour des signaux stables"""
        return self.config.period
    
    @property
    def is_ready(self) -> bool:
        return self.calculator.is_ready()
    
    @property
    def current_value(self) -> Optional[Decimal]:
        return self.calculator.get_current_value()
    
    @property
    def data_count(self) -> int:
        return self.calculator.get_data_count()
    
    def add_data(self, market_data: MarketData) -> Optional[IndicatorResult]:
        """
        Ajoute des données et calcule EMA
        
        Args:
            market_data: Données de marché
            
        Returns:
            IndicatorResult ou None
        """
        # Stocker prix pour analyse
        self._price_history.append(market_data.close)
        if len(self._price_history) > 100:  # Garder seulement les 100 derniers
            self._price_history.pop(0)
        
        # Calculer EMA
        result = self.calculator.add_data_point(market_data)
        
        if result:
            # Mettre à jour l'état pour signaux
            self._previous_result = self._current_result
            self._current_result = result
        
        return result
    
    def generate_signal(self, current_result: IndicatorResult) -> Optional[Signal]:
        """
        Génère des signaux basés sur EMA vs Prix
        
        Types de signaux EMA :
        1. Prix croise au-dessus EMA = BUY
        2. Prix croise en-dessous EMA = SELL  
        3. Pente EMA + distance = Force du signal
        
        Args:
            current_result: Résultat EMA actuel
            
        Returns:
            Signal ou None
        """
        if not self.config.enable_signals or not self._previous_result:
            return None
        
        current_price = self._price_history[-1] if self._price_history else None
        previous_price = self._price_history[-2] if len(self._price_history) >= 2 else None
        
        if not current_price or not previous_price:
            return None
        
        current_ema = current_result.value
        previous_ema = self._previous_result.value
        
        # Détection de croisement Prix vs EMA
        signal_direction = None
        signal_strength = SignalStrength.WEAK
        
        # Prix précédent vs EMA précédent
        was_above = previous_price > previous_ema
        # Prix actuel vs EMA actuel  
        is_above = current_price > current_ema
        
        # Croisement détecté
        if was_above != is_above:
            if is_above:
                signal_direction = SignalDirection.BUY
            else:
                signal_direction = SignalDirection.SELL
        
        # Pas de croisement, vérifier divergence continue
        elif abs(current_price - current_ema) / current_ema > self.config.crossover_sensitivity:
            # Distance significative du prix par rapport à l'EMA
            price_distance = abs(current_price - current_ema) / current_ema
            
            # Signal faible si prix s'éloigne de l'EMA dans le sens de la tendance
            ema_trend = self.get_trend_direction()
            if ema_trend == SignalDirection.BUY and current_price > current_ema:
                signal_direction = SignalDirection.BUY
                signal_strength = SignalStrength.WEAK
            elif ema_trend == SignalDirection.SELL and current_price < current_ema:
                signal_direction = SignalDirection.SELL  
                signal_strength = SignalStrength.WEAK
        
        # Ajuster la force du signal selon la pente EMA et distance
        if signal_direction:
            # Distance prix/EMA
            price_distance = abs(current_price - current_ema) / current_ema
            
            # Pente EMA (tendance)
            ema_slope = self.calculator.get_trend_slope(periods=3)
            
            # Force basée sur distance et pente
            if price_distance > Decimal('0.02'):  # 2%
                signal_strength = SignalStrength.STRONG
            elif price_distance > Decimal('0.01'):  # 1%  
                signal_strength = SignalStrength.MEDIUM
            
            # Bonus si pente EMA dans le même sens
            if ema_slope:
                if (signal_direction == SignalDirection.BUY and ema_slope > 0) or \
                   (signal_direction == SignalDirection.SELL and ema_slope < 0):
                    # Upgrade la force
                    if signal_strength == SignalStrength.WEAK:
                        signal_strength = SignalStrength.MEDIUM
                    elif signal_strength == SignalStrength.MEDIUM:
                        signal_strength = SignalStrength.STRONG
            
            # Confiance basée sur stabilité
            confidence = min(Decimal('0.9'), Decimal('0.6') + price_distance * 10)
            
            return Signal(
                direction=signal_direction,
                strength=signal_strength,
                price=current_price,
                timestamp=current_result.timestamp,
                source=self.name,
                confidence=float(confidence),
                metadata={
                    'indicator': self.name,
                    'ema_value': float(current_ema),
                    'price_distance': float(price_distance),
                    'ema_slope': float(ema_slope) if ema_slope else None,
                    'crossover_detected': was_above != is_above
                }
            )
        
        return None
    
    def get_trend_direction(self) -> SignalDirection:
        """
        Détermine la direction de tendance basée sur la pente EMA
        
        Returns:
            SignalDirection (BUY/SELL/NEUTRAL)
        """
        slope = self.calculator.get_trend_slope(periods=min(5, self.data_count))
        
        if slope is None:
            return SignalDirection.NEUTRAL
        
        # Seuil de pente significative (ajustable)
        slope_threshold = Decimal('0.1')
        
        if slope > slope_threshold:
            return SignalDirection.BUY
        elif slope < -slope_threshold:
            return SignalDirection.SELL
        else:
            return SignalDirection.NEUTRAL
    
    def get_distance_from_ema(self) -> Optional[Decimal]:
        """
        Calcule la distance du prix actuel par rapport à l'EMA (en %)
        
        Returns:
            Distance en pourcentage ou None
        """
        if not self._price_history or not self.current_value:
            return None
        
        current_price = self._price_history[-1]
        distance = ((current_price - self.current_value) / self.current_value) * 100
        return distance
    
    def get_ema_efficiency(self) -> Optional[Decimal]:
        """
        Calcule l'efficacité de l'EMA (réactivité vs bruit)
        
        Returns:
            Ratio efficacité (0-1) ou None
        """
        volatility = self.calculator.get_volatility()
        if volatility is None or volatility == 0:
            return None
        
        slope = self.calculator.get_trend_slope()
        if slope is None:
            return Decimal('0.5')
        
        # Ratio signal/bruit
        efficiency = abs(slope) / (volatility + abs(slope))
        return min(Decimal('1'), efficiency)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Métadonnées complètes de l'indicateur"""
        base_metadata = {
            'name': self.name,
            'config': self.config.to_dict(),
            'data_points': self.data_count,
            'is_ready': self.is_ready,
            'required_periods': self.get_required_periods(),
            'stable_periods': self.get_stable_periods()
        }
        
        # Ajout métadonnées calculées si disponibles
        if self.current_value:
            base_metadata.update({
                'current_value': float(self.current_value),
                'alpha': float(self.calculator.alpha),
                'distance_from_price': float(self.get_distance_from_ema() or 0),
                'trend_direction': self.get_trend_direction().value,
                'efficiency': float(self.get_ema_efficiency() or 0)
            })
        
        return base_metadata
    
    def reset(self) -> None:
        """Remet à zéro l'indicateur"""
        self.calculator.reset()
        self._previous_result = None
        self._current_result = None
        self._price_history.clear()
    
    def clone_with_period(self, new_period: int) -> 'EMAIndicator':
        """
        Clone l'indicateur avec une nouvelle période
        
        Args:
            new_period: Nouvelle période EMA
            
        Returns:
            Nouveau EMAIndicator avec période différente
        """
        new_config = EMAConfig(
            period=new_period,
            enable_signals=self.config.enable_signals,
            crossover_sensitivity=self.config.crossover_sensitivity,
            use_decimal=self.config.use_decimal,
            store_history=self.config.store_history
        )
        return EMAIndicator(new_config)