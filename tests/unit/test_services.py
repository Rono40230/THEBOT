"""
Tests pour les services métier THEBOT
"""

import pytest
import tempfile
from pathlib import Path

from dash_modules.services import AlertService, MarketDataService, NewsService


class TestAlertService:
    """Tests pour AlertService"""

    def setup_method(self):
        """Configuration avant chaque test"""
        # Créer un fichier temporaire pour les tests
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.write('[]')  # Fichier vide
        self.temp_file.close()
        self.service = AlertService()

    def teardown_method(self):
        """Nettoyage après chaque test"""
        Path(self.temp_file.name).unlink(missing_ok=True)

    def test_initialization(self):
        """Test initialisation du service"""
        assert self.service is not None
        assert hasattr(self.service, 'alerts')
        assert isinstance(self.service.alerts, dict)


class TestMarketDataService:
    """Tests pour MarketDataService"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.service = MarketDataService()

    def test_initialization(self):
        """Test initialisation du service"""
        assert self.service is not None


class TestNewsService:
    """Tests pour NewsService"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.service = NewsService()

    def test_initialization(self):
        """Test initialisation du service"""
        assert self.service is not None

    def test_get_news_empty(self):
        """Test récupération news vides"""
        news = self.service.get_news()
        assert isinstance(news, list)