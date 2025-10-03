"""
Formatage adaptatif des prix pour cryptomonnaies
Affiche intelligemment les 4 chiffres significatifs après les zéros
"""
import re
from typing import Union

def format_crypto_price_adaptive(price: Union[float, int, str]) -> str:
    """
    Formate un prix de cryptomonnaie de manière adaptative
    
    Règles :
    - Prix >= 1 : Format standard avec 2 décimales (ex: $1,234.56)
    - Prix < 1 : Trouve le dernier zéro et affiche 4 chiffres significatifs suivants
    
    Exemples :
    - 1234.56 → $1,234.56
    - 0.123456 → $0.1234
    - 0.000012345 → $0.00001234
    - 0.00000008976 → $0.00000008976
    - 0.000000000123456 → $0.0000000001234
    
    Args:
        price: Prix à formater (float, int ou string)
        
    Returns:
        str: Prix formaté avec le symbole $
    """
    try:
        # Convertir en float si nécessaire
        if isinstance(price, str):
            price = float(price)
        elif isinstance(price, int):
            price = float(price)
            
        # Gérer les cas spéciaux
        if price == 0:
            return "$0.0000"
        
        if price < 0:
            # Gérer les prix négatifs (variations)
            return f"-{format_crypto_price_adaptive(abs(price))}"
            
        # Prix >= 1 : format standard avec virgules
        if price >= 1:
            return f"${price:,.2f}"
        
        # Prix < 1 : formatage adaptatif
        # Convertir en chaîne pour analyser la structure
        price_str = f"{price:.20f}".rstrip('0')  # 20 décimales max, enlever zéros finaux
        
        # Trouver la position du premier chiffre non-zéro après la virgule
        match = re.search(r'0\.0*([1-9])', price_str)
        
        if not match:
            # Cas où tous les chiffres sont des zéros (ne devrait pas arriver)
            return f"${price:.6f}"
        
        # Compter le nombre de zéros après la virgule
        zeros_after_decimal = len(match.group(0)) - 3  # -3 pour "0." et le premier chiffre non-zéro
        
        # Calculer le nombre de décimales nécessaires pour avoir 4 chiffres significatifs
        # +1 pour inclure le premier chiffre non-zéro + 3 pour les 3 suivants
        significant_decimals = zeros_after_decimal + 4
        
        # Limiter à un maximum raisonnable pour éviter les nombres trop longs
        significant_decimals = min(significant_decimals, 15)
        
        # Formater avec le nombre approprié de décimales
        formatted = f"${price:.{significant_decimals}f}"
        
        # Enlever les zéros inutiles à la fin
        if '.' in formatted:
            formatted = formatted.rstrip('0').rstrip('.')
            
        # S'assurer qu'on a au moins le format de base si quelque chose a mal tourné
        if formatted == '$':
            formatted = f"${price:.6f}"
            
        return formatted
        
    except (ValueError, TypeError, AttributeError):
        # En cas d'erreur, retourner un format par défaut
        return f"${float(price):.6f}" if price else "$0.0000"


def format_price_label_adaptive(price: Union[float, int, str]) -> str:
    """
    Formate un prix pour les labels d'indicateurs (sans symbole $)
    
    Args:
        price: Prix à formater
        
    Returns:
        str: Prix formaté sans symbole $
    """
    formatted_with_dollar = format_crypto_price_adaptive(price)
    # Enlever le symbole $ pour les labels
    return formatted_with_dollar[1:] if formatted_with_dollar.startswith('$') else formatted_with_dollar


def format_percentage_change(change: Union[float, int, str], decimals: int = 2) -> str:
    """
    Formate un changement de pourcentage
    
    Args:
        change: Changement en pourcentage
        decimals: Nombre de décimales à afficher
        
    Returns:
        str: Changement formaté avec signe et %
    """
    try:
        if isinstance(change, str):
            change = float(change)
        elif isinstance(change, int):
            change = float(change)
            
        sign = "+" if change > 0 else ""
        return f"{sign}{change:.{decimals}f}%"
        
    except (ValueError, TypeError):
        return "0.00%"


def format_volume_adaptive(volume: Union[float, int, str]) -> str:
    """
    Formate un volume de manière lisible
    
    Args:
        volume: Volume à formater
        
    Returns:
        str: Volume formaté (K, M, B, T)
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


# Tests de validation (pour développement)
if __name__ == "__main__":
    # Tests de la fonction principale
    test_prices = [
        1234.56,      # → $1,234.56
        0.123456,     # → $0.1234
        0.000012345,  # → $0.00001234
        0.00000008976, # → $0.00000008976
        0.000000000123456, # → $0.0000000001234
        0.0,          # → $0.0000
        1.0,          # → $1.00
        0.1,          # → $0.1000
        0.01,         # → $0.0100
        0.001,        # → $0.0010
    ]
    
    print("🧪 Tests formatage prix crypto adaptatif:")
    for price in test_prices:
        formatted = format_crypto_price_adaptive(price)
        print(f"  {price:>15} → {formatted}")