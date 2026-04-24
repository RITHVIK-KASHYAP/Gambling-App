"""
Strategy Pattern implementations for betting and outcome calculation.
Supports multiple betting strategies and outcome determination methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, List
import random
from gambling_app_core.config import APP_CONFIG
from gambling_app_core.exceptions import StrategyException
import logging


logger = logging.getLogger(__name__)


# ============= BETTING STRATEGIES =============

class BettingStrategy(ABC):
    """Abstract base class for betting strategies."""
    
    @abstractmethod
    def calculate_bet(self, current_stake: float, previous_bet: float = None, 
                     last_outcome: str = None) -> float:
        """
        Calculate bet amount based on strategy.
        
        Args:
            current_stake: Current stake amount
            previous_bet: Previous bet amount (for progressive strategies)
            last_outcome: Last bet outcome (win/loss)
        
        Returns:
            Calculated bet amount
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get strategy name."""
        pass
    
    def validate_bet(self, bet_amount: float, current_stake: float) -> bool:
        """
        Validate if calculated bet is reasonable.
        
        Args:
            bet_amount: Calculated bet amount
            current_stake: Current stake
        
        Returns:
            True if valid, False otherwise
        """
        return 0 < bet_amount <= current_stake and \
               bet_amount >= APP_CONFIG.betting.min_bet and \
               bet_amount <= APP_CONFIG.betting.max_bet


class FixedBettingStrategy(BettingStrategy):
    """Fixed amount betting strategy."""
    
    def __init__(self, fixed_amount: float = 100.0):
        """
        Initialize fixed betting strategy.
        
        Args:
            fixed_amount: Fixed bet amount
        """
        self.fixed_amount = fixed_amount
    
    def calculate_bet(self, current_stake: float, previous_bet: float = None,
                     last_outcome: str = None) -> float:
        """Always bet the same fixed amount."""
        return min(self.fixed_amount, current_stake)
    
    def get_name(self) -> str:
        return "Fixed"


class PercentageBettingStrategy(BettingStrategy):
    """Percentage-based betting strategy."""
    
    def __init__(self, percentage: float = 10.0):
        """
        Initialize percentage betting strategy.
        
        Args:
            percentage: Percentage of stake to bet (0-100)
        """
        if percentage <= 0 or percentage > 100:
            raise StrategyException("Percentage must be between 0 and 100")
        self.percentage = percentage
    
    def calculate_bet(self, current_stake: float, previous_bet: float = None,
                     last_outcome: str = None) -> float:
        """Bet a percentage of current stake."""
        return current_stake * (self.percentage / 100)
    
    def get_name(self) -> str:
        return "Percentage"


class MartingaleStrategy(BettingStrategy):
    """Martingale betting strategy (double after loss)."""
    
    def __init__(self, initial_bet: float = 100.0):
        """
        Initialize Martingale strategy.
        
        Args:
            initial_bet: Initial bet amount
        """
        self.initial_bet = initial_bet
    
    def calculate_bet(self, current_stake: float, previous_bet: float = None,
                     last_outcome: str = None) -> float:
        """
        Double bet after loss, reset to initial after win.
        """
        if last_outcome is None or last_outcome == "win":
            return min(self.initial_bet, current_stake)
        
        # After loss, double previous bet
        if previous_bet is not None:
            next_bet = previous_bet * 2
            return min(next_bet, current_stake)
        
        return min(self.initial_bet, current_stake)
    
    def get_name(self) -> str:
        return "Martingale"


class ReverseMartingaleStrategy(BettingStrategy):
    """Reverse Martingale strategy (increase after win)."""
    
    def __init__(self, initial_bet: float = 100.0):
        """
        Initialize Reverse Martingale strategy.
        
        Args:
            initial_bet: Initial bet amount
        """
        self.initial_bet = initial_bet
    
    def calculate_bet(self, current_stake: float, previous_bet: float = None,
                     last_outcome: str = None) -> float:
        """
        Double bet after win, reset to initial after loss.
        """
        if last_outcome is None or last_outcome == "loss":
            return min(self.initial_bet, current_stake)
        
        # After win, double previous bet
        if previous_bet is not None:
            next_bet = previous_bet * 2
            return min(next_bet, current_stake)
        
        return min(self.initial_bet, current_stake)
    
    def get_name(self) -> str:
        return "Reverse Martingale"


class FibonacciStrategy(BettingStrategy):
    """Fibonacci sequence betting strategy."""
    
    def __init__(self, initial_bet: float = 100.0):
        """
        Initialize Fibonacci strategy.
        
        Args:
            initial_bet: Initial bet amount
        """
        self.initial_bet = initial_bet
        self.sequence = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
        self.current_index = 0
    
    def calculate_bet(self, current_stake: float, previous_bet: float = None,
                     last_outcome: str = None) -> float:
        """
        Use Fibonacci sequence for bet amounts.
        """
        if last_outcome is None or last_outcome == "win":
            self.current_index = 0
        else:
            self.current_index = min(self.current_index + 1, len(self.sequence) - 1)
        
        fib_value = self.sequence[self.current_index]
        bet_amount = self.initial_bet * fib_value
        return min(bet_amount, current_stake)
    
    def get_name(self) -> str:
        return "Fibonacci"


class DAlembert_Strategy(BettingStrategy):
    """D'Alembert betting strategy (unit increase/decrease)."""
    
    def __init__(self, initial_bet: float = 100.0, unit: float = 50.0):
        """
        Initialize D'Alembert strategy.
        
        Args:
            initial_bet: Initial bet amount
            unit: Unit to increase/decrease
        """
        self.initial_bet = initial_bet
        self.unit = unit
        self.current_bet = initial_bet
    
    def calculate_bet(self, current_stake: float, previous_bet: float = None,
                     last_outcome: str = None) -> float:
        """
        Increase by unit after loss, decrease by unit after win.
        """
        if last_outcome is None or last_outcome == "win":
            self.current_bet = max(self.initial_bet, self.current_bet - self.unit)
        elif last_outcome == "loss":
            self.current_bet = self.current_bet + self.unit
        
        return min(self.current_bet, current_stake)
    
    def get_name(self) -> str:
        return "D'Alembert"


# ============= OUTCOME STRATEGIES =============

class OutcomeStrategy(ABC):
    """Abstract base class for outcome determination."""
    
    @abstractmethod
    def determine_outcome(self, odds: float) -> bool:
        """
        Determine if a bet wins.
        
        Args:
            odds: Odds value
        
        Returns:
            True if bet wins, False if loses
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get strategy name."""
        pass


class RandomOutcomeStrategy(OutcomeStrategy):
    """Random outcome strategy (50-50 chance)."""
    
    def determine_outcome(self, odds: float) -> bool:
        """Win with 50% probability regardless of odds."""
        return random.random() < 0.5
    
    def get_name(self) -> str:
        return "Random"


class WeightedOutcomeStrategy(OutcomeStrategy):
    """Weighted outcome strategy with house edge."""
    
    def __init__(self, house_edge: float = None):
        """
        Initialize weighted outcome strategy.
        
        Args:
            house_edge: House edge percentage (defaults to config value)
        """
        self.house_edge = house_edge or APP_CONFIG.betting.house_edge
    
    def determine_outcome(self, odds: float) -> bool:
        """
        Win probability based on odds, adjusted for house edge.
        
        Args:
            odds: Decimal odds
        
        Returns:
            True if bet wins, False if loses
        """
        # Convert decimal odds to win probability
        # For decimal odds: probability = 1 / odds
        implied_probability = 1.0 / odds if odds > 0 else 0.5
        
        # Apply house edge to reduce player's winning probability
        adjusted_probability = implied_probability * (1 - self.house_edge)
        
        return random.random() < adjusted_probability
    
    def get_name(self) -> str:
        return "Weighted"


class ProbabilityBasedOutcomeStrategy(OutcomeStrategy):
    """Outcome strategy based on explicit probability."""
    
    def __init__(self, win_probability: float = 0.5):
        """
        Initialize probability-based outcome strategy.
        
        Args:
            win_probability: Win probability (0-1)
        """
        if win_probability < 0 or win_probability > 1:
            raise StrategyException("Win probability must be between 0 and 1")
        self.win_probability = win_probability
    
    def determine_outcome(self, odds: float) -> bool:
        """Win with specified probability."""
        return random.random() < self.win_probability
    
    def get_name(self) -> str:
        return "Probability-Based"


# ============= STRATEGY REGISTRY =============

class BettingStrategyRegistry:
    """Registry for available betting strategies."""
    
    _strategies: Dict[str, BettingStrategy] = {}
    
    @classmethod
    def register(cls, name: str, strategy: BettingStrategy) -> None:
        """Register a betting strategy."""
        cls._strategies[name.lower()] = strategy
        logger.info(f"Registered betting strategy: {name}")
    
    @classmethod
    def get(cls, name: str) -> BettingStrategy:
        """Get a registered betting strategy."""
        strategy = cls._strategies.get(name.lower())
        if strategy is None:
            raise StrategyException(f"Unknown betting strategy: {name}")
        return strategy
    
    @classmethod
    def list_all(cls) -> List[str]:
        """List all available strategies."""
        return list(cls._strategies.keys())


class OutcomeStrategyRegistry:
    """Registry for available outcome strategies."""
    
    _strategies: Dict[str, OutcomeStrategy] = {}
    
    @classmethod
    def register(cls, name: str, strategy: OutcomeStrategy) -> None:
        """Register an outcome strategy."""
        cls._strategies[name.lower()] = strategy
        logger.info(f"Registered outcome strategy: {name}")
    
    @classmethod
    def get(cls, name: str) -> OutcomeStrategy:
        """Get a registered outcome strategy."""
        strategy = cls._strategies.get(name.lower())
        if strategy is None:
            raise StrategyException(f"Unknown outcome strategy: {name}")
        return strategy
    
    @classmethod
    def list_all(cls) -> List[str]:
        """List all available strategies."""
        return list(cls._strategies.keys())


# ============= INITIALIZE REGISTRIES =============

# Register default betting strategies
BettingStrategyRegistry.register("fixed", FixedBettingStrategy(100))
BettingStrategyRegistry.register("percentage", PercentageBettingStrategy(10))
BettingStrategyRegistry.register("martingale", MartingaleStrategy(100))
BettingStrategyRegistry.register("reverse_martingale", ReverseMartingaleStrategy(100))
BettingStrategyRegistry.register("fibonacci", FibonacciStrategy(100))
BettingStrategyRegistry.register("dalembert", DAlembert_Strategy(100, 50))

# Register default outcome strategies
OutcomeStrategyRegistry.register("random", RandomOutcomeStrategy())
OutcomeStrategyRegistry.register("weighted", WeightedOutcomeStrategy())
OutcomeStrategyRegistry.register("probability", ProbabilityBasedOutcomeStrategy(0.45))
