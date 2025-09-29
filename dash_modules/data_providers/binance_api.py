"""
Module Binance API - GRATUIT et ILLIMITÉ
Données de marché crypto en temps réel
Architecture modulaire THEBOT
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional, Any
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BinanceProvider:
    """Fournisseur de données Binance - GRATUIT et ILLIMITÉ"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.cache = {}
        self.last_request_time = 0
        self.request_delay = 0.1  # Binance permet 1200 req/min = 20 req/sec
        
        # Symboles populaires Binance
        self.popular_symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 
            'SOLUSDT', 'DOTUSDT', 'LINKUSDT', 'LTCUSDT',
            'AVAXUSDT', 'MATICUSDT', 'ATOMUSDT', 'XRPUSDT'
        ]
        
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Any]:
        """Effectuer une requête API Binance (GRATUITE)"""
        try:
            # Rate limiting très léger (Binance est généreux)
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.request_delay:
                time.sleep(self.request_delay - time_since_last)
            
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, params=params or {}, timeout=30)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erreur HTTP Binance: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erreur requête Binance: {str(e)}")
            return None
    
    def get_ticker_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Récupérer prix actuel d'un symbole"""
        cache_key = f"{symbol}_price"
        
        # Cache très court (5 secondes) pour prix en temps réel
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if time.time() - cache_time < 5:
                return data
        
        endpoint = "ticker/price"
        params = {"symbol": symbol}
        
        response = self._make_request(endpoint, params)
        if response:
            price_data = {
                'symbol': response['symbol'],
                'price': float(response['price']),
                'timestamp': datetime.now()
            }
            self.cache[cache_key] = (time.time(), price_data)
            return price_data
        
        return None
    
    def get_ticker_24hr(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Récupérer statistiques 24h d'un symbole"""
        cache_key = f"{symbol}_24hr"
        
        # Cache 30 secondes pour stats 24h
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if time.time() - cache_time < 30:
                return data
        
        endpoint = "ticker/24hr"
        params = {"symbol": symbol}
        
        response = self._make_request(endpoint, params)
        if response:
            ticker_data = {
                'symbol': response['symbol'],
                'price_change': float(response['priceChange']),
                'price_change_percent': float(response['priceChangePercent']),
                'weighted_avg_price': float(response['weightedAvgPrice']),
                'prev_close_price': float(response['prevClosePrice']),
                'last_price': float(response['lastPrice']),
                'bid_price': float(response['bidPrice']),
                'ask_price': float(response['askPrice']),
                'open_price': float(response['openPrice']),
                'high_price': float(response['highPrice']),
                'low_price': float(response['lowPrice']),
                'volume': float(response['volume']),
                'quote_volume': float(response['quoteVolume']),
                'count': int(response['count']),
                'timestamp': datetime.now()
            }
            self.cache[cache_key] = (time.time(), ticker_data)
            return ticker_data
        
        return None
    
    def get_klines(self, symbol: str, interval: str = '1h', limit: int = 100) -> Optional[pd.DataFrame]:
        """Récupérer données OHLCV (candlesticks)"""
        cache_key = f"{symbol}_{interval}_{limit}_klines"
        
        # Cache selon l'intervalle
        cache_duration = {
            '1m': 60, '5m': 300, '15m': 900, '30m': 1800,
            '1h': 3600, '4h': 14400, '1d': 86400
        }.get(interval, 3600)
        
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if time.time() - cache_time < cache_duration:
                return data
        
        endpoint = "klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        response = self._make_request(endpoint, params)
        if not response:
            return None
        
        try:
            # Convertir réponse Binance en DataFrame
            df_data = []
            for kline in response:
                df_data.append({
                    'timestamp': pd.to_datetime(int(kline[0]), unit='ms'),
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5]),
                    'close_time': pd.to_datetime(int(kline[6]), unit='ms'),
                    'quote_asset_volume': float(kline[7]),
                    'number_of_trades': int(kline[8])
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('timestamp', inplace=True)
            
            self.cache[cache_key] = (time.time(), df)
            return df
            
        except Exception as e:
            logger.error(f"Erreur traitement klines {symbol}: {str(e)}")
            return None
    
    def get_exchange_info(self) -> Optional[Dict[str, Any]]:
        """Récupérer informations sur l'exchange"""
        cache_key = "exchange_info"
        
        # Cache 1 heure pour infos exchange
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if time.time() - cache_time < 3600:
                return data
        
        endpoint = "exchangeInfo"
        response = self._make_request(endpoint)
        
        if response:
            self.cache[cache_key] = (time.time(), response)
            return response
        
        return None
    
    def get_all_tickers(self) -> List[Dict[str, Any]]:
        """Récupérer tous les prix (ATTENTION: requête lourde)"""
        cache_key = "all_tickers"
        
        # Cache 10 secondes pour tous les prix
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if time.time() - cache_time < 10:
                return data
        
        endpoint = "ticker/price"
        response = self._make_request(endpoint)
        
        if response:
            tickers = [
                {
                    'symbol': ticker['symbol'],
                    'price': float(ticker['price'])
                }
                for ticker in response
            ]
            self.cache[cache_key] = (time.time(), tickers)
            return tickers
        
        return []
    
    def get_popular_symbols(self) -> List[str]:
        """Retourner symboles populaires"""
        return self.popular_symbols.copy()
    
    def search_symbols(self, query: str) -> List[str]:
        """Rechercher symboles contenant la requête"""
        try:
            exchange_info = self.get_exchange_info()
            if not exchange_info:
                return self.popular_symbols[:5]
            
            symbols = [s['symbol'] for s in exchange_info['symbols'] 
                      if s['status'] == 'TRADING']
            
            # Filtrer par requête
            query_upper = query.upper()
            matching_symbols = [s for s in symbols if query_upper in s]
            
            return matching_symbols[:20]  # Limiter à 20 résultats
            
        except Exception as e:
            logger.error(f"Erreur recherche symboles: {str(e)}")
            return self.popular_symbols[:5]
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Résumé du marché avec symboles populaires"""
        summary = {
            'total_symbols': 0,
            'active_symbols': 0,
            'popular_prices': {},
            'last_updated': datetime.now()
        }
        
        try:
            # Récupérer infos exchange
            exchange_info = self.get_exchange_info()
            if exchange_info:
                summary['total_symbols'] = len(exchange_info['symbols'])
                summary['active_symbols'] = len([
                    s for s in exchange_info['symbols'] 
                    if s['status'] == 'TRADING'
                ])
            
            # Prix des symboles populaires
            for symbol in self.popular_symbols[:5]:  # 5 premiers
                ticker = self.get_ticker_24hr(symbol)
                if ticker:
                    summary['popular_prices'][symbol] = {
                        'price': ticker['last_price'],
                        'change_percent': ticker['price_change_percent']
                    }
            
        except Exception as e:
            logger.error(f"Erreur résumé marché: {str(e)}")
        
        return summary


# Instance globale
binance_provider = BinanceProvider()