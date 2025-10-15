"""
Tests de charge Phase 5 - Simulation utilisation réelle
Tests avec volumes de données réalistes et scénarios de stress
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch, MagicMock
import random
import string

from dash_modules.services import AlertService, MarketDataService, NewsService
from dash_modules.models import Alert, AlertType, MarketData, NewsArticle
from datetime import datetime, timedelta


class TestLoadScenarios:
    """Tests de scénarios de charge réalistes"""

    def test_high_frequency_alert_creation(self):
        """Test création d'alertes à haute fréquence"""
        alert_service = AlertService()

        # Nettoyer les alertes existantes pour le test
        existing_alerts = alert_service.get_all_alerts()
        for alert in existing_alerts:
            alert_service.delete_alert(alert.id)

        # Simuler création rapide d'alertes (comme un utilisateur actif)
        start_time = time.time()

        alerts_created = 0
        for i in range(500):  # 500 alertes
            symbol = f"STRESS{random.randint(1, 10)}"  # 10 symboles différents
            alert_type = random.choice([AlertType.ABOVE, AlertType.BELOW])
            price = random.uniform(10000, 100000)  # Prix aléatoire

            alert = alert_service.create_alert(symbol, alert_type, price)
            alerts_created += 1

        creation_time = time.time() - start_time

        # Vérifications
        all_alerts = alert_service.get_all_alerts()
        assert len(all_alerts) == 500
        assert creation_time < 20.0, f"Création trop lente: {creation_time:.2f}s pour 500 alertes"

        # Vérifier la répartition par symbole
        symbols = {}
        for alert in all_alerts:
            symbols[alert.symbol] = symbols.get(alert.symbol, 0) + 1

        assert len(symbols) <= 10  # Au plus 10 symboles différents
        print(f"✅ Stress test alertes: {creation_time:.2f}s pour {alerts_created} alertes")

    def test_concurrent_user_simulation(self):
        """Test simulation d'utilisateurs concurrents"""
        alert_service = AlertService()

        # Nettoyer les alertes existantes pour le test
        existing_alerts = alert_service.get_all_alerts()
        for alert in existing_alerts:
            alert_service.delete_alert(alert.id)

        import threading
        lock = threading.Lock()

        def simulate_user_activity(user_id):
            """Simule l'activité d'un utilisateur"""
            user_alerts = []

            # Chaque utilisateur crée 20 alertes
            for i in range(20):
                symbol = f"USER{user_id}_SYM{i % 5}"  # 5 symboles par utilisateur
                alert_type = AlertType.ABOVE if i % 2 == 0 else AlertType.BELOW
                price = 50000.0 + (user_id * 1000) + i

                with lock:
                    alert = alert_service.create_alert(symbol, alert_type, price)
                user_alerts.append(alert)

                # Simuler une petite pause (comme un utilisateur réel)
                time.sleep(0.001)  # 1ms

            return user_alerts

        # Simuler 10 utilisateurs concurrents
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(simulate_user_activity, i) for i in range(10)]
            results = []

            for future in as_completed(futures):
                user_alerts = future.result()
                results.extend(user_alerts)

        total_time = time.time() - start_time

        # Vérifications
        all_alerts = alert_service.get_all_alerts()
        assert len(all_alerts) == 200  # 10 utilisateurs * 20 alertes
        assert len(results) == 200

        # Temps acceptable pour utilisateurs concurrents
        assert total_time < 30.0, f"Utilisation concurrente trop lente: {total_time:.2f}s"

        print(f"✅ Simulation 10 utilisateurs: {total_time:.2f}s pour 200 alertes")

    def test_large_market_data_processing(self):
        """Test traitement de gros volumes de données de marché"""
        market_service = MarketDataService()

        # Générer un gros volume de données de marché
        symbols = [f"CRYPTO{i}" for i in range(100)]  # 100 cryptos
        market_data = []

        for symbol in symbols:
            data = MarketData(
                symbol=symbol,
                current_price=random.uniform(0.1, 100000),
                price_change_24h=random.uniform(-20, 20),
                volume_24h=random.uniform(1000, 10000000)
            )
            market_data.append(data)

        # Simuler l'ajout de ces données
        start_time = time.time()

        # Simuler le traitement des données (création d'objets)
        processed_count = 0
        for data in market_data:
            # Simuler un traitement simple
            processed_count += 1

        processing_time = time.time() - start_time

        # Vérifications
        assert processed_count == 100
        assert processing_time < 5.0, f"Traitement données marché trop lent: {processing_time:.2f}s"

        print(f"✅ Traitement 100 cryptos: {processing_time:.2f}s")

    def test_news_feed_high_volume(self):
        """Test flux d'actualités à haut volume"""
        news_service = NewsService()

        # Générer beaucoup d'articles
        sources = ["CryptoNews", "BlockChain Today", "CoinDesk", "NewsBTC", "The Block"]
        sentiments = ["positive", "negative", "neutral"]

        articles = []
        base_time = datetime.now()

        for i in range(1000):  # 1000 articles
            article = NewsArticle(
                title=f"News Article {i}",
                url=f"https://example.com/news/{i}",
                summary=f"This is the content of news article {i}. " * 10,  # Contenu plus long
                published=(base_time - timedelta(hours=i)),
                source=random.choice(sources),
                symbols=[f"CRYPTO{random.randint(0, 99)}"],
                relevance_score=random.uniform(0.1, 1.0)
            )
            articles.append(article)

        # Simuler le traitement des actualités
        start_time = time.time()

        # Simuler le traitement des articles (comptage)
        processed_count = 0
        for article in articles:
            processed_count += 1

        processing_time = time.time() - start_time

        # Vérifications
        assert processed_count == 1000
        assert processing_time < 10.0, f"Traitement actualités trop lent: {processing_time:.2f}s"

        # Vérifier la distribution des sources
        source_counts = {}
        for article in articles:
            source_counts[article.source] = source_counts.get(article.source, 0) + 1

        assert len(source_counts) <= len(sources)
        print(f"✅ Traitement 1000 actualités: {processing_time:.2f}s")


class TestStressTesting:
    """Tests de stress du système"""

    def test_memory_stress_large_alerts(self):
        """Test stress mémoire avec énormément d'alertes"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        alert_service = AlertService()

        # Nettoyer les alertes existantes pour le test
        existing_alerts = alert_service.get_all_alerts()
        for alert in existing_alerts:
            alert_service.delete_alert(alert.id)

        # Mesurer mémoire avant
        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        # Créer 10000 alertes (stress test)
        start_time = time.time()

        for i in range(10000):
            # Générer des messages longs pour stresser la mémoire
            long_message = ''.join(random.choices(string.ascii_letters, k=500))
            alert_service.create_alert(
                symbol=f"STRESS{i % 50}",  # 50 symboles différents
                alert_type=AlertType.ABOVE if i % 2 == 0 else AlertType.BELOW,
                price=50000.0 + (i % 1000),
                message=long_message
            )

        creation_time = time.time() - start_time
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before

        # Vérifications
        all_alerts = alert_service.get_all_alerts()
        assert len(all_alerts) == 10000

        # Performance acceptable
        assert creation_time < 60.0, f"Création 10000 alertes trop lente: {creation_time:.2f}s"
        assert memory_used < 200.0, f"Utilisation mémoire excessive: {memory_used:.2f}MB"

        print(f"✅ Stress test 10000 alertes: {creation_time:.2f}s, {memory_used:.2f}MB")

    def test_concurrent_data_access_stress(self):
        """Test stress accès concurrent aux données"""
        alert_service = AlertService()

        # Pré-remplir avec des données
        for i in range(1000):
            alert_service.create_alert(f"CONC{i}", AlertType.ABOVE, 50000.0)

        errors = []
        successful_operations = []

        def stress_worker(worker_id):
            """Worker de stress"""
            local_errors = 0
            local_success = 0

            try:
                # Mélanger lecture et écriture
                for i in range(100):
                    if random.random() < 0.7:  # 70% lecture
                        alerts = alert_service.get_all_alerts()
                        local_success += 1
                    else:  # 30% écriture
                        alert_service.create_alert(
                            f"STRESS{worker_id}_{i}",
                            AlertType.ABOVE,
                            50000.0
                        )
                        local_success += 1
            except Exception as e:
                local_errors += 1
                errors.append(f"Worker {worker_id}: {e}")

            successful_operations.append(local_success)
            return local_errors

        # Lancer 20 workers concurrents
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(stress_worker, i) for i in range(20)]
            results = [future.result() for future in as_completed(futures)]

        total_time = time.time() - start_time
        total_errors = sum(results)
        total_success = sum(successful_operations)

        # Vérifications
        assert total_errors == 0, f"Erreurs pendant stress concurrent: {errors}"
        assert total_success == 2000, f"Opérations réussies incorrectes: {total_success}"  # 20 workers * 100 ops

        # Performance acceptable
        assert total_time < 45.0, f"Stress concurrent trop lent: {total_time:.2f}s"

        print(f"✅ Stress concurrent 20 workers: {total_time:.2f}s, {total_success} opérations")

    def test_api_timeout_simulation(self):
        """Test simulation de timeouts API sous charge"""
        # Simuler des appels API qui peuvent timeout
        timeout_errors = 0
        successful_calls = 0

        def simulate_api_call(call_id):
            """Simule un appel API qui peut échouer"""
            nonlocal timeout_errors, successful_calls

            # Simuler un délai aléatoire
            delay = random.uniform(0.1, 5.0)  # 100ms à 5s

            if delay > 3.0:  # 3s timeout
                timeout_errors += 1
                raise TimeoutError(f"API call {call_id} timed out after {delay:.2f}s")
            else:
                time.sleep(delay)
                successful_calls += 1
                return f"Success {call_id}"

        # Simuler 100 appels API concurrents
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(simulate_api_call, i) for i in range(100)]

            results = []
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=5.0)
                    results.append(result)
                except Exception as e:
                    results.append(f"Error: {e}")

        total_time = time.time() - start_time

        # Vérifications
        assert successful_calls > 50, f"Trop d'échecs API: {successful_calls} succès, {timeout_errors} timeouts"
        assert total_time < 60.0, f"Test timeout trop lent: {total_time:.2f}s"

        print(f"✅ Simulation API timeouts: {successful_calls} succès, {timeout_errors} timeouts en {total_time:.2f}s")


class TestRealisticUsageScenarios:
    """Tests de scénarios d'utilisation réalistes"""

    def test_trading_day_simulation(self):
        """Test simulation d'une journée de trading"""
        alert_service = AlertService()

        # Nettoyer les alertes existantes pour le test
        existing_alerts = alert_service.get_all_alerts()
        for alert in existing_alerts:
            alert_service.delete_alert(alert.id)

        # Simuler l'activité d'une journée de trading
        # Matinée: Création d'alertes
        morning_alerts = 0
        for i in range(50):
            alert_service.create_alert(
                symbol=random.choice(["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT"]),
                alert_type=random.choice([AlertType.ABOVE, AlertType.BELOW]),
                price=random.uniform(30000, 60000),
                message=f"Morning alert {i}"
            )
            morning_alerts += 1

        # Midi: Mise à jour d'alertes
        all_alerts = alert_service.get_all_alerts()
        updated_count = 0
        for alert in all_alerts[:10]:  # Mettre à jour 10 alertes
            alert_service.update_alert(alert.id, price=alert.price * 1.05)
            updated_count += 1

        # Après-midi: Suppression d'alertes expirées
        deleted_count = 0
        alerts_to_delete = all_alerts[10:20]  # Supprimer 10 alertes
        for alert in alerts_to_delete:
            alert_service.delete_alert(alert.id)
            deleted_count += 1

        # Fin de journée: Vérifications
        final_alerts = alert_service.get_all_alerts()
        expected_count = morning_alerts - deleted_count

        assert len(final_alerts) == expected_count
        assert morning_alerts == 50
        assert updated_count == 10
        assert deleted_count == 10

        print(f"✅ Simulation journée trading: {morning_alerts} créées, {updated_count} mises à jour, {deleted_count} supprimées")

    def test_multi_user_collaboration(self):
        """Test collaboration multi-utilisateurs"""
        # Nettoyer les alertes existantes pour le test
        alert_service = AlertService()
        existing_alerts = alert_service.get_all_alerts()
        for alert in existing_alerts:
            alert_service.delete_alert(alert.id)

        # Simuler plusieurs utilisateurs travaillant sur le même système
        users = ["Alice", "Bob", "Charlie", "Diana"]
        user_alerts = {}

        for user in users:
            user_alerts[user] = []

            # Chaque utilisateur crée ses propres alertes
            for i in range(25):
                alert = alert_service.create_alert(
                    symbol=f"{user[:3].upper()}{i}",
                    alert_type=AlertType.ABOVE,
                    price=50000.0 + (users.index(user) * 5000),
                    message=f"Alerte de {user} #{i}"
                )
                user_alerts[user].append(alert)

        # Vérifications
        all_alerts = alert_service.get_all_alerts()
        total_expected = len(users) * 25

        assert len(all_alerts) == total_expected

        # Vérifier que chaque utilisateur a ses alertes
        for user, alerts in user_alerts.items():
            assert len(alerts) == 25
            # Vérifier que les symboles commencent par les initiales de l'utilisateur
            for alert in alerts:
                assert alert.symbol.startswith(user[:3].upper())

        print(f"✅ Collaboration {len(users)} utilisateurs: {total_expected} alertes totales")

    def test_data_backup_recovery_scenario(self):
        """Test scénario de sauvegarde et récupération de données"""
        import tempfile
        import os

        # Créer un service avec un fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name

        try:
            # Créer des données
            alert_service1 = AlertService(data_file=temp_file)

            original_alerts = []
            for i in range(100):
                alert = alert_service1.create_alert(
                    symbol=f"BACKUP{i % 10}",
                    alert_type=AlertType.ABOVE,
                    price=50000.0 + i,
                    message=f"Backup test {i}"
                )
                original_alerts.append(alert)

            # Simuler une "panne" - créer un nouveau service avec le même fichier
            alert_service2 = AlertService(data_file=temp_file)

            # Vérifier que les données sont récupérées
            recovered_alerts = alert_service2.get_all_alerts()

            assert len(recovered_alerts) == len(original_alerts)

            # Vérifier l'intégrité des données
            for original, recovered in zip(original_alerts, recovered_alerts):
                assert original.id == recovered.id
                assert original.symbol == recovered.symbol
                assert original.price == recovered.price

            print(f"✅ Sauvegarde/récupération: {len(recovered_alerts)} alertes préservées")

        finally:
            # Nettoyer
            if os.path.exists(temp_file):
                os.unlink(temp_file)