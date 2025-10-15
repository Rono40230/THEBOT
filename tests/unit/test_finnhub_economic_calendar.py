"""
Tests pour Finnhub Economic Calendar - API calendrier économique professionnel
Tests se concentrant sur les fonctionnalités sans appels réseau réels (mocks)
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from dash_modules.data_providers.finnhub_economic_calendar import (
    FinnhubEconomicCalendar,
    finnhub_calendar
)


class TestFinnhubEconomicCalendar:
    """Tests pour FinnhubEconomicCalendar"""

    def test_initialization(self):
        """Test d'initialisation du calendrier économique"""
        calendar = FinnhubEconomicCalendar(api_key="test_key")

        assert calendar.api_key == "test_key"
        assert calendar.base_url == "https://finnhub.io/api/v1"
        assert isinstance(calendar.country_mapping, dict)
        assert isinstance(calendar.impact_mapping, dict)
        assert isinstance(calendar.category_keywords, dict)
        assert len(calendar.country_mapping) > 0
        assert len(calendar.impact_mapping) > 0
        assert len(calendar.category_keywords) > 0

    def test_country_mapping(self):
        """Test du mapping des pays"""
        calendar = FinnhubEconomicCalendar()

        # Vérifier quelques mappings importants
        assert calendar.country_mapping["US"] == "United States"
        assert calendar.country_mapping["EU"] == "European Union"
        assert calendar.country_mapping["UK"] == "United Kingdom"
        assert calendar.country_mapping["JP"] == "Japan"
        assert calendar.country_mapping["CN"] == "China"

    def test_impact_mapping(self):
        """Test du mapping des impacts"""
        calendar = FinnhubEconomicCalendar()

        assert calendar.impact_mapping["1"] == "low"
        assert calendar.impact_mapping["2"] == "medium"
        assert calendar.impact_mapping["3"] == "high"
        assert calendar.impact_mapping["4"] == "critical"

    def test_categorize_event(self):
        """Test de la catégorisation d'événements"""
        calendar = FinnhubEconomicCalendar()

        # Test événements monétaires
        assert calendar._categorize_event("Fed Interest Rate Decision") == "monetary_policy"
        assert calendar._categorize_event("ECB Monetary Policy Meeting") == "monetary_policy"

        # Test événements inflation
        assert calendar._categorize_event("US CPI Inflation") == "inflation"
        assert calendar._categorize_event("Eurozone PPI Data") == "inflation"

        # Test événements emploi
        assert calendar._categorize_event("Non-Farm Payrolls") == "employment"
        assert calendar._categorize_event("Unemployment Rate") == "employment"

        # Test événements GDP
        assert calendar._categorize_event("GDP Growth Quarterly") == "gdp_growth"
        assert calendar._categorize_event("Economic Output Data") == "gdp_growth"

        # Test événements industriels
        assert calendar._categorize_event("Manufacturing PMI") == "industrial"
        assert calendar._categorize_event("Industrial Production") == "industrial"

        # Test événements retail
        assert calendar._categorize_event("Retail Sales Data") == "retail"
        assert calendar._categorize_event("Consumer Spending") == "retail"

        # Test événements housing
        assert calendar._categorize_event("Housing Starts") == "housing"
        assert calendar._categorize_event("Building Permits") == "housing"

        # Test événements trade
        assert calendar._categorize_event("Trade Balance") == "trade"
        assert calendar._categorize_event("Exports Data") == "trade"

        # Test événements confidence
        assert calendar._categorize_event("Consumer Confidence") == "confidence"
        assert calendar._categorize_event("Business Sentiment") == "confidence"

        # Test événement inconnu
        assert calendar._categorize_event("Unknown Event") == "other"

    def test_build_description(self):
        """Test construction de descriptions"""
        calendar = FinnhubEconomicCalendar()

        # Test avec toutes les valeurs
        desc = calendar._build_description("Test Event", "2.5", "2.8", "2.3")
        assert "Test Event" in desc
        assert "Précédent: 2.3" in desc
        assert "Prévision: 2.5" in desc
        assert "Réel: 2.8" in desc

        # Test avec valeurs partielles
        desc = calendar._build_description("Test Event", "", "2.8", "")
        assert "Test Event" in desc
        assert "Réel: 2.8" in desc
        assert "Précédent:" not in desc
        assert "Prévision:" not in desc

        # Test avec valeurs vides
        desc = calendar._build_description("Test Event", "", "", "")
        assert desc == "Test Event"

    def test_passes_filters(self):
        """Test des filtres d'événements"""
        calendar = FinnhubEconomicCalendar()

        event = {
            "country_code": "US",
            "country": "United States",
            "impact": "high"
        }

        # Test sans filtres
        assert calendar._passes_filters(event, None, None)

        # Test filtre pays (code pays)
        assert calendar._passes_filters(event, ["US", "EU"], None)
        assert not calendar._passes_filters(event, ["EU", "UK"], None)

        # Test filtre pays (nom pays)
        assert calendar._passes_filters(event, ["United States"], None)
        assert not calendar._passes_filters(event, ["European Union"], None)

        # Test filtre impact
        assert calendar._passes_filters(event, None, ["high", "critical"])
        assert not calendar._passes_filters(event, None, ["low", "medium"])

        # Test filtres combinés
        assert calendar._passes_filters(event, ["US"], ["high"])
        assert not calendar._passes_filters(event, ["US"], ["low"])
        assert not calendar._passes_filters(event, ["EU"], ["high"])

    def test_format_event(self):
        """Test formatage d'événement"""
        calendar = FinnhubEconomicCalendar()

        # Événement brut simulé
        raw_event = {
            "event": "Fed Interest Rate Decision",
            "country": "US",
            "time": 1693526400,  # Timestamp
            "impact": 3,  # High impact
            "estimate": "5.25-5.50",
            "actual": "5.25-5.50",
            "previous": "5.25-5.50"
        }

        formatted = calendar._format_event(raw_event)

        assert formatted is not None
        assert formatted["title"] == "Fed Interest Rate Decision"
        assert formatted["country"] == "United States"
        assert formatted["country_code"] == "US"
        assert formatted["impact"] == "high"
        assert formatted["category"] == "monetary_policy"
        assert formatted["estimate"] == "5.25-5.50"
        assert formatted["actual"] == "5.25-5.50"
        assert formatted["previous"] == "5.25-5.50"
        assert formatted["source"] == "Finnhub"
        assert "url" in formatted
        assert "is_released" in formatted

    def test_format_event_missing_data(self):
        """Test formatage d'événement avec données manquantes"""
        calendar = FinnhubEconomicCalendar()

        # Événement minimal
        raw_event = {
            "event": "Test Event",
            "country": "XX",  # Pays inconnu
        }

        formatted = calendar._format_event(raw_event)

        assert formatted is not None
        assert formatted["title"] == "Test Event"
        assert formatted["country"] == "XX"  # Devrait garder le code original
        assert formatted["impact"] == "medium"  # Valeur par défaut
        assert formatted["category"] == "other"  # Catégorie par défaut

    def test_get_fallback_events(self):
        """Test génération d'événements de fallback"""
        calendar = FinnhubEconomicCalendar()

        fallback_events = calendar._get_fallback_events()

        assert isinstance(fallback_events, list)
        assert len(fallback_events) > 50  # Devrait avoir beaucoup d'événements

        # Vérifier la structure d'un événement
        if fallback_events:
            event = fallback_events[0]
            required_keys = [
                "title", "description", "event_date", "event_time",
                "country", "country_code", "impact", "category",
                "is_released", "estimate", "actual", "previous", "source", "url"
            ]
            for key in required_keys:
                assert key in event

            # Vérifier que certains événements importants sont présents
            titles = [e["title"] for e in fallback_events]
            assert "Fed Interest Rate Decision" in titles
            assert "US Non-Farm Payrolls" in titles
            assert "ECB Monetary Policy Meeting" in titles

    @patch('requests.Session.get')
    def test_test_connection_success(self, mock_get):
        """Test connexion API réussie"""
        calendar = FinnhubEconomicCalendar(api_key="test_key")

        # Mock réponse réussie
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = calendar.test_connection()

        assert result["status"] == "success"
        assert "accessible" in result["message"]
        assert "test_key" in result["api_key"]

    @patch('requests.Session.get')
    def test_test_connection_failure(self, mock_get):
        """Test connexion API échouée"""
        calendar = FinnhubEconomicCalendar(api_key="test_key")

        # Mock exception
        mock_get.side_effect = Exception("Connection failed")

        result = calendar.test_connection()

        assert result["status"] == "error"
        assert "erreur" in result["message"].lower()
        assert "test_key" in result["api_key"]

    @patch('requests.Session.get')
    def test_get_economic_events_success(self, mock_get):
        """Test récupération d'événements réussie"""
        calendar = FinnhubEconomicCalendar(api_key="test_key")

        # Mock réponse API
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "economicCalendar": [
                {
                    "event": "Fed Rate Decision",
                    "country": "US",
                    "time": 1693526400,
                    "impact": 3,
                    "estimate": "5.25",
                    "actual": "5.25",
                    "previous": "5.25"
                }
            ]
        }
        mock_get.return_value = mock_response

        events = calendar.get_economic_events(days_ahead=7)

        assert isinstance(events, list)
        assert len(events) == 1
        assert events[0]["title"] == "Fed Rate Decision"
        assert events[0]["impact"] == "high"

    @patch('requests.Session.get')
    def test_get_economic_events_api_error(self, mock_get):
        """Test récupération d'événements avec erreur API"""
        calendar = FinnhubEconomicCalendar(api_key="test_key")

        # Mock exception API
        mock_get.side_effect = Exception("API Error")

        events = calendar.get_economic_events(days_ahead=7)

        # Devrait retourner des événements de fallback
        assert isinstance(events, list)
        assert len(events) > 0  # Fallback events

    @patch('requests.Session.get')
    def test_get_economic_events_with_filters(self, mock_get):
        """Test récupération d'événements avec filtres"""
        calendar = FinnhubEconomicCalendar(api_key="test_key")

        # Mock réponse API avec événements qui seront filtrés
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "economicCalendar": [
                {
                    "event": "US Fed Rate Decision",
                    "country": "US",
                    "time": 1693526400,
                    "impact": 3,  # high
                    "estimate": "5.25",
                    "actual": "5.25",
                    "previous": "5.25"
                },
                {
                    "event": "EU ECB Meeting",
                    "country": "EU",
                    "time": 1693612800,
                    "impact": 2,  # medium/low
                    "estimate": "4.0",
                    "actual": "4.0",
                    "previous": "4.0"
                }
            ]
        }
        mock_get.return_value = mock_response

        # Test filtre pays
        events = calendar.get_economic_events(countries=["US"])
        assert len(events) == 1
        assert events[0]["country_code"] == "US"

        # Test filtre impact
        events = calendar.get_economic_events(impacts=["medium", "low"])
        assert len(events) == 1
        assert events[0]["impact"] == "medium"

        # Test filtres combinés
        events = calendar.get_economic_events(countries=["EU"], impacts=["medium"])
        assert len(events) == 1
        assert events[0]["country_code"] == "EU"
        assert events[0]["impact"] == "medium"

    def test_global_instance(self):
        """Test de l'instance globale"""
        assert isinstance(finnhub_calendar, FinnhubEconomicCalendar)
        assert hasattr(finnhub_calendar, 'api_key')
        assert hasattr(finnhub_calendar, 'base_url')
        assert hasattr(finnhub_calendar, 'country_mapping')