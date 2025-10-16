"""
Module MACD (Moving Average Convergence Divergence)
Orchestration et API publique selon architecture modulaire THEBOT
"""

import logging
from typing import Dict, Optional, Tuple

import pandas as pd

from ....core.logger import logger
from .calculator import MACDCalculator
from .config import MACDConfig
from .plotter import MACDPlotter


class MACD:
    """
    API publique pour l'indicateur MACD.

    Pattern Factory + Facade pour orchestrer config, calcul et visualisation.
    """

    def __init__(self, config: Optional[MACDConfig] = None):
        """
        Initialise l'indicateur MACD.

        Args:
            config: Configuration optionnelle (défaut: configuration standard)
        """
        self.config = config or MACDConfig()
        self.calculator = MACDCalculator(self.config)
        self.plotter = MACDPlotter(self.config)

        logger.debug(
            f"MACD initialisé: {self.config.fast_period}/{self.config.slow_period}/{self.config.signal_period}"
        )

    def calculate(
        self, data: pd.DataFrame, include_signals: bool = True
    ) -> Dict[str, any]:
        """
        Calcule MACD complet avec signaux optionnels.

        Args:
            data: DataFrame avec colonnes OHLCV
            include_signals: Inclure les signaux de trading

        Returns:
            Dict avec 'data', 'signals', 'info'
        """
        try:
            # Calcul principal
            macd_data = self.calculator.calculate(data)

            result = {"data": macd_data, "info": self.calculator.get_calculation_info()}

            # Signaux optionnels
            if include_signals:
                signals = self.calculator.calculate_signals(macd_data)
                result["signals"] = signals

            logger.debug(f"MACD calculé: {len(macd_data['macd'])} points")
            return result

        except Exception as e:
            logger.error(f"Erreur calcul MACD: {e}")
            raise

    def plot(
        self, data: pd.DataFrame, include_signals: bool = True, title: str = "MACD"
    ) -> any:
        """
        Crée le graphique MACD complet.

        Args:
            data: DataFrame avec colonnes OHLCV
            include_signals: Afficher les signaux
            title: Titre du graphique

        Returns:
            Figure Plotly
        """
        try:
            # Calculer données
            result = self.calculate(data, include_signals)

            # Créer graphique
            signals = result.get("signals") if include_signals else None
            figure = self.plotter.create_subplot_figure(result["data"], signals, title)

            return figure

        except Exception as e:
            logger.error(f"Erreur plot MACD: {e}")
            raise

    def get_latest_signal(self, data: pd.DataFrame) -> Optional[Dict[str, any]]:
        """
        Retourne le dernier signal généré.

        Args:
            data: DataFrame avec colonnes OHLCV

        Returns:
            Dict avec détails du signal ou None
        """
        try:
            result = self.calculate(data, include_signals=True)
            signals = result["signals"]

            # Chercher le dernier signal non-hold
            latest_signals = signals[signals["signal_type"] != "hold"]

            if latest_signals.empty:
                return None

            latest = latest_signals.iloc[-1]
            macd_value = result["data"]["macd"].iloc[-1]
            signal_value = result["data"]["signal"].iloc[-1]

            return {
                "timestamp": latest.name,
                "signal_type": latest["signal_type"],
                "strength": latest["strength"],
                "macd_value": macd_value,
                "signal_value": signal_value,
                "histogram": macd_value - signal_value,
            }

        except Exception as e:
            logger.warning(f"Erreur récupération signal MACD: {e}")
            return None

    def update_config(self, **kwargs):
        """
        Met à jour la configuration dynamiquement.

        Args:
            **kwargs: Paramètres à modifier
        """
        # Créer nouvelle config avec paramètres modifiés
        from dataclasses import asdict
        config_dict = asdict(self.config)
        config_dict.update(kwargs)

        self.config = MACDConfig(**config_dict)
        self.calculator = MACDCalculator(self.config)
        self.plotter = MACDPlotter(self.config)

        logger.debug(f"Configuration MACD mise à jour: {kwargs}")

    def get_trading_recommendation(self, data: pd.DataFrame) -> Dict[str, any]:
        """
        Analyse complète pour recommandation trading.

        Args:
            data: DataFrame avec colonnes OHLCV

        Returns:
            Dict avec recommandation détaillée
        """
        try:
            result = self.calculate(data, include_signals=True)
            latest_signal = self.get_latest_signal(data)

            macd_current = result["data"]["macd"].iloc[-1]
            signal_current = result["data"]["signal"].iloc[-1]
            histogram_current = result["data"]["histogram"].iloc[-1]

            # Analyse tendance
            macd_trend = "haussière" if macd_current > signal_current else "baissière"
            momentum = "forte" if abs(histogram_current) > 0.01 else "faible"

            # Recommandation
            if latest_signal and latest_signal["signal_type"] == "buy":
                recommendation = "ACHAT"
                confidence = min(latest_signal["strength"] * 100, 95)
            elif latest_signal and latest_signal["signal_type"] == "sell":
                recommendation = "VENTE"
                confidence = min(latest_signal["strength"] * 100, 95)
            else:
                recommendation = "ATTENDRE"
                confidence = 50

            return {
                "recommendation": recommendation,
                "confidence": confidence,
                "trend": macd_trend,
                "momentum": momentum,
                "latest_signal": latest_signal,
                "current_values": {
                    "macd": macd_current,
                    "signal": signal_current,
                    "histogram": histogram_current,
                },
            }

        except Exception as e:
            logger.error(f"Erreur recommandation MACD: {e}")
            return {"recommendation": "ERREUR", "confidence": 0, "error": str(e)}


# Factory functions pour les styles de trading courants
def create_scalping_macd() -> MACD:
    """MACD optimisé pour scalping (8/21/5)"""
    config = MACDConfig(fast_period=8, slow_period=21, signal_period=5)
    return MACD(config)


def create_daytrading_macd() -> MACD:
    """MACD standard pour day trading (12/26/9)"""
    config = MACDConfig(fast_period=12, slow_period=26, signal_period=9)
    return MACD(config)


def create_swing_macd() -> MACD:
    """MACD pour swing trading (12/30/12)"""
    config = MACDConfig(fast_period=12, slow_period=30, signal_period=12)
    return MACD(config)


def create_position_macd() -> MACD:
    """MACD pour position trading (15/35/15)"""
    config = MACDConfig(fast_period=15, slow_period=35, signal_period=15)
    return MACD(config)


# Export API publique
__all__ = [
    "MACD",
    "MACDConfig",
    "MACDCalculator",
    "MACDPlotter",
    "create_scalping_macd",
    "create_daytrading_macd",
    "create_swing_macd",
    "create_position_macd",
]
