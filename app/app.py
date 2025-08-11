import streamlit as st
import numpy as np
import pandas as pd
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.bs import black_scholes_price, d1, d2
from src.core.greeks import calculate_all_greeks
from src.core.iv import implied_vol_from_price
from src.utils.plots import plot_price_curve, plot_price_heatmap, plot_greeks_curves
from src.utils.logging import log_scenario


def check_put_call_parity(call_price, put_price, S, K, r, T):
    """
    Check put-call parity: C - P = S - Ke^(-rT)
    
    Returns:
        (is_valid, difference, tolerance_met)
    """
    left_side = call_price - put_price
    right_side = S - K * np.exp(-r * T)
    difference = abs(left_side - right_side)
    tolerance = 1e-6
    tolerance_met = difference < tolerance
    
    return tolerance_met, difference, left_side, right_side


def format_greek_value(value, greek_name, time_period="per year"):
    """
    Format Greek values with appropriate units and time period.
    """
    if greek_name == "theta":
        if time_period == "per day":
            value = value / 365
            unit = "/day"
        elif time_period == "per trading day":
            value = value / 252
            unit = "/trading day"
        else:
            unit = "/year"
    elif greek_name == "vega":
        unit = "/1.0 vol"
    elif greek_name == "rho":
        unit = "/1.0 rate"
    else:
        unit = ""
    
    return f"{value:.6f}{unit}"


def calculate_all_results(S, K, r, T, sigma, option_type, market_price):
    results = {}
    
    try:
        price = black_scholes_price(S, K, T, r, sigma, option_type)
        greeks = calculate_all_greeks(S, K, T, r, sigma, option_type)
        results['price'] = price
        results['greeks'] = greeks
        results['price_success'] = True
    except ValueError as e:
        results['price_error'] = str(e)
        results['price_success'] = False
    
    try:
        implied_vol = implied_vol_from_price(
            market_price, S, K, r, T, is_call=(option_type == "call")
        )
        results['implied_vol'] = implied_vol
        results['iv_success'] = True
    except ValueError as e:
        results['iv_error'] = str(e)
        results['iv_success'] = False
    
    try:
        S_range = np.linspace(max(1, S * 0.5), S * 1.5, 100)
        fig = plot_price_curve(S_range.tolist(), K, r, sigma, T, option_type)
        results['price_curve_fig'] = fig
        results['price_curve_success'] = True
    except Exception as e:
        results['price_curve_error'] = str(e)
        results['price_curve_success'] = False
    
    try:
        fig = plot_greeks_curves(S_range.tolist(), K, r, sigma, T, option_type)
        results['greeks_curves_fig'] = fig
        results['greeks_curves_success'] = True
    except Exception as e:
        results['greeks_curves_error'] = str(e)
        results['greeks_curves_success'] = False
    
    try:
        S_values = np.linspace(max(1, S * 0.5), S * 1.5, 50)
        vol_values = np.linspace(0.05, 0.5, 50)
        fig = plot_price_heatmap(S_values.tolist(), vol_values.tolist(), K, r, T, option_type)
        results['heatmap_fig'] = fig
        results['heatmap_success'] = True
    except Exception as e:
        results['heatmap_error'] = str(e)
        results['heatmap_success'] = False
    
    try:
        test_S, test_K, test_r, test_sigma, test_T = 100.0, 100.0, 0.05, 0.2, 1.0
        call_price = black_scholes_price(test_S, test_K, test_T, test_r, test_sigma, "call")
        put_price = black_scholes_price(test_S, test_K, test_T, test_r, test_sigma, "put")
        call_greeks = calculate_all_greeks(test_S, test_K, test_T, test_r, test_sigma, "call")
        put_greeks = calculate_all_greeks(test_S, test_K, test_T, test_r, test_sigma, "put")
        
        results['golden_values'] = {
            'call_price': call_price,
            'put_price': put_price,
            'call_greeks': call_greeks,
            'put_greeks': put_greeks
        }
        results['golden_values_success'] = True
    except Exception as e:
        results['golden_values_error'] = str(e)
        results['golden_values_success'] = False
    
    return results


def calculate_valid_market_price_bounds(S, K, r, T, option_type):
    """
    Calculate valid market price bounds for implied volatility calculation.
    
    Returns:
        (lower_bound, upper_bound, suggested_price)
    """
    if option_type == "call":
        # For calls: max(0, S - Ke^(-rT)) <= price <= S
        lower_bound = max(0, S - K * np.exp(-r * T))
        upper_bound = S
    else:
        # For puts: max(0, Ke^(-rT) - S) <= price <= K
        lower_bound = max(0, K * np.exp(-r * T) - S)
        upper_bound = K
    
    # Suggest a reasonable price within bounds
    if lower_bound == upper_bound:
        suggested_price = lower_bound
    else:
        suggested_price = lower_bound + 0.1 * (upper_bound - lower_bound)
    
    return lower_bound, upper_bound, suggested_price


def main():
    st.set_page_config(
        page_title="QuantPricer - Option Pricing Tool",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("QuantPricer - Option Pricing Tool")
    st.markdown("A personal learning tool for European option pricing using Black-Scholes formulas.")
    
    st.sidebar.header("Calculate")
    
    if st.sidebar.button("Calculate Option Price", type="primary", key="calculate_button"):
        st.session_state.calculate_triggered = True
    
    st.sidebar.header("Option Parameters")
    
    S = st.sidebar.number_input("Stock Price (S)", value=100.0, min_value=0.1, step=1.0, key="S_input")
    K = st.sidebar.number_input("Strike Price (K)", value=100.0, min_value=0.1, step=1.0, key="K_input")
    r = st.sidebar.number_input("Risk-free Rate (r)", value=0.05, min_value=0.0, max_value=1.0, step=0.01, format="%.3f", key="r_input")
    T = st.sidebar.number_input("Time to Expiration (T)", value=1.0, min_value=0.0, step=0.1, format="%.1f", key="T_input")
    sigma = st.sidebar.number_input("Volatility (σ)", value=0.2, min_value=0.001, max_value=5.0, step=0.1, format="%.3f", key="sigma_input")
    option_type = st.sidebar.selectbox("Option Type", ["call", "put"], key="option_type_input")
    
    # Calculate valid market price bounds
    lower_bound, upper_bound, suggested_price = calculate_valid_market_price_bounds(S, K, r, T, option_type)
    
    # Use a more robust session state key that includes parameter hash
    param_hash = hash((S, K, r, T, option_type))
    market_price_key = f"market_price_{param_hash}"
    
    # Initialize market price in session state if not present or if parameters changed
    if market_price_key not in st.session_state:
        st.session_state[market_price_key] = suggested_price
    
    # Check if current market price is still valid
    current_market_price = st.session_state[market_price_key]
    if current_market_price < lower_bound or current_market_price > upper_bound:
        st.session_state[market_price_key] = suggested_price
    
    # Use a unique key for the number input to ensure proper updates
    input_key = f"market_price_input_{param_hash}"
    
    market_price = st.sidebar.number_input(
        "Market Price (for IV)", 
        value=st.session_state[market_price_key],
        min_value=lower_bound,
        max_value=upper_bound,
        step=0.1,
        format="%.2f",
        key=input_key,
        help=f"Valid range: {lower_bound:.2f} to {upper_bound:.2f}"
    )
    
    # Update session state immediately after input
    st.session_state[market_price_key] = market_price
    
    # Show bounds info
    st.sidebar.info(f"**Valid IV range:** {lower_bound:.2f} - {upper_bound:.2f}")
    
    st.sidebar.header("Display Options")
    time_period = st.sidebar.selectbox(
        "Theta Time Period", 
        ["per year", "per day", "per trading day"],
        key="time_period_input"
    )
    
    # Only calculate when button is pressed, not on parameter changes
    if 'calculate_triggered' not in st.session_state:
        st.session_state.calculate_triggered = False
    
    if st.session_state.calculate_triggered:
        results = calculate_all_results(S, K, r, T, sigma, option_type, market_price)
        st.session_state.results = results
        st.session_state.calculate_triggered = False
    
    if 'results' in st.session_state:
        results = st.session_state.results
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.header("Option Pricing")
            
            if results.get('price_success', False):
                price = results['price']
                greeks = results['greeks']
                
                st.success(f"{option_type.title()} Option Price: **${price:.4f}**")
                
                st.subheader("Greeks")
                greeks_df = pd.DataFrame([
                    ["Delta", format_greek_value(greeks['delta'], "delta")],
                    ["Gamma", format_greek_value(greeks['gamma'], "gamma")],
                    ["Vega", format_greek_value(greeks['vega'], "vega")],
                    ["Theta", format_greek_value(greeks['theta'], "theta", time_period)],
                    ["Rho", format_greek_value(greeks['rho'], "rho")]
                ], columns=["Greek", "Value"])
                
                st.dataframe(greeks_df, hide_index=True)
                
                st.session_state.price = price
                st.session_state.greeks = greeks
                st.session_state.params = {
                    'S': S, 'K': K, 'r': r, 'T': T, 'sigma': sigma, 'option_type': option_type
                }
            else:
                st.error(f"Error: {results.get('price_error', 'Unknown error')}")
        
        with col2:
            st.header("Implied Volatility")
            
            if results.get('iv_success', False):
                implied_vol = results['implied_vol']
                
                st.success(f"Implied Volatility: **{implied_vol:.6f}** ({implied_vol*100:.2f}%)")
                
                try:
                    price_with_iv = black_scholes_price(S, K, T, r, implied_vol, option_type)
                    st.info(f"Price with implied volatility: ${price_with_iv:.4f}")
                except:
                    pass
                
                st.session_state.implied_vol = implied_vol
                st.session_state[market_price_key] = market_price
            else:
                st.error(f"Error: {results.get('iv_error', 'Unknown error')}")
        
        st.header("Put-Call Parity Check")
        
        if results.get('price_success', False):
            try:
                call_price = black_scholes_price(S, K, T, r, sigma, "call")
                put_price = black_scholes_price(S, K, T, r, sigma, "put")
                
                parity_ok, difference, left_side, right_side = check_put_call_parity(
                    call_price, put_price, S, K, r, T
                )
                
                if parity_ok:
                    st.success(" Put-Call Parity OK")
                else:
                    st.warning(" Put-Call Parity Check Failed")
                
                st.markdown(f"""
                **Parity Check:** C - P = S - Ke^(-rT)
                
                - **Left side (C - P):** {left_side:.6f}
                - **Right side (S - Ke^(-rT)):** {right_side:.6f}
                - **Difference:** {difference:.8f}
                - **Tolerance:** 1e-6
                """)
                
            except Exception as e:
                st.error(f"Parity check error: {e}")
        
        st.header("Charts & Analysis")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("Price Curve")
            if results.get('price_curve_success', False):
                st.pyplot(results['price_curve_fig'])
            else:
                st.error(f"Plot error: {results.get('price_curve_error', 'Unknown error')}")
            
            st.subheader("Greeks Curves")
            if results.get('greeks_curves_success', False):
                st.pyplot(results['greeks_curves_fig'])
            else:
                st.error(f"Plot error: {results.get('greeks_curves_error', 'Unknown error')}")
        
        with col4:
            st.subheader("Price Heatmap")
            if results.get('heatmap_success', False):
                st.pyplot(results['heatmap_fig'])
            else:
                st.error(f"Plot error: {results.get('heatmap_error', 'Unknown error')}")
        
        st.header("Golden Values Validation")
        st.markdown("""
        **Test Case:** S=100, K=100, r=0.05, σ=0.2, T=1
        
        | Metric | Expected | Calculated |
        |--------|----------|------------|
        | Call Price | 10.4506 | - |
        | Put Price | 5.5735 | - |
        | Call Delta | 0.63683 | - |
        | Put Delta | -0.36317 | - |
        | Gamma | 0.018762 | - |
        | Vega | 37.5240 | - |
        """)
        
        if results.get('golden_values_success', False):
            golden = results['golden_values']
            
            results_df = pd.DataFrame([
                ["Call Price", 10.4506, f"{golden['call_price']:.4f}"],
                ["Put Price", 5.5735, f"{golden['put_price']:.4f}"],
                ["Call Delta", 0.63683, f"{golden['call_greeks']['delta']:.5f}"],
                ["Put Delta", -0.36317, f"{golden['put_greeks']['delta']:.5f}"],
                ["Gamma", 0.018762, f"{golden['call_greeks']['gamma']:.6f}"],
                ["Vega", 37.5240, f"{golden['call_greeks']['vega']:.4f}"]
            ], columns=["Metric", "Expected", "Calculated"])
            
            st.dataframe(results_df, hide_index=True)
            
            tolerance = 1e-3
            call_price_ok = abs(golden['call_price'] - 10.4506) < tolerance
            put_price_ok = abs(golden['put_price'] - 5.5735) < tolerance
            
            if call_price_ok and put_price_ok:
                st.success("Golden values validation passed")
            else:
                st.warning("Some values differ from expected golden values")
        else:
            st.error(f"Validation error: {results.get('golden_values_error', 'Unknown error')}")
    
    st.sidebar.header("Logging")
    log_enabled = st.sidebar.checkbox("Log this scenario")
    
    if log_enabled and 'price' in st.session_state:
        if st.sidebar.button("Save to Database"):
            try:
                log_scenario(
                    params_dict=st.session_state.params,
                    greeks_dict=st.session_state.greeks,
                    price=st.session_state.price,
                    market_price=st.session_state.get('market_price'),
                    implied_vol=st.session_state.get('implied_vol'),
                    notes=f"Streamlit UI calculation"
                )
                st.sidebar.success("Scenario logged successfully")
            except Exception as e:
                st.sidebar.error(f"Logging failed: {e}")
    
    st.markdown("---")
    st.markdown("""
    **QuantPricer** - A personal learning tool for option pricing.
    
    - Core Math: Implemented from scratch using only `math` and `numpy`
    - No SciPy: All normal distribution functions use `math.erf`
    - European Options: No dividends, no early exercise
    - Black-Scholes: Standard formulas with proper edge case handling
    """)


if __name__ == "__main__":
    main()
