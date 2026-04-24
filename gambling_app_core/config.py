"""
Application configuration settings for the Gambling Simulation System.
Centralized configuration management for database, betting rules, and system behavior.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from enum import Enum


class GameType(Enum):
    """Available game types."""
    SLOTS = "slots"
    ROULETTE = "roulette"
    BLACKJACK = "blackjack"
    SPORTS = "sports"
    POKER = "poker"
    CRAPS = "craps"


# Game-specific odds configurations
GAME_ODDS_CONFIG = {
    GameType.SLOTS: [1.5, 2.0, 2.5, 3.0, 4.0],
    GameType.ROULETTE: [1.8, 2.0, 2.2],
    GameType.BLACKJACK: [1.5, 2.0, 2.5],
    GameType.SPORTS: [1.5, 1.8, 2.0, 2.5, 3.0, 3.5],
    GameType.POKER: [1.5, 2.0, 2.5, 3.0],
    GameType.CRAPS: [1.6, 1.8, 2.0, 2.2],
}


@dataclass
class DatabaseConfig:
    """Database connection configuration."""
    host: str = "localhost"
    user: str = "root"
    password: str = "Rithvik@123"
    database: str = "gamblingapp"
    port: int = 3306
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to connection dictionary."""
        return {
            "host": self.host,
            "user": self.user,
            "password": self.password,
            "database": self.database,
            "port": self.port
        }


@dataclass
class BettingConfig:
    """Betting system configuration."""
    min_bet: float = 10.0
    max_bet: float = 10000.0
    default_odd_type: str = "decimal"  # decimal, fixed, probability
    house_edge: float = 0.02  # 2% house edge for weighted outcomes


@dataclass
class GameConfig:
    """Game session configuration."""
    starting_stake: float = 1000.0
    win_threshold: float = 2000.0  # Upper threshold
    loss_threshold: float = 100.0   # Lower threshold
    auto_play_count: int = 10
    default_game_type: GameType = GameType.ROULETTE


@dataclass
class LoggingConfig:
    """Logging configuration."""
    log_file: str = "gambling_app.log"
    log_level: str = "INFO"
    log_to_console: bool = True
    log_to_file: bool = True


class AppConfig:
    """Main application configuration manager."""
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.betting = BettingConfig()
        self.game = GameConfig()
        self.logging = LoggingConfig()
    
    @staticmethod
    def get_default() -> "AppConfig":
        """Get default configuration."""
        return AppConfig()
    
    def update_database_config(self, **kwargs) -> None:
        """Update database configuration."""
        for key, value in kwargs.items():
            if hasattr(self.database, key):
                setattr(self.database, key, value)
    
    def update_game_config(self, **kwargs) -> None:
        """Update game configuration."""
        for key, value in kwargs.items():
            if hasattr(self.game, key):
                setattr(self.game, key, value)
    
    def update_betting_config(self, **kwargs) -> None:
        """Update betting configuration."""
        for key, value in kwargs.items():
            if hasattr(self.betting, key):
                setattr(self.betting, key, value)


# Global configuration instance
APP_CONFIG = AppConfig.get_default()
