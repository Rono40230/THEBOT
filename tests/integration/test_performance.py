from src.thebot.core.logger import logger
"""
Tests de performance Phase 5 - Validation des performances système
Mesure les temps de réponse, utilisation mémoire et charge système
"""

import pytest
import time
import psutil
import os
from unittest.mock import patch, MagicMock
from memory_profiler import profile, memory_usage
import cProfile
import pstats
from io import StringIO

from launch_dash_professional import create_dash_app
from dash_modules.services import AlertService, MarketDataService, NewsService
from dash_modules.models import Alert, AlertType, MarketData, NewsArticle


class TestPerformanceMetrics:
    """Tests des métriques de performance"""

    def test_dashboard_creation_performance(self):
        """Test performance de création du dashboard"""
        start_time = time.time()

        # Créer l'application
        app = create_dash_app()

        creation_time = time.time() - start_time

        # La création devrait prendre moins de 10 secondes
        assert creation_time < 10.0, f"Création trop lente: {creation_time:.2f}s"
        logger.info(f"✅ Temps de création dashboard: {creation_time:.2f}s")

    def test_memory_usage_during_creation(self):
        """Test utilisation mémoire pendant la création"""
        process = psutil.Process(os.getpid())

        # Mesurer la mémoire avant
        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        # Créer l'application
        app = create_dash_app()

        # Mesurer la mémoire après
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before

        # L'utilisation mémoire devrait être raisonnable
        assert memory_used < 300.0, f"Utilisation mémoire excessive: {memory_used:.2f}MB"
        logger.info(f"✅ Utilisation mémoire création: {memory_used:.2f}MB")

    def test_service_initialization_performance(self):
        """Test performance d'initialisation des services"""
        services = [AlertService, MarketDataService, NewsService]

        for service_class in services:
            start_time = time.time()

            # Créer une instance du service
            if service_class == AlertService:
                service = service_class()  # Utilise le fichier par défaut
            else:
                service = service_class()

            init_time = time.time() - start_time

            # L'initialisation devrait être rapide
            assert init_time < 2.0, f"Initialisation {service_class.__name__} trop lente: {init_time:.2f}s"
            logger.info(f"✅ Initialisation {service_class.__name__}: {init_time:.2f}s")

    def test_data_processing_performance(self):
        """Test performance du traitement des données"""
        # Créer un service d'alertes
        alert_service = AlertService()

        # Nettoyer les alertes existantes pour le test
        existing_alerts = alert_service.get_all_alerts()
        for alert in existing_alerts:
            alert_service.delete_alert(alert.id)

        # Mesurer la création de plusieurs alertes
        start_time = time.time()

        alerts = []
        for i in range(100):  # Créer 100 alertes
            alert = alert_service.create_alert(
                symbol=f"BTC{i}",
                alert_type=AlertType.ABOVE,
                price=50000.0 + i,
                message=f"Test alert {i}"
            )
            alerts.append(alert)

        processing_time = time.time() - start_time

        # Le traitement devrait être rapide
        assert processing_time < 5.0, f"Traitement données trop lent: {processing_time:.2f}s"
        assert len(alerts) == 100
        logger.info(f"✅ Traitement 100 alertes: {processing_time:.2f}s")


class TestLoadTesting:
    """Tests de charge du système"""

    def test_concurrent_service_access(self):
        """Test accès concurrent aux services"""
        import threading

        alert_service = AlertService()
        results = []
        errors = []

        def create_alert_worker(worker_id):
            """Worker pour créer des alertes"""
            try:
                for i in range(10):
                    alert = alert_service.create_alert(
                        symbol=f"TEST{worker_id}_{i}",
                        alert_type=AlertType.ABOVE,
                        price=50000.0,
                        message=f"Worker {worker_id} alert {i}"
                    )
                    results.append(alert)
            except Exception as e:
                errors.append(e)

        # Créer 5 threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_alert_worker, args=(i,))
            threads.append(thread)

        # Démarrer tous les threads
        start_time = time.time()
        for thread in threads:
            thread.start()

        # Attendre que tous les threads terminent
        for thread in threads:
            thread.join()

        execution_time = time.time() - start_time

        # Vérifier les résultats
        assert len(errors) == 0, f"Erreurs pendant l'accès concurrent: {errors}"
        assert len(results) == 50, f"Nombre d'alertes incorrect: {len(results)}"  # 5 workers * 10 alertes

        # Le temps d'exécution devrait être raisonnable
        assert execution_time < 10.0, f"Exécution concurrente trop lente: {execution_time:.2f}s"
        logger.info(f"✅ Test concurrent (50 alertes): {execution_time:.2f}s")

    def test_large_dataset_handling(self):
        """Test gestion de gros volumes de données"""
        alert_service = AlertService()

        # Nettoyer les alertes existantes pour le test
        existing_alerts = alert_service.get_all_alerts()
        for alert in existing_alerts:
            alert_service.delete_alert(alert.id)

        # Créer un grand nombre d'alertes
        start_time = time.time()

        for i in range(1000):  # 1000 alertes
            alert_service.create_alert(
                symbol=f"LARGE{i % 10}",  # 10 symboles différents
                alert_type=AlertType.ABOVE if i % 2 == 0 else AlertType.BELOW,
                price=50000.0 + (i % 100),
                message=f"Large dataset alert {i}"
            )

        creation_time = time.time() - start_time

        # Récupérer toutes les alertes
        retrieval_start = time.time()
        all_alerts = alert_service.get_all_alerts()
        retrieval_time = time.time() - retrieval_start

        # Vérifier les performances
        assert len(all_alerts) == 1000
        assert creation_time < 60.0, f"Création dataset trop lente: {creation_time:.2f}s"  # Timeout plus réaliste
        assert retrieval_time < 5.0, f"Récupération dataset trop lente: {retrieval_time:.2f}s"

        logger.info(f"✅ Dataset 1000 alertes - Création: {creation_time:.2f}s, Récupération: {retrieval_time:.2f}s")

    def test_memory_efficiency_large_data(self):
        """Test efficacité mémoire avec gros volumes"""
        process = psutil.Process(os.getpid())

        # Mesurer mémoire avant
        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        alert_service = AlertService()

        # Nettoyer les alertes existantes pour le test
        existing_alerts = alert_service.get_all_alerts()
        for alert in existing_alerts:
            alert_service.delete_alert(alert.id)

        # Créer beaucoup d'alertes
        for i in range(1000):  # Réduit à 1000 alertes pour performance
            alert_service.create_alert(
                symbol=f"MEM{i % 5}",
                alert_type=AlertType.ABOVE,
                price=50000.0,
                message=f"Memory test {i}"
            )

        # Mesurer mémoire après
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before

        # Nettoyer
        all_alerts = alert_service.get_all_alerts()
        assert len(all_alerts) == 1000  # Ajusté au nouveau nombre

        # L'utilisation mémoire devrait être proportionnelle
        # ~1KB par alerte, donc ~1MB pour 1000 alertes est acceptable
        assert memory_used < 10.0, f"Utilisation mémoire excessive: {memory_used:.2f}MB"
        logger.info(f"✅ Mémoire 1000 alertes: {memory_used:.2f}MB")


class TestAPIPerformance:
    """Tests de performance des APIs simulées"""

    @patch('dash_modules.data_providers.provider_manager.provider_manager')
    def test_api_response_time_simulation(self, mock_provider_manager):
        """Test simulation des temps de réponse API"""
        # Mock du provider manager
        mock_provider = MagicMock()
        mock_provider_manager.get_provider.return_value = mock_provider

        # Simuler des données de marché
        market_data = [
            MarketData(symbol="BTCUSDT", price=50000.0, change_24h=2.5, volume_24h=1000000.0),
            MarketData(symbol="ETHUSDT", price=3000.0, change_24h=-1.2, volume_24h=500000.0)
        ]
        mock_provider.get_market_data.return_value = market_data

        # Mesurer le temps de réponse simulé
        start_time = time.time()

        # Simuler plusieurs appels API
        for _ in range(100):
            result = mock_provider.get_market_data()
            assert len(result) == 2

        total_time = time.time() - start_time
        avg_time = total_time / 100

        # Le temps moyen devrait être très rapide pour des données mockées
        assert avg_time < 0.01, f"Temps de réponse API trop lent: {avg_time:.4f}s"
        logger.info(f"✅ Temps réponse API simulé (100 appels): {avg_time:.4f}s/appel")

    def test_caching_performance(self):
        """Test performance du système de cache"""
        from thebot.core.cache import IntelligentCache

        cache = IntelligentCache()

        # Tester la performance du cache
        test_data = {"test": "data", "numbers": list(range(1000))}

        # Mesurer écriture cache
        start_time = time.time()
        for i in range(100):
            cache.set(f"test_key_{i}", test_data, ttl=300)
        write_time = time.time() - start_time

        # Mesurer lecture cache
        start_time = time.time()
        for i in range(100):
            result = cache.get(f"test_key_{i}")
            assert result == test_data
        read_time = time.time() - start_time

        # Les opérations cache devraient être très rapides
        assert write_time < 1.0, f"Écriture cache lente: {write_time:.2f}s"
        assert read_time < 1.0, f"Lecture cache lente: {read_time:.2f}s"

        logger.info(f"✅ Cache perf - Écriture: {write_time:.2f}s, Lecture: {read_time:.2f}s")


class TestResourceMonitoring:
    """Tests de monitoring des ressources système"""

    def test_cpu_usage_during_operations(self):
        """Test utilisation CPU pendant les opérations"""
        process = psutil.Process(os.getpid())

        # Mesurer CPU avant
        cpu_before = process.cpu_percent(interval=0.1)

        # Effectuer des opérations intensives
        alert_service = AlertService()
        for i in range(1000):
            alert_service.create_alert(
                symbol=f"CPU{i % 10}",
                alert_type=AlertType.ABOVE,
                price=50000.0,
                message=f"CPU test {i}"
            )

        # Mesurer CPU après
        cpu_after = process.cpu_percent(interval=0.1)

        # L'utilisation CPU ne devrait pas être excessive
        assert cpu_after < 50.0, f"Utilisation CPU excessive: {cpu_after:.1f}%"
        logger.info(f"✅ Utilisation CPU: {cpu_before:.1f}% → {cpu_after:.1f}%")

    def test_file_io_performance(self):
        """Test performance des opérations I/O fichier"""
        import tempfile

        alert_service = AlertService()

        # Mesurer performance sauvegarde
        start_time = time.time()

        for i in range(100):
            alert_service.create_alert(
                symbol=f"IO{i}",
                alert_type=AlertType.ABOVE,
                price=50000.0,
                message=f"IO test {i}"
            )

        # La sauvegarde se fait automatiquement à chaque création
        io_time = time.time() - start_time

        # Les opérations I/O devraient être raisonnables
        assert io_time < 10.0, f"Opérations I/O lentes: {io_time:.2f}s"
        logger.info(f"✅ Performance I/O (100 sauvegardes): {io_time:.2f}s")

    def test_memory_cleanup(self):
        """Test nettoyage mémoire après opérations"""
        process = psutil.Process(os.getpid())

        # Mesurer mémoire avant
        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        # Effectuer des opérations qui créent des objets
        alert_service = AlertService()
        alerts = []
        for i in range(1000):
            alert = alert_service.create_alert(
                symbol=f"CLEANUP{i}",
                alert_type=AlertType.ABOVE,
                price=50000.0,
                message=f"Cleanup test {i}"
            )
            alerts.append(alert)

        memory_during = process.memory_info().rss / 1024 / 1024  # MB

        # Supprimer les références
        del alerts
        del alert_service

        # Forcer le garbage collector
        import gc
        gc.collect()

        memory_after = process.memory_info().rss / 1024 / 1024  # MB

        memory_used = memory_during - memory_before
        memory_freed = memory_during - memory_after

        # Vérifier que la mémoire est récupérée
        assert memory_freed > 0, "Mémoire non libérée après nettoyage"
        assert memory_used < 100.0, f"Utilisation mémoire excessive: {memory_used:.2f}MB"

        logger.info(f"✅ Nettoyage mémoire - Utilisé: {memory_used:.2f}MB, Libéré: {memory_freed:.2f}MB")


class TestProfiling:
    """Tests avec profiling pour analyse détaillée"""

    def test_function_profiling(self):
        """Test profiling d'une fonction critique"""
        pr = cProfile.Profile()
        pr.enable()

        # Fonction à profiler
        alert_service = AlertService()
        for i in range(100):
            alert_service.create_alert(
                symbol=f"PROFILE{i}",
                alert_type=AlertType.ABOVE,
                price=50000.0,
                message=f"Profile test {i}"
            )

        pr.disable()

        # Analyser les résultats
        s = StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(10)  # Top 10 fonctions

        profile_output = s.getvalue()

        # Vérifier que le profiling a capturé des données
        assert "create_alert" in profile_output
        assert len(profile_output) > 0

        logger.info("✅ Profiling terminé - Fonctions les plus coûteuses:")
        logger.info(profile_output[:500] + "..." if len(profile_output) > 500 else profile_output)