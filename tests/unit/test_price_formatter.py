"""
Tests unitaires pour les fonctions utilitaires du projet THEBOT
"""

import pytest
from dash_modules.core.price_formatter import format_crypto_price_adaptive


class TestPriceFormatter:
    """Tests pour le formateur de prix crypto"""

    def test_format_crypto_price_adaptive_basic(self):
        """Test formatage de base des prix crypto"""
        # Test avec des nombres entiers
        assert format_crypto_price_adaptive(1.0) == "$1.00"
        assert format_crypto_price_adaptive(100.0) == "$100.00"

        # Test avec des décimales
        assert format_crypto_price_adaptive(0.1) == "$0.1"
        assert format_crypto_price_adaptive(0.01) == "$0.01"

    def test_format_crypto_price_adaptive_small_numbers(self):
        """Test formatage des très petits nombres"""
        # Test avec des nombres très petits
        assert format_crypto_price_adaptive(0.0000001) == "$0.0000001"
        assert format_crypto_price_adaptive(0.000000000123456) == "$0.0000000001235"

    def test_format_crypto_price_adaptive_edge_cases(self):
        """Test des cas limites"""
        # Test avec zéro
        assert format_crypto_price_adaptive(0.0) == "$0.0000"

        # Test avec des strings
        assert format_crypto_price_adaptive("0.1") == "$0.1"
        assert format_crypto_price_adaptive("100") == "$100.00"

    def test_format_crypto_price_adaptive_large_numbers(self):
        """Test avec de grands nombres"""
        assert format_crypto_price_adaptive(1000000.0) == "$1,000,000.00"
        assert format_crypto_price_adaptive(1234567.89) == "$1,234,567.89"