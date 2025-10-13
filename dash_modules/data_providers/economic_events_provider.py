"""
Gestionnaire de données pour les événements économiques du calendrier
Simule un fournisseur d'API d'événements économiques avec données réalistes
"""

import random
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from .economic_events_config import (
    EconomicEvent,
    EventCategory,
    EventImpact,
    economic_events_config,
)


class EventStatus(Enum):
    """Statut d'un événement"""

    UPCOMING = "upcoming"
    RELEASED = "released"
    REVISED = "revised"


class EconomicEventsProvider:
    """Fournisseur de données d'événements économiques avec simulation réaliste"""

    def __init__(self):
        self.events_config = economic_events_config
        self.cache = {}
        self.last_update = None

        # Données historiques simulées pour cohérence
        self.historical_data = {}
        self._generate_historical_data()

        print("✅ Economic Events Provider initialisé")

    def _generate_historical_data(self):
        """Générer des données historiques cohérentes pour les événements"""

        # Valeurs réalistes pour les indicateurs principaux
        self.realistic_ranges = {
            "us_nfp": (150000, 350000),  # Emplois créés
            "us_unemployment_rate": (3.5, 6.0),  # %
            "us_initial_jobless_claims": (200000, 450000),  # Personnes
            "fed_rate_decision": (0.0, 5.5),  # %
            "us_cpi": (0.0, 6.0),  # % YoY
            "us_core_cpi": (0.0, 5.0),  # % YoY
            "us_pce": (0.0, 5.5),  # % YoY
            "us_gdp": (-2.0, 4.0),  # % QoQ
            "us_retail_sales": (-2.0, 3.0),  # % MoM
            "us_ism_manufacturing": (40.0, 65.0),  # Index
            "ez_cpi": (0.0, 4.0),  # % YoY
            "ecb_rate_decision": (0.0, 4.0),  # %
            "uk_cpi": (0.0, 5.0),  # % YoY
            "jp_cpi": (-1.0, 3.0),  # % YoY
            "cn_cpi": (0.0, 4.0),  # % YoY
            "eia_crude_oil": (-5000000, 5000000),  # Barils variation
        }

        # Générer l'historique
        for event_id, (min_val, max_val) in self.realistic_ranges.items():
            self.historical_data[event_id] = {
                "last_value": round(random.uniform(min_val, max_val), 1),
                "trend": random.choice(["up", "down", "stable"]),
                "volatility": random.uniform(0.1, 0.5),
            }

    def _generate_realistic_forecast(
        self, event_id: str, base_value: float
    ) -> Tuple[float, float]:
        """Générer prévision et valeur réelle cohérentes"""

        if event_id not in self.historical_data:
            return base_value, base_value

        hist = self.historical_data[event_id]
        volatility = hist["volatility"]

        # Prévision avec petite variation
        forecast_variation = random.uniform(-volatility / 2, volatility / 2)
        forecast = base_value + forecast_variation

        # Valeur réelle avec surprise occasionnelle
        surprise_chance = 0.3  # 30% de chance de surprise
        if random.random() < surprise_chance:
            # Surprise importante
            surprise_factor = (
                random.uniform(1.5, 3.0)
                if random.random() > 0.5
                else random.uniform(0.5, 0.8)
            )
            actual_variation = forecast_variation * surprise_factor
        else:
            # Variation normale
            actual_variation = random.uniform(-volatility, volatility)

        actual = base_value + actual_variation

        # Assurer la cohérence avec les plages réalistes
        if event_id in self.realistic_ranges:
            min_val, max_val = self.realistic_ranges[event_id]
            forecast = max(min_val, min(max_val, forecast))
            actual = max(min_val, min(max_val, actual))

        return round(forecast, 1), round(actual, 1)

    def get_events_for_period(
        self,
        start_date: datetime,
        end_date: datetime,
        selected_events: List[str] = None,
    ) -> List[Dict]:
        """Récupérer les événements pour une période donnée"""

        events_data = []

        # Filtrer par événements sélectionnés si spécifié
        events_to_process = self.events_config.get_enabled_events()
        if selected_events:
            events_to_process = [
                e for e in events_to_process if e.id in selected_events
            ]

        # Générer les événements pour la période
        current_date = start_date
        while current_date <= end_date:
            for event in events_to_process:
                # Simuler la programmation des événements selon leur fréquence
                should_include = self._should_include_event(event, current_date)

                if should_include:
                    event_data = self._generate_event_data(event, current_date)
                    events_data.append(event_data)

            current_date += timedelta(days=1)

        # Trier par date
        events_data.sort(key=lambda x: x["datetime"])

        return events_data

    def _should_include_event(self, event: EconomicEvent, date: datetime) -> bool:
        """Déterminer si un événement doit être inclus à une date donnée"""

        # Simulation basée sur la fréquence
        if event.frequency.value == "weekly":
            # Événements hebdomadaires (ex: Jobless Claims le jeudi)
            return date.weekday() == 3  # Jeudi

        elif event.frequency.value == "monthly":
            # Événements mensuels - premiers vendredis, mi-mois, etc.
            if event.id == "us_nfp":
                # NFP le premier vendredi du mois
                first_friday = self._get_first_weekday_of_month(
                    date.year, date.month, 4
                )  # 4 = vendredi
                return date.date() == first_friday
            elif "cpi" in event.id or "ppi" in event.id:
                # Inflation mi-mois
                return date.day in [13, 14, 15]
            else:
                # Autres événements mensuels
                return date.day in [1, 2, 3, 28, 29, 30]

        elif event.frequency.value == "quarterly":
            # Événements trimestriels
            return date.month in [1, 4, 7, 10] and date.day in [25, 26, 27, 28]

        elif event.frequency.value == "irregular":
            # Événements irréguliers - simulation aléatoire rare
            return random.random() < 0.02  # 2% de chance par jour

        return False

    def _get_first_weekday_of_month(
        self, year: int, month: int, weekday: int
    ) -> datetime:
        """Obtenir le premier jour de la semaine spécifique du mois"""
        first_day = datetime(year, month, 1)
        days_ahead = weekday - first_day.weekday()
        if days_ahead < 0:  # Jour déjà passé cette semaine
            days_ahead += 7
        return (first_day + timedelta(days=days_ahead)).date()

    def _generate_event_data(self, event: EconomicEvent, date: datetime) -> Dict:
        """Générer les données complètes pour un événement"""

        # Déterminer l'heure de l'événement
        event_time = datetime.combine(date.date(), datetime.min.time())
        if event.time_of_release:
            try:
                hour, minute = map(int, event.time_of_release.split(":"))
                event_time = event_time.replace(hour=hour, minute=minute)
            except:
                pass

        # Générer les valeurs
        base_value = None
        forecast_value = None
        actual_value = None
        previous_value = None

        if event.id in self.historical_data:
            hist = self.historical_data[event.id]
            base_value = hist["last_value"]

            # Déterminer si l'événement est dans le futur ou passé
            now = datetime.now()
            is_future = event_time > now

            if is_future:
                # Événement futur - générer seulement prévision
                forecast_value, _ = self._generate_realistic_forecast(
                    event.id, base_value
                )
                previous_value = base_value
            else:
                # Événement passé - générer prévision et valeur réelle
                forecast_value, actual_value = self._generate_realistic_forecast(
                    event.id, base_value
                )
                previous_value = base_value

                # Mettre à jour l'historique pour cohérence
                self.historical_data[event.id]["last_value"] = actual_value

        # Déterminer le statut
        now = datetime.now()
        if event_time > now:
            status = EventStatus.UPCOMING
        elif event_time <= now:
            status = EventStatus.RELEASED

        # Calculer l'impact simulé sur le marché
        market_impact = self._calculate_market_impact(
            event, forecast_value, actual_value
        )

        return {
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "country": event.country,
            "category": event.category.value,
            "impact": event.impact.value,
            "datetime": event_time,
            "date": event_time.date().isoformat(),
            "time": event_time.time().strftime("%H:%M"),
            "status": status.value,
            "previous_value": previous_value,
            "forecast_value": forecast_value,
            "actual_value": actual_value,
            "unit": event.unit,
            "source": event.source,
            "market_impact": market_impact,
            "flag": self.events_config.country_flags.get(event.country, "🌍"),
        }

    def _calculate_market_impact(
        self, event: EconomicEvent, forecast: Optional[float], actual: Optional[float]
    ) -> Dict:
        """Calculer l'impact simulé sur le marché"""

        impact_data = {
            "expected_volatility": 0.0,
            "actual_volatility": 0.0,
            "direction": "neutral",
            "confidence": 0.5,
        }

        # Impact attendu basé sur l'importance de l'événement
        volatility_map = {
            EventImpact.CRITICAL: 2.5,
            EventImpact.HIGH: 1.5,
            EventImpact.MEDIUM: 0.8,
            EventImpact.LOW: 0.3,
        }

        impact_data["expected_volatility"] = volatility_map.get(event.impact, 0.5)

        # Si on a une prévision et une valeur réelle, calculer la surprise
        if forecast is not None and actual is not None:
            surprise_ratio = abs(actual - forecast) / max(abs(forecast), 1)
            impact_data["actual_volatility"] = impact_data["expected_volatility"] * (
                1 + surprise_ratio
            )

            # Direction basée sur surprise positive/négative
            if actual > forecast:
                impact_data["direction"] = (
                    "positive"
                    if event.id
                    not in ["us_unemployment_rate", "initial_jobless_claims"]
                    else "negative"
                )
            elif actual < forecast:
                impact_data["direction"] = (
                    "negative"
                    if event.id
                    not in ["us_unemployment_rate", "initial_jobless_claims"]
                    else "positive"
                )

            # Confiance basée sur l'importance et la surprise
            impact_data["confidence"] = min(0.9, 0.5 + (surprise_ratio * 0.4))

        return impact_data

    def get_upcoming_events(
        self, days_ahead: int = 7, selected_events: List[str] = None
    ) -> List[Dict]:
        """Récupérer les événements à venir"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days_ahead)

        events = self.get_events_for_period(start_date, end_date, selected_events)
        return [e for e in events if e["status"] == "upcoming"]

    def get_recent_events(
        self, days_back: int = 7, selected_events: List[str] = None
    ) -> List[Dict]:
        """Récupérer les événements récents"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        events = self.get_events_for_period(start_date, end_date, selected_events)
        return [e for e in events if e["status"] == "released"]

    def get_events_by_impact(self, impact: str, days_range: int = 30) -> List[Dict]:
        """Récupérer les événements par niveau d'impact"""
        start_date = datetime.now() - timedelta(days=days_range // 2)
        end_date = datetime.now() + timedelta(days=days_range // 2)

        events = self.get_events_for_period(start_date, end_date)
        return [e for e in events if e["impact"] == impact]

    def search_events(self, query: str, days_range: int = 30) -> List[Dict]:
        """Rechercher des événements par nom ou description"""
        start_date = datetime.now() - timedelta(days=days_range // 2)
        end_date = datetime.now() + timedelta(days=days_range // 2)

        events = self.get_events_for_period(start_date, end_date)

        query_lower = query.lower()
        filtered_events = []

        for event in events:
            if (
                query_lower in event["name"].lower()
                or query_lower in event["description"].lower()
                or query_lower in event["country"].lower()
            ):
                filtered_events.append(event)

        return filtered_events

    def get_calendar_data(
        self, month: int, year: int, selected_events: List[str] = None
    ) -> Dict:
        """Récupérer les données pour un mois de calendrier"""
        start_date = datetime(year, month, 1)

        # Dernier jour du mois
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)

        events = self.get_events_for_period(start_date, end_date, selected_events)

        # Organiser par jour
        calendar_data = {}
        for event in events:
            day = event["datetime"].day
            if day not in calendar_data:
                calendar_data[day] = []
            calendar_data[day].append(event)

        return {
            "month": month,
            "year": year,
            "events_by_day": calendar_data,
            "total_events": len(events),
            "critical_events": len([e for e in events if e["impact"] == "critical"]),
            "high_impact_events": len([e for e in events if e["impact"] == "high"]),
        }


# Instance globale
economic_events_provider = EconomicEventsProvider()
