"""
Tests pour le composant TopPerformers
"""

import pytest

from dash_modules.components.top_performers import TopPerformersComponent


class TestTopPerformers:
    """Tests pour TopPerformersComponent"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.performers = TopPerformersComponent()

    def test_initialization(self):
        """Test initialisation du composant"""
        assert self.performers is not None
        assert hasattr(self.performers, 'cache_duration')
        assert hasattr(self.performers, 'last_update')
        assert hasattr(self.performers, 'cache')

    def test_calculate_correlations_empty(self):
        """Test calcul corrélations sans données"""
        result = self.performers.calculate_correlations()
        assert isinstance(result, dict)
        assert 'correlation_matrix' in result
        assert 'market_leaders' in result

    def test_create_performance_widget(self):
        """Test création du widget performance"""
        widget = self.performers.create_performance_widget("test-performers")
        assert widget is not None
        assert hasattr(widget, 'children')

    def test_calculate_performance_score(self):
        """Test calcul score performance"""
        coin_data = {
            'price_change_percentage_24h': 3.5,
            'total_volume': 1000000,
            'market_cap': 50000000
        }
        score = self.performers._calculate_performance_score(coin_data)
        assert isinstance(score, float)
        assert score >= 0

    def test_analyze_momentum(self):
        """Test analyse du momentum"""
        coin_data = {'price_change_percentage_24h': 4.2}
        momentum = self.performers._analyze_momentum(coin_data)
        assert isinstance(momentum, str)

    def test_find_support_level(self):
        """Test recherche niveau de support"""
        coin_data = {'current_price': 50000, 'price_change_percentage_24h': -5.0}
        support = self.performers._find_support_level(coin_data)
        assert isinstance(support, str)

    def test_assess_recovery_potential(self):
        """Test évaluation potentiel de récupération"""
        coin_data = {'price_change_percentage_24h': -8.0, 'total_volume': 2000000}
        potential = self.performers._assess_recovery_potential(coin_data)
        assert isinstance(potential, str)

    def test_calculate_strength_index(self):
        """Test calcul indice de force"""
        index = self.performers._calculate_strength_index(7, 3, 10)
        assert isinstance(index, float)
        assert 0 <= index <= 100

    def test_classify_market_condition(self):
        """Test classification condition marché"""
        ratios = {'market_strength': 65, 'gainers_ratio': 0.7}
        condition = self.performers._classify_market_condition(ratios)
        assert isinstance(condition, str)