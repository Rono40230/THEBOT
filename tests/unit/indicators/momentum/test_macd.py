"""
Tests unitaires pour l'indicateur MACD
Validation complète selon architecture modulaire THEBOT
"""

import pytest
import pandas as pd
import numpy as np
from decimal import Decimal

from src.thebot.indicators.momentum.macd import MACD, MACDConfig
from src.thebot.indicators.momentum.macd.calculator import MACDCalculator
from src.thebot.indicators.momentum.macd.plotter import MACDPlotter


class TestMACDConfig:
    """Tests de configuration MACD"""
    
    def test_default_config(self):
        """Test configuration par défaut"""
        config = MACDConfig()
        assert config.fast_period == 12
        assert config.slow_period == 26
        assert config.signal_period == 9
        assert config.source == "close"
        assert config.histogram_enabled == True
    
    def test_config_validation(self):
        """Test validation des paramètres"""
        # Test période valide
        config = MACDConfig(fast_period=8, slow_period=21, signal_period=5)
        assert config.fast_period < config.slow_period
        
        # Test période invalide
        with pytest.raises(ValueError):
            MACDConfig(fast_period=26, slow_period=12)  # fast >= slow
    
    def test_trading_styles(self):
        """Test configurations par style de trading"""
        config = MACDConfig()
        
        scalping = config.get_trading_style_config("scalping")
        assert scalping.fast_period == 8
        assert scalping.slow_period == 21
        assert scalping.signal_period == 5
        
        day_trading = config.get_trading_style_config("day_trading")
        assert day_trading.fast_period == 12
        assert day_trading.slow_period == 26


class TestMACDCalculator:
    """Tests du calculateur MACD"""
    
    @pytest.fixture
    def sample_data(self):
        """Données de test OHLCV"""
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        
        # Simulation prix avec tendance
        base_price = 100
        returns = np.random.normal(0.001, 0.02, 100)
        prices = [base_price]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        return pd.DataFrame({
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
    
    def test_calculator_init(self):
        """Test initialisation calculateur"""
        config = MACDConfig()
        calculator = MACDCalculator(config)
        assert calculator.config == config
    
    def test_macd_calculation(self, sample_data):
        """Test calcul MACD standard"""
        config = MACDConfig(fast_period=12, slow_period=26, signal_period=9)
        calculator = MACDCalculator(config)
        
        result = calculator.calculate(sample_data)
        
        assert 'macd' in result
        assert 'signal' in result
        assert 'histogram' in result
        
        # Vérifier longueurs
        assert len(result['macd']) == len(sample_data)
        assert len(result['signal']) == len(sample_data)
        assert len(result['histogram']) == len(sample_data)
        
        # Vérifier que histogramme = macd - signal
        histogram_calc = result['macd'] - result['signal']
        pd.testing.assert_series_equal(result['histogram'], histogram_calc)
    
    def test_signals_calculation(self, sample_data):
        """Test calcul des signaux"""
        config = MACDConfig()
        calculator = MACDCalculator(config)
        
        macd_data = calculator.calculate(sample_data)
        signals = calculator.calculate_signals(macd_data)
        
        assert 'signal_type' in signals.columns
        assert 'strength' in signals.columns
        assert len(signals) == len(sample_data)
        
        # Vérifier types de signaux
        signal_types = signals['signal_type'].unique()
        valid_types = ['buy', 'sell', 'hold']
        assert all(sig in valid_types for sig in signal_types)
    
    def test_insufficient_data(self):
        """Test avec données insuffisantes"""
        config = MACDConfig()
        calculator = MACDCalculator(config)
        
        # Données trop courtes
        short_data = pd.DataFrame({
            'open': [100, 101],
            'high': [105, 106],
            'low': [99, 100],
            'close': [104, 105],
            'volume': [1000, 1100]
        })
        
        with pytest.raises(Exception):  # ValidationError attendue
            calculator.calculate(short_data)


class TestMACDPlotter:
    """Tests du visualiseur MACD"""
    
    @pytest.fixture
    def sample_macd_data(self):
        """Données MACD de test"""
        dates = pd.date_range('2023-01-01', periods=50, freq='D')
        
        return {
            'macd': pd.Series(np.random.normal(0, 0.5, 50), index=dates),
            'signal': pd.Series(np.random.normal(0, 0.3, 50), index=dates),
            'histogram': pd.Series(np.random.normal(0, 0.2, 50), index=dates)
        }
    
    def test_plotter_init(self):
        """Test initialisation plotter"""
        config = MACDConfig()
        plotter = MACDPlotter(config)
        assert plotter.config == config
    
    def test_figure_creation(self, sample_macd_data):
        """Test création figure"""
        config = MACDConfig()
        plotter = MACDPlotter(config)
        
        fig = plotter.create_subplot_figure(sample_macd_data)
        
        assert fig is not None
        assert len(fig.data) > 0  # Au moins une trace
        
        # Vérifier que les traces contiennent les bonnes données
        trace_names = [trace.name for trace in fig.data]
        assert 'MACD' in trace_names
        assert 'Signal' in trace_names


class TestMACDIntegration:
    """Tests d'intégration MACD complet"""
    
    @pytest.fixture
    def btc_sample_data(self):
        """Simulation données BTC réalistes"""
        dates = pd.date_range('2023-01-01', periods=200, freq='H')
        np.random.seed(42)
        
        # Simulation prix BTC avec volatilité réaliste
        base_price = 45000
        returns = np.random.normal(0.0001, 0.03, 200)
        prices = [base_price]
        
        for ret in returns[1:]:
            # Ajouter volatilité réaliste crypto
            noise = np.random.normal(1, 0.02)
            prices.append(prices[-1] * (1 + ret) * noise)
        
        return pd.DataFrame({
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.015))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.015))) for p in prices],
            'close': prices,
            'volume': np.random.randint(100, 1000, 200)
        }, index=dates)
    
    def test_full_macd_workflow(self, btc_sample_data):
        """Test workflow complet MACD"""
        macd = MACD()
        
        # Calcul complet
        result = macd.calculate(btc_sample_data, include_signals=True)
        
        assert 'data' in result
        assert 'signals' in result
        assert 'info' in result
        
        # Vérifier info
        info = result['info']
        assert info['indicator'] == 'MACD'
        assert info['fast_period'] == 12
        assert info['slow_period'] == 26
        
        # Test graphique
        fig = macd.plot(btc_sample_data)
        assert fig is not None
    
    def test_latest_signal(self, btc_sample_data):
        """Test récupération dernier signal"""
        macd = MACD()
        
        signal = macd.get_latest_signal(btc_sample_data)
        
        if signal:  # Signal peut être None si aucun crossover
            assert 'signal_type' in signal
            assert 'strength' in signal
            assert 'timestamp' in signal
            assert signal['signal_type'] in ['buy', 'sell']
    
    def test_trading_recommendation(self, btc_sample_data):
        """Test recommandation trading"""
        macd = MACD()
        
        recommendation = macd.get_trading_recommendation(btc_sample_data)
        
        assert 'recommendation' in recommendation
        assert 'confidence' in recommendation
        assert 'trend' in recommendation
        assert recommendation['recommendation'] in ['ACHAT', 'VENTE', 'ATTENDRE']
        assert 0 <= recommendation['confidence'] <= 100
    
    def test_config_update(self):
        """Test mise à jour configuration"""
        macd = MACD()
        original_fast = macd.config.fast_period
        
        macd.update_config(fast_period=8, slow_period=21)
        
        assert macd.config.fast_period == 8
        assert macd.config.slow_period == 21
        assert macd.config.fast_period != original_fast


class TestMACDFactories:
    """Tests des factory functions"""
    
    def test_scalping_factory(self):
        """Test factory scalping"""
        from src.thebot.indicators.momentum.macd import create_scalping_macd
        
        macd = create_scalping_macd()
        assert macd.config.fast_period == 8
        assert macd.config.slow_period == 21
        assert macd.config.signal_period == 5
    
    def test_daytrading_factory(self):
        """Test factory day trading"""
        from src.thebot.indicators.momentum.macd import create_daytrading_macd
        
        macd = create_daytrading_macd()
        assert macd.config.fast_period == 12
        assert macd.config.slow_period == 26
        assert macd.config.signal_period == 9
    
    def test_all_factories(self):
        """Test toutes les factories"""
        from src.thebot.indicators.momentum.macd import (
            create_scalping_macd, create_daytrading_macd,
            create_swing_macd, create_position_macd
        )
        
        factories = [
            create_scalping_macd,
            create_daytrading_macd,
            create_swing_macd,
            create_position_macd
        ]
        
        for factory in factories:
            macd = factory()
            assert isinstance(macd, MACD)
            assert macd.config.fast_period < macd.config.slow_period


if __name__ == "__main__":
    pytest.main([__file__, "-v"])