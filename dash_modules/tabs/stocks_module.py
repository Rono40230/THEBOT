"""
Stocks Market Module for THEBOT
Handles stock data using Alpha Vantage API
"""

from .base_market_module import BaseMarketModule
from ..data_providers.alpha_vantage_api import AlphaVantageAPI
from ..core.api_config import api_config
import pandas as pd
from typing import List, Dict
from datetime import datetime

class StocksModule(BaseMarketModule):
    """Stocks market module using Alpha Vantage API"""
    
    def __init__(self, calculators: Dict = None):
        # Get Alpha Vantage API key from config
        stocks_provider = api_config.get_provider('stocks', 'Alpha Vantage')
        api_key = stocks_provider['config'].get('api_key', '') if stocks_provider else ''
        
        super().__init__(
            market_type='stocks',
            data_provider=AlphaVantageAPI(api_key),
            calculators=calculators
        )
        
        self.popular_stocks = [
            # Tech Giants
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX',
            # Traditional Blue Chips
            'JPM', 'JNJ', 'PG', 'UNH', 'HD', 'MA', 'V', 'WMT', 'DIS', 'KO',
            # Financial
            'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP',
            # Industrial
            'BA', 'CAT', 'GE', 'MMM', 'HON',
            # Healthcare
            'PFE', 'ABBV', 'TMO', 'ABT', 'MRK', 'LLY',
            # Energy
            'XOM', 'CVX', 'COP', 'SLB',
            # ETFs
            'SPY', 'QQQ', 'IWM', 'VTI', 'VEA', 'VWO'
        ]
    
    def get_symbols_list(self) -> List[str]:
        """Get list of available stock symbols"""
        return self.popular_stocks
    
    def get_default_symbol(self) -> str:
        """Get default stock symbol"""
        return 'AAPL'
    
    def load_market_data(self, symbol: str, interval: str = '1h', limit: int = 200) -> pd.DataFrame:
        """Load stock market data from Alpha Vantage"""
        try:
            print(f"🔄 Loading stock data for {symbol}...")
            data = self.data_provider.get_stock_data(symbol, interval)
            
            if not data.empty:
                print(f"✅ {symbol}: {len(data)} stock data points loaded")
                return data
            else:
                print(f"⚠️ No stock data for {symbol}, using fallback")
                return self._create_fallback_stock_data(symbol)
                
        except Exception as e:
            print(f"❌ Error loading stock data for {symbol}: {e}")
            return self._create_fallback_stock_data(symbol)
    
    def _create_fallback_stock_data(self, symbol: str) -> pd.DataFrame:
        """Create fallback stock data when API unavailable"""
        print(f"📊 Creating fallback stock data for {symbol}")
        
        # Base prices for popular stocks
        base_prices = {
            # Tech Giants
            'AAPL': 175.50, 'MSFT': 415.20, 'GOOGL': 140.30, 'AMZN': 145.80,
            'META': 325.40, 'TSLA': 245.60, 'NVDA': 875.30, 'NFLX': 385.90,
            # Blue Chips
            'JPM': 155.20, 'JNJ': 168.30, 'PG': 152.40, 'UNH': 485.70,
            'HD': 325.80, 'MA': 425.90, 'V': 245.60, 'WMT': 165.20,
            'DIS': 95.40, 'KO': 58.70,
            # Financial
            'BAC': 32.45, 'WFC': 45.30, 'GS': 385.20, 'MS': 88.50,
            'C': 52.80, 'AXP': 185.40,
            # ETFs
            'SPY': 485.20, 'QQQ': 385.60, 'IWM': 195.30, 'VTI': 245.80
        }
        
        base_price = base_prices.get(symbol, 100.0)
        
        # Generate realistic stock data
        dates = pd.date_range(end=datetime.now(), periods=200, freq='H')
        
        df_data = []
        current_price = base_price
        
        for i, date in enumerate(dates):
            # Stock market volatility (moderate, less than crypto)
            change = (pd.np.random.randn() * 0.015) + (0.001 * pd.np.sin(i/6))
            current_price *= (1 + change)
            
            # Ensure reasonable stock price range
            current_price = max(current_price, base_price * 0.5)
            
            # Create OHLCV data with stock-like characteristics
            high = current_price * (1 + abs(pd.np.random.randn() * 0.008))
            low = current_price * (1 - abs(pd.np.random.randn() * 0.008))
            open_price = current_price * (1 + pd.np.random.randn() * 0.003)
            
            # Stock volume patterns (higher during market hours)
            hour = date.hour
            if 9 <= hour <= 16:  # Market hours
                volume = int(pd.np.random.randint(500000, 5000000))
            else:
                volume = int(pd.np.random.randint(50000, 500000))
            
            df_data.append({
                'timestamp': date,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(current_price, 2),
                'volume': volume
            })
        
        df = pd.DataFrame(df_data)
        df.index = df['timestamp']
        return df
    
    def get_stocks_specific_analysis(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Get stocks-specific analysis and insights"""
        if data.empty:
            return {}
        
        analysis = {
            'sector': self._get_sector(symbol),
            'market_cap': self._get_market_cap_category(symbol),
            'volatility': self._calculate_stock_volatility(data),
            'volume_analysis': self._analyze_stock_volume(data),
            'valuation_metrics': self._get_valuation_metrics(symbol),
            'earnings_info': self._get_earnings_info(symbol)
        }
        
        return analysis
    
    def _get_sector(self, symbol: str) -> str:
        """Get sector classification for stock"""
        sectors = {
            # Technology
            'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology',
            'AMZN': 'Technology', 'META': 'Technology', 'NVDA': 'Technology',
            'NFLX': 'Technology', 'TSLA': 'Technology',
            
            # Healthcare
            'JNJ': 'Healthcare', 'PFE': 'Healthcare', 'ABBV': 'Healthcare',
            'UNH': 'Healthcare', 'TMO': 'Healthcare', 'ABT': 'Healthcare',
            'MRK': 'Healthcare', 'LLY': 'Healthcare',
            
            # Financial
            'JPM': 'Financial', 'BAC': 'Financial', 'WFC': 'Financial',
            'GS': 'Financial', 'MS': 'Financial', 'C': 'Financial',
            'AXP': 'Financial', 'MA': 'Financial', 'V': 'Financial',
            
            # Consumer Goods
            'PG': 'Consumer Goods', 'KO': 'Consumer Goods', 'WMT': 'Consumer Goods',
            'HD': 'Consumer Goods', 'DIS': 'Consumer Goods',
            
            # Industrial
            'BA': 'Industrial', 'CAT': 'Industrial', 'GE': 'Industrial',
            'MMM': 'Industrial', 'HON': 'Industrial',
            
            # Energy
            'XOM': 'Energy', 'CVX': 'Energy', 'COP': 'Energy', 'SLB': 'Energy'
        }
        
        return sectors.get(symbol, 'Diversified')
    
    def _get_market_cap_category(self, symbol: str) -> str:
        """Categorize stock by market cap"""
        large_cap = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 
                    'JPM', 'JNJ', 'PG', 'UNH', 'HD', 'MA', 'V', 'WMT']
        mid_cap = ['DIS', 'KO', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP']
        
        if symbol in large_cap:
            return 'Large Cap (>$10B)'
        elif symbol in mid_cap:
            return 'Mid Cap ($2B-$10B)'
        else:
            return 'Small Cap (<$2B)'
    
    def _calculate_stock_volatility(self, data: pd.DataFrame) -> Dict:
        """Calculate stock-specific volatility metrics"""
        if len(data) < 20:
            return {'daily_volatility': 0, 'beta_estimate': 1.0}
        
        # Daily returns
        returns = data['close'].pct_change().dropna()
        daily_volatility = float(returns.std() * 100)
        
        # Annualized volatility (assuming 252 trading days)
        annualized_volatility = daily_volatility * (252 ** 0.5)
        
        return {
            'daily_volatility': round(daily_volatility, 2),
            'annualized_volatility': round(annualized_volatility, 2),
            'volatility_category': self._categorize_stock_volatility(daily_volatility)
        }
    
    def _categorize_stock_volatility(self, daily_vol: float) -> str:
        """Categorize stock volatility level"""
        if daily_vol > 3.0:
            return 'High Volatility'
        elif daily_vol > 1.5:
            return 'Medium Volatility'
        else:
            return 'Low Volatility'
    
    def _analyze_stock_volume(self, data: pd.DataFrame) -> Dict:
        """Analyze stock trading volume patterns"""
        if 'volume' not in data.columns or data['volume'].sum() == 0:
            return {'status': 'No volume data', 'trend': 'Unknown'}
        
        # Volume analysis
        recent_volume = data['volume'].tail(10).mean()
        historical_volume = data['volume'].mean()
        
        volume_ratio = recent_volume / historical_volume if historical_volume > 0 else 1
        
        # Volume trend analysis
        if volume_ratio > 2.0:
            trend = 'Exceptional Activity'
        elif volume_ratio > 1.5:
            trend = 'High Activity'
        elif volume_ratio > 1.2:
            trend = 'Above Average'
        elif volume_ratio < 0.7:
            trend = 'Below Average'
        else:
            trend = 'Normal Activity'
        
        return {
            'volume_ratio': round(volume_ratio, 2),
            'trend': trend,
            'recent_avg': f'{recent_volume:,.0f}',
            'historical_avg': f'{historical_volume:,.0f}'
        }
    
    def _get_valuation_metrics(self, symbol: str) -> Dict:
        """Get estimated valuation metrics (simplified)"""
        # Simplified P/E estimates based on sector
        pe_estimates = {
            'Technology': 25.0, 'Healthcare': 18.0, 'Financial': 12.0,
            'Consumer Goods': 22.0, 'Industrial': 16.0, 'Energy': 14.0
        }
        
        sector = self._get_sector(symbol)
        estimated_pe = pe_estimates.get(sector, 20.0)
        
        return {
            'estimated_pe': estimated_pe,
            'sector_avg_pe': estimated_pe,
            'valuation': 'Fair' if 15 <= estimated_pe <= 25 else ('Expensive' if estimated_pe > 25 else 'Cheap')
        }
    
    def _get_earnings_info(self, symbol: str) -> Dict:
        """Get earnings-related information"""
        # Simplified earnings calendar (mock data)
        import random
        
        days_to_earnings = random.randint(5, 90)
        
        return {
            'next_earnings': f'In {days_to_earnings} days',
            'last_earnings': 'Beat estimates',
            'consensus': 'Hold',
            'analysts_target': 'Price target range varies by analyst'
        }
    
    def create_stocks_ai_dashboard(self) -> dict:
        """Create stocks-specific AI insights"""
        return {
            'sentiment_example': 'Bullish',
            'confidence': '72%',
            'prediction': '+8.3%',
            'analysis': 'Strong fundamentals with positive earnings outlook. Sector rotation favoring growth stocks.',
            'key_levels': {
                'support': '$165.20',
                'resistance': '$182.50'
            },
            'earnings_calendar': [
                {'date': '2024-01-15', 'company': 'Major Bank Earnings', 'impact': 'High'},
                {'date': '2024-01-18', 'company': 'Tech Earnings Season', 'impact': 'High'}
            ],
            'analyst_ratings': {
                'buy': 8,
                'hold': 5,
                'sell': 1,
                'average_target': '$185.00'
            }
        }