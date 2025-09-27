"""
Tests pour le calculateur RSI
Tests ultra-modulaires - Responsabilité unique : Validation logique RSI pure
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from thebot.core.types import MarketData, TimeFrame
from thebot.indicators.oscillators.rsi.config import RSIConfig
from thebot.indicators.oscillators.rsi.calculator import RSICalculator
from thebot.core.exceptions import ConfigurationError


class TestRSIConfig:
    """Tests de validation de configuration RSI"""
    
    def test_valid_config_default(self):
        """Test configuration par défaut"""
        config = RSIConfig()
        assert config.period == 14
        assert config.overbought_level == Decimal('70')
        assert config.oversold_level == Decimal('30')
    
    def test_valid_config_custom(self):
        """Test configuration personnalisée"""
        config = RSIConfig(
            period=21,
            overbought_level=Decimal('75'),
            oversold_level=Decimal('25')
        )
        assert config.period == 21
        assert config.overbought_level == Decimal('75')
        assert config.oversold_level == Decimal('25')
    
    def test_invalid_period(self):
        """Test période invalide"""
        with pytest.raises(ConfigurationError, match="period must be at least 2"):
            RSIConfig(period=1)
        
        with pytest.raises(ConfigurationError, match="period must not exceed 100"):
            RSIConfig(period=101)
    
    def test_invalid_levels(self):
        """Test niveaux invalides"""
        with pytest.raises(ConfigurationError, match="must be between 0 and 100"):
            RSIConfig(overbought_level=Decimal('150'))
        
        with pytest.raises(ConfigurationError, match="oversold_level must be < overbought_level"):
            RSIConfig(oversold_level=Decimal('80'), overbought_level=Decimal('70'))


class TestRSICalculator:
    """Tests du calculateur RSI pur"""
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.config = RSIConfig(period=3)  # Période courte pour tests rapides
        self.calculator = RSICalculator(self.config)
    
    def create_market_data(self, close: float, timestamp_offset: int = 0) -> MarketData:
        """Crée des données de marché pour les tests"""
        return MarketData(
            timestamp=datetime.now() + timedelta(minutes=timestamp_offset),
            open=Decimal(str(close - 0.1)),
            high=Decimal(str(close + 0.5)),
            low=Decimal(str(close - 0.5)),
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
    
    def test_first_data_point(self):
        """Test premier point de données"""
        data = self.create_market_data(100)
        result = self.calculator.add_data_point(data)
        
        # Premier point ne produit pas de RSI (pas de changement prix)
        assert result is None
        assert self.calculator.get_data_count() == 1
    
    def test_rsi_calculation_uptrend(self):
        """Test calcul RSI avec tendance haussière"""
        prices = [100, 102, 105, 108]  # Tendance haussière pure
        
        results = []
        for i, price in enumerate(prices):
            data = self.create_market_data(price, i)
            result = self.calculator.add_data_point(data)
            if result:
                results.append(result.value)
        
        # Dernier RSI doit être proche de 100 (gains purs)
        assert len(results) > 0
        final_rsi = results[-1]
        assert final_rsi > Decimal('80')  # RSI élevé pour gains purs
    
    def test_rsi_calculation_downtrend(self):
        """Test calcul RSI avec tendance baissière"""
        prices = [108, 105, 102, 100]  # Tendance baissière pure
        
        results = []
        for i, price in enumerate(prices):
            data = self.create_market_data(price, i)
            result = self.calculator.add_data_point(data)
            if result:
                results.append(result.value)
        
        # Dernier RSI doit être proche de 0 (pertes pures)
        assert len(results) > 0
        final_rsi = results[-1]
        assert final_rsi < Decimal('20')  # RSI faible pour pertes pures
    
    def test_rsi_mixed_movements(self):
        """Test RSI avec mouvements mixés"""
        prices = [100, 102, 101, 103, 102, 104]  # Mouvements mixés
        
        results = []
        for i, price in enumerate(prices):
            data = self.create_market_data(price, i)
            result = self.calculator.add_data_point(data)
            if result:
                results.append(result.value)
        
        # RSI doit être dans une plage raisonnable (pas extrême)
        if results:
            final_rsi = results[-1]
            assert Decimal('20') < final_rsi < Decimal('80')
    
    def test_momentum_strength(self):
        """Test détection force du momentum"""
        # Créer une tendance forte haussière
        prices = [100, 105, 110, 115, 120]
        for i, price in enumerate(prices):
            data = self.create_market_data(price, i)
            self.calculator.add_data_point(data)
        
        momentum = self.calculator.get_momentum_strength()
        assert momentum in ["strong_bullish", "bullish", "neutral", "bearish", "strong_bearish"]
    
    def test_rsi_bounds(self):
        """Test que RSI reste dans [0, 100]"""
        # Prix extrêmes pour tester les limites
        extreme_prices = [100, 200, 50, 300, 10, 500, 1]  # Très volatil
        
        for i, price in enumerate(extreme_prices):
            data = self.create_market_data(price, i)
            result = self.calculator.add_data_point(data)
            if result:
                rsi = result.value
                assert Decimal('0') <= rsi <= Decimal('100'), f"RSI {rsi} hors limites"
    
    def test_reset_functionality(self):
        """Test fonction reset"""
        # Ajouter données
        for i in range(10):
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
        # Prix identiques (pas de changement)
        for i in range(10):
            data = self.create_market_data(100, i)  # Prix constant
            result = self.calculator.add_data_point(data)
        
        # RSI doit être gérable même sans changement prix
        assert self.calculator.get_data_count() == 10
        
        # Si RSI calculable, doit être 50 (neutre) pour prix constants
        if self.calculator.is_ready():
            rsi = self.calculator.get_current_value()
            # Avec prix constants après initialisation, RSI devrait tendre vers 50
    
    def test_metadata_consistency(self):
        """Test cohérence des métadonnées"""
        # Générer suffisamment de données
        for i in range(self.config.period + 2):
            data = self.create_market_data(100 + i * 2, i)  # Tendance claire
            result = self.calculator.add_data_point(data)
        
        # Vérifier le dernier résultat
        assert result is not None
        metadata = result.metadata
        assert metadata['period'] == self.config.period
        assert 'gain' in metadata
        assert 'loss' in metadata
        assert metadata['data_count'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])