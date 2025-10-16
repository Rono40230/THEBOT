from src.thebot.core.logger import logger
"""
THEBOT - Technical Indicators Module
Module dédié pour tous les indicateurs techniques et structurels
Utilise maintenant l'IndicatorFactory unifiée pour éviter les duplications
"""

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from dash_modules.core.price_formatter import format_price_label_adaptive

# Import de la factory unifiée
try:
    from src.thebot.indicators.factory import get_indicator_factory
    _indicator_factory = get_indicator_factory()
    FACTORY_AVAILABLE = True
except ImportError:
    _indicator_factory = None
    FACTORY_AVAILABLE = False


class TechnicalIndicators:
    """Classe pour tous les calculs d'indicateurs techniques - Maintenant utilise IndicatorFactory"""

    def __init__(self):
        self.default_periods = {
            "sma": 20,
            "ema": 21,
            "rsi": 14,
            "atr": 14,
            "macd_fast": 12,
            "macd_slow": 26,
            "macd_signal": 9,
        }

    # === INDICATEURS DE BASE ===

    def calculate_sma(self, data: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calcule la moyenne mobile simple via IndicatorFactory"""
        if FACTORY_AVAILABLE:
            result = _indicator_factory.calculate_sma(data, period=period)
            return result
        else:
            # Fallback direct (code original)
            return data['close'].rolling(window=period).mean()

    def calculate_ema(self, data: pd.DataFrame, period: int = 21) -> pd.Series:
        """Calcule la moyenne mobile exponentielle via IndicatorFactory"""
        if FACTORY_AVAILABLE:
            result = _indicator_factory.calculate_ema(data, period=period)
            return result
        else:
            # Fallback direct
            return data['close'].ewm(span=period).mean()

    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calcule le RSI via IndicatorFactory"""
        if FACTORY_AVAILABLE:
            result = _indicator_factory.calculate_rsi(data, period=period)
            return result
        else:
            # Fallback direct
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        if FACTORY_AVAILABLE:
            result = _indicator_factory.calculate_ema(data, period=period)
            return pd.Series(result, index=data.index)
        else:
            # Fallback direct (code original)
            return data.ewm(span=period, adjust=False).mean()

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calcule le RSI via IndicatorFactory"""
        if FACTORY_AVAILABLE:
            result = _indicator_factory.calculate_rsi(prices, period=period)
            return pd.Series(result, index=prices.index)
        else:
            # Fallback direct (code original)
            try:
                delta = prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                return rsi
            except:
                return pd.Series([50] * len(prices), index=prices.index)

    def calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calcule l'ATR (Average True Range) via IndicatorFactory"""
        if FACTORY_AVAILABLE:
            return _indicator_factory.calculate_atr(data, period=period)
        else:
            # Fallback direct (code original)
            try:
                high_low = data["high"] - data["low"]
                high_close = np.abs(data["high"] - data["close"].shift())
                low_close = np.abs(data["low"] - data["close"].shift())
                ranges = pd.concat([high_low, high_close, low_close], axis=1)
                true_range = ranges.max(axis=1)
                atr = true_range.rolling(period).mean()
                return atr
            except:
                return pd.Series([1] * len(data), index=data.index)

    def calculate_atr_signals(
        self, data: pd.DataFrame, period: int = 14, multiplier: float = 2.0
    ) -> Dict:
        """Calcule l'ATR avec signaux de volatilité"""
        try:
            atr = self.calculate_atr(data, period)
            atr_ma = atr.rolling(window=period // 2).mean()

            upper_threshold = atr * (1 + multiplier)
            lower_threshold = atr * (1 - multiplier / 2)

            # Signaux de volatilité
            expansion_signals = []
            contraction_signals = []

            for i in range(1, len(atr)):
                if atr.iloc[i] > upper_threshold.iloc[i]:
                    expansion_signals.append(
                        {
                            "index": i,
                            "timestamp": atr.index[i],
                            "value": atr.iloc[i],
                            "type": "expansion",
                        }
                    )
                elif atr.iloc[i] < lower_threshold.iloc[i]:
                    contraction_signals.append(
                        {
                            "index": i,
                            "timestamp": atr.index[i],
                            "value": atr.iloc[i],
                            "type": "contraction",
                        }
                    )

            return {
                "atr": atr.tolist(),
                "atr_ma": atr_ma.tolist(),
                "upper_threshold": upper_threshold.tolist(),
                "lower_threshold": lower_threshold.tolist(),
                "volatility_signals": expansion_signals + contraction_signals,
                "trend_signals": [],
                "expansion_signals": expansion_signals,
                "contraction_signals": contraction_signals,
            }
        except Exception as e:
            logger.info(f"⚠️ Erreur calcul ATR signaux: {e}")
            return {
                "atr": [1] * len(data),
                "atr_ma": [1] * len(data),
                "upper_threshold": [2] * len(data),
                "lower_threshold": [0.5] * len(data),
                "volatility_signals": [],
                "trend_signals": [],
                "expansion_signals": [],
                "contraction_signals": [],
            }

    def calculate_macd(
        self, data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Dict:
        """Calcule le MACD via IndicatorFactory"""
        if FACTORY_AVAILABLE:
            result = _indicator_factory.calculate_macd(data, fast_period=fast, slow_period=slow, signal_period=signal)
            return result
        else:
            # Fallback direct
            prices = data['close']
            # EMA rapide et lente
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()

            # Ligne MACD
            macd_line = ema_fast - ema_slow

            # Ligne de signal (EMA du MACD)
            signal_line = macd_line.ewm(span=signal).mean()

            # Histogramme (MACD - Signal)
            histogram = macd_line - signal_line

            return {"macd": macd_line, "signal": signal_line, "histogram": histogram}

    # === INDICATEURS STRUCTURELS ===

    def calculate_support_resistance(
        self,
        data: pd.DataFrame,
        strength: int = 2,
        lookback: int = 50,
        support_color: str = "#27AE60",
        resistance_color: str = "#E74C3C",
        line_style: str = "solid",
        line_width: int = 2,
    ) -> Dict:
        """Calcule les niveaux de support et résistance"""
        try:
            if len(data) < lookback:
                return {"support_levels": [], "resistance_levels": []}

            recent_data = data.tail(lookback)
            current_price = data["close"].iloc[-1]

            support_levels = []
            resistance_levels = []

            # Recherche de niveaux basée sur les minima/maxima locaux
            window = 10
            for i in range(window, len(recent_data) - window):
                price_window = recent_data["close"].iloc[i - window : i + window + 1]
                current_val = recent_data["close"].iloc[i]

                # Support (minimum local)
                if current_val == price_window.min() and current_val < current_price:
                    support_levels.append(
                        {
                            "y": current_val,
                            "strength": strength,
                            "label": f"S: {format_price_label_adaptive(current_val)}",
                            "color": support_color,
                            "line_width": line_width,
                            "line_dash": line_style,
                        }
                    )

                # Résistance (maximum local)
                if current_val == price_window.max() and current_val > current_price:
                    resistance_levels.append(
                        {
                            "y": current_val,
                            "strength": strength,
                            "label": f"R: {format_price_label_adaptive(current_val)}",
                            "color": resistance_color,
                            "line_width": line_width,
                            "line_dash": line_style,
                        }
                    )

            # Limiter le nombre de niveaux et éliminer les doublons
            support_levels = sorted(
                support_levels, key=lambda x: abs(x["y"] - current_price)
            )[:5]
            resistance_levels = sorted(
                resistance_levels, key=lambda x: abs(x["y"] - current_price)
            )[:5]

            return {
                "support_levels": support_levels,
                "resistance_levels": resistance_levels,
            }

        except Exception as e:
            logger.info(f"⚠️ Erreur calcul S/R: {e}")
            return {"support_levels": [], "resistance_levels": []}

    def calculate_fibonacci_retracements(
        self,
        data: pd.DataFrame,
        min_swing_pct: float = 2.0,
        line_style: str = "dashed",
        line_width: int = 1,
        transparency: float = 0.8,
    ) -> Dict:
        """Calcule les retracements de Fibonacci"""
        try:
            if len(data) < 50:
                return {"retracement_levels": [], "extension_levels": []}

            # Trouver le swing high et low récents
            recent_data = data.tail(100)
            swing_high = recent_data["high"].max()
            swing_low = recent_data["low"].min()

            # Vérifier que le swing est assez grand
            swing_size = (swing_high - swing_low) / swing_low * 100
            if swing_size < min_swing_pct:
                return {"retracement_levels": [], "extension_levels": []}

            # Ratios de Fibonacci
            fib_ratios = [0.236, 0.382, 0.5, 0.618, 0.786]
            extension_ratios = [1.272, 1.414, 1.618]

            fib_colors = {
                0.236: "#FFE4B5",
                0.382: "#FFA500",
                0.5: "#FF6347",
                0.618: "#DC143C",
                0.786: "#8B0000",
                1.272: "#9370DB",
                1.414: "#8A2BE2",
                1.618: "#4B0082",
            }

            retracement_levels = []
            extension_levels = []

            # Calculer les retracements
            for ratio in fib_ratios:
                fib_price = swing_high - (swing_high - swing_low) * ratio
                retracement_levels.append(
                    {
                        "y": fib_price,
                        "ratio": ratio,
                        "label": f"Fib {ratio:.1%}: {format_price_label_adaptive(fib_price)}",
                        "color": fib_colors.get(ratio, "#888888"),
                        "line_width": line_width
                        + (1 if ratio in [0.382, 0.5, 0.618] else 0),
                        "line_dash": line_style,
                    }
                )

            # Calculer les extensions
            for ratio in extension_ratios:
                ext_price = swing_high + (swing_high - swing_low) * (ratio - 1.0)
                extension_levels.append(
                    {
                        "y": ext_price,
                        "ratio": ratio,
                        "label": f"Ext {ratio:.1%}: {format_price_label_adaptive(ext_price)}",
                        "color": fib_colors.get(ratio, "#888888"),
                        "line_width": line_width,
                        "line_dash": line_style,
                    }
                )

            return {
                "retracement_levels": retracement_levels,
                "extension_levels": extension_levels,
            }

        except Exception as e:
            logger.info(f"⚠️ Erreur calcul Fibonacci: {e}")
            return {"retracement_levels": [], "extension_levels": []}

    def calculate_pivot_points(
        self,
        data: pd.DataFrame,
        method: str = "standard",
        line_style: str = "dot",
        line_width: int = 2,
    ) -> Dict:
        """Calcule les points pivots"""
        try:
            if len(data) < 2:
                return {"pivot_levels": []}

            # Utiliser les données de la période précédente
            prev_data = data.iloc[-24:] if len(data) >= 24 else data

            high = prev_data["high"].max()
            low = prev_data["low"].min()
            close = prev_data["close"].iloc[-1]

            levels = []

            if method == "standard":
                # Pivot Points standard
                pp = (high + low + close) / 3
                r1 = 2 * pp - low
                s1 = 2 * pp - high
                r2 = pp + (high - low)
                s2 = pp - (high - low)
                r3 = high + 2 * (pp - low)
                s3 = low - 2 * (high - pp)

                pivot_data = [
                    (pp, "PP", "#FFFF00", line_width + 1),
                    (r1, "R1", "#FF6B6B", line_width),
                    (s1, "S1", "#4ECDC4", line_width),
                    (r2, "R2", "#FF8E8E", max(1, line_width - 1)),
                    (s2, "S2", "#7EDDD8", max(1, line_width - 1)),
                    (r3, "R3", "#FFB3B3", max(1, line_width - 1)),
                    (s3, "S3", "#AFEEED", max(1, line_width - 1)),
                ]

            elif method == "fibonacci":
                # Pivot Points Fibonacci
                pp = (high + low + close) / 3
                range_hl = high - low

                pivot_data = [
                    (pp, "PP", "#FFFF00", line_width + 1),
                    (pp + 0.382 * range_hl, "R1", "#FF6B6B", line_width),
                    (pp - 0.382 * range_hl, "S1", "#4ECDC4", line_width),
                    (pp + 0.618 * range_hl, "R2", "#FF8E8E", max(1, line_width - 1)),
                    (pp - 0.618 * range_hl, "S2", "#7EDDD8", max(1, line_width - 1)),
                    (pp + 1.000 * range_hl, "R3", "#FFB3B3", max(1, line_width - 1)),
                    (pp - 1.000 * range_hl, "S3", "#AFEEED", max(1, line_width - 1)),
                ]

            else:  # camarilla
                # Pivot Points Camarilla
                pivot_data = [
                    (close, "PP", "#FFFF00", line_width + 1),
                    (close + (high - low) * 1.1 / 12, "R1", "#FF6B6B", line_width),
                    (close - (high - low) * 1.1 / 12, "S1", "#4ECDC4", line_width),
                    (
                        close + (high - low) * 1.1 / 6,
                        "R2",
                        "#FF8E8E",
                        max(1, line_width - 1),
                    ),
                    (
                        close - (high - low) * 1.1 / 6,
                        "S2",
                        "#7EDDD8",
                        max(1, line_width - 1),
                    ),
                    (
                        close + (high - low) * 1.1 / 4,
                        "R3",
                        "#FFB3B3",
                        max(1, line_width - 1),
                    ),
                    (
                        close - (high - low) * 1.1 / 4,
                        "S3",
                        "#AFEEED",
                        max(1, line_width - 1),
                    ),
                ]

            for price, name, color, width in pivot_data:
                levels.append(
                    {
                        "y": price,
                        "label": f"{name}: {format_price_label_adaptive(price)}",
                        "color": color,
                        "line_width": width,
                        "line_dash": line_style,
                        "level_type": (
                            "pivot"
                            if name == "PP"
                            else ("support" if name.startswith("S") else "resistance")
                        ),
                        "touches": 0,
                    }
                )

            return {"pivot_levels": levels}

        except Exception as e:
            logger.info(f"⚠️ Erreur calcul Pivots: {e}")
            return {"pivot_levels": []}

    # === NOUVEAUX INDICATEURS AVANCÉS ===

    def calculate_supertrend(self, data: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> pd.DataFrame:
        """Calcule SuperTrend via IndicatorFactory"""
        if FACTORY_AVAILABLE:
            return _indicator_factory.calculate_supertrend(data, period=period, multiplier=multiplier)
        else:
            # Fallback simple
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
                    direction_values.append(1)
            
            return pd.DataFrame({
                'supertrend': supertrend_values,
                'direction': direction_values
            }, index=data.index)

    def calculate_breakout(self, data: pd.DataFrame, period: int = 20, breakout_threshold: float = 2.0) -> pd.Series:
        """Calcule Breakout via IndicatorFactory"""
        if FACTORY_AVAILABLE:
            return _indicator_factory.calculate_breakout(data, period=period, breakout_threshold=breakout_threshold)
        else:
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
        """Calcule Squeeze via IndicatorFactory"""
        if FACTORY_AVAILABLE:
            return _indicator_factory.calculate_squeeze(data, bb_period=bb_period, kc_period=kc_period,
                                                       bb_multiplier=bb_multiplier, kc_multiplier=kc_multiplier)
        else:
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
        """Calcule OBV via IndicatorFactory"""
        if FACTORY_AVAILABLE:
            return _indicator_factory.calculate_obv(data)
        else:
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

    def calculate_support_resistance(self, data: pd.DataFrame, lookback: int = 50) -> Dict[str, List[float]]:
        """Calcule Support et Résistance via IndicatorFactory"""
        if FACTORY_AVAILABLE:
            return _indicator_factory.calculate_support_resistance(data, lookback=lookback)
        else:
            # Fallback simple
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

    def calculate_pivot_points(self, high: float, low: float, close: float) -> Dict[str, float]:
        """Calcule Pivot Points via IndicatorFactory"""
        if FACTORY_AVAILABLE:
            return _indicator_factory.calculate_pivot_points(high, low, close)
        else:
            # Fallback simple
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

    # === MÉTHODE PRINCIPALE ===

    def calculate_all_indicators(
        self, data: pd.DataFrame, config: Dict[str, Any]
    ) -> Dict:
        """Calcule tous les indicateurs selon la configuration"""
        results = {}

        if data.empty:
            return results

        try:
            # Indicateurs de base
            if config.get("sma_enabled", False):
                results["sma"] = self.calculate_sma(
                    data, config.get("sma_period", 20)
                )

            if config.get("ema_enabled", False):
                results["ema"] = self.calculate_ema(
                    data, config.get("ema_period", 21)
                )

            if config.get("rsi_enabled", False):
                results["rsi"] = self.calculate_rsi(
                    data, config.get("rsi_period", 14)
                )

            if config.get("atr_enabled", False):
                results["atr"] = self.calculate_atr_signals(
                    data, config.get("atr_period", 14)
                )

            if config.get("macd_enabled", False):
                results["macd"] = self.calculate_macd(
                    data,
                    config.get("macd_fast", 12),
                    config.get("macd_slow", 26),
                    config.get("macd_signal", 9),
                )

            # Nouveaux indicateurs avancés
            if config.get("supertrend_enabled", False):
                results["supertrend"] = self.calculate_supertrend(
                    data, 
                    period=config.get("supertrend_period", 10),
                    multiplier=config.get("supertrend_multiplier", 3.0)
                )

            if config.get("breakout_enabled", False):
                results["breakout"] = self.calculate_breakout(
                    data,
                    period=config.get("breakout_period", 20),
                    breakout_threshold=config.get("breakout_threshold", 2.0)
                )

            if config.get("squeeze_enabled", False):
                results["squeeze"] = self.calculate_squeeze(
                    data,
                    bb_period=config.get("squeeze_bb_period", 20),
                    kc_period=config.get("squeeze_kc_period", 20),
                    bb_multiplier=config.get("squeeze_bb_multiplier", 2.0),
                    kc_multiplier=config.get("squeeze_kc_multiplier", 1.5)
                )

            if config.get("obv_enabled", False):
                results["obv"] = self.calculate_obv(data)

            if config.get("volume_profile_enabled", False):
                results["volume_profile"] = self.calculate_volume_profile(
                    data, bins=config.get("volume_profile_bins", 50)
                )

            # Indicateurs structurels
            if config.get("sr_enabled", False):
                results["support_resistance"] = self.calculate_support_resistance(
                    data,
                    strength=config.get("sr_strength", 2),
                    lookback=config.get("sr_lookback", 50),
                    support_color=config.get("sr_support_color", "#27AE60"),
                    resistance_color=config.get("sr_resistance_color", "#E74C3C"),
                    line_style=config.get("sr_line_style", "solid"),
                    line_width=config.get("sr_line_width", 2),
                )

            if config.get("fibonacci_enabled", False):
                results["fibonacci"] = self.calculate_fibonacci_retracements(
                    data,
                    min_swing_pct=config.get("fibonacci_swing", 2),
                    line_style=config.get("fibonacci_line_style", "dashed"),
                    line_width=config.get("fibonacci_line_width", 1),
                    transparency=config.get("fibonacci_transparency", 0.8),
                )

            if config.get("pivot_enabled", False):
                results["pivot_points"] = self.calculate_pivot_points(
                    data,
                    method=config.get("pivot_method", "standard"),
                    line_style=config.get("pivot_line_style", "dot"),
                    line_width=config.get("pivot_line_width", 2),
                )

        except Exception as e:
            logger.info(f"❌ Erreur calcul indicateurs: {e}")

        return results

    # === NOUVEAUX INDICATEURS VIA FACTORY ===

    def calculate_supertrend(self, data: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> pd.DataFrame:
        """Calcule le SuperTrend via IndicatorFactory"""
        if FACTORY_AVAILABLE:
            return _indicator_factory.calculate_supertrend(data, period=period, multiplier=multiplier)
        else:
            # Fallback simple
            return pd.DataFrame({"supertrend": [0] * len(data), "direction": [0] * len(data)}, index=data.index)

    def calculate_breakout(self, data: pd.DataFrame, period: int = 20, breakout_threshold: float = 2.0) -> pd.Series:
        """Calcule les signaux de breakout via IndicatorFactory"""
        if FACTORY_AVAILABLE:
            return _indicator_factory.calculate_breakout(data, period=period, breakout_threshold=breakout_threshold)
        else:
            # Fallback simple
            return pd.Series([0] * len(data), index=data.index)

    def calculate_squeeze(self, data: pd.DataFrame, bb_period: int = 20, kc_period: int = 20, 
                          bb_multiplier: float = 2.0, kc_multiplier: float = 1.5) -> pd.Series:
        """Calcule le Squeeze Momentum via IndicatorFactory"""
        if FACTORY_AVAILABLE:
            return _indicator_factory.calculate_squeeze(data, bb_period=bb_period, kc_period=kc_period,
                                                       bb_multiplier=bb_multiplier, kc_multiplier=kc_multiplier)
        else:
            # Fallback simple
            return pd.Series([0] * len(data), index=data.index)

    def calculate_obv(self, data: pd.DataFrame) -> pd.Series:
        """Calcule l'On Balance Volume via IndicatorFactory"""
        if FACTORY_AVAILABLE:
            return _indicator_factory.calculate_obv(data)
        else:
            # Fallback simple
            return pd.Series([0] * len(data), index=data.index)

    def calculate_volume_profile(self, data: pd.DataFrame, bins: int = 50) -> Dict:
        """Calcule le Volume Profile via IndicatorFactory"""
        if FACTORY_AVAILABLE:
            return _indicator_factory.calculate_volume_profile(data, bins=bins)
        else:
            # Fallback simple
            return {"volume_profile": [0] * bins, "price_levels": [0] * bins}

    def calculate_fibonacci_levels(self, high: float, low: float) -> Dict[str, float]:
        """Calcule les niveaux de Fibonacci via IndicatorFactory"""
        if FACTORY_AVAILABLE:
            return _indicator_factory.calculate_fibonacci(high, low)
        else:
            # Fallback simple
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


# Instance globale pour l'utilisation dans les modules
technical_indicators = TechnicalIndicators()
