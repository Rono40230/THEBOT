"""
Tests pour SmartAIManager - Gestionnaire intelligent des IA
Phase 2 - Expansion couverture de test THEBOT
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock, mock_open
from dash_modules.ai_engine.smart_ai_manager import SmartAIManager


class TestSmartAIManager:
    """Tests pour le gestionnaire intelligent des IA"""

    def setup_method(self):
        """Initialisation avant chaque test"""
        self.manager = SmartAIManager()

    def test_initialization(self):
        """Test initialisation du gestionnaire IA"""
        assert self.manager.local_ai is None
        assert self.manager.free_ai is None
        assert self.manager.smart_ai is None
        assert isinstance(self.manager.user_preferences, dict)
        assert isinstance(self.manager.performance_metrics, dict)
        assert "local" in self.manager.performance_metrics
        assert "huggingface" in self.manager.performance_metrics
        assert "premium" in self.manager.performance_metrics

    def test_load_user_preferences_default(self):
        """Test chargement préférences par défaut"""
        with patch('os.path.exists', return_value=False):
            prefs = self.manager._load_user_preferences()

            assert prefs["ai_mode"] == "auto"
            assert prefs["max_cost_per_month"] == 0
            assert prefs["priority_speed"] is True
            assert prefs["huggingface_enabled"] is True
            assert prefs["premium_enabled"] is False

    def test_load_user_preferences_from_file(self):
        """Test chargement préférences depuis fichier"""
        mock_prefs = {
            "ai_mode": "manual",
            "max_cost_per_month": 5,
            "huggingface_enabled": False
        }

        mock_file_data = json.dumps(mock_prefs)

        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=mock_file_data)):
            prefs = self.manager._load_user_preferences()

            assert prefs["ai_mode"] == "manual"
            assert prefs["max_cost_per_month"] == 5
            assert prefs["huggingface_enabled"] is False
            # Vérifier que les valeurs par défaut sont préservées pour les clés manquantes
            assert prefs["priority_speed"] is True

    @patch('dash_modules.ai_engine.local_ai_engine.LocalAIEngine')
    @patch('dash_modules.ai_engine.free_ai_engine.FreeAIEngine')
    @patch('dash_modules.ai_engine.smart_ai_engine.SmartAIEngine')
    def test_initialize_engines(self, mock_smart_ai, mock_free_ai, mock_local_ai):
        """Test initialisation des moteurs IA"""
        self.manager.initialize_engines()

        assert self.manager.local_ai is not None
        assert self.manager.free_ai is not None
        assert self.manager.smart_ai is not None

        mock_local_ai.assert_called_once()
        mock_free_ai.assert_called_once()
        mock_smart_ai.assert_called_once()

    def test_choose_best_ai_manual_mode(self):
        """Test choix IA en mode manuel"""
        self.manager.user_preferences["ai_mode"] = "manual"

        result = self.manager.choose_best_ai("sentiment")

        assert result == "local"

    def test_choose_best_ai_sentiment_with_huggingface(self):
        """Test choix IA pour sentiment avec HuggingFace disponible"""
        self.manager.user_preferences["ai_mode"] = "auto"

        with patch.object(self.manager, '_check_huggingface_quota', return_value=True):
            result = self.manager.choose_best_ai("sentiment")

            assert result == "huggingface"

    def test_choose_best_ai_realtime_speed_priority(self):
        """Test choix IA pour temps réel avec priorité vitesse"""
        self.manager.user_preferences["ai_mode"] = "auto"

        result = self.manager.choose_best_ai("realtime", priority="speed")

        assert result == "local"

    def test_choose_best_ai_complex_accuracy_premium(self):
        """Test choix IA pour tâche complexe avec précision et premium disponible"""
        self.manager.user_preferences["ai_mode"] = "auto"

        with patch.object(self.manager, '_check_huggingface_quota', return_value=False), \
             patch.object(self.manager, '_check_premium_budget', return_value=True):
            result = self.manager.choose_best_ai("sentiment", priority="accuracy", complexity="complex")

            assert result == "premium"

    def test_choose_best_ai_technical_local(self):
        """Test choix IA pour analyse technique"""
        self.manager.user_preferences["ai_mode"] = "auto"

        result = self.manager.choose_best_ai("technical")

        assert result == "local"

    def test_choose_best_ai_fallback_local(self):
        """Test choix IA fallback vers local"""
        self.manager.user_preferences["ai_mode"] = "auto"

        with patch.object(self.manager, '_check_huggingface_quota', return_value=False), \
             patch.object(self.manager, '_check_premium_budget', return_value=False):
            result = self.manager.choose_best_ai("sentiment", complexity="medium")

            assert result == "local"

    def test_check_huggingface_quota_with_api_key(self):
        """Test vérification quota HuggingFace avec clé API"""
        self.manager.free_ai = MagicMock()
        self.manager.free_ai.request_history = [1, 2, 3]  # 3 requêtes

        with patch.object(self.manager, '_get_huggingface_api_key', return_value="test_key"):
            result = self.manager._check_huggingface_quota()

            assert result is True

    def test_check_huggingface_quota_no_api_key(self):
        """Test vérification quota HuggingFace sans clé API"""
        with patch.object(self.manager, '_get_huggingface_api_key', return_value=""):
            result = self.manager._check_huggingface_quota()

            assert result is False

    def test_check_huggingface_quota_quota_exceeded(self):
        """Test vérification quota HuggingFace dépassé"""
        self.manager.free_ai = MagicMock()
        self.manager.free_ai.request_history = list(range(1000))  # 1000 requêtes

        with patch.object(self.manager, '_get_huggingface_api_key', return_value="test_key"):
            result = self.manager._check_huggingface_quota()

            assert result is False

    def test_get_huggingface_api_key_success(self):
        """Test récupération clé API HuggingFace réussie"""
        mock_config = {
            "providers": {
                "ai_providers": [
                    {
                        "name": "HuggingFace",
                        "config": {"api_key": "test_api_key_123"}
                    }
                ]
            }
        }

        with patch('dash_modules.core.api_config.api_config') as mock_api_config:
            mock_api_config.config = mock_config

            result = self.manager._get_huggingface_api_key()

            assert result == "test_api_key_123"

    def test_get_huggingface_api_key_not_found(self):
        """Test récupération clé API HuggingFace non trouvée"""
        mock_config = {
            "providers": {
                "ai_providers": []
            }
        }

        with patch('dash_modules.core.api_config.api_config') as mock_api_config:
            mock_api_config.config = mock_config

            result = self.manager._get_huggingface_api_key()

            assert result == ""

    def test_check_premium_budget_enabled(self):
        """Test vérification budget premium activé"""
        self.manager.user_preferences["max_cost_per_month"] = 10
        self.manager.user_preferences["premium_enabled"] = True

        result = self.manager._check_premium_budget()

        assert result is True

    def test_check_premium_budget_disabled(self):
        """Test vérification budget premium désactivé"""
        self.manager.user_preferences["max_cost_per_month"] = 0
        self.manager.user_preferences["premium_enabled"] = False

        result = self.manager._check_premium_budget()

        assert result is False

    @patch('dash_modules.ai_engine.local_ai_engine.LocalAIEngine')
    @patch('dash_modules.ai_engine.free_ai_engine.FreeAIEngine')
    @patch('dash_modules.ai_engine.smart_ai_engine.SmartAIEngine')
    def test_analyze_with_best_ai_local_fallback(self, mock_smart_ai, mock_free_ai, mock_local_ai):
        """Test analyse avec meilleure IA - fallback local"""
        # Setup mocks
        mock_local_instance = MagicMock()
        mock_local_instance.analyze_sentiment.return_value = {"sentiment": "neutral", "confidence": 50}
        mock_local_ai.return_value = mock_local_instance

        self.manager.initialize_engines()

        data = {"news_articles": ["Test news"]}
        result = self.manager.analyze_with_best_ai(data, "sentiment")

        assert result["sentiment"] == "neutral"
        assert result["metadata"]["ai_used"] == "local"
        assert result["metadata"]["auto_selected"] is True
        assert "execution_time_ms" in result["metadata"]

    @patch('dash_modules.ai_engine.local_ai_engine.LocalAIEngine')
    @patch('dash_modules.ai_engine.free_ai_engine.FreeAIEngine')
    @patch('dash_modules.ai_engine.smart_ai_engine.SmartAIEngine')
    def test_analyze_with_best_ai_huggingface(self, mock_smart_ai, mock_free_ai, mock_local_ai):
        """Test analyse avec meilleure IA - HuggingFace"""
        # Setup mocks
        mock_free_instance = MagicMock()
        mock_free_instance.analyze_with_huggingface.return_value = {"sentiment": "positive", "confidence": 80}
        mock_free_instance.request_history = []
        mock_free_ai.return_value = mock_free_instance

        mock_local_instance = MagicMock()
        mock_local_ai.return_value = mock_local_instance

        self.manager.initialize_engines()
        self.manager.user_preferences["ai_mode"] = "auto"

        # Mock pour permettre HuggingFace
        with patch.object(self.manager, '_get_huggingface_api_key', return_value="test_key"):
            data = {"news_articles": ["Bullish news"]}
            result = self.manager.analyze_with_best_ai(data, "sentiment")

            assert result["sentiment"] == "positive"
            assert result["metadata"]["ai_used"] == "huggingface"

    @patch('dash_modules.ai_engine.local_ai_engine.LocalAIEngine')
    @patch('dash_modules.ai_engine.free_ai_engine.FreeAIEngine')
    @patch('dash_modules.ai_engine.smart_ai_engine.SmartAIEngine')
    def test_analyze_with_best_ai_technical(self, mock_smart_ai, mock_free_ai, mock_local_ai):
        """Test analyse technique avec meilleure IA"""
        # Setup mocks
        mock_local_instance = MagicMock()
        mock_local_instance.analyze_technical_pattern_simple.return_value = {
            "pattern": "uptrend", "confidence": 75
        }
        mock_local_ai.return_value = mock_local_instance

        self.manager.initialize_engines()

        data = {"price_data": [100, 105, 110], "indicators": {"rsi": 65}}
        result = self.manager.analyze_with_best_ai(data, "technical")

        assert result["pattern"] == "uptrend"
        assert result["metadata"]["ai_used"] == "local"
        assert result["metadata"]["task_type"] == "technical"

    @patch('dash_modules.ai_engine.local_ai_engine.LocalAIEngine')
    @patch('dash_modules.ai_engine.free_ai_engine.FreeAIEngine')
    @patch('dash_modules.ai_engine.smart_ai_engine.SmartAIEngine')
    def test_analyze_with_best_ai_translation(self, mock_smart_ai, mock_free_ai, mock_local_ai):
        """Test traduction avec meilleure IA"""
        # Setup mocks
        mock_local_instance = MagicMock()
        mock_local_instance.translate_text.return_value = {
            "translated_text": "Bonjour le monde", "confidence": 85
        }
        mock_local_ai.return_value = mock_local_instance

        self.manager.initialize_engines()

        data = {"text": "Hello world", "target_lang": "fr"}
        result = self.manager.analyze_with_best_ai(data, "translation")

        assert result["translated_text"] == "Bonjour le monde"
        assert result["metadata"]["task_type"] == "translation"

    @patch('dash_modules.ai_engine.local_ai_engine.LocalAIEngine')
    @patch('dash_modules.ai_engine.free_ai_engine.FreeAIEngine')
    @patch('dash_modules.ai_engine.smart_ai_engine.SmartAIEngine')
    def test_translate_to_french_already_french(self, mock_smart_ai, mock_free_ai, mock_local_ai):
        """Test traduction vers français - texte déjà en français"""
        self.manager.initialize_engines()

        # Texte avec plusieurs indicateurs français pour éviter la traduction
        text = "Bonjour le monde, comment allez-vous aujourd'hui dans la ville de Paris ?"
        result = self.manager.translate_to_french(text)

        # Devrait retourner le texte original sans traduction car détecté comme français
        assert result == text

    @patch('dash_modules.ai_engine.local_ai_engine.LocalAIEngine')
    @patch('dash_modules.ai_engine.free_ai_engine.FreeAIEngine')
    @patch('dash_modules.ai_engine.smart_ai_engine.SmartAIEngine')
    def test_translate_to_french_english_text(self, mock_smart_ai, mock_free_ai, mock_local_ai):
        """Test traduction vers français - texte anglais"""
        # Setup mocks
        mock_local_instance = MagicMock()
        mock_local_instance.translate_text.return_value = {
            "translated_text": "Bonjour", "confidence": 85
        }
        mock_local_ai.return_value = mock_local_instance

        self.manager.initialize_engines()

        with patch.object(self.manager, 'analyze_with_best_ai') as mock_analyze:
            mock_analyze.return_value = {"translated_text": "Bonjour"}

            result = self.manager.translate_to_french("Hello")

            assert result == "Bonjour"
            mock_analyze.assert_called_once()

    def test_get_ai_status(self):
        """Test récupération status IA"""
        # Setup mock free_ai
        self.manager.free_ai = MagicMock()
        self.manager.free_ai.request_history = [1, 2, 3]

        with patch.object(self.manager, '_check_huggingface_quota', return_value=True), \
             patch.object(self.manager, '_check_premium_budget', return_value=False):
            status = self.manager.get_ai_status()

            assert status["local"]["available"] is False  # Pas initialisé = False
            assert status["huggingface"]["available"] is True
            assert status["premium"]["available"] is False
            assert status["current_selection"] == "auto"
            assert "recommendations" in status

    def test_get_recommendations(self):
        """Test génération recommandations"""
        recommendations = self.manager._get_recommendations()

        # Avec config par défaut (tout activé), pas de recommandations
        assert isinstance(recommendations, list)
        assert len(recommendations) == 0

    def test_update_preferences(self):
        """Test mise à jour préférences"""
        new_prefs = {"ai_mode": "manual", "max_cost_per_month": 5}

        with patch.object(self.manager, '_save_user_preferences') as mock_save:
            self.manager.update_preferences(new_prefs)

            assert self.manager.user_preferences["ai_mode"] == "manual"
            assert self.manager.user_preferences["max_cost_per_month"] == 5
            mock_save.assert_called_once()

    def test_get_usage_stats(self):
        """Test récupération statistiques utilisation"""
        # Setup mock free_ai
        self.manager.free_ai = MagicMock()
        self.manager.free_ai.request_history = [1, 2, 3, 4, 5]

        stats = self.manager.get_usage_stats()

        assert stats["today_huggingface_calls"] == 5
        assert stats["remaining_free_calls"] == 95
        assert stats["estimated_monthly_cost"] == 0
        assert stats["performance_summary"]["fastest"] == "local"
        assert stats["performance_summary"]["most_accurate"] == "premium"
        assert stats["performance_summary"]["best_value"] == "huggingface"

    def test_analyze_with_best_ai_error_fallback(self):
        """Test analyse avec erreur et fallback"""
        # Setup mock local_ai
        self.manager.local_ai = MagicMock()
        self.manager.local_ai.analyze_sentiment.return_value = {"sentiment": "neutral"}

        # Simuler erreur avec HuggingFace
        with patch.object(self.manager, 'choose_best_ai', return_value="huggingface"), \
             patch.object(self.manager, '_analyze_with_huggingface', side_effect=Exception("API Error")):
            data = {"news_articles": ["Test"]}
            result = self.manager.analyze_with_best_ai(data, "sentiment")

            # Devrait fallback vers local
            assert result["sentiment"] == "neutral"

    def test_analyze_with_local_unsupported_task(self):
        """Test analyse locale avec tâche non supportée"""
        self.manager.local_ai = MagicMock()

        data = {"unsupported": "data"}
        result = self.manager._analyze_with_local(data, "unsupported_task")

        assert result["error"] == "Type de tâche non supporté"