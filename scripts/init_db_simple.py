#!/usr/bin/env python3
"""
Script simple d'initialisation de la base de données THEBOT
"""

import logging
import sys
from pathlib import Path

# Ajouter le répertoire racine au path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from dash_modules.models.base import create_tables

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Fonction principale d'initialisation"""
    try:
        logger.info("🚀 Initialisation simple de la base de données THEBOT...")

        # Créer les tables
        logger.info("📋 Création des tables...")
        create_tables()
        logger.info("✅ Tables créées")

        # Créer les données initiales
        logger.info("📊 Création des données initiales...")
        from dash_modules.models.base import SessionLocal
        from dash_modules.models.market_data import MarketData
        from dash_modules.models.user import UserPreferences

        db = SessionLocal()
        try:
            # Créer les marchés par défaut s'ils n'existent pas
            if db.query(MarketData).count() == 0:
                default_markets = [
                    MarketData(symbol="BTCUSDT", name="Bitcoin", type="crypto", provider="binance", base_currency="BTC", quote_currency="USDT"),
                    MarketData(symbol="ETHUSDT", name="Ethereum", type="crypto", provider="binance", base_currency="ETH", quote_currency="USDT"),
                    MarketData(symbol="AAPL", name="Apple Inc.", type="stock", provider="twelve_data", base_currency="AAPL", quote_currency="USD"),
                ]
                for market in default_markets:
                    db.add(market)
                db.commit()
                logger.info(f"✅ {len(default_markets)} marchés par défaut créés")

            # Créer les préférences par défaut
            if db.query(UserPreferences).count() == 0:
                from dash_modules.models.user import UserPreferences
                default_prefs = UserPreferences.get_default_preferences()
                db.add(default_prefs)
                db.commit()
                logger.info("✅ Préférences par défaut créées")

        finally:
            db.close()

        logger.info("✅ Base de données initialisée avec succès!")

    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
