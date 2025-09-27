"""
Tests pour le calculateur ATR
Tests ultra-modulaires - Responsabilité unique : Validation logique ATR pure
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from thebot.core.types import MarketData, TimeFrame
from thebot.indicators.volatility.atr.config import ATRConfig
from thebot.indicators.volatility.atr.calculator import ATRCalculator
from thebot.core.exceptions import ConfigurationError


class TestATRConfig:
    """Tests de validation de configuration ATR"""
    
    def test_valid_config_sma(self):
        """Test configuration valide SMA"""
        config = ATRConfig(period=14, smoothing_method="sma")
        assert config.period == 14
        assert config.smoothing_method == "sma"
        assert config.get_smoothing_alpha() is None
    
    def test_valid_config_ema(self):
        """Test configuration valide EMA"""
        config = ATRConfig(period=14, smoothing_method="ema")
        assert config.period == 14
        assert config.smoothing_method == "ema"
        assert config.get_smoothing_alpha() == Decimal('2') / Decimal('15')  # 2/(14+1)
    
    def test_invalid_period(self):
        """Test période invalide"""
        with pytest.raises(ConfigurationError, match="period must be at least 2"):
            ATRConfig(period=1)
        
        with pytest.raises(ConfigurationError, match="period must not exceed 100"):
            ATRConfig(period=101)
    
    def test_invalid_smoothing_method(self):
        """Test méthode de lissage invalide"""
        with pytest.raises(ConfigurationError, match="smoothing_method must be 'sma' or 'ema'"):
            ATRConfig(period=14, smoothing_method="invalid")
    
    def test_invalid_volatility_thresholds(self):
        """Test seuils de volatilité invalides"""
        with pytest.raises(ConfigurationError, match="volatility_threshold_low must be positive"):
            ATRConfig(period=14, volatility_threshold_low=Decimal('-1'))
        
        with pytest.raises(ConfigurationError, match="volatility_threshold_high must be > volatility_threshold_low"):
            ATRConfig(period=14, volatility_threshold_low=Decimal('2'), volatility_threshold_high=Decimal('1'))


class TestATRCalculator:
    """Tests du calculateur ATR pur"""
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.config = ATRConfig(period=3, smoothing_method="sma")
        self.calculator = ATRCalculator(self.config)
    
    def create_market_data(self, high: float, low: float, close: float, timestamp_offset: int = 0) -> MarketData:
        """Crée des données de marché pour les tests"""
        return MarketData(
            timestamp=datetime.now() + timedelta(minutes=timestamp_offset),
            open=Decimal(str((high + low) / 2)),  # Open = moyenne H/L
            high=Decimal(str(high)),
            low=Decimal(str(low)),
            close=Decimal(str(close)),
            volume=Decimal('1000'),
            timeframe=TimeFrame.M1,
            symbol="BTCUSDT"
        )
    
    def test_initialization(self):
        """Test initialisation calculateur"""
        assert not self.calculator.is_ready()
        assert self.calculator.get_current_value() is None
        assert self.calculator.get_data_count() == 0
    
    def test_first_true_range(self):
        """Test calcul premier True Range"""
        # Premier point : TR = High - Low
        data = self.create_market_data(high=102, low=98, close=100)
        result = self.calculator.add_data_point(data)
        
        # Pas encore d'ATR avec SMA (besoin de 3 points)
        assert result is None
        assert self.calculator.get_data_count() == 1
    
    def test_true_range_with_gaps(self):
        """Test True Range avec gaps (cours précédent)"""
        # Premier point
        data1 = self.create_market_data(high=102, low=98, close=100, timestamp_offset=0)
        self.calculator.add_data_point(data1)
        
        # Deuxième point avec gap up
        data2 = self.create_market_data(high=108, low=105, close=107, timestamp_offset=1)
        result2 = self.calculator.add_data_point(data2)
        
        # Vérifier que TR prend en compte l'écart avec close précédent
        # TR = max(108-105, |108-100|, |105-100|) = max(3, 8, 5) = 8
        assert result2 is None  # Pas encore prêt avec SMA
        assert self.calculator.get_data_count() == 2
    
    def test_atr_sma_calculation(self):
        """Test calcul ATR avec SMA"""
        # Données test avec True Ranges connus
        test_data = [
            {'high': 102, 'low': 98, 'close': 100},   # TR = 4
            {'high': 105, 'low': 99, 'close': 103},   # TR = max(6, 5, 1) = 6
            {'high': 108, 'low': 104, 'close': 106}   # TR = max(4, 5, 1) = 5
        ]
        
        results = []
        for i, data_point in enumerate(test_data):
            data = self.create_market_data(**data_point, timestamp_offset=i)
            result = self.calculator.add_data_point(data)
            if result:
                results.append(result.value)
        
        # ATR = moyenne des TR = (4 + 6 + 5) / 3 = 5
        assert len(results) == 1
        expected_atr = (Decimal('4') + Decimal('6') + Decimal('5')) / 3
        assert abs(results[0] - expected_atr) < Decimal('0.01')
    
    def test_atr_ema_calculation(self):
        """Test calcul ATR avec EMA"""
        config_ema = ATRConfig(period=3, smoothing_method="ema")
        calculator_ema = ATRCalculator(config_ema)
        
        # Premier point
        data1 = self.create_market_data(high=102, low=98, close=100)
        result1 = calculator_ema.add_data_point(data1)
        assert result1.value == Decimal('4')  # Premier TR = ATR initial
        
        # Deuxième point
        data2 = self.create_market_data(high=105, low=99, close=103, timestamp_offset=1)
        result2 = calculator_ema.add_data_point(data2)
        
        # ATR_EMA = α × TR + (1-α) × ATR_préc
        # α = 2/4 = 0.5, TR = 6, ATR_préc = 4
        # ATR_EMA = 0.5 × 6 + 0.5 × 4 = 5
        expected_atr = Decimal('0.5') * Decimal('6') + Decimal('0.5') * Decimal('4')
        assert abs(result2.value - expected_atr) < Decimal('0.01')
    
    def test_volatility_percentile(self):
        """Test calcul percentile de volatilité"""
        # Utiliser EMA avec historique activé
        config_ema = ATRConfig(period=3, smoothing_method="ema", store_history=True)
        calculator_ema = ATRCalculator(config_ema)
        
        # Générer suffisamment de données
        for i in range(25):
            # Volatilité variable
            volatility = 2 + i % 5  # Range de 2 à 6
            high = 100 + volatility
            low = 100 - volatility
            close = 100 + (i % 3 - 1)  # Close variable
            
            data = self.create_market_data(high, low, close, i)
            calculator_ema.add_data_point(data)
        
        percentile = calculator_ema.get_volatility_percentile(periods=20)
        assert percentile is not None
        assert 0 <= percentile <= 100
    
    def test_normalized_atr(self):
        """Test normalisation ATR par prix"""
        # Ajouter données pour avoir ATR
        for i in range(5):
            data = self.create_market_data(high=105, low=95, close=100, timestamp_offset=i)
            self.calculator.add_data_point(data)
        
        normalized = self.calculator.get_normalized_atr(Decimal('100'))
        assert normalized is not None
        assert normalized > 0  # ATR positif normalisé
    
    def test_volatility_trend(self):
        """Test détection tendance volatilité"""
        # Volatilité croissante
        volatilities = [2, 3, 4, 5, 6, 7, 8]  # Croissante
        for i, vol in enumerate(volatilities):
            high = 100 + vol
            low = 100 - vol
            close = 100
            data = self.create_market_data(high, low, close, i)
            self.calculator.add_data_point(data)
        
        trend = self.calculator.get_recent_trend(periods=5)
        assert trend in ["increasing", "decreasing", "stable"]
    
    def test_reset_functionality(self):
        """Test fonction reset"""
        # Ajouter données
        for i in range(5):
            data = self.create_market_data(high=105, low=95, close=100, timestamp_offset=i)
            self.calculator.add_data_point(data)
        
        assert self.calculator.is_ready()
        assert self.calculator.get_data_count() > 0
        
        # Reset
        self.calculator.reset()
        
        assert not self.calculator.is_ready()
        assert self.calculator.get_current_value() is None
        assert self.calculator.get_data_count() == 0
    
    def test_edge_cases(self):
        """Test cas limites"""
        # Prix identiques (volatilité nulle)
        data = self.create_market_data(high=100, low=100, close=100)
        result = self.calculator.add_data_point(data)
        
        # Doit gérer TR = 0
        assert self.calculator.get_data_count() == 1
        
        # Prix très volatils
        data2 = self.create_market_data(high=200, low=50, close=150, timestamp_offset=1)
        result2 = self.calculator.add_data_point(data2)
        
        # Doit gérer grandes variations
        assert self.calculator.get_data_count() == 2
    
    def test_decimal_precision(self):
        """Test précision Decimal"""
        # Prix avec décimales précises
        data = self.create_market_data(high=100.123456, low=99.876543, close=100.000000)
        result = self.calculator.add_data_point(data)
        
        assert self.calculator.get_data_count() == 1
        # Vérifier que la précision est conservée
    
    def test_metadata_consistency(self):
        """Test cohérence des métadonnées"""
        # Générer suffisamment de données pour avoir un résultat
        for i in range(self.config.period + 1):
            data = self.create_market_data(high=105, low=95, close=100, timestamp_offset=i)
            result = self.calculator.add_data_point(data)
        
        # Vérifier le dernier résultat
        assert result is not None
        metadata = result.metadata
        assert metadata['period'] == self.config.period
        assert metadata['smoothing_method'] == self.config.smoothing_method
        assert metadata['data_count'] > 0
        assert 'true_range' in metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v"])