"""
Validation system for the Gambling Simulation System.
Implements comprehensive validation with custom exceptions.
"""

from gambling_app_core.exceptions import (
    StakeValidationException,
    BetValidationException,
    ProbabilityValidationException
)
from gambling_app_core.config import APP_CONFIG


class StakeValidator:
    """Validates stake-related operations."""
    
    @staticmethod
    def validate_initial_stake(amount: float) -> None:
        """
        Validate initial stake amount.
        
        Args:
            amount: Stake amount to validate
        
        Raises:
            StakeValidationException: If validation fails
        """
        if amount <= 0:
            raise StakeValidationException("Initial stake must be positive")
        
        if amount > 1_000_000:
            raise StakeValidationException("Initial stake cannot exceed 1,000,000")
    
    @staticmethod
    def validate_threshold(win_threshold: float, loss_threshold: float, starting_stake: float) -> None:
        """
        Validate thresholds.
        
        Args:
            win_threshold: Upper threshold
            loss_threshold: Lower threshold
            starting_stake: Starting stake amount
        
        Raises:
            StakeValidationException: If thresholds are invalid
        """
        if win_threshold <= starting_stake:
            raise StakeValidationException("Win threshold must be greater than starting stake")
        
        if loss_threshold >= starting_stake:
            raise StakeValidationException("Loss threshold must be less than starting stake")
        
        if loss_threshold <= 0:
            raise StakeValidationException("Loss threshold must be positive")
        
        if win_threshold <= loss_threshold:
            raise StakeValidationException("Win threshold must be greater than loss threshold")
    
    @staticmethod
    def validate_stake_update(current_stake: float, amount: float, operation: str = "update") -> None:
        """
        Validate stake update.
        
        Args:
            current_stake: Current stake
            amount: Amount to add/subtract
            operation: 'add' or 'subtract'
        
        Raises:
            StakeValidationException: If update is invalid
        """
        if operation == "subtract":
            if current_stake - amount < 0:
                raise StakeValidationException("Insufficient stake for this operation")
        
        if amount <= 0:
            raise StakeValidationException("Update amount must be positive")
    
    @staticmethod
    def validate_boundaries(stake: float, win_threshold: float, loss_threshold: float) -> bool:
        """
        Check if stake has crossed thresholds.
        
        Args:
            stake: Current stake
            win_threshold: Win threshold
            loss_threshold: Loss threshold
        
        Returns:
            False if threshold crossed, True otherwise
        """
        return loss_threshold < stake < win_threshold


class BetValidator:
    """Validates betting operations."""
    
    @staticmethod
    def validate_bet_amount(bet_amount: float, current_stake: float) -> None:
        """
        Validate bet amount.
        
        Args:
            bet_amount: Bet amount
            current_stake: Current stake
        
        Raises:
            BetValidationException: If bet is invalid
        """
        if bet_amount <= 0:
            raise BetValidationException("Bet amount must be positive")
        
        if bet_amount < APP_CONFIG.betting.min_bet:
            raise BetValidationException(
                f"Bet amount must be at least {APP_CONFIG.betting.min_bet}"
            )
        
        if bet_amount > APP_CONFIG.betting.max_bet:
            raise BetValidationException(
                f"Bet amount cannot exceed {APP_CONFIG.betting.max_bet}"
            )
        
        if bet_amount > current_stake:
            raise BetValidationException(
                f"Bet amount ({bet_amount}) cannot exceed current stake ({current_stake})"
            )
    
    @staticmethod
    def validate_odds(odds: float, odd_type: str) -> None:
        """
        Validate odds.
        
        Args:
            odds: Odds value
            odd_type: Type of odds (decimal, fixed, probability)
        
        Raises:
            BetValidationException: If odds are invalid
        """
        if odd_type == "decimal":
            if odds < 1.0:
                raise BetValidationException("Decimal odds must be >= 1.0")
        
        elif odd_type == "fixed":
            if odds <= 0 or odds > 1000:
                raise BetValidationException("Fixed odds must be between 0 and 1000")
        
        elif odd_type == "probability":
            if odds <= 0 or odds > 100:
                raise BetValidationException("Probability odds must be between 0 and 100")
        
        else:
            raise BetValidationException(f"Unknown odd type: {odd_type}")
    
    @staticmethod
    def validate_strategy(strategy_name: str, valid_strategies: list) -> None:
        """
        Validate betting strategy.
        
        Args:
            strategy_name: Strategy name
            valid_strategies: List of valid strategies
        
        Raises:
            BetValidationException: If strategy is invalid
        """
        if strategy_name not in valid_strategies:
            raise BetValidationException(
                f"Invalid strategy: {strategy_name}. Must be one of {valid_strategies}"
            )


class ProbabilityValidator:
    """Validates probability-related values."""
    
    @staticmethod
    def validate_probability(probability: float) -> None:
        """
        Validate probability value.
        
        Args:
            probability: Probability value (0-1)
        
        Raises:
            ProbabilityValidationException: If probability is invalid
        """
        if probability < 0 or probability > 1:
            raise ProbabilityValidationException(
                "Probability must be between 0 and 1"
            )
    
    @staticmethod
    def validate_win_rate(wins: int, losses: int) -> float:
        """
        Validate and calculate win rate.
        
        Args:
            wins: Number of wins
            losses: Number of losses
        
        Returns:
            Win rate as percentage (0-100)
        
        Raises:
            ProbabilityValidationException: If values are invalid
        """
        if wins < 0 or losses < 0:
            raise ProbabilityValidationException("Wins and losses must be non-negative")
        
        total = wins + losses
        if total == 0:
            return 0.0
        
        win_rate = (wins / total) * 100
        return round(win_rate, 2)


class GamblerValidator:
    """Validates gambler-related data."""
    
    @staticmethod
    def validate_gambler_name(name: str) -> None:
        """
        Validate gambler name.
        
        Args:
            name: Gambler name
        
        Raises:
            StakeValidationException: If name is invalid
        """
        if not name or not name.strip():
            raise StakeValidationException("Gambler name cannot be empty")
        
        if len(name) > 255:
            raise StakeValidationException("Gambler name cannot exceed 255 characters")
        
        if len(name) < 2:
            raise StakeValidationException("Gambler name must be at least 2 characters")
    
    @staticmethod
    def validate_reset_request(confirm: bool) -> None:
        """
        Validate reset request confirmation.
        
        Args:
            confirm: Confirmation flag
        
        Raises:
            StakeValidationException: If not confirmed
        """
        if not confirm:
            raise StakeValidationException("Reset operation requires confirmation")
