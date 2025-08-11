"""
Plotting utilities for option pricing using matplotlib.
"""

import os
import time
import glob
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Literal
from src.core.bs import black_scholes_price
from src.core.greeks import calculate_all_greeks

OptionType = Literal["call", "put"]


def cleanup_old_plots(max_files_per_type: int = 5):
    """
    Clean up old plot files to prevent the reports directory from filling up.
    
    Args:
        max_files_per_type: Maximum number of files to keep per plot type
    """
    if not os.path.exists('reports'):
        return
    
    plot_types = ['price_curve', 'heatmap', 'greeks_curves']
    
    for plot_type in plot_types:
        pattern = f'reports/{plot_type}_*.png'
        files = glob.glob(pattern)
        
        if len(files) > max_files_per_type:
            files.sort(key=os.path.getmtime, reverse=True)
            for old_file in files[max_files_per_type:]:
                try:
                    os.remove(old_file)
                except:
                    pass


def plot_price_curve(S_range: List[float], K: float, r: float, sigma: float, T: float, 
                    option_type: OptionType) -> str:
    """
    Plot option price curve against stock price.
    
    Args:
        S_range: List of stock prices to plot
        K: Strike price
        r: Risk-free rate (annualized)
        sigma: Volatility (annualized)
        T: Time to expiration (years)
        option_type: "call" or "put"
        
    Returns:
        Path to saved plot file
    """
    cleanup_old_plots()
    
    prices = []
    for S in S_range:
        try:
            price = black_scholes_price(S, K, T, r, sigma, option_type)
            prices.append(price)
        except ValueError:
            prices.append(np.nan)
    
    plt.figure(figsize=(10, 6))
    plt.plot(S_range, prices, 'b-', linewidth=2, label=f'{option_type.title()} Option')
    plt.axvline(x=K, color='r', linestyle='--', alpha=0.7, label=f'Strike (K={K})')
    plt.xlabel('Stock Price (S)')
    plt.ylabel('Option Price')
    plt.title(f'{option_type.title()} Option Price vs Stock Price\n'
              f'K={K}, r={r:.3f}, σ={sigma:.3f}, T={T:.3f}')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Create reports directory if it doesn't exist
    os.makedirs('reports', exist_ok=True)
    
    # Use unique filename with parameters and timestamp
    timestamp = int(time.time() * 1000)
    filename = f'reports/price_curve_{option_type}_K{K}_r{r:.3f}_s{sigma:.3f}_T{T:.3f}_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    return filename


def plot_price_heatmap(S_values: List[float], vol_values: List[float], K: float, r: float, T: float, 
                      option_type: OptionType) -> str:
    """
    Plot option price heatmap against stock price and volatility.
    
    Args:
        S_values: List of stock prices
        vol_values: List of volatility values
        K: Strike price
        r: Risk-free rate (annualized)
        T: Time to expiration (years)
        option_type: "call" or "put"
        
    Returns:
        Path to saved plot file
    """
    cleanup_old_plots()
    
    # Create meshgrid
    S_grid, vol_grid = np.meshgrid(S_values, vol_values)
    price_grid = np.zeros_like(S_grid)
    
    # Calculate prices for each combination
    for i, vol in enumerate(vol_values):
        for j, S in enumerate(S_values):
            try:
                price = black_scholes_price(S, K, T, r, vol, option_type)
                price_grid[i, j] = price
            except ValueError:
                price_grid[i, j] = np.nan
    
    plt.figure(figsize=(12, 8))
    
    # Create heatmap
    im = plt.imshow(price_grid, cmap='viridis', aspect='auto', 
                   extent=[min(S_values), max(S_values), min(vol_values), max(vol_values)],
                   origin='lower')
    
    plt.colorbar(im, label='Option Price')
    plt.xlabel('Stock Price (S)')
    plt.ylabel('Volatility (σ)')
    plt.title(f'{option_type.title()} Option Price Heatmap\n'
              f'K={K}, r={r:.3f}, T={T:.3f}')
    
    # Add strike line
    plt.axvline(x=K, color='r', linestyle='--', alpha=0.8, label=f'Strike (K={K})')
    plt.legend()
    
    # Create reports directory if it doesn't exist
    os.makedirs('reports', exist_ok=True)
    
    # Use unique filename with parameters and timestamp
    timestamp = int(time.time() * 1000)
    filename = f'reports/heatmap_{option_type}_K{K}_r{r:.3f}_T{T:.3f}_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    return filename


def plot_greeks_curves(S_range: List[float], K: float, r: float, sigma: float, T: float, 
                      option_type: OptionType) -> str:
    """
    Plot option Greeks curves against stock price.
    
    Args:
        S_range: List of stock prices to plot
        K: Strike price
        r: Risk-free rate (annualized)
        sigma: Volatility (annualized)
        T: Time to expiration (years)
        option_type: "call" or "put"
        
    Returns:
        Path to saved plot file
    """
    cleanup_old_plots()
    
    deltas, gammas, vegas, thetas, rhos = [], [], [], [], []
    
    for S in S_range:
        try:
            greeks = calculate_all_greeks(S, K, T, r, sigma, option_type)
            deltas.append(greeks['delta'])
            gammas.append(greeks['gamma'])
            vegas.append(greeks['vega'])
            thetas.append(greeks['theta'])
            rhos.append(greeks['rho'])
        except ValueError:
            deltas.append(np.nan)
            gammas.append(np.nan)
            vegas.append(np.nan)
            thetas.append(np.nan)
            rhos.append(np.nan)
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle(f'{option_type.title()} Option Greeks vs Stock Price\n'
                 f'K={K}, r={r:.3f}, σ={sigma:.3f}, T={T:.3f}')
    
    # Delta
    axes[0, 0].plot(S_range, deltas, 'b-', linewidth=2)
    axes[0, 0].axvline(x=K, color='r', linestyle='--', alpha=0.7)
    axes[0, 0].set_xlabel('Stock Price (S)')
    axes[0, 0].set_ylabel('Delta')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].set_title('Delta')
    
    # Gamma
    axes[0, 1].plot(S_range, gammas, 'g-', linewidth=2)
    axes[0, 1].axvline(x=K, color='r', linestyle='--', alpha=0.7)
    axes[0, 1].set_xlabel('Stock Price (S)')
    axes[0, 1].set_ylabel('Gamma')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].set_title('Gamma')
    
    # Vega
    axes[0, 2].plot(S_range, vegas, 'm-', linewidth=2)
    axes[0, 2].axvline(x=K, color='r', linestyle='--', alpha=0.7)
    axes[0, 2].set_xlabel('Stock Price (S)')
    axes[0, 2].set_ylabel('Vega')
    axes[0, 2].grid(True, alpha=0.3)
    axes[0, 2].set_title('Vega')
    
    # Theta
    axes[1, 0].plot(S_range, thetas, 'c-', linewidth=2)
    axes[1, 0].axvline(x=K, color='r', linestyle='--', alpha=0.7)
    axes[1, 0].set_xlabel('Stock Price (S)')
    axes[1, 0].set_ylabel('Theta')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].set_title('Theta')
    
    # Rho
    axes[1, 1].plot(S_range, rhos, 'y-', linewidth=2)
    axes[1, 1].axvline(x=K, color='r', linestyle='--', alpha=0.7)
    axes[1, 1].set_xlabel('Stock Price (S)')
    axes[1, 1].set_ylabel('Rho')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].set_title('Rho')
    
    # Hide the last subplot
    axes[1, 2].set_visible(False)
    
    plt.tight_layout()
    
    # Create reports directory if it doesn't exist
    os.makedirs('reports', exist_ok=True)
    
    # Use unique filename with parameters and timestamp
    timestamp = int(time.time() * 1000)
    filename = f'reports/greeks_curves_{option_type}_K{K}_r{r:.3f}_s{sigma:.3f}_T{T:.3f}_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    return filename
