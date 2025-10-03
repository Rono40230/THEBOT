"""
Pivot Points Indicator
Calcul des points pivots traditionnels (Standard, Fibonacci, Camarilla)
Support pour différentes timeframes et méthodes de calcul
"""

from typing import List, Dict, Optional, Tuple, Any
from decimal import Decimal
import numpy as np
from datetime import datetime, timedelta
from enum import Enum

from ...base.indicator import BaseIndicator
from ...base.types import MarketData, IndicatorResult, Signal, SignalDirection


class PivotMethod(Enum):
    """Méthodes de calcul des pivot points"""
    STANDARD = "standard"
    FIBONACCI = "fibonacci"
    CAMARILLA = "camarilla"
    DEMARK = "demark"


class PivotTimeframe(Enum):
    """Timeframes pour le calcul des pivots"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class PivotLevel:
    """Représente un niveau de pivot"""
    
    def __init__(self, price: float, level_type: str, level_name: str, 
                 calculation_date: datetime):
        self.price = price
        self.level_type = level_type  # 'pivot', 'support', 'resistance'
        self.level_name = level_name  # 'PP', 'S1', 'S2', 'R1', 'R2', etc.
        self.calculation_date = calculation_date
        self.touches = 0
        self.is_active = True
        
    def check_touch(self, current_price: float, tolerance: float = 0.001) -> bool:
        """Vérifie si le prix touche ce niveau"""
        price_tolerance = self.price * tolerance
        if abs(current_price - self.price) <= price_tolerance:
            self.touches += 1
            return True
        return False


class PivotPointsConfig:
    """Configuration pour Pivot Points"""
    
    def __init__(self):
        self.method = PivotMethod.STANDARD
        self.timeframe = PivotTimeframe.DAILY
        self.touch_tolerance = 0.002  # 0.2% de tolérance
        self.show_s3_r3 = True      # Afficher S3/R3
        self.show_s4_r4 = False     # Afficher S4/R4 (Camarilla uniquement)
        self.enabled = True


class PivotPointsIndicator(BaseIndicator):
    """
    Indicateur Pivot Points avec support de multiples méthodes
    Calcul automatique basé sur les données High/Low/Close
    """
    
    def __init__(self, config: PivotPointsConfig = None):
        super().__init__()
        self.config = config or PivotPointsConfig()
        
        # Historique des données
        self._price_history: List[MarketData] = []
        
        # Données pour calcul pivot (par timeframe)
        self._daily_data: Dict[str, Dict] = {}    # Format: {'2024-01-01': {'high': x, 'low': y, 'close': z}}
        self._weekly_data: Dict[str, Dict] = {}
        self._monthly_data: Dict[str, Dict] = {}
        
        # Niveaux pivot actuels
        self._pivot_levels: List[PivotLevel] = []
        
        # État
        self._current_result: Optional[IndicatorResult] = None
        self._last_calculation_date = None
        
    @property
    def name(self) -> str:
        return f"Pivot Points ({self.config.method.value.title()})"
    
    def get_required_periods(self) -> int:
        # Besoin d'au moins une période complète pour calculer
        return 24 if self.config.timeframe == PivotTimeframe.DAILY else 7 * 24
    
    @property
    def is_ready(self) -> bool:
        return len(self._price_history) >= self.get_required_periods()
    
    @property
    def current_value(self) -> Optional[Dict]:
        if not self.is_ready:
            return None
        return {
            'pivot_levels': [
                {
                    'price': level.price,
                    'type': level.level_type,
                    'name': level.level_name,
                    'touches': level.touches,
                    'calculation_date': level.calculation_date.isoformat()
                } for level in self._pivot_levels if level.is_active
            ],
            'method': self.config.method.value,
            'timeframe': self.config.timeframe.value
        }
    
    @property
    def data_count(self) -> int:
        return len(self._price_history)
    
    def add_data(self, market_data: MarketData) -> Optional[IndicatorResult]:
        """Ajoute des données et calcule les pivot points"""
        self._price_history.append(market_data)
        
        # Limiter l'historique (garder 2 mois)
        if len(self._price_history) > 60 * 24:  # 60 jours * 24h
            self._price_history.pop(0)
        
        if not self.is_ready:
            return None
        
        # Agréger les données par timeframe
        self._aggregate_data_by_timeframe()
        
        # Calculer les pivots si nécessaire
        current_date = market_data.timestamp.date()
        if self._should_recalculate_pivots(current_date):
            self._calculate_pivot_points()
            self._last_calculation_date = current_date
        
        # Vérifier les touches
        self._check_level_touches(market_data.close)
        
        # Créer le résultat
        result = IndicatorResult(
            value=self.current_value,
            timestamp=market_data.timestamp,
            indicator_name=self.name,
            metadata={
                'total_levels': len(self._pivot_levels),
                'method': self.config.method.value,
                'timeframe': self.config.timeframe.value,
                'calculation_date': self._last_calculation_date.isoformat() if self._last_calculation_date else None
            }
        )
        
        self._current_result = result
        return result
    
    def _aggregate_data_by_timeframe(self):
        """Agrège les données par timeframe pour le calcul des pivots"""
        if not self._price_history:
            return
        
        # Grouper par jour
        daily_groups = {}
        for data in self._price_history:
            date_key = data.timestamp.date().isoformat()
            if date_key not in daily_groups:
                daily_groups[date_key] = []
            daily_groups[date_key].append(data)
        
        # Calculer OHLC par jour
        for date_key, day_data in daily_groups.items():
            if len(day_data) > 0:
                high = max(d.high for d in day_data)
                low = min(d.low for d in day_data)
                close = day_data[-1].close  # Dernière close du jour
                open_price = day_data[0].open  # Première ouverture du jour
                
                self._daily_data[date_key] = {
                    'high': high,
                    'low': low,
                    'close': close,
                    'open': open_price
                }
        
        # Limiter les données quotidiennes
        if len(self._daily_data) > 60:
            oldest_keys = sorted(self._daily_data.keys())[:-60]
            for key in oldest_keys:
                del self._daily_data[key]
        
        # TODO: Ajouter agrégation hebdomadaire et mensuelle si nécessaire
    
    def _should_recalculate_pivots(self, current_date) -> bool:
        """Détermine si les pivots doivent être recalculés"""
        if not self._last_calculation_date:
            return True
        
        if self.config.timeframe == PivotTimeframe.DAILY:
            return current_date > self._last_calculation_date
        elif self.config.timeframe == PivotTimeframe.WEEKLY:
            # Recalculer le lundi
            return (current_date.weekday() == 0 and 
                   current_date > self._last_calculation_date)
        elif self.config.timeframe == PivotTimeframe.MONTHLY:
            # Recalculer le 1er du mois
            return (current_date.day == 1 and 
                   current_date > self._last_calculation_date)
        
        return False
    
    def _calculate_pivot_points(self):
        """Calcule les pivot points selon la méthode configurée"""
        if not self._daily_data:
            return
        
        # Prendre les données de la période précédente
        sorted_dates = sorted(self._daily_data.keys())
        if len(sorted_dates) < 2:
            return
        
        # Utiliser les données de la veille pour calculer les pivots du jour
        prev_date_key = sorted_dates[-2]
        prev_data = self._daily_data[prev_date_key]
        
        high = prev_data['high']
        low = prev_data['low']
        close = prev_data['close']
        
        # Calculer selon la méthode
        if self.config.method == PivotMethod.STANDARD:
            levels = self._calculate_standard_pivots(high, low, close)
        elif self.config.method == PivotMethod.FIBONACCI:
            levels = self._calculate_fibonacci_pivots(high, low, close)
        elif self.config.method == PivotMethod.CAMARILLA:
            levels = self._calculate_camarilla_pivots(high, low, close)
        elif self.config.method == PivotMethod.DEMARK:
            open_price = prev_data.get('open', close)
            levels = self._calculate_demark_pivots(high, low, close, open_price)
        else:
            levels = self._calculate_standard_pivots(high, low, close)
        
        # Créer les objets PivotLevel
        calculation_date = datetime.now()
        self._pivot_levels = []
        
        for level_name, price in levels.items():
            if level_name == 'PP':
                level_type = 'pivot'
            elif level_name.startswith('S'):
                level_type = 'support'
            else:  # Starts with 'R'
                level_type = 'resistance'
            
            pivot_level = PivotLevel(
                price=price,
                level_type=level_type,
                level_name=level_name,
                calculation_date=calculation_date
            )
            self._pivot_levels.append(pivot_level)
    
    def _calculate_standard_pivots(self, high: float, low: float, close: float) -> Dict[str, float]:
        """Calcule les pivot points standard"""
        pp = (high + low + close) / 3
        
        levels = {'PP': pp}
        
        # Support et résistance niveaux 1
        levels['R1'] = 2 * pp - low
        levels['S1'] = 2 * pp - high
        
        # Support et résistance niveaux 2
        levels['R2'] = pp + (high - low)
        levels['S2'] = pp - (high - low)
        
        # Support et résistance niveaux 3
        if self.config.show_s3_r3:
            levels['R3'] = high + 2 * (pp - low)
            levels['S3'] = low - 2 * (high - pp)
        
        return levels
    
    def _calculate_fibonacci_pivots(self, high: float, low: float, close: float) -> Dict[str, float]:
        """Calcule les pivot points Fibonacci"""
        pp = (high + low + close) / 3
        range_hl = high - low
        
        levels = {'PP': pp}
        
        # Utiliser les ratios Fibonacci
        levels['R1'] = pp + 0.382 * range_hl
        levels['R2'] = pp + 0.618 * range_hl
        levels['R3'] = pp + 1.000 * range_hl
        
        levels['S1'] = pp - 0.382 * range_hl
        levels['S2'] = pp - 0.618 * range_hl
        levels['S3'] = pp - 1.000 * range_hl
        
        return levels
    
    def _calculate_camarilla_pivots(self, high: float, low: float, close: float) -> Dict[str, float]:
        """Calcule les pivot points Camarilla"""
        range_hl = high - low
        
        levels = {'PP': close}  # Camarilla utilise la close comme pivot
        
        # Niveaux Camarilla avec coefficients spécifiques
        levels['R1'] = close + range_hl * 1.1 / 12
        levels['R2'] = close + range_hl * 1.1 / 6
        levels['R3'] = close + range_hl * 1.1 / 4
        
        levels['S1'] = close - range_hl * 1.1 / 12
        levels['S2'] = close - range_hl * 1.1 / 6
        levels['S3'] = close - range_hl * 1.1 / 4
        
        # Niveaux supplémentaires pour breakout
        if self.config.show_s4_r4:
            levels['R4'] = close + range_hl * 1.1 / 2
            levels['S4'] = close - range_hl * 1.1 / 2
        
        return levels
    
    def _calculate_demark_pivots(self, high: float, low: float, close: float, open_price: float) -> Dict[str, float]:
        """Calcule les pivot points DeMark"""
        # DeMark utilise une logique conditionnelle
        if close < open_price:
            x = high + 2 * low + close
        elif close > open_price:
            x = 2 * high + low + close
        else:
            x = high + low + 2 * close
        
        pp = x / 4
        
        levels = {'PP': pp}
        levels['R1'] = x / 2 - low
        levels['S1'] = x / 2 - high
        
        return levels
    
    def _check_level_touches(self, current_price: float):
        """Vérifie les touches des niveaux pivot"""
        for level in self._pivot_levels:
            if level.is_active:
                level.check_touch(current_price, self.config.touch_tolerance)
    
    def generate_signal(self, current_result: IndicatorResult) -> Optional[Signal]:
        """Génère des signaux basés sur les pivot points"""
        if not self.is_ready or not current_result.value:
            return None
        
        current_price = self._price_history[-1].close
        pivot_levels = current_result.value['pivot_levels']
        
        if not pivot_levels:
            return None
        
        # Trouver le niveau le plus proche
        closest_level = min(pivot_levels, key=lambda x: abs(current_price - x['price']))
        distance = abs(current_price - closest_level['price']) / current_price
        
        # Signal si proche d'un niveau important
        if distance <= 0.005:  # 0.5%
            level_name = closest_level['name']
            
            # Déterminer la direction selon le type de niveau
            if closest_level['type'] == 'support':
                direction = SignalDirection.LONG
                message = f"Prix proche support pivot {level_name} à {closest_level['price']:.4f}"
            elif closest_level['type'] == 'resistance':
                direction = SignalDirection.SHORT
                message = f"Prix proche résistance pivot {level_name} à {closest_level['price']:.4f}"
            else:  # pivot
                direction = SignalDirection.NEUTRAL
                message = f"Prix proche point pivot {level_name} à {closest_level['price']:.4f}"
            
            # Force selon l'importance du niveau
            strength = 0.6
            if level_name in ['PP', 'R1', 'S1']:  # Niveaux principaux
                strength = 0.8
            if closest_level['touches'] > 0:  # Bonus si testé
                strength += 0.2
            
            return Signal(
                direction=direction,
                strength=min(strength, 1.0),
                message=message,
                indicator_name=self.name,
                timestamp=datetime.now(),
                metadata={
                    'pivot_level': level_name,
                    'level_price': closest_level['price'],
                    'level_type': closest_level['type'],
                    'touches': closest_level['touches']
                }
            )
        
        return None
    
    def get_levels_for_chart(self) -> Dict[str, List[Dict]]:
        """Retourne les niveaux formatés pour l'affichage graphique"""
        level_colors = {
            'PP': '#FFFF00',    # Jaune pour pivot principal
            'R1': '#FF6B6B',    # Rouge pour résistances
            'R2': '#FF8E8E',
            'R3': '#FFB3B3',
            'R4': '#FFD6D6',
            'S1': '#4ECDC4',    # Vert pour supports
            'S2': '#7EDDD8',
            'S3': '#AFEEED',
            'S4': '#CFFEFC'
        }
        
        level_styles = {
            'PP': 'solid',
            'R1': 'solid', 'S1': 'solid',
            'R2': 'dash', 'S2': 'dash',
            'R3': 'dot', 'S3': 'dot',
            'R4': 'dashdot', 'S4': 'dashdot'
        }
        
        return {
            'pivot_levels': [
                {
                    'y': level.price,
                    'label': f"{level.level_name}: {level.price:.4f}",
                    'color': level_colors.get(level.level_name, '#888888'),
                    'line_width': 3 if level.level_name == 'PP' else (2 if level.touches > 0 else 1),
                    'line_dash': level_styles.get(level.level_name, 'solid'),
                    'level_type': level.level_type,
                    'touches': level.touches
                } for level in self._pivot_levels if level.is_active
            ]
        }
    
    def reset(self) -> None:
        """Remet à zéro l'indicateur"""
        self._price_history.clear()
        self._daily_data.clear()
        self._weekly_data.clear()
        self._monthly_data.clear()
        self._pivot_levels.clear()
        self._current_result = None
        self._last_calculation_date = None