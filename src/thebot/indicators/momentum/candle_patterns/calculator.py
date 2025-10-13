"""
Candle Patterns Calculator
Translation from NonoBot Rust implementation
"""

from collections import deque
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from ....core.types import MarketData
from .config import CandlePatternsConfig


class PatternType(Enum):
    DOJI = "doji"
    HAMMER = "hammer"
    SHOOTING_STAR = "shooting_star"
    BULLISH_ENGULFING = "bullish_engulfing"
    BEARISH_ENGULFING = "bearish_engulfing"
    NONE = "none"


class CandlePatternsCalculator:
    """
    Candle Patterns calculation engine

    NonoBot logic:
    - Analyze candle body/wick ratios
    - Detect classic patterns
    - Calculate pattern strength
    """

    def __init__(self, config: CandlePatternsConfig):
        self.config = config
        self.data_history: deque = deque(maxlen=10)

    def add_data(self, data: MarketData) -> None:
        self.data_history.append(data)

    def calculate_candle_metrics(self, data: MarketData) -> Dict[str, Decimal]:
        """Calculate basic candle metrics"""
        body_size = abs(data.close - data.open)
        total_range = data.high - data.low
        upper_wick = data.high - max(data.open, data.close)
        lower_wick = min(data.open, data.close) - data.low

        body_ratio = body_size / total_range if total_range > 0 else Decimal("0")
        upper_wick_ratio = upper_wick / total_range if total_range > 0 else Decimal("0")
        lower_wick_ratio = lower_wick / total_range if total_range > 0 else Decimal("0")

        return {
            "body_size": body_size,
            "total_range": total_range,
            "body_ratio": body_ratio,
            "upper_wick_ratio": upper_wick_ratio,
            "lower_wick_ratio": lower_wick_ratio,
            "is_bullish": data.close > data.open,
        }

    def detect_doji(self, metrics: Dict[str, Decimal]) -> bool:
        """Detect Doji pattern"""
        return metrics["body_ratio"] <= self.config.doji_threshold

    def detect_hammer(self, metrics: Dict[str, Decimal]) -> bool:
        """Detect Hammer pattern"""
        return (
            metrics["lower_wick_ratio"]
            >= self.config.wick_ratio_threshold * metrics["body_ratio"]
            and metrics["upper_wick_ratio"] <= metrics["body_ratio"]
            and metrics["body_ratio"] >= self.config.min_body_ratio
        )

    def detect_shooting_star(self, metrics: Dict[str, Decimal]) -> bool:
        """Detect Shooting Star pattern"""
        return (
            metrics["upper_wick_ratio"]
            >= self.config.wick_ratio_threshold * metrics["body_ratio"]
            and metrics["lower_wick_ratio"] <= metrics["body_ratio"]
            and metrics["body_ratio"] >= self.config.min_body_ratio
        )

    def detect_engulfing(self) -> Optional[PatternType]:
        """Detect Engulfing patterns"""
        if len(self.data_history) < 2:
            return None

        prev_candle = list(self.data_history)[-2]
        curr_candle = list(self.data_history)[-1]

        prev_metrics = self.calculate_candle_metrics(prev_candle)
        curr_metrics = self.calculate_candle_metrics(curr_candle)

        # Bullish Engulfing
        if (
            not prev_metrics["is_bullish"]
            and curr_metrics["is_bullish"]
            and curr_candle.open < prev_candle.close
            and curr_candle.close > prev_candle.open
        ):
            return PatternType.BULLISH_ENGULFING

        # Bearish Engulfing
        if (
            prev_metrics["is_bullish"]
            and not curr_metrics["is_bullish"]
            and curr_candle.open > prev_candle.close
            and curr_candle.close < prev_candle.open
        ):
            return PatternType.BEARISH_ENGULFING

        return None

    def calculate_from_data(self, data: MarketData) -> Optional[Dict[str, Any]]:
        """Calculate patterns for new data point"""
        self.add_data(data)

        if len(self.data_history) < 1:
            return None

        metrics = self.calculate_candle_metrics(data)

        # Detect patterns
        pattern = PatternType.NONE
        strength = Decimal("0.0")

        if self.detect_doji(metrics):
            pattern = PatternType.DOJI
            strength = Decimal("1.0") - metrics["body_ratio"]
        elif self.detect_hammer(metrics):
            pattern = PatternType.HAMMER
            strength = metrics["lower_wick_ratio"]
        elif self.detect_shooting_star(metrics):
            pattern = PatternType.SHOOTING_STAR
            strength = metrics["upper_wick_ratio"]
        else:
            engulfing = self.detect_engulfing()
            if engulfing:
                pattern = engulfing
                strength = metrics["body_ratio"]

        return {
            "pattern": pattern,
            "strength": strength,
            "metrics": metrics,
            "is_bullish_pattern": pattern
            in [PatternType.HAMMER, PatternType.BULLISH_ENGULFING],
            "is_bearish_pattern": pattern
            in [PatternType.SHOOTING_STAR, PatternType.BEARISH_ENGULFING],
            "is_neutral_pattern": pattern == PatternType.DOJI,
        }
