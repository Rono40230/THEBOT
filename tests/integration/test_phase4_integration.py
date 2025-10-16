from src.thebot.core.logger import logger
"""
Tests d'intégration Phase 4 - Performance et Observabilité
"""

import pytest
import time
from dash_modules.core.lazy_module_loader import LazyModuleLoader
from dash_modules.core.metrics_health import MetricsCollector, HealthChecker
from dash_modules.core.structured_logger import StructuredLogger
from dash_modules.core.rss_paginator import OptimizedRSSPaginator
from dash_modules.core.websocket_pool import WebSocketPool


class TestPhase4Integration:
    """Tests d'intégration pour tous les composants Phase 4"""

    def test_lazy_module_loader_integration(self):
        """Test intégration du chargeur paresseux de modules"""
        loader = LazyModuleLoader()
        
        # Vérifier que les modules sont enregistrés
        assert len(loader._module_classes) > 0
        assert "crypto" in loader._module_classes
        
        # Tester les métriques de performance
        metrics = loader.get_performance_metrics()
        assert "loaded_modules_count" in metrics
        assert "total_load_time" in metrics
        assert "average_load_time" in metrics
        assert "module_load_times" in metrics

    def test_metrics_health_integration(self):
        """Test intégration du système métriques/santé"""
        collector = MetricsCollector()
        checker = HealthChecker(collector)
        
        # Simuler des requêtes
        collector.record_request(0.1, success=True)
        collector.record_request(0.2, success=False)
        collector.record_cache_access(hit=True)
        collector.record_cache_access(hit=False)
        
        # Vérifier les métriques
        metrics = collector.get_application_metrics()
        assert metrics["total_requests"] == 2
        assert metrics["error_count"] == 1
        assert metrics["cache_hit_rate_percent"] == 50.0
        
        # Vérifier les checks de santé
        results = checker.run_all_checks()
        assert len(results) == 2
        
        # Vérifier qu'il y a un check système et un check application
        check_names = [r["name"] for r in results]
        assert "system_health" in check_names
        assert "application_health" in check_names

    def test_structured_logger_integration(self):
        """Test intégration du logger structuré"""
        logger = StructuredLogger()
        
        # Vérifier la création de loggers spécialisés
        perf_logger = logger.get_logger("performance")
        assert perf_logger is not None
        
        # Vérifier les statistiques
        stats = logger.get_stats()
        assert "log_level" in stats
        assert "active_loggers" in stats
        assert "performance" in stats["active_loggers"]

    def test_rss_paginator_integration(self):
        """Test intégration du paginateur RSS"""
        paginator = OptimizedRSSPaginator()
        
        # Vérifier l'initialisation
        assert paginator.cache_ttl == 300  # Valeur par défaut
        assert paginator.default_page_size == 20
        
        # Tester la validation des paramètres
        with pytest.raises(ValueError):
            paginator.get_paginated_feed("http://example.com", page=0)
        
        with pytest.raises(ValueError):
            paginator.get_paginated_feed("http://example.com", page_size=200)
        
        # Vérifier les statistiques
        stats = paginator.get_stats()
        assert "feeds_fetched" in stats
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert "parse_errors" in stats

    def test_websocket_pool_integration(self):
        """Test intégration du pool WebSocket"""
        pool = WebSocketPool()
        
        # Vérifier l'initialisation
        assert pool.max_connections_per_host == 5  # Valeur par défaut
        
        # Tester les statistiques
        stats = pool.get_stats()
        assert all(isinstance(value, int) for value in stats.values())
        assert all(value >= 0 for value in stats.values())

    def test_phase4_components_cooperation(self):
        """Test coopération entre composants Phase 4"""
        # Créer toutes les instances
        loader = LazyModuleLoader()
        collector = MetricsCollector()
        checker = HealthChecker(collector)
        logger = StructuredLogger()
        paginator = OptimizedRSSPaginator()
        pool = WebSocketPool()
        
        # Simuler un workflow complet
        start_time = time.time()
        
        # 1. Enregistrer des métriques de performance
        collector.record_request(0.05, success=True)
        
        # 2. Vérifier la santé du système
        health_results = checker.run_all_checks()
        assert len(health_results) == 2
        
        # 3. Logger des informations de performance
        perf_logger = logger.get_logger("integration_test")
        
        # 4. Vérifier les métriques du loader
        loader_metrics = loader.get_performance_metrics()
        
        # 5. Vérifier les métriques du paginateur
        paginator_stats = paginator.get_stats()
        
        # 6. Vérifier les métriques du pool
        pool_stats = pool.get_stats()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Vérifier que tout fonctionne ensemble
        assert total_time < 1.0  # Doit être rapide
        assert len(health_results) == 2
        assert loader_metrics["loaded_modules_count"] >= 0
        assert isinstance(paginator_stats, dict)
        assert isinstance(pool_stats, dict)
        
        logger.info(f"✅ Test de coopération Phase 4 réussi en {total_time:.3f}s")

    def test_phase4_memory_efficiency(self):
        """Test efficacité mémoire des composants Phase 4"""
        import psutil
        import os
        
        # Mesurer la mémoire avant
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Créer tous les composants Phase 4
        components = []
        components.append(LazyModuleLoader())
        components.append(MetricsCollector())
        components.append(HealthChecker(MetricsCollector()))
        components.append(StructuredLogger())
        components.append(OptimizedRSSPaginator())
        components.append(WebSocketPool())
        
        # Mesurer la mémoire après
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before
        
        # Vérifier que l'utilisation mémoire est raisonnable (< 50MB)
        assert memory_used < 50, f"Utilisation mémoire trop élevée: {memory_used:.1f}MB"
        
        logger.info(f"✅ Utilisation mémoire Phase 4: {memory_used:.1f}MB")


class TestPhase4Performance:
    """Tests de performance pour les composants Phase 4"""

    def test_lazy_loader_performance(self):
        """Test performance du chargeur paresseux"""
        loader = LazyModuleLoader()
        
        start_time = time.time()
        
        # Tester plusieurs accès aux métriques
        for _ in range(100):
            metrics = loader.get_performance_metrics()
            assert "loaded_modules_count" in metrics
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Doit être très rapide (< 0.1s pour 100 appels)
        assert total_time < 0.1, f"Performance trop lente: {total_time:.3f}s"
        logger.info(f"✅ Performance LazyLoader: {total_time:.3f}s pour 100 appels")

    def test_metrics_performance(self):
        """Test performance du système de métriques"""
        collector = MetricsCollector()
        checker = HealthChecker(collector)
        
        start_time = time.time()
        
        # Simuler beaucoup de requêtes
        for i in range(1000):
            collector.record_request(0.001, success=(i % 10 != 0))  # 10% d'erreurs
            collector.record_cache_access(hit=(i % 2 == 0))  # 50% de hits
        
        # Calculer les métriques
        metrics = collector.get_application_metrics()
        
        # Vérifier les checks de santé
        results = checker.run_all_checks()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Vérifier les résultats
        assert metrics["total_requests"] == 1000
        assert metrics["error_count"] == 100  # 10% d'erreurs
        assert 45 <= metrics["cache_hit_rate_percent"] <= 55  # ~50%
        assert len(results) == 2
        
        # Performance acceptable (< 0.5s pour 1000 opérations)
        assert total_time < 0.5, f"Performance métriques trop lente: {total_time:.3f}s"
        logger.info(f"✅ Performance métriques: {total_time:.3f}s pour 1000 opérations")
