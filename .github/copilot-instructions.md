# THEBOT AI Coding Guidelines

## 🏗️ Architecture Overview

THEBOT is a modular trading analysis platform with dual architecture undergoing migration:

- **Legacy**: `dash_modules/` - MVC pattern with mixed responsibilities
- **Modern**: `src/thebot/` - Strict modular pattern with single responsibility

**Core Pattern**: All indicators follow `[category]/[name]/{__init__.py, config.py, calculator.py, plotter.py}`

## 📁 Key Directories

- `src/thebot/indicators/` - Modular indicators (basic/, momentum/, structural/, etc.)
- `src/thebot/services/` - Dependency injection container & cross-cutting concerns
- `src/thebot/types/` - Common type definitions (SignalDirection, TimeFrame, MarketData)
- `src/thebot/core/` - Base classes and shared utilities
- `dash_modules/` - Legacy architecture (being migrated to src/thebot/)
- `tests/unit/indicators/` - Comprehensive indicator tests (15+ tests per indicator)

## ⚙️ Configuration Pattern

Use dataclasses with validation, never Pydantic:

```python
@dataclass
class IndicatorConfig:
    period: int = 20
    enable_signals: bool = True

    def __post_init__(self):
        if self.period <= 0:
            raise ValueError("Period must be positive")
```

## 🔢 Data Handling Rules

- **Prices**: Always use `Decimal` to avoid floating point errors
- **Calculations**: Vectorize with numpy/pandas, never Python loops
- **Validation**: Strict input validation with custom exceptions

## 📊 Indicator Implementation

**Structure** (mandatory):
```
src/thebot/indicators/[category]/[name]/
├── __init__.py       # Factory & API
├── config.py         # Dataclass config with validation
├── calculator.py     # Pure calculation logic (no state)
└── plotter.py        # Plotly visualization
```

**Example**: `src/thebot/indicators/basic/sma/`

## 🚀 Development Workflow

```bash
# Setup
./setup_dev_env.sh                    # Creates .venv
source .venv/bin/activate            # Activate venv

# Development
black .                              # Format code
isort .                              # Sort imports
mypy src/thebot/                     # Type check
pytest tests/unit/indicators/        # Run indicator tests

# Launch
python launch_dash_professional.py   # Start Dash app
```

## 🧪 Testing Requirements

- **Coverage**: >80% target, 15+ tests per indicator
- **Structure**: `tests/unit/indicators/[category]/test_[name].py`
- **Assertions**: Test calculations, signals, edge cases, NaN handling

## 📝 Code Quality Rules

- **Logging**: `logger.info/debug/error()`, never `print()`
- **Imports**: Sorted with isort, no star imports
- **Types**: Full type hints, mypy compliant
- **Errors**: Custom exceptions with error codes
- **Async**: Use async/await for all I/O operations

## 🔧 Dependency Injection

```python
from src.thebot.services.container import DependencyContainer

container = DependencyContainer()
container.register_singleton('data_manager', DataManager())
```

## 📈 Common Patterns

- **Factory Pattern**: `src/thebot/indicators/factory.py` for indicator creation
- **Repository Pattern**: Data access abstraction
- **Observer Pattern**: Event-driven components
- **Strategy Pattern**: Multiple calculation algorithms

## 🚨 Critical Constraints

- Never break existing functionality without explicit approval
- Maintain backward compatibility during migration
- Use Decimal for all price calculations
- Follow single responsibility principle strictly
- No credentials/API keys in code (use secrets_manager)

## 🎯 Trading Focus

- **Scalping**: 1m, 5m, 15m timeframes
- **Day Trading**: 1h, 4h timeframes
- **Markets**: Crypto (Binance), Forex, Stocks
- **Events**: Economic calendar integration

## 🔍 Debugging Commands

```bash
# Validate config
python scripts/validate_config.py

# Run specific tests
pytest tests/unit/indicators/basic/test_sma.py -v

# Check imports
python -c "from src.thebot.indicators.basic.sma import SMA; print('OK')"
```

## 📚 Reference Files

- `ROADMAP.md` - Migration status and priorities
- `.clinerules` - Behavioral guidelines for non-technical users
- `pyproject.toml` - Tool configurations (black, isort, pytest)
- `src/thebot/indicators/basic/sma/` - Complete indicator example</content>
<parameter name="filePath">/home/rono/THEBOT/.github/copilot-instructions.md