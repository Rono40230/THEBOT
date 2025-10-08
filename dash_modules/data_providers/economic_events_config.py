"""
Configuration des événements économiques pour le calendrier d'annonces THEBOT
Tous les événements susceptibles de créer des mouvements de marché
"""

from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class EventImpact(Enum):
    """Niveau d'impact sur les marchés"""
    CRITICAL = "critical"    # Impact >2% (rouge)
    HIGH = "high"           # Impact 1-2% (orange)
    MEDIUM = "medium"       # Impact 0.5-1% (jaune)
    LOW = "low"            # Impact <0.5% (vert)

class EventFrequency(Enum):
    """Fréquence des événements"""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    IRREGULAR = "irregular"
    ANNUAL = "annual"

class EventCategory(Enum):
    """Catégories d'événements"""
    EMPLOYMENT = "employment"
    MONETARY_POLICY = "monetary_policy"
    INFLATION = "inflation"
    ECONOMIC_ACTIVITY = "economic_activity"
    CONSUMPTION = "consumption"
    GEOPOLITICAL = "geopolitical"
    CRYPTO_REGULATORY = "crypto_regulatory"
    CORPORATE = "corporate"
    COMMODITIES = "commodities"

@dataclass
class EconomicEvent:
    """Définition d'un événement économique"""
    id: str
    name: str
    description: str
    country: str
    category: EventCategory
    impact: EventImpact
    frequency: EventFrequency
    source: str
    time_of_release: Optional[str] = None  # Format "HH:MM" UTC
    previous_value: Optional[str] = None
    forecast_value: Optional[str] = None
    actual_value: Optional[str] = None
    unit: Optional[str] = None
    enabled: bool = True

class EconomicEventsConfig:
    """Configuration centralisée des événements économiques"""
    
    def __init__(self):
        self.events = self._init_events()
        self.country_flags = {
            "US": "🇺🇸",
            "EU": "🇪🇺",
            "UK": "🇬🇧", 
            "JP": "🇯🇵",
            "CN": "🇨🇳",
            "CA": "🇨🇦",
            "AU": "🇦🇺",
            "GLOBAL": "🌍"
        }
    
    def _init_events(self) -> List[EconomicEvent]:
        """Initialiser la liste exhaustive des événements économiques"""
        
        events = []
        
        # =========================
        # 🇺🇸 ÉTATS-UNIS - Impact Maximum
        # =========================
        
        # Emploi & Main d'œuvre
        events.extend([
            EconomicEvent(
                id="us_nfp", name="Non-Farm Payrolls (NFP)", 
                description="Emplois non-agricoles créés, indicateur emploi le plus important",
                country="US", category=EventCategory.EMPLOYMENT, impact=EventImpact.CRITICAL,
                frequency=EventFrequency.MONTHLY, source="Bureau of Labor Statistics",
                time_of_release="13:30", unit="emplois"
            ),
            EconomicEvent(
                id="us_unemployment_rate", name="Unemployment Rate",
                description="Taux de chômage américain",
                country="US", category=EventCategory.EMPLOYMENT, impact=EventImpact.HIGH,
                frequency=EventFrequency.MONTHLY, source="Bureau of Labor Statistics",
                time_of_release="13:30", unit="%"
            ),
            EconomicEvent(
                id="us_initial_jobless_claims", name="Initial Jobless Claims",
                description="Nouvelles inscriptions au chômage hebdomadaires",
                country="US", category=EventCategory.EMPLOYMENT, impact=EventImpact.HIGH,
                frequency=EventFrequency.WEEKLY, source="Department of Labor",
                time_of_release="13:30", unit="personnes"
            ),
            EconomicEvent(
                id="us_continuing_claims", name="Continuing Jobless Claims",
                description="Demandeurs d'emploi continus",
                country="US", category=EventCategory.EMPLOYMENT, impact=EventImpact.MEDIUM,
                frequency=EventFrequency.WEEKLY, source="Department of Labor",
                time_of_release="13:30", unit="personnes"
            ),
            EconomicEvent(
                id="us_jolts", name="Job Openings (JOLTS)",
                description="Offres d'emploi disponibles",
                country="US", category=EventCategory.EMPLOYMENT, impact=EventImpact.MEDIUM,
                frequency=EventFrequency.MONTHLY, source="Bureau of Labor Statistics",
                time_of_release="15:00", unit="postes"
            ),
            EconomicEvent(
                id="us_average_hourly_earnings", name="Average Hourly Earnings",
                description="Salaire horaire moyen",
                country="US", category=EventCategory.EMPLOYMENT, impact=EventImpact.HIGH,
                frequency=EventFrequency.MONTHLY, source="Bureau of Labor Statistics",
                time_of_release="13:30", unit="$/heure"
            ),
        ])
        
        # Politique Monétaire Fed
        events.extend([
            EconomicEvent(
                id="fed_rate_decision", name="Federal Funds Rate Decision",
                description="Décision taux directeur de la Fed",
                country="US", category=EventCategory.MONETARY_POLICY, impact=EventImpact.CRITICAL,
                frequency=EventFrequency.IRREGULAR, source="Federal Reserve",
                time_of_release="19:00", unit="%"
            ),
            EconomicEvent(
                id="fomc_minutes", name="FOMC Meeting Minutes",
                description="Procès-verbal des réunions Fed",
                country="US", category=EventCategory.MONETARY_POLICY, impact=EventImpact.HIGH,
                frequency=EventFrequency.IRREGULAR, source="Federal Reserve",
                time_of_release="19:00"
            ),
            EconomicEvent(
                id="fed_chair_speech", name="Fed Chair Speech (Powell)",
                description="Discours du président de la Fed",
                country="US", category=EventCategory.MONETARY_POLICY, impact=EventImpact.CRITICAL,
                frequency=EventFrequency.IRREGULAR, source="Federal Reserve"
            ),
            EconomicEvent(
                id="fed_beige_book", name="Fed Beige Book",
                description="Livre beige de la Fed",
                country="US", category=EventCategory.MONETARY_POLICY, impact=EventImpact.MEDIUM,
                frequency=EventFrequency.IRREGULAR, source="Federal Reserve",
                time_of_release="19:00"
            ),
        ])
        
        # Inflation & Prix
        events.extend([
            EconomicEvent(
                id="us_cpi", name="Consumer Price Index (CPI)",
                description="Inflation des prix à la consommation",
                country="US", category=EventCategory.INFLATION, impact=EventImpact.CRITICAL,
                frequency=EventFrequency.MONTHLY, source="Bureau of Labor Statistics",
                time_of_release="13:30", unit="% YoY"
            ),
            EconomicEvent(
                id="us_core_cpi", name="Core CPI",
                description="CPI hors alimentation et énergie",
                country="US", category=EventCategory.INFLATION, impact=EventImpact.CRITICAL,
                frequency=EventFrequency.MONTHLY, source="Bureau of Labor Statistics",
                time_of_release="13:30", unit="% YoY"
            ),
            EconomicEvent(
                id="us_ppi", name="Producer Price Index (PPI)",
                description="Inflation des prix à la production",
                country="US", category=EventCategory.INFLATION, impact=EventImpact.HIGH,
                frequency=EventFrequency.MONTHLY, source="Bureau of Labor Statistics",
                time_of_release="13:30", unit="% YoY"
            ),
            EconomicEvent(
                id="us_pce", name="Personal Consumption Expenditures (PCE)",
                description="Indice de prix préféré de la Fed",
                country="US", category=EventCategory.INFLATION, impact=EventImpact.CRITICAL,
                frequency=EventFrequency.MONTHLY, source="Bureau of Economic Analysis",
                time_of_release="13:30", unit="% YoY"
            ),
            EconomicEvent(
                id="us_core_pce", name="Core PCE",
                description="PCE hors alimentation et énergie",
                country="US", category=EventCategory.INFLATION, impact=EventImpact.CRITICAL,
                frequency=EventFrequency.MONTHLY, source="Bureau of Economic Analysis",
                time_of_release="13:30", unit="% YoY"
            ),
        ])
        
        # Activité Économique
        events.extend([
            EconomicEvent(
                id="us_gdp", name="Gross Domestic Product (GDP)",
                description="Produit intérieur brut",
                country="US", category=EventCategory.ECONOMIC_ACTIVITY, impact=EventImpact.CRITICAL,
                frequency=EventFrequency.QUARTERLY, source="Bureau of Economic Analysis",
                time_of_release="13:30", unit="% QoQ"
            ),
            EconomicEvent(
                id="us_industrial_production", name="Industrial Production",
                description="Production industrielle",
                country="US", category=EventCategory.ECONOMIC_ACTIVITY, impact=EventImpact.MEDIUM,
                frequency=EventFrequency.MONTHLY, source="Federal Reserve",
                time_of_release="14:15", unit="% MoM"
            ),
            EconomicEvent(
                id="us_ism_manufacturing", name="ISM Manufacturing PMI",
                description="Indice PMI manufacturier",
                country="US", category=EventCategory.ECONOMIC_ACTIVITY, impact=EventImpact.HIGH,
                frequency=EventFrequency.MONTHLY, source="Institute for Supply Management",
                time_of_release="15:00", unit="index"
            ),
            EconomicEvent(
                id="us_ism_services", name="ISM Services PMI",
                description="Indice PMI des services",
                country="US", category=EventCategory.ECONOMIC_ACTIVITY, impact=EventImpact.HIGH,
                frequency=EventFrequency.MONTHLY, source="Institute for Supply Management",
                time_of_release="15:00", unit="index"
            ),
        ])
        
        # Consommation & Ventes
        events.extend([
            EconomicEvent(
                id="us_retail_sales", name="Retail Sales",
                description="Ventes au détail",
                country="US", category=EventCategory.CONSUMPTION, impact=EventImpact.HIGH,
                frequency=EventFrequency.MONTHLY, source="Census Bureau",
                time_of_release="13:30", unit="% MoM"
            ),
            EconomicEvent(
                id="us_personal_income", name="Personal Income",
                description="Revenus personnels",
                country="US", category=EventCategory.CONSUMPTION, impact=EventImpact.MEDIUM,
                frequency=EventFrequency.MONTHLY, source="Bureau of Economic Analysis",
                time_of_release="13:30", unit="% MoM"
            ),
            EconomicEvent(
                id="us_consumer_confidence", name="Consumer Confidence",
                description="Confiance des consommateurs",
                country="US", category=EventCategory.CONSUMPTION, impact=EventImpact.MEDIUM,
                frequency=EventFrequency.MONTHLY, source="Conference Board",
                time_of_release="15:00", unit="index"
            ),
        ])
        
        # =========================
        # 🇪🇺 ZONE EURO
        # =========================
        
        # Banque Centrale Européenne
        events.extend([
            EconomicEvent(
                id="ecb_rate_decision", name="ECB Interest Rate Decision",
                description="Décision taux BCE",
                country="EU", category=EventCategory.MONETARY_POLICY, impact=EventImpact.CRITICAL,
                frequency=EventFrequency.IRREGULAR, source="European Central Bank",
                time_of_release="12:45", unit="%"
            ),
            EconomicEvent(
                id="ecb_press_conference", name="ECB Press Conference",
                description="Conférence de presse BCE (Lagarde)",
                country="EU", category=EventCategory.MONETARY_POLICY, impact=EventImpact.CRITICAL,
                frequency=EventFrequency.IRREGULAR, source="European Central Bank",
                time_of_release="13:30"
            ),
        ])
        
        # Indicateurs Zone Euro
        events.extend([
            EconomicEvent(
                id="ez_cpi", name="Eurozone CPI",
                description="Inflation zone euro",
                country="EU", category=EventCategory.INFLATION, impact=EventImpact.HIGH,
                frequency=EventFrequency.MONTHLY, source="Eurostat",
                time_of_release="10:00", unit="% YoY"
            ),
            EconomicEvent(
                id="ez_gdp", name="Eurozone GDP",
                description="PIB zone euro",
                country="EU", category=EventCategory.ECONOMIC_ACTIVITY, impact=EventImpact.HIGH,
                frequency=EventFrequency.QUARTERLY, source="Eurostat",
                time_of_release="10:00", unit="% QoQ"
            ),
            EconomicEvent(
                id="ez_manufacturing_pmi", name="Eurozone Manufacturing PMI",
                description="PMI manufacturier zone euro",
                country="EU", category=EventCategory.ECONOMIC_ACTIVITY, impact=EventImpact.MEDIUM,
                frequency=EventFrequency.MONTHLY, source="Markit Economics",
                time_of_release="09:00", unit="index"
            ),
        ])
        
        # =========================
        # 🇩🇪 ALLEMAGNE
        # =========================
        
        events.extend([
            EconomicEvent(
                id="de_cpi", name="German CPI",
                description="Inflation Allemagne",
                country="EU", category=EventCategory.INFLATION, impact=EventImpact.HIGH,
                frequency=EventFrequency.MONTHLY, source="Destatis",
                time_of_release="13:00", unit="% YoY"
            ),
            EconomicEvent(
                id="de_ifo", name="IFO Business Climate",
                description="Climat des affaires allemand",
                country="EU", category=EventCategory.ECONOMIC_ACTIVITY, impact=EventImpact.MEDIUM,
                frequency=EventFrequency.MONTHLY, source="IFO Institute",
                time_of_release="09:00", unit="index"
            ),
        ])
        
        # =========================
        # 🇬🇧 ROYAUME-UNI
        # =========================
        
        events.extend([
            EconomicEvent(
                id="uk_boe_rate", name="BoE Interest Rate Decision",
                description="Décision taux Banque d'Angleterre",
                country="UK", category=EventCategory.MONETARY_POLICY, impact=EventImpact.HIGH,
                frequency=EventFrequency.IRREGULAR, source="Bank of England",
                time_of_release="12:00", unit="%"
            ),
            EconomicEvent(
                id="uk_cpi", name="UK CPI",
                description="Inflation Royaume-Uni",
                country="UK", category=EventCategory.INFLATION, impact=EventImpact.HIGH,
                frequency=EventFrequency.MONTHLY, source="ONS",
                time_of_release="07:00", unit="% YoY"
            ),
        ])
        
        # =========================
        # 🇯🇵 JAPON
        # =========================
        
        events.extend([
            EconomicEvent(
                id="jp_boj_rate", name="BoJ Interest Rate Decision",
                description="Décision taux Banque du Japon",
                country="JP", category=EventCategory.MONETARY_POLICY, impact=EventImpact.MEDIUM,
                frequency=EventFrequency.IRREGULAR, source="Bank of Japan",
                time_of_release="03:00", unit="%"
            ),
            EconomicEvent(
                id="jp_cpi", name="Japan CPI",
                description="Inflation Japon",
                country="JP", category=EventCategory.INFLATION, impact=EventImpact.MEDIUM,
                frequency=EventFrequency.MONTHLY, source="Statistics Japan",
                time_of_release="23:30", unit="% YoY"
            ),
        ])
        
        # =========================
        # 🇨🇳 CHINE
        # =========================
        
        events.extend([
            EconomicEvent(
                id="cn_cpi", name="China CPI",
                description="Inflation Chine",
                country="CN", category=EventCategory.INFLATION, impact=EventImpact.MEDIUM,
                frequency=EventFrequency.MONTHLY, source="National Bureau of Statistics",
                time_of_release="01:30", unit="% YoY"
            ),
            EconomicEvent(
                id="cn_gdp", name="China GDP",
                description="PIB Chine",
                country="CN", category=EventCategory.ECONOMIC_ACTIVITY, impact=EventImpact.HIGH,
                frequency=EventFrequency.QUARTERLY, source="National Bureau of Statistics",
                time_of_release="02:00", unit="% YoY"
            ),
            EconomicEvent(
                id="cn_manufacturing_pmi", name="China Manufacturing PMI",
                description="PMI manufacturier Chine (officiel)",
                country="CN", category=EventCategory.ECONOMIC_ACTIVITY, impact=EventImpact.MEDIUM,
                frequency=EventFrequency.MONTHLY, source="National Bureau of Statistics",
                time_of_release="01:00", unit="index"
            ),
        ])
        
        # =========================
        # 🛢️ MATIÈRES PREMIÈRES
        # =========================
        
        events.extend([
            EconomicEvent(
                id="eia_crude_oil", name="EIA Crude Oil Inventories",
                description="Stocks de pétrole brut EIA",
                country="US", category=EventCategory.COMMODITIES, impact=EventImpact.MEDIUM,
                frequency=EventFrequency.WEEKLY, source="Energy Information Administration",
                time_of_release="15:30", unit="barils"
            ),
            EconomicEvent(
                id="api_crude_oil", name="API Crude Oil Inventories",
                description="Stocks de pétrole brut API",
                country="US", category=EventCategory.COMMODITIES, impact=EventImpact.MEDIUM,
                frequency=EventFrequency.WEEKLY, source="American Petroleum Institute",
                time_of_release="21:30", unit="barils"
            ),
            EconomicEvent(
                id="opec_meeting", name="OPEC Meetings",
                description="Réunions OPEC+ sur production pétrolière",
                country="GLOBAL", category=EventCategory.COMMODITIES, impact=EventImpact.HIGH,
                frequency=EventFrequency.IRREGULAR, source="OPEC"
            ),
        ])
        
        # =========================
        # 🏛️ GÉOPOLITIQUE
        # =========================
        
        events.extend([
            EconomicEvent(
                id="us_elections", name="US Elections",
                description="Élections américaines (présidentielles/mi-mandat)",
                country="US", category=EventCategory.GEOPOLITICAL, impact=EventImpact.CRITICAL,
                frequency=EventFrequency.IRREGULAR, source="Government"
            ),
            EconomicEvent(
                id="g7_summit", name="G7 Summit",
                description="Sommet G7",
                country="GLOBAL", category=EventCategory.GEOPOLITICAL, impact=EventImpact.MEDIUM,
                frequency=EventFrequency.ANNUAL, source="G7"
            ),
            EconomicEvent(
                id="g20_summit", name="G20 Summit",
                description="Sommet G20",
                country="GLOBAL", category=EventCategory.GEOPOLITICAL, impact=EventImpact.MEDIUM,
                frequency=EventFrequency.ANNUAL, source="G20"
            ),
        ])
        
        # =========================
        # 💎 CRYPTO & RÉGULATION
        # =========================
        
        events.extend([
            EconomicEvent(
                id="sec_crypto", name="SEC Crypto Announcements",
                description="Annonces SEC sur les cryptomonnaies",
                country="US", category=EventCategory.CRYPTO_REGULATORY, impact=EventImpact.HIGH,
                frequency=EventFrequency.IRREGULAR, source="Securities and Exchange Commission"
            ),
            EconomicEvent(
                id="bitcoin_halving", name="Bitcoin Halving",
                description="Réduction de moitié des récompenses Bitcoin",
                country="GLOBAL", category=EventCategory.CRYPTO_REGULATORY, impact=EventImpact.CRITICAL,
                frequency=EventFrequency.IRREGULAR, source="Bitcoin Network"
            ),
            EconomicEvent(
                id="ethereum_upgrade", name="Ethereum Upgrades",
                description="Mises à niveau majeures d'Ethereum",
                country="GLOBAL", category=EventCategory.CRYPTO_REGULATORY, impact=EventImpact.HIGH,
                frequency=EventFrequency.IRREGULAR, source="Ethereum Foundation"
            ),
        ])
        
        return events
    
    def get_events_by_category(self, category: EventCategory) -> List[EconomicEvent]:
        """Récupérer les événements par catégorie"""
        return [event for event in self.events if event.category == category]
    
    def get_events_by_impact(self, impact: EventImpact) -> List[EconomicEvent]:
        """Récupérer les événements par niveau d'impact"""
        return [event for event in self.events if event.impact == impact]
    
    def get_events_by_country(self, country: str) -> List[EconomicEvent]:
        """Récupérer les événements par pays"""
        return [event for event in self.events if event.country == country]
    
    def get_events_by_frequency(self, frequency: EventFrequency) -> List[EconomicEvent]:
        """Récupérer les événements par fréquence"""
        return [event for event in self.events if event.frequency == frequency]
    
    def get_enabled_events(self) -> List[EconomicEvent]:
        """Récupérer uniquement les événements activés"""
        return [event for event in self.events if event.enabled]
    
    def get_critical_events(self) -> List[EconomicEvent]:
        """Récupérer les événements à impact critique"""
        return self.get_events_by_impact(EventImpact.CRITICAL)
    
    def get_event_by_id(self, event_id: str) -> Optional[EconomicEvent]:
        """Récupérer un événement par son ID"""
        for event in self.events:
            if event.id == event_id:
                return event
        return None
    
    def enable_event(self, event_id: str) -> bool:
        """Activer un événement"""
        event = self.get_event_by_id(event_id)
        if event:
            event.enabled = True
            return True
        return False
    
    def disable_event(self, event_id: str) -> bool:
        """Désactiver un événement"""
        event = self.get_event_by_id(event_id)
        if event:
            event.enabled = False
            return True
        return False
    
    def get_events_summary(self) -> Dict:
        """Résumé statistique des événements"""
        total = len(self.events)
        enabled = len(self.get_enabled_events())
        
        by_impact = {}
        for impact in EventImpact:
            by_impact[impact.value] = len(self.get_events_by_impact(impact))
        
        by_category = {}
        for category in EventCategory:
            by_category[category.value] = len(self.get_events_by_category(category))
        
        by_country = {}
        countries = set(event.country for event in self.events)
        for country in countries:
            by_country[country] = len(self.get_events_by_country(country))
        
        return {
            'total': total,
            'enabled': enabled,
            'disabled': total - enabled,
            'by_impact': by_impact,
            'by_category': by_category,
            'by_country': by_country
        }

# Instance globale
economic_events_config = EconomicEventsConfig()