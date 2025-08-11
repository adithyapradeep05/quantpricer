# QuantPricer 📈

A personal learning tool for European option pricing using Black-Scholes formulas. This project implements core mathematical functions from scratch using only `math` and `numpy`, with no SciPy dependency.

## 🎯 Purpose

QuantPricer is designed to help you learn:
- **Python programming** with clean, readable code
- **Options mathematics** through hands-on implementation
- **Financial engineering** concepts with practical examples
- **Software engineering** best practices (testing, documentation, modular design)

## 📋 Scope

- **European options only** (no American options)
- **No dividends** (standard Black-Scholes assumptions)
- **No early exercise** (European-style)
- **Core math from scratch** (no SciPy dependency)

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Installation

1. **Clone or download** this project
2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment:**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running Tests

Validate that everything works correctly:

```bash
pytest -q
```

You should see all tests pass with the golden values validation.

### Running the Application

Launch the Streamlit web interface:

```bash
streamlit run app/app.py
```

The app will open in your browser with a clean interface for option pricing and analysis.

## 🔍 Golden Values Validation

**Test Case:** S=100, K=100, r=0.05, σ=0.2, T=1

| Metric | Expected Value | Your Results |
|--------|----------------|--------------|
| **d1** | 0.3500 | ✅ |
| **d2** | 0.1500 | ✅ |
| **Call Price** | 10.4506 | ✅ |
| **Put Price** | 5.5735 | ✅ |
| **Call Delta** | 0.63683 | ✅ |
| **Put Delta** | -0.36317 | ✅ |
| **Gamma** | 0.018762 | ✅ |
| **Vega** | 37.5240 | ✅ |
| **Call Theta** | -6.4140 | ✅ |
| **Put Theta** | -1.6579 | ✅ |
| **Call Rho** | 53.2325 | ✅ |
| **Put Rho** | -41.8905 | ✅ |

## 📁 Project Structure

```
quantpricer/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── normals.py        # φ, Φ using math.erf
│   │   ├── bs.py             # d1, d2, price_call, price_put
│   │   ├── greeks.py         # delta, gamma, vega, theta, rho
│   │   └── iv.py             # implied vol: bisection + Newton-Raphson
│   └── utils/
│       ├── __init__.py
│       ├── plots.py          # price curves + heatmaps
│       └── logging.py        # SQLite logger
├── app/
│   └── app.py                # Streamlit UI
├── tests/
│   ├── __init__.py
│   ├── test_normals.py
│   ├── test_bs.py
│   ├── test_greeks.py
│   └── test_iv.py
├── reports/                  # saved charts
├── README.md
├── requirements.txt
└── pyproject.toml
```

## 🧮 Core Features

### 1. Normal Distribution Functions (`src/core/normals.py`)
- `normal_pdf(x)` - Standard normal probability density function φ(x)
- `normal_cdf(x)` - Standard normal cumulative distribution function Φ(x)
- Uses `math.erf` only (no SciPy)

### 2. Black-Scholes Pricing (`src/core/bs.py`)
- `d1(S, K, r, sigma, T)` and `d2(d1, sigma, T)` calculations
- `price_call(S, K, T, r, sigma)` and `price_put(S, K, T, r, sigma)`
- Proper edge case handling (T=0, σ=0)
- Input validation

### 3. Option Greeks (`src/core/greeks.py`)
- **Delta**: Rate of change with respect to stock price
- **Gamma**: Rate of change of delta with respect to stock price
- **Vega**: Rate of change with respect to volatility
- **Theta**: Rate of change with respect to time
- **Rho**: Rate of change with respect to risk-free rate

### 4. Implied Volatility (`src/core/iv.py`)
- Robust bisection method with Newton-Raphson fallback
- No-arbitrage bounds checking
- Handles edge cases and convergence issues

### 5. Visualization (`src/utils/plots.py`)
- Price curves vs stock price
- Price heatmaps (S vs volatility)
- Greeks curves
- Saves charts to `reports/` directory

### 6. Data Logging (`src/utils/logging.py`)
- SQLite database for scenario tracking
- Logs all parameters, prices, and Greeks
- Query and analyze historical calculations

## 🎨 Streamlit Interface

The web interface provides:

- **Sidebar inputs** for all option parameters
- **Real-time pricing** with Greeks calculation
- **Implied volatility** calculation from market prices
- **Interactive charts** (price curves, heatmaps, Greeks)
- **Golden values validation** for quick verification
- **Scenario logging** to SQLite database

## 🧪 Testing

Comprehensive test suite with:

- **Golden values validation** (known mathematical results)
- **Edge case testing** (T=0, σ=0, extreme values)
- **Finite difference checks** for Greeks
- **Round-trip validation** for implied volatility
- **Input validation** and error handling

Run tests with:
```bash
pytest -v                    # Verbose output
pytest -q                    # Quiet output
pytest tests/test_bs.py      # Specific test file
pytest -k "golden"           # Tests with "golden" in name
```

## 📊 Example Usage

### Python API

```python
from src.core.bs import price_call, price_put
from src.core.greeks import calculate_all_greeks
from src.core.iv import implied_vol_from_price

# Price a call option
S, K, r, sigma, T = 100.0, 100.0, 0.05, 0.2, 1.0
call_price = price_call(S, K, T, r, sigma)
print(f"Call Price: ${call_price:.4f}")

# Calculate all Greeks
greeks = calculate_all_greeks(S, K, T, r, sigma, "call")
print(f"Delta: {greeks['delta']:.6f}")

# Calculate implied volatility
market_price = 10.45
implied_vol = implied_vol_from_price(market_price, S, K, r, T, is_call=True)
print(f"Implied Vol: {implied_vol:.6f}")
```

### Command Line

```bash
# Run tests
pytest -q

# Launch web interface
streamlit run app/app.py

# Generate plots (via web interface)
# Use the "Plot Price Curve" and "Plot Heatmap" buttons
```

## 🔧 Development

### Adding New Features

1. **Core math**: Add to `src/core/` modules
2. **Tests**: Add corresponding tests in `tests/`
3. **UI**: Extend `app/app.py` if needed
4. **Documentation**: Update this README

### Code Style

- **Type hints** for all functions
- **Docstrings** with examples
- **Small, focused functions**
- **Comprehensive error handling**
- **Unit tests** for all functionality

## 📚 Mathematical Background

### Black-Scholes Formula

**Call Option:**
```
C = S * Φ(d1) - K * e^(-rT) * Φ(d2)
```

**Put Option:**
```
P = K * e^(-rT) * Φ(-d2) - S * Φ(-d1)
```

**Where:**
```
d1 = (ln(S/K) + (r + σ²/2)T) / (σ√T)
d2 = d1 - σ√T
```

### Greeks

- **Delta**: ∂C/∂S = Φ(d1) for calls, Φ(d1) - 1 for puts
- **Gamma**: ∂²C/∂S² = φ(d1) / (Sσ√T) (same for calls and puts)
- **Vega**: ∂C/∂σ = S√T * φ(d1) (same for calls and puts)
- **Theta**: ∂C/∂T (time decay)
- **Rho**: ∂C/∂r (interest rate sensitivity)

## 🤝 Contributing

This is a personal learning project, but suggestions are welcome:

1. **Fork** the repository
2. **Create** a feature branch
3. **Add** tests for new functionality
4. **Ensure** all tests pass
5. **Submit** a pull request

## 📄 License

This project is for educational purposes. Feel free to use and modify for your own learning.

## 🙏 Acknowledgments

- **Black-Scholes model** by Fischer Black and Myron Scholes
- **Python community** for excellent libraries
- **Streamlit** for the web framework
- **Mathematical finance** community for educational resources

---

**Happy Learning! 📈✨**

