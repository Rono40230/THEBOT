"""
Integration Layer - Connexion entre indicateurs modernes et dashboard Dash
Responsable: Adapter les indicateurs testés pour utilisation dans Dash
Architecture: Factory pattern + Async callbacks
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union

import pandas as pd
from src.thebot.core.logger import logger
from src.thebot.core.types import IndicatorResult, SignalDirection, TimeFrame
from src.thebot.indicators.factory import IndicatorFactory


@dataclass
class IndicatorConfig:
    """Configuration pour un indicateur intégré"""
    name: str
    category: str
    parameters: Dict[str, Any]
    timeframe: TimeFrame
    enabled: bool = True
    show_signals: bool = True
    show_alerts: bool = True


@dataclass
class IndicatorIntegrationResult:
    """Résultat d'intégration d'un indicateur"""
    indicator_name: str
    data: pd.DataFrame
    signals: List[Dict[str, Any]]
    chart_data: Optional[Dict[str, Any]] = None
    statistics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class IndicatorIntegrationFactory:
    """
    Factory pour créer des intégrations d'indicateurs
    Gère la création et la configuration des indicateurs pour Dash
    """

    def __init__(self):
        """Initialiser la factory"""
        self.indicator_factory = IndicatorFactory()
        self.registered_indicators: Dict[str, Any] = {}
        self.active_subscriptions: Dict[str, asyncio.Task] = {}
        logger.info("✅ IndicatorIntegrationFactory initialized")

    def register_indicator(self, indicator_config: IndicatorConfig) -> bool:
        """
        Enregistrer un indicateur pour intégration
        
        Args:
            indicator_config: Configuration de l'indicateur
            
        Returns:
            True si enregistrement réussi
        """
        try:
            indicator_key = f"{indicator_config.name}_{indicator_config.timeframe.value}"
            
            # Créer l'indicateur via la factory
            indicator = self.indicator_factory.create_calculator(
                indicator_config.name.lower(),
                **indicator_config.parameters
            )
            
            if not indicator:
                logger.error(f"❌ Failed to create indicator {indicator_config.name}")
                return False
            
            self.registered_indicators[indicator_key] = {
                'indicator': indicator,
                'config': indicator_config,
                'last_result': None,
                'subscription': None
            }
            
            logger.info(f"✅ Indicator registered: {indicator_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error registering indicator: {e}")
            return False

    def calculate_indicator(
        self,
        data: pd.DataFrame,
        indicator_config: IndicatorConfig
    ) -> Optional[IndicatorIntegrationResult]:
        """
        Calculer un indicateur sur des données
        
        Args:
            data: DataFrame avec OHLCV
            indicator_config: Configuration de l'indicateur
            
        Returns:
            Résultat d'intégration ou None si erreur
        """
        try:
            indicator_key = f"{indicator_config.name}_{indicator_config.timeframe.value}"
            
            if indicator_key not in self.registered_indicators:
                logger.warning(f"⚠️ Indicator not registered: {indicator_key}")
                if not self.register_indicator(indicator_config):
                    return None
            
            registered = self.registered_indicators[indicator_key]
            indicator = registered['indicator']
            
            # Calculer l'indicateur
            result = indicator.calculate(data)
            
            if not result or not result.is_valid:
                logger.warning(f"⚠️ Invalid result for {indicator_key}")
                return IndicatorIntegrationResult(
                    indicator_name=indicator_config.name,
                    data=data,
                    signals=[],
                    error="Invalid calculation result"
                )
            
            # Extraire les signaux
            signals = []
            if indicator_config.show_signals and result.signals:
                signals = [
                    {
                        'direction': s.direction.value,
                        'strength': s.strength,
                        'timestamp': s.timestamp.isoformat(),
                        'metadata': s.metadata
                    }
                    for s in result.signals
                ]
            
            # Générer les données pour le chart
            chart_data = None
            if hasattr(indicator, 'plotter'):
                try:
                    chart_fig = indicator.plotter.plot(data)
                    chart_data = {
                        'type': 'plotly',
                        'figure': chart_fig
                    }
                except Exception as e:
                    logger.warning(f"⚠️ Failed to generate chart: {e}")
            
            # Calculer les statistiques
            statistics = {
                'last_value': result.value,
                'timestamp': result.timestamp.isoformat(),
                'indicator_name': result.indicator_name,
                'period': getattr(indicator_config.parameters, 'period', None)
            }
            
            integration_result = IndicatorIntegrationResult(
                indicator_name=indicator_config.name,
                data=data,
                signals=signals,
                chart_data=chart_data,
                statistics=statistics
            )
            
            # Sauvegarder le résultat
            registered['last_result'] = integration_result
            
            logger.info(f"✅ Calculated {indicator_key}: {len(signals)} signals")
            return integration_result
            
        except Exception as e:
            logger.error(f"❌ Error calculating indicator: {e}")
            return IndicatorIntegrationResult(
                indicator_name=indicator_config.name,
                data=data,
                signals=[],
                error=str(e)
            )

    def get_last_result(
        self,
        indicator_name: str,
        timeframe: TimeFrame
    ) -> Optional[IndicatorIntegrationResult]:
        """
        Récupérer le dernier résultat calculé
        
        Args:
            indicator_name: Nom de l'indicateur
            timeframe: Timeframe
            
        Returns:
            Dernier résultat ou None
        """
        indicator_key = f"{indicator_name}_{timeframe.value}"
        registered = self.registered_indicators.get(indicator_key)
        
        if registered:
            return registered['last_result']
        return None

    def unregister_indicator(
        self,
        indicator_name: str,
        timeframe: TimeFrame
    ) -> bool:
        """
        Désenregistrer un indicateur
        
        Args:
            indicator_name: Nom de l'indicateur
            timeframe: Timeframe
            
        Returns:
            True si succès
        """
        indicator_key = f"{indicator_name}_{timeframe.value}"
        
        if indicator_key in self.registered_indicators:
            registered = self.registered_indicators[indicator_key]
            
            # Arrêter la souscription si active
            if registered['subscription']:
                registered['subscription'].cancel()
            
            del self.registered_indicators[indicator_key]
            logger.info(f"✅ Indicator unregistered: {indicator_key}")
            return True
        
        return False

    def list_registered(self) -> List[str]:
        """
        Lister tous les indicateurs enregistrés
        
        Returns:
            Liste des clés d'indicateurs
        """
        return list(self.registered_indicators.keys())

    def clear_all(self) -> None:
        """Désenregistrer tous les indicateurs"""
        for key in list(self.registered_indicators.keys()):
            registered = self.registered_indicators[key]
            if registered['subscription']:
                registered['subscription'].cancel()
        
        self.registered_indicators.clear()
        logger.info("✅ All indicators cleared")


# Instance globale
indicator_integration_factory = IndicatorIntegrationFactory()


def get_integration_factory() -> IndicatorIntegrationFactory:
    """Obtenir l'instance de factory"""
    return indicator_integration_factory
