"""
THEBOT - Technical Indicators Module
Module dédié pour tous les indicateurs techniques et structurels
"""

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from dash_modules.core.price_formatter import format_price_label_adaptive


class TechnicalIndicators:
    """Classe pour tous les calculs d'indicateurs techniques"""

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

    def calculate_sma(self, data: pd.Series, period: int = 20) -> pd.Series:
        """Calcule la moyenne mobile simple"""
        return data.rolling(window=period).mean()

    def calculate_ema(self, data: pd.Series, period: int = 21) -> pd.Series:
        """Calcule la moyenne mobile exponentielle"""
        return data.ewm(span=period, adjust=False).mean()

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calcule le RSI"""
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
        """Calcule l'ATR (Average True Range)"""
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
            print(f"⚠️ Erreur calcul ATR signaux: {e}")
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
        self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Dict:
        """Calcule le MACD"""
        try:
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
        except Exception as e:
            print(f"⚠️ Erreur calcul MACD: {e}")
            return {
                "macd": pd.Series([0] * len(prices), index=prices.index),
                "signal": pd.Series([0] * len(prices), index=prices.index),
                "histogram": pd.Series([0] * len(prices), index=prices.index),
            }

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
            print(f"⚠️ Erreur calcul S/R: {e}")
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
            print(f"⚠️ Erreur calcul Fibonacci: {e}")
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
            print(f"⚠️ Erreur calcul Pivots: {e}")
            return {"pivot_levels": []}

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
                    data["close"], config.get("sma_period", 20)
                )

            if config.get("ema_enabled", False):
                results["ema"] = self.calculate_ema(
                    data["close"], config.get("ema_period", 21)
                )

            if config.get("rsi_enabled", False):
                results["rsi"] = self.calculate_rsi(
                    data["close"], config.get("rsi_period", 14)
                )

            if config.get("atr_enabled", False):
                results["atr"] = self.calculate_atr_signals(
                    data, config.get("atr_period", 14)
                )

            if config.get("macd_enabled", False):
                results["macd"] = self.calculate_macd(
                    data["close"],
                    config.get("macd_fast", 12),
                    config.get("macd_slow", 26),
                    config.get("macd_signal", 9),
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
            print(f"❌ Erreur calcul indicateurs: {e}")

        return results


# Instance globale pour l'utilisation dans les modules
technical_indicators = TechnicalIndicators()
