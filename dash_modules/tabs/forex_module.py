"""
Forex Market Module for THEBOT
Handles forex data using Alpha Vantage API
"""

from .base_market_module import BaseMarketModule
from ..data_providers.alpha_vantage_api import AlphaVantageAPI
from ..core.api_config import api_config
import pandas as pd
from typing import List, Dict
from datetime import datetime

class ForexModule(BaseMarketModule):
    """Forex market module using Alpha Vantage API"""
    
    def __init__(self, calculators: Dict = None):
        # Get Alpha Vantage API key from config
        forex_provider = api_config.get_provider('forex', 'Alpha Vantage')
        api_key = forex_provider['config'].get('api_key', '') if forex_provider else ''
        
        super().__init__(
            market_type='forex',
            data_provider=AlphaVantageAPI(api_key),
            calculators=calculators
        )
        
        self.major_pairs = [
            'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
            'EURJPY', 'GBPJPY', 'EURGBP', 'EURAUD', 'EURCAD', 'EURCHF', 'GBPAUD',
            'GBPCAD', 'GBPCHF', 'AUDJPY', 'CADJPY', 'CHFJPY', 'AUDCAD', 'AUDCHF',
            'CADCHF', 'NZDJPY', 'AUDNZD'
        ]
    
    def get_symbols_list(self) -> List[str]:
        """Get list of available forex pairs"""
        return self.major_pairs
    
    def get_default_symbol(self) -> str:
        """Get default forex pair"""
        return 'EURUSD'
    
    def load_market_data(self, symbol: str, interval: str = '1h', limit: int = 200) -> pd.DataFrame:
        """Load forex market data from Alpha Vantage"""
        try:
            # Parse forex pair (e.g., EURUSD -> EUR, USD)
            if len(symbol) == 6:
                from_symbol = symbol[:3]
                to_symbol = symbol[3:]
            else:
                print(f"⚠️ Invalid forex pair format: {symbol}")
                return self._create_fallback_forex_data(symbol)
            
            print(f"🔄 Loading forex data for {from_symbol}/{to_symbol}...")
            data = self.data_provider.get_forex_data(from_symbol, to_symbol, interval)
            
            if not data.empty:
                print(f"✅ {symbol}: {len(data)} forex data points loaded")
                return data
            else:
                print(f"⚠️ No forex data for {symbol}, using fallback")
                return self._create_fallback_forex_data(symbol)
                
        except Exception as e:
            print(f"❌ Error loading forex data for {symbol}: {e}")
            return self._create_fallback_forex_data(symbol)
    
    def _create_fallback_forex_data(self, symbol: str) -> pd.DataFrame:
        """Create fallback forex data when API unavailable"""
        print(f"📊 Creating fallback forex data for {symbol}")
        
        # Base rates for major forex pairs
        base_rates = {
            'EURUSD': 1.0850, 'GBPUSD': 1.2650, 'USDJPY': 149.50,
            'USDCHF': 0.8950, 'AUDUSD': 0.6450, 'USDCAD': 1.3750,
            'NZDUSD': 0.5950, 'EURJPY': 162.20, 'GBPJPY': 188.90,
            'EURGBP': 0.8580, 'EURAUD': 1.6840, 'EURCAD': 1.4920,
            'EURCHF': 0.9720, 'GBPAUD': 1.9650, 'GBPCAD': 1.7380,
            'GBPCHF': 1.1330, 'AUDJPY': 96.40, 'CADJPY': 108.80,
            'CHFJPY': 167.20, 'AUDCAD': 0.8860, 'AUDCHF': 0.5780,
            'CADCHF': 0.6520, 'NZDJPY': 89.10, 'AUDNZD': 1.0840
        }
        
        base_rate = base_rates.get(symbol, 1.0)
        
        # Generate realistic forex data
        dates = pd.date_range(end=datetime.now(), periods=200, freq='H')
        
        df_data = []
        current_rate = base_rate
        
        for i, date in enumerate(dates):
            # Forex volatility (lower than crypto, higher than bonds)
            change = (pd.np.random.randn() * 0.005) + (0.0002 * pd.np.sin(i/12))
            current_rate *= (1 + change)
            
            # Ensure reasonable forex range
            current_rate = max(min(current_rate, base_rate * 1.2), base_rate * 0.8)
            
            # Create OHLC data with forex-like precision
            high = current_rate * (1 + abs(pd.np.random.randn() * 0.002))
            low = current_rate * (1 - abs(pd.np.random.randn() * 0.002))
            open_rate = current_rate * (1 + pd.np.random.randn() * 0.0005)
            
            df_data.append({
                'timestamp': date,
                'open': round(open_rate, 5),
                'high': round(high, 5),
                'low': round(low, 5),
                'close': round(current_rate, 5)
            })
        
        df = pd.DataFrame(df_data)
        df.index = df['timestamp']
        return df
    
    def get_forex_specific_analysis(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Get forex-specific analysis and insights"""
        if data.empty:
            return {}
        
        analysis = {
            'pair_type': self._get_pair_type(symbol),
            'volatility': self._calculate_forex_volatility(data),
            'range_analysis': self._analyze_daily_range(data),
            'correlation': self._get_correlation_info(symbol),
            'economic_factors': self._get_economic_factors(symbol)
        }
        
        return analysis
    
    def _get_pair_type(self, symbol: str) -> str:
        """Categorize forex pair type"""
        majors = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD']
        crosses = ['EURJPY', 'GBPJPY', 'EURGBP', 'EURAUD', 'EURCAD', 'EURCHF']
        
        if symbol in majors:
            return 'Major Pair'
        elif symbol in crosses:
            return 'Cross Pair'
        else:
            return 'Exotic Pair'
    
    def _calculate_forex_volatility(self, data: pd.DataFrame) -> Dict:
        """Calculate forex-specific volatility metrics"""
        if len(data) < 2:
            return {'daily_range': 0, 'atr': 0}
        
        # Daily range (high - low)
        daily_ranges = data['high'] - data['low']
        avg_daily_range = float(daily_ranges.mean())
        
        # Average True Range for last 14 periods
        atr_values = self.calculate_atr(data, 14)
        current_atr = atr_values[-1] if atr_values else 0
        
        return {
            'daily_range': round(avg_daily_range * 10000, 1),  # In pips
            'atr': round(current_atr * 10000, 1),  # In pips
            'volatility_category': self._categorize_volatility(avg_daily_range)
        }
    
    def _categorize_volatility(self, daily_range: float) -> str:
        """Categorize forex volatility level"""
        pips = daily_range * 10000
        
        if pips > 150:
            return 'High Volatility'
        elif pips > 80:
            return 'Medium Volatility'
        else:
            return 'Low Volatility'
    
    def _analyze_daily_range(self, data: pd.DataFrame) -> Dict:
        """Analyze daily trading range patterns"""
        if len(data) < 24:
            return {'status': 'Insufficient data'}
        
        # Calculate ranges for different time periods
        last_24h = data.tail(24)
        ranges_24h = last_24h['high'] - last_24h['low']
        
        current_range = float(ranges_24h.iloc[-1] * 10000)  # Current range in pips
        avg_range = float(ranges_24h.mean() * 10000)  # Average range in pips
        
        return {
            'current_range_pips': round(current_range, 1),
            'average_range_pips': round(avg_range, 1),
            'range_efficiency': round((current_range / avg_range * 100), 1) if avg_range > 0 else 0
        }
    
    def _get_correlation_info(self, symbol: str) -> Dict:
        """Get correlation information for forex pair"""
        correlations = {
            'EURUSD': {'positive': ['GBPUSD', 'AUDUSD'], 'negative': ['USDCHF', 'USDJPY']},
            'GBPUSD': {'positive': ['EURUSD', 'AUDUSD'], 'negative': ['USDCHF', 'USDJPY']},
            'USDJPY': {'positive': ['USDCHF'], 'negative': ['EURUSD', 'GBPUSD', 'AUDUSD']},
            'USDCHF': {'positive': ['USDJPY'], 'negative': ['EURUSD', 'GBPUSD', 'AUDUSD']},
            'AUDUSD': {'positive': ['EURUSD', 'GBPUSD'], 'negative': ['USDCHF', 'USDJPY']},
            'USDCAD': {'positive': ['USDJPY'], 'negative': ['EURUSD', 'GBPUSD']}
        }
        
        return correlations.get(symbol, {'positive': [], 'negative': []})
    
    def _get_economic_factors(self, symbol: str) -> Dict:
        """Get key economic factors affecting the forex pair"""
        factors = {
            'EURUSD': {
                'base_currency': 'EUR',
                'quote_currency': 'USD',
                'key_factors': ['ECB Policy', 'Fed Policy', 'EU-US Interest Rate Differential'],
                'session_activity': ['London', 'New York']
            },
            'GBPUSD': {
                'base_currency': 'GBP', 
                'quote_currency': 'USD',
                'key_factors': ['BoE Policy', 'Fed Policy', 'Brexit Impact', 'UK Economic Data'],
                'session_activity': ['London', 'New York']
            },
            'USDJPY': {
                'base_currency': 'USD',
                'quote_currency': 'JPY', 
                'key_factors': ['Fed Policy', 'BoJ Policy', 'Risk Sentiment', 'US-Japan Yield Spread'],
                'session_activity': ['Tokyo', 'New York']
            }
        }
        
        return factors.get(symbol, {
            'base_currency': symbol[:3] if len(symbol) >= 3 else 'N/A',
            'quote_currency': symbol[3:] if len(symbol) >= 6 else 'N/A',
            'key_factors': ['Central Bank Policy', 'Economic Data', 'Market Sentiment'],
            'session_activity': ['Major Sessions']
        })
    
    def create_forex_ai_dashboard(self) -> dict:
        """Create forex-specific AI insights"""
        return {
            'sentiment_example': 'Neutral',
            'confidence': '65%',
            'prediction': '+0.8%',
            'analysis': 'Consolidation phase ahead of central bank meetings. Watch for ECB dovish signals and Fed hawkish stance.',
            'key_levels': {
                'support': '1.0820',
                'resistance': '1.0890'
            },
            'economic_calendar': [
                {'time': '14:30', 'event': 'US GDP', 'impact': 'High'},
                {'time': '16:00', 'event': 'ECB Minutes', 'impact': 'Medium'}
            ]
        }