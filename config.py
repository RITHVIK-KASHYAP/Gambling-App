"""
Application configuration settings for the Gambling Simulation System.
Centralized configuration management using environment variables.
"""

import os
from dataclasses import dataclass
from typing import Dict, Any
from enum import Enum

from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()


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
    host: str = os.getenv("DB_HOST", "localhost")
    user: str = os.getenv("DB_USER", "root")
    password: str = os.getenv("DB_PASSWORD", "")
    database: str = os.getenv("DB_NAME", "gamblingapp")
    port: int = int(os.getenv("DB_PORT", 3306))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to DB connection dictionary."""
        return {
            "host": self.host,
            "user": self.user,
            "password": self.password,
            "database": self.database,
            "port": self.port,
        }


@dataclass
class BettingConfig:
    """Betting system configuration."""
    min_bet: float = 10.0
    max_bet: float = 10000.0
    default_odd_type: str = "decimal"
    house_edge: float = float(os.getenv("HOUSE_EDGE", 0.02))


@dataclass
class GameConfig:
    """Game session configuration."""
    starting_stake: float = 1000.0
    win_threshold: float = 2000.0
    loss_threshold: float = 100.0
    auto_play_count: int = 10
    default_game_type: GameType = GameType.ROULETTE


@dataclass
class LoggingConfig:
    """Logging configuration."""
    log_file: str = os.getenv("LOG_FILE", "gambling_app.log")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
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
        return AppConfig()

    def update_database_config(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self.database, key):
                setattr(self.database, key, value)

    def update_betting_config(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self.betting, key):
                setattr(self.betting, key, value)

    def update_game_config(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self.game, key):
                setattr(self.game, key, value)


# Global configuration instance
APP_CONFIG = AppConfig.get_default()