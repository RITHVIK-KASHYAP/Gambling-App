"""
Custom exception classes for the Gambling Simulation System.
Hierarchical exception structure following SOLID principles.
"""


class GamblingAppException(Exception):
    """Base exception for all gambling app errors."""
    
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(f"[{error_code}] {message}")


class DatabaseException(GamblingAppException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str):
        super().__init__(message, "DB_ERROR")


class ConnectionException(DatabaseException):
    """Raised when database connection fails."""
    
    def __init__(self, message: str):
        super().__init__(message)


class RepositoryException(DatabaseException):
    """Raised when repository operations fail."""
    
    def __init__(self, message: str):
        super().__init__(message)


class ValidationException(GamblingAppException):
    """Base exception for validation errors."""
    
    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR"):
        super().__init__(message, error_code)


class StakeValidationException(ValidationException):
    """Raised when stake validation fails."""
    
    def __init__(self, message: str):
        super().__init__(message, "STAKE_VALIDATION_ERROR")


class BetValidationException(ValidationException):
    """Raised when bet validation fails."""
    
    def __init__(self, message: str):
        super().__init__(message, "BET_VALIDATION_ERROR")


class ProbabilityValidationException(ValidationException):
    """Raised when probability validation fails."""
    
    def __init__(self, message: str):
        super().__init__(message, "PROBABILITY_VALIDATION_ERROR")


class GamblerException(GamblingAppException):
    """Raised when gambler operations fail."""
    
    def __init__(self, message: str):
        super().__init__(message, "GAMBLER_ERROR")


class SessionException(GamblingAppException):
    """Raised when session operations fail."""
    
    def __init__(self, message: str):
        super().__init__(message, "SESSION_ERROR")


class StrategyException(GamblingAppException):
    """Raised when strategy operations fail."""
    
    def __init__(self, message: str):
        super().__init__(message, "STRATEGY_ERROR")


class BettingEngineException(GamblingAppException):
    """Raised when betting engine operations fail."""
    
    def __init__(self, message: str):
        super().__init__(message, "BETTING_ENGINE_ERROR")


class OutcomeException(GamblingAppException):
    """Raised when outcome calculation fails."""
    
    def __init__(self, message: str):
        super().__init__(message, "OUTCOME_ERROR")
