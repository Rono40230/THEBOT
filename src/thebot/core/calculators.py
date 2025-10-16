"""
Calculators Module - THEBOT Dash
Calculs d'indicateurs techniques via IndicatorFactory unifiée
"""

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

# Import de la factory unifiée
try:
    from thebot.indicators.factory import get_indicator_factory
    _indicator_factory = get_indicator_factory()
    FACTORY_AVAILABLE = True
except ImportError as e:
    # Supprimer le warning pour éviter le spam dans les tests
    _indicator_factory = None
    FACTORY_AVAILABLE = False


class TechnicalCalculators:
    """Calculateurs d'indicateurs techniques - Maintenant utilise IndicatorFactory"""

    def __init__(self):
        self.factory_available = FACTORY_AVAILABLE

    def calculate_sma(self, prices: List[float], period: int = 20) -> List[float]:
        """Calculer Simple Moving Average via IndicatorFactory"""
        if self.factory_available:
            return _indicator_factory.calculate_sma(prices, period=period)
        else:
            # Fallback pandas simple
            return pd.Series(prices).rolling(window=period).mean().fillna(0).tolist()

    def calculate_ema(self, prices: List[float], period: int = 12) -> List[float]:
        """Calculer Exponential Moving Average via IndicatorFactory"""
        if self.factory_available:
            return _indicator_factory.calculate_ema(prices, period=period)
        else:
            # Fallback pandas simple
            return pd.Series(prices).ewm(span=period).mean().fillna(0).tolist()

    def calculate_rsi(self, prices: List[float], period: int = 14) -> List[float]:
        """Calculer Relative Strength Index via IndicatorFactory"""
        if self.factory_available:
            return _indicator_factory.calculate_rsi(prices, period=period)
        else:
            # Fallback pandas simple
            if len(prices) < period + 1:
                return [50.0] * len(prices)

            series = pd.Series(prices)
            delta = series.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.fillna(50).tolist()

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

    def calculate_rsi_signals(
        self,
        prices: List[float],
        period: int = 14,
        overbought: float = 70,
        oversold: float = 30,
    ) -> Dict[str, List]:
        """
        Calculer les signaux RSI avec détection de patterns avancés

        Returns:
            Dict contenant les signaux RSI détaillés
        """
        if len(prices) < period + 10:  # Besoin de données suffisantes
            return {
                "rsi_values": [50.0] * len(prices),
                "signals": ["neutral"] * len(prices),
                "signal_strength": [0.0] * len(prices),
                "overbought_signals": [False] * len(prices),
                "oversold_signals": [False] * len(prices),
                "divergence_signals": [False] * len(prices),
                "crossover_signals": ["none"] * len(prices),
                "signal_descriptions": [""] * len(prices),
            }

        # Calcul RSI
        rsi_values = self.calculate_rsi(prices, period)
        prices_series = pd.Series(prices)
        rsi_series = pd.Series(rsi_values)

        # Initialisation des signaux
        signals = ["neutral"] * len(prices)
        signal_strength = [0.0] * len(prices)
        overbought_signals = [False] * len(prices)
        oversold_signals = [False] * len(prices)
        divergence_signals = [False] * len(prices)
        crossover_signals = ["none"] * len(prices)
        signal_descriptions = [""] * len(prices)

        for i in range(period + 5, len(prices)):
            current_rsi = rsi_values[i]
            prev_rsi = rsi_values[i - 1]
            current_price = prices[i]
            prev_price = prices[i - 1]

            # 1. Signaux de surachat/survente
            if current_rsi >= overbought:
                if prev_rsi < overbought:  # Entrée en zone de surachat
                    overbought_signals[i] = True
                    signals[i] = "sell"
                    signal_strength[i] = min(
                        1.0, (current_rsi - overbought) / (100 - overbought)
                    )
                    signal_descriptions[i] = f"🔴 RSI Surachat ({current_rsi:.1f})"

            elif current_rsi <= oversold:
                if prev_rsi > oversold:  # Entrée en zone de survente
                    oversold_signals[i] = True
                    signals[i] = "buy"
                    signal_strength[i] = min(1.0, (oversold - current_rsi) / oversold)
                    signal_descriptions[i] = f"🟢 RSI Survente ({current_rsi:.1f})"

            # 2. Croisements de niveau 50 (ligne médiane)
            if prev_rsi <= 50 and current_rsi > 50:
                crossover_signals[i] = "bullish_50"
                if signals[i] == "neutral":
                    signals[i] = "buy"
                    signal_strength[i] = 0.3
                    signal_descriptions[i] = f"📈 RSI > 50 ({current_rsi:.1f})"

            elif prev_rsi >= 50 and current_rsi < 50:
                crossover_signals[i] = "bearish_50"
                if signals[i] == "neutral":
                    signals[i] = "sell"
                    signal_strength[i] = 0.3
                    signal_descriptions[i] = f"📉 RSI < 50 ({current_rsi:.1f})"

            # 3. Détection de divergences (simplifiée)
            if i >= period + 10:
                # Recherche de pics et creux récents
                rsi_window = rsi_series[i - 10 : i + 1]
                price_window = prices_series[i - 10 : i + 1]

                # Divergence haussière : prix fait un creux plus bas, RSI fait un creux plus haut
                if (
                    current_price == price_window.min()
                    and current_rsi > rsi_window.min()
                    and current_rsi < 40
                ):
                    divergence_signals[i] = True
                    signals[i] = "buy"
                    signal_strength[i] = 0.8
                    signal_descriptions[i] = f"🔄 Divergence Haussière RSI"

                # Divergence baissière : prix fait un pic plus haut, RSI fait un pic plus bas
                elif (
                    current_price == price_window.max()
                    and current_rsi < rsi_window.max()
                    and current_rsi > 60
                ):
                    divergence_signals[i] = True
                    signals[i] = "sell"
                    signal_strength[i] = 0.8
                    signal_descriptions[i] = f"🔄 Divergence Baissière RSI"

            # 4. Signaux de retournement extrême
            if current_rsi >= 85:  # RSI très élevé
                signals[i] = "strong_sell"
                signal_strength[i] = 1.0
                signal_descriptions[i] = f"🔴 RSI Extrême ({current_rsi:.1f})"

            elif current_rsi <= 15:  # RSI très bas
                signals[i] = "strong_buy"
                signal_strength[i] = 1.0
                signal_descriptions[i] = f"🟢 RSI Extrême ({current_rsi:.1f})"

        return {
            "rsi_values": rsi_values,
            "signals": signals,
            "signal_strength": signal_strength,
            "overbought_signals": overbought_signals,
            "oversold_signals": oversold_signals,
            "divergence_signals": divergence_signals,
            "crossover_signals": crossover_signals,
            "signal_descriptions": signal_descriptions,
        }

    def calculate_atr(
        self,
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int = 14,
    ) -> List[float]:
        """Calculer Average True Range via IndicatorFactory"""
        if self.factory_available:
            return _indicator_factory.calculate_atr((highs, lows, closes), period=period)
        else:
            # Fallback direct
            if len(closes) < period + 1:
                return [0.0] * len(closes)

            high_series = pd.Series(highs)
            low_series = pd.Series(lows)
            close_series = pd.Series(closes)
            prev_close = close_series.shift(1)
            tr1 = high_series - low_series
            tr2 = np.abs(high_series - prev_close)
            tr3 = np.abs(low_series - prev_close)
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean()
            return atr.fillna(0).tolist()

    def calculate_atr_signals(
        self,
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int = 14,
        multiplier: float = 2.0,
    ) -> Dict[str, any]:
        """Calculer ATR avec signaux de volatilité et tendance"""

        if len(closes) < period + 1:
            return {
                "atr": [0.0] * len(closes),
                "atr_ma": [0.0] * len(closes),
                "upper_threshold": [0.0] * len(closes),
                "lower_threshold": [0.0] * len(closes),
                "volatility_signals": [],
                "trend_signals": [],
                "expansion_signals": [],
                "contraction_signals": [],
            }

        # Calcul ATR de base
        atr_values = self.calculate_atr(highs, lows, closes, period)
        atr_series = pd.Series(atr_values)

        # Moyenne mobile de l'ATR pour détecter les tendances de volatilité
        atr_ma = atr_series.rolling(window=period // 2).mean()

        # Seuils FIXES basés sur la moyenne globale de l'ATR
        atr_global_mean = atr_series[period:].mean()  # Moyenne globale (sans NaN)
        atr_global_std = atr_series[period:].std()  # Écart-type global

        # Seuils fixes et horizontaux
        upper_threshold_value = atr_global_mean + (
            atr_global_std * multiplier
        )  # Seuil haute volatilité
        lower_threshold_value = max(
            0, atr_global_mean - (atr_global_std * multiplier / 2)
        )  # Seuil basse volatilité (min 0)

        # Créer des séries constantes pour les seuils
        upper_threshold = pd.Series([upper_threshold_value] * len(atr_values))
        lower_threshold = pd.Series([lower_threshold_value] * len(atr_values))

        # Détection des signaux
        volatility_signals = []
        trend_signals = []
        expansion_signals = []
        contraction_signals = []

        for i in range(1, len(atr_values)):
            if i < period:
                continue

            current_atr = atr_values[i]
            prev_atr = atr_values[i - 1]
            current_ma = atr_ma.iloc[i] if not pd.isna(atr_ma.iloc[i]) else 0
            prev_ma = atr_ma.iloc[i - 1] if not pd.isna(atr_ma.iloc[i - 1]) else 0

            # Signal de haute volatilité (croisement vers le haut du seuil fixe)
            if (
                current_atr > upper_threshold_value
                and prev_atr <= upper_threshold_value
            ):
                volatility_signals.append(
                    {
                        "index": i,
                        "type": "high_volatility",
                        "value": current_atr,
                        "threshold": upper_threshold_value,
                        "description": "Volatilité élevée détectée",
                    }
                )

            # Signal de basse volatilité (croisement vers le bas du seuil fixe)
            elif (
                current_atr < lower_threshold_value
                and prev_atr >= lower_threshold_value
            ):
                volatility_signals.append(
                    {
                        "index": i,
                        "type": "low_volatility",
                        "value": current_atr,
                        "threshold": lower_threshold_value,
                        "description": "Volatilité faible détectée",
                    }
                )

            # Tendance de volatilité croissante
            if current_ma > prev_ma and prev_ma > 0:
                if current_ma / prev_ma > 1.1:  # 10% d'augmentation
                    trend_signals.append(
                        {
                            "index": i,
                            "type": "volatility_increasing",
                            "value": current_atr,
                            "ma_value": current_ma,
                            "description": "Tendance de volatilité croissante",
                        }
                    )

            # Tendance de volatilité décroissante
            elif current_ma < prev_ma and prev_ma > 0:
                if current_ma / prev_ma < 0.9:  # 10% de diminution
                    trend_signals.append(
                        {
                            "index": i,
                            "type": "volatility_decreasing",
                            "value": current_atr,
                            "ma_value": current_ma,
                            "description": "Tendance de volatilité décroissante",
                        }
                    )

            # Expansion de volatilité (forte augmentation soudaine)
            if current_atr > prev_atr * 1.5:  # 50% d'augmentation
                expansion_signals.append(
                    {
                        "index": i,
                        "type": "volatility_expansion",
                        "value": current_atr,
                        "previous": prev_atr,
                        "ratio": current_atr / prev_atr,
                        "description": f"Expansion volatilité: +{((current_atr/prev_atr-1)*100):.1f}%",
                    }
                )

            # Contraction de volatilité (forte diminution soudaine)
            elif current_atr < prev_atr * 0.7:  # 30% de diminution
                contraction_signals.append(
                    {
                        "index": i,
                        "type": "volatility_contraction",
                        "value": current_atr,
                        "previous": prev_atr,
                        "ratio": current_atr / prev_atr,
                        "description": f"Contraction volatilité: {((current_atr/prev_atr-1)*100):.1f}%",
                    }
                )

        return {
            "atr": atr_values,
            "atr_ma": atr_ma.fillna(0).tolist(),
            "upper_threshold": upper_threshold.fillna(0).tolist(),
            "lower_threshold": lower_threshold.fillna(0).tolist(),
            "volatility_signals": volatility_signals,
            "trend_signals": trend_signals,
            "expansion_signals": expansion_signals,
            "contraction_signals": contraction_signals,
        }

    def calculate_bollinger_bands(
        self, prices: List[float], period: int = 20, std_dev: float = 2.0
    ) -> Dict[str, List[float]]:
        """Calculer Bollinger Bands"""

        series = pd.Series(prices)
        sma = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()

        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)

        return {
            "upper": upper_band.fillna(0).tolist(),
            "middle": sma.fillna(0).tolist(),
            "lower": lower_band.fillna(0).tolist(),
        }

    def calculate_stochastic(
        self,
        highs: List[float],
        lows: List[float],
        closes: List[float],
        k_period: int = 14,
        d_period: int = 3,
    ) -> Dict[str, List[float]]:
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

        return {"k": k_percent.fillna(50).tolist(), "d": d_percent.fillna(50).tolist()}


# Instance globale
calculator = TechnicalCalculators()
