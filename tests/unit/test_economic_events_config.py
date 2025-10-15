"""
Tests pour Economic Events Config - Configuration des événements économiques
Tests se concentrant sur les fonctionnalités de configuration sans appels réseau
"""

import pytest

from dash_modules.data_providers.economic_events_config import (
    EconomicEventsConfig,
    EconomicEvent,
    EventImpact,
    EventCategory,
    EventFrequency,
    economic_events_config
)


class TestEconomicEventsConfig:
    """Tests pour EconomicEventsConfig"""

    def test_initialization(self):
        """Test d'initialisation de la configuration"""
        config = EconomicEventsConfig()

        assert hasattr(config, 'events')
        assert hasattr(config, 'country_flags')
        assert isinstance(config.events, list)
        assert isinstance(config.country_flags, dict)
        assert len(config.events) > 0  # Devrait avoir des événements

    def test_country_flags(self):
        """Test des drapeaux de pays"""
        config = EconomicEventsConfig()

        expected_flags = {
            "US": "🇺🇸",
            "EU": "🇪🇺",
            "UK": "🇬🇧",
            "JP": "🇯🇵",
            "CN": "🇨🇳",
            "CA": "🇨🇦",
            "AU": "🇦🇺",
            "GLOBAL": "🌍",
        }

        assert config.country_flags == expected_flags

    def test_get_event_by_id(self):
        """Test récupération d'événement par ID"""
        config = EconomicEventsConfig()

        # Tester avec un événement qui devrait exister
        event = config.get_event_by_id("us_nfp")
        assert event is not None
        assert event.id == "us_nfp"
        assert event.name == "Non-Farm Payrolls (NFP)"
        assert event.country == "US"
        assert event.impact == EventImpact.CRITICAL

        # Tester avec un ID inexistant
        nonexistent = config.get_event_by_id("nonexistent")
        assert nonexistent is None

    def test_get_events_by_country(self):
        """Test récupération d'événements par pays"""
        config = EconomicEventsConfig()

        us_events = config.get_events_by_country("US")
        assert isinstance(us_events, list)
        assert len(us_events) > 0

        # Vérifier que tous les événements sont pour les US
        for event in us_events:
            assert event.country == "US"

        # Tester avec un pays sans événements
        empty_events = config.get_events_by_country("XX")
        assert empty_events == []

    def test_get_events_by_category(self):
        """Test récupération d'événements par catégorie"""
        config = EconomicEventsConfig()

        employment_events = config.get_events_by_category(EventCategory.EMPLOYMENT)
        assert isinstance(employment_events, list)
        assert len(employment_events) > 0

        # Vérifier que tous les événements sont de la catégorie employment
        for event in employment_events:
            assert event.category == EventCategory.EMPLOYMENT

    def test_get_events_by_impact(self):
        """Test récupération d'événements par impact"""
        config = EconomicEventsConfig()

        critical_events = config.get_events_by_impact(EventImpact.CRITICAL)
        assert isinstance(critical_events, list)
        assert len(critical_events) > 0

        # Vérifier que tous les événements ont l'impact critical
        for event in critical_events:
            assert event.impact == EventImpact.CRITICAL

    def test_get_enabled_events(self):
        """Test récupération des événements activés"""
        config = EconomicEventsConfig()

        enabled_events = config.get_enabled_events()
        assert isinstance(enabled_events, list)

        # Par défaut, tous les événements devraient être activés
        total_events = len(config.events)
        enabled_count = len(enabled_events)
        assert enabled_count == total_events

        # Vérifier que tous sont activés
        for event in enabled_events:
            assert event.enabled is True

    def test_enable_disable_event(self):
        """Test activation/désactivation d'événement"""
        config = EconomicEventsConfig()

        # Trouver un événement à tester
        test_event = config.events[0]
        event_id = test_event.id

        # Désactiver
        result = config.disable_event(event_id)
        assert result is True

        # Vérifier qu'il est désactivé
        event = config.get_event_by_id(event_id)
        assert event.enabled is False

        # Réactiver
        result = config.enable_event(event_id)
        assert result is True

        # Vérifier qu'il est réactivé
        event = config.get_event_by_id(event_id)
        assert event.enabled is True

        # Tester avec un ID inexistant
        result = config.disable_event("nonexistent")
        assert result is False

    def test_get_events_summary(self):
        """Test du résumé statistique des événements"""
        config = EconomicEventsConfig()

        summary = config.get_events_summary()
        assert isinstance(summary, dict)

        # Vérifier les clés principales
        required_keys = ["total", "enabled", "disabled", "by_impact", "by_category", "by_country"]
        for key in required_keys:
            assert key in summary

        # Vérifier que total > 0
        assert summary["total"] > 0
        assert summary["enabled"] > 0

        # Vérifier les sous-dictionnaires
        assert isinstance(summary["by_impact"], dict)
        assert isinstance(summary["by_category"], dict)
        assert isinstance(summary["by_country"], dict)

    def test_global_instance(self):
        """Test de l'instance globale"""
        assert isinstance(economic_events_config, EconomicEventsConfig)
        assert hasattr(economic_events_config, 'events')
        assert len(economic_events_config.events) > 0


class TestEconomicEvent:
    """Tests pour la classe EconomicEvent"""

    def test_event_creation(self):
        """Test création d'événement économique"""
        event = EconomicEvent(
            id="test_event",
            name="Test Event",
            description="A test economic event",
            country="US",
            category=EventCategory.EMPLOYMENT,
            impact=EventImpact.HIGH,
            frequency=EventFrequency.MONTHLY,
            source="Test Source",
            time_of_release="14:00",
            unit="%",
            enabled=True
        )

        assert event.id == "test_event"
        assert event.name == "Test Event"
        assert event.country == "US"
        assert event.category == EventCategory.EMPLOYMENT
        assert event.impact == EventImpact.HIGH
        assert event.frequency == EventFrequency.MONTHLY
        assert event.enabled is True

    def test_event_defaults(self):
        """Test valeurs par défaut d'événement"""
        event = EconomicEvent(
            id="test_event",
            name="Test Event",
            description="A test economic event",
            country="US",
            category=EventCategory.EMPLOYMENT,
            impact=EventImpact.HIGH,
            frequency=EventFrequency.MONTHLY,
            source="Test Source"
        )

        # Vérifier les valeurs par défaut
        assert event.time_of_release is None
        assert event.previous_value is None
        assert event.forecast_value is None
        assert event.actual_value is None
        assert event.unit is None
        assert event.enabled is True


class TestEnums:
    """Tests pour les énumérations"""

    def test_event_impact_values(self):
        """Test valeurs de EventImpact"""
        assert EventImpact.CRITICAL.value == "critical"
        assert EventImpact.HIGH.value == "high"
        assert EventImpact.MEDIUM.value == "medium"
        assert EventImpact.LOW.value == "low"

    def test_event_category_values(self):
        """Test valeurs de EventCategory"""
        assert EventCategory.EMPLOYMENT.value == "employment"
        assert EventCategory.MONETARY_POLICY.value == "monetary_policy"
        assert EventCategory.INFLATION.value == "inflation"

    def test_event_frequency_values(self):
        """Test valeurs de EventFrequency"""
        assert EventFrequency.WEEKLY.value == "weekly"
        assert EventFrequency.MONTHLY.value == "monthly"
        assert EventFrequency.QUARTERLY.value == "quarterly"