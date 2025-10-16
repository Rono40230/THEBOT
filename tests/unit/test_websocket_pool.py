from src.thebot.core.logger import logger
"""
Tests unitaires pour WebSocketPool - Phase 4
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from dash_modules.core.websocket_pool import WebSocketPool, WEBSOCKETS_AVAILABLE


class TestWebSocketPool:
    """Tests pour le pool WebSocket"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.pool = WebSocketPool(max_connections_per_host=3)

    def test_init(self):
        """Test initialisation du pool"""
        assert self.pool.max_connections_per_host == 3
        assert self.pool._stats["connections_created"] == 0
        assert self.pool._stats["connections_reused"] == 0
        assert self.pool._stats["connections_closed"] == 0
        assert self.pool._stats["messages_sent"] == 0
        assert self.pool._stats["messages_received"] == 0
        assert self.pool._stats["errors"] == 0

    @patch('dash_modules.core.websocket_pool.logger')
    def test_init_without_websockets(self, mock_logger):
        """Test initialisation sans bibliothèque websockets"""
        with patch('dash_modules.core.websocket_pool.WEBSOCKETS_AVAILABLE', False):
            pool = WebSocketPool()
            mock_logger.warning.assert_called_with("WebSocket library non disponible")

    @patch('dash_modules.core.websocket_pool.logger')
    def test_start(self, mock_logger):
        """Test démarrage du pool"""
        self.pool.start()
        mock_logger.info.assert_called_with("🌐 WebSocketPool démarré")

    @patch('dash_modules.core.websocket_pool.logger')
    def test_stop(self, mock_logger):
        """Test arrêt du pool"""
        self.pool.stop()
        mock_logger.info.assert_called_with("🌐 WebSocketPool arrêté")

    def test_get_stats(self):
        """Test récupération des statistiques"""
        # Modifier quelques stats
        self.pool._stats["connections_created"] = 5
        self.pool._stats["messages_sent"] = 100

        stats = self.pool.get_stats()

        assert stats["connections_created"] == 5
        assert stats["messages_sent"] == 100
        # Vérifier que c'est une copie
        assert stats is not self.pool._stats

        # Vérifier que la modification de la copie n'affecte pas l'original
        stats["connections_created"] = 10
        assert self.pool._stats["connections_created"] == 5


class TestWebSocketPoolIntegration:
    """Tests d'intégration pour WebSocketPool"""

    @patch('dash_modules.core.websocket_pool.logger')
    def test_pool_lifecycle(self, mock_logger):
        """Test cycle de vie complet du pool"""
        pool = WebSocketPool()

        # Démarrer le pool
        pool.start()
        mock_logger.info.assert_called_with("🌐 WebSocketPool démarré")

        # Vérifier les stats initiales
        stats = pool.get_stats()
        assert all(value == 0 for value in stats.values())

        # Arrêter le pool
        pool.stop()
        mock_logger.info.assert_called_with("🌐 WebSocketPool arrêté")

    def test_stats_independence(self):
        """Test que les statistiques sont indépendantes entre instances"""
        pool1 = WebSocketPool()
        pool2 = WebSocketPool()

        # Modifier les stats de pool1
        pool1._stats["connections_created"] = 10
        pool1._stats["messages_sent"] = 50

        # Vérifier que pool2 n'est pas affecté
        stats2 = pool2.get_stats()
        assert stats2["connections_created"] == 0
        assert stats2["messages_sent"] == 0

    def test_websockets_availability(self):
        """Test de la disponibilité des websockets"""
        from dash_modules.core.websocket_pool import WEBSOCKETS_AVAILABLE
        # Ce test passe toujours, que websockets soit disponible ou non
        assert isinstance(WEBSOCKETS_AVAILABLE, bool)
