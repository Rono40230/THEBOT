"""
Configuration pour l'indicateur MACD
Moving Average Convergence Divergence - Architecture modulaire THEBOT
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from decimal import Decimal


@dataclass
class MACDConfig:
    """Configuration validée pour l'indicateur MACD"""
    
    # Paramètres de calcul
    fast_period: int = 12
    slow_period: int = 26
    signal_period: int = 9
    source: str = "close"
    
    # Paramètres visuels
    macd_color: str = "#2196F3"
    signal_color: str = "#FF5722"
    histogram_enabled: bool = True
    histogram_positive_color: str = "#4CAF50"
    histogram_negative_color: str = "#F44336"
    line_width: int = 2
    
    # Paramètres avancés
    enable_signals: bool = True
    zero_line_sensitivity: Decimal = field(default_factory=lambda: Decimal('0.001'))
    zero_line_enabled: bool = True
    crossover_signals: bool = True
    
    def __post_init__(self):
        """Validation après initialisation"""
        self._validate_periods()
        self._validate_source()
        self._validate_line_width()
    
    def _validate_periods(self):
        """Valide les périodes"""
        if self.fast_period <= 0:
            raise ValueError(f"fast_period doit être > 0, reçu: {self.fast_period}")
        if self.slow_period <= 0:
            raise ValueError(f"slow_period doit être > 0, reçu: {self.slow_period}")
        if self.signal_period <= 0:
            raise ValueError(f"signal_period doit être > 0, reçu: {self.signal_period}")
        if self.fast_period >= self.slow_period:
            raise ValueError(f"fast_period ({self.fast_period}) doit être < slow_period ({self.slow_period})")
    
    def _validate_source(self):
        """Valide la source de prix"""
        valid_sources = ["open", "high", "low", "close", "typical", "weighted"]
        if self.source not in valid_sources:
            raise ValueError(f"source doit être parmi {valid_sources}, reçu: {self.source}")
    
    def _validate_line_width(self):
        """Valide l'épaisseur de ligne"""
        if not (1 <= self.line_width <= 5):
            raise ValueError(f"line_width doit être entre 1 et 5, reçu: {self.line_width}")
    
    def get_trading_style_config(self, style: str) -> "MACDConfig":
        """Retourne la configuration optimisée pour un style de trading"""
        configs = {
            "scalping": {
                "fast_period": 8,
                "slow_period": 21,
                "signal_period": 5,
                "crossover_signals": True
            },
            "day_trading": {
                "fast_period": 12,
                "slow_period": 26,
                "signal_period": 9,
                "crossover_signals": True
            },
            "swing_trading": {
                "fast_period": 12,
                "slow_period": 30,
                "signal_period": 12,
                "crossover_signals": False
            },
            "position_trading": {
                "fast_period": 15,
                "slow_period": 35,
                "signal_period": 15,
                "crossover_signals": False
            }
        }
        
        if style in configs:
            # Créer une nouvelle instance avec les paramètres modifiés
            config_dict = self.__dict__.copy()
            config_dict.update(configs[style])
            return MACDConfig(**config_dict)
        
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "fast_period": self.fast_period,
            "slow_period": self.slow_period,
            "signal_period": self.signal_period,
            "source": self.source,
            "macd_color": self.macd_color,
            "signal_color": self.signal_color,
            "histogram_enabled": self.histogram_enabled,
            "histogram_positive_color": self.histogram_positive_color,
            "histogram_negative_color": self.histogram_negative_color,
            "line_width": self.line_width,
            "enable_signals": self.enable_signals,
            "zero_line_enabled": self.zero_line_enabled,
            "crossover_signals": self.crossover_signals
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MACDConfig":
        """Crée depuis un dictionnaire"""
        # Filtrer les clés valides
        valid_keys = {
            'fast_period', 'slow_period', 'signal_period', 'source',
            'macd_color', 'signal_color', 'histogram_enabled',
            'histogram_positive_color', 'histogram_negative_color',
            'line_width', 'enable_signals', 'zero_line_enabled', 'crossover_signals'
        }
        
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)
    use_decimal: bool = True
    store_history: bool = True
    
    def __post_init__(self):
        """Validation automatique des paramètres"""
        self.validate()
    
    def validate(self) -> None:
        """Validation complète des paramètres MACD"""
        
        # Validation périodes
        periods = ['fast_period', 'slow_period', 'signal_period']
        for period_name in periods:
            period_value = getattr(self, period_name)
            if not isinstance(period_value, int):
                raise ConfigurationError(f"{period_name} must be an integer")
            
            if period_value < 2:
                raise ConfigurationError(f"{period_name} must be at least 2")
            
            if period_value > 200:
                raise ConfigurationError(f"{period_name} must not exceed 200")
        
        # Validation cohérence des périodes
        if self.fast_period >= self.slow_period:
            raise ConfigurationError("fast_period must be < slow_period")
        
        # Validation sensibilité
        if not isinstance(self.zero_line_sensitivity, Decimal):
            try:
                self.zero_line_sensitivity = Decimal(str(self.zero_line_sensitivity))
            except (ValueError, TypeError):
                raise ConfigurationError("zero_line_sensitivity must be convertible to Decimal")
        
        if self.zero_line_sensitivity <= 0:
            raise ConfigurationError("zero_line_sensitivity must be positive")
    
    def to_dict(self) -> dict:
        """Export configuration vers dictionnaire"""
        return {
            'fast_period': self.fast_period,
            'slow_period': self.slow_period,
            'signal_period': self.signal_period,
            'enable_signals': self.enable_signals,
            'zero_line_sensitivity': float(self.zero_line_sensitivity),
            'use_decimal': self.use_decimal,
            'store_history': self.store_history
        }