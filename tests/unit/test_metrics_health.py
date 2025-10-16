"""
Tests unitaires pour MetricsCollector et HealthChecker - Phase 4
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from dash_modules.core.metrics_health import MetricsCollector, HealthChecker


class TestMetricsCollector:
    """Tests pour le collecteur de métriques"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.collector = MetricsCollector()

    def test_init(self):
        """Test initialisation du collecteur"""
        assert isinstance(self.collector.start_time, datetime)
        assert self.collector.request_count == 0
        assert self.collector.error_count == 0
        assert self.collector.cache_hits == 0
        assert self.collector.cache_misses == 0

    def test_record_request_success(self):
        """Test enregistrement d'une requête réussie"""
        self.collector.record_request(0.5, success=True)

        assert self.collector.request_count == 1
        assert self.collector.error_count == 0

    def test_record_request_error(self):
        """Test enregistrement d'une requête en erreur"""
        self.collector.record_request(0.5, success=False)

        assert self.collector.request_count == 1
        assert self.collector.error_count == 1

    def test_record_cache_hit(self):
        """Test enregistrement d'un hit cache"""
        self.collector.record_cache_access(hit=True)

        assert self.collector.cache_hits == 1
        assert self.collector.cache_misses == 0

    def test_record_cache_miss(self):
        """Test enregistrement d'un miss cache"""
        self.collector.record_cache_access(hit=False)

        assert self.collector.cache_hits == 0
        assert self.collector.cache_misses == 1

    def test_get_application_metrics(self):
        """Test récupération des métriques d'application"""
        # Simuler des données
        self.collector.request_count = 100
        self.collector.error_count = 5
        self.collector.cache_hits = 80
        self.collector.cache_misses = 20

        # Simuler un uptime de 1 heure
        self.collector.start_time = datetime.now() - timedelta(hours=1)

        metrics = self.collector.get_application_metrics()

        assert metrics["total_requests"] == 100
        assert metrics["error_count"] == 5
        assert metrics["error_rate_percent"] == 5.0  # 5/100 * 100
        assert metrics["cache_hit_rate_percent"] == 80.0  # 80/100 * 100
        assert metrics["uptime_seconds"] >= 3600  # Au moins 1 heure

    def test_get_application_metrics_no_requests(self):
        """Test métriques sans requêtes"""
        metrics = self.collector.get_application_metrics()

        assert metrics["total_requests"] == 0
        assert metrics["error_rate_percent"] == 0
        assert metrics["cache_hit_rate_percent"] == 0


class TestHealthChecker:
    """Tests pour le vérificateur de santé"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.metrics = Mock(spec=MetricsCollector)
        self.checker = HealthChecker(self.metrics)

    @patch('dash_modules.core.metrics_health.psutil')
    def test_check_system_health_healthy(self, mock_psutil):
        """Test vérification système en bonne santé"""
        # Mock des valeurs système normales
        mock_cpu = Mock()
        mock_cpu.percent.return_value = 50.0
        mock_psutil.cpu_percent.return_value = 50.0

        mock_memory = Mock()
        mock_memory.percent = 60.0
        mock_psutil.virtual_memory.return_value = mock_memory

        result = self.checker._check_system_health()

        assert result["name"] == "system_health"
        assert result["status"] == "healthy"
        assert "CPU: 50.0%" in result["message"]
        assert "RAM: 60.0%" in result["message"]
        assert result["details"]["cpu_percent"] == 50.0
        assert result["details"]["memory_percent"] == 60.0

    @patch('dash_modules.core.metrics_health.psutil')
    def test_check_system_health_critical(self, mock_psutil):
        """Test vérification système critique"""
        mock_psutil.cpu_percent.return_value = 95.0
        mock_memory = Mock()
        mock_memory.percent = 95.0
        mock_psutil.virtual_memory.return_value = mock_memory

        result = self.checker._check_system_health()

        assert result["status"] == "critical"

    @patch('dash_modules.core.metrics_health.psutil')
    def test_check_system_health_error(self, mock_psutil):
        """Test gestion d'erreur lors de la vérification système"""
        mock_psutil.cpu_percent.side_effect = Exception("Erreur système")

        result = self.checker._check_system_health()

        assert result["status"] == "critical"
        assert "Erreur: Erreur système" in result["message"]

    def test_check_application_health_healthy(self):
        """Test vérification application en bonne santé"""
        self.metrics.get_application_metrics.return_value = {
            "error_rate_percent": 2.0
        }

        result = self.checker._check_application_health()

        assert result["name"] == "application_health"
        assert result["status"] == "healthy"
        assert "Taux d'erreur: 2.0%" in result["message"]

    def test_check_application_health_critical(self):
        """Test vérification application critique"""
        self.metrics.get_application_metrics.return_value = {
            "error_rate_percent": 15.0
        }

        result = self.checker._check_application_health()

        assert result["status"] == "critical"

    def test_run_all_checks(self):
        """Test exécution de toutes les vérifications"""
        # Mock des méthodes
        with patch.object(self.checker, '_check_system_health') as mock_system, \
             patch.object(self.checker, '_check_application_health') as mock_app:

            mock_system.return_value = {"name": "system", "status": "healthy"}
            mock_app.return_value = {"name": "app", "status": "healthy"}

            results = self.checker.run_all_checks()

            assert len(results) == 2
            assert results[0]["name"] == "system"
            assert results[1]["name"] == "app"
