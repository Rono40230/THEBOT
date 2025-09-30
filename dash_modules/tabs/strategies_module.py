"""
Strategies Module for THEBOT
Handles trading strategies, backtesting, and AI-driven recommendations
"""

from .base_market_module import BaseMarketModule
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class StrategiesModule(BaseMarketModule):
    """Strategies module for trading strategy analysis and backtesting"""
    
    def __init__(self, calculators: Dict = None):
        super().__init__(
            market_type='strategies',
            data_provider=None,  # Strategies don't need external data provider
            calculators=calculators
        )
        
        self.available_strategies = [
            'Simple Moving Average Crossover',
            'RSI Mean Reversion',
            'Bollinger Bands Strategy',
            'MACD Signal Strategy',
            'Golden Cross Strategy',
            'Support/Resistance Breakout',
            'Volume Weighted Average Price',
            'AI-Enhanced Momentum'
        ]
        
        self.risk_profiles = [
            'Conservative', 'Moderate', 'Aggressive', 'Custom'
        ]
    
    def get_symbols_list(self) -> List[str]:
        """Get list of available strategies"""
        return self.available_strategies
    
    def get_default_symbol(self) -> str:
        """Get default strategy"""
        return 'Simple Moving Average Crossover'
    
    def load_market_data(self, symbol: str, interval: str = '1h', limit: int = 200) -> pd.DataFrame:
        """Load market data for backtesting (strategies don't load external data)"""
        # Strategies module doesn't load external market data
        # It uses data provided by other modules or creates sample data for backtesting
        return pd.DataFrame()
    
    def create_strategies_layout(self) -> html.Div:
        """Create strategies-specific layout"""
        return html.Div([
            # Strategy selection and configuration
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("🎯 Strategy Configuration", className="mb-0")
                        ]),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Strategy Type:", className="form-label"),
                                    dcc.Dropdown(
                                        id='strategy-type-dropdown',
                                        options=[{'label': strategy, 'value': strategy} 
                                               for strategy in self.available_strategies],
                                        value='Simple Moving Average Crossover',
                                        className="mb-3"
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Risk Profile:", className="form-label"),
                                    dcc.Dropdown(
                                        id='risk-profile-dropdown',
                                        options=[{'label': profile, 'value': profile} 
                                               for profile in self.risk_profiles],
                                        value='Moderate',
                                        className="mb-3"
                                    )
                                ], width=6)
                            ]),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Initial Capital ($):", className="form-label"),
                                    dbc.Input(
                                        id='initial-capital-input',
                                        type='number',
                                        value=10000,
                                        min=1000,
                                        step=1000,
                                        className="mb-3"
                                    )
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Position Size (%):", className="form-label"),
                                    dbc.Input(
                                        id='position-size-input',
                                        type='number',
                                        value=10,
                                        min=1,
                                        max=100,
                                        step=1,
                                        className="mb-3"
                                    )
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Stop Loss (%):", className="form-label"),
                                    dbc.Input(
                                        id='stop-loss-input',
                                        type='number',
                                        value=5,
                                        min=1,
                                        max=20,
                                        step=0.5,
                                        className="mb-3"
                                    )
                                ], width=4)
                            ]),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button(
                                        "🚀 Run Backtest",
                                        id='run-backtest-btn',
                                        color="primary",
                                        className="me-2"
                                    ),
                                    dbc.Button(
                                        "🤖 AI Optimization",
                                        id='ai-optimize-btn',
                                        color="success",
                                        outline=True
                                    )
                                ])
                            ])
                        ])
                    ])
                ], width=12)
            ], className="mb-4"),
            
            # Strategy results
            dbc.Row([
                # Performance metrics
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H6("📊 Performance Metrics", className="mb-0")
                        ]),
                        dbc.CardBody([
                            html.Div(id='performance-metrics-content')
                        ])
                    ])
                ], width=4),
                
                # Equity curve
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H6("📈 Equity Curve", className="mb-0")
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id='equity-curve-chart')
                        ])
                    ])
                ], width=8)
            ], className="mb-4"),
            
            # Trade analysis
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H6("📋 Trade Analysis", className="mb-0")
                        ]),
                        dbc.CardBody([
                            html.Div(id='trade-analysis-content')
                        ])
                    ])
                ], width=6),
                
                # AI recommendations
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H6("🤖 AI Recommendations", className="mb-0")
                        ]),
                        dbc.CardBody([
                            html.Div(id='ai-recommendations-content')
                        ])
                    ])
                ], width=6)
            ])
        ])
    
    def run_strategy_backtest(self, strategy_name: str, market_data: pd.DataFrame, 
                            config: Dict) -> Dict:
        """Run backtest for selected strategy"""
        if market_data.empty:
            # Create sample data for demo
            market_data = self._create_sample_market_data()
        
        # Select strategy function
        strategy_func = self._get_strategy_function(strategy_name)
        
        # Run backtest
        results = strategy_func(market_data, config)
        
        return results
    
    def _create_sample_market_data(self) -> pd.DataFrame:
        """Create sample market data for backtesting"""
        dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
        np.random.seed(42)  # For reproducible results
        
        # Generate realistic price data
        price = 100
        prices = []
        
        for i in range(len(dates)):
            # Random walk with slight upward bias
            change = np.random.randn() * 0.02 + 0.0002
            price *= (1 + change)
            prices.append(price)
        
        # Create OHLCV data
        df_data = []
        for i, (date, close_price) in enumerate(zip(dates, prices)):
            high = close_price * (1 + abs(np.random.randn() * 0.01))
            low = close_price * (1 - abs(np.random.randn() * 0.01))
            open_price = close_price * (1 + np.random.randn() * 0.005)
            volume = int(np.random.randint(50000, 200000))
            
            df_data.append({
                'timestamp': date,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close_price, 2),
                'volume': volume
            })
        
        df = pd.DataFrame(df_data)
        df.index = df['timestamp']
        return df
    
    def _get_strategy_function(self, strategy_name: str):
        """Get the strategy function based on name"""
        strategy_map = {
            'Simple Moving Average Crossover': self._sma_crossover_strategy,
            'RSI Mean Reversion': self._rsi_mean_reversion_strategy,
            'Bollinger Bands Strategy': self._bollinger_bands_strategy,
            'MACD Signal Strategy': self._macd_strategy,
            'Golden Cross Strategy': self._golden_cross_strategy,
            'Support/Resistance Breakout': self._breakout_strategy,
            'Volume Weighted Average Price': self._vwap_strategy,
            'AI-Enhanced Momentum': self._ai_momentum_strategy
        }
        
        return strategy_map.get(strategy_name, self._sma_crossover_strategy)
    
    def _sma_crossover_strategy(self, data: pd.DataFrame, config: Dict) -> Dict:
        """Simple Moving Average Crossover Strategy"""
        # Calculate moving averages
        data['SMA_fast'] = data['close'].rolling(window=10).mean()
        data['SMA_slow'] = data['close'].rolling(window=30).mean()
        
        # Generate signals
        data['signal'] = 0
        data['signal'][10:] = np.where(
            data['SMA_fast'][10:] > data['SMA_slow'][10:], 1, 0
        )
        data['position'] = data['signal'].diff()
        
        # Run backtest
        return self._execute_backtest(data, config, 'SMA Crossover')
    
    def _rsi_mean_reversion_strategy(self, data: pd.DataFrame, config: Dict) -> Dict:
        """RSI Mean Reversion Strategy"""
        # Calculate RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # Generate signals (buy oversold, sell overbought)
        data['signal'] = 0
        data.loc[data['RSI'] < 30, 'signal'] = 1  # Buy signal
        data.loc[data['RSI'] > 70, 'signal'] = -1  # Sell signal
        data['position'] = data['signal'].diff()
        
        return self._execute_backtest(data, config, 'RSI Mean Reversion')
    
    def _bollinger_bands_strategy(self, data: pd.DataFrame, config: Dict) -> Dict:
        """Bollinger Bands Strategy"""
        # Calculate Bollinger Bands
        window = 20
        data['BB_middle'] = data['close'].rolling(window=window).mean()
        data['BB_std'] = data['close'].rolling(window=window).std()
        data['BB_upper'] = data['BB_middle'] + (data['BB_std'] * 2)
        data['BB_lower'] = data['BB_middle'] - (data['BB_std'] * 2)
        
        # Generate signals
        data['signal'] = 0
        data.loc[data['close'] < data['BB_lower'], 'signal'] = 1  # Buy at lower band
        data.loc[data['close'] > data['BB_upper'], 'signal'] = -1  # Sell at upper band
        data['position'] = data['signal'].diff()
        
        return self._execute_backtest(data, config, 'Bollinger Bands')
    
    def _macd_strategy(self, data: pd.DataFrame, config: Dict) -> Dict:
        """MACD Signal Strategy"""
        # Calculate MACD
        ema_fast = data['close'].ewm(span=12).mean()
        ema_slow = data['close'].ewm(span=26).mean()
        data['MACD'] = ema_fast - ema_slow
        data['MACD_signal'] = data['MACD'].ewm(span=9).mean()
        data['MACD_histogram'] = data['MACD'] - data['MACD_signal']
        
        # Generate signals
        data['signal'] = 0
        data['signal'][1:] = np.where(
            (data['MACD'][1:] > data['MACD_signal'][1:]) & 
            (data['MACD'][:-1].values <= data['MACD_signal'][:-1].values), 1, 0
        )
        data.loc[
            (data['MACD'] < data['MACD_signal']) & 
            (data['MACD'].shift(1) >= data['MACD_signal'].shift(1)), 'signal'
        ] = -1
        data['position'] = data['signal'].diff()
        
        return self._execute_backtest(data, config, 'MACD Strategy')
    
    def _golden_cross_strategy(self, data: pd.DataFrame, config: Dict) -> Dict:
        """Golden Cross Strategy (50-day vs 200-day MA)"""
        data['MA_50'] = data['close'].rolling(window=50).mean()
        data['MA_200'] = data['close'].rolling(window=200).mean()
        
        # Generate signals
        data['signal'] = 0
        data['signal'][200:] = np.where(
            data['MA_50'][200:] > data['MA_200'][200:], 1, 0
        )
        data['position'] = data['signal'].diff()
        
        return self._execute_backtest(data, config, 'Golden Cross')
    
    def _breakout_strategy(self, data: pd.DataFrame, config: Dict) -> Dict:
        """Support/Resistance Breakout Strategy"""
        # Calculate support and resistance levels
        window = 20
        data['resistance'] = data['high'].rolling(window=window).max()
        data['support'] = data['low'].rolling(window=window).min()
        
        # Generate signals
        data['signal'] = 0
        data.loc[data['close'] > data['resistance'].shift(1), 'signal'] = 1
        data.loc[data['close'] < data['support'].shift(1), 'signal'] = -1
        data['position'] = data['signal'].diff()
        
        return self._execute_backtest(data, config, 'Breakout Strategy')
    
    def _vwap_strategy(self, data: pd.DataFrame, config: Dict) -> Dict:
        """Volume Weighted Average Price Strategy"""
        # Calculate VWAP
        data['price_volume'] = data['close'] * data['volume']
        data['VWAP'] = data['price_volume'].cumsum() / data['volume'].cumsum()
        
        # Generate signals
        data['signal'] = 0
        data.loc[data['close'] > data['VWAP'], 'signal'] = 1
        data.loc[data['close'] < data['VWAP'], 'signal'] = -1
        data['position'] = data['signal'].diff()
        
        return self._execute_backtest(data, config, 'VWAP Strategy')
    
    def _ai_momentum_strategy(self, data: pd.DataFrame, config: Dict) -> Dict:
        """AI-Enhanced Momentum Strategy"""
        # Combine multiple indicators with AI-like scoring
        data['RSI'] = self._calculate_rsi(data['close'])
        data['SMA_20'] = data['close'].rolling(window=20).mean()
        data['price_change'] = data['close'].pct_change(5)
        data['volume_ratio'] = data['volume'] / data['volume'].rolling(window=10).mean()
        
        # AI scoring system (simplified)
        momentum_score = (
            (data['close'] > data['SMA_20']).astype(int) * 0.3 +
            (data['RSI'] > 50).astype(int) * 0.2 +
            (data['price_change'] > 0.02).astype(int) * 0.3 +
            (data['volume_ratio'] > 1.2).astype(int) * 0.2
        )
        
        # Generate signals based on AI score
        data['signal'] = 0
        data.loc[momentum_score > 0.7, 'signal'] = 1
        data.loc[momentum_score < 0.3, 'signal'] = -1
        data['position'] = data['signal'].diff()
        
        return self._execute_backtest(data, config, 'AI Momentum')
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _execute_backtest(self, data: pd.DataFrame, config: Dict, strategy_name: str) -> Dict:
        """Execute backtest with trade management"""
        initial_capital = config.get('initial_capital', 10000)
        position_size = config.get('position_size', 10) / 100  # Convert to decimal
        stop_loss = config.get('stop_loss', 5) / 100  # Convert to decimal
        
        # Initialize tracking variables
        capital = initial_capital
        position = 0
        entry_price = 0
        equity_curve = []
        trades = []
        
        for i, row in data.iterrows():
            current_price = row['close']
            signal = row.get('signal', 0)
            
            # Check for stop loss
            if position != 0 and entry_price > 0:
                if position > 0 and current_price <= entry_price * (1 - stop_loss):
                    # Stop loss triggered for long position
                    pnl = position * (current_price - entry_price)
                    capital += position * current_price
                    trades.append({
                        'entry_date': entry_date,
                        'exit_date': i,
                        'entry_price': entry_price,
                        'exit_price': current_price,
                        'position_size': position,
                        'pnl': pnl,
                        'exit_reason': 'Stop Loss'
                    })
                    position = 0
                    entry_price = 0
                elif position < 0 and current_price >= entry_price * (1 + stop_loss):
                    # Stop loss triggered for short position
                    pnl = position * (entry_price - current_price)
                    capital += abs(position) * current_price
                    trades.append({
                        'entry_date': entry_date,
                        'exit_date': i,
                        'entry_price': entry_price,
                        'exit_price': current_price,
                        'position_size': position,
                        'pnl': pnl,
                        'exit_reason': 'Stop Loss'
                    })
                    position = 0
                    entry_price = 0
            
            # Process signals
            if signal == 1 and position <= 0:  # Buy signal
                if position < 0:  # Close short position
                    pnl = position * (entry_price - current_price)
                    capital += abs(position) * current_price
                    trades.append({
                        'entry_date': entry_date,
                        'exit_date': i,
                        'entry_price': entry_price,
                        'exit_price': current_price,
                        'position_size': position,
                        'pnl': pnl,
                        'exit_reason': 'Signal'
                    })
                
                # Open long position
                position_value = capital * position_size
                position = position_value / current_price
                capital -= position_value
                entry_price = current_price
                entry_date = i
                
            elif signal == -1 and position >= 0:  # Sell signal
                if position > 0:  # Close long position
                    pnl = position * (current_price - entry_price)
                    capital += position * current_price
                    trades.append({
                        'entry_date': entry_date,
                        'exit_date': i,
                        'entry_price': entry_price,
                        'exit_price': current_price,
                        'position_size': position,
                        'pnl': pnl,
                        'exit_reason': 'Signal'
                    })
                
                # Open short position
                position_value = capital * position_size
                position = -position_value / current_price
                capital -= position_value
                entry_price = current_price
                entry_date = i
            
            # Calculate current equity
            if position > 0:
                current_equity = capital + (position * current_price)
            elif position < 0:
                current_equity = capital + (abs(position) * current_price) + (position * (entry_price - current_price))
            else:
                current_equity = capital
            
            equity_curve.append({
                'date': i,
                'equity': current_equity,
                'price': current_price
            })
        
        # Close any remaining position
        if position != 0:
            final_price = data['close'].iloc[-1]
            if position > 0:
                pnl = position * (final_price - entry_price)
                capital += position * final_price
            else:
                pnl = position * (entry_price - final_price)
                capital += abs(position) * final_price
            
            trades.append({
                'entry_date': entry_date,
                'exit_date': data.index[-1],
                'entry_price': entry_price,
                'exit_price': final_price,
                'position_size': position,
                'pnl': pnl,
                'exit_reason': 'End of Period'
            })
        
        # Calculate performance metrics
        final_equity = capital
        total_return = (final_equity - initial_capital) / initial_capital
        
        # Convert trades to DataFrame for analysis
        trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()
        
        return {
            'strategy_name': strategy_name,
            'initial_capital': initial_capital,
            'final_equity': final_equity,
            'total_return': total_return,
            'equity_curve': equity_curve,
            'trades': trades_df,
            'performance_metrics': self._calculate_performance_metrics(
                equity_curve, trades_df, initial_capital
            )
        }
    
    def _calculate_performance_metrics(self, equity_curve: List[Dict], 
                                     trades_df: pd.DataFrame, initial_capital: float) -> Dict:
        """Calculate comprehensive performance metrics"""
        if not equity_curve:
            return {}
        
        equity_df = pd.DataFrame(equity_curve)
        equity_values = equity_df['equity'].values
        
        # Basic metrics
        total_return = (equity_values[-1] - initial_capital) / initial_capital
        
        # Calculate daily returns
        daily_returns = pd.Series(equity_values).pct_change().dropna()
        
        # Risk metrics
        volatility = daily_returns.std() * np.sqrt(252)  # Annualized
        sharpe_ratio = (daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252)) if volatility > 0 else 0
        
        # Drawdown analysis
        peak = equity_df['equity'].expanding().max()
        drawdown = (equity_df['equity'] - peak) / peak
        max_drawdown = drawdown.min()
        
        # Trade statistics
        if not trades_df.empty:
            winning_trades = trades_df[trades_df['pnl'] > 0]
            losing_trades = trades_df[trades_df['pnl'] < 0]
            
            win_rate = len(winning_trades) / len(trades_df) if len(trades_df) > 0 else 0
            avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
            avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0
            profit_factor = abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) if len(losing_trades) > 0 and losing_trades['pnl'].sum() != 0 else float('inf')
        else:
            win_rate = 0
            avg_win = 0
            avg_loss = 0
            profit_factor = 0
        
        return {
            'total_return': round(total_return * 100, 2),
            'annualized_return': round(total_return * 100, 2),  # Simplified
            'volatility': round(volatility * 100, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_drawdown': round(max_drawdown * 100, 2),
            'total_trades': len(trades_df),
            'win_rate': round(win_rate * 100, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2)
        }
    
    def create_performance_metrics_display(self, metrics: Dict) -> html.Div:
        """Create performance metrics display"""
        if not metrics:
            return html.Div("No metrics available", className="text-muted")
        
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6("📈 Returns", className="text-primary"),
                    html.P(f"{metrics.get('total_return', 0):.2f}%", className="h4 mb-0"),
                    html.Small("Total Return", className="text-muted")
                ], width=6),
                dbc.Col([
                    html.H6("📊 Sharpe Ratio", className="text-success"),
                    html.P(f"{metrics.get('sharpe_ratio', 0):.2f}", className="h4 mb-0"),
                    html.Small("Risk-Adjusted Return", className="text-muted")
                ], width=6)
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    html.H6("📉 Max Drawdown", className="text-danger"),
                    html.P(f"{metrics.get('max_drawdown', 0):.2f}%", className="h4 mb-0"),
                    html.Small("Worst Peak-to-Trough", className="text-muted")
                ], width=6),
                dbc.Col([
                    html.H6("🎯 Win Rate", className="text-info"),
                    html.P(f"{metrics.get('win_rate', 0):.1f}%", className="h4 mb-0"),
                    html.Small(f"{metrics.get('total_trades', 0)} Trades", className="text-muted")
                ], width=6)
            ])
        ])
    
    def create_equity_curve_chart(self, equity_curve: List[Dict]) -> go.Figure:
        """Create equity curve chart"""
        if not equity_curve:
            fig = go.Figure()
            fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
            return fig
        
        df = pd.DataFrame(equity_curve)
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=['Portfolio Equity', 'Asset Price'],
            row_heights=[0.7, 0.3]
        )
        
        # Equity curve
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['equity'],
                mode='lines',
                name='Portfolio Value',
                line=dict(color='#1f77b4', width=2)
            ),
            row=1, col=1
        )
        
        # Asset price
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['price'],
                mode='lines',
                name='Asset Price',
                line=dict(color='#ff7f0e', width=1.5)
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title="Strategy Performance",
            height=500,
            showlegend=True,
            template="plotly_white"
        )
        
        return fig
    
    def create_ai_recommendations(self, strategy_results: Dict) -> html.Div:
        """Create AI-powered strategy recommendations"""
        if not strategy_results:
            return html.Div("Run a backtest to get AI recommendations", className="text-muted")
        
        metrics = strategy_results.get('performance_metrics', {})
        
        # AI analysis (simplified rule-based system)
        recommendations = []
        
        # Performance analysis
        total_return = metrics.get('total_return', 0)
        sharpe_ratio = metrics.get('sharpe_ratio', 0)
        max_drawdown = metrics.get('max_drawdown', 0)
        win_rate = metrics.get('win_rate', 0)
        
        if total_return > 15:
            recommendations.append(("🎯 Strong Performance", "success", 
                                  f"Strategy shows excellent returns of {total_return:.1f}%"))
        elif total_return > 5:
            recommendations.append(("📈 Moderate Performance", "warning", 
                                  f"Strategy shows decent returns of {total_return:.1f}%"))
        else:
            recommendations.append(("🔍 Needs Optimization", "danger", 
                                  f"Strategy underperforming with {total_return:.1f}% returns"))
        
        # Risk analysis
        if abs(max_drawdown) > 20:
            recommendations.append(("⚠️ High Risk", "danger", 
                                  f"Maximum drawdown of {max_drawdown:.1f}% is concerning"))
        elif abs(max_drawdown) > 10:
            recommendations.append(("⚡ Moderate Risk", "warning", 
                                  f"Drawdown of {max_drawdown:.1f}% within acceptable range"))
        else:
            recommendations.append(("🛡️ Low Risk", "success", 
                                  f"Well-controlled risk with {max_drawdown:.1f}% max drawdown"))
        
        # Win rate analysis
        if win_rate > 60:
            recommendations.append(("🎯 High Accuracy", "success", 
                                  f"Excellent win rate of {win_rate:.1f}%"))
        elif win_rate > 40:
            recommendations.append(("📊 Balanced", "info", 
                                  f"Reasonable win rate of {win_rate:.1f}%"))
        else:
            recommendations.append(("🔧 Low Accuracy", "warning", 
                                  f"Win rate of {win_rate:.1f}% needs improvement"))
        
        # Create recommendations display
        recommendation_cards = []
        for title, color, description in recommendations:
            card = dbc.Alert([
                html.H6(title, className="alert-heading mb-1"),
                html.P(description, className="mb-0")
            ], color=color, className="mb-2")
            recommendation_cards.append(card)
        
        # Add optimization suggestions
        optimization_suggestions = html.Div([
            html.Hr(),
            html.H6("🚀 Optimization Suggestions:", className="mb-2"),
            html.Ul([
                html.Li("Consider adjusting position sizing for better risk management"),
                html.Li("Test different time frames for entry/exit signals"),
                html.Li("Add volatility-based position sizing"),
                html.Li("Implement dynamic stop-loss levels"),
                html.Li("Consider market regime filtering")
            ], className="small text-muted")
        ])
        
        return html.Div(recommendation_cards + [optimization_suggestions])