"""
Tests pour Economic Events Provider - Fournisseur de données d'événements économiques
Tests se concentrant sur la génération de données simulées sans appels réseau
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from dash_modules.data_providers.economic_events_provider import (
    EconomicEventsProvider,
    EventStatus,
    economic_events_provider
)


class TestEconomicEventsProvider:
    """Tests pour EconomicEventsProvider"""

    def test_initialization(self):
        """Test d'initialisation du fournisseur d'événements"""
        provider = EconomicEventsProvider()

        assert hasattr(provider, 'events_config')
        assert hasattr(provider, 'cache')
        assert hasattr(provider, 'historical_data')
        assert hasattr(provider, 'realistic_ranges')
        assert isinstance(provider.historical_data, dict)
        assert len(provider.historical_data) > 0

    def test_generate_historical_data(self):
        """Test génération des données historiques"""
        provider = EconomicEventsProvider()

        # Vérifier que les données historiques sont générées
        assert len(provider.historical_data) > 0

        # Vérifier qu'un événement connu est présent
        assert "us_nfp" in provider.historical_data

        # Vérifier la structure des données
        hist_data = provider.historical_data["us_nfp"]
        assert "last_value" in hist_data
        assert "trend" in hist_data
        assert "volatility" in hist_data
        assert hist_data["trend"] in ["up", "down", "stable"]
        assert 0.1 <= hist_data["volatility"] <= 0.5

    def test_generate_realistic_forecast(self):
        """Test génération de prévisions réalistes"""
        provider = EconomicEventsProvider()

        # Tester avec un événement connu
        base_value = 200000.0  # Valeur de base pour NFP
        forecast, actual = provider._generate_realistic_forecast("us_nfp", base_value)

        # Vérifier que les valeurs sont dans la plage réaliste
        min_val, max_val = provider.realistic_ranges["us_nfp"]
        assert min_val <= forecast <= max_val
        assert min_val <= actual <= max_val

        # Vérifier que les valeurs sont arrondies
        assert isinstance(forecast, float)
        assert isinstance(actual, float)

    def test_should_include_event_weekly(self):
        """Test inclusion d'événements hebdomadaires"""
        provider = EconomicEventsProvider()

        # Créer un événement hebdomadaire fictif
        from dash_modules.data_providers.economic_events_config import EconomicEvent, EventCategory, EventImpact, EventFrequency

        weekly_event = EconomicEvent(
            id="test_weekly",
            name="Test Weekly Event",
            description="Test",
            country="US",
            category=EventCategory.EMPLOYMENT,
            impact=EventImpact.MEDIUM,
            frequency=EventFrequency.WEEKLY,
            source="Test"
        )

        # Tester différents jours de la semaine
        test_date = datetime(2024, 1, 1)  # Lundi

        # Devrait être inclus le jeudi (weekday = 3)
        thursday = test_date + timedelta(days=3)  # Jeudi
        assert provider._should_include_event(weekly_event, thursday)

        # Ne devrait pas être inclus les autres jours
        monday = test_date
        assert not provider._should_include_event(weekly_event, monday)

    def test_should_include_event_monthly(self):
        """Test inclusion d'événements mensuels"""
        provider = EconomicEventsProvider()

        from dash_modules.data_providers.economic_events_config import EconomicEvent, EventCategory, EventImpact, EventFrequency

        monthly_event = EconomicEvent(
            id="test_monthly",
            name="Test Monthly Event",
            description="Test",
            country="US",
            category=EventCategory.ECONOMIC_ACTIVITY,
            impact=EventImpact.MEDIUM,
            frequency=EventFrequency.MONTHLY,
            source="Test"
        )

        # Tester le premier jour du mois (devrait être inclus)
        first_day = datetime(2024, 1, 1)
        assert provider._should_include_event(monthly_event, first_day)

        # Tester un jour de fin de mois (devrait être inclus)
        end_month = datetime(2024, 1, 30)
        assert provider._should_include_event(monthly_event, end_month)

        # Tester un jour au milieu qui n'est pas inclus
        mid_month = datetime(2024, 1, 15)
        assert not provider._should_include_event(monthly_event, mid_month)

    def test_get_first_weekday_of_month(self):
        """Test obtention du premier jour de semaine du mois"""
        provider = EconomicEventsProvider()

        # Premier vendredi de janvier 2024 (4 = vendredi)
        first_friday = provider._get_first_weekday_of_month(2024, 1, 4)
        expected = datetime(2024, 1, 5).date()  # 5 janvier 2024 était un vendredi
        assert first_friday == expected

    def test_generate_event_data(self):
        """Test génération des données d'événement"""
        provider = EconomicEventsProvider()

        from dash_modules.data_providers.economic_events_config import EconomicEvent, EventCategory, EventImpact, EventFrequency

        test_event = EconomicEvent(
            id="us_nfp",
            name="Non-Farm Payrolls (NFP)",
            description="Test NFP",
            country="US",
            category=EventCategory.EMPLOYMENT,
            impact=EventImpact.CRITICAL,
            frequency=EventFrequency.MONTHLY,
            source="BLS",
            time_of_release="13:30",
            unit="emplois"
        )

        test_date = datetime(2024, 1, 15, 13, 30)
        event_data = provider._generate_event_data(test_event, test_date)

        # Vérifier la structure des données
        required_keys = [
            "id", "name", "description", "country", "category", "impact",
            "datetime", "date", "time", "status", "unit", "source", "flag"
        ]

        for key in required_keys:
            assert key in event_data

        assert event_data["id"] == "us_nfp"
        assert event_data["name"] == "Non-Farm Payrolls (NFP)"
        assert event_data["country"] == "US"
        assert event_data["flag"] == "🇺🇸"

    def test_calculate_market_impact(self):
        """Test calcul de l'impact marché"""
        provider = EconomicEventsProvider()

        from dash_modules.data_providers.economic_events_config import EconomicEvent, EventCategory, EventImpact, EventFrequency

        test_event = EconomicEvent(
            id="us_nfp",
            name="NFP",
            description="Test",
            country="US",
            category=EventCategory.EMPLOYMENT,
            impact=EventImpact.CRITICAL,
            frequency=EventFrequency.MONTHLY,
            source="Test"
        )

        # Test sans valeurs (événement futur)
        impact = provider._calculate_market_impact(test_event, None, None)
        assert impact["expected_volatility"] == 2.5  # Critical impact
        assert impact["actual_volatility"] == 0.0
        assert impact["direction"] == "neutral"

        # Test avec surprise
        impact = provider._calculate_market_impact(test_event, 200000.0, 250000.0)
        assert impact["expected_volatility"] == 2.5
        assert impact["actual_volatility"] > 2.5  # Devrait être plus élevé avec surprise
        assert impact["direction"] in ["positive", "negative", "neutral"]

    def test_get_events_for_period(self):
        """Test récupération d'événements pour une période"""
        provider = EconomicEventsProvider()

        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 7)  # Une semaine

        events = provider.get_events_for_period(start_date, end_date)

        assert isinstance(events, list)
        # Devrait avoir quelques événements dans une semaine
        assert len(events) >= 0

        # Vérifier la structure des événements
        if events:
            event = events[0]
            required_keys = ["id", "name", "datetime", "status", "impact"]
            for key in required_keys:
                assert key in event

    def test_get_upcoming_events(self):
        """Test récupération des événements à venir"""
        provider = EconomicEventsProvider()

        upcoming = provider.get_upcoming_events(days_ahead=7)

        assert isinstance(upcoming, list)
        # Tous les événements devraient avoir le statut "upcoming"
        for event in upcoming:
            assert event["status"] == "upcoming"

    def test_get_recent_events(self):
        """Test récupération des événements récents"""
        provider = EconomicEventsProvider()

        recent = provider.get_recent_events(days_back=7)

        assert isinstance(recent, list)
        # Tous les événements devraient avoir le statut "released"
        for event in recent:
            assert event["status"] == "released"

    def test_get_events_by_impact(self):
        """Test récupération d'événements par impact"""
        provider = EconomicEventsProvider()

        critical_events = provider.get_events_by_impact("critical", days_range=30)

        assert isinstance(critical_events, list)
        for event in critical_events:
            assert event["impact"] == "critical"

    def test_search_events(self):
        """Test recherche d'événements"""
        provider = EconomicEventsProvider()

        # Rechercher des événements liés à l'emploi
        employment_events = provider.search_events("employment", days_range=30)

        assert isinstance(employment_events, list)
        # Au moins un événement devrait contenir "employment" dans ses champs
        if employment_events:
            found = False
            for event in employment_events:
                if ("employment" in event["name"].lower() or
                    "employment" in event["description"].lower() or
                    "employment" in event["country"].lower()):
                    found = True
                    break
            assert found, "Aucun événement trouvé pour 'employment'"

    def test_get_calendar_data(self):
        """Test récupération des données calendrier"""
        provider = EconomicEventsProvider()

        calendar_data = provider.get_calendar_data(1, 2024)  # Janvier 2024

        assert isinstance(calendar_data, dict)
        required_keys = ["month", "year", "events_by_day", "total_events", "critical_events", "high_impact_events"]
        for key in required_keys:
            assert key in calendar_data

        assert calendar_data["month"] == 1
        assert calendar_data["year"] == 2024
        assert isinstance(calendar_data["events_by_day"], dict)

    def test_global_instance(self):
        """Test de l'instance globale"""
        assert isinstance(economic_events_provider, EconomicEventsProvider)
        assert hasattr(economic_events_provider, 'events_config')
        assert hasattr(economic_events_provider, 'historical_data')


class TestEventStatus:
    """Tests pour l'énumération EventStatus"""

    def test_event_status_values(self):
        """Test valeurs de EventStatus"""
        assert EventStatus.UPCOMING.value == "upcoming"
        assert EventStatus.RELEASED.value == "released"
        assert EventStatus.REVISED.value == "revised"