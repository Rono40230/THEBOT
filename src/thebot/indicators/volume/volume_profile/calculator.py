"""
Calculateur Volume Profile avec POC (Point of Control)
Analyse la distribution du volume par niveau de prix
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime, time
import warnings

from .config import VolumeProfileConfig, VolumeProfileType, ValueAreaMethod
from ...base.indicator import BaseIndicator
from ....core.types import MarketData, IndicatorResult

@dataclass
class VolumeNode:
    """Nœud de volume à un niveau de prix"""
    price_level: float
    volume: float
    volume_percent: float
    is_poc: bool = False
    is_high_volume: bool = False
    is_low_volume: bool = False
    support_strength: float = 0.0
    resistance_strength: float = 0.0

@dataclass
class ValueArea:
    """Zone de Value Area (70% du volume)"""
    high: float
    low: float
    poc: float
    volume_percent: float
    total_volume: float

@dataclass
class VolumeProfileResult:
    """Résultat complet d'analyse Volume Profile"""
    nodes: List[VolumeNode]
    poc: VolumeNode
    value_area: ValueArea
    high_volume_nodes: List[VolumeNode]
    low_volume_nodes: List[VolumeNode]
    total_volume: float
    price_range: Tuple[float, float]
    analysis_period: Tuple[datetime, datetime]
    
class VolumeProfileCalculator(BaseIndicator):
    """Calculateur Volume Profile + POC"""
    
    def __init__(self, config: VolumeProfileConfig):
        self._version = "1.0.0"
        super().__init__("Volume Profile", config.to_dict())
        self.config = config
    
    @property
    def version(self) -> str:
        return self._version
    
    def get_required_periods(self) -> int:
        """Retourne le nombre minimum de périodes nécessaires"""
        return max(self.config.lookback_periods, 20)
    
    def generate_signal(self, current_result: IndicatorResult) -> Optional[Dict]:
        """Génère un signal basé sur Volume Profile"""
        # Implémentation basique pour satisfaire l'interface
        # Le vrai calcul des signaux est dans _calculate_signals
        if not current_result or not current_result.value:
            return None
            
        # Signal simple basé sur la position du prix par rapport au POC
        profile_data = current_result.value
        if isinstance(profile_data, dict) and 'poc' in profile_data:
            return {"signal": "neutral", "strength": 0.5}
        
        return None
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Point d'entrée principal du calcul"""
        try:
            if len(data) < 10:
                return self._empty_result()
            
            # Analyse Volume Profile
            result = self.analyze_volume_profile(data)
            
            # Calcul des signaux
            signals = self._calculate_signals(data, result)
            
            return {
                "volume_profile": result,
                "signals": signals,
                "metadata": {
                    "calculation_time": datetime.now(),
                    "data_points": len(data),
                    "config": self.config.to_dict()
                }
            }
            
        except Exception as e:
            warnings.warn(f"Erreur calcul Volume Profile: {e}")
            return self._empty_result()
    
    def analyze_volume_profile(self, data: pd.DataFrame) -> VolumeProfileResult:
        """Analyse complète du Volume Profile"""
        
        # Sélection des données selon le type de profil
        analysis_data = self._select_analysis_data(data)
        
        if len(analysis_data) == 0:
            return self._empty_profile_result()
        
        # Calcul des niveaux de prix
        price_levels = self._calculate_price_levels(analysis_data)
        
        # Distribution du volume par niveau
        volume_nodes = self._distribute_volume_by_price(analysis_data, price_levels)
        
        # Identification du POC
        poc = self._find_poc(volume_nodes)
        
        # Calcul de la Value Area
        value_area = self._calculate_value_area(volume_nodes)
        
        # Classification des nœuds
        high_volume_nodes, low_volume_nodes = self._classify_volume_nodes(volume_nodes)
        
        # Calcul forces support/résistance
        self._calculate_support_resistance_strength(volume_nodes, analysis_data)
        
        return VolumeProfileResult(
            nodes=volume_nodes,
            poc=poc,
            value_area=value_area,
            high_volume_nodes=high_volume_nodes,
            low_volume_nodes=low_volume_nodes,
            total_volume=analysis_data['volume'].sum(),
            price_range=(analysis_data['low'].min(), analysis_data['high'].max()),
            analysis_period=(analysis_data.index[0], analysis_data.index[-1])
        )
    
    def _select_analysis_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Sélectionne les données selon le type de profil"""
        
        if self.config.profile_type == VolumeProfileType.FIXED_RANGE:
            # Période fixe basée sur lookback_periods
            periods = min(self.config.lookback_periods, len(data))
            return data.tail(periods).copy()
        
        elif self.config.profile_type == VolumeProfileType.SESSION:
            # Par session de trading (à implémenter selon timezone)
            return data.tail(self.config.lookback_periods).copy()
        
        elif self.config.profile_type == VolumeProfileType.VISIBLE_RANGE:
            # Zone visible (simule avec lookback pour l'instant)
            periods = min(self.config.lookback_periods, len(data))
            return data.tail(periods).copy()
        
        else:  # CUSTOM
            periods = min(self.config.lookback_periods, len(data))
            return data.tail(periods).copy()
    
    def _calculate_price_levels(self, data: pd.DataFrame) -> np.ndarray:
        """Calcule les niveaux de prix pour l'histogramme"""
        price_min = data['low'].min()
        price_max = data['high'].max()
        
        # Création des bins de prix
        return np.linspace(price_min, price_max, self.config.bins_count + 1)
    
    def _distribute_volume_by_price(self, data: pd.DataFrame, price_levels: np.ndarray) -> List[VolumeNode]:
        """Distribue le volume par niveau de prix"""
        
        # Initialisation des volumes par niveau
        volume_by_level = np.zeros(len(price_levels) - 1)
        
        # Pour chaque bougie, distribuer le volume
        for idx, row in data.iterrows():
            candle_high = row['high']
            candle_low = row['low']
            candle_volume = row['volume']
            
            # Trouver les niveaux couverts par cette bougie
            high_bin = np.searchsorted(price_levels, candle_high, side='right') - 1
            low_bin = np.searchsorted(price_levels, candle_low, side='left')
            
            high_bin = max(0, min(high_bin, len(volume_by_level) - 1))
            low_bin = max(0, min(low_bin, len(volume_by_level) - 1))
            
            # Distribution du volume
            if high_bin == low_bin:
                # Volume concentré sur un seul niveau
                volume_by_level[low_bin] += candle_volume
            else:
                # Distribution proportionnelle
                price_range = candle_high - candle_low
                if price_range > 0:
                    for bin_idx in range(low_bin, high_bin + 1):
                        bin_low = price_levels[bin_idx]
                        bin_high = price_levels[bin_idx + 1]
                        
                        # Intersection entre bougie et bin
                        overlap_low = max(candle_low, bin_low)
                        overlap_high = min(candle_high, bin_high)
                        overlap = max(0, overlap_high - overlap_low)
                        
                        # Volume proportionnel
                        proportion = overlap / price_range
                        volume_by_level[bin_idx] += candle_volume * proportion
        
        # Conversion en VolumeNode
        total_volume = volume_by_level.sum()
        nodes = []
        
        for i in range(len(volume_by_level)):
            price_level = (price_levels[i] + price_levels[i + 1]) / 2
            volume = volume_by_level[i]
            volume_percent = (volume / total_volume * 100) if total_volume > 0 else 0
            
            # Filtrage volume minimum
            if volume_percent >= self.config.min_volume_threshold:
                nodes.append(VolumeNode(
                    price_level=price_level,
                    volume=volume,
                    volume_percent=volume_percent
                ))
        
        return sorted(nodes, key=lambda x: x.volume, reverse=True)
    
    def _find_poc(self, nodes: List[VolumeNode]) -> VolumeNode:
        """Trouve le Point of Control (POC)"""
        if not nodes:
            return VolumeNode(0, 0, 0, is_poc=True)
        
        # POC = niveau avec le plus gros volume
        poc = max(nodes, key=lambda x: x.volume)
        poc.is_poc = True
        
        return poc
    
    def _calculate_value_area(self, nodes: List[VolumeNode]) -> ValueArea:
        """Calcule la Value Area (70% du volume)"""
        if not nodes:
            return ValueArea(0, 0, 0, 0, 0)
        
        # Tri par volume décroissant
        sorted_nodes = sorted(nodes, key=lambda x: x.volume, reverse=True)
        total_volume = sum(node.volume for node in nodes)
        target_volume = total_volume * (self.config.value_area_percent / 100.0)
        
        # Sélection des nœuds jusqu'à atteindre le % cible
        selected_nodes = []
        cumulative_volume = 0
        
        for node in sorted_nodes:
            selected_nodes.append(node)
            cumulative_volume += node.volume
            
            if cumulative_volume >= target_volume:
                break
        
        # Calcul des bornes de la Value Area
        if selected_nodes:
            prices = [node.price_level for node in selected_nodes]
            value_area_high = max(prices)
            value_area_low = min(prices)
            
            # POC au centre de la Value Area
            poc_price = max(selected_nodes, key=lambda x: x.volume).price_level
        else:
            value_area_high = value_area_low = poc_price = 0
        
        return ValueArea(
            high=value_area_high,
            low=value_area_low,
            poc=poc_price,
            volume_percent=self.config.value_area_percent,
            total_volume=cumulative_volume
        )
    
    def _classify_volume_nodes(self, nodes: List[VolumeNode]) -> Tuple[List[VolumeNode], List[VolumeNode]]:
        """Classifie les nœuds en High/Low Volume Nodes"""
        if not nodes:
            return [], []
        
        # Calcul des seuils
        max_volume_percent = max(node.volume_percent for node in nodes)
        high_threshold = max_volume_percent * (self.config.high_volume_threshold / 100.0)
        low_threshold = max_volume_percent * (self.config.low_volume_threshold / 100.0)
        
        high_volume_nodes = []
        low_volume_nodes = []
        
        for node in nodes:
            if node.volume_percent >= high_threshold:
                node.is_high_volume = True
                high_volume_nodes.append(node)
            elif node.volume_percent <= low_threshold:
                node.is_low_volume = True
                low_volume_nodes.append(node)
        
        return high_volume_nodes, low_volume_nodes
    
    def _calculate_support_resistance_strength(self, nodes: List[VolumeNode], data: pd.DataFrame):
        """Calcule la force de support/résistance basée sur le volume"""
        
        for node in nodes:
            # Force basée sur le volume relatif
            base_strength = node.volume_percent / 100.0
            
            # Ajustement selon proximité des prix récents
            recent_prices = data['close'].tail(20)
            price_distance = abs(recent_prices - node.price_level).min()
            price_range = data['high'].max() - data['low'].min()
            
            if price_range > 0:
                proximity_factor = 1.0 - (price_distance / price_range)
                node.support_strength = base_strength * proximity_factor * self.config.support_resistance_strength
                node.resistance_strength = node.support_strength
    
    def _calculate_signals(self, data: pd.DataFrame, result: VolumeProfileResult) -> Dict[str, Any]:
        """Calcule les signaux de trading basés sur Volume Profile"""
        
        if len(data) == 0 or not result.nodes:
            return {"signal": "neutral", "strength": 0.0, "details": {}}
        
        current_price = float(data['close'].iloc[-1])
        
        # Distance au POC
        poc_distance = abs(current_price - result.poc.price_level) / current_price
        
        # Position dans Value Area
        in_value_area = result.value_area.low <= current_price <= result.value_area.high
        
        # Proximité High Volume Nodes
        hvn_proximities = []
        for hvn in result.high_volume_nodes:
            distance = abs(current_price - hvn.price_level) / current_price
            if distance <= (self.config.poc_proximity_percent / 100.0):
                hvn_proximities.append((hvn, distance))
        
        # Génération du signal
        signal_strength = 0.0
        signal_type = "neutral"
        
        if poc_distance <= (self.config.poc_proximity_percent / 100.0):
            signal_strength = 0.8
            signal_type = "poc_retest"
        elif in_value_area and hvn_proximities:
            signal_strength = 0.6
            signal_type = "hvn_support"
        elif not in_value_area:
            if current_price > result.value_area.high:
                signal_strength = 0.5
                signal_type = "above_value_area"
            else:
                signal_strength = 0.5
                signal_type = "below_value_area"
        
        return {
            "signal": signal_type,
            "strength": signal_strength,
            "details": {
                "current_price": current_price,
                "poc_price": result.poc.price_level,
                "poc_distance": poc_distance,
                "in_value_area": in_value_area,
                "value_area_high": result.value_area.high,
                "value_area_low": result.value_area.low,
                "hvn_proximities": len(hvn_proximities)
            }
        }
    
    def _empty_result(self) -> Dict[str, Any]:
        """Résultat vide en cas d'erreur"""
        return {
            "volume_profile": self._empty_profile_result(),
            "signals": {"signal": "neutral", "strength": 0.0, "details": {}},
            "metadata": {"error": "Insufficient data"}
        }
    
    def _empty_profile_result(self) -> VolumeProfileResult:
        """Résultat Volume Profile vide"""
        empty_node = VolumeNode(0, 0, 0)
        empty_value_area = ValueArea(0, 0, 0, 0, 0)
        
        return VolumeProfileResult(
            nodes=[],
            poc=empty_node,
            value_area=empty_value_area,
            high_volume_nodes=[],
            low_volume_nodes=[],
            total_volume=0,
            price_range=(0, 0),
            analysis_period=(datetime.now(), datetime.now())
        )
    
    def get_trading_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Interface publique pour les signaux de trading"""
        result = self.calculate(data)
        return result.get("signals", {"signal": "neutral", "strength": 0.0})
    
    def get_support_resistance_levels(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Retourne les niveaux de support/résistance basés sur le volume"""
        result = self.calculate(data)
        profile = result.get("volume_profile")
        
        if not profile or not profile.nodes:
            return []
        
        levels = []
        
        # POC comme niveau principal
        levels.append({
            "price": profile.poc.price_level,
            "type": "poc",
            "strength": profile.poc.volume_percent / 100.0,
            "volume": profile.poc.volume
        })
        
        # High Volume Nodes
        for hvn in profile.high_volume_nodes:
            if not hvn.is_poc:  # Éviter doublons avec POC
                levels.append({
                    "price": hvn.price_level,
                    "type": "high_volume_node",
                    "strength": hvn.support_strength,
                    "volume": hvn.volume
                })
        
        # Bornes Value Area
        levels.extend([
            {
                "price": profile.value_area.high,
                "type": "value_area_high",
                "strength": 0.6,
                "volume": 0
            },
            {
                "price": profile.value_area.low,
                "type": "value_area_low", 
                "strength": 0.6,
                "volume": 0
            }
        ])
        
        return sorted(levels, key=lambda x: x["strength"], reverse=True)