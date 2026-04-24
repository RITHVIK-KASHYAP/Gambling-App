"""
Utility modules for the Gambling Simulation System.
Contains logging, formatting, and calculation utilities.
"""

import logging
import logging.handlers
from typing import List, Tuple
from datetime import datetime, timedelta
from statistics import stdev
from gambling_app_core.config import APP_CONFIG


# ============= LOGGING SETUP =============

class LoggerSetup:
    """Configure logging for the application."""
    
    _initialized = False
    
    @staticmethod
    def setup() -> logging.Logger:
        """Initialize logging configuration."""
        if LoggerSetup._initialized:
            return logging.getLogger(__name__)
        
        # Create logger
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, APP_CONFIG.logging.log_level))
        
        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        if APP_CONFIG.logging.log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # File handler
        if APP_CONFIG.logging.log_to_file:
            file_handler = logging.handlers.RotatingFileHandler(
                APP_CONFIG.logging.log_file,
                maxBytes=10_000_000,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        LoggerSetup._initialized = True
        logger.info("Logging initialized")
        
        return logger


# ============= FORMATTING UTILITIES =============

class FormattingUtils:
    """Utilities for formatting output."""
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """Format amount as currency."""
        return f"${amount:,.2f}"
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 2) -> str:
        """Format value as percentage."""
        return f"{value:.{decimals}f}%"
    
    @staticmethod
    def format_odds(odds: float, odd_type: str) -> str:
        """Format odds based on type."""
        if odd_type == "decimal":
            return f"{odds:.2f}"
        elif odd_type == "fixed":
            return f"{odds:.0f}:1"
        elif odd_type == "probability":
            return f"{odds:.2f}%"
        return str(odds)
    
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """Format datetime for display."""
        if dt is None:
            return "N/A"
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human-readable format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"


# ============= CALCULATION UTILITIES =============

class CalculationUtils:
    """Utilities for mathematical calculations."""
    
    @staticmethod
    def calculate_win_rate(wins: int, total: int) -> float:
        """Calculate win rate percentage."""
        if total == 0:
            return 0.0
        return round((wins / total) * 100, 2)
    
    @staticmethod
    def calculate_roi(profit_loss: float, starting_stake: float) -> float:
        """Calculate Return on Investment percentage."""
        if starting_stake == 0:
            return 0.0
        return round((profit_loss / starting_stake) * 100, 2)
    
    @staticmethod
    def calculate_average(values: List[float]) -> float:
        """Calculate average of values."""
        if not values:
            return 0.0
        return round(sum(values) / len(values), 2)
    
    @staticmethod
    def calculate_volatility(values: List[float]) -> float:
        """Calculate volatility (standard deviation) of values."""
        if len(values) < 2:
            return 0.0
        try:
            return round(stdev(values), 4)
        except:
            return 0.0
    
    @staticmethod
    def calculate_streak(outcomes: List[str], streak_type: str = "win") -> int:
        """
        Calculate longest streak of specified type.
        
        Args:
            outcomes: List of outcomes ('win' or 'loss')
            streak_type: Type of streak to find ('win' or 'loss')
        
        Returns:
            Length of longest streak
        """
        if not outcomes:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        for outcome in outcomes:
            if outcome == streak_type:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    @staticmethod
    def calculate_average_bet(total_wagered: float, total_bets: int) -> float:
        """Calculate average bet amount."""
        if total_bets == 0:
            return 0.0
        return round(total_wagered / total_bets, 2)


# ============= STATISTICS CALCULATION =============

class StatisticsCalculator:
    """Calculate gambling statistics."""
    
    @staticmethod
    def calculate_volatility_from_stakes(stakes: List[float]) -> float:
        """
        Calculate volatility from stake history.
        
        Args:
            stakes: List of stake amounts
        
        Returns:
            Volatility value
        """
        if len(stakes) < 2:
            return 0.0
        
        changes = []
        for i in range(1, len(stakes)):
            if stakes[i-1] != 0:
                change = ((stakes[i] - stakes[i-1]) / stakes[i-1]) * 100
                changes.append(change)
        
        return CalculationUtils.calculate_volatility(changes)
    
    @staticmethod
    def calculate_session_duration(start_time: datetime, end_time: datetime = None) -> float:
        """
        Calculate session duration in seconds.
        
        Args:
            start_time: Session start time
            end_time: Session end time (defaults to now)
        
        Returns:
            Duration in seconds
        """
        if end_time is None:
            end_time = datetime.now()
        
        delta = end_time - start_time
        return delta.total_seconds()
    
    @staticmethod
    def calculate_average_bet(total_wagered: float, bet_count: int) -> float:
        """Calculate average bet amount."""
        if bet_count == 0:
            return 0.0
        return round(total_wagered / bet_count, 2)


# ============= PROGRESSION UTILITIES =============

class StreakTracker:
    """Track win/loss streaks."""
    
    def __init__(self):
        """Initialize streak tracker."""
        self.current_streak = 0
        self.current_streak_type = None
        self.longest_win_streak = 0
        self.longest_loss_streak = 0
    
    def record_outcome(self, outcome: str) -> None:
        """
        Record a bet outcome.
        
        Args:
            outcome: 'win' or 'loss'
        """
        if outcome == self.current_streak_type:
            self.current_streak += 1
        else:
            # Streak ended
            if self.current_streak_type == "win":
                self.longest_win_streak = max(self.longest_win_streak, self.current_streak)
            elif self.current_streak_type == "loss":
                self.longest_loss_streak = max(self.longest_loss_streak, self.current_streak)
            
            self.current_streak = 1
            self.current_streak_type = outcome
    
    def finalize(self) -> None:
        """Finalize the tracker (call at end of session)."""
        if self.current_streak_type == "win":
            self.longest_win_streak = max(self.longest_win_streak, self.current_streak)
        elif self.current_streak_type == "loss":
            self.longest_loss_streak = max(self.longest_loss_streak, self.current_streak)
    
    def get_longest_win_streak(self) -> int:
        """Get longest win streak."""
        return self.longest_win_streak
    
    def get_longest_loss_streak(self) -> int:
        """Get longest loss streak."""
        return self.longest_loss_streak
