"""
Gestionnaire de données réelles THEBOT
Support multi-providers: Binance (gratuit), Yahoo Finance, FMP
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional, Any
import logging

# Import des providers
from .binance_api import binance_provider
from .crypto_panic_api import crypto_panic_api
from .coin_gecko_api import coin_gecko_api

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealDataManager:
    """Gestionnaire central des données réelles - Multi-providers"""
    
    def __init__(self):
        self.cache = {}
        self.binance_provider = binance_provider
        
        # Configure API keys for providers
        self._configure_api_keys()
        
        # Providers disponibles
        self.providers = {
            'binance': self.binance_provider,
            'crypto_panic': crypto_panic_api,
            'coin_gecko': coin_gecko_api,
            # 'yahoo': yahoo_finance_api,  # TODO: À implémenter
            # 'fmp': fmp_api  # TODO: À implémenter
        }
        
        # Marchés supportés par provider
        self.supported_markets = {
            # Binance - Crypto (GRATUIT et ILLIMITÉ)
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
            'XRPUSDT': {'label': 'XRP/USDT', 'type': 'crypto', 'provider': 'binance'},
            
            # Yahoo Finance - Actions (quand disponible)
            'AAPL': {'label': 'Apple Inc.', 'type': 'stocks', 'provider': 'yahoo'},
            'MSFT': {'label': 'Microsoft Corp.', 'type': 'stocks', 'provider': 'yahoo'},
            'GOOGL': {'label': 'Alphabet Inc.', 'type': 'stocks', 'provider': 'yahoo'},
            'TSLA': {'label': 'Tesla Inc.', 'type': 'stocks', 'provider': 'yahoo'},
            
            # FMP - Actions (quand disponible)
            'NVDA': {'label': 'NVIDIA Corp.', 'type': 'stocks', 'provider': 'fmp'},
            'AMZN': {'label': 'Amazon.com Inc.', 'type': 'stocks', 'provider': 'fmp'},
            
            # CoinGecko - Crypto (GRATUIT avec rate limits)
            'bitcoin': {'label': 'Bitcoin', 'type': 'crypto', 'provider': 'coin_gecko'},
            'ethereum': {'label': 'Ethereum', 'type': 'crypto', 'provider': 'coin_gecko'},
            'binancecoin': {'label': 'BNB', 'type': 'crypto', 'provider': 'coin_gecko'},
            'cardano': {'label': 'Cardano', 'type': 'crypto', 'provider': 'coin_gecko'},
            'solana': {'label': 'Solana', 'type': 'crypto', 'provider': 'coin_gecko'},
        }
        
        logger.info(f"✅ RealDataManager initialisé - {len(self.supported_markets)} marchés disponibles")
        logger.info(f"📊 Providers: Binance (actif), CryptoPanic (actif), CoinGecko (actif), Yahoo Finance (en attente), FMP (en attente)")
    
    def _configure_api_keys(self):
        """Configure API keys for all providers from configuration"""
        try:
            from ..core.api_config import APIConfig
            config = APIConfig()
            
            # Configure CryptoPanic API key
            for provider in config.config['providers']['data_sources']['news']:
                if provider['name'] == 'CryptoPanic' and provider.get('config', {}).get('api_key'):
                    crypto_panic_api.api_key = provider['config']['api_key']
                    logger.info(f"✅ CryptoPanic API key configured")
                elif provider['name'] == 'FMP' and provider.get('config', {}).get('api_key'):
                    # Import and configure FMP
                    from .fmp_api import fmp_api
                    fmp_api.api_key = provider['config']['api_key']
                    logger.info(f"✅ FMP API key configured")
                elif provider['name'] == 'CoinGecko' and provider.get('config', {}).get('api_key'):
                    coin_gecko_api.api_key = provider['config']['api_key']
                    logger.info(f"✅ CoinGecko API key configured")
                    
        except Exception as e:
            logger.warning(f"⚠️ Erreur configuration API keys: {e}")
        
    def get_available_markets(self) -> List[str]:
        """Retourner liste des marchés disponibles"""
        return list(self.supported_markets.keys())
    
    def get_market_data(self, symbol: str, timeframe: str = '1h', 
                       limit: int = 100) -> Optional[pd.DataFrame]:
        """Récupérer données de marché depuis le provider approprié"""
        if symbol not in self.supported_markets:
            logger.error(f"Marché non supporté: {symbol}")
            return None
        
        market_info = self.supported_markets[symbol]
        provider_name = market_info['provider']
        
        try:
            if provider_name == 'binance':
                return self._get_binance_data(symbol, timeframe, limit)
            elif provider_name == 'coin_gecko':
                return self._get_coingecko_data(symbol, timeframe, limit)
            elif provider_name == 'crypto_panic':
                logger.warning(f"CryptoPanic utilisé principalement pour les news, pas de données OHLCV pour {symbol}")
                return None
            elif provider_name == 'yahoo':
                logger.warning(f"Yahoo Finance provider pas encore implémenté pour {symbol}")
                return None
            elif provider_name == 'fmp':
                logger.warning(f"FMP provider pas encore implémenté pour {symbol}")
                return None
            else:
                logger.error(f"Provider inconnu: {provider_name}")
                return None
                
        except Exception as e:
            logger.error(f"Erreur récupération données {symbol}: {str(e)}")
            return None
    
    def _get_binance_data(self, symbol: str, timeframe: str, limit: int) -> Optional[pd.DataFrame]:
        """Récupérer données depuis Binance"""
        # Mapper timeframes Dash vers Binance
        binance_interval_map = {
            '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
            '1h': '1h', '4h': '4h', '1d': '1d', '1w': '1w'
        }
        
        binance_interval = binance_interval_map.get(timeframe, '1h')
        
        logger.info(f"📊 Récupération {symbol} (Binance) - {binance_interval} - {limit} points")
        
        # Récupérer klines depuis Binance
        df = self.binance_provider.get_klines(symbol, binance_interval, limit)
        
        if df is not None and not df.empty:
            logger.info(f"✅ {symbol}: {len(df)} points récupérés")
            return df
        else:
            logger.warning(f"⚠️ {symbol}: Aucune donnée reçue")
            return None
    
    def _get_coingecko_data(self, symbol: str, timeframe: str, limit: int) -> Optional[pd.DataFrame]:
        """Récupérer données depuis CoinGecko"""
        # Mapper timeframes pour CoinGecko (utilise des jours)
        days_map = {
            '1m': 1, '5m': 1, '15m': 1, '30m': 1,
            '1h': 1, '4h': 2, '1d': 7, '1w': 30
        }
        days = days_map.get(timeframe, 7)
        
        logger.info(f"📊 Récupération {symbol} (CoinGecko) - {days} jours")
        
        # Récupérer données historiques depuis CoinGecko
        df = coin_gecko_api.get_price_data(symbol, days=days)
        
        if df is not None and not df.empty:
            # Convertir au format standard OHLCV si nécessaire
            if 'price' in df.columns and 'volume' in df.columns:
                # CoinGecko retourne price/volume, on simule OHLC
                df['open'] = df['price'].shift(1).fillna(df['price'])
                df['high'] = df['price']
                df['low'] = df['price']
                df['close'] = df['price']
                
                # Réorganiser les colonnes
                df = df[['open', 'high', 'low', 'close', 'volume']].copy()
            
            # Limiter les résultats
            df = df.tail(limit)
            
            logger.info(f"✅ {symbol}: {len(df)} points récupérés (CoinGecko)")
            return df
        else:
            logger.warning(f"⚠️ {symbol}: Aucune donnée CoinGecko reçue")
            return None
    
    def get_current_prices(self) -> Dict[str, Dict[str, Any]]:
        """Récupérer prix actuels pour tous les marchés"""
        prices = {}
        
        logger.info(f"💰 Récupération prix pour {len(self.supported_markets)} marchés")
        
        # Séparer par provider pour optimiser les appels
        binance_symbols = [symbol for symbol, info in self.supported_markets.items() 
                          if info['provider'] == 'binance']
        
        # Récupérer prix Binance
        for symbol in binance_symbols:
            try:
                ticker_data = self.binance_provider.get_ticker_24hr(symbol)
                
                if ticker_data:
                    prices[symbol] = {
                        'price': ticker_data['last_price'],
                        'change': ticker_data['price_change'],
                        'change_percent': ticker_data['price_change_percent'],
                        'volume': ticker_data['volume'],
                        'high_24h': ticker_data['high_price'],
                        'low_24h': ticker_data['low_price'],
                        'provider': 'binance'
                    }
                    
            except Exception as e:
                logger.error(f"Erreur prix {symbol}: {str(e)}")
                continue
        
        # TODO: Ajouter récupération prix pour Yahoo Finance et FMP
        other_symbols = [symbol for symbol, info in self.supported_markets.items() 
                        if info['provider'] in ['yahoo', 'fmp']]
        
        for symbol in other_symbols:
            provider = self.supported_markets[symbol]['provider']
            logger.info(f"⏳ {symbol} ({provider}) - Provider en attente d'implémentation")
            
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
    
    def get_news_data(self, sources: List[str] = None, limit: int = 20) -> List[Dict]:
        """Récupérer données de news depuis tous les providers disponibles"""
        if sources is None:
            sources = ['binance', 'crypto_panic', 'coin_gecko', 'yahoo', 'fmp']
        
        all_news = []
        
        try:
            # Binance News (Annonces officielles)
            if 'binance' in sources:
                try:
                    from .binance_api import binance_provider
                    binance_news = binance_provider.get_news(limit=limit//5)
                    all_news.extend(binance_news)
                    logger.info(f"✅ Récupéré {len(binance_news)} news de Binance")
                except Exception as e:
                    logger.error(f"❌ Erreur news Binance: {e}")
            
            # CryptoPanic News
            if 'crypto_panic' in sources:
                try:
                    crypto_panic_news = crypto_panic_api.get_news(limit=limit//5)
                    all_news.extend(crypto_panic_news)
                    logger.info(f"✅ Récupéré {len(crypto_panic_news)} news de CryptoPanic")
                except Exception as e:
                    logger.error(f"❌ Erreur news CryptoPanic: {e}")
            
            # CoinGecko Market Updates
            if 'coin_gecko' in sources:
                try:
                    coin_gecko_news = coin_gecko_api.get_news(limit=limit//5)
                    all_news.extend(coin_gecko_news)
                    logger.info(f"✅ Récupéré {len(coin_gecko_news)} updates de CoinGecko")
                except Exception as e:
                    logger.error(f"❌ Erreur updates CoinGecko: {e}")
            
            # Yahoo Finance News
            if 'yahoo' in sources:
                try:
                    from .yahoo_finance_api import yahoo_finance_api
                    yahoo_news = yahoo_finance_api.get_news(limit=limit//3)
                    all_news.extend(yahoo_news)
                    logger.info(f"✅ Récupéré {len(yahoo_news)} news de Yahoo Finance")
                except Exception as e:
                    logger.error(f"❌ Erreur news Yahoo Finance: {e}")
            
            # FMP News
            if 'fmp' in sources:
                try:
                    from .fmp_api import fmp_api
                    if fmp_api.api_key:
                        fmp_news = fmp_api.get_economic_news(limit=limit//3)
                        all_news.extend(fmp_news)
                        logger.info(f"✅ Récupéré {len(fmp_news)} news de FMP")
                    else:
                        logger.warning("⚠️ FMP API key manquante pour les news")
                except Exception as e:
                    logger.error(f"❌ Erreur news FMP: {e}")
        
        except Exception as e:
            logger.error(f"❌ Erreur générale récupération news: {e}")
        
        # Trier par date de publication (plus récent en premier)
        try:
            all_news.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        except Exception as e:
            logger.warning(f"⚠️ Erreur tri news: {e}")
        
        # Limiter et formater
        final_news = all_news[:limit]
        
        # Ajouter des metadata
        for news in final_news:
            if 'id' not in news:
                news['id'] = f"{news.get('source', 'unknown')}_{hash(news.get('title', ''))}"
            if 'category' not in news:
                news['category'] = 'financial'
        
        logger.info(f"✅ Retour {len(final_news)} articles de news combinés")
        return final_news

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