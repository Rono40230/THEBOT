"""
Data Manager - Gestion Centralisée des Données THEBOT
Architecture MVC - Couche MODEL conforme .clinerules
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import logging
from dataclasses import dataclass

# Configuration du logging conforme .clinerules
logger = logging.getLogger(__name__)

@dataclass
class MarketDataConfig:
    """Configuration des données de marché selon .clinerules"""
    default_limit: int = 500
    default_interval: str = '1h'
    timeout_seconds: int = 10
    fallback_enabled: bool = True

class DataManager:
    """
    Gestionnaire centralisé des données financières
    
    Responsabilités selon .clinerules :
    - Single Responsibility : Gestion des données uniquement
    - Type hints obligatoires
    - Logging structuré
    - Gestion d'erreurs robuste
    """
    
    def __init__(self, config: Optional[MarketDataConfig] = None) -> None:
        """
        Initialise le gestionnaire de données
        
        Args:
            config: Configuration optionnelle du gestionnaire
        """
        self.config: MarketDataConfig = config or MarketDataConfig()
        self.market_data: Dict[str, pd.DataFrame] = {}
        self.logger: logging.Logger = logging.getLogger("thebot.data_manager")
        
        # Cache des symboles pour éviter les appels répétés
        self._symbols_cache: Optional[List[str]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl_minutes: int = 60  # TTL cache 1 heure
        
        self.logger.info("🔧 DataManager initialisé")
    
    def get_all_binance_symbols(self) -> List[str]:
        """
        Récupère tous les symboles Binance disponibles avec cache
        
        Returns:
            List[str]: Liste des symboles USDT trading actifs
            
        Raises:
            requests.RequestException: En cas d'erreur réseau
        """
        try:
            # Vérifier le cache
            if self._is_cache_valid():
                self.logger.debug("📦 Utilisation du cache des symboles")
                return self._symbols_cache
            
            self.logger.info("🔄 Récupération des symboles Binance...")
            
            url = "https://api.binance.com/api/v3/exchangeInfo"
            response = requests.get(url, timeout=self.config.timeout_seconds)
            response.raise_for_status()
            
            data = response.json()
            symbols = []
            
            for symbol_info in data['symbols']:
                if (symbol_info['status'] == 'TRADING' and 
                    symbol_info['symbol'].endswith('USDT')):
                    symbols.append(symbol_info['symbol'])
            
            # Mise à jour du cache
            self._symbols_cache = sorted(symbols)
            self._cache_timestamp = datetime.now()
            
            self.logger.info(f"✅ {len(symbols)} symboles Binance chargés")
            return self._symbols_cache
            
        except requests.RequestException as e:
            self.logger.error(f"❌ Erreur réseau API exchange info: {e}")
            return self.get_popular_symbols()
        except Exception as e:
            self.logger.error(f"❌ Erreur inattendue récupération symboles: {e}")
            return self.get_popular_symbols()
    
    def _is_cache_valid(self) -> bool:
        """Vérifie si le cache des symboles est valide"""
        if not self._symbols_cache or not self._cache_timestamp:
            return False
        
        elapsed = datetime.now() - self._cache_timestamp
        return elapsed.total_seconds() < (self._cache_ttl_minutes * 60)
    
    def get_popular_symbols(self) -> List[str]:
        """
        Retourne les symboles populaires en fallback
        
        Returns:
            List[str]: Symboles crypto populaires
        """
        return [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT', 
            'XRPUSDT', 'DOTUSDT', 'LINKUSDT', 'LTCUSDT', 'BCHUSDT', 
            'EOSUSDT', 'TRXUSDT', 'ETCUSDT', 'XLMUSDT', 'ATOMUSDT'
        ]
    
    def search_symbols(self, query: str, symbols_list: Optional[List[str]] = None, 
                      limit: int = 10) -> List[str]:
        """
        Recherche des symboles selon une requête
        
        Args:
            query: Terme de recherche
            symbols_list: Liste optionnelle de symboles (sinon utilise tous les symboles)
            limit: Nombre maximum de résultats
            
        Returns:
            List[str]: Symboles correspondants
        """
        if not query:
            return self.get_popular_symbols()[:limit]
        
        if symbols_list is None:
            symbols_list = self.get_all_binance_symbols()
        
        query_upper = query.upper()
        matches = []
        
        # Recherche exacte au début (priorité)
        for symbol in symbols_list:
            if symbol.startswith(query_upper):
                matches.append(symbol)
                
        # Recherche partielle
        for symbol in symbols_list:
            if query_upper in symbol and symbol not in matches:
                matches.append(symbol)
                
        result = matches[:limit]
        self.logger.debug(f"🔍 Recherche '{query}': {len(result)} résultats")
        return result
    
    def get_binance_data(self, symbol: str, interval: str = None, 
                        limit: int = None) -> Optional[pd.DataFrame]:
        """
        Récupère les données OHLCV de Binance
        
        Args:
            symbol: Symbole à récupérer (ex: 'BTCUSDT')
            interval: Intervalle de temps (défaut: config.default_interval)
            limit: Nombre de bougies (défaut: config.default_limit)
            
        Returns:
            Optional[pd.DataFrame]: DataFrame avec colonnes OHLCV ou None si erreur
            
        Raises:
            ValueError: Si symbol est invalide
        """
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Symbol doit être une chaîne non vide")
        
        interval = interval or self.config.default_interval
        limit = limit or self.config.default_limit
        
        try:
            self.logger.info(f"🔄 Chargement {symbol} ({interval}, {limit} points)...")
            
            url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval, 
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=self.config.timeout_seconds)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                self.logger.warning(f"⚠️ Aucune donnée reçue pour {symbol}")
                return None
            
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades', 
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Conversion des types (conforme .clinerules)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Index sur timestamp pour compatibilité
            df.set_index('timestamp', inplace=True)
            df.dropna(inplace=True)  # Supprimer les lignes avec des NaN
                
            self.logger.info(f"✅ {symbol}: {len(df)} points récupérés")
            return df
            
        except requests.RequestException as e:
            self.logger.error(f"❌ Erreur réseau pour {symbol}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Erreur inattendue pour {symbol}: {e}")
            return None
    
    def load_symbol_data(self, symbol: str, interval: str = '1h', 
                        limit: int = 200) -> pd.DataFrame:
        """
        Charge et met en cache les données d'un symbole
        
        Args:
            symbol: Symbole à charger
            interval: Intervalle de temps
            limit: Nombre de bougies
            
        Returns:
            pd.DataFrame: Données du symbole (réelles ou fallback)
        """
        try:
            df = self.get_binance_data(symbol, interval, limit)
            
            if df is not None and not df.empty:
                self.market_data[symbol] = df
                return df
            else:
                # Fallback avec données simulées
                if self.config.fallback_enabled:
                    self.logger.warning(f"⚠️ Fallback simulation pour {symbol}")
                    fallback_data = self._create_fallback_data(symbol)
                    self.market_data[symbol] = fallback_data
                    return fallback_data
                else:
                    raise ValueError(f"Impossible de charger les données pour {symbol}")
                    
        except Exception as e:
            self.logger.error(f"❌ Erreur chargement {symbol}: {e}")
            if self.config.fallback_enabled:
                return self._create_fallback_data(symbol)
            raise
    
    def _create_fallback_data(self, symbol: str) -> pd.DataFrame:
        """
        Crée des données simulées pour les tests
        
        Args:
            symbol: Symbole pour lequel créer des données
            
        Returns:
            pd.DataFrame: Données OHLCV simulées
        """
        try:
            dates = pd.date_range(
                start=datetime.now() - timedelta(days=7),
                end=datetime.now(),
                freq='1h'
            )
            
            # Prix de base selon le symbole
            base_prices = {
                'BTCUSDT': 43000,
                'ETHUSDT': 2600, 
                'BNBUSDT': 250,
                'ADAUSDT': 0.5,
                'SOLUSDT': 50,
                'XRPUSDT': 0.6,
                'DOTUSDT': 8,
                'LINKUSDT': 15
            }
            base_price = base_prices.get(symbol, 100)
            
            # Génération prix simulés avec marche aléatoire
            np.random.seed(hash(symbol) % 2**32)  # Reproductibilité par symbole
            prices = [base_price]
            
            for i in range(1, len(dates)):
                change_percent = np.random.randn() * 0.02  # 2% volatilité
                new_price = prices[-1] * (1 + change_percent)
                prices.append(max(0.01, new_price))  # Prix minimum
            
            # Construction OHLCV
            data = []
            for i in range(len(prices)-1):
                open_price = prices[i]
                close_price = prices[i+1]
                
                # High/Low avec volatilité intraday
                volatility = abs(np.random.randn()) * 0.01
                high_price = max(open_price, close_price) * (1 + volatility)
                low_price = min(open_price, close_price) * (1 - volatility)
                
                # Volume simulé
                volume = abs(np.random.randn()) * 1000 + 500
                
                data.append({
                    'open': round(open_price, 8),
                    'high': round(high_price, 8),
                    'low': round(low_price, 8),
                    'close': round(close_price, 8),
                    'volume': round(volume, 2)
                })
            
            df = pd.DataFrame(data, index=dates[1:])
            self.logger.debug(f"📊 Données simulées créées pour {symbol}: {len(df)} points")
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Erreur création données simulées pour {symbol}: {e}")
            # Fallback ultime : DataFrame minimal
            return pd.DataFrame({
                'open': [100], 'high': [105], 'low': [95], 
                'close': [102], 'volume': [1000]
            }, index=[datetime.now()])
    
    def get_cached_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Récupère les données mises en cache
        
        Args:
            symbol: Symbole à récupérer
            
        Returns:
            Optional[pd.DataFrame]: Données en cache ou None
        """
        return self.market_data.get(symbol)
    
    def clear_cache(self) -> None:
        """Vide le cache des données et des symboles"""
        self.market_data.clear()
        self._symbols_cache = None
        self._cache_timestamp = None
        self.logger.info("🗑️ Cache vidé")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Retourne les informations du cache
        
        Returns:
            Dict: Informations détaillées du cache
        """
        return {
            'symbols_cached': len(self._symbols_cache) if self._symbols_cache else 0,
            'data_cached': len(self.market_data),
            'cache_valid': self._is_cache_valid(),
            'cache_timestamp': self._cache_timestamp.isoformat() if self._cache_timestamp else None,
            'cached_symbols': list(self.market_data.keys())
        }

# Instance globale singleton
data_manager = DataManager()

# Export conforme .clinerules
__all__ = ['DataManager', 'MarketDataConfig', 'data_manager']