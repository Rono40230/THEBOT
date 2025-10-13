# src/thebot/indicators/smart_money/fair_value_gaps/__init__.py

"""
Fair Value Gaps (FVG) - Indicateur Smart Money
==============================================

Module professionnel pour la détection et l'analyse des Fair Value Gaps,
ces zones de prix non comblées qui révèlent l'activité des institutions
et représentent des niveaux clés de support/résistance future.

Usage:
    >>> from thebot.indicators.smart_money.fair_value_gaps import create_fvg_analyzer
    >>> analyzer = create_fvg_analyzer(trading_style='day_trading')
    >>> gaps = analyzer.analyze_gaps(df)
    >>> active_gaps = [gap for gap in gaps if gap.is_active()]

Classes principales:
    - FVGAnalyzer: Analyseur principal combinant configuration, calcul et visualisation
    - FVGConfig: Configuration avancée avec presets et validation
    - FVGCalculator: Moteur de calcul des gaps avec détection sophistiquée
    - FVGPlotter: Visualiseur professionnel avec Plotly

Concepts Smart Money:
    - Institutional Order Flow: Les gaps révèlent les ordres institutionnels
    - Liquidity Zones: Zones où les institutions collectent la liquidité
    - Market Structure: Les gaps valident les changements de structure
    - Price Discovery: Zones de découverte de prix non comblées

Tooltips éducatifs inclus pour chaque concept et paramètre.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from .calculator import FairValueGap, FVGCalculator, FVGStatus, FVGType

# Imports principaux
from .config import (
    FVGConfig,
    TradingStyle,
    get_trading_style_preset,
    validate_fvg_parameters,
)
from .plotter import FVGPlotter, FVGPlotterError

# Version et métadonnées
__version__ = "1.0.0"
__author__ = "THEBOT Development Team"
__description__ = "Fair Value Gaps - Smart Money Analysis Module"

# Exports publics
__all__ = [
    # Classes principales
    "FVGAnalyzer",
    "FVGConfig",
    "FVGCalculator",
    "FVGPlotter",
    # Types et énumérations
    "FairValueGap",
    "FVGType",
    "FVGStatus",
    "TradingStyle",
    # Fonctions utilitaires
    "create_fvg_analyzer",
    "create_fvg_config",
    "get_trading_style_preset",
    "validate_fvg_parameters",
    # Constantes
    "DEFAULT_FVG_PARAMS",
    "TRADING_STYLE_PRESETS",
    # Exceptions
    "FVGError",
    "FVGPlotterError",
]

# Constantes globales
DEFAULT_FVG_PARAMS = {
    "gap_threshold": 0.1,
    "volume_confirmation": True,
    "max_gap_age": 50,
    "min_gap_size": 0.05,
    "strength_calculation": True,
}

TRADING_STYLE_PRESETS = {
    "scalping": "scalping",
    "day_trading": "day_trading",
    "swing_trading": "swing_trading",
    "position_trading": "position_trading",
}


class FVGError(Exception):
    """Exception de base pour les erreurs FVG."""

    pass


class FVGAnalyzer:
    """
    Analyseur principal des Fair Value Gaps.

    Combine configuration, calcul et visualisation dans une interface
    unifiée pour l'analyse professionnelle des gaps institutionnels.

    Attributes:
        config: Configuration FVG avec validation
        calculator: Moteur de calcul des gaps
        plotter: Visualiseur Plotly professionnel
    """

    def __init__(self, config: Optional[FVGConfig] = None):
        """
        Initialise l'analyseur FVG.

        Args:
            config: Configuration FVG (défaut: configuration standard)
        """
        self.config = config or FVGConfig()
        self.calculator = FVGCalculator(self.config)
        self.plotter = FVGPlotter(self.config)

        # Cache pour les résultats
        self._last_analysis: Optional[Dict[str, Any]] = None
        self._gaps_cache: List[FairValueGap] = []

    def analyze_gaps(
        self, data: pd.DataFrame, update_existing: bool = True
    ) -> List[FairValueGap]:
        """
        Analyse complète des Fair Value Gaps.

        Args:
            data: DataFrame avec colonnes OHLCV
            update_existing: Mettre à jour les gaps existants

        Returns:
            Liste des gaps détectés et analysés

        Raises:
            FVGError: En cas d'erreur dans l'analyse
        """
        try:
            # Valider les données
            self._validate_input_data(data)

            # Calculer les nouveaux gaps
            new_gaps = self.calculator.calculate_gaps(data)

            if update_existing and self._gaps_cache:
                # Mettre à jour les gaps existants
                updated_gaps = self.calculator.update_gaps_status(
                    self._gaps_cache, data
                )

                # Fusionner avec les nouveaux gaps
                all_gaps = self._merge_gaps(updated_gaps, new_gaps)
            else:
                all_gaps = new_gaps

            # Mettre en cache
            self._gaps_cache = all_gaps

            # Calculer les statistiques
            statistics = self.calculator.calculate_statistics(all_gaps)

            # Sauvegarder l'analyse
            self._last_analysis = {
                "gaps": all_gaps,
                "statistics": statistics,
                "timestamp": datetime.now(),
                "data_length": len(data),
            }

            return all_gaps

        except Exception as e:
            raise FVGError(f"Erreur lors de l'analyse FVG: {str(e)}")

    def get_active_gaps(self, max_age: Optional[int] = None) -> List[FairValueGap]:
        """
        Retourne les gaps actuellement actifs.

        Args:
            max_age: Âge maximum en bougies (optionnel)

        Returns:
            Liste des gaps actifs
        """
        if not self._gaps_cache:
            return []

        active_gaps = [gap for gap in self._gaps_cache if gap.is_active()]

        if max_age is not None:
            active_gaps = [gap for gap in active_gaps if gap.age_in_candles <= max_age]

        return active_gaps

    def get_strong_gaps(self, min_strength: float = 0.7) -> List[FairValueGap]:
        """
        Retourne les gaps avec force significative.

        Args:
            min_strength: Force minimale requise (0-1)

        Returns:
            Liste des gaps forts
        """
        if not self._gaps_cache:
            return []

        return [
            gap
            for gap in self._gaps_cache
            if gap.strength >= min_strength and gap.is_active()
        ]

    def get_gaps_near_price(
        self, current_price: float, percentage_range: float = 2.0
    ) -> List[FairValueGap]:
        """
        Retourne les gaps proches du prix actuel.

        Args:
            current_price: Prix actuel
            percentage_range: Plage en pourcentage

        Returns:
            Liste des gaps dans la plage
        """
        if not self._gaps_cache:
            return []

        price_range = current_price * (percentage_range / 100)
        near_gaps = []

        for gap in self._gaps_cache:
            if gap.is_active():
                if (
                    gap.bottom <= current_price + price_range
                    and gap.top >= current_price - price_range
                ):
                    near_gaps.append(gap)

        return sorted(near_gaps, key=lambda g: abs(g.mid_point - current_price))

    def create_visualization(
        self, fig, x_data: List[datetime], show_summary: bool = True
    ):
        """
        Ajoute la visualisation FVG à un graphique.

        Args:
            fig: Figure Plotly existante
            x_data: Données temporelles
            show_summary: Afficher le résumé des gaps

        Returns:
            Figure modifiée avec visualisation FVG
        """
        if not self._gaps_cache:
            return fig

        # Ajouter les gaps au graphique
        fig = self.plotter.add_gaps_to_figure(fig, self._gaps_cache, x_data)

        return fig

    def get_trading_signals(self, current_price: float) -> Dict[str, Any]:
        """
        Génère des signaux de trading basés sur les gaps.

        Args:
            current_price: Prix actuel

        Returns:
            Dictionnaire avec signaux et recommandations
        """
        if not self._gaps_cache:
            return {"signal": "NEUTRAL", "strength": 0, "recommendations": []}

        active_gaps = self.get_active_gaps()
        strong_gaps = self.get_strong_gaps()
        near_gaps = self.get_gaps_near_price(current_price, 1.0)

        signals = {
            "signal": "NEUTRAL",
            "strength": 0,
            "confidence": 0,
            "recommendations": [],
            "key_levels": [],
            "risk_zones": [],
        }

        # Analyser les gaps proches
        bullish_gaps = [g for g in near_gaps if g.type == FVGType.BULLISH]
        bearish_gaps = [g for g in near_gaps if g.type == FVGType.BEARISH]

        if bullish_gaps and not bearish_gaps:
            signals["signal"] = "BULLISH"
            signals["strength"] = sum(g.strength for g in bullish_gaps) / len(
                bullish_gaps
            )
            signals["recommendations"].append(
                "Prix près de gaps bullish - opportunité d'achat"
            )

        elif bearish_gaps and not bullish_gaps:
            signals["signal"] = "BEARISH"
            signals["strength"] = sum(g.strength for g in bearish_gaps) / len(
                bearish_gaps
            )
            signals["recommendations"].append(
                "Prix près de gaps bearish - prudence ou vente"
            )

        # Ajouter les niveaux clés
        for gap in strong_gaps[:5]:  # Top 5 gaps forts
            signals["key_levels"].append(
                {
                    "price": gap.mid_point,
                    "type": gap.type.value,
                    "strength": gap.strength,
                    "description": f"FVG {gap.type.value} fort (strength: {gap.strength:.2f})",
                }
            )

        return signals

    def export_gaps_data(self) -> Dict[str, Any]:
        """
        Exporte les données des gaps pour sauvegarde/partage.

        Returns:
            Dictionnaire avec toutes les données FVG
        """
        if not self._last_analysis:
            return {}

        return {
            "config": self.config.__dict__,
            "gaps": [gap.__dict__ for gap in self._gaps_cache],
            "statistics": self._last_analysis.get("statistics", {}),
            "analysis_timestamp": self._last_analysis.get("timestamp"),
            "version": __version__,
        }

    def _validate_input_data(self, data: pd.DataFrame):
        """Valide les données d'entrée."""
        required_columns = ["open", "high", "low", "close"]
        if not all(col in data.columns for col in required_columns):
            raise FVGError(f"Colonnes manquantes. Requis: {required_columns}")

        if len(data) < 10:
            raise FVGError("Données insuffisantes (minimum 10 bougies)")

    def _merge_gaps(
        self, existing_gaps: List[FairValueGap], new_gaps: List[FairValueGap]
    ) -> List[FairValueGap]:
        """Fusionne les gaps existants avec les nouveaux."""
        # Créer un dictionnaire des gaps existants par ID
        existing_dict = {gap.id: gap for gap in existing_gaps}

        # Ajouter les nouveaux gaps
        for gap in new_gaps:
            if gap.id not in existing_dict:
                existing_dict[gap.id] = gap

        return list(existing_dict.values())


# Fonctions utilitaires publiques


def create_fvg_analyzer(
    trading_style: Union[str, TradingStyle] = "day_trading",
    custom_params: Optional[Dict[str, Any]] = None,
) -> FVGAnalyzer:
    """
    Crée un analyseur FVG avec configuration optimisée.

    Args:
        trading_style: Style de trading pour preset automatique
        custom_params: Paramètres personnalisés supplémentaires

    Returns:
        Analyseur FVG configuré

    Example:
        >>> analyzer = create_fvg_analyzer('scalping', {'gap_threshold': 0.05})
        >>> gaps = analyzer.analyze_gaps(df)
    """
    # Obtenir le preset du style de trading
    if isinstance(trading_style, str):
        trading_style = TradingStyle(trading_style)

    config = get_trading_style_preset(trading_style)

    # Appliquer les paramètres personnalisés
    if custom_params:
        for key, value in custom_params.items():
            if hasattr(config, key):
                setattr(config, key, value)

    return FVGAnalyzer(config)


def create_fvg_config(
    gap_threshold: float = 0.1,
    volume_confirmation: bool = True,
    trading_style: Optional[TradingStyle] = None,
    **kwargs,
) -> FVGConfig:
    """
    Crée une configuration FVG personnalisée.

    Args:
        gap_threshold: Seuil minimum du gap en %
        volume_confirmation: Activer la confirmation de volume
        trading_style: Style de trading pour optimisation
        **kwargs: Paramètres supplémentaires

    Returns:
        Configuration FVG validée
    """
    if trading_style:
        config = get_trading_style_preset(trading_style)
        config.gap_threshold = gap_threshold
        config.volume_confirmation = volume_confirmation
    else:
        config = FVGConfig(
            gap_threshold=gap_threshold,
            volume_confirmation=volume_confirmation,
            **kwargs,
        )

    return config


# Aliases pour compatibilité
FairValueGapAnalyzer = FVGAnalyzer
create_fair_value_gap_analyzer = create_fvg_analyzer
