"""
SQLite logging utilities for option pricing scenarios.
"""

import sqlite3
import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class QuantPricerLogger:
    """SQLite logger for option pricing scenarios."""
    
    def __init__(self, db_path: str = "quantpricer.db"):
        """
        Initialize the logger.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database and create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create scenarios table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scenarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    S REAL NOT NULL,
                    K REAL NOT NULL,
                    r REAL NOT NULL,
                    T REAL NOT NULL,
                    sigma REAL NOT NULL,
                    option_type TEXT NOT NULL,
                    price REAL NOT NULL,
                    delta REAL,
                    gamma REAL,
                    vega REAL,
                    theta REAL,
                    rho REAL,
                    market_price REAL,
                    implied_vol REAL,
                    notes TEXT
                )
            """)
            
            conn.commit()
    
    def log_scenario(self, params_dict: Dict[str, Any], greeks_dict: Optional[Dict[str, float]] = None, 
                    price: Optional[float] = None, market_price: Optional[float] = None, 
                    implied_vol: Optional[float] = None, notes: Optional[str] = None):
        """
        Log an option pricing scenario to the database.
        
        Args:
            params_dict: Dictionary containing S, K, r, T, sigma, option_type
            greeks_dict: Dictionary containing delta, gamma, vega, theta, rho
            price: Calculated option price
            market_price: Market price (for implied vol calculations)
            implied_vol: Implied volatility
            notes: Additional notes
        """
        timestamp = datetime.datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO scenarios (
                    timestamp, S, K, r, T, sigma, option_type, price, 
                    delta, gamma, vega, theta, rho, market_price, implied_vol, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                params_dict.get('S'),
                params_dict.get('K'),
                params_dict.get('r'),
                params_dict.get('T'),
                params_dict.get('sigma'),
                params_dict.get('option_type'),
                price,
                greeks_dict.get('delta') if greeks_dict else None,
                greeks_dict.get('gamma') if greeks_dict else None,
                greeks_dict.get('vega') if greeks_dict else None,
                greeks_dict.get('theta') if greeks_dict else None,
                greeks_dict.get('rho') if greeks_dict else None,
                market_price,
                implied_vol,
                notes
            ))
            
            conn.commit()
    
    def get_recent_scenarios(self, limit: int = 10) -> list:
        """
        Get recent pricing scenarios.
        
        Args:
            limit: Maximum number of scenarios to return
            
        Returns:
            List of recent scenarios
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM scenarios 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
    
    def get_scenarios_by_type(self, option_type: str, limit: int = 10) -> list:
        """
        Get scenarios filtered by option type.
        
        Args:
            option_type: "call" or "put"
            limit: Maximum number of scenarios to return
            
        Returns:
            List of scenarios for the specified option type
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM scenarios 
                WHERE option_type = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (option_type, limit))
            
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
    
    def clear_scenarios(self):
        """Clear all scenarios from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scenarios")
            conn.commit()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary containing database statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total scenarios
            cursor.execute("SELECT COUNT(*) FROM scenarios")
            total_scenarios = cursor.fetchone()[0]
            
            # Scenarios by type
            cursor.execute("""
                SELECT option_type, COUNT(*) 
                FROM scenarios 
                GROUP BY option_type
            """)
            scenarios_by_type = dict(cursor.fetchall())
            
            # Date range
            cursor.execute("""
                SELECT MIN(timestamp), MAX(timestamp) 
                FROM scenarios
            """)
            date_range = cursor.fetchone()
            
            return {
                'total_scenarios': total_scenarios,
                'scenarios_by_type': scenarios_by_type,
                'date_range': date_range
            }


# Global logger instance
logger = QuantPricerLogger()


def log_scenario(params_dict: Dict[str, Any], greeks_dict: Optional[Dict[str, float]] = None, 
                price: Optional[float] = None, market_price: Optional[float] = None, 
                implied_vol: Optional[float] = None, notes: Optional[str] = None):
    """
    Convenience function to log a scenario using the global logger.
    
    Args:
        params_dict: Dictionary containing S, K, r, T, sigma, option_type
        greeks_dict: Dictionary containing delta, gamma, vega, theta, rho
        price: Calculated option price
        market_price: Market price (for implied vol calculations)
        implied_vol: Implied volatility
        notes: Additional notes
    """
    logger.log_scenario(params_dict, greeks_dict, price, market_price, implied_vol, notes)
