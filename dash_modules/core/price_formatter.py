"""
Price Formatter Compatibility Module - Phase 1 THEBOT
Stub module pour maintenir la compatibilité avec dash_modules.core.price_formatter
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def format_crypto_price_adaptive(price: float, symbol: Optional[str] = None) -> str:
    """
    Formater un prix crypto de manière adaptative

    Args:
        price: Prix à formater
        symbol: Symbole optionnel

    Returns:
        Prix formaté
    """
    try:
        if price >= 1:
            return f"${price:,.2f}"
        elif price >= 0.01:
            return f"${price:.4f}"
        else:
            return f"${price:.8f}"
    except Exception as e:
        logger.warning(f"Erreur formatage prix {price}: {e}")
        return f"${price}"


def format_percentage_change(change: float) -> str:
    """
    Formater un changement en pourcentage

    Args:
        change: Changement en pourcentage

    Returns:
        Changement formaté
    """
    try:
        if change >= 0:
            return f"+{change:.2f}%"
        else:
            return f"{change:.2f}%"
    except Exception as e:
        logger.warning(f"Erreur formatage pourcentage {change}: {e}")
        return f"{change}%"


def format_price_label_adaptive(price: float) -> str:
    """
    Formate un prix pour les labels d'indicateurs (sans symbole $)

    Args:
        price: Prix à formater

    Returns:
        Prix formaté sans symbole $
    """
    try:
        formatted_with_dollar = format_crypto_price_adaptive(price)
        # Enlever le symbole $ pour les labels
        return formatted_with_dollar[1:] if formatted_with_dollar.startswith('$') else formatted_with_dollar
    except Exception as e:
        logger.warning(f"Erreur formatage label prix {price}: {e}")
        return str(price)


def format_volume_adaptive(volume: float) -> str:
    """
    Formate un volume de manière lisible

    Args:
        volume: Volume à formater

    Returns:
        Volume formaté (K, M, B, T)
    """
    try:
        if isinstance(volume, str):
            volume = float(volume)
        elif isinstance(volume, int):
            volume = float(volume)

        if volume >= 1_000_000_000_000:  # Trillion
            return f"${volume/1_000_000_000_000:.2f}T"
        elif volume >= 1_000_000_000:  # Billion
            return f"${volume/1_000_000_000:.2f}B"
        elif volume >= 1_000_000:  # Million
            return f"${volume/1_000_000:.2f}M"
        elif volume >= 1_000:  # Thousand
            return f"${volume/1_000:.2f}K"
        else:
            return f"${volume:.2f}"

    except (ValueError, TypeError):
        return "$0.00"


__all__ = ["format_crypto_price_adaptive", "format_percentage_change", "format_price_label_adaptive", "format_volume_adaptive"]