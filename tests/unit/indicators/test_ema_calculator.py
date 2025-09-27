"""
Tests pour le calculateur EMA
Tests ultra-modulaires - Responsabilité unique : Validation logique EMA pure
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from thebot.core.types import MarketData, TimeFrame
from thebot.indicators.basic.ema.config import EMAConfig
from thebot.indicators.basic.ema.calculator import EMACalculator
from thebot.core.exceptions import ConfigurationError


class TestEMAConfig:
    """Tests de validation de configuration EMA"""
    
    def test_valid_config(self):
        """Test configuration valide"""
        config = EMAConfig(period=10)
        assert config.period == 10
        assert config.smoothing_factor == Decimal('2') / (Decimal('10') + 1)  # 2/11
        assert config.enable_signals is True
    
    def test_custom_smoothing_factor(self):
        """Test facteur de lissage personnalisé"""
        config = EMAConfig(period=10, smoothing_factor=Decimal('0.2'))
        assert config.smoothing_factor == Decimal('0.2')
        assert config.get_one_minus_alpha() == Decimal('0.8')
    
    def test_invalid_period(self):
        """Test période invalide"""
        with pytest.raises(ConfigurationError, match="period must be at least 2"):
            EMAConfig(period=1)
        
        with pytest.raises(ConfigurationError, match="period must not exceed 200"):
            EMAConfig(period=201)
    
    def test_invalid_smoothing_factor(self):
        """Test facteur de lissage invalide"""
        with pytest.raises(ConfigurationError, match="smoothing_factor must be between 0 and 1"):
            EMAConfig(period=10, smoothing_factor=Decimal('1.5'))
        
        with pytest.raises(ConfigurationError, match="smoothing_factor must be between 0 and 1"):
            EMAConfig(period=10, smoothing_factor=Decimal('0'))


class TestEMACalculator:
    """Tests du calculateur EMA pur"""
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.config = EMAConfig(period=3)
        self.calculator = EMACalculator(self.config)
    
    def create_market_data(self, price: float, timestamp_offset: int = 0) -> MarketData:
        """Crée des données de marché pour les tests"""
        return MarketData(
            timestamp=datetime.now() + timedelta(minutes=timestamp_offset),
            open=Decimal(str(price - 0.5)),
            high=Decimal(str(price + 1)),
            low=Decimal(str(price - 1)),
            close=Decimal(str(price)),
            volume=Decimal('1000'),
            timeframe=TimeFrame.M1,
            symbol="BTCUSDT"
        )
    
    def test_initialization(self):
        """Test initialisation calculateur"""
        assert not self.calculator.is_ready()
        assert self.calculator.get_current_value() is None
        assert self.calculator.get_data_count() == 0
        assert self.calculator.alpha == Decimal('2') / (Decimal('3') + 1)  # 0.5
    
    def test_first_data_point(self):
        """Test premier point de données"""
        data = self.create_market_data(100)
        result = self.calculator.add_data_point(data)
        
        assert result is not None
        assert result.value == Decimal('100')  # Premier point = prix
        assert self.calculator.is_ready()
        assert self.calculator.get_data_count() == 1
    
    def test_ema_calculation_sequence(self):
        """Test séquence de calcul EMA"""
        prices = [100, 102, 105, 103]
        expected_emas = []
        
        # Calcul manuel EMA avec α=0.5
        ema = Decimal('100')  # Premier point
        expected_emas.append(ema)
        
        for price in prices[1:]:
            ema = Decimal('0.5') * Decimal(str(price)) + Decimal('0.5') * ema
            expected_emas.append(ema)
        
        # Test avec calculateur
        calculated_emas = []
        for i, price in enumerate(prices):
            data = self.create_market_data(price, i)
            result = self.calculator.add_data_point(data)
            calculated_emas.append(result.value)
        
        # Vérification avec tolérance pour erreurs de précision
        for i, (expected, calculated) in enumerate(zip(expected_emas, calculated_emas)):
            assert abs(expected - calculated) < Decimal('0.0001'), \
                f"Point {i}: expected {expected}, got {calculated}"
    
    def test_ema_convergence(self):
        """Test convergence EMA vers prix stable"""
        stable_price = 100
        config = EMAConfig(period=10)  # α = 2/11 ≈ 0.18
        calculator = EMACalculator(config)
        
        # Ajouter beaucoup de points au même prix
        for i in range(50):
            data = self.create_market_data(stable_price, i)
            result = calculator.add_data_point(data)
        
        # EMA doit converger vers le prix stable
        final_ema = calculator.get_current_value()
        assert abs(final_ema - Decimal(str(stable_price))) < Decimal('0.1')
    
    def test_ema_responsiveness(self):
        """Test réactivité EMA vs période"""
        prices = [100, 110, 120]  # Forte hausse
        
        # EMA courte (α élevé = plus réactif)
        config_fast = EMAConfig(period=2)  # α = 2/3 ≈ 0.67
        calc_fast = EMACalculator(config_fast)
        
        # EMA longue (α faible = moins réactif)
        config_slow = EMAConfig(period=20)  # α = 2/21 ≈ 0.095
        calc_slow = EMACalculator(config_slow)
        
        for i, price in enumerate(prices):
            data = self.create_market_data(price, i)
            result_fast = calc_fast.add_data_point(data)
            result_slow = calc_slow.add_data_point(data)
        
        # EMA rapide doit être plus proche du prix final
        final_price = Decimal('120')
        fast_distance = abs(calc_fast.get_current_value() - final_price)
        slow_distance = abs(calc_slow.get_current_value() - final_price)
        
        assert fast_distance < slow_distance, \
            f"EMA rapide ({fast_distance}) doit être plus proche que EMA lente ({slow_distance})"
    
    def test_trend_slope_calculation(self):
        """Test calcul de pente de tendance"""
        # Tendance haussière
        prices = [100, 101, 102, 103, 104]
        for i, price in enumerate(prices):
            data = self.create_market_data(price, i)
            self.calculator.add_data_point(data)
        
        slope = self.calculator.get_trend_slope(periods=3)
        assert slope is not None
        assert slope > 0, "Pente doit être positive pour tendance haussière"
    
    def test_volatility_calculation(self):
        """Test calcul de volatilité"""
        # Prix volatils
        prices = [100, 105, 95, 110, 90, 115, 85]
        for i, price in enumerate(prices):
            data = self.create_market_data(price, i)
            self.calculator.add_data_point(data)
        
        volatility = self.calculator.get_volatility(periods=5)
        assert volatility is not None
        assert volatility > 0, "Volatilité doit être positive pour prix volatils"
    
    def test_reset_functionality(self):
        """Test fonction reset"""
        # Ajouter des données
        for i in range(5):
            data = self.create_market_data(100 + i, i)
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
        # Prix négatifs (crypto ne peut pas mais test robustesse)
        data = self.create_market_data(-10)
        result = self.calculator.add_data_point(data)
        assert result is not None
        assert result.value == Decimal('-10')
        
        # Prix très élevé
        data = self.create_market_data(1000000)
        result = self.calculator.add_data_point(data)
        assert result is not None
    
    def test_decimal_precision(self):
        """Test précision Decimal"""
        # Prix avec beaucoup de décimales
        precise_price = 100.123456789
        data = self.create_market_data(precise_price)
        result = self.calculator.add_data_point(data)
        
        # Vérifier que la précision est conservée
        assert str(result.value) == "100.123456789"
    
    def test_metadata_consistency(self):
        """Test cohérence des métadonnées"""
        data = self.create_market_data(100)
        result = self.calculator.add_data_point(data)
        
        metadata = result.metadata
        assert metadata['period'] == self.config.period
        assert metadata['alpha'] == float(self.calculator.alpha)
        assert metadata['data_count'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])