"""
Crypto Market Module for THEBOT
Handles cryptocurrency data using Binance API
"""

from .base_market_module import BaseMarketModule
from ..data_providers.binance_api import binance_provider
import pandas as pd
from typing import List, Dict
from datetime import datetime

class CryptoModule(BaseMarketModule):
    """Crypto market module using Binance API"""
    
    def __init__(self, calculators: Dict = None):
        super().__init__(
            market_type='crypto',
            data_provider=binance_provider,
            calculators=calculators
        )
        self.popular_symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
            'SOLUSDT', 'DOGEUSDT', 'DOTUSDT', 'MATICUSDT', 'SHIBUSDT',
            'AVAXUSDT', 'LTCUSDT', 'UNIUSDT', 'LINKUSDT', 'ATOMUSDT',
            'ETCUSDT', 'XLMUSDT', 'BCHUSDT', 'FILUSDT', 'THETAUSDT',
            'VETUSDT', 'TRXUSDT', 'EOSUSDT', 'AAVEUSDT', 'MKRUSDT',
            'COMPUSDT', 'YFIUSDT', 'SUSHIUSDT', 'SNXUSDT', 'CRVUSDT',
            'PEPEUSDT', 'FLOKIUSDT', 'BONKUSDT', '1000SATSUSDT'
        ]
    
    def get_symbols_list(self) -> List[str]:
        """Get list of available crypto symbols"""
        try:
            symbols = self.data_provider.get_all_symbols()
            return symbols if symbols else self.popular_symbols
        except Exception as e:
            print(f"⚠️ Error loading crypto symbols: {e}")
            return self.popular_symbols
    
    def get_default_symbol(self) -> str:
        """Get default crypto symbol"""
        return 'BTCUSDT'
    
    def load_market_data(self, symbol: str, interval: str = '1h', limit: int = 200) -> pd.DataFrame:
        """Load crypto market data from Binance"""
        try:
            print(f"🔄 Loading crypto data for {symbol}...")
            data = self.data_provider.get_binance_data(symbol, interval, limit)
            
            if not data.empty:
                print(f"✅ {symbol}: {len(data)} crypto data points loaded")
                return data
            else:
                print(f"⚠️ No crypto data for {symbol}, using fallback")
                return self._create_fallback_crypto_data(symbol)
                
        except Exception as e:
            print(f"❌ Error loading crypto data for {symbol}: {e}")
            return self._create_fallback_crypto_data(symbol)
    
    def _create_fallback_crypto_data(self, symbol: str) -> pd.DataFrame:
        """Create fallback crypto data when API unavailable"""
        print(f"📊 Creating fallback crypto data for {symbol}")
        
        # Base prices for popular cryptos
        base_prices = {
            'BTCUSDT': 65000.0, 'ETHUSDT': 2500.0, 'BNBUSDT': 315.0,
            'ADAUSDT': 0.45, 'XRPUSDT': 0.62, 'SOLUSDT': 145.0,
            'DOGEUSDT': 0.085, 'DOTUSDT': 6.50, 'MATICUSDT': 0.75,
            'SHIBUSDT': 0.000018, 'AVAXUSDT': 28.5, 'LTCUSDT': 75.0,
            'PEPEUSDT': 0.000007869, 'FLOKIUSDT': 0.000145
        }
        
        base_price = base_prices.get(symbol, 100.0)
        
        # Generate realistic crypto data
        dates = pd.date_range(end=datetime.now(), periods=200, freq='H')
        
        df_data = []
        current_price = base_price
        
        for i, date in enumerate(dates):
            # Crypto volatility (higher than traditional markets)
            change = (pd.np.random.randn() * 0.025) + (0.002 * pd.np.sin(i/8))
            current_price *= (1 + change)
            
            # Ensure positive price
            current_price = max(current_price, base_price * 0.01)
            
            # Create OHLCV data with crypto-like volatility
            high = current_price * (1 + abs(pd.np.random.randn() * 0.015))
            low = current_price * (1 - abs(pd.np.random.randn() * 0.015))
            open_price = current_price * (1 + pd.np.random.randn() * 0.005)
            
            # Crypto volume patterns
            volume = int(pd.np.random.randint(100000, 5000000))
            
            # Format according to symbol type
            if 'USDT' in symbol and base_price < 1:
                # Small cap cryptos
                decimals = 8 if base_price < 0.001 else 6
            else:
                # Major cryptos
                decimals = 2
            
            df_data.append({
                'timestamp': date,
                'open': round(open_price, decimals),
                'high': round(high, decimals),
                'low': round(low, decimals), 
                'close': round(current_price, decimals),
                'volume': volume
            })
        
        df = pd.DataFrame(df_data)
        df.index = df['timestamp']
        return df
    
    def get_crypto_specific_analysis(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Get crypto-specific analysis and insights"""
        if data.empty:
            return {}
        
        analysis = {
            'market_cap_category': self._get_market_cap_category(symbol),
            'volatility': self._calculate_volatility(data),
            'volume_analysis': self._analyze_volume(data),
            'support_resistance': self._find_support_resistance(data),
            'trend_strength': self._calculate_trend_strength(data)
        }
        
        return analysis
    
    def _get_market_cap_category(self, symbol: str) -> str:
        """Categorize crypto by market cap"""
        large_cap = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'SOLUSDT']
        mid_cap = ['DOGEUSDT', 'DOTUSDT', 'MATICUSDT', 'AVAXUSDT', 'LTCUSDT', 'LINKUSDT']
        
        if symbol in large_cap:
            return 'Large Cap'
        elif symbol in mid_cap:
            return 'Mid Cap'
        else:
            return 'Small Cap'
    
    def _calculate_volatility(self, data: pd.DataFrame) -> float:
        """Calculate crypto volatility (24h price change %)"""
        if len(data) < 2:
            return 0.0
        
        price_changes = data['close'].pct_change().dropna()
        return float(price_changes.std() * 100)
    
    def _analyze_volume(self, data: pd.DataFrame) -> Dict:
        """Analyze trading volume patterns"""
        if 'volume' not in data.columns or data['volume'].sum() == 0:
            return {'status': 'No volume data', 'trend': 'Unknown'}
        
        recent_volume = data['volume'].tail(24).mean()
        historical_volume = data['volume'].mean()
        
        volume_ratio = recent_volume / historical_volume if historical_volume > 0 else 1
        
        if volume_ratio > 1.5:
            trend = 'High Activity'
        elif volume_ratio > 1.2:
            trend = 'Increased Activity' 
        elif volume_ratio < 0.8:
            trend = 'Low Activity'
        else:
            trend = 'Normal Activity'
        
        return {
            'status': f'Volume Ratio: {volume_ratio:.2f}x',
            'trend': trend,
            'recent_avg': f'{recent_volume:,.0f}',
            'historical_avg': f'{historical_volume:,.0f}'
        }
    
    def _find_support_resistance(self, data: pd.DataFrame) -> Dict:
        """Find key support and resistance levels"""
        if len(data) < 50:
            return {'support': 0, 'resistance': 0}
        
        highs = data['high'].tail(100)
        lows = data['low'].tail(100)
        
        # Simple support/resistance based on recent price action
        resistance = float(highs.quantile(0.9))
        support = float(lows.quantile(0.1))
        
        return {
            'support': support,
            'resistance': resistance,
            'current_position': self._get_price_position(data['close'].iloc[-1], support, resistance)
        }
    
    def _get_price_position(self, current_price: float, support: float, resistance: float) -> str:
        """Determine current price position relative to support/resistance"""
        range_size = resistance - support
        if range_size == 0:
            return 'Neutral'
        
        position = (current_price - support) / range_size
        
        if position > 0.8:
            return 'Near Resistance'
        elif position < 0.2:
            return 'Near Support'
        elif position > 0.6:
            return 'Upper Range'
        elif position < 0.4:
            return 'Lower Range'
        else:
            return 'Mid Range'
    
    def _calculate_trend_strength(self, data: pd.DataFrame) -> Dict:
        """Calculate trend strength and direction"""
        if len(data) < 20:
            return {'direction': 'Unknown', 'strength': 0}
        
        # Simple trend calculation using price changes
        short_ma = data['close'].tail(10).mean()
        long_ma = data['close'].tail(20).mean()
        
        if short_ma > long_ma * 1.02:
            direction = 'Strong Uptrend'
            strength = min(100, abs((short_ma / long_ma - 1) * 100))
        elif short_ma > long_ma * 1.005:
            direction = 'Weak Uptrend'
            strength = abs((short_ma / long_ma - 1) * 100)
        elif short_ma < long_ma * 0.98:
            direction = 'Strong Downtrend'
            strength = min(100, abs((short_ma / long_ma - 1) * 100))
        elif short_ma < long_ma * 0.995:
            direction = 'Weak Downtrend'
            strength = abs((short_ma / long_ma - 1) * 100)
        else:
            direction = 'Sideways'
            strength = 0
        
        return {
            'direction': direction,
            'strength': round(strength, 1)
        }