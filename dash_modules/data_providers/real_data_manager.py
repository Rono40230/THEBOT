"""
Gestionnaire de données réelles THEBOT
UNIQUEMENT API Binance - GRATUITE et ILLIMITÉE
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional, Any
import logging

# Import du provider Binance
from .binance_api import binance_provider

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealDataManager:
    """Gestionnaire central des données réelles - BINANCE UNIQUEMENT"""
    
    def __init__(self):
        self.cache = {}
        self.provider = binance_provider
        
        # Marchés populaires Binance (GRATUITS et ILLIMITÉS)
        self.supported_markets = {
            'BTCUSDT': {'label': 'Bitcoin/USDT', 'type': 'crypto', 'provider': 'binance'},
            'ETHUSDT': {'label': 'Ethereum/USDT', 'type': 'crypto', 'provider': 'binance'},
            'BNBUSDT': {'label': 'Binance Coin/USDT', 'type': 'crypto', 'provider': 'binance'},
            'ADAUSDT': {'label': 'Cardano/USDT', 'type': 'crypto', 'provider': 'binance'},
            'SOLUSDT': {'label': 'Solana/USDT', 'type': 'crypto', 'provider': 'binance'},
            'DOTUSDT': {'label': 'Polkadot/USDT', 'type': 'crypto', 'provider': 'binance'},
            'LINKUSDT': {'label': 'Chainlink/USDT', 'type': 'crypto', 'provider': 'binance'},
            'LTCUSDT': {'label': 'Litecoin/USDT', 'type': 'crypto', 'provider': 'binance'},
            'AVAXUSDT': {'label': 'Avalanche/USDT', 'type': 'crypto', 'provider': 'binance'},
            'MATICUSDT': {'label': 'Polygon/USDT', 'type': 'crypto', 'provider': 'binance'},
            'ATOMUSDT': {'label': 'Cosmos/USDT', 'type': 'crypto', 'provider': 'binance'},
            'XRPUSDT': {'label': 'XRP/USDT', 'type': 'crypto', 'provider': 'binance'}
        }
        
        logger.info(f"✅ RealDataManager initialisé - {len(self.supported_markets)} marchés Binance disponibles")
        
    def get_available_markets(self) -> List[str]:
        """Retourner liste des marchés disponibles"""
        return list(self.supported_markets.keys())
    
    def get_market_data(self, symbol: str, timeframe: str = '1h', 
                       limit: int = 100) -> Optional[pd.DataFrame]:
        """Récupérer données de marché Binance en temps réel"""
        if symbol not in self.supported_markets:
            logger.error(f"Marché non supporté: {symbol}")
            return None
        
        try:
            # Mapper timeframes Dash vers Binance
            binance_interval_map = {
                '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
                '1h': '1h', '4h': '4h', '1d': '1d', '1w': '1w'
            }
            
            binance_interval = binance_interval_map.get(timeframe, '1h')
            
            logger.info(f"📊 Récupération {symbol} (Binance) - {binance_interval} - {limit} points")
            
            # Récupérer klines depuis Binance
            df = self.provider.get_klines(symbol, binance_interval, limit)
            
            if df is not None and not df.empty:
                logger.info(f"✅ {symbol}: {len(df)} points récupérés")
                return df
            else:
                logger.warning(f"⚠️ {symbol}: Aucune donnée reçue")
                return None
                
        except Exception as e:
            logger.error(f"Erreur récupération données {symbol}: {str(e)}")
            return None
    
    def get_current_prices(self) -> Dict[str, Dict[str, Any]]:
        """Récupérer prix actuels pour tous les marchés"""
        prices = {}
        
        logger.info(f"💰 Récupération prix pour {len(self.supported_markets)} marchés")
        
        for symbol in self.supported_markets.keys():
            try:
                # Récupérer ticker 24h complet
                ticker_data = self.provider.get_ticker_24hr(symbol)
                
                if ticker_data:
                    prices[symbol] = {
                        'price': ticker_data['last_price'],
                        'change': ticker_data['price_change'],
                        'change_percent': ticker_data['price_change_percent'],
                        'volume': ticker_data['volume'],
                        'high_24h': ticker_data['high_price'],
                        'low_24h': ticker_data['low_price'],
                        'type': 'crypto',
                        'provider': 'binance',
                        'timestamp': ticker_data['timestamp']
                    }
                    
            except Exception as e:
                logger.error(f"Erreur prix {symbol}: {str(e)}")
        
        logger.info(f"✅ Prix récupérés pour {len(prices)} marchés")
        return prices
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Récupérer résumé général du marché"""
        try:
            summary = self.provider.get_market_summary()
            summary['supported_markets'] = len(self.supported_markets)
            summary['provider'] = 'binance'
            return summary
            
        except Exception as e:
            logger.error(f"Erreur résumé marché: {str(e)}")
            return {
                'supported_markets': len(self.supported_markets),
                'provider': 'binance',
                'error': str(e)
            }
    
    def search_markets(self, query: str) -> List[Dict[str, str]]:
        """Rechercher marchés par mots-clés"""
        results = []
        
        try:
            # Recherche dans marchés supportés d'abord
            query_upper = query.upper()
            for symbol, info in self.supported_markets.items():
                if (query_upper in symbol or 
                    query_upper in info['label'].upper()):
                    results.append({
                        'symbol': symbol,
                        'name': info['label'],
                        'type': info['type']
                    })
            
            # Si peu de résultats, recherche externe Binance
            if len(results) < 5:
                binance_symbols = self.provider.search_symbols(query)
                for symbol in binance_symbols[:10]:
                    if symbol not in self.supported_markets:
                        results.append({
                            'symbol': symbol,
                            'name': f"{symbol} (Binance)",
                            'type': 'crypto'
                        })
            
        except Exception as e:
            logger.error(f"Erreur recherche marchés: {str(e)}")
        
        return results[:15]
    
    def get_api_status(self) -> Dict[str, Any]:
        """Statut de l'API Binance"""
        try:
            # Test simple avec un symbole populaire
            test_data = self.provider.get_ticker_price('BTCUSDT')
            
            return {
                'binance': {
                    'active': test_data is not None,
                    'name': 'Binance API',
                    'markets_count': len(self.supported_markets),
                    'type': 'Gratuit et illimité',
                    'last_test': datetime.now(),
                    'test_result': 'Success' if test_data else 'Failed'
                }
            }
            
        except Exception as e:
            return {
                'binance': {
                    'active': False,
                    'name': 'Binance API',
                    'markets_count': 0,
                    'type': 'Gratuit et illimité',
                    'last_test': datetime.now(),
                    'test_result': f'Error: {str(e)}'
                }
            }
    
    def get_configuration_info(self):
        """Afficher informations de configuration"""
        print("\n" + "="*60)
        print("🚀 THEBOT - CONFIGURATION BINANCE API")
        print("="*60)
        print()
        print("✅ Binance API - GRATUITE et ILLIMITÉE")
        print(f"   📊 Marchés disponibles: {len(self.supported_markets)}")
        print("   🔄 Données en temps réel")
        print("   🎯 Aucune clé API requise")
        print("   ⚡ Rate limit généreux (1200 req/min)")
        print()
        
        # Test de connexion
        status = self.get_api_status()
        binance_status = status.get('binance', {})
        
        if binance_status.get('active', False):
            print("🟢 STATUT: Binance API fonctionnelle")
            print(f"   Test: {binance_status.get('test_result', 'Unknown')}")
        else:
            print("🔴 STATUT: Binance API non accessible")
            print(f"   Erreur: {binance_status.get('test_result', 'Unknown')}")
        
        print()
        print("📈 Marchés supportés:")
        for i, (symbol, info) in enumerate(self.supported_markets.items()):
            if i < 5:  # Afficher 5 premiers
                print(f"   • {symbol}: {info['label']}")
        
        if len(self.supported_markets) > 5:
            print(f"   ... et {len(self.supported_markets) - 5} autres")
        
        print("\n" + "="*60)
        print("🎯 Prêt pour le trading avec des données réelles gratuites !")
        print("="*60)


# Instance globale
real_data_manager = RealDataManager()